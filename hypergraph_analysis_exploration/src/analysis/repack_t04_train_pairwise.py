"""Rebuild A-D candidate tokens from train.json only with corrected pairwise C."""
import argparse
import hashlib
import json
from pathlib import Path

from src.analysis.compact_sense_budget import pack, representations
from src.analysis.sense_representation_pilot import build


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def context_prefix(sequence, sep_id):
    if not sequence or sequence[0] != 101:
        raise ValueError('expected BERT CLS at start of training input')
    try:
        end = sequence.index(sep_id)
    except ValueError as exc:
        raise ValueError('training input has no context separator') from exc
    if end < 2:
        raise ValueError('empty context prefix')
    return sequence[:end]


def rebuild_rows(rows, prepare_candidate, joint_budget, sep_id=102, pad_id=0):
    rebuilt = []
    stats = {'targets': len(rows), 'scorable_targets': 0, 'candidate_instances': 0,
             'all_candidates_ready': 0}
    for row in rows:
        ids = row.get('scorable_candidate_ids', row.get('candidate_ids'))
        if not isinstance(ids, list) or not ids:
            raise ValueError('training row lacks scorable candidates')
        old_inputs = row['inputs']
        prefixes = [context_prefix(seq, sep_id) for condition in 'ABCD' for seq in old_inputs[condition]]
        if len(prefixes) != 4 * len(ids) or any(prefix != prefixes[0] for prefix in prefixes[1:]):
            raise ValueError('A-D candidate inputs do not share one train context')
        inputs = {condition: [] for condition in 'ABCD'}
        for candidate_id in ids:
            candidate_tokens = prepare_candidate(candidate_id)
            stats['candidate_instances'] += 1
            for condition in 'ABCD':
                seq = prefixes[0] + [sep_id] + candidate_tokens[condition] + [sep_id]
                if len(seq) > joint_budget:
                    raise ValueError('rebuilt candidate exceeds joint budget')
                inputs[condition].append(seq + [pad_id] * (joint_budget - len(seq)))
        copied = dict(row)
        copied['inputs'] = inputs
        rebuilt.append(copied)
        if row.get('label', -1) >= 0:
            stats['scorable_targets'] += 1
        if row.get('candidate_ids') == ids:
            stats['all_candidates_ready'] += 1
    return rebuilt, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True, help='existing data directory; only train.json is opened')
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--vocab', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True, help='new train-only output directory')
    args = parser.parse_args()
    import csv
    import tokenizers

    train_path = args.data / 'train.json'
    metadata_path = args.data / 'metadata.json'
    metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
    if digest(args.vocab) != metadata['inputs_sha256']['vocab.txt']:
        raise ValueError('vocabulary differs from source training metadata')
    if digest(args.bundle / 'graph/nodes.tsv') != metadata['inputs_sha256']['nodes.tsv']:
        raise ValueError('OEWN node data differ from source training metadata')
    if digest(args.bundle / 'graph/hypergraph_rules.jsonl') != metadata['inputs_sha256']['rules.jsonl']:
        raise ValueError('OEWN rules differ from source training metadata')

    nodes_path = args.bundle / 'graph/nodes.tsv'
    rules_path = args.bundle / 'graph/hypergraph_rules.jsonl'
    with nodes_path.open(encoding='utf-8-sig', newline='') as f:
        nodes = {row['synset_id']: row for row in csv.DictReader(f, delimiter='\t')}
    with rules_path.open(encoding='utf-8') as f:
        rules = {row['head']: row['clauses'] for row in (json.loads(line) for line in f if line.strip())}
    definitions = {key: value['definition'] for key, value in nodes.items()}
    tokenizer = tokenizers.BertWordPieceTokenizer(str(args.vocab), lowercase=True)
    sep_id, pad_id = tokenizer.token_to_id('[SEP]'), tokenizer.token_to_id('[PAD]')
    if (tokenizer.token_to_id('[CLS]'), sep_id, pad_id) != (101, 102, 0):
        raise ValueError('expected BERT special token IDs 101, 102 and 0')

    cache = {}
    branch_stats = {'candidates': 0, 'original_branches': 0, 'retained_branches': 0,
                    'pairwise_edges': 0}

    def prepare(candidate_id):
        if candidate_id not in cache:
            if candidate_id not in nodes or candidate_id not in rules:
                raise ValueError('training candidate missing from frozen graph')
            item = build(candidate_id, nodes[candidate_id]['definition'], rules[candidate_id], definitions)
            selected = pack(item, lambda text: tokenizer.encode(text).ids, metadata['candidate_budget'])
            if selected['status'] == 'base_over_budget':
                raise ValueError('base candidate representation exceeds budget')
            branches = [item['D']['branches'][i] for i in selected['selected_indices']]
            forms, _ = representations(item, branches)
            encoded = {condition: tokenizer.encode(
                json.dumps(forms[condition], sort_keys=True, ensure_ascii=False, separators=(',', ':')),
                add_special_tokens=False).ids for condition in 'ABCD'}
            if any(len(ids) > metadata['candidate_budget'] - 2 for ids in encoded.values()):
                raise ValueError('candidate exceeds reserved token budget')
            cache[candidate_id] = encoded
            branch_stats['candidates'] += 1
            branch_stats['original_branches'] += len(item['D']['branches'])
            branch_stats['retained_branches'] += len(branches)
            branch_stats['pairwise_edges'] += len(forms['C']['edges'])
        return cache[candidate_id]

    source_rows = json.loads(train_path.read_text(encoding='utf-8'))
    output, counts = rebuild_rows(source_rows, prepare, metadata['joint_budget'], sep_id, pad_id)
    args.out.mkdir(parents=True, exist_ok=False)
    out_train = args.out / 'train.json'
    out_train.write_text(json.dumps(output, sort_keys=True, separators=(',', ':')), encoding='utf-8')
    out_metadata = {'run_scope': 'train-only; dev.json was not opened',
                    'joint_budget': metadata['joint_budget'],
                    'candidate_budget': metadata['candidate_budget'],
                    'tokenizers_version': tokenizers.__version__,
                    'inputs_sha256': {'vocab.txt': digest(args.vocab),
                        'source_train.json': digest(train_path), 'source_metadata.json': digest(metadata_path),
                        'nodes.tsv': digest(nodes_path), 'rules.jsonl': digest(rules_path)},
                    'train_sha256': digest(out_train), 'counts': counts,
                    'branch_audit': branch_stats,
                    'limitations': 'Train-only pipeline validation; no development or test examples/labels were read. Not an evaluation.'}
    (args.out / 'metadata.json').write_text(json.dumps(out_metadata, sort_keys=True, indent=2), encoding='utf-8')
    print(json.dumps({'counts': counts, 'branch_audit': branch_stats,
                      'train_sha256': out_metadata['train_sha256']}, sort_keys=True))


if __name__ == '__main__':
    main()
