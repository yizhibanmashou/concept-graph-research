"""Audit approximate worst-case precision of the text-free pair frame design.

This reports planning margins, not confirmatory confidence intervals or power.
It reads only aggregate counts from the candidate manifest; no pair IDs or text
are read or printed.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


Z_975 = 1.959963984540054
POSITIVE_STRATA = (
    "direct_edge", "lift_one_class_edge", "lift_two_plus_class_edges",
)


def _positive_int(value: Any, name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _normal_half_width(n: int, variance: float, fpc: float = 1.0) -> float:
    return Z_975 * math.sqrt(variance / n * fpc)


def _fpc(sample_size: int, population_size: int) -> float:
    if sample_size > population_size:
        raise ValueError("sample size exceeds population size")
    return (population_size - sample_size) / (population_size - 1) if population_size > 1 else 0.0


def minimum_n_for_worst_case_margin(population_size: int, margin: float) -> int:
    """Normal-approximation n for a binary proportion at p=.5, with FPC."""
    population_size = _positive_int(population_size, "population_size")
    if not 0 < margin < 0.5:
        raise ValueError("margin must be between 0 and 0.5")
    z2_variance = Z_975**2 * 0.25
    estimate = z2_variance * population_size / (
        margin**2 * (population_size - 1) + z2_variance
    )
    return min(population_size, math.ceil(estimate))


def minimum_n_for_contrast_margin(population_a: int, population_b: int, margin: float) -> int:
    """Equal n per stratum for a worst-case difference of two binary proportions."""
    population_a = _positive_int(population_a, "population_a")
    population_b = _positive_int(population_b, "population_b")
    if not 0 < margin < 1:
        raise ValueError("contrast margin must be between 0 and 1")
    for n in range(1, min(population_a, population_b) + 1):
        variance_bound = (
            0.25 / n * _fpc(n, population_a)
            + 0.25 / n * _fpc(n, population_b)
        )
        if Z_975 * math.sqrt(variance_bound) <= margin:
            return n
    raise ValueError("target contrast margin cannot be reached with equal stratum sample sizes")


def audit_manifest(
    manifest: dict[str, Any], target_margin: float = 0.10,
    target_contrast_margin: float = 0.10,
) -> dict[str, Any]:
    populations = manifest.get("population_counts")
    samples = manifest.get("stratum_counts")
    if not isinstance(populations, dict) or not isinstance(samples, dict):
        raise ValueError("manifest must contain population_counts and stratum_counts objects")

    strata: dict[str, dict[str, Any]] = {}
    for name in (*POSITIVE_STRATA, "reverse_direct_challenge"):
        N = _positive_int(populations.get(name), f"population_counts.{name}")
        n = _positive_int(samples.get(name), f"stratum_counts.{name}")
        factor = _fpc(n, N)
        strata[name] = {
            "population_n": N,
            "sample_n": n,
            "worst_case_95pct_normal_half_width": _normal_half_width(n, 0.25, factor),
            "approx_sample_n_for_10pp_half_width": minimum_n_for_worst_case_margin(N, target_margin),
        }

    positive_population = sum(strata[name]["population_n"] for name in POSITIVE_STRATA)
    weights = {name: strata[name]["population_n"] / positive_population for name in POSITIVE_STRATA}
    positive_variance_bound = sum(
        weights[name] ** 2 * 0.25 / strata[name]["sample_n"]
        * _fpc(strata[name]["sample_n"], strata[name]["population_n"])
        for name in POSITIVE_STRATA
    )
    positive_total = {
        "population_n": positive_population,
        "stratum_weights": weights,
        "worst_case_95pct_normal_half_width": Z_975 * math.sqrt(positive_variance_bound),
    }

    pairwise_contrasts: dict[str, float] = {}
    for left, right in zip(POSITIVE_STRATA, POSITIVE_STRATA[1:]):
        variance_bound = sum(
            0.25 / strata[name]["sample_n"]
            * _fpc(strata[name]["sample_n"], strata[name]["population_n"])
            for name in (left, right)
        )
        pairwise_contrasts[f"{left}_minus_{right}"] = {
            "worst_case_95pct_normal_half_width": Z_975 * math.sqrt(variance_bound),
            "approx_equal_n_per_stratum_for_target_margin": minimum_n_for_contrast_margin(
                strata[left]["population_n"], strata[right]["population_n"],
                target_contrast_margin,
            ),
        }

    same_pos = populations.get("same_pos_nonclosure_challenge")
    if not isinstance(same_pos, dict):
        raise ValueError("same_pos_nonclosure_challenge population metadata must be an object")
    source_population = _positive_int(
        same_pos.get("eligible_source_synset_count"),
        "population_counts.same_pos_nonclosure_challenge.eligible_source_synset_count",
    )
    source_sample = _positive_int(
        samples.get("same_pos_nonclosure_challenge"),
        "stratum_counts.same_pos_nonclosure_challenge",
    )
    source_fpc = _fpc(source_sample, source_population)

    return {
        "method": "pointwise 95% normal planning margin; binary outcome worst case p=0.5",
        "confirmatory_power_calculated": False,
        "per_stratum": strata,
        "positive_closure_weighted_total": positive_total,
        "positive_stratum_pairwise_contrast_half_widths": pairwise_contrasts,
        "same_pos_challenge": {
            "estimand": "macro-average across eligible source synsets, with one target drawn uniformly within each selected source",
            "source_population_n": source_population,
            "source_sample_n": source_sample,
            "worst_case_95pct_normal_half_width_ignoring_fpc": _normal_half_width(source_sample, 0.25),
            "source_fpc": source_fpc,
            "warning": "Do not interpret as a uniform-over-all-nonclosure-pairs estimate; challenge stratum stays separate.",
        },
        "target_margin": target_margin,
        "target_contrast_margin": target_contrast_margin,
        "annotation_workload_at_two_annotators": 2 * _positive_int(manifest.get("candidate_count"), "candidate_count"),
        "interpretation": "Approximate design-planning diagnostics only; actual intervals require the frozen estimand and a prespecified design-based estimator.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="text-free candidate manifest JSON")
    parser.add_argument("--target-margin", type=float, default=0.10,
                        help="desired worst-case normal half-width for stratum n planning (default: 0.10)")
    parser.add_argument("--target-contrast-margin", type=float, default=0.10,
                        help="desired half-width for difference of two stratum proportions (default: 0.10)")
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        report = audit_manifest(manifest, args.target_margin, args.target_contrast_margin)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
