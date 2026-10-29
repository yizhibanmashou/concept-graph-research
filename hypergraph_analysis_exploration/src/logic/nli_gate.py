"""NLI score evaluation and conservative routing policy.

No model is bundled. Probabilities must come from a separately versioned NLI
model and thresholds must be selected on development data, never on test data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
from statistics import NormalDist
from typing import Any


LABELS = ("entailment", "neutral", "contradiction")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _is_finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, ValueError):
        return False


def _validate_scores(scores: Any, row_label: str = "NLI") -> None:
    if not isinstance(scores, dict) or set(scores) != set(LABELS):
        raise ValueError(f"{row_label} scores must contain exactly {LABELS}")
    values = [scores[label] for label in LABELS]
    if any(
        not _is_finite_number(value)
        or not 0 <= value <= 1
        for value in values
    ):
        raise ValueError(f"{row_label} probabilities must be finite numbers in [0, 1]")
    if abs(sum(values) - 1.0) > 1e-6:
        raise ValueError(f"{row_label} probabilities must sum to 1")


def _validated(rows: list[dict[str, Any]]):
    result = []
    example_ids = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or row.get("gold") not in LABELS:
            raise ValueError(f"Row {i}: gold must be one of {LABELS}")
        if row.get("split") not in {"dev", "test"} or not isinstance(row.get("sense_id"), str) or not row["sense_id"]:
            raise ValueError(f"Row {i}: include split=dev|test and a non-empty sense_id")
        for field in ("example_id", "group_id", "claim_id"):
            if field in row and (not isinstance(row[field], str) or not row[field]):
                raise ValueError(f"Row {i}: {field} must be a non-empty string when supplied")
        premise_hash = row.get("premise_sha256")
        hypothesis_hash = row.get("hypothesis_sha256")
        if (premise_hash is None) != (hypothesis_hash is None):
            raise ValueError(f"Row {i}: premise_sha256 and hypothesis_sha256 must be supplied together")
        if premise_hash is not None and (
            not isinstance(premise_hash, str) or not SHA256_RE.fullmatch(premise_hash)
            or not isinstance(hypothesis_hash, str) or not SHA256_RE.fullmatch(hypothesis_hash)
        ):
            raise ValueError(f"Row {i}: premise/hypothesis hashes must be 64-character SHA-256 values")
        example_id = row.get("example_id", row["sense_id"])
        if example_id in example_ids:
            raise ValueError(f"Row {i}: duplicate example_id {example_id!r}")
        example_ids.add(example_id)
        _validate_scores(row.get("scores"), f"Row {i}:")
        result.append(row)
    if not result:
        raise ValueError("No prediction rows supplied")
    if len({row["split"] for row in result}) != 1:
        raise ValueError("Do not mix development and test rows in one evaluation")
    return result


def _wilson_lower_bound(successes: int, total: int, confidence_level: float = 0.95):
    """One-sided Wilson score lower bound at the requested confidence level."""
    if total <= 0:
        return None
    if not _is_finite_number(confidence_level) or not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be in (0, 1)")
    z = NormalDist().inv_cdf(confidence_level)
    proportion = successes / total
    z2 = z * z
    denominator = 1 + z2 / total
    center = proportion + z2 / (2 * total)
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z2 / (4 * total * total))
    return max(0.0, (center - margin) / denominator)


def _binomial_upper_tail(successes: int, total: int, null_precision: float) -> float:
    """Exact one-sided binomial p-value for H0: precision <= null_precision."""
    if total <= 0 or successes <= 0:
        return 1.0
    if successes > total:
        raise ValueError("successes cannot exceed total")
    if null_precision == 0:
        return 0.0
    if null_precision == 1:
        return 1.0

    def log_pmf(count: int) -> float:
        return (
            math.lgamma(total + 1) - math.lgamma(count + 1)
            - math.lgamma(total - count + 1)
            + count * math.log(null_precision)
            + (total - count) * math.log1p(-null_precision)
        )

    # Sum relative to a boundary term instead of exponentiating the first PMF;
    # that PMF can underflow even when the requested tail is not negligible.
    if successes > total * null_precision:
        relative_sum = 1.0
        relative_term = 1.0
        for count in range(successes, total):
            relative_term *= (
                (total - count) / (count + 1)
                * null_precision / (1 - null_precision)
            )
            relative_sum += relative_term
        log_tail = log_pmf(successes) + math.log(relative_sum)
        return min(1.0, math.exp(log_tail)) if log_tail > -745 else 0.0

    lower_last = successes - 1
    relative_sum = 1.0
    relative_term = 1.0
    for count in range(lower_last, 0, -1):
        relative_term *= (
            count / (total - count + 1)
            * (1 - null_precision) / null_precision
        )
        relative_sum += relative_term
    log_lower_tail = log_pmf(lower_last) + math.log(relative_sum)
    return max(0.0, min(1.0, -math.expm1(log_lower_tail)))


CERTIFIED_THRESHOLD_GRID = tuple(round(index / 100, 2) for index in range(101))
CERTIFIED_SELECTOR_VERSION = "fixed-grid-exact-binomial-bonferroni/1"


def select_certified_entailment_threshold(
    dev_rows: list[dict[str, Any]], minimum_precision: float = 0.9,
    precision_confidence_level: float = 0.95,
):
    """Select a fixed-grid threshold using exact binomial tests and Bonferroni control.

    This is a finite-sample familywise certificate under IID calibration examples.
    The threshold grid is fixed independently of the observed development scores.
    """
    rows = _validated(dev_rows)
    if rows[0]["split"] != "dev":
        raise ValueError("Threshold selection must use development rows only")
    if any(not isinstance(row.get("group_id"), str) or not row["group_id"] for row in rows):
        raise ValueError("certified calibration requires a group_id for every development row")
    group_ids = [row["group_id"] for row in rows]
    if len(set(group_ids)) != len(group_ids):
        raise ValueError("certified calibration requires exactly one row per independent group_id")
    try:
        canonical_rows = json.dumps(
            sorted(rows, key=lambda row: row["group_id"]),
            ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("certified calibration rows must be finite JSON values") from exc
    development_rows_sha256 = hashlib.sha256(canonical_rows).hexdigest()
    if not _is_finite_number(minimum_precision) or not 0 < minimum_precision <= 1:
        raise ValueError("minimum_precision must be in (0, 1]")
    if not _is_finite_number(precision_confidence_level) or not 0 < precision_confidence_level < 1:
        raise ValueError("precision_confidence_level must be in (0, 1)")

    candidate_count = len(CERTIFIED_THRESHOLD_GRID)
    family_alpha = 1 - precision_confidence_level
    per_threshold_alpha = family_alpha / candidate_count
    positives = sum(row["gold"] == "entailment" for row in rows)
    best = None
    for threshold in CERTIFIED_THRESHOLD_GRID:
        selected = [row for row in rows if row["scores"]["entailment"] >= threshold]
        if not selected:
            continue
        successes = sum(row["gold"] == "entailment" for row in selected)
        p_value = _binomial_upper_tail(successes, len(selected), minimum_precision)
        if p_value <= per_threshold_alpha:
            candidate = {
                "threshold": threshold,
                "precision": successes / len(selected),
                "recall": successes / positives if positives else 0.0,
                "selected_count": len(selected),
                "selected_successes": successes,
                "minimum_precision": minimum_precision,
                "precision_confidence_level": precision_confidence_level,
                "familywise_confidence_level": precision_confidence_level,
                "familywise_alpha": family_alpha,
                "per_threshold_alpha": per_threshold_alpha,
                "exact_binomial_p_value": p_value,
                "threshold_candidate_count": candidate_count,
                "threshold_grid": "fixed_0.00_to_1.00_step_0.01_v1",
                "selector_version": CERTIFIED_SELECTOR_VERSION,
                "development_rows_sha256": development_rows_sha256,
                "multiplicity_method": "bonferroni_exact_binomial_upper_tail",
                "selection_scope": "finite-sample familywise precision tests on a predeclared fixed threshold grid",
            }
            if best is None or (candidate["recall"], -candidate["threshold"]) > (best["recall"], -best["threshold"]):
                best = candidate
    if best is None:
        return {
            "status": "no_threshold_meets_precision_floor",
            "minimum_precision": minimum_precision,
            "precision_confidence_level": precision_confidence_level,
            "familywise_confidence_level": precision_confidence_level,
            "familywise_alpha": family_alpha,
            "per_threshold_alpha": per_threshold_alpha,
            "threshold_candidate_count": candidate_count,
            "threshold_grid": "fixed_0.00_to_1.00_step_0.01_v1",
            "selector_version": CERTIFIED_SELECTOR_VERSION,
            "development_rows_sha256": development_rows_sha256,
            "multiplicity_method": "bonferroni_exact_binomial_upper_tail",
            "selection_scope": "finite-sample familywise precision tests on a predeclared fixed threshold grid",
        }
    return {"status": "selected_on_development_data", **best}


def _metrics(rows):
    confusion = {gold: {pred: 0 for pred in LABELS} for gold in LABELS}
    brier_sum = 0.0
    confidences = []
    correct = []
    calibration_bins = [{"count": 0, "confidence_sum": 0.0, "correct_sum": 0}
                       for _ in range(10)]
    for row in rows:
        pred = max(LABELS, key=lambda label: row["scores"][label])
        confusion[row["gold"]][pred] += 1
        confidence = max(row["scores"].values())
        is_correct = pred == row["gold"]
        confidences.append(confidence)
        correct.append(is_correct)
        bin_index = min(9, int(confidence * 10))
        calibration_bins[bin_index]["count"] += 1
        calibration_bins[bin_index]["confidence_sum"] += confidence
        calibration_bins[bin_index]["correct_sum"] += int(is_correct)
        brier_sum += sum((row["scores"][label] - float(row["gold"] == label)) ** 2 for label in LABELS)
    per_label = {}
    f1_values = []
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[gold][label] for gold in LABELS if gold != label)
        fn = sum(confusion[label][pred] for pred in LABELS if pred != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_label[label] = {"precision": precision, "recall": recall, "f1": f1, "support": sum(confusion[label].values())}
        f1_values.append(f1)
    bins = []
    ece = 0.0
    for index, bucket in enumerate(calibration_bins):
        count = bucket["count"]
        mean_confidence = bucket["confidence_sum"] / count if count else None
        accuracy = bucket["correct_sum"] / count if count else None
        if count:
            ece += count / len(rows) * abs(mean_confidence - accuracy)
        bins.append({"lower": index / 10, "upper": (index + 1) / 10,
                     "count": count, "mean_confidence": mean_confidence, "accuracy": accuracy})
    return {"split": rows[0]["split"], "n": len(rows), "accuracy": sum(correct) / len(rows),
            "macro_f1": sum(f1_values) / len(f1_values), "multiclass_brier": brier_sum / len(rows),
            "confusion_gold_rows_pred_columns": confusion, "per_label": per_label,
            "top_label_ece_10_bins": ece, "top_label_calibration_bins": bins,
            "max_confidence": confidences, "correct": correct}


def select_entailment_threshold(dev_rows: list[dict[str, Any]], minimum_precision: float = 0.9,
                                precision_confidence_level: float = 0.95):
    """Maximize dev recall under a Bonferroni simultaneous Wilson precision floor."""
    rows = _validated(dev_rows)
    if rows[0]["split"] != "dev":
        raise ValueError("Threshold selection must use development rows only")
    if (not _is_finite_number(minimum_precision)
            or not 0 < minimum_precision <= 1):
        raise ValueError("minimum_precision must be in (0, 1]")
    if (not _is_finite_number(precision_confidence_level)
            or not 0 < precision_confidence_level < 1):
        raise ValueError("precision_confidence_level must be in (0, 1)")
    candidates = sorted({float(row["scores"]["entailment"]) for row in rows}, reverse=True)
    candidate_count = len(candidates)
    per_threshold_confidence = 1 - (1 - precision_confidence_level) / candidate_count
    best = None
    for threshold in candidates:
        selected = [row for row in rows if row["scores"]["entailment"] >= threshold]
        if not selected:
            continue
        tp = sum(row["gold"] == "entailment" for row in selected)
        precision = tp / len(selected)
        precision_lower_bound = _wilson_lower_bound(tp, len(selected), per_threshold_confidence)
        recall_denom = sum(row["gold"] == "entailment" for row in rows)
        recall = tp / recall_denom if recall_denom else 0.0
        if precision_lower_bound >= minimum_precision:
            candidate = {"threshold": threshold, "precision": precision, "recall": recall,
                         "precision_wilson_lower_bound": precision_lower_bound,
                         "precision_confidence_level": precision_confidence_level,
                         "familywise_confidence_level": precision_confidence_level,
                         "per_threshold_confidence_level": per_threshold_confidence,
                         "threshold_candidate_count": candidate_count,
                         "multiplicity_method": "bonferroni",
                         "selected_count": len(selected), "minimum_precision": minimum_precision}
            if best is None or (candidate["recall"], candidate["threshold"]) > (best["recall"], best["threshold"]):
                best = candidate
    if best is None:
        return {"status": "no_threshold_meets_precision_floor", "minimum_precision": minimum_precision,
                "precision_confidence_level": precision_confidence_level,
                "familywise_confidence_level": precision_confidence_level,
                "per_threshold_confidence_level": per_threshold_confidence,
                "threshold_candidate_count": candidate_count,
                "multiplicity_method": "bonferroni",
                "selection_scope": "familywise Bonferroni-adjusted one-sided Wilson lower bounds over all distinct observed development entailment scores"}
    best["selection_scope"] = "familywise Bonferroni-adjusted one-sided Wilson lower bounds over all distinct observed development entailment scores"
    return {"status": "selected_on_development_data", **best}


def _entailment_gate_metrics(rows, threshold):
    selected = [row for row in rows if row["scores"]["entailment"] >= threshold]
    true_positives = sum(row["gold"] == "entailment" for row in selected)
    gold_positives = sum(row["gold"] == "entailment" for row in rows)
    return {
        "threshold": threshold,
        "selected_count": len(selected),
        "coverage": len(selected) / len(rows),
        "precision": true_positives / len(selected) if selected else None,
        "recall": true_positives / gold_positives if gold_positives else None,
        "false_positive_count": len(selected) - true_positives,
        "false_negative_count": gold_positives - true_positives,
    }


def evaluate_calibrated_splits(dev_rows: list[dict[str, Any]], test_rows: list[dict[str, Any]],
                               minimum_precision: float = 0.9,
                               precision_confidence_level: float = 0.95):
    """Select a gate on dev and evaluate once on group-disjoint test examples."""
    dev = _validated(dev_rows)
    test = _validated(test_rows)
    if dev[0]["split"] != "dev" or test[0]["split"] != "test":
        raise ValueError("Provide development rows first and test rows second")
    dev_example_ids = {row.get("example_id", row["sense_id"]) for row in dev}
    test_example_ids = {row.get("example_id", row["sense_id"]) for row in test}
    duplicate_examples = dev_example_ids & test_example_ids
    if duplicate_examples:
        raise ValueError(
            f"Development/test example_id leakage detected ({len(duplicate_examples)} overlapping IDs)"
        )
    uses_group_id = any("group_id" in row for row in dev + test)
    if uses_group_id and any("group_id" not in row for row in dev + test):
        raise ValueError("If group_id is used, it must be present on every dev and test row")
    group_field = "group_id" if uses_group_id else "sense_id"
    dev_groups = {row[group_field] for row in dev}
    test_groups = {row[group_field] for row in test}
    overlap = dev_groups & test_groups
    if overlap:
        raise ValueError(f"Development/test group leakage detected ({len(overlap)} overlapping group IDs)")
    uses_premise_hash = any("premise_sha256" in row for row in dev + test)
    if uses_premise_hash and any("premise_sha256" not in row for row in dev + test):
        raise ValueError("If premise_sha256 is used, it must be present on every dev and test row")
    if uses_premise_hash:
        dev_premises = {row["premise_sha256"].lower() for row in dev}
        test_premises = {row["premise_sha256"].lower() for row in test}
        premise_overlap = dev_premises & test_premises
        if premise_overlap:
            raise ValueError(
                f"Development/test exact-premise leakage detected ({len(premise_overlap)} overlapping premise hashes)"
            )

    selection = select_entailment_threshold(dev, minimum_precision, precision_confidence_level)
    test_metrics = _metrics(test)
    test_metrics.pop("max_confidence")
    test_metrics.pop("correct")
    if selection["status"] == "selected_on_development_data":
        test_metrics["entailment_gate"] = _entailment_gate_metrics(test, selection["threshold"])
    else:
        test_metrics["entailment_gate"] = {"status": "not_evaluated_no_dev_threshold"}
    return {
        "evaluation_version": "nli-dev-calibration-test/3",
        "development": {"n": len(dev), "threshold_selection": selection},
        "test": test_metrics,
        "grouping_policy": "group_id when supplied, otherwise sense_id; use normalized lemma-group IDs in group_id when preventing cross-sense lemma leakage; when premise_sha256 is supplied, exact premise hashes must be complete and disjoint across dev/test",
        "interpretation_limit": "Threshold and test metrics are valid only for the supplied adjudicated gold, prediction/model version, and split manifest; the tool does not establish source-rule faithfulness or proof validity.",
    }


def _read_jsonl(path: Path):
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate_calibrated_jsonl(dev_path: Path, test_path: Path,
                              minimum_precision: float = 0.9,
                              precision_confidence_level: float = 0.95):
    report = evaluate_calibrated_splits(_read_jsonl(dev_path), _read_jsonl(test_path),
                                        minimum_precision, precision_confidence_level)
    report["input_sha256"] = {"development_predictions": _sha256_file(dev_path),
                              "test_predictions": _sha256_file(test_path)}
    return report


def route_candidate(scores: dict[str, float], threshold_selection: dict[str, Any],
                    proof_certificate_valid: bool, source_semantics_reviewed: bool):
    """Never let a neural score stand in for a formal proof or source audit."""
    _validate_scores(scores)
    if not isinstance(proof_certificate_valid, bool) or not isinstance(source_semantics_reviewed, bool):
        raise ValueError("proof/source review flags must be boolean")
    if not isinstance(threshold_selection, dict):
        raise ValueError("threshold_selection must be the development calibration result")
    if threshold_selection.get("status") != "selected_on_development_data":
        return {"route": "abstain_no_calibrated_threshold", "nli_entailment_score": scores["entailment"],
                "threshold_source": "development_set", "nli_is_not_a_proof": True}
    entailment_threshold = threshold_selection.get("threshold")
    if (not _is_finite_number(entailment_threshold)
            or not 0 <= entailment_threshold <= 1):
        raise ValueError("calibration result has an invalid threshold")
    if threshold_selection.get("multiplicity_method") == "bonferroni_exact_binomial_upper_tail":
        minimum_precision = threshold_selection.get("minimum_precision")
        confidence_level = threshold_selection.get("familywise_confidence_level")
        family_alpha = threshold_selection.get("familywise_alpha")
        per_threshold_alpha = threshold_selection.get("per_threshold_alpha")
        candidate_count = threshold_selection.get("threshold_candidate_count")
        selected_count = threshold_selection.get("selected_count")
        selected_successes = threshold_selection.get("selected_successes")
        p_value = threshold_selection.get("exact_binomial_p_value")
        if (not _is_finite_number(minimum_precision) or not 0 < minimum_precision <= 1
                or not _is_finite_number(confidence_level) or not 0 < confidence_level < 1
                or not _is_finite_number(family_alpha)
                or not math.isclose(1 - confidence_level, family_alpha, rel_tol=0, abs_tol=1e-12)
                or isinstance(candidate_count, bool) or not isinstance(candidate_count, int)
                or candidate_count != len(CERTIFIED_THRESHOLD_GRID)
                or threshold_selection.get("threshold_grid") != "fixed_0.00_to_1.00_step_0.01_v1"
                or threshold_selection.get("selector_version") != CERTIFIED_SELECTOR_VERSION
                or not isinstance(threshold_selection.get("development_rows_sha256"), str)
                or not SHA256_RE.fullmatch(threshold_selection["development_rows_sha256"])
                or not any(math.isclose(entailment_threshold, item, rel_tol=0, abs_tol=1e-12)
                           for item in CERTIFIED_THRESHOLD_GRID)
                or not _is_finite_number(per_threshold_alpha)
                or not math.isclose(per_threshold_alpha, family_alpha / candidate_count,
                                    rel_tol=0, abs_tol=1e-12)
                or isinstance(selected_count, bool) or not isinstance(selected_count, int) or selected_count < 1
                or isinstance(selected_successes, bool) or not isinstance(selected_successes, int)
                or not 0 <= selected_successes <= selected_count
                or not _is_finite_number(p_value) or not 0 <= p_value <= per_threshold_alpha
                or not math.isclose(p_value,
                                    _binomial_upper_tail(selected_successes, selected_count, minimum_precision),
                                    rel_tol=1e-10, abs_tol=1e-15)
                or not _is_finite_number(threshold_selection.get("precision"))
                or not math.isclose(threshold_selection["precision"],
                                    selected_successes / selected_count, rel_tol=0, abs_tol=1e-12)):
            raise ValueError("calibration result lacks a valid exact-binomial familywise certificate")
    elif threshold_selection.get("multiplicity_method") != "bonferroni":
        raise ValueError("calibration result uses an unsupported multiplicity method")
    minimum_precision = threshold_selection.get("minimum_precision")
    precision_lower_bound = threshold_selection.get("precision_wilson_lower_bound")
    confidence_level = threshold_selection.get("familywise_confidence_level")
    legacy_confidence_level = threshold_selection.get("precision_confidence_level")
    per_threshold_confidence = threshold_selection.get("per_threshold_confidence_level")
    candidate_count = threshold_selection.get("threshold_candidate_count")
    multiplicity_method = threshold_selection.get("multiplicity_method")
    selected_count = threshold_selection.get("selected_count")
    if threshold_selection.get("multiplicity_method") == "bonferroni_exact_binomial_upper_tail":
        if scores["entailment"] < entailment_threshold:
            route = "not_supported_by_nli_threshold"
        elif not proof_certificate_valid:
            route = "abstain_missing_or_invalid_proof"
        elif not source_semantics_reviewed:
            route = "abstain_source_rule_not_semantically_audited"
        else:
            route = "candidate_supported_by_proof_nli_and_review"
        return {"route": route, "nli_entailment_score": scores["entailment"],
                "entailment_threshold": entailment_threshold, "threshold_source": "development_set",
                "nli_is_not_a_proof": True}
    expected_per_threshold_confidence = (
        1 - (1 - confidence_level) / candidate_count
        if _is_finite_number(confidence_level)
        and isinstance(candidate_count, int) and not isinstance(candidate_count, bool)
        and candidate_count > 0 else None
    )
    if (not _is_finite_number(minimum_precision) or not 0 < minimum_precision <= 1
            or not _is_finite_number(precision_lower_bound) or not 0 <= precision_lower_bound <= 1
            or not _is_finite_number(confidence_level) or not 0 < confidence_level < 1
            or not _is_finite_number(legacy_confidence_level)
            or not math.isclose(legacy_confidence_level, confidence_level, rel_tol=0, abs_tol=1e-12)
            or not _is_finite_number(per_threshold_confidence) or not 0 < per_threshold_confidence < 1
            or isinstance(candidate_count, bool) or not isinstance(candidate_count, int) or candidate_count < 1
            or expected_per_threshold_confidence is None
            or not math.isclose(per_threshold_confidence, expected_per_threshold_confidence, rel_tol=0, abs_tol=1e-12)
            or multiplicity_method != "bonferroni"
            or isinstance(selected_count, bool) or not isinstance(selected_count, int) or selected_count < 1
            or precision_lower_bound < minimum_precision):
        raise ValueError("calibration result lacks a valid development precision lower-bound criterion")
    if scores["entailment"] < entailment_threshold:
        route = "not_supported_by_nli_threshold"
    elif not proof_certificate_valid:
        route = "abstain_missing_or_invalid_proof"
    elif not source_semantics_reviewed:
        route = "abstain_source_rule_not_semantically_audited"
    else:
        route = "candidate_supported_by_proof_nli_and_review"
    return {"route": route, "nli_entailment_score": scores["entailment"],
            "entailment_threshold": entailment_threshold, "threshold_source": "development_set",
            "nli_is_not_a_proof": True}


def evaluate_jsonl(path: Path, confidence_threshold: float):
    if not _is_finite_number(confidence_threshold) or not 0 <= confidence_threshold <= 1:
        raise ValueError("confidence_threshold must be in [0, 1]")
    rows = _validated(_read_jsonl(path))
    metrics = _metrics(rows)
    calibrated = [row for row in rows if max(row["scores"].values()) >= confidence_threshold]
    metrics["selective"] = {"confidence_threshold": confidence_threshold, "coverage": len(calibrated) / len(rows),
                            "selective_accuracy": sum(max(LABELS, key=lambda label: row["scores"][label]) == row["gold"]
                                                       for row in calibrated) / len(calibrated) if calibrated else None}
    metrics.pop("max_confidence")
    metrics.pop("correct")
    metrics["input_sha256"] = _sha256_file(path)
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path,
                        nargs="?",
                        help="JSONL rows: sense_id, split=dev|test, gold, scores:{entailment,neutral,contradiction}")
    parser.add_argument("--dev-predictions", type=Path,
                        help="development JSONL used only to select the entailment gate")
    parser.add_argument("--test-predictions", type=Path,
                        help="group-disjoint test JSONL evaluated once after calibration")
    parser.add_argument("--minimum-precision", type=float, default=0.9,
                        help="required Wilson lower bound for development entailment precision")
    parser.add_argument("--precision-confidence-level", type=float, default=0.95,
                        help="familywise confidence level for Bonferroni-adjusted one-sided Wilson precision lower bounds")
    parser.add_argument("--model-id", help="identifier for the separately-run NLI model")
    parser.add_argument("--model-revision", help="immutable model revision or artifact hash")
    parser.add_argument("--confidence-threshold", type=float,
                        help="max-class confidence threshold selected on development data")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.dev_predictions or args.test_predictions:
        if args.predictions or not args.dev_predictions or not args.test_predictions:
            parser.error("provide both --dev-predictions and --test-predictions, without positional predictions")
        if bool(args.model_id) != bool(args.model_revision):
            parser.error("--model-id and --model-revision must be supplied together")
        try:
            result = evaluate_calibrated_jsonl(
                args.dev_predictions, args.test_predictions,
                args.minimum_precision, args.precision_confidence_level)
        except ValueError as exc:
            parser.error(str(exc))
        result["model"] = {"id": args.model_id, "revision": args.model_revision}
    else:
        if args.predictions is None or args.confidence_threshold is None:
            parser.error("single-split mode requires predictions and --confidence-threshold")
        if bool(args.model_id) != bool(args.model_revision):
            parser.error("--model-id and --model-revision must be supplied together")
        if not 0 <= args.confidence_threshold <= 1:
            parser.error("--confidence-threshold must be between 0 and 1")
        result = evaluate_jsonl(args.predictions, args.confidence_threshold)
        result["model"] = {"id": args.model_id, "revision": args.model_revision}
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
