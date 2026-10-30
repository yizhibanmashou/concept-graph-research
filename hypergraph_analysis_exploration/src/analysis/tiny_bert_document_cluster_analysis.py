"""Cluster-aware descriptive uncertainty for the reused tiny-BERT WSD development set."""
import argparse
import hashlib
import json
import random
import zipfile
from collections import defaultdict
from pathlib import Path

from src.analysis.semcor_dev_pilot import sentence_records
from src.analysis.semcor_train_mapping import digest, partition


def stable_hash(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def document_cluster_id(document_id):
    """Make a pseudonymous join key; hashes are linkable and are not anonymization."""
    return stable_hash('semcor-document:' + document_id)


def map_sample_documents(archive, document_ids, sample_ids):
    """Recover source document clusters by joining the frozen sample hashes."""
    wanted = set(sample_ids)
    found = {}
    for document_id in document_ids:
        for sentence_index, (_context, _words, annotated) in enumerate(sentence_records(archive, document_id)):
            for token_index, _token in enumerate(annotated):
                sample_id = stable_hash(f'{document_id}:{sentence_index}:{token_index}')
                if sample_id in wanted:
                    cluster_id = document_cluster_id(document_id)
                    if sample_id in found and found[sample_id] != cluster_id:
                        raise ValueError('sample hash collision across SemCor documents')
                    found[sample_id] = cluster_id
    missing = wanted - found.keys()
    if missing:
        raise ValueError(f'{len(missing)} selected sample IDs did not map to the frozen SemCor document pool')
    return found


def correctness_by_target(rows, runs):
    """Average repeated-seed correctness per target; map predictions through ready IDs."""
    conditions = ('A', 'B', 'C', 'D')
    output = {}
    for condition in conditions:
        per_target = defaultdict(list)
        for run in runs:
            predictions = run['dev'][condition]['predictions']
            if len(predictions) != len(rows):
                raise ValueError('prediction count does not match frozen development rows')
            for row, prediction in zip(rows, predictions):
                if row['label'] < 0:
                    per_target[row['sample_id']].append(0.0)
                    continue
                ids = row.get('scorable_candidate_ids', row['candidate_ids'])
                if not 0 <= prediction < len(ids):
                    raise ValueError('prediction index is outside the scorable candidate list')
                per_target[row['sample_id']].append(float(ids[prediction] == row['gold_candidate_id']))
        output[condition] = {key: sum(values) / len(values) for key, values in per_target.items()}
    return output


def bootstrap_by_document(rows, clusters, scores, replicates=20000, seed=20261031):
    grouped = defaultdict(list)
    by_id = {row['sample_id']: row for row in rows}
    for sample_id, cluster_id in clusters.items():
        grouped[cluster_id].append(sample_id)
    cluster_ids = sorted(grouped)
    if len(cluster_ids) < 2:
        raise ValueError('document-cluster bootstrap requires at least two documents')

    def metric(sample_ids, condition, covered_only):
        selected = [sample for sample in sample_ids
                    if not covered_only or by_id[sample]['label'] >= 0]
        if not selected:
            return None
        return sum(scores[condition][sample] for sample in selected) / len(selected)

    rng = random.Random(seed)
    covered_draws = {name: [] for name in ('A', 'B', 'C', 'D')}
    selected_draws = {name: [] for name in ('A', 'B', 'C', 'D')}
    differences = {'D_minus_B_covered': [], 'D_minus_B_selected': []}
    for _ in range(replicates):
        sampled_clusters = [rng.choice(cluster_ids) for _ in cluster_ids]
        sample_ids = [sample for cluster in sampled_clusters for sample in grouped[cluster]]
        current = {condition: metric(sample_ids, condition, True) for condition in covered_draws}
        for condition in covered_draws:
            covered_draws[condition].append(current[condition])
            selected_draws[condition].append(metric(sample_ids, condition, False))
        selected_b = metric(sample_ids, 'B', False)
        selected_d = metric(sample_ids, 'D', False)
        if current['D'] is not None and current['B'] is not None:
            differences['D_minus_B_covered'].append(current['D'] - current['B'])
        else:
            differences['D_minus_B_covered'].append(None)
        differences['D_minus_B_selected'].append(selected_d - selected_b)

    def interval(values):
        ordered = sorted(value for value in values if value is not None)
        if not ordered:
            raise ValueError('no valid bootstrap replicates for requested interval')
        return {'lower_95_percentile': ordered[int(0.025 * (len(ordered) - 1))],
                'upper_95_percentile': ordered[int(0.975 * (len(ordered) - 1))]}

    return {'document_clusters': len(cluster_ids), 'replicates': replicates, 'seed': seed,
            'covered_accuracy_intervals': {key: interval(values) for key, values in covered_draws.items()},
            'selected_accuracy_intervals': {key: interval(values) for key, values in selected_draws.items()},
            'paired_difference_intervals': {key: interval(values) for key, values in differences.items()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nltk-data', type=Path, required=True)
    parser.add_argument('--prepared-dev', type=Path, required=True)
    parser.add_argument('--run', action='append', required=True,
                        help='seed result.json; pass once for each completed seed')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--replicates', type=int, default=20000)
    args = parser.parse_args()

    import nltk
    nltk.data.path = [str(args.nltk_data.resolve())]
    from nltk.corpus import semcor
    split = partition(semcor.fileids())
    rows = json.loads((args.prepared_dev / 'dev.json').read_text(encoding='utf-8'))
    metadata = json.loads((args.prepared_dev / 'metadata.json').read_text(encoding='utf-8'))
    runs = [json.loads(Path(value).read_text(encoding='utf-8')) for value in args.run]
    run_seeds = [run['seed'] for run in runs]
    if len(run_seeds) != len(set(run_seeds)):
        raise ValueError('each repeated-seed run must be unique')
    prepared_dev_sha256 = digest(args.prepared_dev / 'dev.json')
    for run in runs:
        if run.get('inputs_sha256', {}).get('dev.json') != prepared_dev_sha256:
            raise ValueError(f"seed {run.get('seed')} was not evaluated on the supplied frozen dev file")
    expected_ids = [row['sample_id'] for row in rows]
    expected_hash = stable_hash('\n'.join(expected_ids))
    if metadata['sample_ids_sha256']['dev'] != expected_hash:
        raise ValueError('prepared development rows do not match their metadata sample hash')
    with zipfile.ZipFile(args.nltk_data / 'corpora/semcor.zip') as archive:
        # The frozen T04 split further subdivided the official SemCor training pool;
        # do not substitute the present-day official dev assignment for that manifest.
        clusters = map_sample_documents(archive, split['train'], expected_ids)
    scores = correctness_by_target(rows, runs)
    bootstrap = bootstrap_by_document(rows, clusters, scores, args.replicates)

    def observed(condition, covered_only):
        selected = [row for row in rows if not covered_only or row['label'] >= 0]
        return sum(scores[condition][row['sample_id']] for row in selected) / len(selected)

    result = {'analysis': 'post-hoc document-cluster bootstrap on reused SemCor development targets',
              'source': {'prepared_dev_sha256': prepared_dev_sha256,
                         'prepared_metadata_sha256': digest(args.prepared_dev / 'metadata.json'),
                         'sample_ids_sha256': expected_hash,
                         'cluster_ids_sha256': stable_hash('\n'.join(sorted(set(clusters.values()))))},
              'nltk_version': nltk.__version__,
              'seeds': run_seeds,
              'selected_targets': len(rows),
              'covered_targets': sum(row['label'] >= 0 for row in rows),
              'observed_accuracy': {condition: {'covered': observed(condition, True),
                                                 'selected_uncovered_as_wrong': observed(condition, False)}
                                    for condition in ('A', 'B', 'C', 'D')},
              'bootstrap': bootstrap,
              'limits': 'Exploratory uncertainty only: reused, previously inspected development targets; 13-document source split with fewer selected document clusters; repeated model seeds are averaged within target and are not independent observations. No held-out test accessed.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
    print(json.dumps({'selected_targets': result['selected_targets'], 'covered_targets': result['covered_targets'],
                      'bootstrap': bootstrap, 'observed_accuracy': result['observed_accuracy']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
