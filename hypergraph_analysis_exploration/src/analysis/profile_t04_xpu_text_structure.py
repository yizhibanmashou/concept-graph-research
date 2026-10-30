"""Profile pinned BERT-tiny gloss encoding plus T04 relation pooling.

Reads candidate_ids only from a frozen train JSON and uses local graph glosses
and rules. It never reads labels, contexts, dev or test examples. This measures
inference resource use, not training or WSD quality.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import time
from pathlib import Path
from typing import Any

from src.analysis.t04_relation_aggregation import aggregate_relation_views


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_train_candidate_ids(path: Path) -> tuple[list[str], int]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("train input must be a JSON array")
    ids: set[str] = set()
    occurrences = 0
    for row in rows:
        values = row.get("candidate_ids") if isinstance(row, dict) else None
        if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
            raise ValueError("every train row must contain nonempty candidate_ids")
        ids.update(values)
        occurrences += len(values)
    return sorted(ids), occurrences


def read_graph(nodes_path: Path, rules_path: Path, target_ids: set[str]) -> tuple[dict[str, str], dict[str, list[list[str]]]]:
    definitions: dict[str, str] = {}
    with nodes_path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if row.get("synset_id") in target_ids:
                definitions[row["synset_id"]] = row.get("definition", "")

    rules: dict[str, list[list[str]]] = {}
    with rules_path.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("head") in target_ids:
                rules[row["head"]] = row["clauses"]

    missing = sorted(target_ids - set(rules))
    if missing:
        raise ValueError(f"train candidates missing graph rules: {len(missing)}")
    node_ids = set(target_ids)
    for target_id, branches in rules.items():
        for branch in branches:
            node_ids.update(branch)

    # Read only the definitions needed by the train candidate graph.
    if node_ids - set(definitions):
        with nodes_path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                node_id = row.get("synset_id")
                if node_id in node_ids and node_id not in definitions:
                    definitions[node_id] = row.get("definition", "")
    missing_definitions = sorted(node_ids - set(definitions))
    if missing_definitions:
        raise ValueError(f"train graph nodes missing definitions: {len(missing_definitions)}")
    if any(not definitions[node_id].strip() for node_id in node_ids):
        raise ValueError("train graph contains an empty gloss")
    return definitions, rules


def pad_token_batch(
    encoded: list[list[int]], pad_id: int = 0, pad_to_multiple: int = 1
) -> tuple[list[list[int]], list[list[int]]]:
    if not encoded or any(not row for row in encoded):
        raise ValueError("token batch must contain nonempty sequences")
    if pad_to_multiple < 1:
        raise ValueError("pad_to_multiple must be positive")
    max_width = max(map(len, encoded))
    width = ((max_width + pad_to_multiple - 1) // pad_to_multiple) * pad_to_multiple
    input_ids = [row + [pad_id] * (width - len(row)) for row in encoded]
    attention_mask = [[1] * len(row) + [0] * (width - len(row)) for row in encoded]
    return input_ids, attention_mask


def make_gloss_batches(
    encoded_by_id: dict[str, list[int]], batch_size: int, order: str = "id"
) -> list[list[tuple[str, list[int]]]]:
    if batch_size < 1:
        raise ValueError("batch size must be positive")
    if order not in ("id", "length"):
        raise ValueError("batch order must be id or length")
    items = list(encoded_by_id.items())
    if order == "length":
        items.sort(key=lambda item: (len(item[1]), item[0]))
    else:
        items.sort(key=lambda item: item[0])
    return [items[start:start + batch_size] for start in range(0, len(items), batch_size)]


def profile(
    train_path: Path,
    nodes_path: Path,
    rules_path: Path,
    model_path: Path,
    out_path: Path,
    batch_size: int = 32,
    warmup_passes: int = 1,
    batch_order: str = "length",
    pad_to_multiple: int = 1,
    relation_warmup_candidates: int = 32,
) -> dict[str, Any]:
    import torch
    import transformers
    from tokenizers import BertWordPieceTokenizer
    from transformers import BertConfig, BertModel

    if batch_size < 1 or warmup_passes < 0 or pad_to_multiple < 1 or relation_warmup_candidates < 0:
        raise ValueError("batch size/pad multiple must be positive and warmup passes nonnegative")
    if not torch.xpu.is_available():
        raise ValueError("XPU is unavailable in this Conda environment")
    if not all((model_path / name).is_file() for name in ("config.json", "pytorch_model.bin", "vocab.txt")):
        raise ValueError("pinned model directory must contain config.json, pytorch_model.bin and vocab.txt")

    candidate_ids, candidate_occurrences = read_train_candidate_ids(train_path)
    definitions, rules = read_graph(nodes_path, rules_path, set(candidate_ids))
    all_node_ids = set(definitions)
    for branches in rules.values():
        for branch in branches:
            all_node_ids.update(branch)

    tokenizer = BertWordPieceTokenizer(str(model_path / "vocab.txt"), lowercase=True)
    tokenizer.enable_truncation(max_length=512)
    encoded_by_id = {node_id: tokenizer.encode(definitions[node_id]).ids for node_id in sorted(all_node_ids)}
    if any(not ids for ids in encoded_by_id.values()):
        raise ValueError("tokenizer produced an empty gloss sequence")
    sequence_lengths = [len(ids) for ids in encoded_by_id.values()]

    expected_model_hashes = {
        "config.json": "cf3179684f7c360dd6185962d480e7d426ceb8fe49f5db7b64bdc15dba0b8798",
        "pytorch_model.bin": "dab2c2bddcfb48ea430ef63fd76d46d67d704487844d967256a50dd7d7fd0a66",
        "vocab.txt": "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3",
    }
    model_hashes = {name: _sha256(model_path / name) for name in expected_model_hashes}
    if model_hashes != expected_model_hashes:
        raise ValueError("pinned model file SHA-256 mismatch")

    config = BertConfig.from_json_file(str(model_path / "config.json"))
    model = BertModel.from_pretrained(str(model_path.resolve()), config=config, local_files_only=True).to("xpu")
    model.eval()
    vectors: dict[str, Any] = {}
    batches = make_gloss_batches(encoded_by_id, batch_size, batch_order)

    def encode_batch(batch: list[tuple[str, list[int]]]) -> None:
        node_batch = [node_id for node_id, _ in batch]
        encoded = [ids for _, ids in batch]
        padded, masks = pad_token_batch(encoded, pad_to_multiple=pad_to_multiple)
        input_ids = torch.tensor(padded, dtype=torch.long, device="xpu")
        attention = torch.tensor(masks, dtype=torch.long, device="xpu")
        with torch.inference_mode():
            output = model(input_ids=input_ids, attention_mask=attention).last_hidden_state[:, 0]
        vectors.update({node_id: vector for node_id, vector in zip(node_batch, output)})

    warmup_started = time.perf_counter()
    for _ in range(warmup_passes):
        for batch in batches:
            encode_batch(batch)
    vectors.clear()
    torch.xpu.synchronize()
    warmup_seconds = time.perf_counter() - warmup_started
    baseline_after_model_bytes = torch.xpu.memory_allocated()
    torch.xpu.reset_peak_memory_stats()
    encoder_started = time.perf_counter()
    padded_token_count = 0
    actual_token_count = 0
    for batch in batches:
        node_batch = [node_id for node_id, _ in batch]
        encoded = [ids for _, ids in batch]
        padded, masks = pad_token_batch(encoded, pad_to_multiple=pad_to_multiple)
        padded_token_count += sum(len(row) for row in padded)
        actual_token_count += sum(len(row) for row in encoded)
        input_ids = torch.tensor(padded, dtype=torch.long, device="xpu")
        attention = torch.tensor(masks, dtype=torch.long, device="xpu")
        with torch.inference_mode():
            output = model(input_ids=input_ids, attention_mask=attention).last_hidden_state[:, 0]
        vectors.update({node_id: vector for node_id, vector in zip(node_batch, output)})
    torch.xpu.synchronize()
    encoder_seconds = time.perf_counter() - encoder_started
    encoder_peak = torch.xpu.max_memory_allocated()
    encoder_peak_increment = max(0, encoder_peak - baseline_after_model_bytes)

    for target_id in candidate_ids[:relation_warmup_candidates]:
        aggregate_relation_views(vectors, target_id, rules[target_id])
    torch.xpu.synchronize()
    torch.xpu.reset_peak_memory_stats()
    aggregation_baseline_bytes = torch.xpu.memory_allocated()
    aggregation_started = time.perf_counter()
    finite = True
    checksum = 0.0
    for target_id in candidate_ids:
        pooled = aggregate_relation_views(vectors, target_id, rules[target_id])
        for condition in "ABCD":
            finite = finite and bool(torch.isfinite(pooled[condition]).all().item())
        checksum += float(pooled["D"][0].item())
    torch.xpu.synchronize()
    aggregation_seconds = time.perf_counter() - aggregation_started
    aggregation_peak = torch.xpu.max_memory_allocated()
    del model, vectors
    torch.xpu.empty_cache()

    result = {
        "schema": "t04-xpu-text-structure-profile/1",
        "device_name": torch.xpu.get_device_name(0),
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "python_version": platform.python_version(),
        "model_revision": "prajjwal1/bert-tiny@6f75de8b60a9f8a2fdf7b69cbd86d9e64bcb3837",
        "model_sha256": model_hashes,
        "train_candidate_unique_count": len(candidate_ids),
        "train_candidate_occurrences": candidate_occurrences,
        "unique_gloss_node_count": len(encoded_by_id),
        "gloss_tokens": {
            "actual_unpadded": actual_token_count,
            "padded": padded_token_count,
            "padding_fraction": 1 - actual_token_count / padded_token_count,
            "max_sequence_length": max(sequence_lengths),
            "batch_size": batch_size,
            "batch_order": batch_order,
            "warmup_passes": warmup_passes,
            "warmup_batches": warmup_passes * len(batches),
            "pad_to_multiple": pad_to_multiple,
            "warmup_seconds": warmup_seconds,
        },
        "text_encoder": {
            "wall_clock_seconds": encoder_seconds,
            "nodes_per_second": len(encoded_by_id) / encoder_seconds if encoder_seconds else None,
            "baseline_allocated_bytes_after_model_load": baseline_after_model_bytes,
            "peak_allocated_bytes_after_reset": encoder_peak,
            "peak_increment_bytes": encoder_peak_increment,
        },
        "relation_aggregation": {
            "wall_clock_seconds": aggregation_seconds,
            "candidates_per_second": len(candidate_ids) / aggregation_seconds if aggregation_seconds else None,
            "warmup_candidates": min(relation_warmup_candidates, len(candidate_ids)),
            "baseline_allocated_bytes": aggregation_baseline_bytes,
            "peak_allocated_bytes_after_reset": aggregation_peak,
            "peak_increment_bytes": max(0, aggregation_peak - aggregation_baseline_bytes),
            "finite_output_check": finite and checksum == checksum,
        },
        "inputs_sha256": {
            "train_json": _sha256(train_path),
            "nodes_tsv": _sha256(nodes_path),
            "hypergraph_rules_jsonl": _sha256(rules_path),
        },
        "limits": (
            "Inference-only resource profile over train candidate IDs and local graph glosses/rules. No labels, contexts, "
            "dev/test examples or training updates are read. Does not measure optimizer/backpropagation or WSD quality."
        ),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--warmup-passes", type=int, default=1)
    parser.add_argument("--batch-order", choices=("id", "length"), default="length")
    parser.add_argument("--pad-to-multiple", type=int, default=1)
    parser.add_argument("--relation-warmup-candidates", type=int, default=32)
    args = parser.parse_args()
    result = profile(args.train, args.nodes, args.rules, args.model, args.out, args.batch_size,
                     args.warmup_passes, args.batch_order, args.pad_to_multiple,
                     args.relation_warmup_candidates)
    print(json.dumps({
        "candidate_count": result["train_candidate_unique_count"],
        "gloss_node_count": result["unique_gloss_node_count"],
        "text_encoder": result["text_encoder"],
        "relation_aggregation": result["relation_aggregation"],
        "gloss_tokens": result["gloss_tokens"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
