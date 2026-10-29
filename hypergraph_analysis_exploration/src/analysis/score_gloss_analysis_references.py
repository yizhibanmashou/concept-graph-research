"""Score predicted gloss analyses against adjudicated, multi-reference gold.

Each prediction is compared with each complete accepted alternative as an
indivisible claim set. We select the per-item alternative with the highest
F1 (ties: higher exact-match indicator, then lexicographically smaller ID),
then aggregate its counts. The alternative union is never used as a reference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.annotation_agreement import AGREEMENT_VERSION, _claim_counter, _root_counter
from src.logic.annotation_validator import load_jsonl, validate_dataset
from src.logic.gloss_analysis_reference import (
    SCHEMA_VERSION,
    annotation_source_sense_identity,
    canonical_annotation_record_sha256,
    validate_reference_dataset,
)


SCORE_SCHEMA_VERSION = "gloss-analysis-reference-score/0.2"
SCORER_VERSION = "gloss-analysis-reference-scorer/0.5"
_SCORER_PATH = Path(__file__).resolve()
_IMPLEMENTATION_PATHS = {
    "scorer": _SCORER_PATH,
    "claim_canonicalizer": _SCORER_PATH.with_name("annotation_agreement.py"),
    "annotation_validator": _SCORER_PATH.parents[1] / "logic" / "annotation_validator.py",
    "reference_validator": _SCORER_PATH.parents[1] / "logic" / "gloss_analysis_reference.py",
}


def _selected_claim_record(record: dict[str, Any], claim_ids: list[str] | None = None) -> dict[str, Any]:
    copied = dict(record)
    analysis = dict(record["analysis"])
    claims = analysis["rule_claims"]
    if claim_ids is not None:
        wanted = set(claim_ids)
        claims = [claim for claim in claims if claim["id"] in wanted]
    analysis["rule_claims"] = claims
    copied["analysis"] = analysis
    return copied


def _counter_key(counter: Counter) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(
        (json.dumps(key, ensure_ascii=False, separators=(",", ":")), count)
        for key, count in counter.items()
    ))


def _counts(predicted: Counter, reference: Counter) -> dict[str, Any]:
    predicted_count = sum(predicted.values())
    reference_count = sum(reference.values())
    true_positive = sum((predicted & reference).values())
    if predicted_count == 0 and reference_count == 0:
        precision = recall = f1 = None
    else:
        precision = true_positive / predicted_count if predicted_count else 0.0
        recall = true_positive / reference_count if reference_count else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    exact = predicted == reference
    return {
        "true_positive": true_positive,
        "predicted_count": predicted_count,
        "reference_count": reference_count,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match": exact,
    }


def _micro_from_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(row["true_positive"] for row in rows)
    predicted_count = sum(row["predicted_count"] for row in rows)
    reference_count = sum(row["reference_count"] for row in rows)
    if predicted_count == 0 and reference_count == 0:
        precision = recall = f1 = None
    else:
        precision = tp / predicted_count if predicted_count else 0.0
        recall = tp / reference_count if reference_count else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    n = len(rows)
    return {
        "items": n,
        "true_positive": tp,
        "predicted_count": predicted_count,
        "reference_count": reference_count,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match_rate": sum(row["exact_match"] for row in rows) / n if n else None,
        "claim_exact_match_rate": sum(row["claim_exact_match"] for row in rows) / n if n else None,
        "root_structure_exact_match_rate": sum(row["root_structure_exact_match"] for row in rows) / n if n else None,
        "analysis_status_match_rate": sum(row["analysis_status_match"] for row in rows) / n if n else None,
    }


def _macro_from_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    claim_rows = [row for row in rows if row["f1"] is not None]
    n = len(claim_rows)
    return {
        "items": len(rows),
        "items_with_nonempty_claim_comparison": n,
        "empty_claim_pair_items_excluded_from_macro": len(rows) - n,
        "precision": sum(row["precision"] for row in claim_rows) / n if n else None,
        "recall": sum(row["recall"] for row in claim_rows) / n if n else None,
        "f1": sum(row["f1"] for row in claim_rows) / n if n else None,
    }


def score_reference_sets(
    references: list[dict[str, Any]],
    adjudicated_records: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
) -> dict[str, Any]:
    errors = validate_reference_dataset(references, adjudicated_records)
    errors.extend(validate_dataset(predictions))
    if errors:
        raise ValueError("input validation failed: " + "; ".join(errors[:12]))

    adjudicated_by_hash = {
        canonical_annotation_record_sha256(record): record for record in adjudicated_records
    }
    references_by_item = {reference["item_id"]: reference for reference in references}
    predictions_by_item: dict[str, dict[str, Any]] = {}
    for record in predictions:
        item_id = record["item_id"]
        if item_id in predictions_by_item:
            raise ValueError(f"more than one prediction record for item_id {item_id!r}")
        predictions_by_item[item_id] = record
    if set(predictions_by_item) != set(references_by_item):
        missing = sorted(set(references_by_item) - set(predictions_by_item))
        extra = sorted(set(predictions_by_item) - set(references_by_item))
        raise ValueError(f"prediction item set mismatch; missing={missing[:5]}, extra={extra[:5]}")

    scored_rows: list[dict[str, Any]] = []
    single_reference_rows: list[dict[str, Any]] = []
    unresolved_items = 0
    alternative_counts: Counter[str] = Counter()
    per_item: list[dict[str, Any]] = []

    for item_id in sorted(references_by_item):
        reference = references_by_item[item_id]
        prediction = predictions_by_item[item_id]
        if prediction["source"]["input_sha256"] != reference["source_gloss_sha256"]:
            raise ValueError(f"prediction gloss hash mismatch for item_id {item_id!r}")
        linked_records = [
            adjudicated_by_hash[entry["annotation_record_sha256"]]
            for entry in reference["accepted_alternatives"] + reference["unresolved_candidates"]
        ]
        if not linked_records:
            raise ValueError(f"reference has no linked annotation records for item_id {item_id!r}")
        if annotation_source_sense_identity(prediction) != annotation_source_sense_identity(linked_records[0]):
            raise ValueError(f"prediction source/sense identity mismatch for item_id {item_id!r}")
        linked_splits = {record["split"] for record in linked_records}
        if len(linked_splits) != 1 or prediction["split"] not in linked_splits:
            raise ValueError(f"prediction split mismatch for item_id {item_id!r}")
        alternatives = reference["accepted_alternatives"]
        alternative_counts[str(len(alternatives))] += 1
        if reference["adjudication_status"] == "unresolved":
            unresolved_items += 1
            per_item.append({"item_id": item_id, "status": "unresolved", "scored": False})
            continue

        predicted_record = _selected_claim_record(prediction)
        predicted_counter = _claim_counter(predicted_record, include_evidence=False)
        candidate_rows: list[tuple[dict[str, Any], Counter, dict[str, Any]]] = []
        seen_semantic_sets: set[tuple[Any, ...]] = set()
        for alternative in alternatives:
            record = adjudicated_by_hash[alternative["annotation_record_sha256"]]
            selected = _selected_claim_record(record, alternative["rule_claim_ids"])
            reference_counter = _claim_counter(selected, include_evidence=False)
            semantic_set_key = (
                alternative["analysis_status"],
                _counter_key(reference_counter),
                _counter_key(_root_counter(record)),
            )
            if semantic_set_key in seen_semantic_sets:
                raise ValueError(
                    f"duplicate semantic reference alternatives for item_id {item_id!r}; "
                    "differences in evidence spans belong in a separate evidence metric"
                )
            seen_semantic_sets.add(semantic_set_key)
            metrics = _counts(predicted_counter, reference_counter)
            roots_match = _root_counter(prediction) == _root_counter(record)
            status_match = prediction["analysis"]["status"] == alternative["analysis_status"]
            metrics.update({
                "claim_exact_match": metrics["exact_match"],
                "root_structure_exact_match": roots_match,
                "analysis_status_match": status_match,
                "exact_match": metrics["exact_match"] and roots_match and status_match,
            })
            candidate_rows.append((alternative, reference_counter, metrics))
        if not candidate_rows:
            raise ValueError(f"complete sidecar has no accepted alternatives for item_id {item_id!r}")

        # Root structure and status are part of whole-analysis exact match, even
        # though rule-claim F1 remains the primary per-alternative selection key.
        best = min(
            candidate_rows,
            key=lambda row: (
                -(row[2]["f1"] if row[2]["f1"] is not None else (1.0 if row[2]["exact_match"] else 0.0)),
                -int(row[2]["exact_match"]),
                row[0]["alternative_id"],
            ),
        )
        alternative, _, metrics = best
        row = {key: metrics[key] for key in (
            "true_positive", "predicted_count", "reference_count", "precision", "recall", "f1",
            "exact_match", "claim_exact_match", "root_structure_exact_match", "analysis_status_match",
        )}
        scored_rows.append(row)
        if len(alternatives) == 1:
            single_reference_rows.append(row)
        per_item.append({
            "item_id": item_id,
            "status": "complete",
            "scored": True,
            "accepted_alternative_count": len(alternatives),
            "selected_alternative_id": alternative["alternative_id"],
            **metrics,
        })

    result = {
        "schema_version": SCORE_SCHEMA_VERSION,
        "scorer_version": SCORER_VERSION,
        "reference_schema_version": SCHEMA_VERSION,
        "claim_signature_version": AGREEMENT_VERSION,
        "aggregation": (
            "For each complete item, select the whole accepted alternative with the highest rule-claim set F1; ties prefer "
            "whole-analysis exact match (claim set, canonical root structure, and analysis status), "
            "then lexicographically smaller alternative_id. Aggregate selected TP/predicted/reference counts. "
            "No union of accepted alternatives is formed. Empty/empty sets count as exact match; they contribute no micro counts. "
            "Exact-match rates use complete-adjudication items only; unresolved items are excluded and reported separately."
        ),
        "items": len(references),
        "scored_items": len(scored_rows),
        "unresolved_items": unresolved_items,
        "unresolved_rate": unresolved_items / len(references) if references else None,
        "accepted_alternative_count_distribution": dict(sorted(alternative_counts.items(), key=lambda item: int(item[0]))),
        "alternative_aware_micro": _micro_from_rows(scored_rows),
        "alternative_aware_macro": _macro_from_rows(scored_rows),
        "single_reference_only_micro": _micro_from_rows(single_reference_rows),
        "single_reference_only_macro": _macro_from_rows(single_reference_rows),
        "per_item": per_item,
        "interpretation_limit": (
            "Scores are relative to the adjudicated reference sets supplied to this command, not to every valid analysis "
            "a gloss could admit. Formula/support fidelity and source-span quality require separate metrics."
        ),
    }
    result["implementation_sha256"] = {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in _IMPLEMENTATION_PATHS.items()
    }
    result["runtime"] = {
        "python_implementation": sys.implementation.name,
        "python_version": sys.version,
        "sys_platform": sys.platform,
    }
    return result


def _load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records, _, errors = load_jsonl(path)
    if errors:
        raise ValueError(f"invalid JSONL in {path}: " + "; ".join(errors[:5]))
    return records, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("references", type=Path, help=f"{SCHEMA_VERSION} JSONL")
    parser.add_argument("adjudicated_records", type=Path, help="annotation JSONL records linked by canonical record hash")
    parser.add_argument("predictions", type=Path, help="one predicted annotation record per sidecar item")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        references, _ = _load_jsonl(args.references)
        adjudicated_records, _ = _load_jsonl(args.adjudicated_records)
        predictions, _ = _load_jsonl(args.predictions)
        result = score_reference_sets(references, adjudicated_records, predictions)
        result["input_sha256"] = {
            "references": hashlib.sha256(args.references.read_bytes()).hexdigest(),
            "adjudicated_records": hashlib.sha256(args.adjudicated_records.read_bytes()).hexdigest(),
            "predictions": hashlib.sha256(args.predictions.read_bytes()).hexdigest(),
        }
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {result['schema_version']} for {result['scored_items']} scored / {result['unresolved_items']} unresolved items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
