"""Preregistered calibration, frozen selection and held-out hearing tests."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import numpy as np
from scipy.sparse import csr_matrix
from flybench.graph import load
from flybench.dictionary import groups as dictionary_groups
from flybench.sim.fast_gpu import Simulator, Drive
from flybench.sim.params import Parameters
from flybench.song import Song
from flybench.ear import rates, RMS_FULL
from .runner import BatchRates, select_groups
from .record import sha256, environment

PROTOCOL = Path('experiments/female_hearing_v1.md')
PREFIX = Path('records/female_hearing_v1')
READOUTS = ('vpoEN', 'vpoDN', 'pC1')
DRIVES = ('JO-A', 'JO-B', 'SAG', 'vpoEN')


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def seeds_for(stage):
    return {'quick': (0, 1), 'calibration': tuple(range(10)), 'test': tuple(range(10, 30))}[stage]


def condition(state='virgin', song=False, jo=180, direct=0, gain=1.0):
    return dict(state=state, song=song, jo_max_hz=jo, direct_vpoEN_hz=direct, excitatory_gain=gain)


def key(c):
    return json.dumps(c, sort_keys=True)


def conditions(stage, frozen=None):
    values = []
    doses = (60, 180, 360, 720) if stage != 'test' else (frozen['jo']['dose'],)
    for dose in doses:
        values += [condition(song=s, jo=dose) for s in (False, True)]
    doses = (0, 60, 180, 360) if stage != 'test' else (0, frozen['vpoEN']['dose'])
    for state in ('virgin', 'mated'):
        values += [condition(state=state, direct=d) for d in doses]
    for gain in (1.0, 1.3):
        for state in ('virgin', 'mated'):
            values += [condition(state=state, song=s, gain=gain) for s in (False, True)]
    return list({key(c): c for c in values}.values())


def summary(values, descriptive=False):
    values = np.asarray(values, dtype=float)
    if len(values) < 2 or not np.isfinite(values).all():
        raise ValueError('Need finite paired differences')
    mean, se = float(values.mean()), float(values.std(ddof=1)/np.sqrt(len(values)))
    return dict(mean=mean, se=se, n=len(values), paired_values=values.tolist(),
                verdict='descriptive' if descriptive else ('supported' if mean > 2*se else 'not supported'))


def differences(record, positive, negative, group):
    def get(c):
        return {t['seed']: t['rates_hz'][group] for t in record['trials'] if t['condition'] == c}
    a, b = get(positive), get(negative)
    if set(a) != set(record['seeds']) or set(a) != set(b):
        raise ValueError('Incomplete seed pairs')
    return [a[s]-b[s] for s in record['seeds']]


def contrast(record, a, b, group='vpoDN', descriptive=False):
    return summary(differences(record, a, b, group), descriptive)


def choose(rows, fallback):
    for row in sorted(rows, key=lambda r: r['dose']):
        if row['mean'] > 2*row['se']:
            return dict(dose=row['dose'], rule='lowest dose with difference > 2 SE', fallback=False)
    return dict(dose=fallback, rule='no transfer', fallback=True)


def calibration_result(record):
    a, b, c = [], [], []
    for dose in (60, 180, 360, 720):
        a.append(dict(dose=dose, **{g: contrast(record, condition(song=True, jo=dose), condition(jo=dose), g) for g in READOUTS[:2]}))
    for state in ('virgin', 'mated'):
        for dose in (0, 60, 180, 360):
            cfg = condition(state=state, direct=dose)
            b.append(dict(state=state, dose=dose,
                          realized_vpoEN=summary([t['rates_hz']['vpoEN'] for t in record['trials'] if t['condition'] == cfg], True),
                          **{g: contrast(record, cfg, condition(state=state), g) for g in READOUTS[:2]}))
    for gain in (1.0, 1.3):
        c.append(dict(gain=gain, **{g: contrast(record, condition(song=True, gain=gain), condition(gain=gain), g, True) for g in READOUTS[:2]}))
    return dict(a=a, b=b, c=c)


def freeze(record):
    validate(record)
    if record['stage'] != 'calibration':
        raise ValueError('Only full calibration can freeze')
    result = calibration_result(record)
    return dict(jo=choose([dict(dose=r['dose'], **r['vpoEN']) for r in result['a']], 720),
                vpoEN=choose([dict(dose=r['dose'], **r['vpoDN']) for r in result['b'] if r['state'] == 'virgin' and r['dose'] > 0], 360),
                protocol_sha256=record['protocol']['sha256'], graph_sha256=record['graph']['sha256'],
                calibration_seeds=record['seeds'], test_seeds=list(seeds_for('test')),
                created_utc=datetime.now(timezone.utc).isoformat())


def test_result(record, frozen):
    jo, en = frozen['jo']['dose'], frozen['vpoEN']['dose']
    virgin = differences(record, condition(direct=en), condition(), 'vpoDN')
    mated = differences(record, condition(state='mated', direct=en), condition(state='mated'), 'vpoDN')
    return dict(T1=contrast(record, condition(song=True, jo=jo), condition(jo=jo)),
                T2=summary(virgin), T3=summary(np.asarray(mated)-virgin, True),
                T3_mated_relay=summary(mated, True), T3_mated_smaller=float(np.mean(mated)) < float(np.mean(virgin)),
                T4=contrast(record, condition(song=True, gain=1.3), condition(gain=1.3), descriptive=True))


def scaled_weights(graph, gain):
    data = np.asarray(graph['data'], dtype=float).copy()
    data[data > 0] *= gain
    n = len(graph['body_id'])
    return csr_matrix((data, graph['indices'], graph['indptr']), shape=(n, n))


def run(stage, graph, groups, graph_sha='synthetic', device='cuda', frozen=None, progress=False):
    start = time.perf_counter()
    raw = PROTOCOL.read_bytes()
    import hashlib
    protocol = dict(text=raw.decode('utf-8'), sha256=hashlib.sha256(raw).hexdigest())
    if stage == 'test' and (frozen is None or frozen['protocol_sha256'] != protocol['sha256'] or frozen['graph_sha256'] != graph_sha):
        raise ValueError('Frozen selection does not match protocol and graph')
    seeds, windows = seeds_for(stage), 6 if stage == 'quick' else 20
    targets = np.concatenate([groups[k] for k in DRIVES])
    if len(np.unique(targets)) != len(targets) or any(len(groups[g]) == 0 for g in (*DRIVES, *READOUTS)):
        raise ValueError('Nonempty groups and disjoint drive targets required')
    positions, offset = {}, 0
    for name in DRIVES:
        positions[name] = slice(offset, offset+len(groups[name]))
        offset += len(groups[name])
    record = dict(schema_version='hearing-1', stage=stage, protocol=protocol, seeds=list(seeds),
                  graph=dict(sha256=graph_sha, neurons=len(graph['body_id'])), environment=environment(device),
                  backend='fast_gpu', kernel='shiu', dtype='float32', parameters=asdict(Parameters(dt=.2)),
                  timing=dict(window_ms=50, windows=windows, warmup=4, drive_slice_ms=5),
                  ear=dict(RMS_FULL=RMS_FULL, padlen=27),
                  groups={g: dict(indices=idx.tolist(), body_ids=graph['body_id'][idx].tolist(), count=len(idx)) for g, idx in groups.items()},
                  source_sha256={str(p).replace('\\', '/'): sha256(p) for p in (Path('flybench/experiment/hearing.py'), Path('flybench/experiment/runner.py'), Path('flybench/sim/fast_gpu.py'), Path('flybench/sim/params.py'), Path('flybench/song.py'), Path('flybench/ear.py'), Path('flybench/dictionary/entries.py'))},
                  frozen=frozen, trials=[])
    for gain in (1.0, 1.3):
        sim = Simulator(scaled_weights(graph, gain), device=device, params=Parameters(dt=.2), kernel='shiu', groups=groups, drive=Drive(tuple(targets), 0))
        for cfg in [c for c in conditions(stage, frozen) if c['excitatory_gain'] == gain]:
            state = sim.initial_batch_state(seeds)
            song = Song(amplitude=int(cfg['song']))
            trials = [dict(condition=cfg, seed=s, windows=[]) for s in seeds]
            for w in range(windows):
                ear = rates(song.window(), jo_max_hz=cfg['jo_max_hz'])
                cells = {g: np.zeros((len(groups[g]), len(seeds))) for g in READOUTS}
                network = np.zeros(len(seeds))
                slices = [[] for _ in seeds]
                for i in range(10):
                    requested = np.zeros(len(targets))
                    for g in DRIVES:
                        value = (50 if cfg['state'] == 'virgin' else 0) if g == 'SAG' else cfg['direct_vpoEN_hz'] if g == 'vpoEN' else ear[g][i]
                        requested[positions[g]] = value
                    sim.drive = Drive(tuple(targets), BatchRates(requested, .2), 'poisson')
                    result = sim.run_batch(5, state=state)
                    for g in cells:
                        cells[g] += result.rates_hz[groups[g]]/10
                    network += result.total_hz_per_neuron/10
                    for j in range(len(seeds)):
                        slices[j].append({label: {g: array[groups[g], j].tolist() for g in DRIVES} for label, array in
                                          (('requested_hz', result.requested_hz), ('sampled_hz', result.sampled_drive_hz), ('delivered_hz', result.delivered_hz))})
                for j, trial in enumerate(trials):
                    trial['windows'].append(dict(index=w, cell_rates_hz={g: v[:, j].tolist() for g, v in cells.items()},
                        rates_hz={**{g: float(v[:, j].mean()) for g, v in cells.items()}, 'network': float(network[j])},
                        network_total_spikes=int(round(network[j]*.05*len(graph['body_id']))), drive_slices=slices[j]))
            for trial in trials:
                measured = trial['windows'][4:]
                trial['rates_hz'] = {g: float(np.mean([w['rates_hz'][g] for w in measured])) for g in (*READOUTS, 'network')}
                trial['cell_rates_hz'] = {g: np.mean([w['cell_rates_hz'][g] for w in measured], axis=0).tolist() for g in READOUTS}
                trial['ignition_fraction'] = float(np.mean([w['rates_hz']['network'] > 30 for w in measured]))
            record['trials'].extend(trials)
            if progress:
                print(f"{stage}: {cfg}; {len(seeds)} seeds; {time.perf_counter()-start:.1f} s", flush=True)
        del sim, state, result
    record['elapsed_seconds'] = time.perf_counter()-start
    validate(record)
    return record


def validate(record):
    stage = record['stage']
    if record['seeds'] != list(seeds_for(stage)):
        raise ValueError('Seed split violated')
    expected = {(key(c), s) for c in conditions(stage, record.get('frozen')) for s in seeds_for(stage)}
    found = [(key(t['condition']), t['seed']) for t in record['trials']]
    if len(found) != len(expected) or set(found) != expected:
        raise ValueError('Incomplete or duplicate trial coverage')
    for t in record['trials']:
        if len(t['windows']) != (6 if stage == 'quick' else 20):
            raise ValueError('Wrong window count')
        for w in t['windows']:
            if len(w['drive_slices']) != 10 or set(w['cell_rates_hz']) != set(READOUTS):
                raise ValueError('Missing cell or drive data')
    json.dumps(record, allow_nan=False)
    return record


def ignition(record):
    return [dict(condition=c, fraction=float(np.mean([t['ignition_fraction'] for t in record['trials'] if t['condition'] == c]))) for c in conditions(record['stage'], record.get('frozen'))]


def make_report():
    calpath, testpath, freezepath = [Path(str(PREFIX)+suffix) for suffix in ('_calibration.json', '_test.json', '_frozen.json')]
    cal, test, frozen = [json.loads(p.read_text(encoding='utf-8')) for p in (calpath, testpath, freezepath)]
    validate(cal); validate(test)
    if frozen['calibration_sha256'] != sha256(calpath) or test['frozen_sha256'] != sha256(freezepath):
        raise ValueError('Evidence chain changed')
    result = dict(calibration=calibration_result(cal), frozen=frozen, pre_registered_test=test_result(test, frozen),
                  ignition=dict(calibration=ignition(cal), pre_registered_test=ignition(test)),
                  elapsed_seconds=dict(calibration=cal['elapsed_seconds'], test=test['elapsed_seconds']),
                  evidence_sha256={p.name: sha256(p) for p in (calpath, testpath, freezepath)})
    out = Path(str(PREFIX)+'_report.json')
    save(out, {'Result': result})
    r = json.loads(out.read_text(encoding='utf-8'))['Result']
    def fmt(v):
        return f"{v['mean']:.6g} +/- {v['se']:.6g}"
    lines = ['# female_hearing_v1', '', 'All differences are paired Hz/cell, mean +/- SE.', '', '## calibration', '', '| Arm | State | Dose / gain | vpoEN difference | vpoDN difference |', '| --- | --- | ---: | ---: | ---: |']
    for arm in ('a', 'b', 'c'):
        for row in r['calibration'][arm]:
            lines.append(f"| {arm} | {row.get('state', 'virgin')} | {row.get('dose', row.get('gain'))} | {fmt(row['vpoEN'])} | {fmt(row['vpoDN'])} |")
    lines += ['', 'Direct-drive realized vpoEN firing (mean +/- SE):']
    for row in r['calibration']['b']:
        lines.append(f"- {row['state']}, {row['dose']} Hz: {fmt(row['realized_vpoEN'])}")
    lines += ['', 'Frozen selection: '+json.dumps(r['frozen'], sort_keys=True), '', '## pre-registered test', '', '| Test | Difference | Verdict |', '| --- | ---: | --- |']
    for name in ('T1', 'T2', 'T3', 'T4'):
        row = r['pre_registered_test'][name]
        lines.append(f"| {name} | {fmt(row)} | {row['verdict']} |")
    lines += ['', 'T3 is mated-minus-virgin difference of relay differences; negative supports the descriptive direction.',
              'Mated relay: '+fmt(r['pre_registered_test']['T3_mated_relay']), '', '## Ignition', '', '| Stage | Condition | Fraction >30 Hz/neuron |', '| --- | --- | ---: |']
    for stage, rows in r['ignition'].items():
        for row in rows:
            lines.append(f"| {stage} | {json.dumps(row['condition'], sort_keys=True)} | {row['fraction']:.6g} |")
    lines += ['', 'Elapsed seconds: '+json.dumps(r['elapsed_seconds']), '',
              'The gain-1 sensitivity controls include all four state/song conditions. Identical configurations are reused within a stage. Quick data are excluded.',
              'No behavioural conclusion follows from these isolated neuronal readouts.', '', '## Preregistration', '', cal['protocol']['text']]
    Path(str(PREFIX)+'_report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('quick', 'calibration', 'freeze', 'test', 'report'))
    args = parser.parse_args()
    if args.stage == 'report':
        make_report(); return
    calpath, freezepath = Path(str(PREFIX)+'_calibration.json'), Path(str(PREFIX)+'_frozen.json')
    if args.stage == 'freeze':
        if freezepath.exists():
            raise ValueError('Frozen decision already exists')
        frozen = freeze(json.loads(calpath.read_text(encoding='utf-8')))
        frozen['calibration_sha256'] = sha256(calpath)
        save(freezepath, frozen)
        print(json.dumps(frozen), flush=True); return
    frozen = json.loads(freezepath.read_text(encoding='utf-8')) if args.stage == 'test' else None
    if frozen and frozen['calibration_sha256'] != sha256(calpath):
        raise ValueError('Calibration changed after freezing')
    graphpath = Path('build/graph_female.npz')
    graph = load(graphpath)
    if any(graph['meta'].get(k) != v for k, v in dict(dataset='FAFB', version='783', sign_rule='shiu2024-parquet', connectivity_source='shiu').items()):
        raise ValueError('Unexpected graph metadata')
    groups = select_groups(graph)
    groups['vpoEN'] = dictionary_groups('female', graph=graph)['vpoEN']
    if {g: len(groups[g]) for g in READOUTS} != dict(vpoEN=4, vpoDN=2, pC1=10):
        raise ValueError('Unexpected readout counts')
    record = run(args.stage, graph, groups, sha256(graphpath), frozen=frozen, progress=True)
    if frozen:
        record['frozen_sha256'] = sha256(freezepath)
    destination = Path('build/female_hearing_v1_quick.json') if args.stage == 'quick' else Path(str(PREFIX)+'_'+args.stage+'.json')
    save(destination, record)


if __name__ == '__main__':
    main()
