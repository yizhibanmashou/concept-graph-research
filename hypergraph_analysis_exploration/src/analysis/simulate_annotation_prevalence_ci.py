"""Design-based coverage diagnostic for stratified prevalence Wald intervals.

For each scenario this generates one synthetic finite population, then repeats
the v3 stratified SRSWOR design. Results diagnose the implemented intervals;
they are not evidence about real annotator behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

from src.analysis.annotation_agreement import (
    AGREEMENT_VERSION,
    _design_weighted_prevalence,
    _load_stratified_design,
)


SCENARIOS = (
    "balanced_prevalence",
    "moderate_prevalence",
    "rare_prevalence",
    "very_rare_prevalence",
    "stratum_heterogeneity",
)
Z_975 = 1.959963984540054
TRANSFORMED_METHODS = ("logit_delta", "arcsine_delta")


def _stratum_probability(scenario: str, index: int, stratum_count: int) -> float:
    t = index / max(stratum_count - 1, 1)
    probabilities = {
        "balanced_prevalence": 0.5,
        "moderate_prevalence": 0.1,
        "rare_prevalence": 0.01,
        "very_rare_prevalence": 0.002,
        "stratum_heterogeneity": 0.001 + 0.029 * t,
    }
    try:
        return probabilities[scenario]
    except KeyError as exc:
        raise ValueError(f"unknown prevalence scenario: {scenario}") from exc


def _make_population(
    scenario: str, design: dict[str, Any], rng: random.Random,
) -> tuple[dict[str, list[int]], float]:
    strata = list(design["strata"].items())
    population: dict[str, list[int]] = {}
    positive_count = 0
    for index, (name, spec) in enumerate(strata):
        probability = _stratum_probability(scenario, index, len(strata))
        labels = [int(rng.random() < probability) for _ in range(int(spec["population_count"]))]
        population[name] = labels
        positive_count += sum(labels)
    truth = positive_count / design["population_count"]
    return population, truth


def _transformed_interval(estimate: float, standard_error: float, method: str) -> dict[str, float] | None:
    """Diagnostic transformed-Wald alternatives; endpoints stay in [0, 1]."""
    if standard_error <= 0 or not 0.0 < estimate < 1.0:
        return None
    if method == "logit_delta":
        transformed = math.log(estimate / (1.0 - estimate))
        transformed_se = standard_error / (estimate * (1.0 - estimate))

        def inverse(value: float) -> float:
            if value >= 0:
                exp_negative = math.exp(-value)
                return 1.0 / (1.0 + exp_negative)
            exp_positive = math.exp(value)
            return exp_positive / (1.0 + exp_positive)

        return {
            "lower": inverse(transformed - Z_975 * transformed_se),
            "upper": inverse(transformed + Z_975 * transformed_se),
        }
    if method == "arcsine_delta":
        transformed = math.asin(math.sqrt(estimate))
        transformed_se = standard_error / (2.0 * math.sqrt(estimate * (1.0 - estimate)))
        lower_angle = min(math.pi / 2.0, max(0.0, transformed - Z_975 * transformed_se))
        upper_angle = min(math.pi / 2.0, max(0.0, transformed + Z_975 * transformed_se))
        return {"lower": math.sin(lower_angle) ** 2, "upper": math.sin(upper_angle) ** 2}
    raise ValueError(f"unknown transformed interval method: {method}")


def _simulate_scenario(
    scenario: str,
    design: dict[str, Any],
    replicates: int,
    population_seed: int,
    sampling_seed: int,
) -> dict[str, Any]:
    population, truth = _make_population(scenario, design, random.Random(population_seed))
    rng = random.Random(sampling_seed)
    estimates: list[float] = []
    standard_errors: list[float] = []
    interval_widths: list[float] = []
    covered_intervals = 0
    unavailable_zero_variance = 0
    transformed_intervals = {name: {"widths": [], "covered": 0} for name in TRANSFORMED_METHODS}
    transformed_unavailable = {name: 0 for name in TRANSFORMED_METHODS}

    for _ in range(replicates):
        item_ids: list[str] = []
        stratum_by_item: dict[str, str] = {}
        values: list[str] = []
        for stratum, spec in design["strata"].items():
            selected = rng.sample(population[stratum], int(spec["sample_count"]))
            for within_stratum, label in enumerate(selected):
                item_id = f"{stratum}:{within_stratum}"
                item_ids.append(item_id)
                stratum_by_item[item_id] = stratum
                values.append("positive" if label else "negative")

        result = _design_weighted_prevalence(
            item_ids, values, stratum_by_item, design, ["negative", "positive"],
        )["category_estimates"]["positive"]
        estimate = result["estimated_proportion"]
        estimates.append(estimate)
        standard_errors.append(result["standard_error"])
        interval = result["wald_95_ci"]
        for method in TRANSFORMED_METHODS:
            transformed_interval = _transformed_interval(estimate, result["standard_error"], method)
            if transformed_interval is None:
                transformed_unavailable[method] += 1
            else:
                transformed_intervals[method]["widths"].append(
                    transformed_interval["upper"] - transformed_interval["lower"]
                )
                if transformed_interval["lower"] <= truth <= transformed_interval["upper"]:
                    transformed_intervals[method]["covered"] += 1
        if interval is None:
            unavailable_zero_variance += 1
            continue
        interval_widths.append(interval["upper"] - interval["lower"])
        if interval["lower"] <= truth <= interval["upper"]:
            covered_intervals += 1

    interval_count = len(interval_widths)
    conditional_coverage = covered_intervals / interval_count if interval_count else None
    transformed_summaries = {}
    for method in TRANSFORMED_METHODS:
        widths = transformed_intervals[method]["widths"]
        method_count = len(widths)
        method_coverage = transformed_intervals[method]["covered"] / method_count if method_count else None
        transformed_summaries[method] = {
            "intervals_reported": method_count,
            "covered_intervals": transformed_intervals[method]["covered"],
            "interval_unavailable_zero_variance_or_boundary_estimate": transformed_unavailable[method],
            "interval_availability_rate": method_count / replicates,
            "conditional_coverage": method_coverage,
            "covered_and_reported_rate": transformed_intervals[method]["covered"] / replicates,
            "coverage_monte_carlo_se": (
                math.sqrt(method_coverage * (1 - method_coverage) / method_count)
                if method_count and method_coverage is not None else None
            ),
            "mean_reported_interval_width": sum(widths) / method_count if method_count else None,
        }
    mean_estimate = sum(estimates) / len(estimates)
    empirical_sd = (
        math.sqrt(sum((value - mean_estimate) ** 2 for value in estimates) / (len(estimates) - 1))
        if len(estimates) > 1 else None
    )
    return {
        "scenario": scenario,
        "finite_population_prevalence": truth,
        "replicates_requested": replicates,
        "valid_point_estimates": len(estimates),
        "bias": mean_estimate - truth,
        "empirical_sd_of_estimator": empirical_sd,
        "mean_estimated_standard_error": sum(standard_errors) / len(standard_errors),
        "intervals_reported": interval_count,
        "covered_intervals": covered_intervals,
        "interval_unavailable_zero_estimated_variance": unavailable_zero_variance,
        "interval_availability_rate": interval_count / replicates,
        "conditional_coverage": conditional_coverage,
        "coverage_denominator": "replicates for which the implemented interval is reported",
        "covered_and_reported_rate": covered_intervals / replicates,
        "coverage_monte_carlo_se": (
            math.sqrt(conditional_coverage * (1 - conditional_coverage) / interval_count)
            if interval_count and conditional_coverage is not None else None
        ),
        "mean_reported_interval_width": sum(interval_widths) / interval_count if interval_count else None,
        "transformed_interval_diagnostics": transformed_summaries,
    }


def _aggregate_population_runs(scenario: str, runs: list[dict[str, Any]]) -> dict[str, Any]:
    total_replicates = sum(row["replicates_requested"] for row in runs)
    interval_count = sum(row["intervals_reported"] for row in runs)
    covered = sum(row["covered_intervals"] for row in runs)
    coverage = covered / interval_count if interval_count else None
    transformed = {}
    for method in TRANSFORMED_METHODS:
        method_rows = [row["transformed_interval_diagnostics"][method] for row in runs]
        method_count = sum(row["intervals_reported"] for row in method_rows)
        method_covered = sum(row["covered_intervals"] for row in method_rows)
        method_coverage = method_covered / method_count if method_count else None
        transformed[method] = {
            "intervals_reported": method_count,
            "covered_intervals": method_covered,
            "interval_unavailable_zero_variance_or_boundary_estimate": sum(
                row["interval_unavailable_zero_variance_or_boundary_estimate"] for row in method_rows
            ),
            "interval_availability_rate": method_count / total_replicates,
            "conditional_coverage": method_coverage,
            "covered_and_reported_rate": method_covered / total_replicates,
            "coverage_monte_carlo_se": (
                math.sqrt(method_coverage * (1 - method_coverage) / method_count)
                if method_count and method_coverage is not None else None
            ),
            "mean_reported_interval_width": (
                sum(row["mean_reported_interval_width"] * row["intervals_reported"]
                    for row in method_rows if row["intervals_reported"]) / method_count
                if method_count else None
            ),
        }
    run_coverages = [row["conditional_coverage"] for row in runs if row["conditional_coverage"] is not None]
    return {
        "scenario": scenario,
        "population_replicates": len(runs),
        "finite_population_prevalence_mean": sum(row["finite_population_prevalence"] for row in runs) / len(runs),
        "finite_population_prevalence_range": {
            "minimum": min(row["finite_population_prevalence"] for row in runs),
            "maximum": max(row["finite_population_prevalence"] for row in runs),
        },
        "replicates_requested": total_replicates,
        "valid_point_estimates": total_replicates,
        "mean_bias_across_populations": sum(row["bias"] for row in runs) / len(runs),
        "mean_within_population_estimator_sd": sum(row["empirical_sd_of_estimator"] for row in runs) / len(runs),
        "mean_estimated_standard_error": sum(
            row["mean_estimated_standard_error"] * row["replicates_requested"] for row in runs
        ) / total_replicates,
        "intervals_reported": interval_count,
        "covered_intervals": covered,
        "interval_unavailable_zero_estimated_variance": sum(
            row["interval_unavailable_zero_estimated_variance"] for row in runs
        ),
        "interval_availability_rate": interval_count / total_replicates,
        "conditional_coverage": coverage,
        "coverage_denominator": "all reported intervals pooled across generated finite populations",
        "covered_and_reported_rate": covered / total_replicates,
        "coverage_monte_carlo_se": (
            math.sqrt(coverage * (1 - coverage) / interval_count)
            if interval_count and coverage is not None else None
        ),
        "mean_reported_interval_width": (
            sum(row["mean_reported_interval_width"] * row["intervals_reported"]
                for row in runs if row["intervals_reported"]) / interval_count
            if interval_count else None
        ),
        "population_run_coverage_range": {
            "minimum": min(run_coverages), "maximum": max(run_coverages),
        } if run_coverages else None,
        "transformed_interval_diagnostics": transformed,
        "population_runs": runs,
    }


def run_simulation(
    manifest: dict[str, Any], replicates: int = 2000, seed: int = 20261006,
    population_replicates: int = 1,
) -> dict[str, Any]:
    if replicates < 1:
        raise ValueError("replicates must be at least 1")
    if population_replicates < 1:
        raise ValueError("population_replicates must be at least 1")
    design = _load_stratified_design(manifest)
    results = []
    for scenario_index, name in enumerate(SCENARIOS):
        runs = [
            _simulate_scenario(
                name, design, replicates,
                population_seed=seed + 100000 * scenario_index + 10 * population_index,
                sampling_seed=seed + 100000 * scenario_index + 10 * population_index + 1,
            )
            for population_index in range(population_replicates)
        ]
        results.append(_aggregate_population_runs(name, runs))
    return {
        "simulation_version": "stratified-prevalence-interval-simulation/2",
        "agreement_analyzer_version": AGREEMENT_VERSION,
        "estimand": "single_binary_category_prevalence_in_a_fixed_synthetic_finite_population",
        "design": "manifest strata; independent SRSWOR within every stratum",
        "interval_method": "implemented stratified SRSWOR variance; clipped normal Wald 95% interval; suppress interval at zero estimated variance unless census",
        "comparison_methods": [
            "logit-transformed delta-Wald interval with logistic back-transformation",
            "arcsine-square-root delta-Wald interval with bounded back-transformation",
        ],
        "seed": seed,
        "replicates_per_population": replicates,
        "population_replicates_per_scenario": population_replicates,
        "scenarios": results,
        "limitations": [
            "Synthetic prevalence patterns are diagnostic assumptions, not observed annotator behavior.",
            "Each scenario conditions on one generated finite population and measures repeated-sampling coverage.",
            "Coverage is conditional on intervals being reported; the covered-and-reported rate and availability are also shown.",
            "Transformed intervals are diagnostics only and are not established as design-valid replacements.",
            "The simulation assesses these scenarios only and does not prove general interval validity.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sampling-manifest", type=Path,
        default=Path("outputs/phase7/annotation_candidate_frame_v3_400_manifest.json"),
    )
    parser.add_argument("--replicates", type=int, default=2000)
    parser.add_argument("--population-replicates", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20261006)
    parser.add_argument(
        "--output", type=Path,
        default=Path("outputs/phase10/prevalence_ci_design_simulation.json"),
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        manifest_bytes = args.sampling_manifest.read_bytes()
        manifest = json.loads(manifest_bytes)
        if not isinstance(manifest, dict):
            raise ValueError("sampling manifest must contain a JSON object")
        report = run_simulation(manifest, args.replicates, args.seed, args.population_replicates)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    report["input_sha256"] = {
        "sampling_manifest": hashlib.sha256(manifest_bytes).hexdigest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Simulation report: {args.output}")
    for row in report["scenarios"]:
        coverage = row["conditional_coverage"]
        transformed = row["transformed_interval_diagnostics"]
        print(
            f"{row['scenario']}: coverage={coverage if coverage is not None else 'NA'}, "
            f"availability={row['interval_availability_rate']:.3f}, "
            f"logit={transformed['logit_delta']['conditional_coverage']}, "
            f"arcsine={transformed['arcsine_delta']['conditional_coverage']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
