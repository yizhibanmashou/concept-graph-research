"""Inventory output artifacts for release review without copying their values."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from src.analysis.project_paths import PROJECT_ROOT


DEFAULT_OUTPUT = Path("outputs/phase18/output_release_surface_audit.json")
AUDIT_RELATIVE_PATH = DEFAULT_OUTPUT.as_posix()
TEXT_RISK_KEYS = {
    "definition", "effective_definition", "example", "examples", "gloss",
    "lemma", "lemmas", "notes", "raw_definition", "raw_gloss", "text",
}
IDENTITY_RISK_KEYS = {
    "basis_id", "head", "identity", "literal_id", "sense_id", "source_path",
    "synset_id", "task_id",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                found.add(key.casefold())
            found.update(_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_keys(child))
    return found


def _json_field_keys(path: Path) -> tuple[set[str], bool]:
    """Return field names only; never return or log JSON values."""
    try:
        if path.suffix.casefold() == ".json":
            return _keys(json.loads(path.read_text(encoding="utf-8"))), True
        if path.suffix.casefold() == ".jsonl":
            found: set[str] = set()
            with path.open("r", encoding="utf-8") as stream:
                for line in stream:
                    if line.strip():
                        found.update(_keys(json.loads(line)))
            return found, True
    except (OSError, UnicodeError, json.JSONDecodeError):
        return set(), False
    return set(), False


def _ignored_by_git(project_root: Path, relative_path: str) -> bool | None:
    try:
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", "--", relative_path],
            cwd=project_root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return None
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None


def audit_output_release_surface(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Create a conservative file-level inventory; this is not release clearance."""
    root = project_root.resolve()
    output_root = root / "outputs"
    if not output_root.is_dir():
        return {
            "schema_version": "output-release-surface-audit/1",
            "release_clearance": "not_cleared_for_public_release",
            "inventory_complete": False,
            "error": "outputs directory is missing",
            "artifacts": [],
        }

    artifacts: list[dict[str, Any]] = []
    for path in sorted(output_root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root).as_posix()
        if relative == AUDIT_RELATIVE_PATH:
            continue
        field_names, parsed = _json_field_keys(path)
        text_risk = sorted(field_names & TEXT_RISK_KEYS)
        identity_risk = sorted(field_names & IDENTITY_RISK_KEYS)
        ignored = _ignored_by_git(root, relative)
        structured = path.suffix.casefold() in {".json", ".jsonl"}
        review_reasons: list[str] = []
        if text_risk:
            review_reasons.append("text_bearing_field_names")
        if identity_risk:
            review_reasons.append("identity_or_provenance_field_names")
        if not structured:
            review_reasons.append("non_json_artifact_requires_manual_review")
        elif not parsed:
            review_reasons.append("json_parse_failed")
        elif not field_names:
            review_reasons.append("no_inspectable_object_fields")
        if ignored is True:
            review_reasons.append("git_ignored_local_artifact")
        elif ignored is None:
            review_reasons.append("git_ignore_status_unavailable")
        if not review_reasons:
            review_reasons.append("manual_content_and_rights_review_still_required")

        artifacts.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
            "format": path.suffix.casefold().lstrip(".") or "extensionless",
            "json_parse_ok": parsed if structured else None,
            "field_names": sorted(field_names),
            "text_risk_field_names": text_risk,
            "identity_risk_field_names": identity_risk,
            "git_ignored": ignored,
            "review_reasons": review_reasons,
            "release_decision": "manual_review_required",
        })

    return {
        "schema_version": "output-release-surface-audit/1",
        "release_clearance": "not_cleared_for_public_release",
        "inventory_complete": True,
        "scope_note": (
            "Read-only path/hash/JSON-key inventory. Field-name screening is heuristic; "
            "values are not copied, and no artifact is cleared for release."
        ),
        "artifact_count": len(artifacts),
        "artifacts_with_text_risk_keys": sum(bool(item["text_risk_field_names"]) for item in artifacts),
        "artifacts_with_identity_risk_keys": sum(bool(item["identity_risk_field_names"]) for item in artifacts),
        "git_ignored_artifacts": sum(item["git_ignored"] is True for item in artifacts),
        "artifacts": artifacts,
    }


def _write_report(report: dict[str, Any], destination: Path, root: Path, force: bool) -> None:
    resolved = destination.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("Audit report must be written inside the project root") from exc
    if resolved.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing report: {resolved}; pass --force")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="Replace an existing audit report")
    args = parser.parse_args(argv)
    report = audit_output_release_surface(args.project_root)
    try:
        _write_report(report, args.output, args.project_root, args.force)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps({key: value for key, value in report.items() if key != "artifacts"}, ensure_ascii=False, indent=2))
    return 0 if report["inventory_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
