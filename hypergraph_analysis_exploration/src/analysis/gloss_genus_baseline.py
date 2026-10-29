"""Evaluate a conservative lexical genus-candidate baseline on a blind batch.

This is a lexical lookup baseline, not a semantic parser. It selects the first
exact noun-lemma match near the beginning of noun glosses and compares that
candidate to the released OEWN direct-hypernym relation. It never emits rules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


BASELINE_VERSION = "first-exact-noun-lemma/1"
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*")
LEADING_DETERMINERS = {"a", "an", "the", "some", "any", "one"}
NON_GENUS_PRONOUNS = {"someone", "somebody", "something", "anyone", "anybody", "anything"}
MAX_NGRAM_TOKENS = 4
MAX_PREFIX_TOKENS = 12
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RELEASE_DIR = PROJECT_ROOT / "tmp" / "oewn-2025-plus-json"
DEFAULT_RELEASE_ARCHIVE = PROJECT_ROOT / "tmp" / "oewn-2025-plus-json.zip"
DEFAULT_BATCH = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_blind.jsonl"
DEFAULT_ANSWER_KEY = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_answer_key.json"
DEFAULT_MANIFEST = PROJECT_ROOT / "outputs" / "phase7" / "annotation_batch_2025_plus_manifest.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: row must be a JSON object")
            rows.append(row)
    return rows


def build_noun_lemma_index(release_dir: Path) -> dict[str, list[str]]:
    """Map normalized OEWN noun lemmas to sorted synset IDs."""
    index: dict[str, set[str]] = {}
    entry_files = sorted(release_dir.glob("entries-*.json"))
    if not entry_files:
        raise FileNotFoundError(f"no entries-*.json files found in {release_dir}")
    for path in entry_files:
        entries = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(entries, dict):
            raise ValueError(f"expected an object in {path}")
        for lemma, pos_map in entries.items():
            if not isinstance(lemma, str) or not isinstance(pos_map, dict):
                continue
            noun_entry = pos_map.get("n")
            senses = noun_entry.get("sense", []) if isinstance(noun_entry, dict) else []
            if not isinstance(senses, list):
                continue
            normalized = " ".join(lemma.casefold().split())
            for sense in senses:
                synset_id = sense.get("synset") if isinstance(sense, dict) else None
                if isinstance(synset_id, str) and synset_id:
                    index.setdefault(normalized, set()).add(synset_id)
    return {lemma: sorted(synsets) for lemma, synsets in index.items()}


def load_direct_hypernyms(release_dir: Path, target_ids: set[str]) -> dict[str, list[str]]:
    """Read direct hypernym IDs for requested OEWN namespace synsets only."""
    result: dict[str, list[str]] = {}
    release_to_oewn = {target_id.removeprefix("oewn-"): target_id for target_id in target_ids}
    paths = sorted(release_dir.glob("noun.*.json"))
    if not paths:
        raise FileNotFoundError(f"no noun.*.json synset files found in {release_dir}")
    for path in paths:
        synsets = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(synsets, dict):
            raise ValueError(f"expected an object in {path}")
        for release_id in release_to_oewn.keys() - {key.removeprefix("oewn-") for key in result}:
            record = synsets.get(release_id)
            if isinstance(record, dict):
                hypernyms = record.get("hypernym", [])
                if not isinstance(hypernyms, list) or any(not isinstance(x, str) for x in hypernyms):
                    raise ValueError(f"invalid hypernym list for synset {release_id} in {path}")
                result[release_to_oewn[release_id]] = sorted(set(hypernyms))
    missing = target_ids - result.keys()
    if missing:
        raise ValueError(f"{len(missing)} target synset(s) are missing from OEWN release")
    return result


def find_first_noun_candidate(gloss: str, excluded_lemmas: list[str],
                              noun_index: dict[str, list[str]]) -> dict[str, Any] | None:
    """Return the earliest exact noun lemma match, preserving character span."""
    tokens = list(TOKEN_RE.finditer(gloss))[:MAX_PREFIX_TOKENS]
    excluded = {" ".join(lemma.casefold().split()) for lemma in excluded_lemmas if isinstance(lemma, str)}
    start_index = 0
    while start_index < len(tokens) and tokens[start_index].group(0).casefold() in LEADING_DETERMINERS:
        start_index += 1
    if start_index < len(tokens) and tokens[start_index].group(0).casefold() in NON_GENUS_PRONOUNS:
        return None

    for token_index in range(start_index, len(tokens)):
        for length in range(min(MAX_NGRAM_TOKENS, len(tokens) - token_index), 0, -1):
            selection = tokens[token_index:token_index + length]
            lemma = " ".join(token.group(0).casefold() for token in selection)
            if lemma in excluded:
                continue
            synset_ids = noun_index.get(lemma)
            if synset_ids:
                return {
                    "lemma": lemma,
                    "span": {"start": selection[0].start(), "end": selection[-1].end()},
                    "candidate_synset_ids": synset_ids,
                    "candidate_sense_count": len(synset_ids),
                    "token_index": token_index,
                }
    return None


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def evaluate_batch(batch_rows: list[dict[str, Any]], answer_rows: list[dict[str, Any]],
                   noun_index: dict[str, list[str]],
                   direct_hypernyms: dict[str, list[str]]) -> dict[str, Any]:
    answer_by_task = {row.get("task_id"): row for row in answer_rows if isinstance(row, dict)}
    batch_by_task = {row.get("task_id"): row for row in batch_rows if isinstance(row, dict)}
    if len(batch_by_task) != len(batch_rows) or len(answer_by_task) != len(answer_rows):
        raise ValueError("batch and answer key must have unique task_id values")
    if set(batch_by_task) != set(answer_by_task):
        raise ValueError("blind batch and answer key task IDs differ")

    per_task = []
    for task_id in sorted(batch_by_task):
        row = batch_by_task[task_id]
        answer = answer_by_task[task_id]
        if row.get("pos") != "n":
            per_task.append({"task_id": task_id, "panel": answer.get("panel"), "status": "unsupported_pos"})
            continue
        sense_id = answer.get("sense_id")
        if not isinstance(sense_id, str) or sense_id not in direct_hypernyms:
            raise ValueError(f"answer key target lacks release taxonomy record for task {task_id}")
        hypernyms = set(direct_hypernyms[sense_id])
        if not hypernyms:
            per_task.append({"task_id": task_id, "panel": answer.get("panel"), "status": "target_has_no_direct_hypernym"})
            continue
        gloss, lemmas = row.get("gloss"), row.get("lemmas")
        if not isinstance(gloss, str) or not isinstance(lemmas, list):
            raise ValueError(f"blind batch row {task_id} has invalid gloss/lemmas")
        candidate = find_first_noun_candidate(gloss, lemmas, noun_index)
        if candidate is None:
            per_task.append({"task_id": task_id, "panel": answer.get("panel"), "status": "no_lexical_candidate"})
            continue
        matched_hypernyms = sorted(hypernyms.intersection(candidate["candidate_synset_ids"]))
        per_task.append({
            "task_id": task_id,
            "panel": answer.get("panel"),
            "status": "candidate_matches_direct_hypernym" if matched_hypernyms else "candidate_not_direct_hypernym",
            "candidate": candidate,
            "direct_hypernym_count": len(hypernyms),
            "matched_hypernym_sense_count": len(matched_hypernyms),
        })

    def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
        counts = Counter(row["status"] for row in rows)
        eligible_statuses = {
            "candidate_matches_direct_hypernym",
            "candidate_not_direct_hypernym",
            "no_lexical_candidate",
        }
        eligible = sum(count for status, count in counts.items() if status in eligible_statuses)
        covered = counts["candidate_matches_direct_hypernym"] + counts["candidate_not_direct_hypernym"]
        matches = counts["candidate_matches_direct_hypernym"]
        sense_counts = [row["candidate"]["candidate_sense_count"] for row in rows if "candidate" in row]
        return {
            "items": len(rows),
            "eligible_noun_targets_with_direct_hypernym": eligible,
            "status_counts": dict(sorted(counts.items())),
            "candidate_coverage": _ratio(covered, eligible),
            "direct_hypernym_match_rate_among_candidates": _ratio(matches, covered),
            "direct_hypernym_match_rate_over_eligible": _ratio(matches, eligible),
            "candidate_sense_count_mean": _ratio(sum(sense_counts), len(sense_counts)),
            "candidate_sense_count_max": max(sense_counts, default=0),
        }

    groups: dict[str, list[dict[str, Any]]] = {}
    for row in per_task:
        panel = row.get("panel")
        groups.setdefault(panel if isinstance(panel, str) else "unlabeled", []).append(row)
    return {
        "baseline_version": BASELINE_VERSION,
        "method": "In noun glosses, skip an initial determiner, abstain on an initial indefinite pronoun, then select the earliest exact 1-4-token noun lemma match within the first 12 tokens; exclude the target lemmas. No stemming, POS tagging, word-sense disambiguation, or rule generation.",
        "evaluation_target": "Whether any OEWN noun sense for the candidate lemma is listed as a direct hypernym of the target sense in the same release. This is a resource-relative lexical proxy, not semantic gold or evidence that the gloss entails the relation.",
        "overall": summarize(per_task),
        "by_sampling_panel": {panel: summarize(rows) for panel, rows in sorted(groups.items())},
        "per_task": per_task,
    }


def analyze(batch_path: Path, answer_key_path: Path, manifest_path: Path,
            release_dir: Path, release_archive: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks = [
        (batch_path, "batch_sha256"),
        (answer_key_path, "answer_key_sha256"),
        (release_archive, "source_release_archive_sha256"),
    ]
    for path, manifest_key in checks:
        if _sha256(path) != manifest.get(manifest_key):
            raise ValueError(f"SHA-256 mismatch against manifest for {path.name}")
    if manifest.get("source_release") != "Open English WordNet 2025 Plus":
        raise ValueError("this baseline expects the OEWN 2025 Plus blind batch")
    batch_rows = load_jsonl(batch_path)
    answer_rows = json.loads(answer_key_path.read_text(encoding="utf-8"))
    if not isinstance(answer_rows, list):
        raise ValueError("answer key must be a JSON list")
    all_target_ids = [row.get("sense_id") for row in answer_rows if isinstance(row, dict)]
    if len(all_target_ids) != len(answer_rows) or any(not isinstance(x, str) or not x.startswith("oewn-") for x in all_target_ids):
        raise ValueError("answer key has missing or invalid OEWN sense IDs")
    if len(set(all_target_ids)) != len(all_target_ids):
        raise ValueError("answer key has duplicate target sense IDs")
    batch_by_task = {row.get("task_id"): row for row in batch_rows}
    target_ids = {
        row["sense_id"] for row in answer_rows
        if isinstance(row, dict)
        and batch_by_task.get(row.get("task_id"), {}).get("pos") == "n"
    }
    noun_index = build_noun_lemma_index(release_dir)
    taxonomy = load_direct_hypernyms(release_dir, target_ids)
    result = evaluate_batch(batch_rows, answer_rows, noun_index, taxonomy)
    result["inputs"] = {
        "batch_sha256": _sha256(batch_path),
        "answer_key_sha256": _sha256(answer_key_path),
        "release_archive_sha256": _sha256(release_archive),
        "release_name": manifest.get("source_release"),
        "release_date": manifest.get("source_release_date"),
    }
    result["limitations"] = [
        "The first lexical noun is a weak heuristic and may be an adjective used as a noun, an incidental noun, or the wrong head of a phrase.",
        "A match means only that at least one candidate sense is already linked as a direct OEWN hypernym; no candidate sense is disambiguated.",
        "OEWN taxonomy is a resource-relative comparison target, not independent human semantic gold; this experiment does not evaluate rule faithfulness, entailment, or NLI.",
        "Diagnostic-panel figures must not be interpreted as population estimates; report the random panel separately.",
    ]
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, default=DEFAULT_BATCH)
    parser.add_argument("--answer-key", type=Path, default=DEFAULT_ANSWER_KEY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        result = analyze(args.batch, args.answer_key, args.manifest, args.release_dir, args.release_archive)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["overall"], ensure_ascii=False, sort_keys=True))
    print(f"Diagnostic output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
