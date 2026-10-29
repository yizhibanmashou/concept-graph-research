"""Independent finite scope oracle and result selection for event closure."""
from copy import deepcopy
from itertools import product
import json

from build_trial import HERE, STUDY, PROJECT, read, write, sha
from tologic_v3.common import canonical_hash
from tologic_v3.enumeration_input import prepare_request
from tologic_v3.enumeration_interfaces import instantiate_interface_call


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def key(node):
    def normalize(n):
        if not isinstance(n, dict):
            return n
        result = {k: [normalize(x) for x in v] if isinstance(v, list) else normalize(v) for k, v in n.items()}
        if result.get("op") == "and":
            flat = []
            for child in result["args"]:
                flat.extend(child["args"] if child.get("op") == "and" else [child])
            flat.sort(key=lambda x: json.dumps(x, sort_keys=True))
            return flat[0] if len(flat) == 1 else {"op": "and", "args": flat}
        return result
    return json.dumps(normalize(node), sort_keys=True, separators=(",", ":"))


def conj(args):
    assert args
    return args[0] if len(args) == 1 else {"op": "and", "args": args}


def independent_oracle(request, constrained):
    interfaces = {p["synset_id"]: p for p in request["interfaces"].values()}
    occurrences = {o["text"]: o for o in request["source"]["occurrences"]}
    def use(word, args):
        source = occurrences[word]
        interface = interfaces[source["synset_id"]]
        digest = canonical_hash({k: interface.get(k) for k in ("synset_id", "usage_id", "is_basis", "parameters", "lhs", "voice")})
        return {"op": "use", "synset_id": source["synset_id"], "usage_id": interface["usage_id"],
                "interface_hash": digest, "occurrence_id": source["occurrence_id"], "args": args}
    r, b = {"var": "r"}, {"var": "b"}
    implicit = {"op": "struct", "name": "ImplicitSubj", "args": [r]}
    atoms = [{"op": "struct", "name": name, "args": args} for name, args in [
        ("Agent", [r,b]), ("Agent", [r,implicit]), ("Theme", [r,b]), ("Theme", [r,r])]]
    call = use("permitted", [r,b])
    def event(body):
        return {"op": "exists", "variables": [{"name": "r", "type": "V"}],
                "origin": "verb_event", "occurrence_id": occurrences["permitted"]["occurrence_id"], "body": body}
    def neg(body):
        return use("not", [body])
    result = {}
    def save(node):
        result[key(node)] = node
    for mask in product([False, True], repeat=4):
        body = conj([call] + [atom for atom, on in zip(atoms, mask) if on])
        save(neg(event(body)))
        if not constrained:
            save(event(body))
    if not constrained:
        # The existential surrounds Not; each atom is absent/outside/inside Not.
        for locations in product([-1,0,1], repeat=4):
            outside = [a for a, pos in zip(atoms, locations) if pos == 0]
            inside = [a for a, pos in zip(atoms, locations) if pos == 1]
            save(event(conj(outside + [neg(conj([call] + inside))])))
            if inside:
                save(event(conj([call] + outside + [neg(conj(inside))])))
    return result, neg(event(call)), call


def realized_atoms(node, context):
    if node.get("op") == "and":
        return set().union(*(realized_atoms(child, context) for child in node["args"]))
    if node.get("op") == "use":
        return realized_atoms(instantiate_interface_call(node, context), context)
    assert node.get("op") in {"struct", "target"}
    return {key(node)}


def main():
    checks, all_rows = {}, {}
    frozen = read(HERE / "lhs_frozen.json")
    for name, input_file in [("constrained", "input.json"), ("open_scope", "open_scope_input.json")]:
        request = read(HERE / input_file)
        expected, wanted, call = independent_oracle(request, name == "constrained")
        run = HERE / "runs" / name
        report = read(run / "report.json")
        rows = [json.loads(line) for line in (run / "candidates.jsonl").read_text(encoding="utf-8").splitlines()]
        observed = {key(row["formula"]["rhs"]) for row in rows}
        assert observed == set(expected), {"missing": len(set(expected) - observed), "extra": len(observed - set(expected))}
        assert len(observed) == len(rows) == report["candidate_count"]
        assert report["complete"] and report["exhausted"] and report["max_candidates"] is None
        assert key(wanted) in observed
        for row in rows:
            assert row["interface_gate"]["passed"]
            assert row["formula"]["lhs"] == frozen["lhs"] and row["formula"]["parameters"] == frozen["parameters"]
            assert sum(n.get("op") == "exists" for n in nodes(row["formula"]["rhs"])) == 1
            assert not any(n.get("op") in {"nom", "nom_internal"} for n in nodes(row["formula"]["rhs"]))
        checks[name] = {"candidate_count": len(rows), "whole_candidate_sets_equal": True,
                       "uncapped_exhaustion": True, "intended_formula_present": True,
                       "input_sha256": sha(HERE / input_file), "candidates_sha256": sha(run / "candidates.jsonl")}
        all_rows[name] = rows
    constrained_ids = {r["candidate_id"] for r in all_rows["constrained"]}
    assert constrained_ids <= {r["candidate_id"] for r in all_rows["open_scope"]}
    prepared = prepare_request(read(HERE / "input.json"), PROJECT)
    baseline = realized_atoms(call, prepared["context"])
    equivalents = []
    for line, row in enumerate(all_rows["constrained"], 1):
        rhs = row["formula"]["rhs"]
        assert rhs["op"] == "use" and rhs["synset_id"] == "oewn-00024432-r"
        quantifier = rhs["args"][0]
        assert quantifier["op"] == "exists"
        if realized_atoms(quantifier["body"], prepared["context"]) == baseline:
            equivalents.append((line, row))
    assert len(equivalents) == 4
    line, selected = next((i, row) for i, row in equivalents if key(row["formula"]["rhs"]) == key(wanted))
    readable = "Impermissible(b:E) IFF Not(EXISTS r:V (Permit(r) AND Agent(r,ImplicitSubj(r)) AND Theme(r,b)))"
    result = {"status": "MATCHED_USER_APPROVED_EVENT_CLOSURE", "case": "impermissible", "synset_id": "oewn-01765698-a",
              "candidate_count": 16, "open_scope_candidate_count": 178, "candidate_id": selected["candidate_id"],
              "selected_line": line, "candidate": selected, "readable_formula": readable,
              "run": "revisions/verb_event_closure/runs/constrained",
              "equivalent_candidate_ids": [row["candidate_id"] for _, row in equivalents],
              "equivalence_reason": "Other matching variants only repeat Agent(r,ImplicitSubj(r)) and/or Theme(r,b), already included in the complete Permit LHS.",
              "input_sha256": checks["constrained"]["input_sha256"], "candidates_sha256": checks["constrained"]["candidates_sha256"],
              "independent_model_review_performed": False, "published": False}
    write(HERE / "selected.json", result)
    expanded = deepcopy(selected["formula"])
    expanded["rhs"]["args"][0]["body"] = instantiate_interface_call(call, prepared["context"])
    write(HERE / "expanded_lhs_calls.json", {"status": "COMPLETE_DEPENDENCY_LHS_INSTANTIATED", "formula": expanded,
                                            "basis_rhs_supplied": False, "published": False})
    old_nom = STUDY / "revisions/nominalized_verb/runs/current/candidates.jsonl"
    new_nom = HERE / "regressions/immobility/candidates.jsonl"
    old_ids = {json.loads(line)["candidate_id"] for line in old_nom.read_text(encoding="utf-8").splitlines()}
    new_ids = {json.loads(line)["candidate_id"] for line in new_nom.read_text(encoding="utf-8").splitlines()}
    assert old_ids == new_ids and len(new_ids) == 122
    verification = {"status": "EVENT_CLOSURE_VERIFIED_AND_NOM_UNCHANGED", "checks": checks,
        "constrained_set_is_subset_of_open_scope": True, "selected_candidate_id": selected["candidate_id"],
        "selected_line": line, "equivalent_candidate_count": 4,
        "immobility_regression": {"count": 122, "all_candidate_ids_identical": True},
        "target_lhs": "Impermissible(b:E)", "no_target_slot_added": True,
        "independent_model_review_performed": False, "published": False}
    write(HERE / "verification.json", verification)
    print(json.dumps(verification, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
