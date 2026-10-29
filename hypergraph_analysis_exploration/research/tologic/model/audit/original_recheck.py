"""Fresh exhaustive enumeration, followed by matching user-approved answers.

No answer AST is passed to the search. Source, typed LHS interfaces, argument
inventory, Nom rules and event ownership remain fixed; semantic scope locks
are removed from a copy. The original accepted artifacts are never modified.
"""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
STAGING = PROJECT / "staging"
SIMPLE = STAGING / "first_layer_simple_trials_20261014"
SCOPE = STAGING / "scope_trials_20261014"
sys.path.insert(0, str(PROJECT / "src"))

from tologic_v3.common import canonical_hash
from tologic_v3.enumeration import enumerate_request

CASES = [(name, SIMPLE) for name in ("bear", "life", "hand_in_hand")] + [
    (name, SCOPE) for name in ("all_along", "immobility", "impermissible")]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def load_helper(name, path, companion=None):
    """Load existing standalone oracle functions without invoking their mains."""
    previous = sys.modules.pop(companion, None) if companion else None
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)
        if companion:
            sys.modules.pop(companion, None)
            if previous is not None:
                sys.modules[companion] = previous


def produce():
    audits = []
    for name, folder in CASES:
        path = folder / "inputs" / (name + ".json")
        original = read(path)
        request = deepcopy(original)
        assert not request["usage"].get("binding_plan"), "Do not import a selected answer's binding plan"
        assert not request["enumeration"].get("slot_scopes"), "A scope-slot lock must be explicitly reviewed"
        assert not request["enumeration"].get("required_structures")
        assert not request["enumeration"].get("structural_budgets")
        assert all(not row.get("bindings") and row.get("scope_id") is None
                   for row in request["enumeration"]["lexical"])
        changes = []
        for i, binding in enumerate(request["enumeration"].get("event_bindings", [])):
            if "within" in binding:
                changes.append({"path": f"enumeration.event_bindings[{i}].within",
                                "previous": binding.pop("within"),
                                "reason": "Enumerate event-exists and lexical negation scope, rather than selecting their order before search."})
        assert request["source"] == original["source"]
        assert request["usage"] == original["usage"]
        assert request["interfaces"] == original["interfaces"]
        assert all("rhs" not in interface and "primitives" not in interface
                   for interface in request["interfaces"].values())
        write(HERE / "accepted_inputs" / (name + ".json"), original)
        write(HERE / "inputs" / (name + ".json"), request)
        report = enumerate_request(request, HERE / "runs" / name, project=PROJECT)
        audits.append({"case": name, "original_input": str(path), "original_input_sha256": sha(path),
                       "new_input_sha256": sha(HERE / "inputs" / (name + ".json")),
                       "scope_changes": changes, "target_interfaces_unchanged": True,
                       "no_fixed_binding_plan": True, "no_slot_mapping": True,
                       "no_structural_caps": True, "no_rhs_constraints": True,
                       "all_event_scope_within_constraints_removed": True,
                       "scope_templates_are_typed_binders_not_slot_assignments": True,
                       "prose_and_syntax_preserved_as_evidence": True,
                       "candidate_count": report["candidate_count"]})
        print(json.dumps({"case": name, "status": report["status"], "count": report["candidate_count"]}), flush=True)
    write(HERE / "scope_audit.json", audits)


def scope_examples(name, rows):
    def collect(predicate):
        selected = [(i, row) for i, row in enumerate(rows, 1) if predicate(row["formula"]["rhs"])]
        return {"count": len(selected), "example_line": selected[0][0] if selected else None,
                "example_candidate_id": selected[0][1]["candidate_id"] if selected else None,
                "example_readable": selected[0][1]["readable_formula"] if selected else None}
    def is_not(n):
        return n.get("op") == "use" and n.get("synset_id") == "oewn-00024432-r"
    def contains(n, predicate):
        return any(predicate(x) for x in walk(n))
    def contains_time(n):
        return contains(n, lambda x: x.get("op") == "use" and x.get("synset_id") == "oewn-00028468-n")
    if name == "all_along":
        result = {"time_in_S": collect(lambda n: contains(n, lambda x: x.get("op") == "use"
                            and x.get("synset_id") == "supplied-all-quantifier" and contains_time(x["args"][1]))),
                  "time_in_P": collect(lambda n: contains(n, lambda x: x.get("op") == "use"
                            and x.get("synset_id") == "supplied-all-quantifier" and contains_time(x["args"][2])))}
    elif name == "immobility":
        result = {"not_inside_Nom": collect(lambda n: contains(n, lambda x: x.get("op") == "nom" and bool(x["negation_occurrence_ids"]))),
                  "not_outside_Nom": collect(lambda n: contains(n, lambda x: is_not(x) and contains(x["args"][0], lambda y: y.get("op") == "nom"))),
                  "not_outside_exists_h": collect(lambda n: contains(n, lambda x: is_not(x) and contains(x["args"][0], lambda y: y.get("op") == "exists"))),
                  "exists_h_outside_not": collect(lambda n: contains(n, lambda x: x.get("op") == "exists" and contains(x["body"], is_not)))}
    elif name == "impermissible":
        result = {"not_outside_exists_r": collect(lambda n: is_not(n) and n["args"][0].get("op") == "exists"),
                  "exists_r_outside_not": collect(lambda n: n.get("op") == "exists" and contains(n["body"], is_not)),
                  "without_not": collect(lambda n: not contains(n, is_not))}
    else:
        return {}
    assert all(row["count"] > 0 for row in result.values()), (name, result)
    return result


def verify():
    simple = load_helper("recheck_flat_oracle", SIMPLE / "check_trials.py", "build_trials")
    all_scope = load_helper("recheck_all_oracle", SCOPE / "verify_coverage.py")
    nominal = load_helper("recheck_nom_oracle", SCOPE / "revisions/nominalized_verb/verify_trial.py", "build_trial")
    event = load_helper("recheck_event_oracle", SCOPE / "revisions/verb_event_closure/verify_trial.py", "build_trial")
    results = []
    for name, folder in CASES:
        run = HERE / "runs" / name
        request = read(HERE / "inputs" / (name + ".json"))
        report = read(run / "report.json")
        rows = [json.loads(line) for line in (run / "candidates.jsonl").read_text(encoding="utf-8").splitlines()]
        assert report["status"] == "COMPLETE" and report["exhausted"] and report["max_candidates"] is None
        assert report["input_hash"] == canonical_hash(request)
        assert len(rows) == report["candidate_count"]
        assert all(row["interface_gate"]["passed"] for row in rows)
        # Answers are only read after the six independent search runs finish.
        reference_path = folder / "selected" / (name + ".json")
        reference = read(reference_path)
        expected_formula = reference["candidate"]["formula"]
        expected_id = reference["candidate_id"]
        assert expected_id == canonical_hash(expected_formula)
        matches = [(i, row) for i, row in enumerate(rows, 1)
                   if row["candidate_id"] == expected_id and row["formula"] == expected_formula]
        assert len(matches) == 1, f"Approved exact formula missing: {name}"
        assert all(row["formula"]["lhs"] == expected_formula["lhs"]
                   and row["formula"]["parameters"] == expected_formula["parameters"] for row in rows)
        if folder == SIMPLE:
            expected, _ = simple.oracle(request)
            observed = {simple.key(simple.flat_atoms(r["formula"]["rhs"])) for r in rows}
        elif name == "all_along":
            contract = all_scope.Contract(name, HERE / "inputs" / (name + ".json"))
            expected = {all_scope.formula_key(contract.formula(rhs), contract) for rhs in all_scope.all_along(contract)}
            observed = {all_scope.formula_key(r["formula"], contract) for r in rows}
        elif name == "immobility":
            nid = request["enumeration"]["nominalizations"][0]["nominalization_id"]
            expected = set(nominal.oracle(request, report, nid))
            observed = {nominal.key(r["formula"]["rhs"]) for r in rows}
        else:
            generated, _, _ = event.independent_oracle(request, constrained=False)
            expected = set(generated)
            observed = {event.key(r["formula"]["rhs"]) for r in rows}
        assert expected == observed and len(observed) == len(rows), name
        line, selected = matches[0]
        write(HERE / "approved_references" / (name + ".json"), reference)
        result = {"case": name, "candidate_count": len(rows), "complete": True,
                  "exact_approved_formula_present": True, "approved_candidate_id": expected_id,
                  "matched_line": line, "parameters_and_lhs_unchanged": True,
                  "all_static_checks_passed": True, "whole_set_equals_separate_oracle": True,
                  "oracle_candidate_count": len(expected), "scope_alternatives": scope_examples(name, rows),
                  "reference_path": str(reference_path), "reference_sha256": sha(reference_path),
                  "input_sha256": sha(HERE / "inputs" / (name + ".json")),
                  "candidate_file_sha256": sha(run / "candidates.jsonl")}
        write(HERE / "matches" / (name + ".json"), {**result, "matched_candidate": selected})
        results.append(result)
    protected = [p for _, folder in CASES for p in (folder / "inputs", folder / "selected")]
    audits = read(HERE / "scope_audit.json")
    assert all(sha(Path(a["original_input"])) == a["original_input_sha256"] for a in audits)
    policy_paths = ["config/policy.json", "config/structural_relations.json", "config/nominalization.json",
                    "config/event_closure.json", "specification/ENUMERATION.md"]
    code_paths = sorted((PROJECT / "src/tologic_v3").glob("*.py"))
    output = {"status": "ALL_APPROVED_FORMULAS_FOUND_AFTER_FRESH_OPEN_SCOPE_ENUMERATION",
              "results": results, "total_candidates": sum(r["candidate_count"] for r in results),
              "scope_was_not_semantically_preselected": True,
              "answer_loaded_only_after_search_completed": True,
              "unchanged_sources_interfaces_and_target_parameters": True,
              "basis_rhs_supplied": False, "new_semantic_review_needed_for_this_containment_check": False,
              "published": False,
              "frozen_policies": {p: sha(PROJECT / p) for p in policy_paths},
              "search_code": {str(p.relative_to(PROJECT)): sha(p) for p in code_paths}}
    write(HERE / "verification.json", output)
    print(json.dumps({"status": output["status"], "total": output["total_candidates"],
                      "matches": {r["case"]: {"count": r["candidate_count"], "line": r["matched_line"]} for r in results}}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    if "--verify-only" not in sys.argv:
        produce()
    verify()
