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
        sizes = {len(inputs[v]) for v in 'ABCD'}
        if len(sizes) != 1 or not 2 <= next(iter(sizes)) <= 4:
            raise ValueError('conditions require identical candidate counts')
        if not 0 <= row['label'] < next(iter(sizes)):
            raise ValueError('invalid label')
        if any(len(seq) != width for v in 'ABCD' for seq in inputs[v]):
            raise ValueError('invalid sequence length')
    return ids


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

        def forward(self, values, valid):
            batch, candidates, width = values.shape
            flat = values.reshape(batch * candidates, width)
            mask = flat.ne(0)
            separators = flat.eq(102).long()
            segments = ((separators.cumsum(-1) - separators) > 0).long() * mask.long()
            hidden = self.encoder(input_ids=flat, attention_mask=mask, token_type_ids=segments).last_hidden_state[:, 0]
            scores = self.head(hidden).reshape(batch, candidates)
            return scores.masked_fill(~valid, -1e9)

    def batchify(rows, version):
        inputs, valid, labels = [], [], []
        for row in rows:
            candidates = row['inputs'][version]
            if not 2 <= len(candidates) <= 4 or any(len(x) != max_len for x in candidates):
                raise ValueError('unexpected candidate shape')
            if not 0 <= row['label'] < len(candidates):
                raise ValueError('invalid label')
            inputs.append(candidates + [[0] * max_len] * (4 - len(candidates)))
            valid.append([True] * len(candidates) + [False] * (4 - len(candidates)))
            labels.append(row['label'])
        return (torch.tensor(inputs, dtype=torch.long, device=args.device),
                torch.tensor(valid, dtype=torch.bool, device=args.device),
                torch.tensor(labels, dtype=torch.long, device=args.device))

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
        total_loss = 0.0
        for start in range(0, len(order), 4):
            batch = [train[i] for i in order[start:start + 4]]
            values, valid, labels = batchify(batch, condition)
            optimizer.zero_grad(set_to_none=True)
            loss = torch.nn.functional.cross_entropy(scorer(values, valid), labels)
            if not torch.isfinite(loss): raise ValueError('nonfinite training loss')
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(batch)
        checkpoint = args.out / (condition + '.pt')
        torch.save(scorer.state_dict(), checkpoint)
        train_log[condition] = {'examples': len(order), 'mean_loss': total_loss / len(order),
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
        for condition in conditions:
            scorer = Scorer().to(args.device)
            scorer.load_state_dict(torch.load(args.out / (condition + '.pt'), map_location=args.device, weights_only=True))
            scorer.eval()
            correct = 0
            predictions = []
            with torch.inference_mode():
                for start in range(0, len(dev), 4):
                    batch = dev[start:start + 4]
                    values, valid, labels = batchify(batch, condition)
                    choice = scorer(values, valid).argmax(dim=-1)
                    correct += int((choice == labels).sum().item())
                    predictions.extend(choice.cpu().tolist())
            evaluation[condition] = {'covered': len(dev), 'correct': correct,
                'accuracy_covered': correct / len(dev) if dev else None,
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
