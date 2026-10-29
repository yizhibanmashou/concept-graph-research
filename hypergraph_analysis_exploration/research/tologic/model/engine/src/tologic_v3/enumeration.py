"""Standalone, exhaustive single-usage enumeration from supplied dependencies.

No remote model, historical registry, production certificate, or publishing is
involved. The existing V3 gate is diagnostic, never an unproved pruning oracle.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from .common import canonical_hash, write_json
from .enumeration_input import prepare_request
from .enumeration_interfaces import instantiate_interface_call, validate_interface_candidate
from .enumeration_search import iter_candidates
from .gates import instantiate_provider_call, validate_formula
from .event_closure import validate_event_bindings


def _walk(node, scopes=()):
    if not isinstance(node, dict):
        return
    yield node, scopes
    child_scopes = scopes
    if node.get("op") == "lambda" and node.get("scope_id") is not None:
        child_scopes += (node["scope_id"],)
    for value in node.values():
        if isinstance(value, dict):
            yield from _walk(value, child_scopes)
        elif isinstance(value, list):
            for child in value:
                yield from _walk(child, child_scopes)


def _term(value):
    if isinstance(value, str):
        return {"var": value}
    if isinstance(value, dict) and set(value) == {"implicit_subject"}:
        return {"op": "struct", "name": "ImplicitSubj", "args": [{"var": value["implicit_subject"]}]}
    if isinstance(value, dict) and set(value) == {"world_of"}:
        return {"op": "struct", "name": "World", "args": [{"var": value["world_of"]}]}
    raise ValueError("Malformed frozen structural argument")


def _atom(row):
    return {"op": "struct", "name": row["name"], "args": [_term(x) for x in row["arguments"]]}


def _scope_matches(row, scopes):
    return row.get("scope_id") is None or row["scope_id"] in scopes


def _unique_rows(rows):
    return list({canonical_hash(row): deepcopy(row) for row in rows}.values())


def _satisfies_frozen_constraints(prepared, result):
    """Only exact, supplied constraints; no English interpretation or scoring."""
    if validate_event_bindings(prepared, result["rhs"]):
        return False
    calls, authored_structures, realized_structures = [], [], []
    for node, scopes in _walk(result["rhs"]):
        if node.get("op") == "use":
            calls.append((node, scopes))
            # Provider macro LHS roles count as realizing a supplied commitment,
            # without spending the caller's newly authored structural budget.
            pattern = (instantiate_interface_call(node, prepared["context"])
                       if prepared["assumption_mode"] == "interface-only-symbolic"
                       else instantiate_provider_call(node, prepared["context"]))
            realized_structures.extend((part, caller_scopes) for part, caller_scopes in _walk(pattern, scopes)
                                       if part.get("op") == "struct" and part.get("name") not in {"ImplicitSubj", "World"})
        elif node.get("op") == "struct" and node.get("name") not in {"ImplicitSubj", "World"}:
            authored_structures.append((node, scopes))
            realized_structures.append((node, scopes))
        elif node.get("op") == "nom":
            # Internal event roles are not assertions at the author's scope.
            calls.append((node, scopes))

    head_bindings = {oid: set(names) for oid, names in prepared.get("head_bindings", {}).items()}
    for witness in result["witnesses"]:
        # Optional noun witnesses acquire their head obligation only when
        # selected. Quantifying y without the licensed Noun(y) is not a
        # realization of that noun-introduced witness.
        if witness["origin"] != "verb_event":
            head_bindings.setdefault(witness["head_occurrence_id"], set()).add(witness["name"])
    for oid, names in head_bindings.items():
        matched = [node for node, _ in calls if node["occurrence_id"] == oid]
        if not any(set(names) <= {arg["var"] for arg in (node["args"][:1] if node.get("op") == "nom" else node["args"])
                                 if isinstance(arg, dict) and set(arg) == {"var"}} for node in matched):
            return False

    fixed = prepared.get("fixed_plan")
    if fixed is not None:
        lexical = fixed["lexical"]
        seen = set()
        for node, scopes in calls:
            collection = "interfaces" if prepared["assumption_mode"] == "interface-only-symbolic" else "providers"
            provider = prepared["context"][collection][node["synset_id"] + "::" + node["usage_id"]]
            actual = {p["name"]: arg for p, arg in zip(provider["parameters"], node["args"])}
            direct = {}
            for key, value in actual.items():
                if isinstance(value, dict) and set(value) == {"var"}:
                    direct[key] = value["var"]
                elif value.get("op") == "struct" and value.get("name") == "World":
                    direct[key] = {"world_of": value["args"][0]["var"]}
            matching = [i for i, row in enumerate(lexical)
                        if row["occurrence_id"] == node["occurrence_id"] and row["usage_id"] == node["usage_id"]
                        and _scope_matches(row, scopes)
                        and all(actual.get(key) == _term(name) for key, name in row["bindings"].items())
                        and all(row["bindings"].get(key) == name for key, name in direct.items())]
            if not matching:
                return False
            seen.update(matching)
        if seen != set(range(len(lexical))):
            return False
        allowed = fixed["structural"]["rhs"]
        if any(not any(node == _atom(row) and _scope_matches(row, scopes) for row in allowed)
               for node, scopes in authored_structures):
            return False

    required = list(prepared.get("required_structures", []))
    if fixed is not None:
        required += fixed["structural"]["rhs"]
    return all(any(node == _atom(row) and _scope_matches(row, scopes)
                   for node, scopes in realized_structures) for row in required)


def _inventory(prepared, result):
    usage = deepcopy(prepared["usage"])
    usage.pop("lhs_structures", None)
    plan = deepcopy(result["binding_plan"])
    plan["structural"]["lhs"] = deepcopy(prepared.get("lhs_structures", []))
    required = list(prepared.get("required_structures", []))
    if prepared.get("fixed_plan") is not None:
        required += prepared["fixed_plan"]["structural"]["rhs"]
    plan["structural"]["rhs"] = _unique_rows(plan["structural"]["rhs"] + required)
    usage["binding_plan"] = plan
    usage["witnesses"] = [{key: deepcopy(w[key]) for key in ("name", "type", "origin", "occurrence_id", "reason")}
                           for w in result["witnesses"]]
    inventory = {
        "synset_id": prepared["source"]["synset_id"],
        "coverage": {
            "complete": True,
            "scope": "supplied_single_usage_only",
            "rationale": "Covers this supplied single usage only. Proposed enumeration inventory; not certification of all lexical usages.",
            "evidence_ids": deepcopy(usage["evidence"]),
        },
        "usages": [usage],
    }
    return inventory


def _render(node):
    if "var" in node:
        return node["var"]
    op = node["op"]
    if op == "nom":
        prefix = "not " * len(node["negation_occurrence_ids"])
        return "Nom[" + prefix + node["synset_id"] + "::" + node["usage_id"] + "](" + ", ".join(_render(a) for a in node["args"]) + ")"
    if op in {"use", "struct", "target"}:
        name = (node["synset_id"] + "::" + node["usage_id"] if op == "use"
                else node.get("name", "TARGET"))
        return name + "(" + ", ".join(_render(arg) for arg in node["args"]) + ")"
    if op == "and":
        return "(" + " AND ".join(_render(arg) for arg in node["args"]) + ")"
    if op in {"exists", "lambda"}:
        names = node["variables" if op == "exists" else "parameters"]
        return ("EXISTS " if op == "exists" else "LAMBDA ") + ",".join(v["name"] for v in names) + "." + _render(node["body"])
    raise ValueError("Unexpected authored AST operation in enumerator output")


def enumerate_request(request, output_dir, project=None, max_candidates=None):
    """Write every candidate; complete=True only after actual generator exhaustion.

    An explicit max_candidates is an inspection limit, never a completeness
    claim. Lookahead distinguishes exact exhaustion at the limit from truncation.
    """
    if max_candidates is not None and (type(max_candidates) is not int or max_candidates < 1):
        raise ValueError("max_candidates must be a positive integer or omitted")
    prepared = prepare_request(request, project=project)
    interface_only = prepared["assumption_mode"] == "interface-only-symbolic"
    destination = Path(output_dir).resolve()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise FileExistsError("Enumeration output must be a new or empty directory; existing results are preserved")
    destination.mkdir(parents=True, exist_ok=True)
    stats = {}
    report = {
        "schema_version": "v3.enumeration-report/1", "status": "RUNNING",
        "complete": False, "exhausted": False, "candidate_count": 0,
        "input_hash": canonical_hash(request), "assumption_mode": "supplied-dependencies",
        "semantic_acceptance": False, "published": False,
        "synset_id": prepared["source"]["synset_id"], "usage_id": prepared["usage"]["usage_id"],
        "max_candidates": max_candidates, "output_dir": str(destination), "stats": stats,
        "guarantee": (
            "For validated input, COMPLETE exhausts the declared finite lexical/parameter/scope grammar. "
            "Any correct formula satisfying that grammar and the supplied structured constraints has its "
            "canonical representative in candidates.jsonl. Provider semantics and input constraints are assumptions."
        ),
        "v3_gate_is_diagnostic_only": True,
        "inventory_status": "PROPOSED_SINGLE_USAGE_NOT_CERTIFIED",
    }
    if interface_only:
        report.update(assumption_mode="interface-only-symbolic", basis_rhs_status="pending",
                      publishable=False, v3_gate_is_diagnostic_only=False,
                      v3_gate_status="NOT_RUN_REQUIRES_CERTIFIED_FORMULAS",
                      interface_gate_is_diagnostic_only=True,
                      interface_assumptions=deepcopy(prepared["interface_assumptions"]),
                      interface_hashes={key: row["interface_hash"] for key, row in
                                        prepared["context"]["interfaces"].items()})
    if prepared.get("nominalizations"):
        report["nominalization_analysis"] = deepcopy(prepared["nominalization_analysis"])
        report["nominalization_hashes"] = {key: site["construction_hash"] for key, site in prepared["nominalizations"].items()}
    if prepared.get("event_bindings"):
        report["event_binding_hashes"] = {oid: binding["binding_hash"] for oid, binding in prepared["event_bindings"].items()}
        report["event_ownership"] = {oid: {k: binding[k] for k in ("usage_id", "event_parameter", "mode", "bound_parameter")}
                                     for oid, binding in prepared["event_bindings"].items()}
    write_json(destination / "input.json", request)
    write_json(destination / "report.json", report)
    seen = set()
    stream = None
    try:
        stream = (destination / "candidates.jsonl").open("w", encoding="utf-8", newline="\n")
        for result in iter_candidates(prepared, stats):
            if not _satisfies_frozen_constraints(prepared, result):
                stats["supplied_constraint_rejections"] = stats.get("supplied_constraint_rejections", 0) + 1
                continue
            formula = {
                "synset_id": prepared["source"]["synset_id"], "usage_id": prepared["usage"]["usage_id"],
                "parameters": deepcopy(prepared["parameters"]), "lhs": deepcopy(prepared["lhs"]),
                "rhs": result["rhs"], "primitives": [],
            }
            if interface_only:
                formula["schema_version"] = "v3.interface-formula-candidate/1"
            digest = canonical_hash(formula)
            if digest in seen:
                continue
            seen.add(digest)
            if max_candidates is not None and report["candidate_count"] >= max_candidates:
                report["status"] = "PARTIAL"
                report["stop_reason"] = "EXPLICIT_CANDIDATE_LIMIT"
                break
            inventory = _inventory(prepared, result)
            gate_issues = (validate_interface_candidate(prepared, formula) if interface_only else
                           validate_formula(prepared["source"], inventory, formula, prepared["context"]))
            row = {
                "candidate_id": digest, "formula": formula, "inventory": inventory,
                "binding_plan": inventory["usages"][0]["binding_plan"],
                "resource_counts": result["resource_counts"],
                "used_occurrence_ids": result["used_occurrence_ids"],
                "readable_formula": _render(formula["lhs"]) + " IFF " + _render(formula["rhs"]),
                "semantic_acceptance": False, "inventory_status": "PROPOSED_SINGLE_USAGE_NOT_CERTIFIED",
                "v3_gate": {"passed": not gate_issues, "issues": gate_issues, "filters_enumeration": False},
            }
            if interface_only:
                row["interface_gate"] = row.pop("v3_gate")
                row.update(assumption_mode="interface-only-symbolic", publishable=False,
                           basis_rhs_status="pending",
                           v3_gate={"passed": False, "status": "NOT_RUN_REQUIRES_CERTIFIED_FORMULAS",
                                    "issues": [], "filters_enumeration": False})
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n")
            stream.flush()
            report["candidate_count"] += 1
            gate_prefix = "interface_gate" if interface_only else "v3_gate"
            key = gate_prefix + ("_passed" if not gate_issues else "_diagnostics")
            stats[key] = stats.get(key, 0) + 1
            # A killed process leaves a truthful incomplete checkpoint.
            if report["candidate_count"] == 1 or report["candidate_count"] % 100 == 0:
                write_json(destination / "report.json", report)
        else:
            report.update(status="COMPLETE", complete=True, exhausted=True)
        if report["status"] == "COMPLETE" and not report["candidate_count"]:
            report["diagnostic"] = "No candidate satisfies all supplied constraints; inspect input constraints and enumeration coverage before any semantic conclusion."
    except KeyboardInterrupt:
        report.update(status="INTERRUPTED", complete=False, exhausted=False, stop_reason="USER_INTERRUPTION")
        raise
    except Exception as exc:
        report.update(status="ERROR", complete=False, exhausted=False,
                      error={"type": type(exc).__name__, "message": str(exc)})
        raise
    finally:
        if stream is not None:
            stream.close()
        write_json(destination / "report.json", report)
    return report
