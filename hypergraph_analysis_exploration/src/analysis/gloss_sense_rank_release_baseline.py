"""Rank noun senses for the first lexical genus candidate using gloss context.

This release-wide baseline uses only gloss text and noun synset definitions to
rank candidate senses. Direct hypernym links are consulted only after ranking
to report a same-resource proxy; they are never features of the ranker.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.analysis.gloss_genus_baseline import (
    DEFAULT_MANIFEST,
    DEFAULT_RELEASE_ARCHIVE,
    DEFAULT_RELEASE_DIR,
    TOKEN_RE,
    build_noun_lemma_index,
    find_first_noun_candidate,
)
from src.analysis.gloss_genus_release_baseline import (
    load_noun_synsets,
    verify_extracted_inputs,
)


RANKER_VERSION = "first-noun-candidate-idf-gloss-cosine/1"
STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "if", "as", "at", "by", "for",
    "from", "in", "into", "of", "on", "onto", "out", "over", "per", "to",
    "up", "with", "without", "about", "after", "against", "among", "around",
    "before", "between", "during", "through", "under", "until", "while", "within",
    "is", "are", "was", "were", "be", "been", "being", "has", "have", "had",
    "do", "does", "did", "can", "could", "may", "might", "must", "shall", "should",
    "will", "would", "that", "which", "who", "whom", "whose", "what", "when", "where",
    "why", "how", "this", "these", "those", "it", "its", "their", "them", "they",
    "he", "she", "his", "her", "we", "you", "your", "one", "some", "any", "each",
    "all", "another", "other", "such", "more", "most", "less", "least", "very", "often",
    "usually", "typically", "especially", "also", "rather", "than", "like", "used", "use",
})
TOP_K = (1, 3, 5, 10)


def content_tokens(text: str) -> set[str]:
    """Return a small, deterministic set of content-word tokens."""
    return {
        match.group(0).casefold()
        for match in TOKEN_RE.finditer(text)
        if len(match.group(0)) > 1 and match.group(0).casefold() not in STOPWORDS
    }


def build_idf(records: list[dict[str, Any]]) -> tuple[dict[str, float], dict[str, set[str]]]:
    """Build release-local IDF weights and one token set per noun synset."""
    tokens_by_synset: dict[str, set[str]] = {}
    document_frequency: Counter[str] = Counter()
    for record in records:
        tokens: set[str] = set()
        for definition in record["definitions"]:
            tokens.update(content_tokens(definition))
        tokens_by_synset[record["synset_id"]] = tokens
        document_frequency.update(tokens)
    document_count = len(records)
    idf = {
        token: math.log((document_count + 1) / (frequency + 1)) + 1.0
        for token, frequency in document_frequency.items()
    }
    return idf, tokens_by_synset


def _cosine_idf(left: set[str], right: set[str], idf: dict[str, float]) -> float:
    """Cosine similarity over binary TF-IDF vectors."""
    shared = left & right
    if not shared:
        return 0.0
    dot = sum(idf[token] ** 2 for token in shared)
    left_norm = math.sqrt(sum(idf[token] ** 2 for token in left))
    right_norm = math.sqrt(sum(idf[token] ** 2 for token in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def rank_candidate_senses(
    gloss: str,
    target_members: list[str],
    candidate: dict[str, Any],
    idf: dict[str, float],
    tokens_by_synset: dict[str, set[str]],
) -> dict[str, Any]:
    """Rank candidate senses by overlap with context outside target/candidate lemmas.

    The returned scores depend only on text, IDF weights, and candidate sense
    definitions. No target hypernym labels or graph structure enter this step.
    """
    span = candidate["span"]
    context = gloss[:span["start"]] + " " + gloss[span["end"]:]
    context_tokens = content_tokens(context)
    masked_lemmas = [candidate["lemma"], *target_members]
    for lemma in masked_lemmas:
        context_tokens.difference_update(content_tokens(lemma))

    scored = []
    for synset_id in candidate["candidate_synset_ids"]:
        if synset_id not in tokens_by_synset:
            raise ValueError(f"candidate synset missing from noun definitions: {synset_id}")
        scored.append({
            "synset_id": synset_id,
            "score": _cosine_idf(context_tokens, tokens_by_synset[synset_id], idf),
        })
    scored.sort(key=lambda row: (-row["score"], row["synset_id"]))

    positive = [row for row in scored if row["score"] > 0.0]
    if not positive:
        return {
            "rankable_sense_count": 0,
            "decision": "abstain_no_context_overlap",
            "selected_synset_id": None,
            "top_score": 0.0,
            "top_tie_size": 0,
            "ranked_senses": scored,
        }

    top_score = positive[0]["score"]
    top_group = [row for row in positive if math.isclose(row["score"], top_score, rel_tol=0.0, abs_tol=1e-12)]
    if len(top_group) != 1:
        decision = "abstain_tied_top_score"
        selected = None
    else:
        decision = "selected_unique_top_sense"
        selected = top_group[0]["synset_id"]

    return {
        "rankable_sense_count": len(positive),
        "decision": decision,
        "selected_synset_id": selected,
        "top_score": top_score,
        "top_tie_size": len(top_group),
        "ranked_senses": scored,
    }


def _rank_of_first_match(ranked: list[dict[str, Any]], matching_ids: set[str]) -> int | None:
    """Return the best rank interval's starting rank, treating score ties fairly."""
    rank_start = 1
    index = 0
    while index < len(ranked):
        score = ranked[index]["score"]
        end = index + 1
        while end < len(ranked) and math.isclose(ranked[end]["score"], score, rel_tol=0.0, abs_tol=1e-12):
            end += 1
        if score > 0.0 and any(row["synset_id"] in matching_ids for row in ranked[index:end]):
            return rank_start
        rank_start += end - index
        index = end
    return None


def evaluate_synsets(records: list[dict[str, Any]], noun_index: dict[str, list[str]]) -> dict[str, Any]:
    """Evaluate context-ranked sense decisions using direct hypernyms post hoc."""
    idf, tokens_by_synset = build_idf(records)
    by_lexname: dict[str, list[dict[str, Any]]] = defaultdict(list)
    rows = []
    no_hypernym_instances = 0
    definition_instance_count = 0

    for record in records:
        for definition_index, gloss in enumerate(record["definitions"]):
            definition_instance_count += 1
            if not record["hypernyms"]:
                no_hypernym_instances += 1
                continue
            candidate = find_first_noun_candidate(gloss, record["members"], noun_index)
            if candidate is None:
                row = {"status": "no_lexical_candidate", "ranker": None}
            else:
                ranking = rank_candidate_senses(
                    gloss, record["members"], candidate, idf, tokens_by_synset,
                )
                matching_ids = set(candidate["candidate_synset_ids"]) & set(record["hypernyms"])
                matched_rank_start = _rank_of_first_match(ranking["ranked_senses"], matching_ids)
                selected_match = ranking["selected_synset_id"] in record["hypernyms"] if ranking["selected_synset_id"] else False
                row = {
                    "status": "candidate_matches_direct_hypernym" if matching_ids else "candidate_not_direct_hypernym",
                    "candidate_sense_count": len(candidate["candidate_synset_ids"]),
                    "candidate_pool_match_count": len(matching_ids),
                    "ranker": ranking,
                    "unique_top1_match": selected_match,
                    "matched_rank_start": matched_rank_start,
                }
            row["lexname"] = record["lexname"]
            row["definition_index"] = definition_index
            rows.append(row)
            by_lexname[record["lexname"]].append(row)

    def summarize(panel_rows: list[dict[str, Any]]) -> dict[str, Any]:
        eligible = len(panel_rows)
        counts = Counter(row["status"] for row in panel_rows)
        candidate_rows = [row for row in panel_rows if row["ranker"] is not None]
        rankable_rows = [row for row in candidate_rows if row["ranker"]["rankable_sense_count"] > 0]
        decisions = [row for row in candidate_rows if row["ranker"]["decision"] == "selected_unique_top_sense"]
        matched_candidate_pools = [row for row in candidate_rows if row["candidate_pool_match_count"] > 0]
        top1_correct = sum(bool(row["unique_top1_match"]) for row in decisions)
        retrieval = {}
        for k in TOP_K:
            hit_count = sum(
                row["matched_rank_start"] is not None and row["matched_rank_start"] <= k
                for row in candidate_rows
            )
            conditional_hit_count = sum(
                row["matched_rank_start"] is not None and row["matched_rank_start"] <= k
                for row in matched_candidate_pools
            )
            retrieval[str(k)] = {
                "hits_over_eligible": hit_count / eligible if eligible else None,
                "hits_over_pools_with_any_direct_hypernym": (
                    conditional_hit_count / len(matched_candidate_pools) if matched_candidate_pools else None
                ),
                "hit_count": hit_count,
                "conditional_denominator": len(matched_candidate_pools),
            }
        ranker_statuses = Counter(row["ranker"]["decision"] for row in candidate_rows)
        return {
            "eligible_definition_instances": eligible,
            "status_counts": dict(sorted(counts.items())),
            "candidate_coverage": len(candidate_rows) / eligible if eligible else None,
            "candidate_pool_any_sense_match_rate": counts["candidate_matches_direct_hypernym"] / len(candidate_rows) if candidate_rows else None,
            "rankable_context_coverage_over_eligible": len(rankable_rows) / eligible if eligible else None,
            "ranker_decision_counts": dict(sorted(ranker_statuses.items())),
            "unique_top1_decision_coverage_over_eligible": len(decisions) / eligible if eligible else None,
            "unique_top1_match_rate_among_decisions": top1_correct / len(decisions) if decisions else None,
            "unique_top1_matches_over_eligible": top1_correct / eligible if eligible else None,
            "top_k_retrieval": retrieval,
        }

    overall = summarize(rows)
    return {
        "ranker_version": RANKER_VERSION,
        "method": (
            "Select the same first exact noun-lemma candidate as Phase 9/11. Remove the candidate span and target-member tokens; "
            "rank its noun senses by binary TF-IDF cosine between each sense's release-local definition token set and the remaining "
            "target-gloss context. IDF is computed over noun synset definition documents in this release. Abstain when there is no "
            "positive overlap or the highest score is tied. Direct hypernym IDs are used only for post-hoc evaluation, never ranking."
        ),
        "evaluation_target": (
            "Whether a selected or ranked candidate sense is listed as a direct hypernym of the target in the same OEWN release. "
            "This remains an internal resource-alignment proxy, not semantic gold or evidence that the gloss entails the relation."
        ),
        "noun_synset_count": len(records),
        "definition_instance_count": definition_instance_count,
        "definition_instances_without_direct_hypernym": no_hypernym_instances,
        "idf_document_count": len(tokens_by_synset),
        "overall": overall,
        "by_lexname": {key: summarize(panel_rows) for key, panel_rows in sorted(by_lexname.items())},
        "source_gloss_text_emitted": False,
        "per_definition_results_emitted": False,
        "limitations": [
            "This is a lexical TF-IDF overlap baseline without stemming, contextual POS tagging, phrase-head parsing, embeddings, or learned WSD.",
            "The candidate lemma is still selected by the same early exact-match heuristic; the experiment only adds a transparent sense-ranking stage.",
            "Candidate definitions and evaluation hypernym links come from the same OEWN release, so this is not independent semantic validation.",
            "A missing lexical overlap is an abstention, not evidence that no candidate sense is correct.",
            "The experiment does not generate formal rules or evaluate source-span faithfulness, Horn proof correctness, or NLI.",
        ],
    }


def analyze_release(release_dir: Path, release_archive: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    from src.analysis.gloss_genus_baseline import _sha256

    archive_hash = _sha256(release_archive)
    if archive_hash != manifest.get("source_release_archive_sha256"):
        raise ValueError("release archive SHA-256 does not match the phase7 manifest")
    if manifest.get("source_release") != "Open English WordNet 2025 Plus":
        raise ValueError("expected the pinned Open English WordNet 2025 Plus release")
    extracted_verification = verify_extracted_inputs(release_dir, release_archive)
    records = load_noun_synsets(release_dir)
    noun_index = build_noun_lemma_index(release_dir)
    result = evaluate_synsets(records, noun_index)
    result["inputs"] = {
        "release_name": manifest.get("source_release"),
        "release_date": manifest.get("source_release_date"),
        "release_archive_sha256": archive_hash,
        **extracted_verification,
    }
    result["reproducibility_note"] = (
        "All extracted entries/noun files were byte-verified against the pinned archive. "
        "The aggregate extracted_inputs_sha256 fingerprints filenames and file digests without exposing glosses."
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-dir", type=Path, default=DEFAULT_RELEASE_DIR)
    parser.add_argument("--release-archive", type=Path, default=DEFAULT_RELEASE_ARCHIVE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        parser.error("output already exists; pass --force to replace it")
    try:
        result = analyze_release(args.release_dir, args.release_archive, args.manifest)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["overall"], ensure_ascii=False, sort_keys=True))
    print(f"Scanned {result['noun_synset_count']} noun synsets / {result['definition_instance_count']} definitions")
    print(f"Aggregate report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
