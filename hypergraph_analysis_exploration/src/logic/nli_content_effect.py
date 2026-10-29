"""Diagnostic metrics for blinded NLI content-effect sidecars.

This module is intentionally separate from nli_gate and the verified proof
router. It reports descriptive diagnostics only: no threshold selection,
confidence intervals, or route decisions are produced here.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from statistics import mean, median
from typing import Any


LABELS = ("entailment", "neutral", "contradiction")
SUPPORT_LABELS = {"supported", "not_supported", "uncertain"}
PLAUSIBILITY_LABELS = {"plausible", "implausible", "uncertain"}
CONDITIONS = {"plausibility_stratum", "matched_plausibility_pair", "irrelevant_context_pair"}
CONDITION_VALUES = {"plausible", "implausible", "uncertain", "source_only", "irrelevant_context"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha256(value: Any, field: str, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 64-character SHA-256")


def _same_pair_identity(pair: list[dict[str, Any]], fields: tuple[str, ...], group_id: str) -> None:
    for field in fields:
        if len({row[field] for row in pair}) != 1:
            raise ValueError(f"contrast group {group_id!r} has mismatched {field}")


def validate_content_effect_sidecar(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate sidecar rows and pair contracts; return the input rows unchanged."""
    if not isinstance(rows, list) or not rows:
        raise ValueError("sidecar must be a non-empty list")

    seen_ids: set[str] = set()
    splits_by_group: dict[str, set[str]] = defaultdict(set)
    splits_by_identity: dict[tuple[str, str], set[str]] = defaultdict(set)
    contrast_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    required = (
        "example_id", "contrast_group_id", "split", "diagnostic_condition",
        "condition_value", "source_sense_id", "claim_id", "gloss_sha256",
        "hypothesis_sha256", "model_premise_sha256", "context_sha256",
        "gold_support_label", "nli_gold_relation", "claim_plausibility",
        "review_status", "group_id",
    )

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"row {index} must be an object")
        if {"gloss", "premise", "hypothesis", "context"} & row.keys():
            raise ValueError(f"row {index} must not contain source or model-input text")
        missing = [field for field in required if field not in row]
        if missing:
            raise ValueError(f"row {index} is missing required fields: {missing}")
        for field in ("example_id", "source_sense_id", "claim_id", "group_id"):
            if not _nonempty(row[field]):
                raise ValueError(f"row {index} {field} must be a non-empty string")
        if row["example_id"] in seen_ids:
            raise ValueError(f"duplicate example_id {row['example_id']!r}")
        seen_ids.add(row["example_id"])
        if not isinstance(row["split"], str) or row["split"] not in {"dev", "test"}:
            raise ValueError(f"row {index} split must be dev or test")
        if not isinstance(row["diagnostic_condition"], str) or row["diagnostic_condition"] not in CONDITIONS:
            raise ValueError(f"row {index} has an unsupported diagnostic_condition")
        if not isinstance(row["condition_value"], str) or row["condition_value"] not in CONDITION_VALUES:
            raise ValueError(f"row {index} has an unsupported condition_value")
        if row["diagnostic_condition"] in {"plausibility_stratum", "matched_plausibility_pair"}:
            if row["condition_value"] not in PLAUSIBILITY_LABELS:
                raise ValueError(f"row {index} plausibility condition requires a plausibility value")
            if row["claim_plausibility"] != row["condition_value"]:
                raise ValueError(f"row {index} condition_value must match claim_plausibility")
        else:
            if row["condition_value"] not in {"source_only", "irrelevant_context"}:
                raise ValueError(f"row {index} context condition requires source_only or irrelevant_context")
            if row["claim_plausibility"] not in PLAUSIBILITY_LABELS:
                raise ValueError(f"row {index} has an invalid claim_plausibility")
        if row["claim_plausibility"] not in PLAUSIBILITY_LABELS:
            raise ValueError(f"row {index} has an invalid claim_plausibility")
        if not isinstance(row["review_status"], str) or row["review_status"] not in {"adjudicated", "unassessed"}:
            raise ValueError(f"row {index} review_status must be adjudicated or unassessed")
        if row["review_status"] == "adjudicated":
            if not isinstance(row["gold_support_label"], str) or row["gold_support_label"] not in SUPPORT_LABELS:
                raise ValueError(f"row {index} has an invalid gold_support_label")
            if not isinstance(row["nli_gold_relation"], str) or row["nli_gold_relation"] not in LABELS:
                raise ValueError(f"row {index} has an invalid nli_gold_relation")
        elif row["gold_support_label"] is not None or row["nli_gold_relation"] is not None:
            raise ValueError(f"row {index} unassessed rows must have null gold labels")

        for field in ("gloss_sha256", "hypothesis_sha256", "model_premise_sha256"):
            _sha256(row[field], f"row {index} {field}")
        _sha256(row["context_sha256"], f"row {index} context_sha256", optional=True)
        if row["diagnostic_condition"] == "irrelevant_context_pair":
            if row["condition_value"] == "source_only" and row["context_sha256"] is not None:
                raise ValueError(f"row {index} source_only condition must not have a context hash")
            if row["condition_value"] == "irrelevant_context" and row["context_sha256"] is None:
                raise ValueError(f"row {index} irrelevant_context condition requires a context hash")
        elif row["context_sha256"] is not None:
            raise ValueError(f"row {index} non-context diagnostic must not have a context hash")
        if row["diagnostic_condition"] == "irrelevant_context_pair" and row["condition_value"] == "source_only":
            if row["model_premise_sha256"] != row["gloss_sha256"]:
                raise ValueError(f"row {index} source_only premise hash must equal gloss hash")

        splits_by_group[row["group_id"]].add(row["split"])
        for field in (
            "source_sense_id", "claim_id", "gloss_sha256", "hypothesis_sha256",
            "model_premise_sha256", "context_sha256",
        ):
            identity = row[field]
            if identity is not None:
                splits_by_identity[(field, identity)].add(row["split"])
        contrast_id = row["contrast_group_id"]
        if contrast_id is not None:
            if not _nonempty(contrast_id):
                raise ValueError(f"row {index} contrast_group_id must be non-empty or null")
            contrast_groups[(row["diagnostic_condition"], contrast_id)].append(row)
        elif row["diagnostic_condition"] != "plausibility_stratum":
            raise ValueError(f"row {index} paired diagnostic requires contrast_group_id")

    leaked_groups = sorted(group for group, splits in splits_by_group.items() if len(splits) > 1)
    if leaked_groups:
        raise ValueError(f"group_id leakage across dev/test: {leaked_groups[:3]}")

    leaked_identity_fields = sorted({
        field for (field, _), splits in splits_by_identity.items() if len(splits) > 1
    })
    if leaked_identity_fields:
        raise ValueError(
            "source/claim/input identity leakage across dev/test for fields: "
            f"{leaked_identity_fields}"
        )

    for (condition, contrast_id), pair in contrast_groups.items():
        if len(pair) != 2:
            raise ValueError(f"contrast group {contrast_id!r} must contain exactly two rows")
        if pair[0]["split"] != pair[1]["split"] or pair[0]["group_id"] != pair[1]["group_id"]:
            raise ValueError(f"contrast group {contrast_id!r} crosses split/group boundary")
        if any(row["review_status"] != "adjudicated" for row in pair):
            raise ValueError(f"contrast group {contrast_id!r} must be fully adjudicated")
        if condition == "matched_plausibility_pair":
            if {row["condition_value"] for row in pair} != {"plausible", "implausible"}:
                raise ValueError(f"contrast group {contrast_id!r} must pair plausible and implausible")
            _same_pair_identity(pair, ("gold_support_label", "nli_gold_relation"), contrast_id)
            if pair[0]["gold_support_label"] == "uncertain":
                raise ValueError(f"contrast group {contrast_id!r} cannot use uncertain support labels")
        elif condition == "irrelevant_context_pair":
            if {row["condition_value"] for row in pair} != {"source_only", "irrelevant_context"}:
                raise ValueError(f"contrast group {contrast_id!r} must pair source_only and irrelevant_context")
            _same_pair_identity(pair, (
                "source_sense_id", "claim_id", "gloss_sha256", "hypothesis_sha256",
                "gold_support_label", "nli_gold_relation", "claim_plausibility",
            ), contrast_id)
            if pair[0]["gold_support_label"] == "uncertain":
                raise ValueError(f"contrast group {contrast_id!r} cannot use uncertain support labels")
            source_row = next(row for row in pair if row["condition_value"] == "source_only")
            context_row = next(row for row in pair if row["condition_value"] == "irrelevant_context")
            if source_row["model_premise_sha256"] == context_row["model_premise_sha256"]:
                raise ValueError(f"contrast group {contrast_id!r} must hash distinct model premise inputs")
    return rows


def _validate_predictions(predictions: list[dict[str, Any]], sidecar_ids: set[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(predictions, list):
        raise ValueError("predictions must be a list")
    by_id: dict[str, dict[str, Any]] = {}
    model_identities: set[tuple[str, str]] = set()
    for index, row in enumerate(predictions):
        if not isinstance(row, dict) or not _nonempty(row.get("example_id")):
            raise ValueError(f"prediction row {index} requires example_id")
        example_id = row["example_id"]
        if example_id in by_id:
            raise ValueError(f"duplicate prediction example_id {example_id!r}")
        scores = row.get("scores")
        if not isinstance(scores, dict) or set(scores) != set(LABELS):
            raise ValueError(f"prediction row {index} scores must contain exactly {LABELS}")
        values = []
        for label in LABELS:
            value = scores[label]
            try:
                valid_probability = (not isinstance(value, bool) and isinstance(value, (int, float))
                                     and math.isfinite(float(value)) and 0 <= value <= 1)
            except (OverflowError, ValueError):
                valid_probability = False
            if not valid_probability:
                raise ValueError(f"prediction row {index} scores must be finite probabilities")
            values.append(float(value))
        if abs(sum(values) - 1) > 1e-6:
            raise ValueError(f"prediction row {index} scores must sum to 1")
        if "split" not in row or row["split"] not in {"dev", "test"}:
            raise ValueError(f"prediction row {index} split must be dev or test")
        if not _nonempty(row.get("model_id")) or not _nonempty(row.get("model_revision")):
            raise ValueError(f"prediction row {index} requires model_id and immutable model_revision")
        model_identities.add((row["model_id"], row["model_revision"]))
        by_id[example_id] = row
    if len(model_identities) > 1:
        raise ValueError("prediction rows must use one fixed model_id/model_revision")
    if set(by_id) != sidecar_ids:
        raise ValueError("prediction example IDs must exactly match diagnostic sidecar IDs")
    return by_id


def _predicted_label(scores: dict[str, float]) -> str:
    return max(LABELS, key=lambda label: scores[label])


def _cell_metrics(rows: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    reviewed = [row for row in rows if row["review_status"] == "adjudicated"]
    scores = [predictions[row["example_id"]]["scores"] for row in reviewed]
    gold_supported = [row for row in reviewed if row["gold_support_label"] == "supported"]
    gold_unsupported = [row for row in reviewed if row["gold_support_label"] == "not_supported"]
    classified = [row for row in reviewed if row["nli_gold_relation"] in LABELS]
    confusion = {gold: {pred: 0 for pred in LABELS} for gold in LABELS}
    for row in classified:
        prediction = _predicted_label(predictions[row["example_id"]]["scores"])
        confusion[row["nli_gold_relation"]][prediction] += 1
    return {
        "n_rows": len(rows),
        "n_adjudicated": len(reviewed),
        "n_unassessed": len(rows) - len(reviewed),
        "mean_entailment_score": mean([predictions[row["example_id"]]["scores"]["entailment"] for row in reviewed]) if reviewed else None,
        "nli_three_way_accuracy": mean([
            _predicted_label(predictions[row["example_id"]]["scores"]) == row["nli_gold_relation"]
            for row in classified
        ]) if classified else None,
        "nli_three_way_confusion_gold_rows_pred_columns": confusion,
        "support_false_negative_rate": mean([
            _predicted_label(predictions[row["example_id"]]["scores"]) != "entailment"
            for row in gold_supported
        ]) if gold_supported else None,
        "unsupported_false_positive_rate": mean([
            _predicted_label(predictions[row["example_id"]]["scores"]) == "entailment"
            for row in gold_unsupported
        ]) if gold_unsupported else None,
    }


def _paired_result(pairs: list[tuple[dict[str, Any], dict[str, Any]]], predictions: dict[str, dict[str, Any]],
                   left_value: str, right_value: str) -> dict[str, Any]:
    score_deltas = []
    flips = 0
    left_correct = []
    right_correct = []
    for left, right in pairs:
        left_scores = predictions[left["example_id"]]["scores"]
        right_scores = predictions[right["example_id"]]["scores"]
        score_deltas.append(right_scores["entailment"] - left_scores["entailment"])
        left_pred = _predicted_label(left_scores)
        right_pred = _predicted_label(right_scores)
        flips += left_pred != right_pred
        left_correct.append(left_pred == left["nli_gold_relation"])
        right_correct.append(right_pred == right["nli_gold_relation"])
    return {
        "left_condition": left_value,
        "right_condition": right_value,
        "n_pairs": len(pairs),
        "mean_entailment_score_delta_right_minus_left": mean(score_deltas) if pairs else None,
        "median_entailment_score_delta_right_minus_left": median(score_deltas) if pairs else None,
        "prediction_flip_rate": flips / len(pairs) if pairs else None,
        "left_three_way_accuracy": mean(left_correct) if pairs else None,
        "right_three_way_accuracy": mean(right_correct) if pairs else None,
        "accuracy_delta_right_minus_left": (mean(right_correct) - mean(left_correct)) if pairs else None,
    }


def evaluate_content_effect(sidecar_rows: list[dict[str, Any]], prediction_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Return per-split descriptive strata and paired diagnostics, without inference."""
    validate_content_effect_sidecar(sidecar_rows)
    predictions = _validate_predictions(prediction_rows, {row["example_id"] for row in sidecar_rows})
    for row in sidecar_rows:
        if predictions[row["example_id"]]["split"] != row["split"]:
            raise ValueError(f"prediction split mismatch for {row['example_id']!r}")

    report: dict[str, Any] = {
        "evaluation_version": "nli-content-effect-diagnostic/0.2",
        "diagnostic_only": True,
        "threshold_selection_performed": False,
        "proof_route_eligible": False,
        "inference_performed": False,
        "model_identity": {
            "model_id": prediction_rows[0]["model_id"],
            "model_revision": prediction_rows[0]["model_revision"],
        },
        "interpretation_limit": "Descriptive metrics relative to supplied adjudicated labels; no causal claim, interval, calibration, or proof decision is produced.",
        "splits": {},
    }
    by_split: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sidecar_rows:
        by_split[row["split"]].append(row)

    for split, rows in sorted(by_split.items()):
        reviewed = [row for row in rows if row["review_status"] == "adjudicated"]
        plausibility_reviewed = [
            row for row in reviewed if row["diagnostic_condition"] == "plausibility_stratum"
        ]
        cells: dict[str, Any] = {}
        for support_label in ("supported", "not_supported", "uncertain"):
            for plausibility in ("plausible", "implausible", "uncertain"):
                cell = [row for row in plausibility_reviewed if row["gold_support_label"] == support_label
                        and row["claim_plausibility"] == plausibility]
                if cell:
                    cells[f"{support_label}|{plausibility}"] = _cell_metrics(cell, predictions)

        unsupported_relation_slices: dict[str, Any] = {}
        unsupported_rows = [row for row in plausibility_reviewed if row["gold_support_label"] == "not_supported"]
        for relation in LABELS:
            relation_cells = {}
            for plausibility in ("plausible", "implausible", "uncertain"):
                cell = [row for row in unsupported_rows
                        if row["nli_gold_relation"] == relation
                        and row["claim_plausibility"] == plausibility]
                if cell:
                    relation_cells[plausibility] = _cell_metrics(cell, predictions)
            if relation_cells:
                unsupported_relation_slices[relation] = relation_cells

        gaps = {}
        supported_plausible = [row for row in plausibility_reviewed if row["gold_support_label"] == "supported"
                               and row["claim_plausibility"] == "plausible"]
        supported_implausible = [row for row in plausibility_reviewed if row["gold_support_label"] == "supported"
                                 and row["claim_plausibility"] == "implausible"]
        fnr_p = (_cell_metrics(supported_plausible, predictions)["support_false_negative_rate"]
                 if supported_plausible else None)
        fnr_i = (_cell_metrics(supported_implausible, predictions)["support_false_negative_rate"]
                 if supported_implausible else None)
        gaps["CE_supported_fnr_implausible_minus_plausible"] = (
            fnr_i - fnr_p if fnr_i is not None and fnr_p is not None else None
        )

        def unsupported_fpr_gap(relations: set[str]) -> float | None:
            plausible = [row for row in unsupported_rows
                         if row["nli_gold_relation"] in relations
                         and row["claim_plausibility"] == "plausible"]
            implausible = [row for row in unsupported_rows
                           if row["nli_gold_relation"] in relations
                           and row["claim_plausibility"] == "implausible"]
            fpr_p = (_cell_metrics(plausible, predictions)["unsupported_false_positive_rate"]
                     if plausible else None)
            fpr_i = (_cell_metrics(implausible, predictions)["unsupported_false_positive_rate"]
                     if implausible else None)
            return fpr_p - fpr_i if fpr_p is not None and fpr_i is not None else None

        gaps["CE_neutral_not_supported_fpr_plausible_minus_implausible"] = unsupported_fpr_gap({"neutral"})
        gaps["CE_contradiction_not_supported_fpr_plausible_minus_implausible"] = unsupported_fpr_gap(
            {"contradiction"}
        )
        gaps["CE_non_entailment_not_supported_fpr_plausible_minus_implausible"] = unsupported_fpr_gap(
            {"neutral", "contradiction"}
        )
        # Retain the legacy field name as an alias for the combined auxiliary gap.
        gaps["CE_not_supported_fpr_plausible_minus_implausible"] = gaps[
            "CE_non_entailment_not_supported_fpr_plausible_minus_implausible"
        ]

        paired: dict[str, Any] = {}
        for condition in ("matched_plausibility_pair", "irrelevant_context_pair"):
            groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in rows:
                if row["diagnostic_condition"] == condition and row["contrast_group_id"] is not None:
                    groups[row["contrast_group_id"]].append(row)
            left_value, right_value = (("plausible", "implausible") if condition == "matched_plausibility_pair"
                                       else ("source_only", "irrelevant_context"))
            pairs = []
            for pair in groups.values():
                left = next(row for row in pair if row["condition_value"] == left_value)
                right = next(row for row in pair if row["condition_value"] == right_value)
                pairs.append((left, right))
            if condition == "matched_plausibility_pair":
                support_results = {}
                for support_label in ("supported", "not_supported"):
                    selected = [pair for pair in pairs if pair[0]["gold_support_label"] == support_label]
                    support_results[support_label] = _paired_result(selected, predictions, left_value, right_value)
                paired[condition] = support_results
            else:
                paired[condition] = _paired_result(pairs, predictions, left_value, right_value)
        report["splits"][split] = {
            "n_rows": len(rows),
            "n_adjudicated": len(reviewed),
            "n_unassessed": len(rows) - len(reviewed),
            "plausibility_strata": cells,
            "not_supported_nli_relation_slices": unsupported_relation_slices,
            "descriptive_content_effect_gaps": gaps,
            "paired_diagnostics": paired,
        }
    return report
