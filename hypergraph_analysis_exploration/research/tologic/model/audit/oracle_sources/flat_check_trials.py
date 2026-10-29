"""Independent flat-grammar completeness oracle and exact containment check.

The production enumerator searches arbitrary resource/scope trees. These three
small trials have no binders. Here a separate Cartesian-product/power-set oracle
exhausts the flat grammar, then compares the entire candidate sets, not counts.
Only interface LHS patterns are substituted; no basis RHS is read or expanded.
"""
from __future__ import annotations

from itertools import combinations, product
import json

from build_trials import BY_ID, CASES, HERE, read, sha, write


def flat_atoms(node):
    if node["op"] == "and":
        return [atom for child in node["args"] for atom in flat_atoms(child)]
    if node["op"] == "use":
        return [("use", node["synset_id"], node["usage_id"], tuple(a["var"] for a in node["args"]))]
    assert node["op"] == "struct"
    return [("struct", node["name"], tuple(a["var"] for a in node["args"]))]


def key(atoms):
    return tuple(sorted(atoms))


def subsets(atoms):
    for size in range(len(atoms) + 1):
        yield from combinations(atoms, size)


def oracle(request):
    parameters = request["usage"]["parameters"]
    assert all(isinstance(p["type"], str) for p in parameters)
    assert not request["usage"]["witnesses"] and "binding_plan" not in request["usage"]
    assert "structural_budgets" not in request["enumeration"]
    typed = {kind: [p["name"] for p in parameters if p["type"] == kind] for kind in ("E", "V", "Time")}
    external = {p["name"] for p in parameters}
    structures = []
    for name, objects in [("Agent", typed["E"]), ("Theme", typed["E"] + typed["V"]), ("Happen", typed["Time"])]:
        structures.extend(("struct", name, (e, x)) for e in typed["V"] for x in objects)
    calls = []
    by_occurrence = {o["occurrence_id"]: o for o in request["source"]["occurrences"]}
    heads = {d["head_occurrence_id"]: d["parameter"] for d in request["usage"]["determiners"]}
    for resource in request["enumeration"]["lexical"]:
        occurrence = by_occurrence[resource["occurrence_id"]]
        choices = [None] if resource["min_calls"] == 0 and resource["occurrence_id"] not in heads else []
        for interface in request["interfaces"].values():
            if interface["synset_id"] != occurrence["synset_id"]:
                continue
            for args in product(*(typed[p["type"]] for p in interface["parameters"])):
                if resource["occurrence_id"] in heads and heads[resource["occurrence_id"]] not in args:
                    continue
                choices.append(("use", interface["synset_id"], interface["usage_id"], args))
        calls.append(choices)
    result = set()
    for selected in product(*calls):
        lexical = [call for call in selected if call is not None]
        for structural in subsets(structures):
            atoms = lexical + list(structural)
            mentioned = {v for atom in atoms for v in atom[-1]}
            if atoms and mentioned == external:
                result.add(key(atoms))
    return result, structures


def instantiate_pattern(node, binding, sid):
    if node["op"] == "and":
        return [a for child in node["args"] for a in instantiate_pattern(child, binding, sid)]
    args = tuple(binding[a["var"]] for a in node["args"])
    return [("basis_target", sid, args)] if node["op"] == "target" else [("struct", node["name"], args)]


def realized_atoms(raw, interfaces):
    result = []
    for atom in raw:
        if atom[0] == "struct":
            result.append(atom)
        else:
            _, sid, uid, args = atom
            interface = interfaces[sid + "::" + uid]
            binding = dict(zip((p["name"] for p in interface["parameters"]), args))
            result.extend(instantiate_pattern(interface["lhs"], binding, sid))
    # Associativity, commutativity and idempotence of conjunction only.
    return frozenset(result)


def node_count(node):
    if isinstance(node, list):
        return sum(node_count(n) for n in node)
    if isinstance(node, dict):
        return 1 + sum(node_count(n) for n in node.values())
    return 0


def check(case):
    name = case["name"]
    request = read(HERE / "inputs" / (name + ".json"))
    run = HERE / "runs" / case.get("run_directory", name)
    report = read(run / "report.json")
    rows = [json.loads(line) for line in (run / "candidates.jsonl").read_text(encoding="utf-8").splitlines()]
    assert report["status"] == "COMPLETE" and report["exhausted"] and report["max_candidates"] is None
    assert all(row["interface_gate"]["passed"] for row in rows)
    assert all(not row["semantic_acceptance"] and not row["publishable"] for row in rows)
    expected, structures = oracle(request)
    generated = {key(flat_atoms(row["formula"]["rhs"])) for row in rows}
    assert len(generated) == len(rows) == report["candidate_count"]
    assert generated == expected, {"missing": expected - generated, "extra": generated - expected}
    reference_calls = []
    for interface in request["interfaces"].values():
        binding = case["reference_bindings"][interface["usage_id"]]
        reference_calls.append(("use", interface["synset_id"], interface["usage_id"],
                                tuple(binding[p["name"]] for p in interface["parameters"])))
    reference = realized_atoms(reference_calls, request["interfaces"])
    matches = []
    rejections = []
    for index, row in enumerate(rows, 1):
        actual = realized_atoms(flat_atoms(row["formula"]["rhs"]), request["interfaces"])
        if actual == reference:
            matches.append((index, row))
        else:
            # Ground atoms can be independent under the supplied, axiom-free
            # interfaces. A differing atom supplies a countervaluation. This
            # does not assert anything about a future completed basis theory.
            rejections.append({"candidate_id": row["candidate_id"],
                               "missing_required_atoms": sorted(reference - actual),
                               "additional_unentailed_atoms": sorted(actual - reference)})
    assert matches, "Correct reference formula absent from exhaustive candidates"
    index, selected = min(matches, key=lambda pair: (node_count(pair[1]["formula"]["rhs"]), pair[0]))
    selection = {"status": "REFERENCE_CONTAINMENT_CONFIRMED_PENDING_INDEPENDENT_SEMANTIC_REVIEW",
                 "formula_readable": case["selected_readable"], "candidate_line": index,
                 "candidate_id": selected["candidate_id"], "candidate": selected,
                 "equivalent_candidate_ids": [row["candidate_id"] for _, row in matches],
                 "equivalence_method": "Substitute complete basis LHS; compare conjunction atom sets modulo AND associativity/commutativity/idempotence. No basis RHS expansion or unprovided lexical/role axioms.",
                 "basis_rhs_supplied": False, "published": False}
    review_path = HERE / "formula_review.json"
    if review_path.exists():
        review = read(review_path)
        assert review["decision"] == "ACCEPT"
        reviewed = next(r for r in review["rationale"]["cases"] if r["rationale"]["case"] == name)
        assert reviewed["decision"] == "ACCEPT"
        evidence = reviewed["rationale"]
        current_input_hash = sha(HERE / "inputs" / (name + ".json"))
        if evidence["hashes"]["input_file_sha256"] == current_input_hash:
            assert evidence["selected_candidate_id"] == selected["candidate_id"]
            assert evidence["selected_candidate_ast"] == selected["formula"]
            assert set(evidence["equivalent_candidate_ids"]) == set(selection["equivalent_candidate_ids"])
            assert evidence["hashes"]["candidates_file_sha256"] == sha(run / "candidates.jsonl")
            selection["status"] = "SELECTED_AND_INDEPENDENTLY_ACCEPTED_FOR_SUPPLIED_INTERFACE_TRIAL"
            selection["independent_review"] = {"path": "../formula_review.json", "sha256": sha(review_path),
                                               "decision": "ACCEPT", "scope": review["rationale"]["scope"]}
        else:
            assert case.get("revision_id") == "together_event_only_user_correction"
            selection["status"] = "SELECTED_FOR_USER_CORRECTED_USAGE_STATICALLY_CHECKED"
            selection["revision_id"] = case["revision_id"]
            selection["run_directory"] = "../runs/" + case["run_directory"]
            selection["previous_independent_review"] = {
                "path": "../formula_review.json", "sha256": sha(review_path),
                "applicability": "SUPERSEDED_INPUT_NOT_REUSED_AS_CURRENT_ACCEPTANCE",
                "reason": "User corrected this adverb usage to depend only on e; g remains in sentence context.",
                "reviewed_input_sha256": evidence["hashes"]["input_file_sha256"],
                "current_input_sha256": current_input_hash,
            }
    write(HERE / "selected" / (name + ".json"), selection)
    write(HERE / "rejection_analysis" / (name + ".json"), rejections)
    return {"name": name, "synset_id": case["sid"], "candidate_count": len(rows),
            "independent_oracle_count": len(expected), "whole_candidate_sets_identical": True,
            "search_exhausted": True, "all_interface_gates_passed": True,
            "available_structural_atoms": structures,
            "canonical_LHS_expansion_classes": len({realized_atoms(flat_atoms(row["formula"]["rhs"]), request["interfaces"]) for row in rows}),
            "correct_formula_present": True, "matching_candidate_count": len(matches),
            "independent_semantic_selection_matches": "independent_review" in selection,
            **({"run_directory": "runs/" + case["run_directory"], "revision_id": case["revision_id"]}
               if "revision_id" in case else {}),
            "selected_candidate_id": selected["candidate_id"], "selected_candidate_line": index,
            "selected_readable": case["selected_readable"],
            "input_sha256": sha(HERE / "inputs" / (name + ".json")),
            "candidates_sha256": sha(run / "candidates.jsonl")}


def main():
    results = [check(case) for case in CASES]
    output = {"status": "ALL_THREE_EXHAUSTIVE_SETS_MATCH_INDEPENDENT_ORACLE",
              "scope": "These binder-free supplied usage contracts only; not a proof for arbitrary semantics or future basis implementations.",
              "results": results, "total_candidates": sum(r["candidate_count"] for r in results),
              "published": False, "basis_rhs_supplied": False}
    write(HERE / "containment_check.json", output)
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
