"""Portable, offline verification and exhaustive replay of the six-sense bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / "engine"
sys.path.insert(0, str(ENGINE / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from tologic_v3.common import canonical_hash, read_json
from tologic_v3.enumeration import enumerate_request
from tologic_v3.enumeration_input import prepare_request
from tologic_v3.enumeration_interfaces import validate_interface_candidate
from oracle_adapter import compare_all


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest():
    manifest = read_json(ROOT / "MANIFEST.json")
    for row in manifest["files"]:
        path = ROOT / row["path"]
        if not path.is_file() or path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
            raise ValueError("Bundle file missing or changed: " + row["path"])
    return len(manifest["files"])


def check_case(case, run=None):
    case_root = ROOT / case["directory"]
    request = read_json(case_root / "input.json")
    run = run or case_root / "results"
    report = read_json(run / "report.json")
    if read_json(run / "input.json") != request:
        raise ValueError("Run used a different input: " + case["name"])
    if not (report["status"] == "COMPLETE" and report["complete"] and report["exhausted"]
            and report["max_candidates"] is None and report["input_hash"] == canonical_hash(request)):
        raise ValueError("Run is not an uncapped completed enumeration: " + case["name"])
    rows = [json.loads(line) for line in (run / "candidates.jsonl").read_text(encoding="utf-8").splitlines()]
    expected = read_json(case_root / "expected/formula.json")
    selection = read_json(case_root / "expected/selection.json")
    if len(rows) != report["candidate_count"] or len(rows) != case["candidate_count"]:
        raise ValueError("Candidate count changed: " + case["name"])
    prepared = prepare_request(request, ENGINE)
    matching = []
    for line, row in enumerate(rows, 1):
        if row["candidate_id"] != canonical_hash(row["formula"]):
            raise ValueError("Incorrect candidate hash")
        issues = validate_interface_candidate(prepared, row["formula"])
        if issues or not row["interface_gate"]["passed"]:
            raise ValueError("Static gate failure: " + repr(issues))
        if row["formula"]["lhs"] != expected["lhs"] or row["formula"]["parameters"] != expected["parameters"]:
            raise ValueError("Target LHS or external parameters changed")
        if row["candidate_id"] == selection["candidate_id"] and row["formula"] == expected:
            matching.append(line)
    if matching != [case["selected_line"]]:
        raise ValueError("The exact accepted formula is absent or changed: " + case["name"])
    oracle_count = compare_all(case["name"], case_root / "input.json", request, report, rows, ROOT)
    return {"case": case["name"], "candidate_count": len(rows), "selected_line": matching[0],
            "exact_formula_found": True, "all_static_checks_passed": True,
            "separate_oracle_count": oracle_count, "whole_candidate_sets_identical": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify", help="Check all bundled hashes, saved results and accepted formulas")
    replay = sub.add_parser("replay", help="Run fresh uncapped enumerations; then compare to archived results")
    replay.add_argument("--out", type=Path, required=True, help="New or empty output directory")
    replay.add_argument("--case", action="append", help="Optional case name; repeat to select multiple cases")
    args = parser.parse_args()
    file_count = verify_manifest()
    cases = read_json(ROOT / "INDEX.json")["cases"]
    if args.command == "replay":
        if args.case:
            unknown = set(args.case) - {c["name"] for c in cases}
            if unknown:
                parser.error("Unknown cases: " + ", ".join(sorted(unknown)))
            cases = [c for c in cases if c["name"] in args.case]
        output = args.out.resolve()
        if output.exists() and (not output.is_dir() or any(output.iterdir())):
            parser.error("--out must be a new or empty directory; saved results are never overwritten")
        output.mkdir(parents=True, exist_ok=True)
        # Search receives only request JSON. Accepted formulas are read later.
        for case in cases:
            request = read_json(ROOT / case["directory"] / "input.json")
            report = enumerate_request(request, output / case["name"], project=ENGINE)
            print(json.dumps({"case": case["name"], "status": report["status"],
                              "candidate_count": report["candidate_count"]}), flush=True)
        results = []
        for case in cases:
            run = output / case["name"]
            result = check_case(case, run)
            saved = ROOT / case["directory"] / "results/candidates.jsonl"
            fresh_ids = {json.loads(line)["candidate_id"] for line in (run / "candidates.jsonl").read_text(encoding="utf-8").splitlines()}
            saved_ids = {json.loads(line)["candidate_id"] for line in saved.read_text(encoding="utf-8").splitlines()}
            if fresh_ids != saved_ids:
                raise ValueError("Fresh candidate set differs from archive: " + case["name"])
            result["fresh_ids_equal_archived_ids"] = True
            results.append(result)
    else:
        results = [check_case(case) for case in cases]
    summary = {"status": "PASS", "command": args.command, "manifest_files_verified": file_count,
               "total_candidates": sum(r["candidate_count"] for r in results), "results": results,
               "basis_rhs_supplied": False, "published": False}
    if args.command == "replay":
        (output / "verification.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
