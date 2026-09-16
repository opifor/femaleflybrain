"""Preregistered two-body courtship using persistent GPU seed columns."""
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
from scipy.stats import spearmanr
from flybench import eye, scent, ear, motor
from flybench.dictionary import groups
from flybench.dictionary.entries import entries
from flybench.graph import load
from flybench.sim.fast_gpu import Simulator, Drive
from flybench.sim.params import Parameters
from flybench.song import Song, SAMPLE_RATE
from flybench.world.arena import Arena
from flybench.world import constants as C
from .runner import select_groups
from .record import sha256, environment

PROTOCOL = Path('experiments/courtship_v1.md')
CONDITIONS = ('virgin_live', 'mated_live', 'virgin_mute', 'mated_mute')
READOUTS = ('P1', 'pIP10', 'LC10a', 'vpoDN', 'pC1', 'DNa02', 'DNa02_L',
            'DNa02_R', 'DNa01', 'MDN', 'DNp09', C.PULSE_GROUP, C.SINE_GROUP)


def save(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n', encoding='utf-8')


class ColumnRates:
    """Sampling adapter for fast_gpu's ordered per-column RNG comprehension.

    Every first multiplication selects one seed column; subsequent arithmetic
    is ordinary Tensor arithmetic. Array conversion exposes [target,batch].
    The adapter is recreated for every 5 ms run (25 steps, one draw chunk).
    """
    def __init__(self, values, dt=.2):
        self.values = np.asarray(values, dtype=np.float64)
        if self.values.ndim != 2 or not np.isfinite(self.values).all() or np.any(self.values < 0) or np.any(self.values*dt/1000 > 1):
            raise ValueError('Invalid column rates')
        self.calls = 0

    def __mul__(self, scalar):
        column = self.calls % self.values.shape[1]
        self.calls += 1
        return torch.from_numpy(self.values[:, column].copy())*scalar

    def __array__(self, dtype=None, copy=None):
        return np.array(self.values, dtype=dtype, copy=True)


def sensory(observation, sex, retina, sag_hz=0.0):
    """No peer brain, readout or reproductive label enters male drive."""
    if sex == 'male':
        if sag_hz != 0:
            raise ValueError('Male input accepts no reproductive-state drive')
        return dict(chemical=scent.rates(observation), visual=eye.rates(observation, retina),
                    auditory={}, sag_hz=0.0, delivered_rms=0.0)
    wave = observation.sound or (0.0,)*round(SAMPLE_RATE*C.WINDOW_MS/1000)
    return dict(chemical={}, visual={}, auditory={k: v.tolist() for k, v in ear.rates(wave).items()},
                sag_hz=sag_hz,
                delivered_rms=float(np.sqrt(np.mean(np.square(wave)))))


def emit(song, readings, mute, refractory):
    song.amplitude = float(np.clip(readings['pIP10']/(1000/refractory), 0, 1))
    pulse, sine = readings[C.PULSE_GROUP], readings[C.SINE_GROUP]
    song.mixture = pulse/(pulse+sine) if pulse+sine > 0 else 0.0
    wave = song.window(C.WINDOW_MS/1000)
    if mute or pulse+sine == 0:
        wave[:] = 0
    return wave, dict(amplitude=song.amplitude, pulse_fraction=song.mixture,
                      emitted_rms=float(np.sqrt(np.mean(wave**2))), female_song_hz=0)


class BatchBrain:
    def __init__(self, graph, sex, device='cuda'):
        self.sex = sex
        self.sag_hz = 0.0
        self.groups = groups(sex, graph=graph)
        self.groups['pC1'] = np.unique(np.concatenate([self.groups['pC1'+s] for s in 'abcde']))
        if sex == 'female':
            self.groups['SAG'] = select_groups(graph)['SAG']
        for side in ('L', 'R'):
            ids = self.groups['DNa02']
            self.groups['DNa02_'+side] = ids[graph['side'][ids] == side]
        self.retina = eye.columns(graph, self.groups) if sex == 'male' else []
        names = ('Or47b', C.CONTACT_GROUP, 'L1', 'L2') if sex == 'male' else ('JO-A', 'JO-B', 'SAG')
        targets = np.unique(np.concatenate([self.groups[k] for k in names]))
        n = len(graph['body_id'])
        weights = csr_matrix((graph['data'], graph['indices'], graph['indptr']), shape=(n, n))
        self.sim = Simulator(weights, device=device, params=Parameters(dt=.2), kernel='shiu',
                             groups={k: self.groups[k] for k in READOUTS}, drive=Drive(tuple(targets), 0))
        self.metadata = dict(neurons=n, graph_meta=graph.get('meta', {}),
            counts={k: len(v) for k, v in self.groups.items()},
            missing_groups=[k for k, v in self.groups.items() if not len(v)],
            scent=next(e.to_dict() for e in entries(sex) if e.name == 'Or47b'),
            target_count=len(targets), retina_columns=len(self.retina))
        self.raw_metadata = dict(retina=[asdict(c) for c in self.retina],
            groups={k: dict(indices=v.tolist(), body_ids=graph['body_id'][v].tolist()) for k, v in self.groups.items()})

    def reset(self, seeds, *, sag_hz=0.0):
        if self.sex == 'male' and sag_hz != 0:
            raise ValueError('Male brain accepts no reproductive-state drive')
        self.sag_hz = sag_hz
        self.state = self.sim.initial_batch_state([s+(10000 if self.sex == 'female' else 0) for s in seeds])

    def run(self, observations):
        inputs = [sensory(o, self.sex, self.retina, self.sag_hz) for o in observations]
        batch = len(inputs)
        counts = np.zeros((self.sim.n, batch), dtype=np.int64)
        for slot in range(10):
            drive = np.zeros((self.sim.n, batch))
            for j, inp in enumerate(inputs):
                for name, hz in inp['chemical'].items():
                    drive[self.groups[name], j] += hz
                for neuron, hz in inp['visual'].items():
                    drive[neuron, j] += hz
                for name, hz in inp['auditory'].items():
                    drive[self.groups[name], j] += hz[slot]
                if self.sex == 'female':
                    drive[self.groups['SAG'], j] += inp['sag_hz']
            adapter = ColumnRates(drive[self.sim.targets])
            self.sim.drive = Drive(tuple(self.sim.targets), adapter, 'poisson')
            result = self.sim.run_batch(C.EAR_BIN_MS, state=self.state)
            self.state = result.state
            if adapter.calls != batch:
                raise RuntimeError('Backend column sampling contract changed')
            counts += result.counts
        rates = counts/.05
        readings = []
        cells = []
        for j in range(batch):
            row = {k: float(rates[v, j].mean()) if len(v) else 0.0 for k, v in self.sim.groups.items()}
            row.update(network=float(rates[:, j].mean()), total_spikes=int(counts[:, j].sum()))
            readings.append(row)
            cells.append({k: rates[v, j].tolist() for k, v in self.sim.groups.items()})
        return readings, inputs, cells


def paired(trials, field, a='virgin_live', b='virgin_mute'):
    left = {t['seed']: t[field] for t in trials if t['condition'] == a}
    right = {t['seed']: t[field] for t in trials if t['condition'] == b}
    if len(left) < 2 or left.keys() != right.keys():
        raise ValueError('Incomplete paired data')
    values = np.array([left[s]-right[s] for s in sorted(left)])
    return dict(mean=float(values.mean()), se=float(values.std(ddof=1)/np.sqrt(len(values))),
                n=len(values), differences=values.tolist())


def verdicts(trials, full):
    keys = [(t['condition'], t['seed']) for t in trials]
    seeds = sorted({t['seed'] for t in trials})
    if len(keys) != len(set(keys)) or set(keys) != {(c, s) for c in CONDITIONS for s in seeds}:
        raise ValueError('Incomplete or duplicate coverage')
    eligible = full and seeds == list(range(10))
    rms = paired(trials, 'rms')
    state = paired(trials, 'vpoDN', b='mated_live')
    positive = {c: sum(t['pIP10'] > 0 for t in trials if t['condition'] == c) for c in CONDITIONS[:2]}
    audible = {c: sum(t['rms'] > 0 for t in trials if t['condition'] == c) for c in CONDITIONS[:2]}
    c1 = all(n >= 8 for n in positive.values()) and rms['mean'] > 2*rms['se'] and all(n > 0 for n in audible.values())
    return dict(C1=dict(verdict=('supported' if c1 else 'not supported') if eligible else 'unassessed',
                        pIP10_positive_seeds=positive, audible_seeds=audible, rms_contrast=rms),
                C2=dict(verdict=('supported' if state['mean'] > 2*state['se'] else 'not supported') if eligible else 'unassessed', contrast=state),
                C3=dict(verdict='descriptive', contrast=paired(trials, 'vpoDN')),
                C4=dict(verdict='descriptive'), C5=dict(verdict='descriptive'))


def aggregate(condition, seed, rows):
    measured = rows[40:]
    def mean(key, sex=None):
        return float(np.mean([r[sex][key] if sex else r[key] for r in measured]))
    delta = [r['male']['DNa02_L']-r['male']['DNa02_R'] for r in measured]
    bearing = [r['observations'][0]['bearing'] for r in measured]
    constant = np.ptp(delta) == 0 or np.ptp(bearing) == 0
    return dict(condition=condition, seed=seed, windows=len(rows), measured_windows=len(measured),
        **{k: mean(k, 'male') for k in ('pIP10', 'P1', 'LC10a', 'DNa02_L', 'DNa02_R', 'DNa01', 'MDN')},
        **{k: mean(k, 'female') for k in ('vpoDN', 'pC1')},
        rms=float(np.mean([r['sensory'][1]['delivered_rms'] for r in measured])),
        distance=mean('distance'), final_distance=rows[-1]['distance'],
        spearman=None if constant else float(spearmanr(delta, bearing).statistic),
        spearman_reason='constant series' if constant else None,
        **{sex+'_ignition': float(np.mean([r[sex]['network'] > 30 for r in measured])) for sex in ('male', 'female')},
        **{sex+'_network_hz': mean('network', sex) for sex in ('male', 'female')},
        **{sex+'_total_spikes': sum(r[sex]['total_spikes'] for r in measured) for sex in ('male', 'female')},
        readouts={sex: {k: mean(k, sex) for k in READOUTS} for sex in ('male', 'female')})


def table(record):
    fields = ('pIP10', 'rms', 'vpoDN', 'pC1', 'P1', 'distance', 'final_distance', 'male_ignition', 'female_ignition')
    lines = ['| Condition | '+' | '.join(fields)+' |', '| --- | '+' | '.join(['---:']*len(fields))+' |']
    for c in CONDITIONS:
        rows = [t for t in record['trials'] if t['condition'] == c]
        lines.append('| '+c+' | '+' | '.join(f'{np.mean([r[k] for r in rows]):.6g}' for k in fields)+' |')
    return lines


def run(stage, seeds):
    start = time.perf_counter()
    protocol_hash = sha256(PROTOCOL)
    windows = 60 if stage == 'quick' else 400
    brains = []
    for sex in ('male', 'female'):
        graphpath = Path('build/graph_'+sex+'.npz')
        brain = BatchBrain(load(graphpath), sex)
        brain.metadata['graph_sha256'] = sha256(graphpath)
        dictionary = Path('build/dictionary_'+sex+'.json')
        brain.metadata['dictionary_sha256'] = sha256(dictionary)
        brains.append(brain)
    rawdir = Path('build/records-raw/courtship_v1_'+stage)
    rawdir.mkdir(parents=True, exist_ok=True)
    source_paths = [Path(__file__).relative_to(Path.cwd())] if Path(__file__).is_absolute() else [Path(__file__)]
    source_paths += [Path('flybench')/p for p in ('world/arena.py', 'world/constants.py', 'eye.py', 'scent.py', 'motor.py', 'song.py', 'ear.py', 'sim/fast_gpu.py', 'sim/params.py', 'dictionary/entries.py', 'dictionary/api.py', 'experiment/runner.py')]
    record = dict(schema_version='courtship-1', stage=stage, seeds=list(seeds), windows=windows, warmup=40,
        created_utc=datetime.now(timezone.utc).isoformat(), protocol_sha256=protocol_hash,
        protocol_text=PROTOCOL.read_text(encoding='utf-8'), environment=environment('cuda'),
        backend='fast_gpu', kernel='shiu', parameters=asdict(Parameters(dt=.2)), chosen=C.chosen(),
        female_blind=True, female_scent=False, female_song_hz=0, sound_delay_windows=1,
        female_seed_offset=10000, sag_alias='^(?:AN_SMP_2|AN_FLA_SMP_2|ANXXX983)$',
        brains={s: b.metadata for s, b in zip(('male', 'female'), brains)},
        source_sha256={p.as_posix(): sha256(p) for p in source_paths}, trials=[], raw=[])
    save(rawdir/'metadata.json', {s: b.raw_metadata for s, b in zip(('male', 'female'), brains)})
    for condition in CONDITIONS:
        arenas, songs = [Arena(s) for s in seeds], [Song(amplitude=0) for _ in seeds]
        brains[0].reset(seeds)
        brains[1].reset(seeds, sag_hz=50.0 if condition.startswith('virgin') else 0.0)
        trials = [[] for _ in seeds]
        destination = rawdir/(condition+'.jsonl.gz')
        with gzip.open(destination, 'wt', encoding='utf-8', newline='\n') as stream:
            for w in range(windows):
                observations = [[a.observe(i) for a in arenas] for i in (0, 1)]
                results = [brain.run(obs) for brain, obs in zip(brains, observations)]
                for j, arena in enumerate(arenas):
                    readings = [r[0][j] for r in results]
                    commands = [motor.command(r) for r in readings]
                    wave, songlog = emit(songs[j], readings[0], condition.endswith('mute'), brains[0].sim.params.refractory)
                    arena.advance(commands, wave)
                    row = dict(window=w, time_ms=(w+1)*50, seed=seeds[j],
                        bodies=[asdict(b) for b in arena.bodies], distance=arena.observe(0).distance,
                        contact=arena.observe(0).contact,
                        observations=[{k: v for k, v in asdict(obs[j]).items() if k != 'sound'} for obs in observations],
                        commands=[asdict(c) for c in commands], sensory=[r[1][j] for r in results],
                        male=readings[0], female=readings[1], song=songlog)
                    stream.write(json.dumps(dict(**row, cell_rates={s: r[2][j] for s, r in zip(('male', 'female'), results)}), allow_nan=False)+'\n')
                    # Retain only compact inputs needed for seed aggregation.
                    trials[j].append({k: row[k] for k in ('male', 'female', 'distance', 'observations')} | {'sensory': [{}, {'delivered_rms': row['sensory'][1]['delivered_rms']}]})
                if (w+1) % 20 == 0:
                    print(f'{stage} {condition} {w+1}/{windows}; elapsed {time.perf_counter()-start:.1f}s', flush=True)
        record['trials'].extend(aggregate(condition, s, rows) for s, rows in zip(seeds, trials))
        record['raw'].append(dict(path=destination.as_posix(), bytes=destination.stat().st_size, sha256=sha256(destination)))
        save(Path('build')/('courtship_v1_'+stage+'_checkpoint.json'), record)
    if sha256(PROTOCOL) != protocol_hash:
        raise RuntimeError('Preregistration changed during execution')
    record['elapsed_seconds'] = time.perf_counter()-start
    record['verdicts'] = verdicts(record['trials'], stage == 'full')
    record['raw'].append(dict(path=(rawdir/'metadata.json').as_posix(), bytes=(rawdir/'metadata.json').stat().st_size, sha256=sha256(rawdir/'metadata.json')))
    save(Path('build' if stage == 'quick' else 'records')/('courtship_v1_'+stage+'.json'), record)
    print('\n'.join(table(record)), flush=True)
    return record


def report():
    quick = json.loads(Path('build/courtship_v1_quick.json').read_text(encoding='utf-8'))
    full = json.loads(Path('records/courtship_v1_full.json').read_text(encoding='utf-8'))
    lines = ['# courtship_v1', '', 'Rates are Hz per neuron; distance is mm; RMS is waveform amplitude. Ignition is a window fraction.',
        '', '## Quick (excluded from verdicts)', '', *table(quick), '', '## Full' if len(full['seeds']) == 10 else '## Partial (five seeds)', '', *table(full),
        '', '## Paired predictions', '', '```json', json.dumps(full['verdicts'], indent=2), '```',
        '', '## Dictionary and limitations', '', '```json', json.dumps({s: dict(counts=b['counts'], missing_groups=b['missing_groups']) for s, b in full['brains'].items()}, indent=2), '```',
        '', 'C4 and C5 are descriptive only. Per-seed correlations, final distances, network rates and totals are in the summary JSON. Null correlations mean a constant series.',
        'The existing DNp09 stop gate is retained. Female SAG uses the prior protocol alias union. No kernel or world modules were modified.',
        'The experiment-local adapter supplies distinct rates to seed columns; synthetic CPU tests cover its equivalence to independent runs. Scientific runs use CUDA fast_gpu/shiu.',
        'No mating or acceptance outcome is inferred from neural activity or contact.',
        f"Elapsed seconds: quick {quick['elapsed_seconds']:.3f}; full {full['elapsed_seconds']:.3f}.",
        'Clean room: only this repository was inspected; the supplied dependency import path was used without inspecting its project sources.',
        '', 'Summary evidence: courtship_v1_full.json SHA256 '+sha256('records/courtship_v1_full.json'),
        'Quick evidence: build/courtship_v1_quick.json SHA256 '+sha256('build/courtship_v1_quick.json')]
    Path('records/courtship_v1_report.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('quick', 'full', 'report'))
    parser.add_argument('--partial', action='store_true')
    args = parser.parse_args()
    if args.stage == 'report':
        report()
    else:
        run(args.stage, list(range(2 if args.stage == 'quick' else 5 if args.partial else 10)))


if __name__ == '__main__':
    main()
