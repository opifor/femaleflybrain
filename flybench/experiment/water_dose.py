"""Frozen water dose and MN9 laterality experiment."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import time

import numpy as np
from scipy.sparse import csr_matrix

from flybench.graph import load
from flybench.sim.fast_gpu import Simulator, Drive
from flybench.sim.params import Parameters
from .benchmarks import SHIU_IDS, summary, drive_audit, save
from .record import sha256, environment

PROTOCOL = Path('experiments/water_dose_v1.md')
FROZEN_HASH = '76ec17cba6cfe8e82d18831e6c9c2a73a67b11f8851a9183a4f1f7a9cec958a0'
RAW = Path('build/records-raw')
REF = 720575940660219265


def conditions():
    return {'baseline': (None, 0), **{f'water{d}': ('water', d) for d in (100, 160, 200, 260)},
            **{f'sugar{d}': ('sugar', d) for d in (100, 200)}}


def mn9_other(graph):
    ref = np.flatnonzero(graph['body_id'] == REF)
    if len(ref) != 1:
        raise ValueError('MN9_ref must exist exactly once')
    i = ref[0]
    opposite = {'L': 'R', 'R': 'L'}.get(str(graph['side'][i]))
    typ = str(graph['type'][i])
    if opposite is None or not typ:
        return np.array([], dtype=int)
    return np.flatnonzero((graph['type'] == typ) & (graph['side'] == opposite))


def select_groups(graph):
    lookup = {int(v): i for i, v in enumerate(graph['body_id'])}
    groups, audit = {}, {}
    for name in ('water', 'sugar'):
        ids = SHIU_IDS[name]
        groups[name] = np.array([lookup[v] for v in ids if v in lookup], dtype=int)
        if not len(groups[name]):
            raise ValueError(f'Empty required input: {name}')
        audit[name] = dict(requested_count=len(ids), missing_ids=[v for v in ids if v not in lookup])
    other = mn9_other(graph)
    groups['MN9_ref'] = np.array([lookup[REF]], dtype=int)
    if len(other):
        groups['MN9_other'] = other
    for name, idx in {**groups, 'MN9_other': other}.items():
        audit.setdefault(name, {})
        audit[name].update(count=len(idx), status='present' if len(idx) else 'absent',
                           body_ids=graph['body_id'][idx].tolist(),
                           types=sorted(set(graph['type'][idx].tolist())),
                           sides={s or 'unknown': int(np.sum(graph['side'][idx] == s)) for s in ('L', 'R', 'M', '')})
    return groups, audit


def evaluate(record):
    seeds = record['seeds']
    if seeds != list(range(2 if record['stage'] == 'quick' else 10)):
        raise ValueError('Invalid seed coverage')
    rows = {(t['condition'], t['seed']): t for t in record['trials']}
    if len(rows) != len(record['trials']) or set(rows) != {(c, s) for c in conditions() for s in seeds}:
        raise ValueError('Incomplete or duplicate coverage')
    other = record['groups']['MN9_other']['count'] > 0
    names = ['MN9_ref'] + (['MN9_other'] if other else [])
    def values(c, g):
        return np.array([rows[c, s]['rates_hz'][g] for s in seeds])
    table = {c: {g: summary(values(c, g)) for g in names} for c in conditions()}
    for c in table:
        if not other:
            table[c]['MN9_other'] = None
        table[c]['delivered_grn_hz'] = summary([rows[c, s]['delivered_grn_hz'] for s in seeds])
    w1 = summary(values('water160', 'MN9_ref') - values('baseline', 'MN9_ref'))
    w2 = {g: bool(table['water260'][g]['mean'] > table['water160'][g]['mean'] > table['water100'][g]['mean']) for g in names}
    w2.setdefault('MN9_other', None)
    contrasts = {}
    if not other:
        w3 = 'not evaluable: MN9_other absent'
    else:
        contrasts = {c: summary(values(c, 'MN9_other') - values(c, 'MN9_ref')) for c in conditions() if c.startswith('water')}
        if any(v['supported'] for v in contrasts.values()):
            w3 = 'laterality mismatch SUSPECTED'
        elif all(np.all(values(c, g) == 0) for c in contrasts for g in names):
            w3 = 'pathway silent at all tested doses'
        else:
            w3 = 'no laterality signal'
    w4 = bool(63.4 * .85 <= table['sugar100']['MN9_ref']['mean'] <= 63.4 * 1.15)
    return dict(table=table, W1=w1, W2=w2, W3=w3, W3_contrasts=contrasts,
                W4=dict(passed=w4, reference_hz=63.4, band_hz=[63.4*.85, 63.4*1.15]),
                status='PASS' if w4 else 'FAIL-CLOSED')


def report(record):
    result = record['Result']
    def fmt(v):
        return 'absent' if v is None else f'{v["mean"]:.3f} +/- {v["se"]:.3f}'
    lines = ['# water_dose_v1 report', '',
             'Full run, ten seeds; mean +/- SE in Hz. MN9 readout [200,1000) ms.',
             'GRN drive is delivered external-event Hz over the full 1 s.', '',
             '| Condition | MN9_ref | MN9_other | Delivered GRN drive |',
             '| --- | ---: | ---: | ---: |']
    for c, row in result['table'].items():
        lines.append(f'| {c} | {fmt(row["MN9_ref"])} | {fmt(row["MN9_other"])} | {fmt(row["delivered_grn_hz"])} |')
    lines += ['', f'W1: {fmt(result["W1"])}; supported={result["W1"]["supported"]}.',
              f'W2 descriptive order: {result["W2"]}.', f'W3: {result["W3"]}.',
              f'W4: {result["W4"]}; status={result["status"]}.',
              'W4 is a reproducibility control; graph, parameter and engine hashes also match the prior benchmark.', '',
              '| Population | Present/requested | IDs | Graph sides | Types |', '| --- | --- | --- | --- | --- |']
    for name, row in record['groups'].items():
        lines.append(f'| {name} | {row["count"]}/{row.get("requested_count", row["count"])} | {row["body_ids"]} | {row["sides"]} | {row["types"]} |')
    lines += ['', '## Limits and provenance', '',
              'Deviation: sugar has 20/21 source IDs, as in the prior benchmark; missing ID 720575940620900446. No remapping.',
              'Graph labels are reported literally. Historical FAFB left/right reversal and the unverified water pairing prevent an anatomical-side conclusion.',
              'Supplied paper context (qualitative): paper: water activates MN9 at 160 Hz necessity dose; exact water100 value not published.',
              'No parameter or gain changes. An absent other readout cannot establish bilateral silence.',
              f'Run wall time: {record["elapsed_seconds"]:.3f} s.',
              f'Protocol SHA256: {record["protocol_sha256"]}.', f'Graph SHA256: {record["graph_sha256"]}.',
              f'Environment: {json.dumps(record["environment"], sort_keys=True)}.',
              'Clean room: no sibling project or archive source read; only the explicitly supplied dependency directory used for imports. No git writes.',
              'Raw seed and cell audits: build/records-raw/water_dose_v1_full.json.',
              'Quick, test and execution evidence: records/water_dose_v1_checks.json.', '']
    if not result['W4']['passed']:
        lines += ['FAIL-CLOSED: control failed; biological interpretation withheld.', '']
    Path('records/water_dose_v1_report.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()
    start = time.perf_counter()
    if sha256(PROTOCOL) != FROZEN_HASH:
        raise ValueError('Preregistration hash changed')
    RAW.mkdir(parents=True, exist_ok=True)
    graph_path = Path('build/graph_female.npz')
    graph_hash = sha256(graph_path)
    prior = json.loads(Path('records/shiu_benchmarks_v1_report.json').read_text(encoding='utf-8'))
    if graph_hash != prior['graph']['sha256'] or asdict(Parameters(dt=.2)) != prior['parameters']:
        raise ValueError('Benchmark graph or parameter mismatch')
    code_hashes = {p: sha256(p) for p in prior['code_sha256']}
    if code_hashes != prior['code_sha256']:
        raise ValueError('Benchmark engine/source hashes changed')
    code_hashes['flybench/experiment/water_dose.py'] = sha256(__file__)
    if not args.quick:
        quick = json.loads((RAW / 'water_dose_v1_quick.json').read_text(encoding='utf-8'))
        evaluate(quick)
        if quick['stage'] != 'quick' or quick['protocol_sha256'] != FROZEN_HASH or quick['graph_sha256'] != graph_hash or quick['code_sha256'] != code_hashes:
            raise ValueError('Quick frozen inputs mismatch')
    graph = load(graph_path)
    required = dict(dataset='FAFB', version='783', sign_rule='shiu2024-parquet', sign_rule_version='1', connectivity_source='shiu')
    if any(graph['meta'].get(k) != v for k, v in required.items()):
        raise ValueError('Unexpected graph metadata')
    groups, audit = select_groups(graph)
    seeds = list(range(2 if args.quick else 10))
    record = dict(stage='quick' if args.quick else 'full', seeds=seeds, groups=audit,
                  created_utc=datetime.now(timezone.utc).isoformat(), protocol_sha256=FROZEN_HASH,
                  graph_sha256=graph_hash, code_sha256=code_hashes, parameters=asdict(Parameters(dt=.2)),
                  environment=environment('cuda'), kernel='shiu', dtype='float32',
                  duration_ms=1000, readout_ms=[200, 1000], trials=[])
    n = len(graph['body_id'])
    weights = csr_matrix((graph['data'], graph['indices'], graph['indptr']), shape=(n, n))
    print(json.dumps(audit), flush=True)
    for condition, (source, rate) in conditions().items():
        targets = groups[source] if source else np.array([], dtype=int)
        sim = Simulator(weights, device='cuda', params=Parameters(dt=.2), kernel='shiu', groups=groups,
                        drive=Drive(tuple(targets), rate) if source else None)
        head = sim.run_batch(200, seeds=seeds)
        tail = sim.run_batch(800, state=head.state)
        for j, seed in enumerate(seeds):
            drive = drive_audit(head, tail, targets, j) if source else None
            record['trials'].append(dict(condition=condition, seed=seed,
                rates_hz={k: float(v[j]) for k, v in tail.group_rates_hz.items()},
                cell_rates_hz={k: tail.rates_hz[idx, j].tolist() for k, idx in groups.items()},
                delivered_grn_hz=drive['full_1s']['delivered_hz'] if drive else 0., drive=drive))
        print(f'{condition}: MN9_ref={np.mean(tail.group_rates_hz["MN9_ref"]):.3f}; elapsed={time.perf_counter()-start:.1f}s', flush=True)
        del head, tail, sim
    record['Result'] = evaluate(record)
    record['elapsed_seconds'] = time.perf_counter() - start
    save(RAW / f'water_dose_v1_{record["stage"]}.json', record)
    if not args.quick:
        compact = {k: v for k, v in record.items() if k != 'trials'}
        save('records/water_dose_v1_report.json', compact)
        report(record)
        if not record['Result']['W4']['passed']:
            raise SystemExit(2)


if __name__ == '__main__':
    main()
