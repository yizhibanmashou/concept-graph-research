from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise ValueError(f"Non-finite JSON number: {value}")


def parse_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=_nonfinite)


def read_json(path: str | Path) -> Any:
    return parse_json(Path(path).read_text(encoding="utf-8-sig"))


def canonical_hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def file_hash(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path: str | Path, obj: Any) -> None:
    """Atomic UTF-8 JSON replacement, never a partially visible JSON document."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=".v3-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def provider_key(synset_id: str, usage_id: str) -> str:
    return f"{synset_id}::{usage_id}"


def safe_id(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_. -]{0,159}", value) or value.endswith((" ", ".")):
        raise ValueError("Unsafe identifier")
    if value.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}:
        raise ValueError("Reserved filesystem identifier")
    return value


def load_context(project: str | Path, round_number: int = 0, mode: str = "production") -> dict[str, Any]:
    """Load only completed earlier rounds; the current round is never a provider."""
    project = Path(project)
    if type(round_number) is not int or round_number < 0:
        raise ValueError("round_number must be a nonnegative integer")
    if mode not in {"production", "demo"}:
        raise ValueError("Invalid mode")
    policy = read_json(project / "config/policy.json")
    structures = read_json(project / "config/structural_relations.json")
    basis_doc = read_json(project / "sources/basis_ids.json")
    basis_ids = basis_doc["basis_ids"]
    if not isinstance(basis_ids, list) or not all(isinstance(x, str) and x.strip() for x in basis_ids) or len(set(basis_ids)) != len(basis_ids):
        raise ValueError("Invalid frozen basis membership")
    providers: dict[str, Any] = {}
    snapshots: list[dict[str, Any]] = []
    publication_root = project / ("published" if mode == "production" else "demo_published")
    previous_manifest_hash = None
    expected_round = 0
    config_hashes = {"policy_hash": canonical_hash(policy), "structures_hash": canonical_hash(structures),
                     "basis_hash": canonical_hash(basis_ids)}
    for directory in sorted(publication_root.glob("round_*"), key=lambda p: p.name):
        match = re.fullmatch(r"round_(\d+)", directory.name)
        if not match or int(match[1]) >= round_number:
            continue
        manifest = read_json(directory / "manifest.json")
        registry = read_json(directory / "registry.json")
        number = int(match[1])
        if number != expected_round or manifest.get("round") != number or registry.get("round") != number:
            raise ValueError("Published rounds must form a contiguous ordered chain")
        if manifest.get("mode") != mode or manifest.get("previous_manifest_hash") != previous_manifest_hash:
            raise ValueError("Published manifest chain or mode mismatch")
        if manifest.get("config_hashes") != config_hashes:
            raise ValueError("Published providers use stale policy, structures or basis membership")
        if manifest.get("registry_hash") != canonical_hash(registry):
            raise ValueError("Published registry hash mismatch")
        # Import locally to avoid the common/pipeline module import cycle.
        from .pipeline import _authority, FORMULA_CHECKS, INVENTORY_CHECKS
        authority_hash = canonical_hash(_authority(project))
        expected_providers = dict(providers)
        bundle_rows = manifest.get("bundles")
        if not isinstance(bundle_rows, list) or not bundle_rows:
            raise ValueError("Published round has no complete bundles")
        new_ids = set()
        for metadata in bundle_rows:
            sid = safe_id(metadata["synset_id"])
            if sid in new_ids:
                raise ValueError("Duplicate published sense bundle")
            new_ids.add(sid)
            relative = metadata.get("path")
            if relative != f"bundles/{sid}.json":
                raise ValueError("Unexpected published bundle path")
            bundle_path = (directory / relative).resolve()
            if not bundle_path.is_relative_to(directory.resolve()):
                raise ValueError("Published bundle escapes its frozen round")
            bundle = read_json(bundle_path)
            digest = canonical_hash(bundle)
            if digest != metadata.get("bundle_hash") or bundle.get("synset_id") != sid:
                raise ValueError("Published bundle hash or identity mismatch")
            if bundle.get("round") != number or bundle.get("mode") != mode:
                raise ValueError("Published bundle round/mode mismatch")
            if bundle.get("config_hashes") != config_hashes or bundle.get("authority_hash") != authority_hash:
                raise ValueError("Published bundle has stale rules, schemas or skills")
            if bundle.get("context_hash") != manifest.get("context_hash"):
                raise ValueError("Published bundle context mismatch")
            source, inventory = bundle["source"], bundle["inventory"]
            source_hash = canonical_hash(source)
            if source_hash != manifest.get("source_hashes", {}).get(sid):
                raise ValueError("Published source hash mismatch")
            if source != read_json(project / "sources/items" / (sid + ".json")):
                raise ValueError("Published source differs from frozen current source")
            source_manifest = project / "sources/manifest.json"
            if source_manifest.exists():
                item = read_json(source_manifest).get("items", {}).get(sid)
                if not item or item.get("source_hash") != source_hash:
                    raise ValueError("Published source no longer matches import manifest")
            if source.get("is_basis") != (sid in basis_ids):
                raise ValueError("Published basis membership mismatch")
            formulas = bundle["formulas"]
            usage_ids = [u["usage_id"] for u in inventory["usages"]]
            formula_ids = [f["usage_id"] for f in formulas]
            if not usage_ids or len(set(usage_ids)) != len(usage_ids) or len(set(formula_ids)) != len(formula_ids) or set(usage_ids) != set(formula_ids):
                raise ValueError("Published bundle has incomplete or duplicate usages")
            certs = bundle["certificates"]
            stages = [(certs["inventory"], None, "inventory", INVENTORY_CHECKS)] + [
                (certs["formulas"][f["usage_id"]], f, "formula", FORMULA_CHECKS) for f in formulas]
            for cert, formula, stage, required in stages:
                review = cert.get("review", {})
                if (cert.get("stage") != stage or cert.get("mode") != mode or cert.get("source_hash") != source_hash
                        or cert.get("inventory_hash") != canonical_hash(inventory)
                        or cert.get("formula_hash") != (canonical_hash(formula) if formula is not None else None)
                        or cert.get("context_hash") != bundle.get("context_hash")
                        or review.get("decision") != "ACCEPT" or review.get("issues") != []
                        or any(review.get("checks", {}).get(check) is not True for check in required)):
                    raise ValueError("Published certificate is incomplete or stale")
            for formula in formulas:
                key = provider_key(sid, formula["usage_id"])
                if key in expected_providers:
                    raise ValueError("Published provider shadows an earlier usage")
                expected_providers[key] = {
                    "synset_id": sid, "usage_id": formula["usage_id"], "bundle_hash": digest,
                    "round": number, "is_basis": sid in basis_ids, "mode": mode,
                    "parameters": formula["parameters"], "lhs": formula["lhs"], "rhs": formula["rhs"],
                    "primitives": formula.get("primitives", []), "source": source, "inventory": inventory,
                    "formula": formula, "certificates": certs,
                }
        if number == 0 and new_ids != set(basis_ids):
            raise ValueError("Round zero must publish the complete frozen basis")
        if number > 0 and new_ids.intersection(basis_ids):
            raise ValueError("Basis implementation belongs in round zero")
        snapshots.append({"round": int(match[1]), "manifest_hash": canonical_hash(manifest),
                          "registry_hash": canonical_hash(registry)})
        entries = registry.get("providers")
        if not isinstance(entries, dict):
            raise ValueError("Malformed published provider registry")
        if entries != expected_providers:
            raise ValueError("Registry does not exactly match the certified complete bundle formulas")
        for key, row in entries.items():
            if not isinstance(row, dict) or "rhs" not in row or "lhs" not in row:
                raise ValueError(f"Formula-less provider: {key}")
            if row.get("mode") != mode or row.get("round", round_number) >= round_number:
                raise ValueError(f"Invalid provider authority: {key}")
            if key != provider_key(row["synset_id"], row["usage_id"]):
                raise ValueError(f"Invalid provider identity: {key}")
            if key in providers and providers[key] != row:
                raise ValueError(f"Provider shadow forbidden: {key}")
            providers[key] = row
        previous_manifest_hash = canonical_hash(manifest)
        expected_round += 1
    context: dict[str, Any] = {
        "policy": policy, "structures": structures, "basis_ids": basis_ids,
        "providers": providers, "round": round_number, "mode": mode,
        "policy_hash": canonical_hash(policy), "structures_hash": canonical_hash(structures),
        "basis_hash": canonical_hash(basis_ids), "snapshots": snapshots,
    }
    context["context_hash"] = canonical_hash(context)
    return context
