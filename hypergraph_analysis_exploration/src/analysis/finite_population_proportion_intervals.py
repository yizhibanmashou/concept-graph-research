"""Exact design-based intervals for binary proportions under SRSWOR.

Intervals invert equal-tailed hypergeometric tests. Stratified intervals use
Bonferroni simultaneous coverage and can be population-weighted. When sampled
outcomes are missing, bounds treat them as all failures/all successes.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def _integer(value: Any, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _log_choose(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("-inf")
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def hypergeometric_pmf(N: int, M: int, n: int, k: int) -> float:
    """P(X=k) for X~Hypergeom(N, M, n), using stable log combinations."""
    N = _integer(N, "N", 1)
    M = _integer(M, "M")
    n = _integer(n, "n")
    k = _integer(k, "k")
    if M > N or n > N:
        raise ValueError("M and n must not exceed N")
    low, high = max(0, n - (N - M)), min(n, M)
    if not low <= k <= high:
        return 0.0
    return math.exp(_log_choose(M, k) + _log_choose(N - M, n - k) - _log_choose(N, n))


def _hypergeom_range_probability(N: int, M: int, n: int, low: int, high: int) -> float:
    support_low, support_high = max(0, n - (N - M)), min(n, M)
    if high < support_low or low > support_high:
        return 0.0
    low, high = max(low, support_low), min(high, support_high)
    support = range(support_low, support_high + 1)
    log_weights = [
        _log_choose(M, k) + _log_choose(N - M, n - k)
        for k in support
    ]
    scale = max(log_weights)
    denominator = sum(math.exp(value - scale) for value in log_weights)
    numerator = sum(
        math.exp(value - scale)
        for k, value in zip(support, log_weights)
        if low <= k <= high
    )
    return min(1.0, max(0.0, numerator / denominator))


def hypergeometric_exact_interval(
    N: int, n: int, k: int, confidence: float = 0.95,
) -> tuple[int, int]:
    """Equal-tailed exact interval for the unknown finite-population successes M.

    Returns inclusive integer bounds on M. The interval is conservative because
    the hypergeometric distribution is discrete.
    """
    N = _integer(N, "N", 1)
    n = _integer(n, "n", 1)
    k = _integer(k, "k")
    if n > N:
        raise ValueError("n must not exceed N")
    if k > n:
        raise ValueError("k must not exceed n")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    alpha_tail = (1.0 - confidence) / 2.0
    comparison_tolerance = 1e-12

    # The lower endpoint is the smallest M whose upper tail can produce k.
    lo, hi = 0, N
    while lo < hi:
        mid = (lo + hi) // 2
        upper_tail = _hypergeom_range_probability(N, mid, n, k, n)
        if upper_tail + comparison_tolerance >= alpha_tail:
            hi = mid
        else:
            lo = mid + 1
    lower_M = lo

    # The upper endpoint is the largest M whose lower tail can produce k.
    lo, hi = 0, N
    while lo < hi:
        mid = (lo + hi + 1) // 2
        lower_tail = _hypergeom_range_probability(N, mid, n, 0, k)
        if lower_tail + comparison_tolerance >= alpha_tail:
            lo = mid
        else:
            hi = mid - 1
    upper_M = lo
    return lower_M, upper_M


def stratified_supported_interval(
    strata: dict[str, dict[str, Any]], confidence: float = 0.95,
) -> dict[str, Any]:
    """Build simultaneous exact intervals and a weighted total for SRSWOR strata.

    Each stratum input has ``population_n``, ``sample_n``, ``supported_n`` and
    optional ``missing_n``. Missing sampled outcomes are bounded worst-case.
    """
    if not isinstance(strata, dict) or not strata:
        raise ValueError("strata must be a non-empty object")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    alpha_per_stratum = (1.0 - confidence) / len(strata)
    simultaneous_confidence = 1.0 - alpha_per_stratum
    parsed: dict[str, dict[str, int]] = {}
    for name, row in strata.items():
        if not isinstance(name, str) or not name:
            raise ValueError("stratum names must be non-empty strings")
        if not isinstance(row, dict):
            raise ValueError(f"strata.{name} must be an object")
        N = _integer(row.get("population_n"), f"strata.{name}.population_n", 1)
        n = _integer(row.get("sample_n"), f"strata.{name}.sample_n", 1)
        k = _integer(row.get("supported_n"), f"strata.{name}.supported_n")
        missing = _integer(row.get("missing_n", 0), f"strata.{name}.missing_n")
        if n > N or k > n or missing > n - k:
            raise ValueError(f"invalid sample counts in stratum {name!r}")
        parsed[name] = {"population_n": N, "sample_n": n,
                        "supported_n": k, "missing_n": missing}

    population_total = sum(row["population_n"] for row in parsed.values())
    results: dict[str, dict[str, Any]] = {}
    for name, row in parsed.items():
        N, n = row["population_n"], row["sample_n"]
        k_low = row["supported_n"]
        k_high = k_low + row["missing_n"]
        lower_low, _ = hypergeometric_exact_interval(N, n, k_low, simultaneous_confidence)
        _, upper_high = hypergeometric_exact_interval(N, n, k_high, simultaneous_confidence)
        results[name] = {
            **row,
            "weight": N / population_total,
            "supported_proportion_point_estimate": (k_low / n if row["missing_n"] == 0 else None),
            "finite_population_success_count_bounds": [lower_low, upper_high],
            "supported_proportion_bounds": [lower_low / N, upper_high / N],
            "simultaneous_confidence_level_at_least": confidence,
        }

    weighted_bounds = [
        sum(results[name]["weight"] * results[name]["supported_proportion_bounds"][idx]
            for name in results)
        for idx in (0, 1)
    ]
    weighted_point = None
    if all(row["missing_n"] == 0 for row in parsed.values()):
        weighted_point = sum(
            results[name]["weight"] * results[name]["supported_proportion_point_estimate"]
            for name in results
        )
    contrasts: dict[str, list[float]] = {}
    names = list(results)
    for left_index, left in enumerate(names):
        for right in names[left_index + 1:]:
            left_bounds = results[left]["supported_proportion_bounds"]
            right_bounds = results[right]["supported_proportion_bounds"]
            contrasts[f"{left}_minus_{right}"] = [
                left_bounds[0] - right_bounds[1],
                left_bounds[1] - right_bounds[0],
            ]
    return {
        "method": "equal-tailed exact hypergeometric intervals; Bonferroni simultaneous strata",
        "family_confidence_level": confidence,
        "stratum_confidence_level": simultaneous_confidence,
        "strata": results,
        "population_weighted_supported_prevalence_point_estimate": weighted_point,
        "population_weighted_supported_prevalence_bounds": weighted_bounds,
        "simultaneous_stratum_difference_bounds": contrasts,
        "missingness_method": "worst-case: missing sampled outcomes range from all unsupported to all supported",
        "interpretation": "Intervals cover the finite-population prevalence of the adjudicated supported label under SRSWOR; they do not establish semantic truth.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("counts_json", type=Path,
                        help="JSON with {confidence, strata:{name:{population_n,sample_n,supported_n,missing_n?}}}")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.counts_json.read_text(encoding="utf-8"))
        result = stratified_supported_interval(payload["strata"], payload.get("confidence", 0.95))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
