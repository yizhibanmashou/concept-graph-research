"""Descriptive, non-tuning analysis of the frozen fresh SemCor dev pilot."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


CONDITIONS = ("A", "B", "C", "D")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_bucket(count: int) -> str:
    if count <= 3:
        return "2-3"
    if count <= 7:
        return "4-7"
    return "8+"


def input_lengths(example: dict[str, Any], condition: str) -> tuple[int, int]:
    """Return candidate count and total non-padding tokens in its fixed tensor."""
    rows = example["inputs"][condition]
    return len(rows), sum(token != 0 for row in rows for token in row)


def summarize(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "mean": None, "median": None}
    return {
        "n": len(values),
        "mean": round(statistics.mean(values), 4),
        "median": round(statistics.median(values), 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--runs", type=Path, nargs="+", required=True,
                        help="One directory per seed; each must contain result.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    examples = read_json(args.data / "dev.json")
    metadata = read_json(args.data / "metadata.json")
    run_results = [read_json(path / "result.json") for path in args.runs]
    if not examples or len(run_results) < 2:
        raise ValueError("Need a nonempty dev set and at least two completed seed runs")
    sample_ids = [row["sample_id"] for row in examples]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Duplicate dev sample IDs")
    expected_dev_hash = metadata["sample_ids_sha256"]["dev"]
    actual_dev_hash = hashlib.sha256("\n".join(sorted(sample_ids)).encode()).hexdigest()
    if actual_dev_hash != expected_dev_hash:
        raise ValueError("dev sample IDs do not match metadata hash")

    for run in run_results:
        if run["inputs_sha256"]["dev.json"] != sha256(args.data / "dev.json"):
            raise ValueError("A run was scored on a different dev serialization")
        if run["dev"]["A"]["covered"] != len(examples):
            raise ValueError("Run does not cover all selected dev examples")

    scorable = [i for i, row in enumerate(examples) if row.get("gold_candidate_index") is not None]
    bucket_ids: dict[str, list[int]] = defaultdict(list)
    for i in scorable:
        bucket_ids[candidate_bucket(len(examples[i]["scorable_candidate_ids"]))].append(i)

    strata: dict[str, Any] = {}
    for bucket in ("2-3", "4-7", "8+"):
        ids = bucket_ids.get(bucket, [])
        conditions: dict[str, Any] = {}
        for condition in CONDITIONS:
            correct = 0
            outcomes = 0
            for run in run_results:
                predictions = run["dev"][condition]["predictions"]
                for i in ids:
                    correct += int(predictions[i] == examples[i]["gold_candidate_index"])
                    outcomes += 1
            conditions[condition] = {
                "correct": correct,
                "outcomes": outcomes,
                "accuracy": round(correct / outcomes, 4) if outcomes else None,
            }
        strata[bucket] = {"targets": len(ids), "conditions": conditions}

    paired: dict[str, Any] = {}
    for left, right in (("D", "B"), ("D", "C"), ("B", "A")):
        left_only = right_only = ties = 0
        for run in run_results:
            lp = run["dev"][left]["predictions"]
            rp = run["dev"][right]["predictions"]
            for i in scorable:
                gold = examples[i]["gold_candidate_index"]
                lc, rc = lp[i] == gold, rp[i] == gold
                left_only += int(lc and not rc)
                right_only += int(rc and not lc)
                ties += int(lc == rc)
        paired[f"{left}-{right}"] = {
            f"{left}_only_correct": left_only,
            f"{right}_only_correct": right_only,
            "same_correctness": ties,
            "paired_outcomes": len(scorable) * len(run_results),
        }

    token_lengths: dict[str, Any] = {}
    for condition in CONDITIONS:
        candidate_totals, per_candidate = [], []
        for row in examples:
            n_candidates, total = input_lengths(row, condition)
            candidate_totals.append(total)
            per_candidate.append(total / n_candidates if n_candidates else 0)
        token_lengths[condition] = {
            "total_nonpadding_tokens_per_target": summarize(candidate_totals),
            "nonpadding_tokens_per_candidate": summarize(per_candidate),
        }

    output = {
        "analysis": "descriptive error stratification; no model selection or tuning",
        "data_sha256": sha256(args.data / "dev.json"),
        "dev_sample_ids_sha256": actual_dev_hash,
        "seeds": [run["seed"] for run in run_results],
        "selected_targets": len(examples),
        "scorable_targets": len(scorable),
        "candidate_count_strata": strata,
        "paired_correctness_across_target_seed_outcomes": paired,
        "input_length_by_condition": token_lengths,
        "limitations": [
            "Only the internal document-disjoint SemCor development sample is analyzed.",
            "Candidate-count strata and input lengths are descriptive; they are not causal explanations.",
            "Repeated seeds reuse targets and do not create independent observations.",
            "No thresholds, model settings, or representation choices are selected from this output.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "out": str(args.out),
        "selected_targets": len(examples),
        "scorable_targets": len(scorable),
        "candidate_count_strata": strata,
        "paired": paired,
        "input_length_by_condition": token_lengths,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
