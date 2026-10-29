"""Join adjudicated claim-review labels to model scores for nli_gate."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

from src.logic.claim_review_validator import (
    load_jsonl,
    validate_against_candidate_manifest,
    validate_dataset,
)


LABELS = ("entailment", "neutral", "contradiction")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _valid_scores(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != set(LABELS):
        return False
    for score in value.values():
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            return False
        try:
            if not math.isfinite(float(score)) or not 0 <= score <= 1:
                return False
        except (OverflowError, ValueError):
            return False
    try:
        return abs(sum(value.values()) - 1.0) <= 1e-6
    except OverflowError:
        return False


def export(sidecar_path: Path, predictions_path: Path, output_dir: Path,
           model_id: str, model_revision: str, candidate_manifest_path: Path,
           expected_candidate_manifest_sha256: str) -> dict[str, Any]:
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("model_id must be a non-empty string")
    if not isinstance(model_revision, str) or not model_revision.strip():
        raise ValueError("model_revision must be a non-empty immutable revision or artifact hash")
    sidecar, sidecar_lines, errors = load_jsonl(sidecar_path)
    errors.extend(validate_dataset(sidecar, sidecar_lines))
    manifest_bytes = candidate_manifest_path.read_bytes()
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    if manifest_sha256 != expected_candidate_manifest_sha256:
        errors.append("candidate manifest SHA-256 does not match the externally pinned value")
    try:
        candidate_manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid candidate manifest JSON: {exc}") from exc
    errors.extend(validate_against_candidate_manifest(sidecar, candidate_manifest))
    if errors:
        raise ValueError("invalid claim-review sidecar:\n" + "\n".join(errors))
    manifest_by_id = {
        row["candidate_id"]: row
        for row in candidate_manifest["candidates"]
        if isinstance(row, dict) and isinstance(row.get("candidate_id"), str)
    }

    eligible = [row for row in sidecar if row["split"] in {"dev", "test"}]
    if not eligible:
        raise ValueError("sidecar contains no dev/test candidates")
    unresolved = [row["candidate_id"] for row in eligible
                  if row["nli_relation_status"] != "adjudicated"
                  or row["annotation"]["adjudication_status"] != "adjudicated"]
    if unresolved:
        raise ValueError(
            f"all dev/test candidates must have adjudicated NLI labels and final adjudication; "
            f"unresolved count={len(unresolved)} (examples: {unresolved[:5]})"
        )
    dev_groups = [row["group_id"] for row in eligible if row["split"] == "dev"]
    if len(dev_groups) != len(set(dev_groups)):
        raise ValueError("certified dev calibration requires exactly one candidate per group_id")

    score_rows, score_lines, score_errors = load_jsonl(predictions_path)
    if score_errors:
        raise ValueError("invalid prediction JSONL:\n" + "\n".join(score_errors))
    expected = {row["candidate_id"]: row for row in eligible}
    scores_by_id: dict[str, dict[str, Any]] = {}
    for line, prediction in zip(score_lines, score_rows):
        if not isinstance(prediction, dict):
            raise ValueError(f"prediction line {line}: expected a JSON object")
        candidate_id = prediction.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            raise ValueError(f"prediction line {line}: candidate_id must be a non-empty string")
        if candidate_id in scores_by_id:
            raise ValueError(f"prediction line {line}: duplicate candidate_id {candidate_id!r}")
        if candidate_id not in expected:
            raise ValueError(f"prediction line {line}: candidate_id {candidate_id!r} is not a dev/test sidecar row")
        sidecar_row = expected[candidate_id]
        for field in ("premise_sha256", "hypothesis_sha256"):
            if prediction.get(field) != sidecar_row[field]:
                raise ValueError(f"prediction line {line}: {field} mismatch for {candidate_id!r}")
        if not _valid_scores(prediction.get("scores")):
            raise ValueError(f"prediction line {line}: scores must be finite three-class probabilities summing to 1")
        scores_by_id[candidate_id] = prediction

    missing = sorted(set(expected) - set(scores_by_id))
    if missing:
        raise ValueError(f"missing model scores for {len(missing)} dev/test candidates (examples: {missing[:5]})")

    exported: dict[str, list[dict[str, Any]]] = {"dev": [], "test": []}
    for row in eligible:
        candidate_id = row["candidate_id"]
        exported_row = {
            "sense_id": row["source"]["sense_id"],
            "split": row["split"],
            "gold": row["nli_relation_gold"],
            "scores": scores_by_id[candidate_id]["scores"],
            "example_id": candidate_id,
            "group_id": row["group_id"],
            "claim_id": candidate_id,
            "premise_sha256": row["premise_sha256"],
            "hypothesis_sha256": row["hypothesis_sha256"],
            "model_id": model_id,
            "model_revision": model_revision,
        }
        composition = manifest_by_id[candidate_id].get("composition")
        if composition is not None:
            exported_row["composition"] = composition
        exported[row["split"]].append(exported_row)
    for split in ("dev", "test"):
        if not exported[split]:
            raise ValueError(f"no {split} rows available for calibrated evaluation")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_hashes = {}
    for split in ("dev", "test"):
        output = "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n"
                         for row in exported[split])
        output_path = output_dir / f"{split}_predictions.jsonl"
        output_path.write_text(output, encoding="utf-8")
        output_hashes[split] = _sha256_file(output_path)
    manifest = {
        "schema_version": "claim-review-nli-export/0.2",
        "model": {"id": model_id, "revision": model_revision},
        "sidecar_sha256": _sha256_file(sidecar_path),
        "candidate_manifest_sha256": manifest_sha256,
        "model_scores_sha256": _sha256_file(predictions_path),
        "outputs": {split: {"path": f"{split}_predictions.jsonl", "rows": len(exported[split]),
                            "sha256": output_hashes[split]}
                    for split in ("dev", "test")},
        "exported_gold_source": "adjudicated nli_relation_gold only",
        "semantic_support_used_as_nli_gold": False,
    }
    (output_dir / "export_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sidecar", type=Path, help="validated claim-review JSONL")
    parser.add_argument("predictions", type=Path, help="model scores JSONL keyed by candidate_id")
    parser.add_argument("output_dir", type=Path, help="directory for nli_gate dev/test JSONL and export manifest")
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--model-revision", required=True, help="immutable revision or artifact hash")
    parser.add_argument("--candidate-manifest", type=Path, required=True,
                        help="frozen text-free candidate manifest")
    parser.add_argument("--candidate-manifest-sha256", required=True,
                        help="manifest file SHA-256 independently recorded in the external lock")
    args = parser.parse_args(argv)
    try:
        manifest = export(args.sidecar, args.predictions, args.output_dir,
                          args.model_id, args.model_revision,
                          args.candidate_manifest, args.candidate_manifest_sha256)
    except (OSError, ValueError) as exc:
        print(f"claim-review NLI export failed: {exc}", file=sys.stderr)
        return 1
    manifest_path = args.output_dir / "export_manifest.json"
    print(json.dumps({**manifest, "export_manifest_sha256": _sha256_file(manifest_path)},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
