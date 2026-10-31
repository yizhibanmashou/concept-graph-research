"""Run a train-only A/B/C/D epoch with a shared gloss encoder.

This is an engineering run only. It reads the train split, graph definitions,
and graph rules; it never opens development or test files and does not report
WSD quality. Each candidate receives the same context+candidate-gloss token
sequence in every condition. The default `mean_pool` mode is the historical
parameter-free baseline; `shared_set_encoder` is the newer nonlinear prototype.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from pathlib import Path
from typing import Any

from src.analysis.profile_t04_xpu_text_structure import (
    make_gloss_batches,
    pad_token_batch,
    read_graph,
)
from src.analysis.t04_relation_aggregation import aggregate_relation_views
from src.analysis.t04_relation_set_encoder import (
    SharedRelationItemEncoder,
    encode_relation_item_views,
)
from src.analysis.tiny_bert_wsd_train import digest, validate


EXPECTED_MODEL_HASHES = {
    "config.json": "cf3179684f7c360dd6185962d480e7d426ceb8fe49f5db7b64bdc15dba0b8798",
    "pytorch_model.bin": "dab2c2bddcfb48ea430ef63fd76d46d67d704487844d967256a50dd7d7fd0a66",
    "vocab.txt": "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3",
}


def _input_hashes(paths: dict[str, Path]) -> dict[str, str]:
    return {name: digest(path) for name, path in paths.items()}


def run_epoch(
    data_dir: Path,
    nodes_path: Path,
    rules_path: Path,
    model_path: Path,
    out_dir: Path,
    seed: int = 17,
    target_batch_size: int = 2,
    graph_batch_size: int = 32,
    relation_mode: str = "mean_pool",
) -> dict[str, Any]:
    import torch
    import transformers
    from tokenizers import BertWordPieceTokenizer
    from transformers import BertConfig, BertModel

    if not torch.xpu.is_available():
        raise ValueError("XPU is unavailable in this Conda environment")
    if target_batch_size < 1 or graph_batch_size < 1:
        raise ValueError("batch sizes must be positive")
    if relation_mode not in {"mean_pool", "shared_set_encoder"}:
        raise ValueError("unsupported relation mode")
    if out_dir.exists():
        raise FileExistsError(f"output directory already exists: {out_dir}")

    train_path = data_dir / "train.json"
    metadata_path = data_dir / "metadata.json"
    train = json.loads(train_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    train_sample_ids = validate(train, metadata["joint_budget"])
    trainable = [row for row in train if row["label"] >= 0]
    if not trainable:
        raise ValueError("no train rows have a scorable gold candidate")
    if digest(model_path / "vocab.txt") != metadata["inputs_sha256"]["vocab.txt"]:
        raise ValueError("pinned vocabulary does not match prepared train data")
    model_hashes = _input_hashes({name: model_path / name for name in EXPECTED_MODEL_HASHES})
    if model_hashes != EXPECTED_MODEL_HASHES:
        raise ValueError("pinned BERT-tiny file SHA-256 mismatch")

    trainable_candidate_ids = sorted({
        candidate_id
        for row in trainable
        for candidate_id in row["scorable_candidate_ids"]
    })
    definitions, rules = read_graph(nodes_path, rules_path, set(trainable_candidate_ids))
    graph_node_ids = set(trainable_candidate_ids)
    for target_id in trainable_candidate_ids:
        for branch in rules[target_id]:
            graph_node_ids.update(branch)

    tokenizer = BertWordPieceTokenizer(str(model_path / "vocab.txt"), lowercase=True)
    tokenizer.enable_truncation(max_length=512)
    encoded_glosses = {
        node_id: tokenizer.encode(definitions[node_id]).ids
        for node_id in sorted(graph_node_ids)
    }
    if any(not ids for ids in encoded_glosses.values()):
        raise ValueError("an OEWN graph gloss tokenized to an empty sequence")

    config = BertConfig.from_json_file(str(model_path / "config.json"))
    hashes = _input_hashes({
        "train.json": train_path,
        "metadata.json": metadata_path,
        "nodes.tsv": nodes_path,
        "rules.jsonl": rules_path,
        **{f"model/{name}": model_path / name for name in EXPECTED_MODEL_HASHES},
    })
    results: dict[str, Any] = {}

    for condition in "ABCD":
        # Reset the initialization and shuffle seed for paired engineering runs.
        random.seed(seed)
        torch.manual_seed(seed)
        torch.xpu.manual_seed_all(seed)
        order = list(range(len(trainable)))
        random.Random(seed).shuffle(order)
        encoder = BertModel.from_pretrained(
            str(model_path.resolve()), config=config, local_files_only=True
        ).to("xpu")
        relation_encoder = (
            SharedRelationItemEncoder(config.hidden_size, config.hidden_size).to("xpu")
            if relation_mode == "shared_set_encoder" else None
        )
        head = torch.nn.Linear(config.hidden_size * 3, 1).to("xpu")
        encoder.train()
        if relation_encoder is not None:
            relation_encoder.train()
        head.train()
        parameters = [*encoder.parameters(), *head.parameters()]
        if relation_encoder is not None:
            parameters.extend(relation_encoder.parameters())
        optimizer = torch.optim.AdamW(parameters, lr=2e-5)
        torch.xpu.synchronize()
        torch.xpu.reset_peak_memory_stats()
        started = time.perf_counter()
        examples_seen = 0
        steps = 0
        total_loss = 0.0
        gloss_node_instances = 0
        context_candidate_instances = 0

        for start in range(0, len(order), target_batch_size):
            rows = [trainable[index] for index in order[start:start + target_batch_size]]
            candidate_ids = sorted({
                candidate_id for row in rows for candidate_id in row["scorable_candidate_ids"]
            })
            batch_node_ids = set(candidate_ids)
            for target_id in candidate_ids:
                for branch in rules[target_id]:
                    batch_node_ids.update(branch)
            batch_encoded = {node_id: encoded_glosses[node_id] for node_id in sorted(batch_node_ids)}
            graph_batches = make_gloss_batches(batch_encoded, graph_batch_size, order="length")

            optimizer.zero_grad(set_to_none=True)
            node_vectors: dict[str, Any] = {}
            for batch in graph_batches:
                node_batch = [node_id for node_id, _ in batch]
                token_rows = [ids for _, ids in batch]
                padded, masks = pad_token_batch(token_rows)
                token_tensor = torch.tensor(padded, dtype=torch.long, device="xpu")
                mask_tensor = torch.tensor(masks, dtype=torch.long, device="xpu")
                hidden = encoder(input_ids=token_tensor, attention_mask=mask_tensor).last_hidden_state[:, 0]
                node_vectors.update({node_id: hidden[index] for index, node_id in enumerate(node_batch)})

            if relation_mode == "mean_pool":
                graph_views = {
                    target_id: aggregate_relation_views(node_vectors, target_id, rules[target_id])
                    for target_id in candidate_ids
                }
            else:
                graph_views = {}
                for target_id in candidate_ids:
                    item_views = aggregate_relation_views(
                        node_vectors,
                        target_id,
                        rules[target_id],
                        include_relation_items=True,
                    )["relation_items"]
                    encoded_views = encode_relation_item_views(item_views, relation_encoder)
                    target_vector = node_vectors[target_id]
                    graph_views[target_id] = {
                        name: torch.cat([target_vector, encoded_views[name]])
                        for name in "ABCD"
                    }
            context_rows = [
                token_row for row in rows for token_row in row["inputs"]["A"]
            ]
            flat_candidates = [
                candidate_id for row in rows for candidate_id in row["scorable_candidate_ids"]
            ]
            lengths = [next((index for index, token in enumerate(row) if token == 0), len(row))
                       for row in context_rows]
            width = max(lengths)
            flat_tensor = torch.tensor([row[:width] for row in context_rows], dtype=torch.long, device="xpu")
            attention = flat_tensor.ne(0).long()
            separators = flat_tensor.eq(102).long()
            segments = ((separators.cumsum(-1) - separators) > 0).long() * attention
            context_vectors = encoder(
                input_ids=flat_tensor,
                attention_mask=attention,
                token_type_ids=segments,
            ).last_hidden_state[:, 0]
            relation_vectors = torch.stack([
                graph_views[candidate_id][condition] for candidate_id in flat_candidates
            ])
            logits = head(torch.cat([context_vectors, relation_vectors], dim=-1)).squeeze(-1)

            losses = []
            offset = 0
            for row in rows:
                count = len(row["scorable_candidate_ids"])
                candidate_logits = logits[offset:offset + count]
                offset += count
                losses.append(torch.nn.functional.cross_entropy(
                    candidate_logits.unsqueeze(0),
                    torch.tensor([row["label"]], dtype=torch.long, device="xpu"),
                ))
            loss = torch.stack(losses).mean()
            if not torch.isfinite(loss):
                raise RuntimeError("non-finite train loss")
            loss.backward()
            gradients = [
                parameter.grad for parameter in parameters
                if parameter.grad is not None
            ]
            if not gradients or not bool(torch.stack([
                torch.isfinite(gradient).all() for gradient in gradients
            ]).all().item()):
                raise RuntimeError("missing or non-finite gradients")
            optimizer.step()
            examples_seen += len(rows)
            steps += 1
            total_loss += float(loss.detach().cpu()) * len(rows)
            gloss_node_instances += len(batch_node_ids)
            context_candidate_instances += len(flat_candidates)

        torch.xpu.synchronize()
        elapsed = time.perf_counter() - started
        checkpoint = out_dir / f"{condition}.pt"
        out_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_state = {"encoder": encoder.state_dict(), "head": head.state_dict()}
        if relation_encoder is not None:
            checkpoint_state["relation_encoder"] = relation_encoder.state_dict()
        torch.save(checkpoint_state, checkpoint)
        results[condition] = {
            "train_examples": examples_seen,
            "optimizer_steps": steps,
            "mean_train_loss": total_loss / examples_seen,
            "gloss_node_instances_encoded": gloss_node_instances,
            "context_candidate_instances_encoded": context_candidate_instances,
            "wall_clock_seconds": elapsed,
            "peak_allocated_bytes": int(torch.xpu.max_memory_allocated()),
            "checkpoint_sha256": digest(checkpoint),
        }
        del encoder, relation_encoder, head, optimizer
        torch.xpu.empty_cache()

    result = {
        "schema": "t04-xpu-train-only-structural-epoch/1",
        "device": torch.xpu.get_device_name(0),
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "python_version": __import__("platform").python_version(),
        "seed": seed,
        "target_batch_size": target_batch_size,
        "graph_batch_size": graph_batch_size,
        "relation_mode": relation_mode,
        "train_rows": len(train),
        "trainable_rows": len(trainable),
        "unscorable_train_rows": len(train) - len(trainable),
        "train_sample_id_set_sha256": hashlib.sha256(
            "\n".join(sorted(train_sample_ids)).encode("utf-8")
        ).hexdigest(),
        "unique_candidate_count": len(trainable_candidate_ids),
        "unique_graph_node_count": len(graph_node_ids),
        "input_sha256": hashes,
        "conditions": results,
        "limits": (
            "One train-only epoch per condition. No development or test files were opened. "
            "Training loss, runtime and memory are engineering diagnostics, not WSD quality estimates; "
            "the four conditions share the same base context-candidate token sequence; relation_mode records whether"
            " relation items use legacy linear means or the shared nonlinear set encoder."
        ),
    }
    with (out_dir / "result.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--nodes", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--target-batch-size", type=int, default=2)
    parser.add_argument("--graph-batch-size", type=int, default=32)
    parser.add_argument("--relation-mode", choices=("mean_pool", "shared_set_encoder"), default="mean_pool")
    args = parser.parse_args()
    result = run_epoch(
        args.data, args.nodes, args.rules, args.model, args.out,
        seed=args.seed,
        target_batch_size=args.target_batch_size,
        graph_batch_size=args.graph_batch_size,
        relation_mode=args.relation_mode,
    )
    print(json.dumps({
        "device": result["device"],
        "trainable_rows": result["trainable_rows"],
        "unique_candidate_count": result["unique_candidate_count"],
        "conditions": result["conditions"],
        "input_sha256": result["input_sha256"],
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
