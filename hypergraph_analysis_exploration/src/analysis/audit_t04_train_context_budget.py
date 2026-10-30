"""Train-only sensitivity audit for target-centered WSD context budgets.

Reconstructs the fixed SemCor train sample and compares bounded context
windows. Output contains aggregates and hashes only. No dev/test documents,
labels, contexts, or identifiers are written.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from src.analysis.semcor_dev_pilot import build_index, observed_key
from src.analysis.semcor_train_mapping import digest, partition
from src.analysis.tiny_bert_wsd_data import encode_target_centered_context, select, stable_hash


def _sentence_records(raw: bytes):
    root = ElementTree.fromstring(raw)
    for sentence in root.iter("s"):
        words = list(sentence)
        surfaces = [(word.text or "").replace("_", " ") for word in words]
        annotated = [
            (position, word)
            for position, word in enumerate(words)
            if word.tag == "wf" and word.get("wnsn") and word.get("lexsn")
        ]
        yield surfaces, annotated


def _sequence_parts(sequence: list[int]) -> tuple[list[int], list[int]]:
    first_sep = sequence.index(102, 1)
    second_sep = sequence.index(102, first_sep + 1)
    return sequence[1:first_sep], sequence[first_sep + 1:second_sep]


def audit(
    nltk_data: Path,
    nodes_path: Path,
    train_path: Path,
    metadata_path: Path,
    vocab_path: Path,
    budgets: tuple[int, ...] = (32, 64, 96, 128, 256, 512),
) -> dict[str, Any]:
    import nltk
    from nltk.corpus import semcor, wordnet
    from tokenizers import BertWordPieceTokenizer

    nltk_data = nltk_data.resolve()
    nltk.data.path = [str(nltk_data)]
    if wordnet.get_version() != "3.0":
        raise ValueError("expected WordNet 3.0")
    prepared = json.loads(train_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    width = metadata["joint_budget"]
    with nodes_path.open(encoding="utf-8-sig", newline="") as stream:
        node_rows = list(csv.DictReader(stream, delimiter="\t"))
    graph_index = build_index(node_rows)
    tokenizer = BertWordPieceTokenizer(str(vocab_path), lowercase=True)
    marker_ids = metadata["target_marker_ids"]
    if (tokenizer.token_to_id("[unused0]"), tokenizer.token_to_id("[unused1]")) != (
        marker_ids["start"], marker_ids["end"]
    ):
        raise ValueError("prepared target markers differ from the pinned vocabulary")

    documents = partition(semcor.fileids())["train"]
    records: list[dict[str, Any]] = []
    train_member_hash = hashlib.sha256()
    with zipfile.ZipFile(nltk_data / "corpora" / "semcor.zip") as archive:
        for doc in documents:
            member_name = "semcor/" + doc
            raw = archive.read(member_name)
            train_member_hash.update(member_name.encode("utf-8"))
            train_member_hash.update(b"\0")
            train_member_hash.update(raw)
            for sentence_i, (words, annotated) in enumerate(_sentence_records(raw)):
                for token_i, (word_i, token) in enumerate(annotated):
                    if token.get("rdf"):
                        continue
                    observed = observed_key(token.text or "", token.get("pos", ""), wordnet.morphy)
                    if observed is None or len(graph_index.get(observed, {})) < 2:
                        continue
                    instance = f"{doc}:{sentence_i}:{token_i}"
                    records.append({
                        "sample_id": stable_hash(instance),
                        "doc": doc,
                        "sentence": sentence_i,
                        "token": token_i,
                        "word_index": word_i,
                        "surface": (token.text or "").replace("_", " "),
                        "words": words,
                    })
    selected = select(records, 400)
    if len(selected) != len(prepared):
        raise ValueError("reconstructed train target count differs from prepared data")
    if [row["sample_id"] for row in selected] != [row["sample_id"] for row in prepared]:
        raise ValueError("reconstructed train targets differ from prepared data order")
    expected_hash = metadata["sample_ids_sha256"]["train"]
    observed_hash = stable_hash("\n".join(row["sample_id"] for row in selected))
    if observed_hash != expected_hash:
        raise ValueError("reconstructed sample hash differs from prepared metadata")

    def encode(text: str) -> list[int]:
        return tokenizer.encode(text, add_special_tokens=False).ids

    results: dict[str, Any] = {}
    for budget in budgets:
        context_lengths: list[int] = []
        truncated = marker_errors = total_pairs = over_budget_pairs = 0
        total_tokens = context_token_occurrences = max_sequence = 0
        over_model_position = 0
        sensitivity_width = metadata["candidate_budget"] + budget + 2
        for target, row in zip(selected, prepared):
            context, window = encode_target_centered_context(
                target["words"], target["word_index"], target["surface"],
                encode, marker_ids["start"], marker_ids["end"], maximum=budget,
            )
            context_lengths.append(len(context))
            truncated += bool(window["sentence_truncated"])
            marker_errors += int(context.count(marker_ids["start"]) != 1 or
                                 context.count(marker_ids["end"]) != 1)
            candidate_counts = {len(row["inputs"][version]) for version in "ABCD"}
            if len(candidate_counts) != 1:
                raise ValueError("A/B/C/D candidate counts differ")
            total_pairs += len(row["inputs"]["A"])
            for version in "ABCD":
                for sequence in row["inputs"][version]:
                    old_context, candidate = _sequence_parts(sequence)
                    if budget == metadata["context_budget"] and context != old_context:
                        raise ValueError("reconstructed context differs from prepared input")
                    sequence_length = len(context) + len(candidate) + 3
                    total_tokens += sequence_length
                    context_token_occurrences += len(context)
                    max_sequence = max(max_sequence, sequence_length)
                    over_budget_pairs += sequence_length > sensitivity_width
                    over_model_position += sequence_length > 512
        ordered = sorted(context_lengths)
        results[str(budget)] = {
            "targets": len(selected),
            "candidate_pairs": total_pairs,
            "condition_candidate_pairs": total_pairs * 4,
            "sentence_windows_truncated": truncated,
            "target_marker_errors": marker_errors,
            "context_piece_min_median_p90_max": [
                ordered[0], ordered[len(ordered) // 2],
                ordered[int(.9 * (len(ordered) - 1))], ordered[-1],
            ],
            "candidate_pairs_over_joint_budget": over_budget_pairs,
            "joint_budget_for_this_context_cap": sensitivity_width,
            "condition_pairs_over_model_position_limit": over_model_position,
            "candidate_pair_token_occurrences": total_tokens,
            "repeated_context_token_occurrences": context_token_occurrences,
            "max_joint_sequence_length": max_sequence,
        }
    return {
        "schema": "t04-train-context-budget-audit/1",
        "budgets": results,
        "prepared_joint_budget": width,
        "candidate_budget": metadata["candidate_budget"],
        "model_position_limit": 512,
        "train_rows": len(prepared),
        "train_sample_ids_sha256": observed_hash,
        "train_documents_read": len(documents),
        "dev_documents_read": 0,
        "test_documents_read": 0,
        "train_document_members_sha256": train_member_hash.hexdigest(),
        "train_json_sha256": digest(train_path),
        "metadata_sha256": digest(metadata_path),
        "nodes_sha256": digest(nodes_path),
        "vocab_sha256": digest(vocab_path),
        "nltk_version": nltk.__version__,
        "wordnet_version": wordnet.get_version(),
        "limits": "Train-only context and resource sensitivity; no model-quality or semantic-effect estimate.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nltk-data", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--vocab", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.nltk_data, args.nodes, args.train, args.metadata, args.vocab)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
