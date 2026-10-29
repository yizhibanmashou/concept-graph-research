"""Design simulation for stratified Taylor-Wald confidence intervals of nominal kappa.

The script conditions on a synthetic finite population generated once per scenario,
then repeatedly samples each v3 stratum by SRS without replacement. It is a
method diagnostic, not evidence about annotator agreement in the OEWN population.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from pathlib import Path
from typing import Any

from src.analysis.annotation_agreement import AGREEMENT_VERSION, _design_weighted_kappa, _load_stratified_design


CATEGORIES = ("c0", "c1", "c2")


def _normalize(values: list[float]) -> list[float]:
    total = sum(values)
    return [value / total for value in values]


def _joint_probabilities(scenario: str, stratum_index: int) -> list[float]:
    if scenario == "balanced_three_category":
        matrix = [
            [0.50, 0.08, 0.02],
            [0.08, 0.20, 0.02],
            [0.02, 0.02, 0.06],
        ]
    elif scenario == "rare_category":
        matrix = [
            [0.68, 0.08, 0.01],
            [0.08, 0.12, 0.01],
            [0.01, 0.01, 0.00],
        ]
    elif scenario == "near_zero_kappa":
        prevalence = [0.50, 0.30, 0.20]
        matrix = [[prevalence[i] * prevalence[j] for j in range(3)] for i in range(3)]
    elif scenario == "near_degenerate_margins":
        prevalence = [0.99, 0.009, 0.001]
        agreement_probability = 0.95
        matrix = [
            [(agreement_probability * prevalence[i] if i == j else 0.0)
             + (1 - agreement_probability) * prevalence[i] * prevalence[j]
             for j in range(3)]
            for i in range(3)
        ]
    elif scenario == "stratum_heterogeneity":
        t = stratum_index / 23
        prevalence_a = _normalize([0.70 - 0.20 * t, 0.24 + 0.15 * t, 0.06 + 0.05 * t])
        prevalence_b = _normalize([0.58 - 0.12 * t, 0.34 + 0.08 * t, 0.08 + 0.04 * t])
        shared = _normalize([prevalence_a[i] + prevalence_b[i] for i in range(3)])
        agreement = 0.55 + 0.35 * t
        matrix = [
            [(agreement * shared[i] if i == j else 0.0)
             + (1 - agreement) * prevalence_a[i] * prevalence_b[j]
             for j in range(3)]
            for i in range(3)
        ]
    else:
        raise ValueError(f"unknown simulation scenario: {scenario}")
    flat = [cell for row in matrix for cell in row]
    total = sum(flat)
    if any(value < 0 for value in flat) or not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"invalid joint probabilities for scenario {scenario!r}")
    return flat


def _kappa_from_counts(counts: list[float | int]) -> float | None:
    total = sum(counts)
    joint = [value / total for value in counts]
    rows = [sum(joint[i * 3:(i + 1) * 3]) for i in range(3)]
    cols = [sum(joint[i * 3 + j] for i in range(3)) for j in range(3)]
    disagreement = sum(joint[i * 3 + j] for i in range(3) for j in range(3) if i != j)
    observed = 1.0 - disagreement
    expected = sum(rows[i] * cols[i] for i in range(3))
    return None if expected >= 1 - 1e-15 else 1.0 - disagreement / (1.0 - expected)


def _stratified_jackknife_se(cells_by_stratum: dict[str, list[int]], design: dict[str, Any]) -> float | None:
    """Delete-one jackknife SE with SRSWOR finite-population corrections."""
    full_counts = [0.0] * 9
    for name, cells in cells_by_stratum.items():
        expansion = design["strata"][name]["population_count"] / len(cells)
        for cell in cells:
            full_counts[cell] += expansion

    variance = 0.0
    for name, cells in cells_by_stratum.items():
        spec = design["strata"][name]
        n_h = len(cells)
        N_h = int(spec["population_count"])
        if n_h == N_h:
            continue
        if n_h < 2:
            return None
        base_weight = N_h / n_h
        replicate_weight = N_h / (n_h - 1)
        observed_counts = [sum(value == cell for value in cells) for cell in range(9)]
        theta_replicates = []
        for deleted_cell in cells:
            replicate_counts = full_counts.copy()
            for cell in range(9):
                observed_in_h = observed_counts[cell]
                retained_in_h = observed_in_h - (1 if deleted_cell == cell else 0)
                replicate_counts[cell] += replicate_weight * retained_in_h - base_weight * observed_in_h
            theta = _kappa_from_counts(replicate_counts)
            if theta is None:
                return None
            theta_replicates.append(theta)
        mean_replicate = sum(theta_replicates) / n_h
        fpc = 1.0 - n_h / N_h
        variance += fpc * (n_h - 1) / n_h * sum(
            (value - mean_replicate) ** 2 for value in theta_replicates
        )
    return math.sqrt(max(variance, 0.0))


def _make_population(
    scenario: str, design: dict[str, Any], rng: random.Random,
) -> tuple[dict[str, list[int]], float]:
    population: dict[str, list[int]] = {}
    total_counts = [0] * 9
    for index, (name, spec) in enumerate(design["strata"].items()):
        probabilities = _joint_probabilities(scenario, index)
        cells = rng.choices(range(9), weights=probabilities, k=int(spec["population_count"]))
        counts = [0] * 9
        for cell in cells:
            counts[cell] += 1
        population[name] = cells
        total_counts = [left + right for left, right in zip(total_counts, counts)]
    truth = _kappa_from_counts(total_counts)
    if truth is None:
        raise ValueError(f"finite population kappa is undefined in scenario {scenario!r}")
    return population, truth


def _simulate_scenario(
    scenario: str, design: dict[str, Any], replicates: int, population_seed: int,
    sampling_seed: int,
) -> dict[str, Any]:
    population, truth = _make_population(scenario, design, random.Random(population_seed))
    rng = random.Random(sampling_seed)
    item_ids: list[str] = []
    stratum_by_item: dict[str, str] = {}
    estimates: list[float] = []
    standard_errors: list[float] = []
    widths: list[float] = []
    covered = 0
    jackknife_standard_errors: list[float] = []
    jackknife_widths: list[float] = []
    jackknife_covered = 0
    jackknife_undefined = 0
    undefined = 0
    taylor_interval_unavailable = 0
    jackknife_interval_unavailable = 0
    observed_disagreements: list[int] = []

    for replicate in range(replicates):
        values_a: list[str] = []
        values_b: list[str] = []
        cells_by_stratum: dict[str, list[int]] = {}
        item_ids.clear()
        stratum_by_item.clear()
        for stratum, spec in design["strata"].items():
            selected = rng.sample(population[stratum], int(spec["sample_count"]))
            cells_by_stratum[stratum] = selected
            for within_stratum, cell in enumerate(selected):
                item_id = f"{stratum}:{within_stratum}"
                item_ids.append(item_id)
                stratum_by_item[item_id] = stratum
                left, right = divmod(cell, 3)
                values_a.append(CATEGORIES[left])
                values_b.append(CATEGORIES[right])

        estimate = _design_weighted_kappa(item_ids, values_a, values_b, stratum_by_item, design)
        observed_disagreements.append(sum(left != right for left, right in zip(values_a, values_b)))
        kappa = estimate["weighted_cohens_kappa"]
        interval = estimate.get("wald_95_ci")
        if kappa is None:
            undefined += 1
            jackknife_undefined += 1
            continue
        estimates.append(kappa)
        standard_errors.append(estimate["standard_error"])
        if interval is None:
            taylor_interval_unavailable += 1
        else:
            widths.append(interval["upper"] - interval["lower"])
            if interval["lower"] <= truth <= interval["upper"]:
                covered += 1

        jackknife_se = _stratified_jackknife_se(cells_by_stratum, design)
        if jackknife_se is not None:
            if observed_disagreements[-1] == 0:
                jackknife_interval_unavailable += 1
            else:
                jackknife_standard_errors.append(jackknife_se)
                jackknife_lower, jackknife_upper = kappa - 1.959963984540054 * jackknife_se, kappa + 1.959963984540054 * jackknife_se
                jackknife_widths.append(jackknife_upper - jackknife_lower)
                if jackknife_lower <= truth <= jackknife_upper:
                    jackknife_covered += 1
        else:
            jackknife_undefined += 1

    point_estimates_valid = len(estimates)
    valid = len(widths)
    coverage = covered / valid if valid else None
    jackknife_valid = len(jackknife_widths)
    jackknife_coverage = jackknife_covered / jackknife_valid if jackknife_valid else None
    mean_estimate = sum(estimates) / point_estimates_valid if point_estimates_valid else None
    mean_se = sum(standard_errors) / point_estimates_valid if point_estimates_valid else None
    mean_width = sum(widths) / valid if valid else None
    empirical_sd = (
        math.sqrt(sum((value - mean_estimate) ** 2 for value in estimates) / (point_estimates_valid - 1))
        if point_estimates_valid > 1 and mean_estimate is not None else None
    )
    return {
        "scenario": scenario,
        "finite_population_kappa": truth,
        "replicates_requested": replicates,
        "point_estimates_valid": point_estimates_valid,
        "replicates_valid": valid,
        "undefined_point_estimate": undefined,
        "taylor_interval_unavailable": taylor_interval_unavailable,
        "zero_observed_disagreement_replicates": sum(value == 0 for value in observed_disagreements),
        "zero_disagreement_rate": sum(value == 0 for value in observed_disagreements) / replicates,
        "mean_sample_disagreement_count": statistics.mean(observed_disagreements),
        "median_sample_disagreement_count": statistics.median(observed_disagreements),
        "coverage": coverage,
        "coverage_denominator": "replicates for which the Taylor interval is reported",
        "interval_availability_rate": valid / replicates,
        "covered_and_reported_interval_rate": covered / replicates,
        "coverage_monte_carlo_se": math.sqrt(coverage * (1 - coverage) / valid) if valid and coverage is not None else None,
        "mean_estimated_kappa": mean_estimate,
        "bias": mean_estimate - truth if mean_estimate is not None else None,
        "empirical_sd_of_estimator": empirical_sd,
        "mean_taylor_standard_error": mean_se,
        "mean_wald_interval_width": mean_width,
        "jackknife_valid": jackknife_valid,
        "jackknife_undefined_estimate": jackknife_undefined,
        "jackknife_interval_unavailable": jackknife_interval_unavailable,
        "jackknife_coverage": jackknife_coverage,
        "jackknife_coverage_denominator": "replicates for which the jackknife interval is reported",
        "jackknife_interval_availability_rate": jackknife_valid / replicates,
        "jackknife_covered_and_reported_interval_rate": jackknife_covered / replicates,
        "jackknife_coverage_monte_carlo_se": (
            math.sqrt(jackknife_coverage * (1 - jackknife_coverage) / jackknife_valid)
            if jackknife_valid and jackknife_coverage is not None else None
        ),
        "jackknife_mean_standard_error": (
            sum(jackknife_standard_errors) / jackknife_valid if jackknife_valid else None
        ),
        "jackknife_mean_wald_interval_width": (
            sum(jackknife_widths) / jackknife_valid if jackknife_valid else None
        ),
    }


def run_simulation(manifest: dict[str, Any], replicates: int = 2000, seed: int = 20261005) -> dict[str, Any]:
    if replicates < 1:
        raise ValueError("replicates must be at least 1")
    design = _load_stratified_design(manifest)
    scenarios = (
        "balanced_three_category", "rare_category", "near_zero_kappa",
        "near_degenerate_margins", "stratum_heterogeneity",
    )
    results = []
    for index, scenario in enumerate(scenarios):
        results.append(_simulate_scenario(
            scenario,
            design,
            replicates,
            population_seed=seed + 1000 * index,
            sampling_seed=seed + 1000 * index + 1,
        ))
    return {
        "simulation_version": "stratified-kappa-interval-simulation/3",
        "agreement_analyzer_version": AGREEMENT_VERSION,
        "estimand": "finite_population_nominal_cohens_kappa_for_two_synthetic_raters",
        "design": "v3 manifest strata; independent SRSWOR within every stratum",
        "variance_methods_compared": [
            "first-order Taylor linearization with SRSWOR finite-population correction; normal Wald 95% interval",
            "stratified delete-one jackknife with SRSWOR finite-population correction; normal Wald 95% interval",
        ],
        "seed": seed,
        "scenarios": results,
        "limitations": [
            "Synthetic joint label distributions are diagnostic assumptions, not observed annotation behavior.",
            "Results condition on one generated finite population per scenario and measure repeated-sampling coverage.",
            "This simulation assesses the implemented interval under these scenarios only; it is not a proof of general validity.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sampling-manifest", type=Path,
                        default=Path("outputs/phase7/annotation_candidate_frame_v3_400_manifest.json"))
    parser.add_argument("--replicates", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261005)
    parser.add_argument("--output", type=Path, default=Path("outputs/phase10/kappa_ci_design_simulation.json"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        manifest_bytes = args.sampling_manifest.read_bytes()
        manifest = json.loads(manifest_bytes)
        if not isinstance(manifest, dict):
            raise ValueError("sampling manifest must contain a JSON object")
        report = run_simulation(manifest, args.replicates, args.seed)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    report["input_sha256"] = {
        "sampling_manifest": hashlib.sha256(manifest_bytes).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Simulation report: {args.output}")
    for row in report["scenarios"]:
        print(
            f"{row['scenario']}: Taylor={row['coverage']:.4f}, "
            f"jackknife={row['jackknife_coverage']:.4f}, "
            f"valid={row['replicates_valid']}/{row['replicates_requested']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
