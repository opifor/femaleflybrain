"""Preregistered outgoing-lesion test of male olfactory routing."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import gzip
import heapq
import json
from pathlib import Path
import time

import numpy as np
from scipy.sparse import csr_matrix

from flybench.dictionary import groups
from flybench.graph import load
from flybench.sim.fast_gpu import Simulator, Drive
from flybench.sim.params import Parameters
from .male_decides import BatchRates, save, stats
from .record import sha256, environment

PROTOCOL = Path('experiments/male_route_v1.md')
PROTOCOL_HASH = '20a1d9be86cbbe0517bbc64e0816075245dbf45868c3db2d0ddb1340ff2449e3'
SEEDS = {'quick': (100, 101), 'test': tuple(range(20))}
NETWORKS = ('intact', 'p1_lesion', 'random_lesion')
DOSES = {'zero': 0, 'scent240': 240, 'scent960': 960}
RAW = Path('build/records-raw')


def lesion_outgoing(graph, cells):
    """Copy edge values, preserving incoming edges from every unaffected row."""
    cells = np.asarray(cells, dtype=np.int64)
    if cells.ndim != 1 or np.any(cells < 0) or np.any(cells >= len(graph['indptr'])-1):
        raise ValueError('Invalid lesion indices')
    result = dict(graph)
    for key in ('count', 'data'):
        result[key] = graph[key].copy()
        for cell in cells:
            result[key][graph['indptr'][cell]:graph['indptr'][cell+1]] = 0
    return result


def random_cells(n, p1, seed):
    return np.sort(np.random.default_rng(seed+1000).choice(
        np.setdiff1d(np.arange(n), p1), size=len(p1), replace=False))


def route_rule(intact, lesion, difference, r0=True, r2=True):
    if not r0 or not r2:
        return 'unassessed'
    if lesion < .5*intact and difference['mean'] > 2*difference['se']:
        return 'route through P1 SUPPORTED'
    if lesion > .8*intact:
        return 'P1 bypass SUPPORTED'
    return 'inconclusive'


def analyze(trials, dose=240):
    lookup = {(t['seed'], t['network'], t['drive']): t['metrics']['pIP10'] for t in trials}
    expected = {(s, n, d) for s in SEEDS['test'] for n in NETWORKS for d in DOSES}
    if len(trials) != len(expected) or set(lookup) != expected:
        raise ValueError('Incomplete or duplicate TEST coverage')
    delta = {n: np.array([lookup[s, n, 'scent'+str(dose)]-lookup[s, n, 'zero']
                         for s in SEEDS['test']]) for n in NETWORKS}
    result = {n: stats(v) for n, v in delta.items()}
    difference = stats(delta['intact']-delta['p1_lesion'])
    control = stats(delta['random_lesion']-.8*delta['intact'])
    r0 = result['intact']['mean'] > 2*result['intact']['se']
    r2 = result['random_lesion']['mean'] > .8*result['intact']['mean']
    result.update(difference_of_differences=difference, control_margin=control,
                  R0='supported' if r0 else 'not supported',
                  R2=('supported' if r2 else 'not supported') if r0 else 'unassessed',
                  R1=route_rule(result['intact']['mean'], result['p1_lesion']['mean'], difference, r0, r2))
    return result


def summarize(trials):
    result = []
    for network in NETWORKS:
        for drive in DOSES:
            rows = [t for t in trials if t['network'] == network and t['drive'] == drive]
            if len(rows) >= 2:
                result.append({'network_kind': network, 'drive': drive,
                               **{k: stats([t['metrics'][k] for t in rows]) for k in rows[0]['metrics']}})
    return result


def provenance():
    if sha256(PROTOCOL) != PROTOCOL_HASH:
        raise ValueError('Preregistration hash mismatch')
    source = ('flybench/experiment/male_route.py', 'flybench/experiment/male_decides.py',
              'flybench/sim/fast_gpu.py', 'flybench/sim/params.py',
              'flybench/dictionary/entries.py', 'flybench/dictionary/api.py')
    return {'created_utc': datetime.now(timezone.utc).isoformat(),
            'protocol_sha256': PROTOCOL_HASH, 'graph_sha256': sha256('build/graph_male.npz'),
            'dictionary_sha256': sha256('build/dictionary_male.json'),
            'source_sha256': {p: sha256(p) for p in source}, 'environment': environment('cuda')}


def run(stage, budget_seconds=1200):
    start = time.perf_counter()
    record = provenance()
    graph = load('build/graph_male.npz')
    g = groups('male', graph=graph)
    if len(g['P1']) != 46 or len(g['pIP10']) != 2 or not len(g['Or47b']):
        raise ValueError('Unexpected dictionary populations')
    n = len(graph['body_id'])
    visual = np.union1d(g['L1'], g['L2'])
    visual = visual[graph['side'][visual] == 'R']
    targets = np.unique(np.concatenate([g['Or47b'], visual, g['P1']]))
    readouts = {key: g[key] for key in ('P1', 'pIP10', 'Or47b')}
    rawdir = RAW/('male_route_v1_'+stage)
    rawdir.mkdir(parents=True, exist_ok=True)
    lesions = {str(s): random_cells(n, g['P1'], s) for s in SEEDS[stage]}
    identity = lambda ids: {'indices': ids.tolist(), 'body_ids': graph['body_id'][ids].tolist()}
    save(rawdir/'targets_lesions.json', {'P1': identity(g['P1']),
        'random': {s: identity(ids) for s, ids in lesions.items()},
        'random_superclass_matching': False, 'random_rng': 'numpy.default_rng(seed+1000)',
        'targets': identity(targets), 'readouts': {k: identity(v) for k, v in readouts.items()}})
    record.update(stage=stage, seeds=list(SEEDS[stage]), parameters=asdict(Parameters(dt=.2)),
                  kernel='shiu', backend='fast_gpu', batch_size=1, windows=20, warmup=4,
                  neurons=n, target_count=len(targets), readout_counts={k: len(v) for k, v in readouts.items()},
                  random_superclass_matching=False, trials=[], raw=[], complete=False)
    networks = NETWORKS[:2] if stage == 'quick' else NETWORKS
    doses = ('zero', 'scent960') if stage == 'quick' else tuple(DOSES)
    deadline_hit = False
    for seed in SEEDS[stage]:
        for network in networks:
            if time.perf_counter()-start > budget_seconds:
                deadline_hit = True
                break
            ids = g['P1'] if network == 'p1_lesion' else lesions[str(seed)]
            changed = graph if network == 'intact' else lesion_outgoing(graph, ids)
            weights = csr_matrix((changed['data'], changed['indices'], changed['indptr']), shape=(n, n))
            sim = Simulator(weights, device='cuda', params=Parameters(dt=.2), kernel='shiu',
                            groups=readouts, drive=Drive(tuple(targets), 0))
            for drive in doses:
                rates = np.zeros(len(targets))
                rates[np.searchsorted(targets, g['Or47b'])] = DOSES[drive]
                sim.drive = Drive(tuple(targets), BatchRates(rates, 1), 'poisson')
                state = sim.initial_batch_state((seed,))
                active = np.zeros(n, dtype=bool)
                measured = []
                path = rawdir/f'{seed}_{network}_{drive}.jsonl.gz'
                with gzip.open(path, 'wt', encoding='utf-8', newline='\n') as stream:
                    for window in range(20):
                        result = sim.run_batch(50, state=state)
                        state = result.state
                        metrics = {k: float(v[0]) for k, v in result.group_rates_hz.items()}
                        metrics.update(network=float(result.total_hz_per_neuron[0]),
                                       ignition=float(result.total_hz_per_neuron[0] > 30),
                                       Or47b_sampled_hz=float(result.sampled_drive_hz[g['Or47b'], 0].mean()),
                                       Or47b_delivered_hz=float(result.delivered_hz[g['Or47b'], 0].mean()))
                        stream.write(json.dumps({'window': window, 'metrics': metrics})+'\n')
                        if window >= 4:
                            active |= result.counts[:, 0] > 0
                            measured.append(metrics)
                metrics = {k: float(np.mean([m[k] for m in measured])) for k in measured[0]}
                metrics['active_percent'] = float(100*active.mean())
                active_path = rawdir/f'{seed}_{network}_{drive}_active.npz'
                np.savez_compressed(active_path, indices=np.flatnonzero(active))
                record['trials'].append({'seed': seed, 'network': network, 'drive': drive, 'metrics': metrics})
                for artifact in (path, active_path):
                    record['raw'].append({'path': artifact.as_posix(), 'sha256': sha256(artifact), 'bytes': artifact.stat().st_size})
                record['elapsed_seconds'] = time.perf_counter()-start
                save(rawdir/'checkpoint.json', record)
            print(f'{stage} seed={seed} network={network} elapsed={time.perf_counter()-start:.1f}s', flush=True)
            del sim, state, result, weights, changed
        if deadline_hit:
            break
    record['complete'] = len(record['trials']) == len(SEEDS[stage])*len(networks)*len(doses)
    record['summary'] = summarize(record['trials'])
    record['elapsed_seconds'] = time.perf_counter()-start
    metadata = rawdir/'targets_lesions.json'
    record['raw'].append({'path': metadata.as_posix(), 'sha256': sha256(metadata), 'bytes': metadata.stat().st_size})
    if sha256(PROTOCOL) != PROTOCOL_HASH:
        raise ValueError('Protocol changed during execution')
    if stage == 'test' and record['complete']:
        record['inference'] = analyze(record['trials'])
        record['descriptive960'] = analyze(record['trials'], 960)
    save('records/male_route_v1_'+stage+'.json', record)


def top_paths(graph, sources, targets, length, limit=10):
    """Exact best-first bottleneck search with admissible walk bounds."""
    n = len(graph['body_id'])
    ptr, dst, count = (graph[k] for k in ('indptr', 'indices', 'count'))
    bound = [np.zeros(n, dtype=np.int64)]
    bound[0][targets] = np.iinfo(np.int32).max
    # Maximum bottleneck over walks of exactly r steps is an upper bound
    # for simple completions. maximum.at also handles empty CSR rows.
    for remaining in range(1, length+1):
        values = np.zeros(n, dtype=np.int64)
        for start in range(0, len(dst), 1_000_000):
            stop = min(start+1_000_000, len(dst))
            edge = np.arange(start, stop)
            src = np.searchsorted(ptr, edge, side='right')-1
            np.maximum.at(values, src, np.minimum(count[start:stop], bound[-1][dst[start:stop]]))
        bound.append(values)
    heap = []
    for source in sources:
        score = int(bound[length][source])
        if score:
            heapq.heappush(heap, (-score, -1, (int(source),), (), (), np.iinfo(np.int32).max))
    found = []
    while heap and len(found) < limit:
        neg_bound, depth, path, counts, signed, score = heapq.heappop(heap)
        remaining = length-len(path)+1
        if remaining == 0:
            found.append({'indices': list(path), 'body_ids': graph['body_id'][list(path)].tolist(),
                          'types': graph['type'][list(path)].tolist(), 'edge_counts': list(counts),
                          'signed_weights': list(signed), 'bottleneck': int(score)})
            continue
        cell = path[-1]
        for edge in range(ptr[cell], ptr[cell+1]):
            nxt = int(dst[edge])
            if nxt in path:
                continue
            next_score = min(score, int(count[edge]))
            upper = min(next_score, int(bound[remaining-1][nxt]))
            if upper > 0:
                heapq.heappush(heap, (-upper, -len(path)-1, path+(nxt,),
                                    counts+(int(count[edge]),), signed+(int(graph['data'][edge]),), next_score))
    return found


def paths():
    start = time.perf_counter()
    record = provenance()
    graph = load('build/graph_male.npz')
    g = groups('male', graph=graph)
    p1 = set(g['P1'])
    record['lengths'] = {}
    for length in (2, 3, 4):
        rows = top_paths(graph, g['Or47b'], g['pIP10'], length)
        for row in rows:
            row['through_P1'] = any(i in p1 for i in row['indices'][1:-1])
        record['lengths'][str(length)] = {'paths': rows, 'P1_count': sum(r['through_P1'] for r in rows),
                                         'path_count': len(rows)}
        print(f'paths length={length} count={len(rows)} elapsed={time.perf_counter()-start:.1f}s', flush=True)
    record['elapsed_seconds'] = time.perf_counter()-start
    record['ranking'] = 'Minimum unsigned edge count; top ten simple paths per exact length; signs ignored for ranking'
    record['share_denominator'] = 'Returned top paths only, not all anatomical paths'
    save('records/male_route_v1_paths.json', record)


def report():
    test = json.loads(Path('records/male_route_v1_test.json').read_text(encoding='utf-8'))
    quick = json.loads(Path('records/male_route_v1_quick.json').read_text(encoding='utf-8'))
    path_record = json.loads(Path('records/male_route_v1_paths.json').read_text(encoding='utf-8'))
    # Rebuild summaries from per-seed data; keep network identity separate
    # from the numerical network-rate metric.
    for stage, record in (('test', test), ('quick', quick)):
        record['summary'] = summarize(record['trials'])
        save('records/male_route_v1_'+stage+'.json', record)
    lines = ['# male_route_v1', '', '## Test', '',
             'Rates are Hz/neuron; ignition is a window fraction; active is a percent over the measured-period union.',
             'Values are mean +/- SE across 20 seeds, with windows averaged within seed. Quick is excluded.', '',
             '| Network | Drive | pIP10 | P1 | Network | Ignition | Active % | Or47b sampled Hz |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in test['summary']:
        lines.append('| '+row['network_kind']+' | '+row['drive']+' | '+' | '.join(
            f"{row[k]['mean']:.6g} +/- {row[k]['se']:.3g}" for k in
            ('pIP10', 'P1', 'network', 'ignition', 'active_percent', 'Or47b_sampled_hz'))+' |')
    lines += ['', 'Primary 240 Hz inference:', '', '```json', json.dumps(test.get('inference', {'verdict': 'unassessed'}), indent=2), '```',
              '', 'Descriptive 960 Hz analysis:', '', '```json', json.dumps(test.get('descriptive960', {'verdict': 'unassessed'}), indent=2), '```',
              '', '## Paths', '', 'Exact-length top-ten simple anatomical paths, ranked by minimum unsigned edge synapse count.',
              'Signs do not affect ranking. P1 shares refer only to returned paths. Full IDs and edge weights are in the paths JSON.', '',
              '| Synapses | Rank | Bottleneck | Types (source to target) | Through P1 |', '| ---: | ---: | ---: | --- | --- |']
    for length, entry in path_record['lengths'].items():
        for rank, row in enumerate(entry['paths'], 1):
            lines.append(f"| {length} | {rank} | {row['bottleneck']} | {' -> '.join(row['types'])} | {row['through_P1']} |")
    for length, entry in path_record['lengths'].items():
        lines += ['', f"Length {length}: P1 share {entry['P1_count']}/{entry['path_count']}.", '']
    lines += ['', '## Provenance and limitations', '', f"Protocol SHA256: {PROTOCOL_HASH}",
              f"Graph SHA256: {test['graph_sha256']}", f"Dictionary SHA256: {test['dictionary_sha256']}",
              'Environment: '+json.dumps(test['environment']),
              f"Wall seconds: quick={quick['elapsed_seconds']:.3f}, TEST={test['elapsed_seconds']:.3f}, paths={path_record['elapsed_seconds']:.3f}.",
              f"Complete: quick={quick['complete']}, TEST={test['complete']}.",
              'Random control is not superclass matched and can include sensory or readout cells; all lesion IDs are in raw metadata.',
              'Batch size one uses the unchanged fast_gpu backend. Fixed zero-dose targets retain the backend input/refractory convention.',
              'Source hashes, parameters, realized input, per-seed metrics and raw hashes are in the stage JSON files.',
              'Clean room: only this repository was inspected; the supplied dependency import path was used without inspecting adjacent project sources.',
              'No world or behavior was simulated. Anatomical top paths are descriptive; GPU reproducibility is not claimed bitwise.']
    Path('records/male_route_v1_report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('quick', 'test', 'paths', 'report'))
    parser.add_argument('--budget-seconds', type=float, default=1200)
    args = parser.parse_args()
    if args.stage == 'paths':
        paths()
    elif args.stage == 'report':
        report()
    else:
        run(args.stage, args.budget_seconds)


if __name__ == '__main__':
    main()
