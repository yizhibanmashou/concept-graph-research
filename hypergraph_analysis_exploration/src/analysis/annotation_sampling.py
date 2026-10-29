"""Build a reproducible, text-free candidate frame for WordNet annotation.

The emitted frame contains IDs, strata, hashes, and source paths, but no gloss
text. It is not a gold dataset or a population performance estimate.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any


try:  # Direct script execution and package/module execution are both supported.
    from .project_paths import PROJECT_ROOT, configured_bundle_root
except ImportError:
    from project_paths import PROJECT_ROOT, configured_bundle_root


DEFAULT_BUNDLE = configured_bundle_root()
DEFAULT_OUTPUT = PROJECT_ROOT / "outputs" / "phase7" / "annotation_sampling_frame.jsonl"
DEFAULT_MANIFEST = PROJECT_ROOT / "outputs" / "phase7" / "annotation_sampling_manifest.json"
TARGET_POS = {"n", "v", "a", "r"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _length_band(length: int) -> str:
    if length <= 50:
        return "short_le_50"
    if length <= 100:
        return "medium_51_100"
    return "long_gt_100"


def _apportion(total: int, sizes: dict[str, int], minimum_per_nonempty: int = 1) -> dict[str, int]:
    """Allocate proportional quotas after a minimum floor per nonempty stratum."""
    if (not isinstance(minimum_per_nonempty, int) or isinstance(minimum_per_nonempty, bool)
            or minimum_per_nonempty < 1):
        raise ValueError("minimum_per_nonempty must be a positive integer")
    if total < 0 or total > sum(sizes.values()):
        raise ValueError("sample size must be between zero and total population")
    active = [key for key, size in sizes.items() if size > 0]
    if not active or total == 0:
        return {key: 0 for key in sizes}
    allocation = {key: min(minimum_per_nonempty, sizes[key]) if key in active else 0 for key in sizes}
    minimum_total = sum(allocation.values())
    if total < minimum_total:
        raise ValueError("sample size is below the requested minimum per nonempty stratum")

    remaining_total = total - minimum_total
    capacities = {key: max(0, sizes[key] - allocation[key]) for key in sizes}
    capacity_total = sum(capacities.values())
    if remaining_total == 0 or capacity_total == 0:
        return allocation
    quotas = {key: remaining_total * capacities[key] / capacity_total for key in sizes}
    for key in sizes:
        allocation[key] += min(capacities[key], int(quotas[key]))
    remaining = total - sum(allocation.values())
    order = sorted(sizes, key=lambda key: (-(quotas[key] - int(quotas[key])), key))
    while remaining:
        progressed = False
        for key in order:
            if allocation[key] < sizes[key]:
                allocation[key] += 1
                remaining -= 1
                progressed = True
                if remaining == 0:
                    break
        if not progressed:
            raise ValueError("could not allocate requested sample within stratum capacities")
    return allocation


def _stratum(row: dict[str, Any]) -> str:
    punctuation = "punct" if any(mark in row["definition"] for mark in (";", ",")) else "plain"
    return f"pos={row['pos']}|length={_length_band(len(row['definition']))}|{punctuation}"


def _read_witness_features(bundle: Path) -> dict[str, dict[str, int]]:
    witness_path = bundle / "graph" / "coverage_witnesses.jsonl"
    witness_by_head: dict[str, dict[str, Any]] = {}
    fanout: Counter[str] = Counter()
    with witness_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                head = row["head"]
                depth = row["proof_depth"]
                clause = row["witness_clause"]
                is_seed = row["is_seed"]
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                raise ValueError(f"invalid selected witness at line {line_number}") from exc
            if (not isinstance(head, str) or not head or head in witness_by_head
                    or not isinstance(depth, int) or isinstance(depth, bool) or depth < 0
                    or not isinstance(clause, list)
                    or any(not isinstance(dep, str) or not dep for dep in clause)
                    or not isinstance(is_seed, bool)):
                raise ValueError(f"malformed selected witness at line {line_number}")
            if is_seed != (depth == 0) or (is_seed and clause) or (not is_seed and not clause):
                raise ValueError(f"inconsistent selected witness at line {line_number}")
            witness_by_head[head] = {"proof_depth": depth, "witness_clause": clause}
            if not is_seed:
                fanout.update(set(clause))

    return {
        head: {
            "selected_witness_depth": row["proof_depth"],
            "selected_witness_width": len(row["witness_clause"]),
            "selected_witness_fanout": fanout.get(head, 0),
        }
        for head, row in witness_by_head.items()
    }


def _read_population(bundle: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    nodes_path = bundle / "graph" / "nodes.tsv"
    clauses_by_head: dict[str, list[int]] = defaultdict(list)
    with (bundle / "graph" / "hypergraph_rules.jsonl").open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                rule = json.loads(line)
                head = rule["head"]
                if head in clauses_by_head:
                    raise ValueError(f"duplicate rule head {head}")
                clauses_by_head[head] = [len(clause) for clause in rule["clauses"]]
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                raise ValueError(f"invalid graph rule at line {line_number}") from exc

    witness_features = _read_witness_features(bundle)
    if set(witness_features) != set(clauses_by_head):
        raise ValueError("selected witness heads do not exactly match hypergraph rule heads")

    rows: list[dict[str, Any]] = []
    exclusions = {
        "oewn_namespace_rows": 0,
        "excluded_nonstandard_pos": 0,
        "excluded_missing_definition_in_standard_pos": 0,
    }
    with nodes_path.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            sense_id = row.get("synset_id", "")
            pos = row.get("pos", "")
            definition = row.get("definition", "")
            # Exclude external WordNet additions and project-local numbered concepts.
            if not sense_id.startswith("oewn-"):
                continue
            exclusions["oewn_namespace_rows"] += 1
            if pos not in TARGET_POS:
                exclusions["excluded_nonstandard_pos"] += 1
                continue
            if not definition:
                exclusions["excluded_missing_definition_in_standard_pos"] += 1
                continue
            widths = clauses_by_head.get(sense_id)
            if not widths:
                raise ValueError(f"no hypergraph rule found for OEWN node {sense_id}")
            rows.append({
                "sense_id": sense_id,
                "pos": pos,
                "definition": definition,
                "source_root": row.get("source_root", ""),
                "is_basis": row.get("is_basis", "False").casefold() == "true",
                "clause_count": len(widths),
                "max_clause_width": max(widths),
                "has_alternative_clauses": len(widths) > 1,
                **witness_features[sense_id],
            })
    if not rows:
        raise ValueError("no eligible OEWN synsets found")
    exclusions["eligible_standard_pos_nonempty_definition"] = len(rows)
    return rows, exclusions


def _allocate_random_panel(
    population: list[dict[str, Any]], size: int, rng: random.Random,
    minimum_per_nonempty_stratum: int = 1,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    strata: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in population:
        strata[_stratum(row)].append(row)
    quotas = _apportion(
        size, {key: len(value) for key, value in strata.items()},
        minimum_per_nonempty=minimum_per_nonempty_stratum,
    )
    chosen: list[dict[str, Any]] = []
    for key in sorted(strata):
        chosen.extend(rng.sample(strata[key], quotas[key]))
    rng.shuffle(chosen)
    return chosen, quotas


def _choose_diagnostic_panel(
    population: list[dict[str, Any]], already_selected: set[str], size: int, rng: random.Random
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    if size == 0:
        return [], {"max_clause_width_p90": 0, "selected_witness_depth_p90": 0}
    eligible = [row for row in population if row["sense_id"] not in already_selected]
    alternatives = [row for row in eligible if row["has_alternative_clauses"]]
    if not eligible:
        raise ValueError("no remaining candidates for diagnostic sample")
    widths = sorted(row["max_clause_width"] for row in eligible)
    depths = sorted(row["selected_witness_depth"] for row in eligible)
    width_p90 = widths[int(.9 * (len(widths) - 1))]
    depth_p90 = depths[int(.9 * (len(depths) - 1))]
    wide = [row for row in eligible if row["max_clause_width"] >= width_p90]
    alternative_ids = {row["sense_id"] for row in alternatives}
    wide_only = [row for row in wide if row["sense_id"] not in alternative_ids]
    deep = [row for row in eligible if row["selected_witness_depth"] >= depth_p90]
    already_diagnostic_ids = alternative_ids | {row["sense_id"] for row in wide_only}
    deep_only = [row for row in deep if row["sense_id"] not in already_diagnostic_ids]

    base, remainder = divmod(size, 3)
    alternative_quota = base + (1 if remainder > 0 else 0)
    width_quota = base + (1 if remainder > 1 else 0)
    depth_quota = base
    if (len(alternatives) < alternative_quota or len(wide_only) < width_quota
            or len(deep_only) < depth_quota):
        raise ValueError("not enough non-overlapping OR/high-width/high-depth cases for requested diagnostic size")
    picked_alternatives = rng.sample(alternatives, alternative_quota)
    picked_wide = rng.sample(wide_only, width_quota)
    picked_deep = rng.sample(deep_only, depth_quota)
    for row in picked_alternatives:
        row["diagnostic_reason"] = "multiple_OR_clauses"
    for row in picked_wide:
        row["diagnostic_reason"] = f"high_max_clause_width_p90_threshold_{width_p90}"
    for row in picked_deep:
        row["diagnostic_reason"] = f"high_selected_witness_depth_p90_threshold_{depth_p90}"
    return picked_alternatives + picked_wide + picked_deep, {
        "max_clause_width_p90": width_p90,
        "selected_witness_depth_p90": depth_p90,
    }


def _read_selected_lineage(bundle: Path, selected_ids: set[str]) -> dict[str, dict[str, Any]]:
    index_path = bundle / "indexes" / "senses.jsonl"
    found: dict[str, dict[str, Any]] = {}
    with index_path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid sense index at line {line_number}") from exc
            identity = row.get("identity")
            if identity in selected_ids:
                found[identity] = row
                if len(found) == len(selected_ids):
                    break
    missing = selected_ids - set(found)
    if missing:
        raise ValueError(f"missing provenance index records, e.g. {sorted(missing)[:5]}")
    return found


def _source_records(bundle: Path, row: dict[str, Any]) -> list[dict[str, str]]:
    raw_records = row.get("source_records")
    if not isinstance(raw_records, list) or not raw_records:
        raise ValueError(f"no source records indexed for {row.get('identity')}")
    bundle_root = bundle.resolve()
    result = []
    for source in raw_records:
        if not isinstance(source, dict) or not isinstance(source.get("path"), str):
            raise ValueError(f"malformed source record entry for {row.get('identity')}")
        relative = PurePosixPath(source["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"unsafe source path for {row.get('identity')}: {source['path']}")
        path = bundle_root.joinpath(*relative.parts).resolve()
        if not path.is_relative_to(bundle_root) or not path.is_file():
            raise ValueError(f"source path is missing or escapes bundle for {row.get('identity')}: {source['path']}")
        result.append({"path": source["path"], "sha256": _sha256(path)})
    return result


def build_frame(
    bundle: Path, random_size: int = 160, diagnostic_size: int = 40, seed: int = 20261002,
    minimum_random_per_stratum: int = 1,
):
    bundle = bundle.resolve()
    manifest_path = bundle / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"missing bundle manifest: {manifest_path}")
    bundle_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if bundle_manifest.get("graph_version") != "alternative_or_definition_wsd_complete_hypergraph_after_basis85_law_complete_or":
        raise ValueError("unexpected graph version; check this bundle before sampling")
    population, exclusions = _read_population(bundle)
    if random_size + diagnostic_size > len(population):
        raise ValueError("requested sample is larger than the eligible population")

    rng = random.Random(seed)
    random_panel, random_quotas = _allocate_random_panel(
        population, random_size, rng, minimum_per_nonempty_stratum=minimum_random_per_stratum,
    )
    selected = {row["sense_id"] for row in random_panel}
    diagnostic_panel, diagnostic_thresholds = _choose_diagnostic_panel(population, selected, diagnostic_size, rng)
    for row in random_panel:
        row["panel"] = "random_stratified"
        row["stratum"] = _stratum(row)
    for row in diagnostic_panel:
        row["panel"] = "diagnostic_not_for_population_estimates"
        row["stratum"] = row["diagnostic_reason"]
    chosen = random_panel + diagnostic_panel

    population_by_stratum = Counter(_stratum(row) for row in population)
    selected_by_stratum = Counter(row["stratum"] for row in random_panel)
    random_panel_strata = {
        stratum: {
            "population_count": count,
            "sample_count": selected_by_stratum.get(stratum, 0),
            "inclusion_probability": selected_by_stratum.get(stratum, 0) / count,
            "design_weight": count / selected_by_stratum[stratum] if selected_by_stratum.get(stratum, 0) else None,
        }
        for stratum, count in sorted(population_by_stratum.items())
    }

    selected_ids = {row["sense_id"] for row in chosen}
    lineage = _read_selected_lineage(bundle, selected_ids)
    frame = []
    for row in chosen:
        source_index = lineage[row["sense_id"]]
        source_records = _source_records(bundle, source_index)
        lemmas = []
        for source in source_index.get("source_records", []):
            if source.get("identity") == row["sense_id"] and isinstance(source.get("lemmas"), list):
                lemmas = source["lemmas"]
                break
        if not lemmas:
            lemmas = [source_index.get("lemmas", "")]
        frame.append({
            "frame_version": "oewn-annotation-candidate/2",
            "item_id": f"{bundle_manifest.get('graph_version')}:{row['sense_id']}",
            "sense_id": row["sense_id"],
            "lemmas": lemmas,
            "pos": row["pos"],
            "source_root": row["source_root"],
            "snapshot_definition_sha256": hashlib.sha256(row["definition"].encode("utf-8")).hexdigest(),
            "snapshot_definition_length_codepoints": len(row["definition"]),
            "graph": {
                "semantic_fingerprint_sha256": bundle_manifest.get("semantic_fingerprint_sha256"),
                "head_count": bundle_manifest.get("head_count"),
                "clause_count": bundle_manifest.get("clause_count"),
            },
            "structural_features": {
                "clause_count": row["clause_count"],
                "max_clause_width": row["max_clause_width"],
                "is_basis": row["is_basis"],
                "selected_witness_depth": row["selected_witness_depth"],
                "selected_witness_width": row["selected_witness_width"],
                "selected_witness_fanout": row["selected_witness_fanout"],
            },
            "panel": row["panel"],
            "annotator_visible": False,
            "stratum": row["stratum"],
            "random_seed": seed,
            "source_records": source_records,
            "license_review": "pending_per_source_record_and_version",
        })
    summary = {
        "frame_version": "oewn-annotation-candidate/2",
        "bundle_path_for_local_reproduction": str(bundle),
        "graph_version": bundle_manifest.get("graph_version"),
        "graph_sha256": bundle_manifest.get("graph_sha256"),
        "semantic_fingerprint_sha256": bundle_manifest.get("semantic_fingerprint_sha256"),
        "eligible_oewn_sense_count": len(population),
        "population_scope_exclusions": exclusions,
        "random_panel_count": len(random_panel),
        "random_panel_stratification": (
            "POS x gloss length band (<=50, 51-100, >100 code points) x comma-or-semicolon marker; "
            f"minimum {minimum_random_per_stratum} per nonempty stratum, residual allocated proportionally; excludes graph features"
        ),
        "minimum_random_per_nonempty_stratum": minimum_random_per_stratum,
        "random_panel_allocation": random_quotas,
        "diagnostic_panel_count": len(diagnostic_panel),
        "sampling_policy_version": "oewn-annotation-candidate/3" if minimum_random_per_stratum > 1 else "oewn-annotation-candidate/2",
        "diagnostic_categories": {
            "alternative_clause_cases": (diagnostic_size + 2) // 3,
            "high_width_non_or_cases": (diagnostic_size + 1) // 3,
            "high_witness_depth_non_or_high_width_cases": diagnostic_size // 3,
        },
        "diagnostic_p90_thresholds": diagnostic_thresholds,
        "diagnostic_panel_for_population_estimates": False,
        "annotator_visible": False,
        "random_panel_strata": random_panel_strata,
        "seed": seed,
        "gloss_text_included": False,
        "source_version_and_license_review": "pending; bundle includes transformed records and does not declare a single source license",
    }
    return frame, summary


def write_frame_outputs(
    frame: list[dict[str, Any]], summary: dict[str, Any], output_path: Path, manifest_path: Path
) -> dict[str, Any]:
    """Write an LF-stable candidate frame and bind its manifest to exact bytes."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in frame),
        encoding="utf-8",
    )
    result = dict(summary)
    result["candidate_count"] = len(frame)
    result["frame_sha256"] = _sha256(output_path)
    manifest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest-output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--random-size", type=int, default=160)
    parser.add_argument("--diagnostic-size", type=int, default=40)
    parser.add_argument("--minimum-random-per-stratum", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20261002)
    parser.add_argument("--force", action="store_true", help="replace existing frame and manifest outputs")
    args = parser.parse_args(argv)
    if args.random_size < 0 or args.diagnostic_size < 0:
        parser.error("sample sizes must be non-negative")
    if args.minimum_random_per_stratum < 1:
        parser.error("minimum random sample per stratum must be positive")
    if not args.force and (args.output.exists() or args.manifest_output.exists()):
        parser.error("output already exists; choose another path or pass --force to replace it")
    try:
        frame, summary = build_frame(
            args.bundle, args.random_size, args.diagnostic_size, args.seed,
            minimum_random_per_stratum=args.minimum_random_per_stratum,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    write_frame_outputs(frame, summary, args.output, args.manifest_output)
    print(f"Wrote {len(frame)} text-free annotation candidates to {args.output}")
    print(f"Sampling manifest: {args.manifest_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
