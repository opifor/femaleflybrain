"""Fixed synthetic release direction diagnostic; no parameter selection."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np
from scipy.sparse import csr_matrix

PROTOCOL = 'experiments/direction_probe_v1.md'
PROTOCOL_HASH = '1f25c7ab1f2ae166a837fc322e3a5f300f52f8b953f4c44698eb6141636e3c53'
GAMMAS = (.01, .03, .1, .3, 1., 3.)
CAPS = (('uncapped', None), ('1/2.2', 1/2.2), ('1/5', .2))
SOURCES = {'K1': 'AMMC-B1-candidate', 'K2': 'AMMC-B1-candidate-graph'}
RAW = Path('build/records-raw')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def grid():
    return [dict(gamma=g, ceiling=name, flux=g if cap is None else min(g, cap))
            for name, cap in CAPS for g in GAMMAS]


def flux_table(value, n):
    result = np.zeros((5000, n), dtype=np.float64)
    result[1000:] = value
    return result


def source_rows(dictionary, arm):
    rows = np.asarray(dictionary[SOURCES[arm]], dtype=np.int64)
    if rows.ndim != 1 or len(rows) != len(np.unique(rows)) or not len(rows):
        raise ValueError('Invalid source population')
    return rows


def paired(arm, base, seeds, baseline_seeds):
    if list(seeds) != list(baseline_seeds) or len(set(seeds)) != len(seeds):
        raise ValueError('Seed pairing mismatch')
    arm, base = np.asarray(arm), np.asarray(base)
    if arm.shape != base.shape or arm.shape[-1] != len(seeds):
        raise ValueError('Trial shape mismatch')
    return arm - base


def classify(cell_delta):
    cells = np.asarray(cell_delta, dtype=float)
    mean = float(cells.mean())
    if mean < -1 and np.all(cells <= 3):
        return 'suppression'
    if abs(mean) <= 1 and np.all(np.abs(cells) <= 3):
        return 'equivalence-zero'
    if mean > 1:
        return 'unexplained increase'
    return 'unclassified (cell heterogeneity)'


def stats(values):
    values = np.asarray(values, dtype=float)
    return dict(mean=float(values.mean()),
                se=float(values.std(ddof=1)/np.sqrt(values.size)) if values.size > 1 else None)


def arrived_mass(original, value, final_step, delay_steps=9):
    bins = max(0, final_step-delay_steps-1000)
    return np.asarray(abs(original).sum(axis=0)).ravel() * value * .2 * bins


def resolve(graph):
    from flybench.dictionary import groups
    dictionary = groups('female', graph=graph)
    file = Path('build/dictionary_fafb.json')
    if file.exists():
        # Refuse an unknown serialization rather than silently use another list.
        data = json.loads(file.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict) or not all(k in data for k in SOURCES.values()):
            raise ValueError('Unrecognized dictionary_fafb serialization')
        for name in SOURCES.values():
            ids = data[name]
            if not isinstance(ids, list) or not np.array_equal(ids, dictionary[name]):
                raise ValueError('Dictionary file/API identity mismatch')
        evidence = {str(file).replace('\\', '/'): sha(file)}
    else:
        evidence = {str(p).replace('\\', '/'): sha(p)
                    for p in sorted(Path('flybench/dictionary').glob('*.py'))}
        evidence['flybench/graph/select.py'] = sha('flybench/graph/select.py')
    read = {k: dictionary[k] for k in ('vpoEN', 'vpoDN', 'vpoDN-GABA-input',
                                       'pC1a', 'pC1b', 'pC1c', 'pC1d', 'pC1e')}
    read['pC1'] = np.unique(np.concatenate([read['pC1'+s] for s in 'abcde']))
    if len(read['vpoEN']) != 4 or any(not len(v) for v in read.values()):
        raise ValueError('Unexpected readout populations')
    sources = {arm: source_rows(dictionary, arm) for arm in SOURCES}
    if [len(sources[a]) for a in SOURCES] != [39, 23]:
        raise ValueError('Unexpected B1 populations')
    return sources, read, evidence


def simulate(weights, sources, read, arm, value, seeds, path, deadline):
    import torch
    from flybench.sim.fast_gpu import Simulator
    from flybench.sim.params import Parameters
    from flybench.sim.release import GradedRelease
    start = time.perf_counter()
    release = None if arm == 'K0' else GradedRelease(sources[arm], flux_table(value, len(sources[arm])))
    sim = Simulator(weights, params=Parameters(dt=.2), kernel='shiu', device='cuda', release=release)
    outgoing = None if release is None else dict(
        installed=sim.release.counts[sources[arm]].tolist(),
        scaled=sim.release.scaled_source_counts.tolist())
    counts = []
    state = None
    result = None
    for window in range(20):
        if time.perf_counter() >= deadline:
            break
        result = sim.run_batch(50, seeds=seeds) if state is None else sim.run_batch(50, state=state)
        state = result.state
        counts.append(result.counts.astype(np.int32))
        print(json.dumps(dict(arm=arm, flux=value, window=window+1,
                              seconds=round(time.perf_counter()-start, 2))), flush=True)
    arrays = np.stack(counts) if counts else np.empty((0, weights.shape[0], len(seeds)), dtype=np.int32)
    drop = np.zeros((weights.shape[0], len(seeds))) if result is None or result.dropped_flux is None else result.dropped_flux
    mass = np.zeros(weights.shape[0]) if release is None or state is None else arrived_mass(sim.release.original_rows, value, state.step, sim.delay_steps)
    np.savez_compressed(path, counts=arrays, dropped_flux=drop, arrived_mass=mass, seeds=seeds)
    info = dict(arm=arm, flux=value, seeds=list(seeds), windows=len(counts),
                complete=len(counts)==20, wall_seconds=time.perf_counter()-start,
                raw=str(path).replace('\\', '/'), raw_sha256=sha(path), outgoing=outgoing)
    if info['complete']:
        measured = arrays[4:]
        network = measured.sum(axis=1) / .05 / weights.shape[0]
        ratios = np.divide(drop, mass[:, None], out=np.zeros_like(drop), where=mass[:, None]>0)
        barred = np.flatnonzero(np.any(ratios > .05, axis=1))
        info.update(rates={k: (measured[:, rows].sum(axis=0)/.8).tolist() for k, rows in read.items()},
                    network=stats(network.mean(axis=0)), ignition=float((network>30).mean()),
                    ignition_by_seed=(network>30).mean(axis=0).tolist(),
                    active_window_fraction=float((measured>0).mean()),
                    active_overall_fraction=float((measured.sum(axis=0)>0).mean()),
                    b1_spikes={a: int(measured[:, rows].sum()) for a, rows in sources.items()},
                    b1_warmup_spikes={a: int(arrays[:4, rows].sum()) for a, rows in sources.items()},
                    drop=dict(total=float(drop.sum()), max_target_loss=float(ratios.max()),
                              barred_target_count=len(barred), barred_target_indices=barred.tolist(),
                              status='saturation interpretation barred' if len(barred) else 'no target exceeds 5% loss'),
                    interpretation='ignited, not interpretable' if (network>30).mean()>.5 else 'not ignited')
    # Break simulator/state ownership cycles before allocating the next graph.
    if state is not None:
        state.owner = None
    del sim, state, result
    torch.cuda.empty_cache()
    return info, arrays[:4]


def analyze(record):
    conditions = record['conditions']
    baseline = next((c for c in conditions if c['arm']=='K0' and c['complete']), None)
    rows = []
    if baseline is None:
        return rows
    for point in record['grid']:
        for arm in SOURCES:
            condition = next((c for c in conditions if c['arm']==arm and c['flux']==point['flux'] and c['complete']), None)
            if condition is None:
                continue
            row = dict(**point, arm=arm, ignition=condition['ignition'], drop=condition['drop'],
                       interpretation=condition['interpretation'])
            for name in ('vpoEN', 'vpoDN'):
                delta = paired(condition['rates'][name], baseline['rates'][name], condition['seeds'], baseline['seeds'])
                row[name] = dict(**stats(delta.mean(axis=0)), cell_delta=delta.mean(axis=1).tolist(),
                                 classification=classify(delta.mean(axis=1)))
            rows.append(row)
    return rows


def report(record, target):
    rows = record['rows']
    lines = ['# Direction probe v1', '', 'Status: '+('COMPLETE' if record['complete'] else 'PARTIAL'),
             '', 'Differences are paired Hz/neuron, mean +/- SE; classes use fixed effect bounds.',
             'Zero SE is expected with constant deterministic input and no random drive.',
             'A silent K0 creates a firing-rate floor: equivalence cannot refute inhibitory connectivity.',
             '', '| gamma | ceiling | arm | vpoEN delta +/- SE | class | vpoDN delta +/- SE | class | ignition | max target loss |',
             '|---:|---|---|---|---|---|---|---:|---:|']
    for row in rows:
        en, dn = row['vpoEN'], row['vpoDN']
        lines.append(f"| {row['gamma']:g} | {row['ceiling']} | {row['arm']} | {en['mean']:.6g} +/- {en['se']} | {en['classification']} | {dn['mean']:.6g} +/- {dn['se']} | {dn['classification']} | {row['ignition']:.6g} | {row['drop']['max_target_loss']:.6g} |")
    lines += ['', '## D1--D5', '',
              '- D1/D2: descriptive direction classes above; no gain changes or E5 efficacy claim.',
              '- D3: per-target/per-seed dropped and arrived mass are in the raw NPZ files.']
    for c in record['conditions']:
        if c['complete']:
            lines.append(f"- {c['arm']} flux={c['flux']:g}: {c['interpretation']}; {c['drop']['status']}; barred targets={c['drop']['barred_target_count']}; B1 measured spikes={c['b1_spikes']}; warmup match={c.get('warmup_matches_K0', True)}.")
    lines += ['- D4: source neurons may spike; zero installed/scaled outgoing counts establish inert ordinary outputs.',
              '- D5: '+json.dumps(record['agreement']), '', '## Provenance', '',
              'Protocol SHA256: '+record['protocol_sha256'],
              'Graph SHA256: '+record['graph_sha256'],
              'Release SHA256: '+record['source_sha256']['flybench/sim/release.py'],
              f"Wall seconds: {record['wall_seconds']:.3f}",
              'Dictionary API and resolved population identities are hashed in the JSON record.',
              'No core, hook, dictionary, ear, gain or parameter changes except prescribed dt.',
              'Clean room: excluded trees were not inspected; only the authorized runtime dependency path was supplied externally.',
              'All raw artifact hashes and environment versions are in the JSON.']
    Path(target).write_text('\n'.join(lines)+'\n', encoding='utf-8')


def run(stage, budget=2400):
    import scipy
    import torch
    from flybench.graph import load
    from flybench.sim.params import Parameters
    start = time.perf_counter()
    if sha(PROTOCOL) != PROTOCOL_HASH:
        raise ValueError('Preregistration hash mismatch')
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA unavailable; no fallback acceptance evidence')
    graph = load('build/graph_female.npz')
    sources, read, dictionary_hashes = resolve(graph)
    n = len(graph['body_id'])
    weights = csr_matrix((graph['data'], graph['indices'], graph['indptr']), shape=(n,n))
    rawdir = RAW/('direction_probe_v1_'+stage)
    rawdir.mkdir(parents=True, exist_ok=True)
    identity = lambda rows: dict(indices=rows.tolist(), body_ids=graph['body_id'][rows].tolist())
    identities = dict(sources={k: identity(v) for k,v in sources.items()},
                      readouts={k: identity(v) for k,v in read.items()})
    save(rawdir/'identities.json', identities)
    seeds = (100,) if stage=='quick' else tuple(range(10))
    points = [grid()[0], grid()[5]] if stage=='quick' else grid()
    record = dict(stage=stage, created_utc=datetime.now(timezone.utc).isoformat(),
                  protocol_sha256=PROTOCOL_HASH, graph_sha256=sha('build/graph_female.npz'),
                  dictionary_sha256=dictionary_hashes, resolved_identities_sha256=sha(rawdir/'identities.json'),
                  identities=identities, source_sha256={p: sha(p) for p in (
                      'flybench/experiment/direction_probe.py', 'flybench/sim/release.py',
                      'flybench/sim/fast_gpu.py', 'flybench/sim/lif.py', 'flybench/sim/params.py')},
                  environment=dict(python=platform.python_version(), os=platform.system(),
                                   numpy=np.__version__, scipy=scipy.__version__, torch=torch.__version__,
                                   cuda=torch.version.cuda, device=torch.cuda.get_device_name(), dtype='float32'),
                  parameters=asdict(Parameters(dt=.2)), kernel='shiu', backend='fast_gpu',
                  seeds=list(seeds), neurons=n, grid=points, conditions=[], complete=False)
    schedule = [('K0',0.)]
    for point in points:
        for arm in SOURCES:
            if (arm,point['flux']) not in schedule:
                schedule.append((arm,point['flux']))
    record['schedule'] = schedule
    checkpoint = rawdir/'checkpoint.json'
    warmup = None
    durations = []
    for index, (arm,value) in enumerate(schedule):
        if durations and max(durations) > start+budget-time.perf_counter():
            record['stop_reason'] = 'insufficient remaining budget for prior measured condition duration'
            break
        condition, head = simulate(weights, sources, read, arm, value, seeds,
                                   rawdir/f'condition_{index:02d}.npz', start+budget)
        if arm=='K0':
            warmup = head
        else:
            condition['warmup_matches_K0'] = bool(np.array_equal(head, warmup))
        record['conditions'].append(condition)
        durations.append(condition['wall_seconds'])
        save(checkpoint, record)
        if not condition['complete'] or condition.get('warmup_matches_K0') is False:
            record['stop_reason'] = 'incomplete condition or failed warmup control'
            break
    record['complete'] = (len(record['conditions'])==len(schedule)
                          and all(c['complete'] and c.get('warmup_matches_K0', True) for c in record['conditions']))
    record['rows'] = analyze(record)
    record['agreement'] = []
    for point in points:
        pair = [r for r in record['rows'] if r['gamma']==point['gamma'] and r['ceiling']==point['ceiling']]
        record['agreement'].append(dict(**point, vpoEN_same=None if len(pair)!=2 else pair[0]['vpoEN']['classification']==pair[1]['vpoEN']['classification'],
                                        vpoDN_same=None if len(pair)!=2 else pair[0]['vpoDN']['classification']==pair[1]['vpoDN']['classification']))
    record['wall_seconds'] = time.perf_counter()-start
    save(checkpoint, record)
    prefix = 'records/direction_probe_v1' if stage=='full' else str(rawdir/'direction_probe_v1_quick')
    save(prefix+'_results.json', record)
    report(record, prefix+'_report.md')
    print(json.dumps(dict(complete=record['complete'], wall_seconds=record['wall_seconds'], conditions=len(record['conditions']))), flush=True)
    return 0 if record['complete'] else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=('quick', 'full'))
    parser.add_argument('--budget', type=float, default=2400)
    args = parser.parse_args()
    raise SystemExit(run(args.stage, args.budget))
