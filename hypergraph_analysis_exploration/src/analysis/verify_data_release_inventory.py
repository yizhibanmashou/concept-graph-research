"""Read-only consistency checks for the data release inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any
import zipfile

from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root


UNCLEARED = "not_cleared_for_public_release"


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_release_inventory(
    project_root: Path = PROJECT_ROOT,
    inventory_path: Path | None = None,
    bundle_root: Path | None = None,
) -> dict[str, Any]:
    """Audit inventory claims against local files without modifying any file.

    This checks reproducibility/provenance consistency only; it never grants legal
    clearance or changes the release status recorded in the inventory.
    """
    root = project_root.resolve()
    inventory_file = inventory_path or root / "sources" / "data_release_inventory.json"
    checks: list[dict[str, Any]] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    try:
        inventory = json.loads(inventory_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "inventory_consistent": False,
            "release_clearance": UNCLEARED,
            "checks": [{"check": "inventory_readable", "ok": False, "detail": str(exc)}],
        }

    record("schema_version", inventory.get("schema_version") == "data-release-inventory/1",
           f"schema_version={inventory.get('schema_version')!r}")
    record("release_status_conservative", inventory.get("project_release_status") == UNCLEARED,
           f"project_release_status={inventory.get('project_release_status')!r}; checker never grants clearance")

    resources = inventory.get("upstream_resources", [])
    if not isinstance(resources, list) or not resources:
        resources = []
        record("upstream_resources_present", False, "No upstream resource entries found")
    else:
        record("upstream_resources_present", True, f"{len(resources)} upstream resource entries")

    for resource in resources:
        if not isinstance(resource, dict):
            record("upstream_entry", False, "Entry is not an object")
            continue
        resource_id = str(resource.get("resource_id", "unknown"))
        rel = resource.get("local_archive")
        expected = resource.get("local_archive_sha256")
        if not isinstance(rel, str) or not isinstance(expected, str):
            record(f"archive:{resource_id}", False, "Missing local_archive or local_archive_sha256")
            continue
        archive = (root / rel).resolve()
        if not _inside(root, archive):
            record(f"archive:{resource_id}", False, "Archive path escapes project root")
            continue
        if not archive.is_file():
            record(f"archive:{resource_id}", False, f"Archive not found: {rel}")
            continue
        actual = _sha256(archive)
        record(f"archive_sha256:{resource_id}", actual == expected,
               f"expected={expected}; actual={actual}")
        try:
            with zipfile.ZipFile(archive) as zipped:
                bad_member = zipped.testzip()
                names = [name.lower().replace("\\", "/") for name in zipped.namelist()]
            record(f"archive_integrity:{resource_id}", bad_member is None,
                   "ZIP members passed CRC check" if bad_member is None else f"Bad ZIP member: {bad_member}")
            declared_presence = resource.get("archive_contains_license_or_readme")
            if isinstance(declared_presence, bool):
                actual_presence = any(
                    Path(name).name.startswith(("license", "licence", "readme", "copying"))
                    for name in names
                )
                record(f"archive_notices:{resource_id}", actual_presence == declared_presence,
                       f"declared={declared_presence}; actual={actual_presence}")
        except (OSError, zipfile.BadZipFile) as exc:
            record(f"archive_integrity:{resource_id}", False, str(exc))

    artifacts = inventory.get("project_artifacts", [])
    code_artifact = next((entry for entry in artifacts
                          if isinstance(entry, dict) and entry.get("resource_id") == "project_source_code_and_docs"), None)
    if code_artifact is None or not isinstance(code_artifact.get("root_license_file_present"), bool):
        record("root_license_file", False, "Missing boolean root_license_file_present inventory field")
    else:
        actual_license = any((root / name).is_file() for name in ("LICENSE", "LICENSE.md"))
        expected_license = code_artifact["root_license_file_present"]
        record("root_license_file", actual_license == expected_license,
               f"declared={expected_license}; actual={actual_license}")

    inputs = inventory.get("project_inputs", [])
    bundle_entry = next((entry for entry in inputs
                         if isinstance(entry, dict) and entry.get("resource_id") == "frozen_hypergraph_bundle_154206"), None)
    if bundle_entry is None:
        record("frozen_bundle_manifest", False, "Frozen bundle entry missing")
    else:
        try:
            selected_bundle = bundle_root.resolve() if bundle_root is not None else configured_bundle_root(root)
            manifest_rel = bundle_entry.get("local_manifest", "manifest.json")
            manifest_path = (selected_bundle / manifest_rel).resolve()
            if not _inside(selected_bundle, manifest_path):
                raise ValueError("Manifest path escapes bundle root")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            comparisons = {
                "head_count": "head_count",
                "clause_count": "clause_count",
                "source_record_files": "source_record_files",
                "graph_sha256": "graph_sha256",
                "semantic_fingerprint_sha256": "semantic_fingerprint_sha256",
                "head_kinds": "head_kinds",
            }
            for inventory_key, manifest_key in comparisons.items():
                expected_value = bundle_entry.get(inventory_key)
                actual_value = manifest.get(manifest_key)
                record(f"bundle:{inventory_key}", expected_value == actual_value,
                       f"inventory={expected_value!r}; manifest={actual_value!r}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            record("frozen_bundle_manifest", False, str(exc))

    return {
        "inventory_consistent": all(item["ok"] for item in checks),
        "release_clearance": UNCLEARED,
        "inventory_path": str(inventory_file),
        "checks": checks,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--bundle", type=Path, help="Override configured frozen bundle root")
    args = parser.parse_args(argv)
    result = audit_release_inventory(args.project_root, args.inventory, args.bundle)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["inventory_consistent"] else 1


if __name__ == "__main__":
    sys.exit(main())
