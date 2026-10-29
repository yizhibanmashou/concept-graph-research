"""Compute reproducible agreement summaries for two independent annotators.

This reports agreement, not annotation correctness. It aligns records by
item_id, checks source identity, and separates categorical, AST, rule, and
evidence-span measurements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.logic.annotation_validator import (
    ANALYSIS_STATUSES,
    PROJECTION_STATUSES,
    SUPPORT_REASON_VALUES,
    load_jsonl,
    validate_dataset,
)


AGREEMENT_VERSION = "wordnet-annotation-agreement/13"
CLAIM_RELATIONS = ("necessary", "sufficient", "biconditional", "typical", "example", "other")
SEMANTIC_SUPPORT_STATUSES = ("supported", "not_supported", "uncertain", "unassessed")
BOOTSTRAP_REPLICATES = 1000
BOOTSTRAP_SEED = 20261003
SPARSE_DISAGREEMENT_WARNING_THRESHOLD = 10


def _canonical_ast(node_id: str, nodes: dict[str, dict[str, Any]]) -> Any:
    def canonical_term(argument: dict[str, Any], bound_variables: tuple[str, ...]) -> Any:
        kind, identifier = argument["kind"], argument["id"]
        if kind == "constant":
            return (kind, identifier)
        for distance, bound_id in enumerate(reversed(bound_variables)):
            if identifier == bound_id:
                return (kind, ("bound", distance))
        return (kind, ("free", identifier))

    def visit(current_id: str, bound_variables: tuple[str, ...] = ()) -> Any:
        node = nodes[current_id]
        kind = node["kind"]
        if kind == "atom":
            terms = tuple(canonical_term(argument, bound_variables) for argument in node["arguments"])
            return ("atom", node["predicate"], terms)
        if kind in {"and", "or"}:
            children = [visit(child_id, bound_variables) for child_id in node["children"]]
            children.sort(key=lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":")))
            return (kind, tuple(children))
        if kind == "not":
            return ("not", visit(node["child"], bound_variables))
        if kind in {"forall", "exists"}:
            binder = node["binder"]
            return (kind, (binder["kind"], "bound"),
                    visit(node["child"], (*bound_variables, binder["id"])))
        if kind == "implies":
            return ("implies", visit(node["antecedent"], bound_variables),
                    visit(node["consequent"], bound_variables))
        if kind == "unknown":
            return ("unknown", node["reason"])
        raise ValueError(f"unsupported AST node kind for agreement: {kind!r}")

    return visit(node_id)


def _node_counter(record: dict[str, Any]) -> Counter:
    counter = Counter()
    analysis = record["analysis"]
    for node in analysis["nodes"]:
        start, end = node["span"]["start"], node["span"]["end"]
        label = node["kind"]
        if node["kind"] == "atom":
            label = (label, node["predicate"], tuple(arg["kind"] for arg in node["arguments"]))
        elif node["kind"] == "unknown":
            label = (label, node["reason"])
        counter[(label, start, end)] += 1
    return counter


def _root_counter(record: dict[str, Any]) -> Counter:
    nodes = {node["id"]: node for node in record["analysis"]["nodes"]}
    roots = record["analysis"]["root_node_ids"]
    return Counter(json.dumps(_canonical_ast(root_id, nodes), ensure_ascii=False, separators=(",", ":"))
                    for root_id in roots)


def _evidence_counter(record: dict[str, Any]) -> Counter:
    return Counter(
        (span["start"], span["end"])
        for claim in record["analysis"]["rule_claims"]
        for span in claim["evidence_spans"]
    )


def _claim_counter(record: dict[str, Any], *, include_evidence: bool) -> Counter:
    nodes = {node["id"]: node for node in record["analysis"]["nodes"]}
    claims = Counter()
    for claim in record["analysis"]["rule_claims"]:
        signature: tuple[Any, ...] = (
            claim["relation"],
            claim["direction"],
            claim.get("target_variable") if record.get("schema_version") == "0.7-draft" else None,
            _canonical_ast(claim["formula_node_id"], nodes),
            tuple(sorted(claim.get("variable_sorts", {}).items()))
            if record.get("schema_version") == "0.5-draft" else (),
            tuple(sorted(
                (
                    variable,
                    judgment.get("status"),
                    judgment.get("sort"),
                    judgment.get("basis"),
                    tuple(sorted((span["start"], span["end"])
                                 for span in judgment.get("evidence_spans", []))),
                )
                for variable, judgment in claim.get("variable_sort_judgments", {}).items()
            )) if record.get("schema_version") in {"0.6-draft", "0.7-draft"} else (),
        )
        if include_evidence:
            evidence = tuple(sorted((span["start"], span["end"]) for span in claim["evidence_spans"]))
            support_reasons = tuple(sorted(claim.get("support_reasons", [])))
            inference_basis = tuple(sorted(claim.get("inference_basis", [])))
            signature += (evidence, claim["semantic_support"], claim["confidence"], support_reasons, inference_basis)
        claims[signature] += 1
    return claims


def _variable_sort_judgment_counter(record: dict[str, Any]) -> Counter:
    """Compare typed-schema sort judgments against aligned claim structure, excluding rationale prose."""
    if record.get("schema_version") not in {"0.6-draft", "0.7-draft"}:
        return Counter()
    nodes = {node["id"]: node for node in record["analysis"]["nodes"]}
    decisions = Counter()
    for claim in record["analysis"]["rule_claims"]:
        claim_key = (claim["relation"], claim["direction"], claim.get("target_variable"),
                     _canonical_ast(claim["formula_node_id"], nodes))
        for variable, judgment in claim["variable_sort_judgments"].items():
            spans = tuple(sorted((span["start"], span["end"])
                                 for span in judgment["evidence_spans"]))
            decisions[(claim_key, variable, judgment["status"], judgment["sort"],
                       judgment["basis"], spans)] += 1
    return decisions


def _micro_prf(predicted: Counter, reference: Counter) -> dict[str, Any]:
    predicted_count, reference_count = sum(predicted.values()), sum(reference.values())
    if predicted_count == 0 and reference_count == 0:
        return {"precision": None, "recall": None, "f1": None, "true_positive": 0,
                "predicted_count": 0, "reference_count": 0, "note": "no spans/nodes to compare"}
    true_positive = sum((predicted & reference).values())
    precision = true_positive / predicted_count if predicted_count else 0.0
    recall = true_positive / reference_count if reference_count else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "true_positive": true_positive,
            "predicted_count": predicted_count, "reference_count": reference_count}


def _cohens_kappa(values_a: list[str], values_b: list[str]) -> dict[str, Any]:
    if len(values_a) != len(values_b):
        raise ValueError("paired categorical values must have equal lengths")
    n = len(values_a)
    if n == 0:
        return {"n": 0, "observed_agreement": None, "cohens_kappa": None, "status": "no_paired_items"}
    observed = sum(left == right for left, right in zip(values_a, values_b)) / n
    count_a, count_b = Counter(values_a), Counter(values_b)
    categories = sorted(set(count_a) | set(count_b))
    expected = sum(count_a[c] * count_b[c] for c in categories) / (n * n)
    matrix = {left: {right: 0 for right in categories} for left in categories}
    for left, right in zip(values_a, values_b):
        matrix[left][right] += 1
    if expected == 1.0:
        return {"n": n, "observed_agreement": observed, "cohens_kappa": None,
                "status": "undefined_expected_agreement_is_one", "confusion_matrix": matrix}
    return {"n": n, "observed_agreement": observed, "cohens_kappa": 1.0 - (1.0 - observed) / (1.0 - expected),
            "status": "computed", "confusion_matrix": matrix}


def _load_stratified_design(manifest: dict[str, Any]) -> dict[str, Any]:
    strata_raw = manifest.get("random_panel_strata")
    if not isinstance(strata_raw, dict) or not strata_raw:
        raise ValueError("sampling manifest lacks random_panel_strata")
    strata: dict[str, dict[str, float | int]] = {}
    for name, row in strata_raw.items():
        if not isinstance(name, str) or not isinstance(row, dict):
            raise ValueError("sampling manifest has an invalid stratum entry")
        population_count = row.get("population_count")
        sample_count = row.get("sample_count")
        if (not isinstance(population_count, int) or isinstance(population_count, bool) or population_count < 1
                or not isinstance(sample_count, int) or isinstance(sample_count, bool)
                or sample_count < 1 or sample_count > population_count):
            raise ValueError(f"invalid population/sample counts for stratum {name!r}")
        if sample_count < 2 and sample_count < population_count:
            raise ValueError(f"stratum {name!r} has one sampled item; design variance is not estimable")
        expected_weight = population_count / sample_count
        design_weight = row.get("design_weight")
        if (not isinstance(design_weight, (int, float)) or isinstance(design_weight, bool)
                or abs(float(design_weight) - expected_weight) > 1e-10 * max(1.0, expected_weight)):
            raise ValueError(f"invalid design weight for stratum {name!r}")
        strata[name] = {
            "population_count": population_count,
            "sample_count": sample_count,
            "design_weight": expected_weight,
        }

    population_total = sum(int(row["population_count"]) for row in strata.values())
    sample_total = sum(int(row["sample_count"]) for row in strata.values())
    if manifest.get("eligible_oewn_sense_count") != population_total:
        raise ValueError("stratum population counts do not sum to eligible_oewn_sense_count")
    if manifest.get("random_panel_count") != sample_total:
        raise ValueError("stratum sample counts do not sum to random_panel_count")
    return {"population_count": population_total, "sample_count": sample_total, "strata": strata}


def _validate_sampling_binding(
    records_a: list[dict[str, Any]], records_b: list[dict[str, Any]],
    sampling_manifest: dict[str, Any], batch_manifest: dict[str, Any],
) -> None:
    frame_hash = sampling_manifest.get("frame_sha256")
    if not isinstance(frame_hash, str) or not frame_hash:
        raise ValueError("sampling manifest lacks frame_sha256")
    if batch_manifest.get("frame_sha256") != frame_hash:
        raise ValueError("sampling and blind-batch manifests refer to different candidate frames")
    expected_batch_hash = batch_manifest.get("batch_sha256")
    if not isinstance(expected_batch_hash, str) or not expected_batch_hash:
        raise ValueError("blind-batch manifest lacks batch_sha256")
    all_records = [*records_a, *records_b]
    observed_hashes = []
    for record in all_records:
        provenance = record.get("provenance", {})
        value = provenance.get("blind_batch_sha256") if isinstance(provenance, dict) else None
        if not isinstance(value, str) or not value:
            raise ValueError("canonical annotation lacks blind_batch_sha256 provenance")
        observed_hashes.append(value)
    if set(observed_hashes) != {expected_batch_hash}:
        raise ValueError("canonical annotations are not bound to the supplied blind-batch manifest")
    candidate_count = batch_manifest.get("candidate_count")
    planned_count = sampling_manifest.get("random_panel_count", 0) + sampling_manifest.get("diagnostic_panel_count", 0)
    if candidate_count != planned_count:
        raise ValueError("blind-batch candidate count differs from the sampling manifest")


def _design_weighted_kappa(
    item_ids: list[str], values_a: list[str], values_b: list[str],
    stratum_by_item: dict[str, str], design: dict[str, Any],
) -> dict[str, Any]:
    """Estimate nominal Cohen kappa and Taylor-linearized SRSWOR variance."""
    if not (len(item_ids) == len(values_a) == len(values_b)):
        raise ValueError("weighted kappa inputs must have equal lengths")
    if len(item_ids) != design["sample_count"]:
        raise ValueError("weighted kappa requires a complete random panel with no missing paired annotations")
    stratum_counts = Counter(stratum_by_item.get(item_id) for item_id in item_ids)
    for name, spec in design["strata"].items():
        if stratum_counts.get(name, 0) != spec["sample_count"]:
            raise ValueError(f"paired sample count does not match manifest for stratum {name!r}")
    if set(stratum_counts) != set(design["strata"]):
        raise ValueError("paired annotations contain unknown or missing sampling strata")

    population_total = design["population_count"]
    weight_by_stratum = {
        name: spec["population_count"] / population_total
        for name, spec in design["strata"].items()
    }
    categories = sorted(set(values_a) | set(values_b))
    sample_disagreement_count = sum(left != right for left, right in zip(values_a, values_b))
    joint: dict[tuple[str, str], float] = {(a, b): 0.0 for a in categories for b in categories}
    weight_sum = 0.0
    item_weights = []
    for item_id, left, right in zip(item_ids, values_a, values_b):
        stratum = stratum_by_item[item_id]
        row = design["strata"][stratum]
        weight = float(row["design_weight"])
        item_weights.append(weight)
        weight_sum += weight
        joint[(left, right)] += weight
    if abs(weight_sum - population_total) > 1e-8 * max(1, population_total):
        raise ValueError("observed design weights do not sum to the eligible population")
    joint = {cell: count / population_total for cell, count in joint.items()}
    row_margins = {category: sum(joint[(category, other)] for other in categories) for category in categories}
    col_margins = {category: sum(joint[(other, category)] for other in categories) for category in categories}
    disagreement = sum(joint[(left, right)] for left in categories for right in categories if left != right)
    observed = 1.0 - disagreement
    expected = sum(row_margins[c] * col_margins[c] for c in categories)
    if expected >= 1.0 - 1e-15:
        return {
            "n": len(item_ids), "population_count": population_total,
            "sample_disagreement_count": sample_disagreement_count,
            "observed_agreement": observed, "expected_agreement": expected,
            "weighted_cohens_kappa": None, "status": "undefined_expected_agreement_is_one",
            "weighted_joint_distribution": {
                left: {right: joint[(left, right)] for right in categories} for left in categories
            },
            "variance_method": "stratified SRSWOR Taylor linearization; unavailable for undefined kappa",
        }

    kappa = 1.0 - disagreement / (1.0 - expected)
    gradients = {}
    for left in categories:
        for right in categories:
            d_observed = 1.0 if left == right else 0.0
            # For q[left, right], d(sum_k row_k * col_k) = col_left + row_right.
            d_expected = col_margins[left] + row_margins[right]
            gradients[(left, right)] = (
                d_observed / (1.0 - expected)
                + (observed - 1.0) * d_expected / (1.0 - expected) ** 2
            )

    influence_by_stratum: dict[str, list[float]] = defaultdict(list)
    for item_id, left, right in zip(item_ids, values_a, values_b):
        influence_by_stratum[stratum_by_item[item_id]].append(gradients[(left, right)])
    variance = 0.0
    for name, influences in influence_by_stratum.items():
        spec = design["strata"][name]
        n_h = int(spec["sample_count"])
        N_h = int(spec["population_count"])
        if n_h == N_h:
            continue
        mean_h = sum(influences) / n_h
        sample_variance = sum((value - mean_h) ** 2 for value in influences) / (n_h - 1)
        stratum_weight = N_h / population_total
        variance += stratum_weight**2 * (1.0 - n_h / N_h) * sample_variance / n_h
    standard_error = variance**0.5
    z_975 = 1.959963984540054
    interval_warning = None
    if sample_disagreement_count < SPARSE_DISAGREEMENT_WARNING_THRESHOLD:
        interval_warning = (
            f"Only {sample_disagreement_count} discordant pairs were observed (<"
            f"{SPARSE_DISAGREEMENT_WARNING_THRESHOLD}). Under a sparse-margin/high-agreement design simulation, "
            "Taylor-Wald intervals severely undercovered. Treat this interval as exploratory, not as a calibrated "
            "95% confidence interval. The threshold is an operational alert, not a validated cutoff."
        )
    wald_ci = None
    if sample_disagreement_count > 0:
        wald_ci = {
            "lower": kappa - z_975 * standard_error,
            "upper": kappa + z_975 * standard_error,
        }
    return {
        "n": len(item_ids), "population_count": population_total,
        "sample_disagreement_count": sample_disagreement_count,
        "observed_agreement": observed, "expected_agreement": expected,
        "weighted_cohens_kappa": kappa,
        "standard_error": standard_error,
        "wald_95_ci": wald_ci,
        "wald_95_ci_warning": interval_warning,
        "sparse_disagreement_warning_threshold": SPARSE_DISAGREEMENT_WARNING_THRESHOLD,
        "status": "computed" if wald_ci is not None else "point_estimate_only_no_observed_disagreements",
        "weighted_joint_distribution": {
            left: {right: joint[(left, right)] for right in categories} for left in categories
        },
        "variance_method": "stratified SRSWOR Taylor linearization; normal Wald 95% interval",
        "kish_effective_n": weight_sum**2 / sum(weight**2 for weight in item_weights),
    }


def _design_weighted_prevalence(
    item_ids: list[str], values: list[str], stratum_by_item: dict[str, str],
    design: dict[str, Any], categories: list[str],
) -> dict[str, Any]:
    """Estimate category prevalence and stratified-SRSWOR variance per annotator."""
    if len(item_ids) != len(values):
        raise ValueError("weighted prevalence inputs must have equal lengths")
    if len(item_ids) != design["sample_count"]:
        raise ValueError("weighted prevalence requires a complete random panel")
    if len(set(item_ids)) != len(item_ids):
        raise ValueError("weighted prevalence item IDs must be unique")
    unknown = set(values) - set(categories)
    if unknown:
        raise ValueError(f"values outside the declared prevalence categories: {sorted(unknown)}")

    rows_by_stratum: dict[str, list[str]] = defaultdict(list)
    for item_id, value in zip(item_ids, values):
        stratum = stratum_by_item.get(item_id)
        if stratum not in design["strata"]:
            raise ValueError(f"missing or unknown sampling stratum for item_id {item_id!r}")
        rows_by_stratum[stratum].append(value)
    if set(rows_by_stratum) != set(design["strata"]):
        raise ValueError("weighted prevalence sample omits one or more planned strata")

    population_total = design["population_count"]
    category_results: dict[str, dict[str, Any]] = {}
    for category in categories:
        estimate = 0.0
        variance = 0.0
        sampled_positive_count = 0
        zero_variance_strata = 0
        all_census = True
        for name, spec in design["strata"].items():
            stratum_values = rows_by_stratum[name]
            n_h = int(spec["sample_count"])
            N_h = int(spec["population_count"])
            if len(stratum_values) != n_h:
                raise ValueError(f"sample count does not match manifest for stratum {name!r}")
            indicators = [value == category for value in stratum_values]
            positives = sum(indicators)
            sampled_positive_count += positives
            p_h = positives / n_h
            W_h = N_h / population_total
            estimate += W_h * p_h
            if n_h == N_h:
                continue
            all_census = False
            sample_variance = (
                sum((int(value) - p_h) ** 2 for value in indicators) / (n_h - 1)
            )
            if sample_variance == 0.0:
                zero_variance_strata += 1
            variance += W_h**2 * (1.0 - n_h / N_h) * sample_variance / n_h

        standard_error = variance**0.5
        if all_census:
            confidence_interval = {"lower": estimate, "upper": estimate}
            status = "exact_census"
            warning = None
        elif variance <= 1e-15:
            confidence_interval = None
            status = "point_estimate_only_zero_estimated_variance"
            warning = (
                "No within-stratum variation was observed for this category; a zero-width Wald interval "
                "would be unjustified without a census."
            )
        else:
            z_975 = 1.959963984540054
            confidence_interval = {
                "lower": max(0.0, estimate - z_975 * standard_error),
                "upper": min(1.0, estimate + z_975 * standard_error),
            }
            status = "computed_exploratory_clipped_normal_wald"
            warning_parts = [
                "Nominal 95% normal-Wald interval is exploratory; v3 design simulation showed undercoverage "
                "for rare and stratum-heterogeneous prevalence scenarios."
            ]
            if min(sampled_positive_count, len(item_ids) - sampled_positive_count) < SPARSE_DISAGREEMENT_WARNING_THRESHOLD:
                warning_parts.append(
                    "Fewer than 10 sampled positive or negative observations were seen; this is an "
                    "operational sparsity alert, not a calibrated cutoff."
                )
            warning = " ".join(warning_parts)
        category_results[category] = {
            "estimated_proportion": estimate,
            "estimated_population_count": estimate * population_total,
            "sampled_positive_count": sampled_positive_count,
            "standard_error": standard_error,
            "wald_95_ci": confidence_interval,
            "strata_with_zero_sample_variance": zero_variance_strata,
            "status": status,
            "ci_warning": warning,
        }
    return {
        "n": len(item_ids),
        "population_count": population_total,
        "method": "stratified post-stratified prevalence; SRSWOR finite-population variance; clipped normal Wald 95% interval",
        "category_estimates": category_results,
        "interpretation": (
            "Per-annotator descriptive marginal distribution; not adjudicated truth. Category intervals are "
            "marginal and are not simultaneous; proportions across a partition are not forced to sum to one "
            "within interval endpoints."
        ),
    }


def _paired_bootstrap(item_rows: list[dict[str, Any]], metric_fn, *,
                      replicates: int = BOOTSTRAP_REPLICATES,
                      seed: int = BOOTSTRAP_SEED) -> dict[str, Any]:
    if not item_rows:
        return {"method": "paired-item percentile bootstrap", "replicates": replicates,
                "seed": seed, "valid_replicates": 0, "intervals": {}}
    rng = random.Random(seed)
    observations: dict[str, list[float]] = {}
    undefined: Counter[str] = Counter()
    for _ in range(replicates):
        sample = [item_rows[rng.randrange(len(item_rows))] for _ in range(len(item_rows))]
        values = metric_fn(sample)
        for name, value in values.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                observations.setdefault(name, []).append(float(value))
            else:
                undefined[name] += 1

    def percentile(values: list[float], probability: float) -> float:
        ordered = sorted(values)
        position = (len(ordered) - 1) * probability
        lower, upper = int(position), min(int(position) + 1, len(ordered) - 1)
        fraction = position - lower
        return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction

    intervals = {}
    for name, values in observations.items():
        intervals[name] = {
            "lower": percentile(values, 0.025),
            "upper": percentile(values, 0.975),
            "valid_replicates": len(values),
            "undefined_replicates": undefined[name],
        }
    return {"method": "paired-item percentile bootstrap; 95% percentile interval",
            "replicates": replicates, "seed": seed, "intervals": intervals}


def _bootstrap_metric_values(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for prefix, field_a, field_b in (
        ("status", "status_a", "status_b"),
        ("projection", "projection_a", "projection_b"),
    ):
        kappa = _cohens_kappa([row[field_a] for row in rows], [row[field_b] for row in rows])
        result[f"{prefix}_observed_agreement"] = kappa["observed_agreement"]
        result[f"{prefix}_cohens_kappa"] = kappa["cohens_kappa"]
    for relation in CLAIM_RELATIONS:
        kappa = _cohens_kappa(
            [str(row["relation_presence_a"][relation]) for row in rows],
            [str(row["relation_presence_b"][relation]) for row in rows],
        )
        result[f"relation_{relation}_observed_agreement"] = kappa["observed_agreement"]
        result[f"relation_{relation}_cohens_kappa"] = kappa["cohens_kappa"]
    any_claim_kappa = _cohens_kappa(
        [str(row["any_relation_presence_a"]) for row in rows],
        [str(row["any_relation_presence_b"]) for row in rows],
    )
    result["any_rule_relation_presence_observed_agreement"] = any_claim_kappa["observed_agreement"]
    result["any_rule_relation_presence_cohens_kappa"] = any_claim_kappa["cohens_kappa"]
    for status in SEMANTIC_SUPPORT_STATUSES:
        kappa = _cohens_kappa(
            [str(row["support_presence_a"][status]) for row in rows],
            [str(row["support_presence_b"][status]) for row in rows],
        )
        result[f"semantic_support_{status}_observed_agreement"] = kappa["observed_agreement"]
        result[f"semantic_support_{status}_cohens_kappa"] = kappa["cohens_kappa"]
    for reason in sorted(SUPPORT_REASON_VALUES):
        kappa = _cohens_kappa(
            [str(row["support_reason_presence_a"][reason]) for row in rows],
            [str(row["support_reason_presence_b"][reason]) for row in rows],
        )
        result[f"support_reason_{reason}_observed_agreement"] = kappa["observed_agreement"]
        result[f"support_reason_{reason}_cohens_kappa"] = kappa["cohens_kappa"]
    for name, field_a, field_b in (
        ("ast_node", "ast_a", "ast_b"),
        ("ast_root", "ast_roots_a", "ast_roots_b"),
        ("evidence_span", "evidence_a", "evidence_b"),
        ("rule_formula_direction", "claims_a", "claims_b"),
        ("complete_claim", "full_claims_a", "full_claims_b"),
        ("variable_sort_judgment", "sort_judgments_a", "sort_judgments_b"),
    ):
        left, right = Counter(), Counter()
        for row in rows:
            left.update(row[field_a])
            right.update(row[field_b])
        scores = _micro_prf(right, left)
        for measure in ("precision", "recall", "f1"):
            result[f"{name}_{measure}"] = scores[measure]
    return result


def _relation_presence_kappas(pairs: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    result = {}
    for relation in CLAIM_RELATIONS:
        values_a = [str(any(c["relation"] == relation for c in left["analysis"]["rule_claims"])) for left, _ in pairs]
        values_b = [str(any(c["relation"] == relation for c in right["analysis"]["rule_claims"])) for _, right in pairs]
        result[relation] = _cohens_kappa(values_a, values_b)
    return result


def _item_map(records: list[dict[str, Any]], name: str) -> tuple[dict[str, dict[str, Any]], str]:
    errors = validate_dataset(records)
    if errors:
        raise ValueError(f"{name} records failed annotation validation: " + "; ".join(errors[:5]))
    by_item: dict[str, dict[str, Any]] = {}
    annotators = set()
    for record in records:
        item_id = record["item_id"]
        if item_id in by_item:
            raise ValueError(f"{name} has multiple records for item_id {item_id!r}; expected one independent pass per item")
        if record["annotation"]["adjudication_status"] != "independent":
            raise ValueError(f"{name} includes a non-independent annotation; agreement requires blind independent passes")
        annotators.add(record["annotation"]["annotator_id"])
        by_item[item_id] = record
    if len(annotators) != 1:
        raise ValueError(f"{name} must contain records from exactly one annotator")
    return by_item, next(iter(annotators))


def compare_annotators(
    records_a: list[dict[str, Any]], records_b: list[dict[str, Any]],
    sampling_manifest: dict[str, Any] | None = None,
    batch_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare two validated, independent annotation batches by item_id."""
    items_a, annotator_a = _item_map(records_a, "annotator A")
    items_b, annotator_b = _item_map(records_b, "annotator B")
    if annotator_a == annotator_b:
        raise ValueError("the two annotation batches must have distinct annotator IDs")
    common = sorted(items_a.keys() & items_b.keys())
    if not common:
        raise ValueError("the two annotation batches have no shared item IDs")

    def sampling_panel(record: dict[str, Any]) -> str:
        provenance = record.get("provenance", {})
        panel = provenance.get("sampling_panel") if isinstance(provenance, dict) else None
        return panel if isinstance(panel, str) and panel else "sampling_panel_unknown"

    for item_id in common:
        if sampling_panel(items_a[item_id]) != sampling_panel(items_b[item_id]):
            raise ValueError(f"sampling panel differs between annotators for item_id {item_id!r}")
    panel_labels = sorted({sampling_panel(items_a[item_id]) for item_id in common})
    if len(panel_labels) > 1:
        by_panel = {}
        for panel in panel_labels:
            panel_a = [record for record in records_a if sampling_panel(record) == panel]
            panel_b = [record for record in records_b if sampling_panel(record) == panel]
            if not panel_a or not panel_b:
                raise ValueError(f"sampling panel {panel!r} is absent from one annotator batch")
            panel_manifest = sampling_manifest if panel == "random_stratified" else None
            panel_batch_manifest = batch_manifest if panel_manifest is not None else None
            by_panel[panel] = compare_annotators(panel_a, panel_b, panel_manifest, panel_batch_manifest)
        return {
            "agreement_version": AGREEMENT_VERSION,
            "annotators": {"a": annotator_a, "b": annotator_b},
            "unpaired_item_count": {"a_only": len(items_a.keys() - items_b.keys()),
                                     "b_only": len(items_b.keys() - items_a.keys())},
            "by_sampling_panel": by_panel,
            "pooled_metrics": None,
            "interpretation_limit": (
                "Panels use different sampling mechanisms and are reported separately. No pooled agreement estimate is computed. "
        "Within-panel unweighted metrics and item bootstrap intervals are exploratory summaries, not design-adjusted population estimates. "
        "A random panel receives weighted categorical kappa only when its matching sampling manifest is supplied and the full planned sample is paired. "
        "The diagnostic panel is not for population estimates."
            ),
        }

    pairs = []
    per_item = []
    bootstrap_items = []
    ast_a, ast_b, ast_roots_a, ast_roots_b = Counter(), Counter(), Counter(), Counter()
    evidence_a, evidence_b = Counter(), Counter()
    claims_a, claims_b, full_claims_a, full_claims_b = Counter(), Counter(), Counter(), Counter()
    sort_judgments_a, sort_judgments_b = Counter(), Counter()
    for item_id in common:
        left, right = items_a[item_id], items_b[item_id]
        identity_fields = ("resource", "version", "record_id", "input_sha256")
        if (left["sense"]["gloss"] != right["sense"]["gloss"]
                or left["sense"]["synset_id"] != right["sense"]["synset_id"]
                or left["sense"]["lemmas"] != right["sense"]["lemmas"]
                or left["sense"]["pos"] != right["sense"]["pos"]
                or any(left["source"][field] != right["source"][field] for field in identity_fields)):
            raise ValueError(f"source identity or gloss differs between annotators for item_id {item_id!r}")
        pairs.append((left, right))
        left_nodes, right_nodes = _node_counter(left), _node_counter(right)
        left_roots, right_roots = _root_counter(left), _root_counter(right)
        left_evidence, right_evidence = _evidence_counter(left), _evidence_counter(right)
        left_claims, right_claims = _claim_counter(left, include_evidence=False), _claim_counter(right, include_evidence=False)
        left_full, right_full = _claim_counter(left, include_evidence=True), _claim_counter(right, include_evidence=True)
        left_sort_judgments = _variable_sort_judgment_counter(left)
        right_sort_judgments = _variable_sort_judgment_counter(right)
        ast_a.update(left_nodes)
        ast_b.update(right_nodes)
        ast_roots_a.update(left_roots)
        ast_roots_b.update(right_roots)
        evidence_a.update(left_evidence)
        evidence_b.update(right_evidence)
        claims_a.update(left_claims)
        claims_b.update(right_claims)
        full_claims_a.update(left_full)
        full_claims_b.update(right_full)
        sort_judgments_a.update(left_sort_judgments)
        sort_judgments_b.update(right_sort_judgments)
        bootstrap_items.append({
            "status_a": left["analysis"]["status"],
            "status_b": right["analysis"]["status"],
            "projection_a": left["analysis"]["horn_projection"]["status"],
            "projection_b": right["analysis"]["horn_projection"]["status"],
            "ast_a": left_nodes,
            "ast_b": right_nodes,
            "ast_roots_a": left_roots,
            "ast_roots_b": right_roots,
            "evidence_a": left_evidence,
            "evidence_b": right_evidence,
            "claims_a": left_claims,
            "claims_b": right_claims,
            "full_claims_a": left_full,
            "full_claims_b": right_full,
            "sort_judgments_a": left_sort_judgments,
            "sort_judgments_b": right_sort_judgments,
            "relation_presence_a": {relation: any(claim["relation"] == relation for claim in left["analysis"]["rule_claims"])
                                    for relation in CLAIM_RELATIONS},
            "relation_presence_b": {relation: any(claim["relation"] == relation for claim in right["analysis"]["rule_claims"])
                                    for relation in CLAIM_RELATIONS},
            "any_relation_presence_a": bool(left["analysis"]["rule_claims"]),
            "any_relation_presence_b": bool(right["analysis"]["rule_claims"]),
            "support_presence_a": {status: any(claim["semantic_support"] == status for claim in left["analysis"]["rule_claims"])
                                    for status in SEMANTIC_SUPPORT_STATUSES},
            "support_presence_b": {status: any(claim["semantic_support"] == status for claim in right["analysis"]["rule_claims"])
                                    for status in SEMANTIC_SUPPORT_STATUSES},
            "support_reason_presence_a": {
                reason: any(reason in claim.get("support_reasons", [])
                            for claim in left["analysis"]["rule_claims"])
                for reason in sorted(SUPPORT_REASON_VALUES)
            },
            "support_reason_presence_b": {
                reason: any(reason in claim.get("support_reasons", [])
                            for claim in right["analysis"]["rule_claims"])
                for reason in sorted(SUPPORT_REASON_VALUES)
            },
        })
        per_item.append({
            "item_id_sha256": hashlib.sha256(item_id.encode("utf-8")).hexdigest(),
            "status_agreement": left["analysis"]["status"] == right["analysis"]["status"],
            "ast_node_multiset_exact": left_nodes == right_nodes,
            "ast_root_structure_multiset_exact": left_roots == right_roots,
            "rule_formula_direction_multiset_exact": left_claims == right_claims,
            "evidence_span_multiset_exact": left_evidence == right_evidence,
            "support_reason_presence_exact": {
                reason: any(reason in claim.get("support_reasons", [])
                            for claim in left["analysis"]["rule_claims"])
                == any(reason in claim.get("support_reasons", [])
                       for claim in right["analysis"]["rule_claims"])
                for reason in sorted(SUPPORT_REASON_VALUES)
            },
            "complete_rule_claim_multiset_exact": left_full == right_full,
            "variable_sort_judgment_multiset_exact": left_sort_judgments == right_sort_judgments,
        })

    status_kappa = _cohens_kappa([left["analysis"]["status"] for left, _ in pairs],
                                 [right["analysis"]["status"] for _, right in pairs])
    projection_kappa = _cohens_kappa([left["analysis"]["horn_projection"]["status"] for left, _ in pairs],
                                     [right["analysis"]["horn_projection"]["status"] for _, right in pairs])
    bootstrap = _paired_bootstrap(bootstrap_items, _bootstrap_metric_values)
    status_kappa["bootstrap_95_ci"] = {
        key: value for key, value in bootstrap["intervals"].items()
        if key.startswith("status_")
    }
    projection_kappa["bootstrap_95_ci"] = {
        key: value for key, value in bootstrap["intervals"].items()
        if key.startswith("projection_")
    }
    metric_intervals = {
        key: value for key, value in bootstrap["intervals"].items()
        if not key.startswith("status_") and not key.startswith("projection_")
    }
    bootstrap_metric_prefixes = (
        ("ast_labeled_span_micro", "ast_node"),
        ("ast_root_structure_micro", "ast_root"),
        ("evidence_span_micro", "evidence_span"),
        ("rule_formula_direction_multiset_micro", "rule_formula_direction"),
        ("complete_rule_claim_multiset_micro", "complete_claim"),
        ("variable_sort_judgment_multiset_micro", "variable_sort_judgment"),
    )
    metric_results = {
        "ast_labeled_span_micro": _micro_prf(ast_b, ast_a),
        "ast_root_structure_micro": _micro_prf(ast_roots_b, ast_roots_a),
        "evidence_span_micro": _micro_prf(evidence_b, evidence_a),
        "rule_formula_direction_multiset_micro": _micro_prf(claims_b, claims_a),
        "complete_rule_claim_multiset_micro": _micro_prf(full_claims_b, full_claims_a),
        "variable_sort_judgment_multiset_micro": _micro_prf(sort_judgments_b, sort_judgments_a),
    }
    for metric_name, prefix in bootstrap_metric_prefixes:
        metric_results[metric_name]["bootstrap_95_ci"] = {
            measure: metric_intervals[f"{prefix}_{measure}"]
            for measure in ("precision", "recall", "f1")
            if f"{prefix}_{measure}" in metric_intervals
        }
    relation_kappas = _relation_presence_kappas(pairs)
    for relation in CLAIM_RELATIONS:
        prefix = f"relation_{relation}"
        relation_kappas[relation]["bootstrap_95_ci"] = {
            key: value for key, value in bootstrap["intervals"].items()
            if key.startswith(prefix + "_")
        }
    any_rule_relation_presence = _cohens_kappa(
        [str(bool(left["analysis"]["rule_claims"])) for left, _ in pairs],
        [str(bool(right["analysis"]["rule_claims"])) for _, right in pairs],
    )
    any_rule_relation_presence["bootstrap_95_ci"] = {
        key: value for key, value in bootstrap["intervals"].items()
        if key.startswith("any_rule_relation_presence_")
    }
    support_kappas = {}
    for status in SEMANTIC_SUPPORT_STATUSES:
        values_a = [str(any(claim["semantic_support"] == status for claim in left["analysis"]["rule_claims"]))
                    for left, _ in pairs]
        values_b = [str(any(claim["semantic_support"] == status for claim in right["analysis"]["rule_claims"]))
                    for _, right in pairs]
        support_kappas[status] = _cohens_kappa(values_a, values_b)
        prefix = f"semantic_support_{status}"
        support_kappas[status]["bootstrap_95_ci"] = {
            key: value for key, value in bootstrap["intervals"].items()
            if key.startswith(prefix + "_")
        }
    support_reason_kappas = {}
    for reason in sorted(SUPPORT_REASON_VALUES):
        values_a = [str(any(reason in claim.get("support_reasons", [])
                            for claim in left["analysis"]["rule_claims"]))
                    for left, _ in pairs]
        values_b = [str(any(reason in claim.get("support_reasons", [])
                            for claim in right["analysis"]["rule_claims"]))
                    for _, right in pairs]
        support_reason_kappas[reason] = _cohens_kappa(values_a, values_b)
        prefix = f"support_reason_{reason}"
        support_reason_kappas[reason]["bootstrap_95_ci"] = {
            key: value for key, value in bootstrap["intervals"].items()
            if key.startswith(prefix + "_")
        }

    design_weighted = None
    if sampling_manifest is not None:
        if batch_manifest is None:
            raise ValueError("design-weighted agreement also requires the matching blind-batch export manifest")
        if sampling_panel(pairs[0][0]) != "random_stratified":
            raise ValueError("design-weighted agreement requires the random_stratified panel")
        if items_a.keys() != items_b.keys():
            raise ValueError("design-weighted agreement requires complete paired returns from both annotators")
        _validate_sampling_binding(records_a, records_b, sampling_manifest, batch_manifest)
        design = _load_stratified_design(sampling_manifest)
        stratum_by_item = {}
        for item_id, (left, right) in zip(common, pairs):
            left_provenance = left.get("provenance", {})
            right_provenance = right.get("provenance", {})
            left_stratum = left_provenance.get("stratum") if isinstance(left_provenance, dict) else None
            right_stratum = right_provenance.get("stratum") if isinstance(right_provenance, dict) else None
            if not isinstance(left_stratum, str) or left_stratum != right_stratum:
                raise ValueError(f"sampling stratum is missing or differs for item_id {item_id!r}")
            stratum_by_item[item_id] = left_stratum

        item_ids = list(common)
        def weighted_kappa(values_a: list[str], values_b: list[str]) -> dict[str, Any]:
            return _design_weighted_kappa(item_ids, values_a, values_b, stratum_by_item, design)

        relation_weighted = {}
        for relation in CLAIM_RELATIONS:
            relation_weighted[relation] = weighted_kappa(
                [str(any(claim["relation"] == relation for claim in left["analysis"]["rule_claims"]))
                 for left, _ in pairs],
                [str(any(claim["relation"] == relation for claim in right["analysis"]["rule_claims"]))
                 for _, right in pairs],
            )
        support_weighted = {}
        for status in SEMANTIC_SUPPORT_STATUSES:
            support_weighted[status] = weighted_kappa(
                [str(any(claim["semantic_support"] == status for claim in left["analysis"]["rule_claims"]))
                 for left, _ in pairs],
                [str(any(claim["semantic_support"] == status for claim in right["analysis"]["rule_claims"]))
                 for _, right in pairs],
            )
        support_reason_weighted = {}
        for reason in sorted(SUPPORT_REASON_VALUES):
            support_reason_weighted[reason] = weighted_kappa(
                [str(any(reason in claim.get("support_reasons", [])
                         for claim in left["analysis"]["rule_claims"]))
                 for left, _ in pairs],
                [str(any(reason in claim.get("support_reasons", [])
                         for claim in right["analysis"]["rule_claims"]))
                 for _, right in pairs],
            )
        any_rule_relation_weighted = weighted_kappa(
            [str(bool(left["analysis"]["rule_claims"])) for left, _ in pairs],
            [str(bool(right["analysis"]["rule_claims"])) for _, right in pairs],
        )

        def marginal_prevalence(records_index: int) -> dict[str, Any]:
            selected_records = [pair[records_index] for pair in pairs]

            def prevalence(values: list[str], categories: list[str]) -> dict[str, Any]:
                return _design_weighted_prevalence(item_ids, values, stratum_by_item, design, categories)

            binary_categories = ["absent", "present"]
            return {
                "analysis_status": prevalence(
                    [record["analysis"]["status"] for record in selected_records],
                    sorted(ANALYSIS_STATUSES),
                ),
                "horn_projection_status": prevalence(
                    [record["analysis"]["horn_projection"]["status"] for record in selected_records],
                    sorted(PROJECTION_STATUSES),
                ),
                "rule_relation_presence_by_item": {
                    relation: prevalence(
                        [
                            "present" if any(claim["relation"] == relation
                                             for claim in record["analysis"]["rule_claims"])
                            else "absent"
                            for record in selected_records
                        ],
                        binary_categories,
                    )
                    for relation in CLAIM_RELATIONS
                },
                "any_rule_relation_presence_by_item": prevalence(
                    [
                        "present" if record["analysis"]["rule_claims"] else "absent"
                        for record in selected_records
                    ],
                    binary_categories,
                ),
                "semantic_support_presence_by_item": {
                    support: prevalence(
                        [
                            "present" if any(claim["semantic_support"] == support
                                             for claim in record["analysis"]["rule_claims"])
                            else "absent"
                            for record in selected_records
                        ],
                        binary_categories,
                    )
                    for support in SEMANTIC_SUPPORT_STATUSES
                },
                "support_reason_presence_by_item": {
                    reason: prevalence(
                        [
                            "present" if any(reason in claim.get("support_reasons", [])
                                             for claim in record["analysis"]["rule_claims"])
                            else "absent"
                            for record in selected_records
                        ],
                        binary_categories,
                    )
                    for reason in sorted(SUPPORT_REASON_VALUES)
                },
            }

        rater_prevalence = {
            "annotator_a": marginal_prevalence(0),
            "annotator_b": marginal_prevalence(1),
        }
        design_weighted = {
            "method": "Horvitz-Thompson stratum weights; weighted nominal Cohen kappa; stratified SRSWOR Taylor linearization",
            "analysis_status": weighted_kappa(
                [left["analysis"]["status"] for left, _ in pairs],
                [right["analysis"]["status"] for _, right in pairs],
            ),
            "horn_projection_status": weighted_kappa(
                [left["analysis"]["horn_projection"]["status"] for left, _ in pairs],
                [right["analysis"]["horn_projection"]["status"] for _, right in pairs],
            ),
            "rule_relation_presence_by_item": relation_weighted,
            "any_rule_relation_presence_by_item": any_rule_relation_weighted,
            "semantic_support_presence_by_item": support_weighted,
            "support_reason_presence_by_item": support_reason_weighted,
            "marginal_prevalence_by_annotator": rater_prevalence,
            "scope": "finite_target_population_defined_by_the_supplied_sampling_manifest",
            "limitations": (
                "Requires every planned random-panel item to have paired labels and stratum metadata. "
                "Kappa intervals are normal Wald approximations from first-order Taylor linearization. "
                "Per-annotator prevalence intervals are clipped normal Wald approximations and have not been coverage-calibrated for rare categories. "
                "No design-weighted AST/F1 intervals are computed."
            ),
        }
    return {
        "agreement_version": AGREEMENT_VERSION,
        "annotators": {"a": annotator_a, "b": annotator_b},
        "sampling_panel": sampling_panel(pairs[0][0]),
        "estimand_scope": (
            "design_weighted_finite_population_agreement_for_categorical_labels"
            if design_weighted is not None else
            "unweighted_descriptive_agreement_within_this_observed_panel; not_a_design_adjusted_population_estimate"
        ),
        "bootstrap_interpretation": "unweighted_paired_item_percentile_resampling; exploratory_only; not_design_adjusted",
        "paired_item_count": len(common),
        "unpaired_item_count": {"a_only": len(items_a.keys() - items_b.keys()),
                                 "b_only": len(items_b.keys() - items_a.keys())},
        "analysis_status": status_kappa,
        "horn_projection_status": projection_kappa,
        "rule_relation_presence_by_item": relation_kappas,
        "any_rule_relation_presence_by_item": any_rule_relation_presence,
        "semantic_support_presence_by_item": support_kappas,
        "support_reason_presence_by_item": support_reason_kappas,
        "design_weighted_category_agreement": design_weighted,
        **metric_results,
        "paired_item_bootstrap": {key: value for key, value in bootstrap.items() if key != "intervals"},
        "per_item_agreement": per_item,
        "interpretation_limit": (
            "Agreement metrics measure reproducibility between these two annotation batches, not truth or semantic validity. "
            "Cohen's kappa is reported with raw agreement and may be undefined when expected agreement is 1; "
            "AST/evidence F1 uses exact labeled spans; rule signatures preserve variable/constant IDs and sort commutative AND/OR children."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotator_a", type=Path)
    parser.add_argument("annotator_b", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sampling-manifest", type=Path,
                        help="use the matching manifest for design-weighted random-panel categorical agreement")
    parser.add_argument("--batch-manifest", type=Path,
                        help="blind-batch export manifest binding annotations to the sampling frame")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        records_a, _, parse_errors_a = load_jsonl(args.annotator_a)
        records_b, _, parse_errors_b = load_jsonl(args.annotator_b)
        if parse_errors_a or parse_errors_b:
            raise ValueError("invalid annotation JSONL: " + "; ".join((parse_errors_a + parse_errors_b)[:5]))
        if bool(args.sampling_manifest) != bool(args.batch_manifest):
            raise ValueError("--sampling-manifest and --batch-manifest must be supplied together")
        sampling_manifest = None
        batch_manifest = None
        if args.sampling_manifest:
            sampling_manifest = json.loads(args.sampling_manifest.read_text(encoding="utf-8"))
            if not isinstance(sampling_manifest, dict):
                raise ValueError("sampling manifest must contain a JSON object")
            batch_manifest = json.loads(args.batch_manifest.read_text(encoding="utf-8"))
            if not isinstance(batch_manifest, dict):
                raise ValueError("blind-batch manifest must contain a JSON object")
        result = compare_annotators(records_a, records_b, sampling_manifest, batch_manifest)
        result["input_sha256"] = {
            "annotator_a": hashlib.sha256(args.annotator_a.read_bytes()).hexdigest(),
            "annotator_b": hashlib.sha256(args.annotator_b.read_bytes()).hexdigest(),
        }
        if args.sampling_manifest:
            result["input_sha256"]["sampling_manifest"] = hashlib.sha256(args.sampling_manifest.read_bytes()).hexdigest()
            result["input_sha256"]["batch_manifest"] = hashlib.sha256(args.batch_manifest.read_bytes()).hexdigest()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if "by_sampling_panel" in result:
        print(f"Paired items reported by sampling panel: {', '.join(result['by_sampling_panel'])}")
    else:
        print(f"Paired items: {result['paired_item_count']}; status agreement: {result['analysis_status']['observed_agreement']}")
    print(f"Agreement report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
