"""Frozen sensory dose ladders in an isolated male Shiu network."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import time

import numpy as np
import torch
from scipy.sparse import csr_matrix

from flybench.dictionary import groups
from flybench.dictionary.entries import entries
from flybench.graph import load
from flybench.sim.fast_gpu import Simulator, Drive
from flybench.sim.params import Parameters
from .record import sha256, environment

PROTOCOL = Path('experiments/male_decides_v1.md')
DOSES = {'A': (30, 60, 120, 240, 480, 960), 'B': (30, 60, 120, 240), 'C': (0, 30, 60, 120)}
SEEDS = {'quick': (100, 101), 'calibration': tuple(range(10)), 'test': tuple(range(10, 30))}


class BatchRates:
    """Constant target rates, broadcast to the backend's seed columns."""
    def __init__(self, rates, batch):
        self.rates = np.asarray(rates, dtype=float)
        self.batch = batch

    def __mul__(self, scalar):
        return torch.from_numpy(self.rates.copy()) * scalar

    def __array__(self, dtype=None, copy=None):
        return np.array(np.broadcast_to(self.rates[:, None], (len(self.rates), self.batch)), dtype=dtype, copy=True)


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def stats(values):
    values = np.asarray(values, dtype=float)
    if len(values) < 2 or not np.isfinite(values).all():
        raise ValueError('At least two finite seed values required')
    return {'mean': float(values.mean()), 'se': float(values.std(ddof=1)/np.sqrt(len(values))), 'n': len(values)}


def ignition_threshold(rows):
    return next((r['dose'] for r in sorted(rows, key=lambda r: r['dose']) if r['ignition']['mean'] > .5), None)


def freeze_choice(rows, arm):
    metric = {'A': 'P1', 'B': 'LC10a', 'C': 'pIP10'}[arm]
    for row in sorted(rows, key=lambda r: r['dose']):
        value = row[metric]
        if value['mean'] > 2*value['se'] and (arm != 'A' or row['ignition']['mean'] <= .5):
            return {'dose': row['dose'], 'fallback': False, 'metric': metric}
    return {'dose': 960 if arm == 'A' else None, 'fallback': arm == 'A', 'metric': metric,
            'reason': 'No qualifying calibration dose'}


def summarize(trials):
    result = []
    for condition in dict.fromkeys(t['condition'] for t in trials):
        rows = [t for t in trials if t['condition'] == condition]
        result.append({'condition': condition, 'dose': rows[0]['dose'],
                       **{k: stats([r['metrics'][k] for r in rows]) for k in rows[0]['metrics']}})
    return result


def contrast(trials, condition, metric):
    a = {t['seed']: t['metrics'][metric] for t in trials if t['condition'] == condition}
    b = {t['seed']: t['metrics'][metric] for t in trials if t['condition'] == 'zero'}
    if set(a) != set(SEEDS['test']) or a.keys() != b.keys():
        raise ValueError('Held-out paired coverage mismatch')
    result = stats([a[s]-b[s] for s in sorted(a)])
    result['verdict'] = 'supported' if result['mean'] > 2*result['se'] else 'not supported'
    return result


def run(stage):
    start = time.perf_counter()
    frozen = None
    if stage == 'test':
        frozen = json.loads(Path('records/male_decides_v1_frozen.json').read_text(encoding='utf-8'))
        if frozen['protocol_sha256'] != sha256(PROTOCOL) or frozen['calibration_sha256'] != sha256('records/male_decides_v1_calibration.json'):
            raise ValueError('Frozen evidence changed')
    graph = load('build/graph_male.npz')
    g = groups('male', graph=graph)
    read = {k: g[k] for k in ('P1', 'pIP10', 'LC10a', 'DNa01', 'MDN', 'Or47b', 'L1', 'L2')}
    for side in ('L', 'R'):
        read['DNa02_'+side] = g['DNa02'][graph['side'][g['DNa02']] == side]
    visual = np.union1d(g['L1'], g['L2'])
    visual = visual[graph['side'][visual] == 'R']
    inputs = {'A': g['Or47b'], 'B': visual, 'C': g['P1']}
    if any(not len(v) for v in [*inputs.values(), *read.values()]):
        raise ValueError('Required population missing')
    for family, ids in (('ORN', inputs['A']), ('L1', np.intersect1d(visual, g['L1'])), ('L2', np.intersect1d(visual, g['L2']))):
        for name in sorted(set(graph['type'][ids]))[:20]:
            read[family+':'+str(name)] = ids[graph['type'][ids] == name]
    targets = np.unique(np.concatenate(list(inputs.values())))
    n = len(graph['body_id'])
    weights = csr_matrix((graph['data'], graph['indices'], graph['indptr']), shape=(n, n))
    sim = Simulator(weights, device='cuda', params=Parameters(dt=.2), kernel='shiu', groups=read, drive=Drive(tuple(targets), 0))
    conditions = [('zero', 0, {})]
    if stage == 'quick':
        conditions += [(arm+str(max(ds)), max(ds), {arm: max(ds)}) for arm, ds in DOSES.items()]
    elif stage == 'calibration':
        conditions += [(arm+str(dose), dose, {arm: dose}) for arm, ds in DOSES.items() for dose in ds]
    else:
        conditions += [(arm, v['dose'], {arm: v['dose']}) for arm, v in frozen['choices'].items() if v['dose'] is not None]
        if all(frozen['choices'][a]['dose'] is not None for a in ('A', 'B')):
            conditions.append(('combined', None, {a: frozen['choices'][a]['dose'] for a in ('A', 'B')}))
    rawdir = Path('build/records-raw/male_decides_v1_'+stage)
    rawdir.mkdir(parents=True, exist_ok=True)
    metadata = {'inputs': {k: v.tolist() for k, v in inputs.items()}, 'readouts': {k: v.tolist() for k, v in read.items()}}
    save(rawdir/'targets.json', metadata)
    source = ('flybench/experiment/male_decides.py', 'flybench/sim/fast_gpu.py', 'flybench/sim/params.py', 'flybench/dictionary/entries.py', 'flybench/dictionary/api.py')
    record = {'stage': stage, 'created_utc': datetime.now(timezone.utc).isoformat(), 'seeds': list(SEEDS[stage]),
              'protocol_sha256': sha256(PROTOCOL), 'graph_sha256': sha256('build/graph_male.npz'),
              'dictionary_sha256': sha256('build/dictionary_male.json'), 'source_sha256': {p: sha256(p) for p in source},
              'environment': environment('cuda'), 'parameters': asdict(sim.params), 'kernel': 'shiu', 'backend': 'fast_gpu',
              'windows': 20, 'warmup': 4, 'counts': {k: len(v) for k, v in read.items()},
              'input_counts': {k: len(v) for k, v in inputs.items()}, 'neurons': n,
              'proxy': next(e.to_dict() for e in entries('male') if e.name == 'Or47b'), 'trials': [], 'raw': []}
    if frozen:
        record['frozen_sha256'] = sha256('records/male_decides_v1_frozen.json')
    for condition, dose, drives in conditions:
        rates = np.zeros(len(targets))
        for arm, hz in drives.items():
            rates[np.searchsorted(targets, inputs[arm])] += hz
        sim.drive = Drive(tuple(targets), BatchRates(rates, len(SEEDS[stage])), 'poisson')
        state = sim.initial_batch_state(SEEDS[stage])
        measured = []
        path = rawdir/(condition+'.jsonl.gz')
        with gzip.open(path, 'wt', encoding='utf-8', newline='\n') as stream:
            for window in range(20):
                result = sim.run_batch(50, state=state)
                state = result.state
                metrics = {k: np.asarray(v) for k, v in result.group_rates_hz.items()}
                metrics.update(network=result.total_hz_per_neuron, total_spikes=result.counts.sum(axis=0),
                               network_total_hz=result.counts.sum(axis=0)/.05,
                               ignition=(result.total_hz_per_neuron > 30).astype(float),
                               DNa02_R_minus_L=result.group_rates_hz['DNa02_R']-result.group_rates_hz['DNa02_L'])
                stream.write(json.dumps({'window': window, 'metrics': {k: v.tolist() for k, v in metrics.items()},
                    'sampled_input_hz': result.sampled_drive_hz[targets].mean(axis=0).tolist()})+'\n')
                if window >= 4:
                    measured.append(metrics)
        for j, seed in enumerate(SEEDS[stage]):
            record['trials'].append({'condition': condition, 'dose': dose, 'seed': seed,
                'metrics': {k: float(np.mean([m[k][j] for m in measured])) for k in measured[0]}})
        record['raw'].append({'path': path.as_posix(), 'sha256': sha256(path), 'bytes': path.stat().st_size})
        print(f'{stage} {condition}: {time.perf_counter()-start:.1f}s', flush=True)
        save('build/male_decides_v1_'+stage+'_checkpoint.json', record)
    record['raw'].append({'path': (rawdir/'targets.json').as_posix(), 'sha256': sha256(rawdir/'targets.json')})
    record['summary'] = summarize(record['trials'])
    record['elapsed_seconds'] = time.perf_counter()-start
    if sha256(PROTOCOL) != record['protocol_sha256']:
        raise ValueError('Protocol changed')
    if stage == 'test':
        record['verdicts'] = {m: contrast(record['trials'], a, metric) if frozen['choices'][a]['dose'] is not None else {'verdict': 'unassessed'}
            for m, a, metric in [('M1', 'A', 'P1'), ('M2', 'B', 'LC10a'), ('M3', 'C', 'pIP10')]}
        record['M4'] = {'verdict': 'descriptive', 'smell_ignition_threshold': frozen['smell_ignition_threshold'],
            'ignition': {r['condition']: r['ignition'] for r in record['summary']},
            'combined_P1_contrast': contrast(record['trials'], 'combined', 'P1') if any(c[0] == 'combined' for c in conditions) else None}
        if record['M4']['combined_P1_contrast']:
            record['M4']['combined_P1_contrast']['verdict'] = 'descriptive'
    save(('build' if stage == 'quick' else 'records')+'/male_decides_v1_'+stage+'.json', record)


def freeze():
    path = 'records/male_decides_v1_calibration.json'
    record = json.loads(Path(path).read_text(encoding='utf-8'))
    if record['seeds'] != list(SEEDS['calibration']) or record['protocol_sha256'] != sha256(PROTOCOL):
        raise ValueError('Invalid calibration provenance')
    rows = {a: [r for r in record['summary'] if r['condition'].startswith(a)] for a in DOSES}
    for a in DOSES:
        if [r['dose'] for r in rows[a]] != list(DOSES[a]):
            raise ValueError('Incomplete ladder')
    save('records/male_decides_v1_frozen.json', {'created_utc': datetime.now(timezone.utc).isoformat(),
        'protocol_sha256': sha256(PROTOCOL), 'calibration_sha256': sha256(path),
        'choices': {a: freeze_choice(rows[a], a) for a in DOSES}, 'smell_ignition_threshold': ignition_threshold(rows['A'])})


def report():
    lines = ['# male_decides_v1', '', 'Rates are Hz per neuron. Ignition is a measured-window fraction. Network totals are retained in JSON.', '']
    for stage in ('calibration', 'test'):
        r = json.loads(Path('records/male_decides_v1_'+stage+'.json').read_text(encoding='utf-8'))
        lines += ['## '+stage.capitalize(), '', '| Condition | P1 | LC10a | pIP10 | Network | Ignition |', '| --- | ---: | ---: | ---: | ---: | ---: |']
        for row in r['summary']:
            lines.append('| '+row['condition']+' | '+' | '.join(f"{row[k]['mean']:.6g} +/- {row[k]['se']:.3g}" for k in ('P1', 'LC10a', 'pIP10', 'network', 'ignition'))+' |')
        lines += ['', f"Elapsed: {r['elapsed_seconds']:.3f} seconds.", '']
        if stage == 'test':
            lines += ['```json', json.dumps({'verdicts': r['verdicts'], 'M4': r['M4']}, indent=2), '```', '']
            vision = next((x for x in r['summary'] if x['condition'] == 'B'), None)
            if vision:
                lines += ['Vision DNa02 R minus L: '+json.dumps(vision['DNa02_R_minus_L']), '']
    lines += ['## Frozen choices', '', '```json', Path('records/male_decides_v1_frozen.json').read_text(encoding='utf-8').strip(), '```', '',
        'SE uses independent seeds, with windows averaged within seed. Calibration is separate from held-out inference.',
        'Right-side L1/L2 drive is CHOSEN. Or47b is a glomerular proxy. Direct-target type summaries are in JSON; fewer than 20 types may exist.',
        'Clean room: only this repository was inspected. The supplied dependency import path was used without inspecting adjacent project sources.',
        'No world, behavior, mating outcome or biological ignition threshold is inferred. GPU numerical reproducibility is not claimed bitwise.']
    Path('records/male_decides_v1_report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('quick', 'calibration', 'freeze', 'test', 'report'))
    args = parser.parse_args()
    if args.stage == 'freeze':
        freeze()
    elif args.stage == 'report':
        report()
    else:
        run(args.stage)


if __name__ == '__main__':
    main()
