"""Run preserved independent grammar constructors without their old workspace mains.

Only standard-library imports and definitions are loaded from byte-identical
auditor source snapshots. Their historical file-copy/main code and workspace
imports are not executed. No production enumeration generator is an oracle.
"""
import ast
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


@lru_cache(None)
def load_definitions(path_string):
    path = Path(path_string)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    stdlib = {"__future__", "functools", "itertools", "collections", "json", "hashlib", "pathlib", "copy"}
    selected = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            selected.append(node)
        elif isinstance(node, ast.ImportFrom) and node.module in stdlib:
            selected.append(node)
        elif isinstance(node, ast.Import) and all(n.name in stdlib for n in node.names):
            selected.append(node)
    namespace = {"__name__": "portable_independent_oracle", "__file__": str(path),
                 "canonical_hash": canonical_hash}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)
    return SimpleNamespace(**namespace)


def compare_all(name, input_path, request, report, rows, root):
    source = root / "audit/oracle_sources"
    if name in {"bear", "life", "hand_in_hand"}:
        helper = load_definitions(str(source / "flat_check_trials.py"))
        expected, _ = helper.oracle(request)
        observed = {helper.key(helper.flat_atoms(r["formula"]["rhs"])) for r in rows}
    elif name == "all_along":
        helper = load_definitions(str(source / "scope_verify_coverage.py"))
        contract = helper.Contract(name, input_path)
        expected = {helper.formula_key(contract.formula(rhs), contract) for rhs in helper.all_along(contract)}
        observed = {helper.formula_key(r["formula"], contract) for r in rows}
    elif name == "immobility":
        helper = load_definitions(str(source / "nominal_verify_trial.py"))
        nid = request["enumeration"]["nominalizations"][0]["nominalization_id"]
        expected = set(helper.oracle(request, report, nid))
        observed = {helper.key(r["formula"]["rhs"]) for r in rows}
    else:
        assert name == "impermissible"
        helper = load_definitions(str(source / "event_verify_trial.py"))
        generated, _, _ = helper.independent_oracle(request, constrained=False)
        expected = set(generated)
        observed = {helper.key(r["formula"]["rhs"]) for r in rows}
    if expected != observed or len(observed) != len(rows):
        raise ValueError(f"Independent whole-set comparison failed for {name}: missing={len(expected-observed)}, extra={len(observed-expected)}")
    return len(expected)
