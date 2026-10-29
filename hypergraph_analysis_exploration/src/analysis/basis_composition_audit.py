"""Aggregate the frozen graph's selected basis by node metadata.

This describes the package's structural seed set. It does not identify semantic
primitives, establish global minimality, or validate gloss meaning.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.analysis.project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_BUNDLE = configured_bundle_root()
DEFAULT_REPORT = PROJECT_ROOT / "outputs" / "phase6" / "basis_composition_audit.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_basis_composition(bundle: Path) -> dict[str, Any]:
    bundle = bundle.resolve()
    graph_dir = bundle / "graph"
    basis_path = graph_dir / "selected_basis_atoms.txt"
    nodes_path = graph_dir / "nodes.tsv"
    manifest_path = bundle / "manifest.json"
    if not all(path.is_file() for path in (basis_path, nodes_path, manifest_path)):
        raise ValueError("bundle must contain manifest.json and graph basis/nodes files")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        raw_basis = basis_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("basis inputs are unreadable or malformed") from exc

    basis_rows = [item.strip() for item in raw_basis if item.strip()]
    basis = set(basis_rows)
    if len(basis) != len(basis_rows):
        raise ValueError("selected_basis_atoms.txt contains duplicate IDs")

    selected_rows: dict[str, dict[str, str]] = {}
    try:
        with nodes_path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            required = {"synset_id", "pos", "source_root", "is_basis"}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError("nodes.tsv lacks required basis metadata columns")
            for row in reader:
                node_id = row.get("synset_id", "")
                if node_id in basis:
                    if node_id in selected_rows:
                        raise ValueError("nodes.tsv contains a duplicate selected basis ID")
                    selected_rows[node_id] = row
    except OSError as exc:
        raise ValueError("could not read graph nodes.tsv") from exc

    missing = basis - selected_rows.keys()
    if missing:
        raise ValueError("one or more selected basis IDs are absent from nodes.tsv")
    if any(row.get("is_basis", "").casefold() != "true" for row in selected_rows.values()):
        raise ValueError("selected_basis_atoms.txt disagrees with nodes.tsv is_basis flags")

    pos_counts = Counter(row.get("pos") or "other_or_missing" for row in selected_rows.values())
    source_root_counts = Counter(
        row.get("source_root") or "other_or_missing" for row in selected_rows.values()
    )
    namespace_counts = Counter(
        "oewn" if node_id.startswith("oewn-") else "non_oewn"
        for node_id in selected_rows
    )
    expected_graph_hash = manifest.get("graph_sha256")
    if not isinstance(expected_graph_hash, str):
        expected_graph_hash = None

    return {
        "audit_version": "frozen-basis-composition/1",
        "claim_type": "structural_basis_metadata_not_semantic_primitives",
        "input_graph_sha256": expected_graph_hash,
        "input_basis_file_sha256": _sha256(basis_path),
        "input_nodes_file_sha256": _sha256(nodes_path),
        "basis_count": len(basis),
        "matched_node_count": len(selected_rows),
        "pos_counts": dict(sorted(pos_counts.items())),
        "source_root_counts": dict(sorted(source_root_counts.items())),
        "id_namespace_counts": dict(sorted(namespace_counts.items())),
        "integrity_checks": {
            "basis_ids_unique": True,
            "all_basis_ids_match_one_node": len(selected_rows) == len(basis),
            "node_basis_flags_agree": True,
        },
        "basis_ids_emitted": False,
        "raw_definitions_emitted": False,
        "interpretation_limit": (
            "POS, source-root and ID-namespace distributions describe the delivered package's "
            "selected structural seeds only; they do not show that these items are semantic "
            "primitives, that the basis is globally minimal, or that gloss-derived rules are valid."
        ),
    }


def _ensure_project_output(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError("report output must be inside the project directory")
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        output = _ensure_project_output(args.output)
        if output.exists() and not args.force:
            raise ValueError("report already exists; choose another path or pass --force")
        report = audit_basis_composition(args.bundle)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Profiled {report['basis_count']} structural basis entries by POS, source root, and namespace"
    )
    print(f"Wrote aggregate-only report: {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
