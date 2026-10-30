"""Run a one-candidate train-only autograd/optimizer smoke on XPU.

This deliberately uses a surrogate squared-norm objective. It verifies that
the pinned gloss encoder and A/B/C/D pooling can backpropagate and update
parameters on the local device; it is not WSD training or an evaluation.
Only candidate IDs from the supplied training JSON are read. Labels, contexts,
development examples, and test examples are never accessed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.analysis.profile_t04_xpu_text_structure import (
    pad_token_batch,
    read_graph,
    read_train_candidate_ids,
)
from src.analysis.t04_relation_aggregation import aggregate_relation_views


def run_smoke(
    train_path: Path,
    nodes_path: Path,
    rules_path: Path,
    model_path: Path,
    target_id: str | None = None,
) -> dict[str, Any]:
    import torch
    from tokenizers import BertWordPieceTokenizer
    from transformers import BertConfig, BertModel

    if not torch.xpu.is_available():
        raise ValueError("XPU is unavailable in this Conda environment")

    candidate_ids, _ = read_train_candidate_ids(train_path)
    definitions, rules = read_graph(nodes_path, rules_path, set(candidate_ids))
    if target_id is None:
        target_id = candidate_ids[0]
    if target_id not in set(candidate_ids):
        raise ValueError("target ID must occur in train candidate_ids")

    branches = rules[target_id]
    node_ids = sorted({target_id, *(node_id for branch in branches for node_id in branch)})
    tokenizer = BertWordPieceTokenizer(str(model_path / "vocab.txt"), lowercase=True)
    tokenizer.enable_truncation(max_length=512)
    encoded = [tokenizer.encode(definitions[node_id]).ids for node_id in node_ids]
    padded, masks = pad_token_batch(encoded)
    input_ids = torch.tensor(padded, dtype=torch.long, device="xpu")
    attention = torch.tensor(masks, dtype=torch.long, device="xpu")

    config = BertConfig.from_json_file(str(model_path / "config.json"))
    model = BertModel.from_pretrained(
        str(model_path.resolve()), config=config, local_files_only=True
    ).to("xpu")
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
    torch.xpu.reset_peak_memory_stats()
    optimizer.zero_grad(set_to_none=True)

    hidden = model(input_ids=input_ids, attention_mask=attention).last_hidden_state[:, 0]
    vectors = {node_id: hidden[index] for index, node_id in enumerate(node_ids)}
    views = aggregate_relation_views(vectors, target_id, branches)
    # A surrogate loss is used only to exercise autograd; it has no WSD target.
    loss = torch.stack([views[key].square().mean() for key in "ABCD"]).mean()
    loss.backward()
    gradients = [parameter.grad for parameter in model.parameters() if parameter.grad is not None]
    if not gradients or not all(torch.isfinite(gradient).all() for gradient in gradients):
        raise RuntimeError("missing or non-finite gradients")
    optimizer.step()
    torch.xpu.synchronize()

    return {
        "device": torch.xpu.get_device_name(0),
        "target_candidate": target_id,
        "gloss_nodes": len(node_ids),
        "branches": len(branches),
        "input_shape": list(input_ids.shape),
        "surrogate_loss": float(loss.detach().cpu()),
        "gradient_tensors": len(gradients),
        "peak_allocated_bytes": int(torch.xpu.max_memory_allocated()),
        "optimizer_step": "ok",
        "scope": "one train-only candidate; surrogate objective; no dev/test",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--target-id")
    args = parser.parse_args()
    print(json.dumps(run_smoke(args.train, args.nodes, args.rules, args.model, args.target_id)))


if __name__ == "__main__":
    main()
