"""One-step supervised A/B/C/D microbatch on train-only WSD records.

This is an engineering smoke, not a performance experiment. It selects a
fixed seeded subset from the supplied train JSON, uses the same A condition
context/candidate token sequences for all variants, and changes only the
candidate's graph relation pooling. It never opens dev/test files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from src.analysis.profile_t04_xpu_text_structure import (
    make_gloss_batches,
    pad_token_batch,
    read_graph,
)
from src.analysis.t04_relation_aggregation import aggregate_relation_views
from src.analysis.tiny_bert_wsd_train import digest, validate


EXPECTED_MODEL_HASHES = {
    "config.json": "cf3179684f7c360dd6185962d480e7d426ceb8fe49f5db7b64bdc15dba0b8798",
    "pytorch_model.bin": "dab2c2bddcfb48ea430ef63fd76d46d67d704487844d967256a50dd7d7fd0a66",
    "vocab.txt": "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3",
}


def run_microbatch(
    data_dir: Path,
    nodes_path: Path,
    rules_path: Path,
    model_path: Path,
    examples: int = 2,
    seed: int = 17,
    graph_batch_size: int = 32,
) -> dict[str, Any]:
    import torch
    import transformers
    from tokenizers import BertWordPieceTokenizer
    from transformers import BertConfig, BertModel

    if not torch.xpu.is_available():
        raise ValueError("XPU is unavailable in this Conda environment")
    if examples < 1 or graph_batch_size < 1:
        raise ValueError("examples and graph batch size must be positive")

    train_path = data_dir / "train.json"
    metadata_path = data_dir / "metadata.json"
    train = json.loads(train_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if digest(model_path / "vocab.txt") != metadata["inputs_sha256"]["vocab.txt"]:
        raise ValueError("model vocabulary differs from prepared training data")
    model_hashes = {name: digest(model_path / name) for name in EXPECTED_MODEL_HASHES}
    if model_hashes != EXPECTED_MODEL_HASHES:
        raise ValueError("pinned model SHA-256 mismatch")
    train_ids = validate(train, metadata["joint_budget"])
    eligible = [row for row in train if row["label"] >= 0]
    if examples > len(eligible):
        raise ValueError("requested examples exceed covered train rows")
    selected = random.Random(seed).sample(eligible, examples)

    # The serialized A input is the common context + raw candidate gloss base.
    # All four variants use it unchanged; only graph pooling differs.
    candidate_ids = sorted({
        candidate_id for row in selected for candidate_id in row["scorable_candidate_ids"]
    })
    definitions, rules = read_graph(nodes_path, rules_path, set(candidate_ids))
    graph_node_ids = set(candidate_ids)
    for target_id in candidate_ids:
        for branch in rules[target_id]:
            graph_node_ids.update(branch)

    tokenizer = BertWordPieceTokenizer(str(model_path / "vocab.txt"), lowercase=True)
    tokenizer.enable_truncation(max_length=512)
    encoded = {
        node_id: tokenizer.encode(definitions[node_id]).ids
        for node_id in graph_node_ids
    }
    if any(not ids for ids in encoded.values()):
        raise ValueError("empty graph gloss after tokenization")

    torch.manual_seed(seed)
    torch.xpu.manual_seed_all(seed)
    config = BertConfig.from_json_file(str(model_path / "config.json"))
    batch_plan = make_gloss_batches(encoded, graph_batch_size, order="length")
    results: dict[str, Any] = {}

    for condition in "ABCD":
        # Reset the RNG so each ablation begins with identical pretrained and
        # task-head parameters and the same dropout stream.
        torch.manual_seed(seed)
        torch.xpu.manual_seed_all(seed)
        encoder = BertModel.from_pretrained(
            str(model_path.resolve()), config=config, local_files_only=True
        ).to("xpu")
        head = torch.nn.Linear(config.hidden_size * 3, 1).to("xpu")
        encoder.train()
        head.train()
        optimizer = torch.optim.AdamW(
            [*encoder.parameters(), *head.parameters()], lr=2e-5
        )

        torch.xpu.reset_peak_memory_stats()
        optimizer.zero_grad(set_to_none=True)
        node_vectors: dict[str, Any] = {}
        for batch in batch_plan:
            node_batch = [node_id for node_id, _ in batch]
            token_rows = [ids for _, ids in batch]
            padded, masks = pad_token_batch(token_rows)
            input_ids = torch.tensor(padded, dtype=torch.long, device="xpu")
            attention = torch.tensor(masks, dtype=torch.long, device="xpu")
            hidden = encoder(input_ids=input_ids, attention_mask=attention).last_hidden_state[:, 0]
            node_vectors.update({key: hidden[i] for i, key in enumerate(node_batch)})

        graph_views = {
            target_id: aggregate_relation_views(node_vectors, target_id, rules[target_id])
            for target_id in candidate_ids
        }
        flat_inputs = [
            values
            for row in selected
            for values in row["inputs"]["A"]
        ]
        flat_candidates = [
            candidate_id
            for row in selected
            for candidate_id in row["scorable_candidate_ids"]
        ]
        flat_tensor = torch.tensor(flat_inputs, dtype=torch.long, device="xpu")
        attention = flat_tensor.ne(0).long()
        separators = flat_tensor.eq(102).long()
        segments = ((separators.cumsum(-1) - separators) > 0).long() * attention
        cross_vectors = encoder(
            input_ids=flat_tensor,
            attention_mask=attention,
            token_type_ids=segments,
        ).last_hidden_state[:, 0]
        structure_vectors = torch.stack([
            graph_views[candidate_id][condition] for candidate_id in flat_candidates
        ])
        logits = head(torch.cat([cross_vectors, structure_vectors], dim=-1)).squeeze(-1)

        losses = []
        offset = 0
        for row in selected:
            count = len(row["scorable_candidate_ids"])
            target_logits = logits[offset:offset + count]
            offset += count
            losses.append(torch.nn.functional.cross_entropy(
                target_logits.unsqueeze(0),
                torch.tensor([row["label"]], dtype=torch.long, device="xpu"),
            ))
        loss = torch.stack(losses).mean()
        if not torch.isfinite(loss):
            raise RuntimeError("non-finite training loss")
        loss.backward()
        gradients = [
            parameter.grad for parameter in [*encoder.parameters(), *head.parameters()]
            if parameter.grad is not None
        ]
        if not gradients or not all(torch.isfinite(gradient).all() for gradient in gradients):
            raise RuntimeError("missing or non-finite gradients")
        optimizer.step()
        torch.xpu.synchronize()
        results[condition] = {
            "train_examples": len(selected),
            "candidate_count": len(flat_candidates),
            "graph_node_count": len(graph_node_ids),
            "branch_count": sum(len(rules[target_id]) for target_id in candidate_ids),
            "loss_before_step": float(loss.detach().cpu()),
            "gradient_tensors": len(gradients),
            "peak_allocated_bytes": int(torch.xpu.max_memory_allocated()),
            "optimizer_step": "ok",
        }
        del encoder, head, optimizer, node_vectors, graph_views
        torch.xpu.empty_cache()

    return {
        "device": torch.xpu.get_device_name(0),
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "seed": seed,
        "selected_train_sample_ids_sha256": hashlib.sha256(
            "\n".join(sorted(row["sample_id"] for row in selected)).encode()
        ).hexdigest(),
        "train_sha256": digest(train_path),
        "model_sha256": model_hashes,
        "base_input": "A context+raw-gloss sequence shared unchanged by A/B/C/D",
        "results": results,
        "limits": "One supervised optimizer step on a seeded train-only microbatch; no dev/test; not an effect estimate.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--examples", type=int, default=2)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--graph-batch-size", type=int, default=32)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run_microbatch(
        args.data, args.nodes, args.rules, args.model,
        examples=args.examples, seed=args.seed,
        graph_batch_size=args.graph_batch_size,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
