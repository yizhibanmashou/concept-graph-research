"""Compute label-free precision/workload scenarios from a T02 frame audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


EMPTY = "new_empty"
COLLISION = "new_collision"
BOTH = "empty_and_collision"
OTHER = "other_affected"
UNAFFECTED = "unaffected"
STRATA = (EMPTY, COLLISION, BOTH, OTHER, UNAFFECTED)


def allocate_targets(
    population: dict[str, int], total_n: int, high_risk_n: int = 50
) -> dict[str, int]:
    """Census overlap stratum, oversample rare strata, proportionally fill rest."""
    if high_risk_n < 1:
        raise ValueError("high-risk sample size must be positive")
    if total_n < population[BOTH] + 2 * high_risk_n:
        raise ValueError("total sample is too small for the requested rare-stratum allocation")
    if high_risk_n > min(population[EMPTY], population[COLLISION]):
        raise ValueError("requested high-risk sample exceeds a stratum population")

    result = {BOTH: population[BOTH], EMPTY: high_risk_n, COLLISION: high_risk_n}
    remainder = total_n - sum(result.values())
    pool = population[OTHER] + population[UNAFFECTED]
    other_n = math.floor(remainder * population[OTHER] / pool + 0.5)
    result[OTHER] = other_n
    result[UNAFFECTED] = remainder - other_n
    if result[OTHER] > population[OTHER] or result[UNAFFECTED] > population[UNAFFECTED]:
        raise ValueError("requested sample exceeds the finite population")
    return result


def scenario(
    population: dict[str, int],
    branches: dict[str, int],
    total_n: int,
    high_risk_n: int = 50,
    reviewers: int = 2,
    conditions: int = 4,
) -> dict[str, Any]:
    allocation = allocate_targets(population, total_n, high_risk_n)
    population_n = sum(population.values())
    weights = {key: population[key] / population_n for key in STRATA}
    if any(allocation[key] < 1 for key in STRATA):
        raise ValueError("each population stratum needs at least one sampled target")

    weighted_bound_sum = sum(weights[key] ** 2 / allocation[key] for key in STRATA)
    mean_half_width = math.sqrt(math.log(2 / 0.05) * weighted_bound_sum / 2)
    paired_three_half_width = math.sqrt(
        2 * math.log(2 * 3 / 0.05) * weighted_bound_sum
    )
    expected_branches = sum(
        allocation[key] * branches[key] / population[key] for key in STRATA
    )
    review_units = expected_branches * reviewers * conditions

    return {
        "total_targets": total_n,
        "allocation_by_stratum": allocation,
        "population_weights": weights,
        "mean_95_worst_half_width": mean_half_width,
        "three_paired_contrasts_simultaneous_95_worst_half_width": paired_three_half_width,
        "expected_source_branches": expected_branches,
        "expected_branch_condition_reviewer_units": review_units,
    }


def analyze(frame: dict[str, Any], sample_sizes: tuple[int, ...] = (200, 500, 800, 1050)) -> dict[str, Any]:
    if frame.get("schema") != "preposition-sampling-frame-audit/2":
        raise ValueError("expected preposition-sampling-frame-audit/2 input")
    details = frame.get("by_effect_class_review_workload", {})
    if any(key not in details for key in STRATA):
        raise ValueError("frame audit is missing a required effect stratum")
    population = {key: details[key]["targets"] for key in STRATA}
    branches = {key: details[key]["branches"] for key in STRATA}
    return {
        "schema": "preposition-stratified-precision-sensitivity/1",
        "source_frame_sha256": frame.get("inputs_sha256"),
        "assumptions": [
            "Census empty_and_collision; sample 50 each from new_empty and new_collision; proportionally allocate remaining targets to other_affected and unaffected.",
            "Population estimates use target stratum weights; all five strata are represented.",
            "Hoeffding bounds use [0,1] for target fidelity and [-1,1] for paired differences; no finite-population correction.",
            "Three paired contrasts use Bonferroni simultaneous 95% coverage.",
            "Review workload extrapolates source branches per target and multiplies by four conditions and two reviewers; it is not reviewer-hours.",
            "No definitions, semantic labels, reviewer outcomes, or sample identifiers are read.",
        ],
        "scenarios": [scenario(population, branches, n) for n in sample_sizes],
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-audit", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="new local JSON output")
    args = parser.parse_args()
    frame = json.loads(args.frame_audit.read_text(encoding="utf-8"))
    result = analyze(frame)
    result["frame_audit_file_sha256"] = sha256(args.frame_audit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps(result["scenarios"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
