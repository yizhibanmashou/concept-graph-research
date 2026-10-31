"""Aggregate gold sense-key mapping failures in the fixed SemCor train sample.

Only documents assigned to the deterministic train split are opened. Output
contains counts and hashes only; no text, document names, sense keys, or IDs.
The audit never edits labels and never opens development or test documents.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from src.analysis.audit_wn30_oewn_sense_key_crosswalk import _load_oewn_sense_keys
from src.analysis.semcor_dev_pilot import build_index, observed_key
from src.analysis.semcor_train_mapping import digest, partition
from src.analysis.tiny_bert_wsd_data import select, stable_hash


def _train_sentence_records(raw: bytes):
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


def _normalize_graph_target(target: str, nodes: dict[str, Any]) -> str:
    if target not in nodes and not target.startswith("oewn-"):
        return "oewn-" + target
    return target


def classify_gold(
    lemma: str | None,
    lexsn: str | None,
    oewn_keys: dict[str, set[str]],
    nodes: dict[str, Any],
    wordnet_lemma_from_key,
) -> tuple[str, str | None]:
    """Return an aggregate-safe status and optional synset sensitivity status."""
    if not lemma or not lexsn or ";" in lexsn:
        return "invalid_gold", None
    key = f"{lemma}%{lexsn}".casefold()
    targets = oewn_keys.get(key, set())
    if len(targets) == 1:
        target = _normalize_graph_target(next(iter(targets)), nodes)
        if target not in nodes:
            return "target_absent_from_graph", None
        return "exact_unique_graph_target", None
    if len(targets) > 1:
        return "multiple_exact_oewn_targets", None

    try:
        wn_lemma = wordnet_lemma_from_key(f"{lemma}%{lexsn}")
    except Exception:
        return "no_exact_key_invalid_in_wn30", None

    member_keys = {item.key().casefold() for item in wn_lemma.synset().lemmas()}
    member_targets = set().union(*(oewn_keys.get(member, set()) for member in member_keys))
    matched_members = sum(bool(oewn_keys.get(member)) for member in member_keys)
    if matched_members == 0:
        return "no_exact_key_valid_wn30_no_oewn_member_match", "synset_no_oewn_member_match"
    if len(member_targets) > 1:
        return "no_exact_key_valid_wn30_oewn_split", "synset_member_keys_split"
    if matched_members == len(member_keys):
        return "no_exact_key_valid_wn30_oewn_complete_single", "synset_all_keys_one_oewn_target"
    return "no_exact_key_valid_wn30_oewn_partial_single", "synset_partial_keys_one_oewn_target"


def audit(
    nltk_data: Path,
    oewn_zip: Path,
    nodes_path: Path,
    prepared_metadata_path: Path,
) -> dict[str, Any]:
    import nltk

    nltk_data = nltk_data.resolve()
    nltk.data.path = [str(nltk_data)]
    from nltk.corpus import semcor, wordnet

    if wordnet.get_version() != "3.0":
        raise ValueError("expected WordNet 3.0 for SemCor source labels")

    with nodes_path.open(encoding="utf-8-sig", newline="") as stream:
        nodes = {row["synset_id"]: row for row in csv.DictReader(stream, delimiter="\t")}
    index = build_index(nodes.values())
    with zipfile.ZipFile(oewn_zip) as archive:
        oewn_keys = _load_oewn_sense_keys(archive)

    train_docs = partition(semcor.fileids())["train"]
    member_hash = hashlib.sha256()
    records: list[dict[str, Any]] = []
    with zipfile.ZipFile(nltk_data / "corpora" / "semcor.zip") as archive:
        for doc in train_docs:
            member_name = "semcor/" + doc
            raw = archive.read(member_name)
            member_hash.update(member_name.encode("utf-8"))
            member_hash.update(b"\0")
            member_hash.update(raw)
            for sentence_index, (words, annotated) in enumerate(_train_sentence_records(raw)):
                for token_index, (_word_index, token) in enumerate(annotated):
                    if token.get("rdf"):
                        continue
                    key = observed_key(token.text or "", token.get("pos", ""), wordnet.morphy)
                    if key is None or len(index.get(key, {})) < 2:
                        continue
                    instance = f"{doc}:{sentence_index}:{token_index}"
                    records.append({
                        "sample_id": stable_hash(instance),
                        "doc": doc,
                        "sentence": sentence_index,
                        "token": token_index,
                        "lemma": token.get("lemma"),
                        "lexsn": token.get("lexsn"),
                    })

    selected = select(records, 400)
    if len(selected) != 400:
        raise ValueError(f"expected 400 selected train records; found {len(selected)}")
    sample_ids_sha256 = stable_hash("\n".join(row["sample_id"] for row in selected))
    prepared = json.loads(prepared_metadata_path.read_text(encoding="utf-8"))
    expected_sample_hash = prepared["sample_ids_sha256"]["train"]
    if sample_ids_sha256 != expected_sample_hash:
        raise ValueError("reconstructed train sample does not match prepared metadata")

    outcomes: Counter[str] = Counter()
    synset_sensitivity: Counter[str] = Counter()
    for row in selected:
        outcome, sensitivity = classify_gold(
            row["lemma"], row["lexsn"], oewn_keys, nodes, wordnet.lemma_from_key
        )
        outcomes[outcome] += 1
        if sensitivity:
            synset_sensitivity[sensitivity] += 1

    if sum(outcomes.values()) != len(selected):
        raise ValueError("gold outcome counts do not reconcile to the selected sample")
    return {
        "schema": "t04-train-gold-mapping-audit/1",
        "train_rows": len(selected),
        "gold_mapping_outcomes": dict(sorted(outcomes.items())),
        "valid_wn30_no_exact_key_synset_sensitivity": dict(sorted(synset_sensitivity.items())),
        "wn30_version": wordnet.get_version(),
        "nltk_version": nltk.__version__,
        "train_sample_ids_sha256": sample_ids_sha256,
        "train_documents_read": len(train_docs),
        "dev_documents_read": 0,
        "test_documents_read": 0,
        "train_document_members_sha256": member_hash.hexdigest(),
        "prepared_metadata_sha256": digest(prepared_metadata_path),
        "oewn_entries_sha256": digest(oewn_zip),
        "nodes_tsv_sha256": digest(nodes_path),
        "limits": "Deterministic SemCor train sample only. Synset sensitivity is diagnostic, not a label repair or sense-level equivalence claim.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nltk-data", type=Path, required=True)
    parser.add_argument("--oewn-zip", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--prepared-metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.nltk_data, args.oewn_zip, args.nodes, args.prepared_metadata)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
