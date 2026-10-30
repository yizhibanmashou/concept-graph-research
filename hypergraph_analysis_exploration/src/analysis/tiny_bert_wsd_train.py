"""Train four BERT-tiny cross-encoders on fixed local training data; evaluate dev afterward."""
import argparse
import hashlib
import json
import random
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def validate(rows, width):
    ids = set()
    for row in rows:
        if row['sample_id'] in ids:
            raise ValueError('duplicate sample ID')
        ids.add(row['sample_id'])
        inputs = row['inputs']
        if set(inputs) != set('ABCD'):
            raise ValueError('four conditions required')
        candidate_ids = row.get('candidate_ids')
        scorable_ids = row.get('scorable_candidate_ids')
        if candidate_ids is None and scorable_ids is None:
            # Keep validation compatible with archived four-candidate pilot rows.
            sizes = {len(inputs[v]) for v in 'ABCD'}
            if len(sizes) != 1 or not 2 <= next(iter(sizes)) <= 4:
                raise ValueError('legacy conditions require two to four candidates')
            if not 0 <= row['label'] < next(iter(sizes)):
                raise ValueError('invalid legacy label')
            if any(len(seq) != width for v in 'ABCD' for seq in inputs[v]):
                raise ValueError('invalid sequence length')
            continue
        if not isinstance(candidate_ids, list) or len(candidate_ids) < 2 or len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError('complete unique candidate_ids required')
        if not isinstance(scorable_ids, list) or len(set(scorable_ids)) != len(scorable_ids):
            raise ValueError('unique scorable_candidate_ids required')
        manifest = row.get('candidates')
        if not isinstance(manifest, list) or [item.get('candidate_id') for item in manifest] != candidate_ids:
            raise ValueError('candidate manifest must preserve the full candidate order')
        ready_ids = [item['candidate_id'] for item in manifest if item.get('status') == 'ready']
        if any(item.get('status') not in ('ready', 'failed') for item in manifest):
            raise ValueError('each candidate needs a ready or failed status')
        if ready_ids != scorable_ids:
            raise ValueError('scorable candidates must match ready manifest entries')
        if not set(scorable_ids) <= set(candidate_ids):
            raise ValueError('scorable candidates must belong to full candidate list')
        sizes = {len(inputs[v]) for v in 'ABCD'}
        if len(sizes) != 1 or next(iter(sizes)) != len(scorable_ids):
            raise ValueError('conditions require identical inputs for every scorable candidate')
        if row['label'] != -1 and not 0 <= row['label'] < len(scorable_ids):
            raise ValueError('invalid scorable label')
        if row['label'] >= 0 and scorable_ids[row['label']] != row.get('gold_candidate_id'):
            raise ValueError('label does not identify gold candidate')
        if any(len(seq) != width for v in 'ABCD' for seq in inputs[v]):
            raise ValueError('invalid sequence length')
    return ids


def candidate_chunks(values, chunk_size):
    """Yield candidate microbatches without changing their target grouping."""
    if chunk_size < 1:
        raise ValueError('candidate chunk size must be positive')
    for start in range(0, len(values), chunk_size):
        yield values[start:start + chunk_size]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--device', choices=('cpu', 'xpu'), default='xpu')
    parser.add_argument('--seed', type=int, default=17)
    parser.add_argument('--smoke', action='store_true', help='train one batch of A without reading dev')
    args = parser.parse_args()
    import torch
    import transformers
    from transformers import BertConfig, BertModel

    if args.device == 'xpu' and not torch.xpu.is_available():
        raise ValueError('XPU device unavailable')
    train_path = args.data / 'train.json'
    train = json.loads(train_path.read_text(encoding='utf-8'))
    if not train:
        raise ValueError('no covered training examples')
    args.out.mkdir(parents=True, exist_ok=False)
    config = BertConfig.from_json_file(str(args.model / 'config.json'))
    metadata = json.loads((args.data / 'metadata.json').read_text(encoding='utf-8'))
    if digest(args.model / 'vocab.txt') != metadata['inputs_sha256']['vocab.txt']:
        raise ValueError('model vocabulary differs from prepared data')
    max_len = metadata['joint_budget']
    train_ids = validate(train, max_len)

    class Scorer(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = BertModel.from_pretrained(str(args.model.resolve()), config=config, local_files_only=True)
            self.head = torch.nn.Linear(config.hidden_size, 1)

        def forward(self, values):
            flat = values
            mask = flat.ne(0)
            separators = flat.eq(102).long()
            segments = ((separators.cumsum(-1) - separators) > 0).long() * mask.long()
            hidden = self.encoder(input_ids=flat, attention_mask=mask, token_type_ids=segments).last_hidden_state[:, 0]
            return self.head(hidden).squeeze(-1)

    def batchify(rows, version):
        inputs, labels = [], []
        for row in rows:
            candidates = row['inputs'][version]
            # Archived pilot rows have no manifest; all stored candidates are scorable.
            expected_count = len(row.get('scorable_candidate_ids', candidates))
            if len(candidates) != expected_count or any(len(x) != max_len for x in candidates):
                raise ValueError('unexpected candidate shape')
            inputs.append(torch.tensor(candidates, dtype=torch.long, device=args.device))
            labels.append(None if row.get('candidate_ids') is not None and row['label'] == -1 else row['label'])
        return inputs, labels

    def score_target(scorer, values):
        # Concatenate every candidate score before applying target-level softmax.
        return torch.cat([scorer(chunk) for chunk in candidate_chunks(values, 8)], dim=0)

    conditions = ('A',) if args.smoke else ('A', 'B', 'C', 'D')
    train_log = {}
    for condition in conditions:
        random.seed(args.seed)
        torch.manual_seed(args.seed)
        if args.device == 'xpu': torch.xpu.manual_seed_all(args.seed)
        scorer = Scorer().to(args.device)
        scorer.train()
        optimizer = torch.optim.AdamW(scorer.parameters(), lr=2e-5)
        order = list(range(len(train)))
        random.Random(args.seed).shuffle(order)
        if args.smoke: order = order[:4]
        trained_targets = 0
        total_loss = 0.0
        for start in range(0, len(order), 4):
            batch = [train[i] for i in order[start:start + 4]]
            values, labels = batchify(batch, condition)
            optimizer.zero_grad(set_to_none=True)
            losses = []
            for target_values, label in zip(values, labels):
                if label is None or not len(target_values):
                    continue
                scores = score_target(scorer, target_values)
                losses.append(torch.nn.functional.cross_entropy(scores.unsqueeze(0),
                    torch.tensor([label], dtype=torch.long, device=args.device)))
            if not losses:
                continue
            loss = torch.stack(losses).mean()
            if not torch.isfinite(loss): raise ValueError('nonfinite training loss')
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(losses)
            trained_targets += len(losses)
        if not trained_targets:
            raise ValueError('no training targets have encodable gold candidates')
        checkpoint = args.out / (condition + '.pt')
        torch.save(scorer.state_dict(), checkpoint)
        train_log[condition] = {'examples': trained_targets, 'mean_loss': total_loss / trained_targets,
                                'checkpoint_sha256': digest(checkpoint)}
        print('trained', condition, train_log[condition], flush=True)
        del scorer, optimizer
        if args.device == 'xpu': torch.xpu.empty_cache()

    result = {'train': train_log, 'device': args.device, 'torch_version': torch.__version__,
              'transformers_version': transformers.__version__, 'seed': args.seed, 'learning_rate': 2e-5,
              'epochs': 1, 'batch_size': 4, 'joint_budget': max_len,
              'inputs_sha256': {'train.json': digest(train_path), 'metadata.json': digest(args.data / 'metadata.json'),
                                'model_config': digest(args.model / 'config.json'),
                                'model_weights': digest(args.model / 'pytorch_model.bin')},
              'limits': 'Exploratory small-data train/dev pilot; development was used in prior design, no test read; no significance or semantic validation.'}
    if not args.smoke:
        dev_path = args.data / 'dev.json'
        dev = json.loads(dev_path.read_text(encoding='utf-8'))
        if train_ids & validate(dev, max_len):
            raise ValueError('train and development sample IDs overlap')
        result['inputs_sha256']['dev.json'] = digest(dev_path)
        evaluation = {}
        scorable_gold_count = sum(row['label'] >= 0 for row in dev)
        for condition in conditions:
            scorer = Scorer().to(args.device)
            scorer.load_state_dict(torch.load(args.out / (condition + '.pt'), map_location=args.device, weights_only=True))
            scorer.eval()
            correct = 0
            predictions = []
            with torch.inference_mode():
                for start in range(0, len(dev), 4):
                    batch = dev[start:start + 4]
                    values, labels = batchify(batch, condition)
                    for target_values, label in zip(values, labels):
                        if not len(target_values):
                            predictions.append(-1)
                            continue
                        choice = int(score_target(scorer, target_values).argmax().item())
                        if label is not None:
                            correct += int(choice == label)
                        predictions.append(choice)
            evaluation[condition] = {'scorable_gold': scorable_gold_count,
                'covered': len(dev), 'correct': correct,
                'accuracy_covered': correct / scorable_gold_count if scorable_gold_count else None,
                'accuracy_selected_with_exclusions_wrong': correct / metadata['counts']['dev']['selected'],
                'predictions': predictions}
            print('dev', condition, correct, '/', len(dev), flush=True)
            del scorer
            if args.device == 'xpu': torch.xpu.empty_cache()
        result['dev'] = evaluation
    (args.out / 'result.json').write_text(json.dumps(result, sort_keys=True, indent=2), encoding='utf-8')
    print('finished', flush=True)


if __name__ == '__main__':
    main()
