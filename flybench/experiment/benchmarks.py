"""Preregistered Shiu sensorimotor benchmarks on the FAFB v783 graph."""
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
from .record import sha256, environment

PROTOCOL = Path('experiments/shiu_benchmarks_v1.md')
PAPER = 'https://doi.org/10.1038/s41586-024-07763-9'


def conditions():
    return {'baseline': ({}, 0),
            **{f'sugar{d}': ({'sugar': d}, d) for d in (10, 50, 100, 200)},
            'water100': ({'water': 100}, 100),
            'sugar100_bitter100': ({'sugar': 100, 'bitter': 100}, 100),
            'sugar100_Ir94e100': ({'sugar': 100, 'Ir94e': 100}, 100),
            'JO-CE100': ({'JO-CE': 100}, 100), 'JO-F100': ({'JO-F': 100}, 100),
            'JO-A180': ({'JO-A': 180}, 180), 'JO-B180': ({'JO-B': 180}, 180),
            'JO-AB180': ({'JO-A': 180, 'JO-B': 180}, 180)}


def select_groups(graph):
    lookup = {int(body): i for i, body in enumerate(graph['body_id'])}
    selected, audit = {}, {}
    for name, ids in SHIU_IDS.items():
        selected[name] = np.array([lookup[i] for i in ids if i in lookup], dtype=int)
        audit[name] = dict(source='Shiu figures.ipynb literal IDs', requested_ids=ids,
                           missing_ids=[i for i in ids if i not in lookup])
    base = dictionary_groups('female', graph=graph)
    for name in ('JO-A', 'JO-B'):
        selected[name] = base[name]
        audit[name] = dict(source='female dictionary selector', missing_ids=[],
                           requested_ids=None)
    for name, idx in selected.items():
        if not len(idx):
            raise ValueError(f'Empty required group: {name}')
        audit[name].update(count=len(idx), body_ids=graph['body_id'][idx].tolist(),
                           types=sorted(set(graph['type'][idx].tolist())))
    return selected, audit


def second_order(graph, selected):
    n = len(graph['body_id'])
    counts = csr_matrix((graph['count'], graph['indices'], graph['indptr']), shape=(n, n))
    groups, audit = {}, {}
    for label, names in (('JO-A', ('JO-A',)), ('JO-B', ('JO-B',)), ('JO-AB', ('JO-A', 'JO-B'))):
        src = np.unique(np.concatenate([selected[k] for k in names]))
        incoming = np.asarray(counts[src].sum(axis=0)).ravel()
        incoming[src] = 0
        totals = {}
        for i in np.flatnonzero(incoming):
            typ = str(graph['type'][i])
            totals[typ] = totals.get(typ, 0) + int(incoming[i])
        top = sorted((t for t in totals if t), key=lambda t: (-totals[t], t))[:20]
        rows = []
        for typ in top:
            key = label + ':' + typ
            idx = np.flatnonzero((graph['type'] == typ) & (incoming > 0))
            groups[key] = idx
            rows.append(dict(type=typ, group=key, synapses=totals[typ], count=len(idx),
                             body_ids=graph['body_id'][idx].tolist()))
        audit[label] = dict(top20=rows, untyped_synapses=totals.get('', 0))
    return groups, audit


def summary(values):
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.isfinite(x).all():
        raise ValueError('Need at least two finite values')
    mean, se = float(x.mean()), float(x.std(ddof=1) / np.sqrt(len(x)))
    return dict(mean=mean, se=se, n=len(x), values=x.tolist(), supported=bool(mean > 2 * se))


def evaluate(record):
    if len(record['seeds']) < 2 or len(set(record['seeds'])) != len(record['seeds']):
        raise ValueError('Invalid seed coverage')
    expected = {(c, s) for c in conditions() for s in record['seeds']}
    rows = {(t['condition'], t['seed']): t for t in record['trials']}
    if len(rows) != len(record['trials']) or set(rows) != expected:
        raise ValueError('Incomplete or duplicate seed coverage')
    def vals(c, g):
        return np.array([rows[c, s]['rates_hz'][g] for s in record['seeds']])
    def contrast(a, b, g):
        return summary(vals(a, g) - (vals(b, g) if b else 0))
    b1 = {'sugar_positive': contrast('sugar100', None, 'MN9'),
          **{f'dose_{a}_minus_{b}': contrast(f'sugar{a}', f'sugar{b}', 'MN9')
             for a, b in ((50, 10), (100, 50), (200, 100))},
          'bitter_suppression': contrast('sugar100', 'sugar100_bitter100', 'MN9')}
    b2 = {'CE_positive': contrast('JO-CE100', None, 'aBN1'),
          'CE_minus_F': contrast('JO-CE100', 'JO-F100', 'aBN1')}
    passed = {k: all(v['supported'] for v in block.values()) for k, block in (('B1', b1), ('B2', b2))}
    return dict(B1=b1, B2=b2, passed=passed, robustness_gate=all(passed.values()),
                secondary=dict(water_positive=contrast('water100', None, 'MN9'),
                               Ir94e_suppression=contrast('sugar100', 'sugar100_Ir94e100', 'MN9')),
                table={c: {g: summary(vals(c, g)) for g in ('MN9', 'aBN1')} for c in conditions()})


def drive_audit(head, tail, idx, column):
    labels = {'requested_hz': 'requested_hz', 'sampled_hz': 'sampled_drive_hz',
              'delivered_hz': 'delivered_hz', 'total_spike_hz': 'rates_hz'}
    result = {}
    for window in ('full_1s', 'measurement_800ms'):
        cells = {}
        for label, attr in labels.items():
            value = getattr(tail, attr)[idx, column]
            if window == 'full_1s':
                value = .2 * getattr(head, attr)[idx, column] + .8 * value
            cells[label] = value.tolist()
        result[window] = dict(cells=cells, **{k: float(np.mean(v)) for k, v in cells.items()})
    return dict(count=len(idx), **result)


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def run(graph, graph_sha, quick=False):
    start = time.perf_counter()
    selected, audit = select_groups(graph)
    downstream, down_audit = second_order(graph, selected)
    groups = {**selected, **downstream}
    n = len(graph['body_id'])
    weights = csr_matrix((graph['data'], graph['indices'], graph['indptr']), shape=(n, n))
    seeds = list(range(2 if quick else 10))
    record = dict(schema_version='shiu-benchmarks-1', stage='quick' if quick else 'full',
                  created_utc=datetime.now(timezone.utc).isoformat(), seeds=seeds,
                  protocol=dict(sha256=sha256(PROTOCOL), text=PROTOCOL.read_text(encoding='utf-8')),
                  graph=dict(sha256=graph_sha, meta=graph['meta']), groups=audit, second_order=down_audit,
                  parameters=asdict(Parameters(dt=.2)), backend='fast_gpu', kernel='shiu', dtype='float32',
                  environment=environment('cuda'), timing=dict(duration_ms=1000, warmup_ms=200),
                  sources=dict(paper=PAPER, notebook='https://github.com/philshiu/Drosophila_brain_model/blob/main/figures.ipynb',
                               notebook_sha256=sha256('build/shiu_figures.ipynb')),
                  code_sha256={p: sha256(p) for p in ('flybench/experiment/benchmarks.py', 'flybench/sim/fast_gpu.py',
                                                     'flybench/sim/lif.py', 'flybench/sim/params.py', 'flybench/dictionary/entries.py')},
                  trials=[])
    for condition, (drives, rate) in conditions().items():
        targets = np.concatenate([selected[k] for k in drives]) if drives else np.array([], dtype=int)
        if len(np.unique(targets)) != len(targets):
            raise ValueError('Overlapping drive populations')
        sim = Simulator(weights, device='cuda', params=Parameters(dt=.2), kernel='shiu', groups=groups,
                        drive=Drive(tuple(targets), rate) if drives else None)
        head = sim.run_batch(200, seeds=seeds)
        tail = sim.run_batch(800, state=head.state)
        for j, seed in enumerate(seeds):
            record['trials'].append(dict(condition=condition, seed=seed, driven_count=len(targets),
                rates_hz={k: float(v[j]) for k, v in tail.group_rates_hz.items()},
                cell_rates_hz={k: tail.rates_hz[idx, j].tolist() for k, idx in groups.items()},
                network_hz=float(tail.total_hz_per_neuron[j]),
                drive={k: drive_audit(head, tail, selected[k], j) for k in drives}))
        print(f'{condition}: MN9={np.mean(tail.group_rates_hz["MN9"]):.3f}, '
              f'aBN1={np.mean(tail.group_rates_hz["aBN1"]):.3f}; {time.perf_counter()-start:.1f}s', flush=True)
        del head, tail, sim
    record['Result'] = evaluate(record)
    record['elapsed_seconds'] = time.perf_counter() - start
    return record


def report(record, path):
    r = record['Result']
    fmt = lambda v: f'{v["mean"]:.3f} +/- {v["se"]:.3f}'
    refs = {'baseline': '0 Hz baseline (Methods)', 'sugar100': '~80% of maximal MN9 (Methods)',
            'sugar100_bitter100': 'suppression (Fig. 3b)', 'sugar100_Ir94e100': 'weaker suppression (Fig. 3c)',
            'water100': 'MN9 activation (Fig. 4a)', 'JO-CE100': 'robust aBN1 (Fig. 5g)',
            'JO-F100': 'little/no aBN1 (Fig. 5g)'}
    lines = ['# shiu_benchmarks_v1 report', '', f'Source: [Shiu et al. 2024]({PAPER}).', '',
             'Rates are Hz, mean +/- SE across ten seeds, measured after 200 ms.',
             'Paper comparisons are qualitative unless explicitly numeric; no figure digitization was performed.', '',
             '| Condition | MN9 | aBN1 | Shiu comparison |', '| --- | ---: | ---: | --- |']
    for c, row in r['table'].items():
        lines.append(f'| {c} | {fmt(row["MN9"])} | {fmt(row["aBN1"])} | {refs.get(c, "dose response (Fig. 1d/Extended Data Fig. 1d)" if c.startswith("sugar") else "descriptive audit")} |')
    ratio = r['table']['sugar100']['MN9']['mean'] / r['table']['sugar200']['MN9']['mean'] if r['table']['sugar200']['MN9']['mean'] else None
    lines += ['', f'Sugar100/sugar200 measured-range ratio: {ratio}; not a proven maximum.', '',
              '## Populations', '', '| Group | Present | Missing source IDs |', '| --- | ---: | --- |']
    for g, row in record['groups'].items():
        lines.append(f'| {g} | {row["count"]} | {row["missing_ids"]} |')
    lines += ['', '## Preregistered decisions', '', '| Check | Paired contrast, Hz | Supported (>2 SE) |', '| --- | ---: | --- |']
    for section in ('B1', 'B2', 'secondary'):
        for name, val in r[section].items():
            lines.append(f'| {section}: {name} | {fmt(val)} | {val["supported"]} |')
    lines += ['', f'Gate: {r["robustness_gate"]}; individual gates: {r["passed"]}.', '',
              '## B3 drive audit', '', 'Full-second rates, averaged across driven cells then seeds. Per-cell and per-trial records also include the measurement interval.', '',
              '| Condition | Group (cells) | Requested | Sampled | Delivered | Total spikes |', '| --- | --- | ---: | ---: | ---: | ---: |']
    for c, (drives, _) in conditions().items():
        trials = [t for t in record['trials'] if t['condition'] == c]
        for g in drives:
            v = {k: summary([t['drive'][g]['full_1s'][k] for t in trials]) for k in ('requested_hz', 'sampled_hz', 'delivered_hz', 'total_spike_hz')}
            lines.append(f'| {c} | {g} ({record["groups"][g]["count"]}) | ' + ' | '.join(fmt(x) for x in v.values()) + ' |')
    lines += ['', '## JO second-order targets', '', '| Input | Type | Raw synapses | Cells | Hz | Any active seed |', '| --- | --- | ---: | ---: | ---: | --- |']
    for inp, spec in record['second_order'].items():
        trials = [t for t in record['trials'] if t['condition'] == inp+'180']
        for row in spec['top20']:
            val = summary([t['rates_hz'][row['group']] for t in trials])
            lines.append(f'| {inp} | {row["type"]} | {row["synapses"]} | {row["count"]} | {fmt(val)} | {any(v > 0 for v in val["values"])} |')
    lines += ['', 'Untyped synapse totals: ' + ', '.join(f'{k}={v["untyped_synapses"]}' for k, v in record['second_order'].items()) + '.']
    lines += ['', '## Limits and provenance', '',
              'v783 replaces paper v630; three source IDs are absent. dt=0.2 rather than 0.1 ms; ten rather than thirty repeats; float32 Torch GPU sampling; first 200 ms excluded. No parameters were tuned.',
              'Bitter and Ir94e are distinct. The 50 mM experiment is behavioural and is not reproduced by a calibrated concentration-to-rate conversion.',
              'Passing controls would support this graph/kernel/input combination for these routes, but would not prove the biological absence of JO-A/B to vpoEN transfer. A failed control also does not identify a unique cause.',
              f'Runtime: {record["elapsed_seconds"]:.2f} s. Graph SHA256: `{record["graph"]["sha256"]}`.',
              f'Protocol SHA256: `{record["protocol"]["sha256"]}`.',
              'Clean room: no sibling project or archive source was read. Only the explicitly supplied dependency directory was used for imports. No git staging, commit or push.',
              '', '## Frozen preregistration', '', record['protocol']['text']]
    Path(path).write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()
    graphpath = Path('build/graph_female.npz')
    graph = load(graphpath)
    required = dict(dataset='FAFB', version='783', sign_rule='shiu2024-parquet', sign_rule_version='1', connectivity_source='shiu')
    if any(graph['meta'].get(k) != v for k, v in required.items()):
        raise ValueError('Unexpected graph metadata')
    graph_sha = sha256(graphpath)
    if not args.quick:
        quick = json.loads(Path('build/shiu_benchmarks_v1_quick.json').read_text(encoding='utf-8'))
        evaluate(quick)
        if quick['stage'] != 'quick' or quick['protocol']['sha256'] != sha256(PROTOCOL) or quick['graph']['sha256'] != graph_sha:
            raise ValueError('Quick record does not match frozen inputs')
    record = run(graph, graph_sha, args.quick)
    out = 'build/shiu_benchmarks_v1_quick.json' if args.quick else 'records/shiu_benchmarks_v1_report.json'
    save(out, record)
    if not args.quick:
        report(record, 'records/shiu_benchmarks_v1_report.md')


# Exact IDs from upstream figures.ipynb; sugar/MN9 also in example.ipynb.
SHIU_IDS = {'sugar': [720575940624963786,
           720575940630233916,
           720575940637568838,
           720575940638202345,
           720575940617000768,
           720575940630797113,
           720575940632889389,
           720575940621754367,
           720575940621502051,
           720575940640649691,
           720575940639332736,
           720575940616885538,
           720575940639198653,
           720575940620900446,
           720575940617937543,
           720575940632425919,
           720575940633143833,
           720575940612670570,
           720575940628853239,
           720575940629176663,
           720575940611875570],
 'MN9': [720575940660219265],
 'bitter': [720575940621778381,
            720575940602353632,
            720575940617094208,
            720575940619197093,
            720575940626287336,
            720575940618600651,
            720575940627692048,
            720575940630195909,
            720575940646212996,
            720575940610483162,
            720575940645743412,
            720575940627578156,
            720575940622298631,
            720575940621008895,
            720575940629146711,
            720575940610259370,
            720575940610481370,
            720575940619028208,
            720575940614281266,
            720575940613061118,
            720575940604027168],
 'Ir94e': [720575940614211295,
           720575940638218173,
           720575940628832256,
           720575940626016017,
           720575940621375231,
           720575940612920386,
           720575940614273292,
           720575940628198503,
           720575940626241636,
           720575940619387814,
           720575940624604560,
           720575940615274425,
           720575940610683315,
           720575940627265265,
           720575940624079544,
           720575940629211607,
           720575940615089369,
           720575940631082124],
 'water': [720575940612950568,
           720575940631898285,
           720575940606002609,
           720575940612579053,
           720575940622902535,
           720575940616177458,
           720575940660292225,
           720575940622486922,
           720575940613786774,
           720575940629852866,
           720575940625861168,
           720575940613996959,
           720575940617857694,
           720575940644965399,
           720575940625203504,
           720575940630553415,
           720575940635172191,
           720575940634796536],
 'JO-CE': [720575940619341105,
           720575940630122015,
           720575940611061526,
           720575940615848788,
           720575940628444667,
           720575940627941431,
           720575940632449619,
           720575940650244342,
           720575940631866508,
           720575940638681845,
           720575940628978450,
           720575940609522461,
           720575940621442224,
           720575940602506208,
           720575940629022149,
           720575940627109991,
           720575940630020111,
           720575940615986459,
           720575940618684481,
           720575940620382889,
           720575940630080071,
           720575940626565455,
           720575940630319671,
           720575940602720940,
           720575940630564179,
           720575940637632419,
           720575940615809349,
           720575940626042149,
           720575940637054835,
           720575940602132509,
           720575940614188149,
           720575940616951124,
           720575940628101126,
           720575940629055721,
           720575940616589878,
           720575940622449388,
           720575940614427195,
           720575940625797617,
           720575940638664437,
           720575940618467195,
           720575940621729757,
           720575940613971485,
           720575940627585688,
           720575940629650997,
           720575940630059847,
           720575940608742409,
           720575940614351477,
           720575940633153375,
           720575940622937528,
           720575940604753437,
           720575940611783464,
           720575940618599872,
           720575940609541917,
           720575940637410869,
           720575940630070343,
           720575940621397417,
           720575940614035485,
           720575940610018266,
           720575940626307902,
           720575940634634606,
           720575940614060829,
           720575940624799290,
           720575940641921421,
           720575940623298559,
           720575940625559358,
           720575940629138959,
           720575940621625597,
           720575940625962568,
           720575940632767383,
           720575940624915230],
 'JO-F': [720575940606239243,
          720575940626956777,
          720575940604973746,
          720575940622222856,
          720575940642517284,
          720575940629719404,
          720575940616613022,
          720575940604299454,
          720575940615473186,
          720575940622217992,
          720575940606800341,
          720575940629267498,
          720575940637366335,
          720575940624224408,
          720575940609543197,
          720575940633364179,
          720575940629502009,
          720575940606431189,
          720575940625733960,
          720575940638529525,
          720575940617524053,
          720575940628935564,
          720575940624308355,
          720575940631170346,
          720575940627704375,
          720575940625885512,
          720575940614929245,
          720575940647493241,
          720575940618888368,
          720575940625087546,
          720575940606657493,
          720575940617273560,
          720575940640591861,
          720575940639410035,
          720575940621532413,
          720575940627523584,
          720575940621521917,
          720575940621097398,
          720575940625915338,
          720575940606222428,
          720575940627868471,
          720575940622179497,
          720575940608297774,
          720575940614026269,
          720575940613012959,
          720575940628100614,
          720575940606611401,
          720575940628649465,
          720575940610008217,
          720575940623791152,
          720575940625571240,
          720575940634923621,
          720575940609530653,
          720575940635968745,
          720575940625703434,
          720575940613105311,
          720575940629386819,
          720575940623077389,
          720575940625763015,
          720575940628359017],
 'aBN1': [720575940630907434]}

if __name__ == '__main__':
    main()
