"""Audit information parity and descriptive lengths of prepared A-D records."""
import argparse
import hashlib
import json
from pathlib import Path


def audit(items):
    results = []
    for item in items:
        a, b, c, d = (item[k] for k in ('A', 'B', 'C', 'D'))
        if any(record['target'] != a['target'] or record['gloss'] != a['gloss'] for record in (b, c, d)):
            raise ValueError('target or gloss differs across conditions')
        dependencies = b['dependencies']
        if c['dependencies'] != dependencies or d['dependencies'] != dependencies:
            raise ValueError('B/C/D dependency inventories differ')
        dep_ids = [dep['id'] for dep in dependencies]
        if len(dep_ids) != len(set(dep_ids)):
            raise ValueError('duplicate dependency IDs')
        edges = c['edges']
        if len(edges) != len(dep_ids) or any(edge['head'] != a['target'] for edge in edges):
            raise ValueError('invalid pair edges')
        if {edge['dependency'] for edge in edges} != set(dep_ids):
            raise ValueError('pair edges do not match dependency inventory')
        branches = d['branches']
        if any(not branch for branch in branches) or set().union(*map(set, branches)) != set(dep_ids):
            raise ValueError('branch dependencies do not match inventory or contain empty branch')
        results.append({'target': a['target'], 'dependency_count': len(dep_ids),
                        'branch_count': len(branches),
                        'json_characters': {key: len(json.dumps(item[key], ensure_ascii=False, sort_keys=True))
                                            for key in ('A', 'B', 'C', 'D')}})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    data = json.loads(raw)
    if not data['items']:
        raise ValueError('no prepared records')
    results = audit(data['items'])
    result = {'input_sha256': hashlib.sha256(raw).hexdigest(), 'items': results,
              'limits': 'Character counts are not model token counts; parity of inventories is not equal model budget or semantic validity.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Audited {len(results)} records; model token budget remains unverified.")


if __name__ == '__main__':
    main()
