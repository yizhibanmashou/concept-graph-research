"""Independent whole-set finite grammar check for these three interface trials.

This script does not import or invoke ToLogicV3. Enumeration is independently
authored from specification/ENUMERATION.md and these input contracts. The only
implementation convention reproduced is the serialization payload for interface
hash annotations (enumeration_input.py lines 322-326 and common.py lines 33-35).
Run: python -B -X utf8 <this_file>

The oracle is deliberately limited to the three checked input shapes. It is a
local exhaustive software comparison, not semantic acceptance or a theorem
about the general production enumerator.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
from itertools import combinations, product, permutations
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent.parent


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(dump(value).encode("utf-8")).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(condition, reason):
    if not condition:
        raise ValueError("Unsupported or changed input/AST: " + reason)


def v(name):
    return {"var": name}


def struct(name, *args):
    return {"op": "struct", "name": name, "args": list(args)}


def conjunction(args):
    require(bool(args), "empty proposition")
    flat = []
    for arg in args:
        flat.extend(arg["args"] if arg.get("op") == "and" else [arg])
    return flat[0] if len(flat) == 1 else {"op": "and", "args": flat}


def lam(name, kind, scope, body):
    return {"op": "lambda", "parameters": [{"name": name, "type": kind}],
            "scope_id": scope, "body": body}


class Contract:
    def __init__(self, name, input_path=None):
        self.name = name
        self.path = input_path or ROOT / "inputs" / (name + ".json")
        self.input = read(self.path)
        self.source = self.input["source"]
        self.usage = self.input["usage"]
        self.enum = self.input["enumeration"]
        require(self.input["schema_version"] == "v3.enumeration-interfaces-input/1", "schema")
        require(not self.usage.get("binding_plan"), "fixed binding plan")
        require(not self.usage.get("witnesses"), "witnesses")
        require(not self.usage.get("determiner_exclusions"), "determiner exclusions")
        require(set(self.enum) <= {"lexical", "lhs_structures", "quantifier_inventory_complete", "scope_templates"}, "enumeration options")
        require(self.enum.get("quantifier_inventory_complete") is True, "quantifier inventory")
        self.occ = {x["text"]: x for x in self.source["occurrences"]}
        require(len(self.occ) == len(self.source["occurrences"]), "repeated surface occurrences")
        require(set(self.usage["occurrence_ids"]) == {x["occurrence_id"] for x in self.occ.values()}, "active occurrences")
        require(all(not x.get("source_occurrence_ids") for x in self.usage.get("parameter_spans", [])), "parameter lexical exclusions")
        for row in self.enum["lexical"]:
            require(set(row) == {"occurrence_id", "min_calls", "max_calls"}
                    and row["min_calls"] == 0 and row["max_calls"] == 1, "lexical restrictions")
        self.hashes = {}
        assumptions = {x["synset_id"]: x for x in self.input.get("interface_assumptions", [])}
        for key, interface in self.input["interfaces"].items():
            require(interface["rhs_status"] == "pending" and "rhs" not in interface, "interface-only mode")
            payload = {field: interface.get(field) for field in
                       ("synset_id", "usage_id", "is_basis", "parameters", "lhs", "voice")}
            if interface["synset_id"] in assumptions:
                payload["interface_assumption"] = assumptions[interface["synset_id"]]
            self.hashes[key] = digest(payload)
        self.known_scopes = {x["scope_id"] for x in self.enum.get("scope_templates", [])}
        self.lhs = conjunction(
            [{"op": "target", "args": [v(x) for x in self.usage["target_arguments"]]}]
            + [struct(x["name"], *(v(a) for a in x["arguments"]))
               for x in self.enum["lhs_structures"]])

    def interface(self, word, parameter_types):
        occurrence = self.occ[word]
        matches = [x for x in self.input["interfaces"].values()
                   if x["synset_id"] == occurrence["synset_id"]]
        require(len(matches) == 1, "multiple or absent interface choices")
        row = matches[0]
        require([x["type"] for x in row["parameters"]] == parameter_types, "interface parameter types")
        require(row["lhs"]["op"] == "target", "nontrivial interface LHS")
        require(set(x["var"] for x in row["lhs"]["args"])
                == set(x["name"] for x in row["parameters"]), "interface LHS arguments")
        return row

    def use(self, word, args):
        occurrence = self.occ[word]
        interface = next(x for x in self.input["interfaces"].values()
                         if x["synset_id"] == occurrence["synset_id"])
        key = interface["synset_id"] + "::" + interface["usage_id"]
        return {"op": "use", "synset_id": interface["synset_id"],
                "usage_id": interface["usage_id"], "interface_hash": self.hashes[key],
                "occurrence_id": occurrence["occurrence_id"], "args": args}

    def formula(self, rhs):
        return {"schema_version": "v3.interface-formula-candidate/1",
                "synset_id": self.source["synset_id"], "usage_id": self.usage["usage_id"],
                "parameters": self.usage["parameters"], "lhs": self.lhs,
                "rhs": rhs, "primitives": []}


def canonical_ast(node, known_scopes, frames=(), slot=None):
    """Alpha-normalize binders and flatten/sort same-region AND only.

    Occurrence IDs, argument order, interface hashes and named input scope IDs
    remain literal. Generated scope names become their owning occurrence/slot.
    Bound variables use de Bruijn distance plus parameter position; free variable
    names remain literal. Duplicated conjuncts are *not* removed.
    """
    if set(node) == {"var"}:
        for distance, frame in enumerate(reversed(frames)):
            if node["var"] in frame:
                return ("bound", distance, frame.index(node["var"]))
        return ("free", node["var"])
    op = node["op"]
    if op == "and":
        require(set(node) == {"op", "args"} and len(node["args"]) >= 2, "AND shape")
        flat = []
        for arg in node["args"]:
            norm = canonical_ast(arg, known_scopes, frames)
            flat.extend(norm[1] if norm[0] == "and" else [norm])
        return ("and", tuple(sorted(flat, key=dump)))
    if op == "lambda":
        require(set(node) == {"op", "parameters", "scope_id", "body"}, "lambda shape")
        require(slot is not None, "lambda must occupy a lexical argument slot")
        names = tuple(x["name"] for x in node["parameters"])
        require(len(names) == len(set(names)), "lambda names")
        sid = node["scope_id"]
        require(sid in known_scopes or sid.startswith("enum_scope_")
                or sid == "oracle_generated", "unrecognized scope")
        scope = ("known", sid) if sid in known_scopes else ("generated_slot", slot)
        types = tuple(dump(x["type"]) for x in node["parameters"])
        return ("lambda", scope, types,
                canonical_ast(node["body"], known_scopes, frames + (names,)))
    if op == "use":
        require(set(node) == {"op", "synset_id", "usage_id", "interface_hash", "occurrence_id", "args"}, "use shape")
        identity = (node["occurrence_id"], node["synset_id"], node["usage_id"], node["interface_hash"])
        return ("use", identity, tuple(canonical_ast(arg, known_scopes, frames,
                       (node["occurrence_id"], node["usage_id"], i))
                       for i, arg in enumerate(node["args"])))
    if op in {"struct", "target"}:
        require(set(node) == ({"op", "name", "args"} if op == "struct" else {"op", "args"}), "atomic shape")
        return (op, node.get("name"), tuple(canonical_ast(x, known_scopes, frames) for x in node["args"]))
    raise ValueError("Unsupported AST op: " + op)


def formula_key(formula, contract):
    require(set(formula) == {"schema_version", "synset_id", "usage_id", "parameters", "lhs", "rhs", "primitives"}, "formula fields")
    result = dict(formula)
    for side in ("lhs", "rhs"):
        result[side] = canonical_ast(formula[side], contract.known_scopes)
    return dump(result)


def check_input_shape(c, words, parameter_types, lexical_words, voice):
    require(set(c.occ) == set(words), "source words")
    require([(x["name"], x["type"]) for x in c.usage["parameters"]] == parameter_types, "external parameters")
    require(c.usage["voice"] == voice, "voice")
    require(c.usage["target_arguments"] == [parameter_types[0][0]], "target arguments")
    require({x["occurrence_id"] for x in c.enum["lexical"]}
            == {c.occ[x]["occurrence_id"] for x in lexical_words}, "lexical inventory")


def all_along(c):
    context_subject = any(x["name"] == "s" for x in c.usage["parameters"])
    params = [("e", "V"), ("s", "E")] if context_subject else [("e", "V")]
    check_input_shape(c, ["all", "the", "time"], params, ["all", "time"], "active")
    c.interface("all", ["World", {"arrow": ["Time", "Prop"]}, {"arrow": ["Time", "Prop"]}])
    c.interface("time", ["Time"])
    expected_lhs = [{"name": "Agent", "arguments": ["e", "s"]}] if context_subject else []
    require(c.enum["lhs_structures"] == expected_lhs, "LHS structures")
    require(c.enum["scope_templates"] == [
        {"scope_id": "time_scope", "parent_scope": None, "kind": "lambda", "variables": [{"name": "r", "type": "Time"}]},
        {"scope_id": "event_scope", "parent_scope": None, "kind": "lambda", "variables": [{"name": "t", "type": "Time"}]}], "two fixed sibling Time scopes")
    require(c.usage["determiners"] == [
        {"kind": "all", "occurrence_id": c.occ["all"]["occurrence_id"], "action": "provider"},
        {"kind": "the", "occurrence_id": c.occ["the"]["occurrence_id"], "action": "drop",
         "head_occurrence_id": c.occ["time"]["occurrence_id"], "parameter": "r", "scope_id": "time_scope"}], "all/the commitments")
    atoms = ([struct("Agent", v("e"), v("s")), struct("Theme", v("e"), v("s"))]
             if context_subject else []) + [struct("Theme", v("e"), v("e"))]
    for ordering in permutations(["time_scope", "event_scope"]):
        # One location per external-argument atom: absent, root, time, event.
        for positions in product([-1, 0, 1, 2], repeat=len(atoms)):
            if context_subject and positions[0] == positions[1] == -1:
                continue  # The external subject s must occur in RHS.
            for hr, ht in product([False, True], repeat=2):
                regions = [[], [c.use("time", [v("r")])], []]
                for atom, position in zip(atoms, positions):
                    if position >= 0:
                        regions[position].append(atom)
                if hr:
                    regions[1].append(struct("Happen", v("e"), v("r")))
                if ht:
                    regions[2].append(struct("Happen", v("e"), v("t")))
                if not regions[2]:
                    continue
                scopes = {"time_scope": lam("r", "Time", "time_scope", conjunction(regions[1])),
                          "event_scope": lam("t", "Time", "event_scope", conjunction(regions[2]))}
                call = c.use("all", [struct("World", v("e"))] + [scopes[s] for s in ordering])
                yield conjunction([call] + regions[0])


def immobility(c):
    check_input_shape(c, ["the", "quality", "of", "not", "moving"], [("q", "E")], ["quality", "of", "not", "moving"], "active")
    for word, kinds in [("quality", ["E"]), ("of", ["E", {"arrow": ["E", "Prop"]}]), ("not", ["Prop"]), ("moving", ["E"])]:
        c.interface(word, kinds)
    require(not c.enum["lhs_structures"] and not c.known_scopes, "extra immobility structure/scopes")
    require(c.usage["determiners"] == [{"kind": "the", "occurrence_id": c.occ["the"]["occurrence_id"],
             "action": "drop", "head_occurrence_id": c.occ["quality"]["occurrence_id"], "parameter": "q"}], "quality head binding")

    @lru_cache(None)
    def region(resources, in_lambda):
        """All nonempty formulas using exactly resources; recursion consumes resources.

        Root is an atomic call, a lexical operator with recursively built body,
        or a conjunction of two strict nonempty resource partitions. Flattening
        AND and deduplication only remove construction-order duplicates.
        """
        out = {}

        def save(node):
            out[dump(canonical_ast(node, c.known_scopes))] = node

        if resources == ("Q",):
            save(c.use("quality", [v("q")]))
        if resources == ("M",):
            for name in (["q", "oracle_b"] if in_lambda else ["q"]):
                save(c.use("moving", [v(name)]))
        if "N" in resources and len(resources) > 1:
            rest = tuple(x for x in resources if x != "N")
            for body in region(rest, in_lambda):
                save(c.use("not", [body]))
        if "O" in resources and len(resources) > 1:
            require(not in_lambda, "a second Of resource would need another local scope")
            rest = tuple(x for x in resources if x != "O")
            for body in region(rest, True):
                save(c.use("of", [v("q"), lam("oracle_b", "E", "oracle_generated", body)]))
        # All unordered proper bipartitions: least resource always on the left.
        for size in range(1, len(resources)):
            for left in combinations(resources, size):
                if resources[0] not in left:
                    continue
                right = tuple(x for x in resources if x not in left)
                for a, b in product(region(tuple(left), in_lambda), region(right, in_lambda)):
                    save(conjunction([a, b]))
        return tuple(out.values())

    # Quality(q) is mandatory because it is the determiner head; others optional.
    for mask in product([False, True], repeat=3):
        resources = tuple(sorted(["Q"] + [x for x, on in zip(["M", "N", "O"], mask) if on]))
        yield from region(resources, False)


def impermissible(c):
    check_input_shape(c, ["not", "permitted"], [("b", "V")], ["not", "permitted"], "passive")
    c.interface("not", ["Prop"])
    c.interface("permitted", ["V"])
    require(not c.usage["determiners"] and not c.enum["lhs_structures"] and not c.known_scopes, "extra impermissible constraints")
    atoms = [c.use("permitted", [v("b")]), struct("Theme", v("b"), v("b")),
             struct("Agent", v("b"), struct("ImplicitSubj", v("b")))]
    # Without Not: every nonempty subset of the three resource leaves.
    for selected in product([False, True], repeat=3):
        leaves = [x for x, on in zip(atoms, selected) if on]
        if leaves:
            yield conjunction(leaves)
    # With Not: each resource can be omitted, outside, or inside; inside nonempty.
    for positions in product([-1, 0, 1], repeat=3):
        outside = [x for x, place in zip(atoms, positions) if place == 0]
        inside = [x for x, place in zip(atoms, positions) if place == 1]
        if inside:
            yield conjunction(outside + [c.use("not", [conjunction(inside)])])


def normalization_checks():
    """Check that the comparison does not erase bindings, scopes or resources."""
    identity = {"op": "use", "synset_id": "test", "usage_id": "u",
                "interface_hash": "hash", "occurrence_id": "o", "args": []}

    def call(*args, occurrence="o"):
        return dict(identity, args=list(args), occurrence_id=occurrence)

    def key(node):
        return canonical_ast(node, {"one", "two"})

    a, b = struct("A", v("e")), struct("B", v("e"))
    tests = {
        "lambda_alpha_names_equal": key(call(lam("x", "E", "one", struct("R", v("x")))))
            == key(call(lam("y", "E", "one", struct("R", v("y"))))),
        "conjunction_order_and_association_equal": key(conjunction([a, conjunction([a, b])]))
            == key(conjunction([conjunction([b, a]), a])),
        "duplicate_conjunct_is_retained": key(conjunction([a, a])) != key(a),
        "external_variable_does_not_become_local": key(call(lam("x", "E", "one", struct("R", v("x")))))
            != key(call(lam("x", "E", "one", struct("R", v("q"))))),
        "named_scope_identity_is_retained": key(call(lam("x", "E", "one", a)))
            != key(call(lam("x", "E", "two", a))),
        "occurrence_identity_is_retained": key(call(a, occurrence="o1"))
            != key(call(a, occurrence="o2")),
        "nested_binding_identity_is_retained": key(call(lam("x", "E", "one",
            call(lam("y", "E", "two", struct("R", v("x")))))))
            != key(call(lam("x", "E", "one", call(lam("y", "E", "two", struct("R", v("y"))))))),
    }
    require(all(tests.values()), "normalization self-check failure")
    return tests


def main():
    normalization = normalization_checks()
    results = {}
    trials = [("all_along_event_only", all_along, ROOT / "inputs" / "all_along.json"),
              ("immobility", immobility, None), ("impermissible", impermissible, None),
              ("all_along", all_along, ROOT / "runs" / "all_along" / "input.json")]
    for name, oracle, input_path in trials:
        c = Contract(name, input_path)
        # Build the complete oracle before reading the saved candidate list.
        expected_rows = [c.formula(rhs) for rhs in oracle(c)]
        expected = {formula_key(row, c) for row in expected_rows}
        run = ROOT / "runs" / name
        rows = [json.loads(line) for line in (run / "candidates.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        observed_keys = [formula_key(row["formula"], c) for row in rows]
        observed = set(observed_keys)
        report = read(run / "report.json")
        missing, extra = expected - observed, observed - expected
        check = {
            "whole_normalized_formula_set_equal": expected == observed,
            "oracle_count": len(expected), "saved_line_count": len(rows),
            "saved_unique_normalized_count": len(observed),
            "normalized_duplicate_lines": len(rows) - len(observed),
            "missing_count": len(missing), "extra_count": len(extra),
            "missing_normalized_formulas": [json.loads(x) for x in sorted(missing)],
            "extra_normalized_formulas": [json.loads(x) for x in sorted(extra)],
            "oracle_normalized_set_sha256": digest(sorted(expected)),
            "saved_normalized_set_sha256": digest(sorted(observed)),
            "input_file_sha256": file_digest(c.path),
            "input_canonical_sha256": digest(c.input),
            "source_object_canonical_sha256": digest(c.source),
            "source_provenance_sha256": c.source["provenance"]["sha256"],
            "source_snapshot_file_sha256": file_digest(ROOT / "source_snapshots" / (c.source["synset_id"] + ".json")),
            "candidates_file_sha256": file_digest(run / "candidates.jsonl"),
            "run_input_file_sha256": file_digest(run / "input.json"),
            "run_input_equal_to_requested_input": read(run / "input.json") == c.input,
            "report_input_hash_matches": report["input_hash"] == digest(c.input),
            "report_interface_hashes_match_independent_calculation": report["interface_hashes"] == c.hashes,
            "report_count_matches": report["candidate_count"] == len(rows),
            "uncapped_exhaustion_recorded": report["status"] == "COMPLETE" and report["complete"] is True
                and report["exhausted"] is True and report["max_candidates"] is None,
        }
        results[name] = check
    historical = results.pop("all_along")
    result = {
        "schema_version": "v3.independent-scope-coverage-check/1",
        "checker_file_sha256": file_digest(Path(__file__)),
        "specification_sha256": file_digest(PROJECT / "specification" / "ENUMERATION.md"),
        "independence": "Python standard library only. No production module imports, prepare_request, iter_candidates, enumerate_request, or capped runs. Oracle derives finite sets from inputs before reading candidates; report counts are not oracle inputs. Only the stable interface-hash payload/JSON encoding convention is shared.",
        "comparison": "Whole formula metadata plus normalized LHS/RHS AST sets; not samples or count-only. Only lambda/generated-scope alpha naming and same-region AND association/order are normalized. Exact source occurrence, provider identity/hash, argument order, named scopes, external names and binder identity remain. No semantic simplification or deduplication.",
        "normalization_self_checks": normalization,
        "oracle_constructions": {
            "all_along_event_only": "2 S/P permutations. Theme(e,e) chooses absent/root/time/event; Happen(e,r) and Happen(e,t) each choose absent/own lambda. Time(r) is required in time_scope by the head; event_scope must be nonempty. Per permutation: 4*2*2 minus 3*2 empty-event choices = 10; total 20.",
            "historical_all_along_context_augmented": "2 S/P permutations. Three external atoms each choose absent/root/time/event; Happen(e,r) and Happen(e,t) each choose absent/own lambda. Time(r) is required in time_scope by the head; event_scope must be nonempty; Agent(e,s) or Theme(e,s) must retain s. Per permutation: 202 region-nonempty choices minus 10 missing-s choices = 192; total 384. This historical input is read from its own run snapshot, not the corrected final input.",
            "immobility": "Recursive finite resource-subset AST grammar. Required Q(q), optional Of/Not/Move; each once. Atomic calls, unary Not, Of(q,lambda E.body), and all nonempty binary resource partitions for AND. Move may bind q or the visible Of local. Quality always binds q. No V parameters, so no structures.",
            "impermissible": "Without Not, 2^3-1=7 nonempty subsets of Permit(b), Theme(b,b), Agent(b,ImplicitSubj(b)). With Not, 3^3-2^3=19 absent/outside/inside assignments with nonempty inside. Total 26."
        },
        "limitations": ["Only these three supported finite input contracts are checked; input-shape changes raise an error.", "No semantic truth/equivalence judgment, full-synset usage coverage, basis RHS certification, publication, or formal proof is claimed."],
        "results": results,
        "main_trial_total": sum(x["oracle_count"] for x in results.values()),
        "optional_historical_comparison": {"all_along_context_augmented": historical},
    }
    result["passed"] = all(
        x["whole_normalized_formula_set_equal"] and x["normalized_duplicate_lines"] == 0
        and x["run_input_equal_to_requested_input"] and x["report_input_hash_matches"]
        and x["report_interface_hashes_match_independent_calculation"]
        and x["report_count_matches"] and x["uncapped_exhaustion_recorded"]
        for x in results.values())
    (ROOT / "coverage_check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "results": {
        name: {key: row[key] for key in ("oracle_count", "saved_unique_normalized_count", "missing_count", "extra_count", "whole_normalized_formula_set_equal")}
        for name, row in results.items()}}, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
