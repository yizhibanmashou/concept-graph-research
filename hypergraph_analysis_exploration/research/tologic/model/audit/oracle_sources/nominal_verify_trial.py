"""Independent recursive grammar oracle and selection for the real Nom trial.

The oracle does not use the production search generator. It constructs all
nonempty resource partitions, optional licensed noun binding, and both not
attachments. The production Nom compiler is used only after selection to show
the resulting expansion, not to decide completeness.
"""
from copy import deepcopy
from functools import lru_cache
from itertools import combinations, product
import json

from build_trial import HERE, PRIOR, PROJECT, read, write
from tologic_v3.common import canonical_hash
from tologic_v3.enumeration_input import prepare_request
from tologic_v3.nominalization import expand_nominalizations


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def key(node):
    def norm(n):
        if isinstance(n, list):
            return [norm(x) for x in n]
        if not isinstance(n, dict):
            return n
        result = {k: norm(v) for k, v in n.items()}
        if n.get("op") == "and":
            args = []
            for child in result["args"]:
                args.extend(child["args"] if child.get("op") == "and" else [child])
            args.sort(key=lambda x: json.dumps(x, sort_keys=True))
            return args[0] if len(args) == 1 else {"op": "and", "args": args}
        return result
    return json.dumps(norm(node), sort_keys=True, separators=(",", ":"))


def oracle(request, report, nid):
    source_by_word = {o["text"]: o for o in request["source"]["occurrences"]}
    interfaces = {p["synset_id"]: p for p in request["interfaces"].values()}
    hashes = {}
    for p in interfaces.values():
        hashes[p["synset_id"]] = canonical_hash({field: p.get(field) for field in
                                               ("synset_id", "usage_id", "is_basis", "parameters", "lhs", "voice")})
    assert {p["synset_id"] + "::" + p["usage_id"]: hashes[p["synset_id"]] for p in interfaces.values()} == report["interface_hashes"]
    def use(word, *args):
        occurrence = source_by_word[word]
        p = interfaces[occurrence["synset_id"]]
        return {"op": "use", "synset_id": p["synset_id"], "usage_id": p["usage_id"],
                "interface_hash": hashes[p["synset_id"]], "occurrence_id": occurrence["occurrence_id"], "args": list(args)}
    def nom(ref, negative):
        node = use("moving", {"var": ref})
        node.update(op="nom", nominalization_id=nid, construction_hash=report["nominalization_hashes"][nid],
                    negation_occurrence_ids=[source_by_word["not"]["occurrence_id"]] if negative else [])
        return node
    def conj(a, b):
        return {"op": "and", "args": [a, b]}

    @lru_cache(None)
    def region(resources, h_visible, negative):
        result = {}
        def save(node):
            result[key(node)] = node
        variables = ["q", "h"] if h_visible else ["q"]
        if resources == ("Q",):
            save(use("quality", {"var": "q"}))
        if resources == ("O",):
            for left, right in product(variables, repeat=2):
                save(use("of", {"var": left}, {"var": right}))
        if resources == ("M",):
            for value in variables:
                save(nom(value, negative))
        if "N" in resources and len(resources) > 1:
            for body in region(tuple(r for r in resources if r != "N"), h_visible, negative):
                save(use("not", body))
        if "W" in resources and len(resources) > 1 and not h_visible:
            for body in region(tuple(r for r in resources if r != "W"), True, negative):
                if not any(n.get("op") == "nom" and n["args"][0] == {"var": "h"} for n in nodes(body)):
                    continue
                save({"op": "exists", "variables": [{"name": "h", "type": "E"}], "body": body,
                      "origin": "nominalization", "occurrence_id": source_by_word["moving"]["occurrence_id"]})
        for size in range(1, len(resources)):
            for left in combinations(resources, size):
                if resources[0] not in left:
                    continue
                right = tuple(r for r in resources if r not in left)
                for a, b in product(region(tuple(left), h_visible, negative), region(right, h_visible, negative)):
                    save(conj(a, b))
        return tuple(result.values())
    complete = {}
    for has_of, has_move, has_not, has_witness in product([False, True], repeat=4):
        if has_witness and not has_move:
            continue
        resources = ["Q"] + [r for r, on in zip(["O", "M", "N", "W"], [has_of, has_move, has_not, has_witness]) if on]
        for node in region(tuple(sorted(resources)), False, False):
            complete[key(node)] = node
    # The same not occurrence is inside Nom here, so an outer N is unavailable.
    for has_of, has_witness in product([False, True], repeat=2):
        resources = ["Q", "M"] + (["O"] if has_of else []) + (["W"] if has_witness else [])
        for node in region(tuple(sorted(resources)), False, True):
            complete[key(node)] = node
    return complete


def main():
    request = read(HERE / "input.json")
    prepared = prepare_request(request, PROJECT)
    run = HERE / "runs/current"
    report = read(run / "report.json")
    assert report["complete"] and report["exhausted"] and report["max_candidates"] is None
    nid = request["enumeration"]["nominalizations"][0]["nominalization_id"]
    expected = oracle(request, report, nid)
    rows = [json.loads(line) for line in (run / "candidates.jsonl").read_text(encoding="utf-8").splitlines()]
    observed = {key(row["formula"]["rhs"]) for row in rows}
    assert observed == set(expected), {"missing": len(set(expected) - observed), "extra": len(observed - set(expected))}
    assert len(observed) == len(rows) == report["candidate_count"]
    lhs = read(HERE / "lhs_frozen.json")
    matches = []
    for index, row in enumerate(rows, 1):
        formula = row["formula"]
        assert formula["lhs"] == lhs["lhs"] and formula["parameters"] == lhs["parameters"]
        assert row["interface_gate"]["passed"]
        ns = list(nodes(formula["rhs"]))
        assert not any(n.get("name") in {"NominalRef", "Holds"} for n in ns)
        noms = [n for n in ns if n.get("op") == "nom"]
        uses = [n for n in ns if n.get("op") == "use"]
        exists = [n for n in ns if n.get("op") == "exists"]
        consumed = [n["occurrence_id"] for n in uses]
        consumed += [oid for n in noms for oid in [n["occurrence_id"], *n["negation_occurrence_ids"]]]
        assert len(consumed) == len(set(consumed))
        if (len(noms) == 1 and noms[0]["negation_occurrence_ids"] and noms[0]["args"] == [{"var": "h"}]
                and len(exists) == 1 and len(uses) == 2
                and any(n["synset_id"] == "of-6" and n["args"] == [{"var": "q"}, {"var": "h"}] for n in uses)
                and any(n["synset_id"] == "oewn-04731092-n" and n["args"] == [{"var": "q"}] for n in uses)):
            matches.append((index, row))
    assert len(matches) == 2
    index, selected = next((i, r) for i, r in matches if r["formula"]["rhs"]["op"] == "and")
    expansion = expand_nominalizations(selected["formula"], prepared)
    expanded_nodes = list(nodes(expansion))
    iff = next(n for n in expanded_nodes if n.get("op") == "iff")
    assert iff["right"]["op"] == "use" and iff["right"]["synset_id"] == "oewn-00024432-r"
    assert iff["right"]["args"][0]["op"] == "exists"
    assert any(n.get("name") == "Agent" for n in nodes(iff["right"]["args"][0]["body"]))
    write(HERE / "selected.json", {"status": "MATCHED_USER_CONFIRMED_NOM_SEMANTICS", "candidate_line": index,
        "candidate_id": selected["candidate_id"], "candidate": selected,
        "readable_formula": "Immobility(q) IFF Quality(q) AND EXISTS h:E (Of(q,h) AND Nom[not moving](h))",
        "equivalent_candidate_ids": [r["candidate_id"] for _, r in matches],
        "equivalence_reason": "Quality(q) does not depend on h, so it may occur outside or inside the licensed exists h.",
        "independent_model_review_performed": False, "published": False})
    write(HERE / "expanded.json", expansion)
    # A negative nominal property is not simply the negation of another nominal.
    moving_by_subject = [True, False]
    unrelated_property_by_subject = [False, False]
    nominal_positive = all(h == m for h, m in zip(unrelated_property_by_subject, moving_by_subject))
    nominal_negative = all(h == (not m) for h, m in zip(unrelated_property_by_subject, moving_by_subject))
    assert (not nominal_positive) is True and nominal_negative is False
    output = {"candidate_count": len(rows), "independent_recursive_oracle_count": len(expected),
              "whole_candidate_sets_identical": True, "uncapped_exhaustion": True,
              "lhs_unchanged": True, "correct_formula_found": True, "selected_line": index,
              "selected_candidate_id": selected["candidate_id"], "equivalent_candidate_count": len(matches),
              "no_internal_symbols_in_authored_rhs": True, "source_occurrences_not_duplicated": True,
              "expanded_not_outside_event_exists": True, "full_move_agent_preserved": True,
              "scope_counterexample": {"moving_by_subject": moving_by_subject,
                  "Holds_of_unrelated_property": unrelated_property_by_subject,
                  "Not_Nom_moving": not nominal_positive, "Nom_not_moving": nominal_negative},
              "basis_rhs_supplied": False, "published": False,
              "checks": "Independent resource-partition oracle, static gates, exact binding/occurrence checks and user-confirmed composition template; not a new independent model review."}
    write(HERE / "verification.json", output)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
