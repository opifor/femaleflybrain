"""Preregistered, descriptive reverse anatomical mapping; no simulation."""
import argparse
import copy
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import gc
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy
from scipy.sparse import csr_matrix

PROTOCOL = Path('experiments/vpoen_inputs_v1.md')
PROTOCOL_HASH = 'd3f6c994b229591a01d6b376baa1673604a749437307c8ec91372b2359527293'
PREFIX = Path('records/vpoen_inputs_v1')
RAW = Path('build/records-raw/vpoen_inputs_v1')
B1 = ('AMMC-B1-candidate', 'AMMC-B1-candidate-graph')
TARGETS = ('vpoEN', 'vpoDN', 'vpoIN')
SCOPE = ('Scope: BANC excludes 4,344,932 synapses under its population contract; '
         'BANC superclass=central_brain_intrinsic versus FAFB central; raw totals '
         'do not have equal scope.')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def summary_record(record):
    """Keep all metric rows; move verbose identities/witnesses to raw records."""
    result = copy.deepcopy(record)
    result['detail_storage'] = ('All cell identities and all M5 witnesses are in the '
                                'hashed raw dataset checkpoints and cell files. '
                                'Summary M5 witnesses are shown for the first 40 rows.')
    for data in result['datasets'].values():
        for identity in data['selectors'].values():
            identity.pop('indices', None)
            identity.pop('body_ids', None)
        for row in data['M5'][40:]:
            row['incoming'].pop('best', None)
            row['outgoing'].pop('best', None)
    return result


def label(g, cell):
    return str(g['type'][cell]) or 'unnamed'


def sign(g, cell):
    return {1: '+', -1: '-', 0: '0'}[int(g['sign'][cell])]


def empty_stat():
    return dict(paths=0, flow=0, maximum=0, best=None, sign_flow={})


def witness(g, path, weights):
    return dict(body_ids=[int(g['body_id'][i]) for i in path],
                types=[label(g, i) for i in path],
                signs=''.join(sign(g, i) for i in path[:-1]),
                counts=[int(w) for w in weights], bottleneck=int(min(weights)))


def better(a, b):
    return b is None or (a['bottleneck'], a['body_ids']) > (b['bottleneck'], b['body_ids'])


def add_batch(stat, g, sources, weights, suffix, suffix_weights):
    """Aggregate paths sharing a suffix; choose the exact E3 tie witness."""
    if not len(sources):
        return
    bottlenecks = np.minimum(weights, min(suffix_weights)) if suffix_weights else weights
    stat['paths'] += int(len(sources))
    stat['flow'] += int(bottlenecks.sum(dtype=np.int64))
    tail_signs = ''.join(sign(g, i) for i in suffix[:-1])
    for s in (-1, 0, 1):
        selected = g['sign'][sources] == s
        if np.any(selected):
            key = {1: '+', -1: '-', 0: '0'}[s] + tail_signs
            stat['sign_flow'][key] = stat['sign_flow'].get(key, 0) + int(bottlenecks[selected].sum(dtype=np.int64))
    maximum = int(bottlenecks.max())
    choices = np.flatnonzero(bottlenecks == maximum)
    j = int(choices[np.argmax(g['body_id'][sources[choices]])])
    w = witness(g, [int(sources[j]), *suffix], [int(weights[j]), *suffix_weights])
    if better(w, stat['best']):
        stat['best'], stat['maximum'] = w, maximum


def merge_stat(dest, src):
    dest['paths'] += src['paths']
    dest['flow'] += src['flow']
    for k, v in src['sign_flow'].items():
        dest['sign_flow'][k] = dest['sign_flow'].get(k, 0) + v
    if src['best'] is not None and better(src['best'], dest['best']):
        dest['best'], dest['maximum'] = src['best'], src['maximum']


def add_one(stat, g, path, weights):
    value = min(weights)
    stat['paths'] += 1
    stat['flow'] += value
    signs = ''.join(sign(g, i) for i in path[:-1])
    stat['sign_flow'][signs] = stat['sign_flow'].get(signs, 0) + value
    ids = [int(g['body_id'][i]) for i in path]
    if stat['best'] is None or (value, ids) > (stat['maximum'], stat['best']['body_ids']):
        stat['maximum'] = value
        stat['best'] = witness(g, path, weights)


class Map:
    def __init__(self, graph, deadline=float('inf')):
        self.g = graph
        n = len(graph['body_id'])
        self.a = csr_matrix((graph['count'], graph['indices'], graph['indptr']), shape=(n, n))
        self.rev = self.a.tocsc()
        self.deadline = deadline

    def guard(self):
        if time.perf_counter() > self.deadline:
            raise TimeoutError('2700-second analysis budget expired')

    def incoming(self, t):
        lo, hi = self.rev.indptr[t:t+2]
        return self.rev.indices[lo:hi], self.rev.data[lo:hi]

    def direct(self, targets):
        cells = defaultdict(lambda: dict(synapses=0, targets=[]))
        edges = []
        self_synapses = 0
        for t in targets:
            src, count = self.incoming(t)
            for u, w in zip(src.tolist(), count.tolist()):
                cells[u]['synapses'] += w
                cells[u]['targets'].append(dict(index=int(t), count=w))
                edges.append((u, int(t), w))
                if u == t:
                    self_synapses += w
        total = sum(v['synapses'] for v in cells.values())
        types = {}
        raw = []
        for u, row in sorted(cells.items()):
            name = label(self.g, u)
            r = types.setdefault(name, dict(type=name, synapses=0, cells=0, sign_synapses={}, nt_synapses={}))
            r['synapses'] += row['synapses']
            r['cells'] += 1
            for key, value in [('sign_synapses', sign(self.g, u)), ('nt_synapses', str(self.g['nt'][u]) or 'unknown')]:
                r[key][value] = r[key].get(value, 0) + row['synapses']
            raw.append(dict(index=u, body_id=int(self.g['body_id'][u]), type=name,
                            sign=sign(self.g, u), nt=str(self.g['nt'][u]), **row))
        rows = sorted(types.values(), key=lambda r: (-r['synapses'], r['type']))
        for i, row in enumerate(rows, 1):
            row.update(rank=i, share=row['synapses']/total if total else None)
        return dict(total_synapses=total, input_cells=len(cells), self_synapses=self_synapses, types=rows), raw, edges

    def two_edges(self, targets):
        """Yield each simple two-edge suffix as vectorized source cells."""
        for t in targets:
            middles, last = self.incoming(t)
            for m, w in zip(middles.tolist(), last.tolist()):
                self.guard()
                if m == t:
                    continue
                sources, first = self.incoming(m)
                ok = (sources != m) & (sources != t)
                yield sources[ok], first[ok], m, int(t), w

    def m2(self, targets):
        types, origins = {}, {}
        for src, weights, m, t, last in self.two_edges(targets):
            name = label(self.g, m)
            r = types.setdefault(name, dict(type=name, **empty_stat()))
            add_batch(r, self.g, src, weights, [m, t], [last])
            for u, w in zip(src.tolist(), weights.tolist()):
                r = origins.setdefault(u, empty_stat())
                add_one(r, self.g, [u, m, t], [w, last])
        rows = sorted((r for r in types.values() if r['paths']), key=lambda r: (-r['maximum'], r['type']))
        for rank, row in enumerate(rows, 1):
            row['rank'] = rank
        return rows, origins

    def source_paths(self, sources, targets, maxdepth=3):
        """Exact source-restricted reverse enumeration, with simple-path guards."""
        mask = np.zeros(self.a.shape[0], dtype=bool)
        mask[np.asarray(sources, dtype=int)] = True
        # Cache filtered first edges; only source cells may start a path.
        filtered = {}

        def first(t):
            if t not in filtered:
                u, w = self.incoming(t)
                ok = mask[u]
                filtered[t] = (u[ok], w[ok])
            return filtered[t]

        stats = [empty_stat() for _ in range(maxdepth)]
        covered = [dict() for _ in range(maxdepth)]
        for t in targets:
            self.guard()
            u, w = first(int(t))
            ok = u != t
            add_batch(stats[0], self.g, u[ok], w[ok], [int(t)], [])
            covered[0].update({(int(s), int(t)): int(c) for s, c in zip(u[ok], w[ok])})
        if maxdepth >= 2:
            for t in targets:
                mids, last = self.incoming(t)
                for m, c in zip(mids.tolist(), last.tolist()):
                    self.guard()
                    if m == t:
                        continue
                    u, w = first(m)
                    ok = (u != m) & (u != t)
                    add_batch(stats[1], self.g, u[ok], w[ok], [m, int(t)], [c])
                    if np.any(ok):
                        covered[1][(m, int(t))] = c
                    if maxdepth >= 3:
                        ns, nw = self.incoming(m)
                        for v, c1 in zip(ns.tolist(), nw.tolist()):
                            if v == m or v == t:
                                continue
                            u, w = first(v)
                            ok = (u != v) & (u != m) & (u != t)
                            add_batch(stats[2], self.g, u[ok], w[ok], [v, m, int(t)], [c1, c])
                            if np.any(ok):
                                covered[2][(m, int(t))] = c
        cumulative = {}
        for d, (row, edges) in enumerate(zip(stats, covered), 1):
            cumulative.update(edges)
            row.update(depth=d, covered_synapses=sum(edges.values()),
                       cumulative_covered_synapses=sum(cumulative.values()))
        return stats, cumulative


def m4(mapping, selected, targets, m1, origins, jo):
    total = m1['total_synapses']
    rows = []
    ranks = {r['type']: r['rank'] for r in m1['types']}
    for name in B1:
        src = selected[name]
        direct = int(mapping.a[src][:, targets].sum(dtype=np.int64))
        combined = empty_stat()
        for u in src:
            merge_stat(combined, origins.get(int(u), empty_stat()))
        jo_middle = empty_stat()
        allowed = set(map(int, src))
        jo_set = set(map(int, jo))
        for u, w, m, t, last in mapping.two_edges(targets):
            if m in allowed:
                ok = np.asarray([int(v) in jo_set for v in u], dtype=bool)
                add_batch(jo_middle, mapping.g, u[ok], w[ok], [m, t], [last])
        rows.append(dict(name=name, cells=len(src), direct_synapses=direct,
                         direct_share=direct/total if total else None,
                         direct_sign_synapses={s: int(mapping.a[src[mapping.g['sign'][src] == v]][:, targets].sum(dtype=np.int64)) for s, v in [('+', 1), ('-', -1), ('0', 0)]},
                         member_type_ranks={label(mapping.g, u): ranks.get(label(mapping.g, u)) for u in src},
                         two_edge=combined, jo_middle=jo_middle))
    return rows


def m5(mapping, jo, targets, origins):
    g = mapping.g
    outgoing = {u: dict(paths=r['paths'], flow=r['flow'], maximum=r['maximum'],
                        best=r['best'], sign_flow=dict(r['sign_flow'])) for u, r in origins.items()}
    excluded = set(map(int, jo)) | set(map(int, targets))
    for t in targets:
        u, w = mapping.incoming(t)
        for s, c in zip(u.tolist(), w.tolist()):
            if s != t:
                add_one(outgoing.setdefault(s, empty_stat()), g, [s, int(t)], [c])
    # All one-edge JO inputs, represented as destination-indexed lists.
    jo_in = defaultdict(list)
    for s in jo:
        lo, hi = mapping.a.indptr[s:s+2]
        for v, w in zip(mapping.a.indices[lo:hi].tolist(), mapping.a.data[lo:hi].tolist()):
            if v != s:
                jo_in[v].append((int(s), w))
    jo_in = {v: (np.asarray([s for s, _ in pairs]), np.asarray([w for _, w in pairs])) for v, pairs in jo_in.items()}
    types, cells = {}, []
    for cell, out in sorted(outgoing.items()):
        mapping.guard()
        if cell in excluded:
            continue
        incoming = empty_stat()
        if cell in jo_in:
            u, w = jo_in[cell]
            add_batch(incoming, g, u, w, [cell], [])
        mids, last = mapping.incoming(cell)
        for m, c in zip(mids.tolist(), last.tolist()):
            if m == cell or m not in jo_in:
                continue
            u, w = jo_in[m]
            ok = u != cell
            add_batch(incoming, g, u[ok], w[ok], [m, cell], [c])
        if not incoming['paths']:
            continue
        name = label(g, cell)
        paired = min(incoming['flow'], out['flow'])
        cells.append(dict(index=cell, body_id=int(g['body_id'][cell]), type=name,
                          incoming=incoming, outgoing=out, paired_score=paired))
        row = types.setdefault(name, dict(type=name, cells=0, incoming=empty_stat(), outgoing=empty_stat(), paired_score=0))
        row['cells'] += 1
        row['paired_score'] += paired
        merge_stat(row['incoming'], incoming)
        merge_stat(row['outgoing'], out)
    rows = sorted(types.values(), key=lambda r: (-r['outgoing']['flow'], -r['incoming']['flow'], r['type']))
    for rank, row in enumerate(rows, 1):
        row['rank'] = rank
    return rows, cells


def overlap(left, right, limit=None):
    a = [r['type'] for r in left if r['type'] != 'unnamed']
    b = [r['type'] for r in right if r['type'] != 'unnamed']
    if limit is not None:
        a, b = a[:limit], b[:limit]
    aa, bb = set(a), set(b)
    return dict(female=a, banc=b, shared=sorted(aa & bb), intersection=len(aa & bb),
                union=len(aa | bb), jaccard=len(aa & bb)/len(aa | bb) if aa | bb else None,
                unnamed_female=[r for r in left if r['type']=='unnamed'],
                unnamed_banc=[r for r in right if r['type']=='unnamed'])


def resolve(dataset, g, graph_hash):
    from flybench.dictionary import groups
    from flybench.dictionary.entries import entries
    selected = groups(dataset, graph=g)
    wanted = list(TARGETS) + list(B1) + ['JO-A', 'JO-B', 'SAG', 'L1', 'L2', 'LC10a', 'ORN']
    if 'PN' in selected:
        wanted.append('PN')
    definitions = {e.name: e for e in entries(dataset)}
    export_path = Path(f'build/dictionary_{dataset}.json')
    export = json.loads(export_path.read_text(encoding='utf-8-sig'))
    if export['graph']['sha256'] != graph_hash:
        raise ValueError('Dictionary export graph identity mismatch')
    # API is authoritative; older serialized exports are retained as provenance.
    serial = export.get('entries', [])
    if isinstance(serial, dict):
        serial = list(serial.values())
    by_name = {r['name']: r for r in serial}
    identities = {}
    for name in wanted:
        rows = selected[name]
        identities[name] = dict(count=len(rows), indices=rows.tolist(), body_ids=g['body_id'][rows].tolist(),
                                selector=asdict(definitions[name].selector),
                                export_count=by_name.get(name, {}).get('count'))
    return selected, identities


def analyze_dataset(dataset, graph_hash, quick, deadline, rawdir):
    from flybench.graph.schema import load, validate
    started = time.perf_counter()
    g = load(f'build/graph_{dataset}.npz')
    validate(g)
    selected, identities = resolve(dataset, g, graph_hash)
    expected = {'female': 4, 'banc': 6, 'male': 4}
    if len(selected['vpoEN']) != expected[dataset]:
        raise ValueError('Unexpected vpoEN selector count')
    mapping = Map(g, deadline)
    result = dict(dataset=dataset, graph_sha256=graph_hash, selectors=identities,
                  graph_meta=g['meta'], M1={}, M2=[], M3={}, M4=[], M5=[])
    raw = {}
    for target in TARGETS:
        result['M1'][target], raw[target], _ = mapping.direct(selected[target])
    save(rawdir/f'{dataset}_M1_cells.json', raw)
    result['M2'], origins = mapping.m2(selected['vpoEN'])
    save(rawdir/f'{dataset}_M2_source_cells.json', {str(k): v for k, v in origins.items()})
    save(rawdir/f'{dataset}_checkpoint.json', result)
    print(json.dumps(dict(dataset=dataset, stage='M1/M2', seconds=time.perf_counter()-started)), flush=True)
    if not quick:
        jo = np.union1d(selected['JO-A'], selected['JO-B'])
        sources = {'JO-A/B': jo, 'SAG': selected['SAG'], 'L1/L2': np.union1d(selected['L1'], selected['L2']),
                   'LC10a': selected['LC10a'], 'ORN': selected['ORN']}
        if 'PN' in selected:
            sources['PN'] = selected['PN']
        result['PN_status'] = 'available' if 'PN' in selected else 'unavailable: no dictionary PN key'
        total = result['M1']['vpoEN']['total_synapses']
        for name, src in sources.items():
            stats, covered = mapping.source_paths(src, selected['vpoEN'])
            for row in stats:
                row['coverage_share'] = row['cumulative_covered_synapses']/total if total else None
            result['M3'][name] = dict(source_cells=len(src), depths=stats, total_flow=sum(r['flow'] for r in stats),
                                      total_paths=sum(r['paths'] for r in stats),
                                      coverage_share=sum(covered.values())/total if total else None)
            save(rawdir/f'{dataset}_M3_{name.replace("/", "_")}_covered.json',
                 [dict(source=u, target=t, count=w) for (u, t), w in sorted(covered.items())])
            save(rawdir/f'{dataset}_checkpoint.json', result)
            print(json.dumps(dict(dataset=dataset, stage='M3', source=name, paths=sum(r['paths'] for r in stats))), flush=True)
        result['M4'] = m4(mapping, selected, selected['vpoEN'], result['M1']['vpoEN'], origins, jo)
        result['M5'], cells = m5(mapping, jo, selected['vpoEN'], origins)
        save(rawdir/f'{dataset}_M5_cells.json', cells)
    result['wall_seconds'] = time.perf_counter()-started
    save(rawdir/f'{dataset}_checkpoint.json', result)
    return result


def path_text(w):
    if w is None:
        return 'no path'
    return ' -> '.join(w['types']) + f" ({w['signs']}; min={w['bottleneck']}; IDs=" + ','.join(map(str, w['body_ids'])) + ')'


def table(lines, columns, rows):
    lines.extend(['', SCOPE, '', '| ' + ' | '.join(columns) + ' |', '| ' + ' | '.join(['---'] * len(columns)) + ' |'])
    for row in rows:
        lines.append('| ' + ' | '.join(str(v).replace('|', '&#124;').replace('\n', ' ') for v in row) + ' |')


def report(record, path):
    lines = ['# vpoEN reverse input map v1', '', 'Status: ' + record['status'], '',
             'Chemical synapses only; electrical synapses are absent from these graphs.',
             'these counts are anatomical path strengths, not predictions of network response',
             'FAFB v783 is primary; BANC v888 is a second individual; MaleCNS is comparison only.',
             'Path sums reuse edges. Input coverage deduplicates final edges; modalities overlap.',
             'Signs come from graph sign, including 0; NT annotations are reported separately.', '',
             '## Provenance', '', 'Protocol SHA-256: ' + PROTOCOL_HASH]
    table(lines, ['Graph', 'SHA-256'], record['graph_sha256'].items())
    lines += ['', 'Data attribution: FAFB/FlyWire, Dorkenwald et al. (2024); Shiu et al. (2024); '
              'BANC source authors (2026); MaleCNS source authors. All source datasets CC-BY-4.0. '
              'Exact input/source hashes and population contracts are preserved in results graph_meta; '
              'see docs/graph-schema.md for original data references.',
              f"Analysis wall seconds: {record['wall_seconds']:.3f}.",
              'Runtime: '+json.dumps(record['environment'])]
    for d, data in record['datasets'].items():
        lines += ['', '## ' + d, '']
        table(lines, ['Selector', 'Cells', 'Definition', 'Export count'],
              [(k, r['count'], json.dumps(r['selector']), r['export_count']) for k, r in data['selectors'].items()])
        for target, item in data['M1'].items():
            lines += ['', f"### M1 {target}: {item['total_synapses']} synapses, {item['input_cells']} input cells",
                      f"Self-edge synapses: {item['self_synapses']}. Top 40; full type and cell tables are retained."]
            table(lines, ['Rank', 'Type', 'Synapses', 'Cells', 'Sign:synapses', 'NT:synapses', 'Input share'],
                  [(r['rank'], r['type'], r['synapses'], r['cells'], json.dumps(r['sign_synapses']),
                    json.dumps(r['nt_synapses']), f"{100*r['share']:.6f}%" if r['share'] is not None else 'undefined') for r in item['types'][:40]])
        lines += ['', '### M2 strongest two-edge chain per middle type', 'Ranked by E3 maximum; sums are separate. Top 40.']
        table(lines, ['Middle type', 'Maximum', 'Paths', 'Sum', 'Signs:sum', 'Strongest witness'],
              [(r['type'], r['maximum'], r['paths'], r['flow'], json.dumps(r['sign_flow']), path_text(r['best'])) for r in data['M2'][:40]])
        if record['quick']:
            continue
        lines += ['', '### M3 source intersections', data['PN_status']]
        table(lines, ['Source', 'Cells', 'Depth', 'Paths', 'Sum', 'Signs:sum', 'Cumulative input coverage', 'Strongest witness'],
              [(name, item['source_cells'], r['depth'], r['paths'], r['flow'], json.dumps(r['sign_flow']),
                f"{100*r['coverage_share']:.6f}%" if r['coverage_share'] is not None else 'undefined', path_text(r['best']))
               for name, item in data['M3'].items() for r in item['depths']])
        lines += ['', '### M4 B1 candidate lists']
        table(lines, ['List', 'Direct synapses', 'Direct signs:synapses', 'Direct share', 'M1 ranks', 'Two-edge maximum', 'Two-edge sum', 'Best chain', 'JO-middle maximum'],
              [(r['name'], r['direct_synapses'], json.dumps(r['direct_sign_synapses']), f"{100*r['direct_share']:.6f}%" if r['direct_share'] is not None else 'undefined',
                json.dumps(r['member_type_ranks']), r['two_edge']['maximum'], r['two_edge']['flow'],
                path_text(r['two_edge']['best']), r['jo_middle']['maximum']) for r in data['M4']])
        lines += ['', '### M5 candidate types', 'Top 40 by outgoing summed bottlenecks; both halves meet at the same eligible cell.']
        table(lines, ['Type', 'Cells', 'JO input sum', 'vpoEN output sum', 'Paired score', 'Input signs:sum', 'Output signs:sum', 'Best input', 'Best output'],
              [(r['type'], r['cells'], r['incoming']['flow'], r['outgoing']['flow'], r['paired_score'],
                json.dumps(r['incoming']['sign_flow']), json.dumps(r['outgoing']['sign_flow']),
                path_text(r['incoming']['best']), path_text(r['outgoing']['best'])) for r in data['M5'][:40]])
    if record.get('M6'):
        lines += ['', '## M6 BANC versus FAFB']
        table(lines, ['Comparison', 'Female named types', 'BANC named types', 'Intersection', 'Union', 'Jaccard', 'Shared types'],
              [(k, len(v['female']), len(v['banc']), v['intersection'], v['union'], v['jaccard'], ', '.join(v['shared'])) for k, v in record['M6'].items()])
        for key, val in record['M6'].items():
            lines += ['', key+' unnamed separately: '+json.dumps({k: v for k, v in val.items() if k.startswith('unnamed')} )]
    female = record['datasets'].get('female', {})
    if female.get('M4'):
        lists = '; '.join(f"{r['name']} supplies {r['direct_synapses']} direct synapses ({100*r['direct_share']:.6f}% of vpoEN input)" for r in female['M4'])
        best = None
        for r in female['M3']['JO-A/B']['depths']:
            if r['best'] is not None and better(r['best'], best):
                best = r['best']
        lines += ['', '## What this map says about L5a', '',
                  lists+'. The strongest JO-to-vpoEN cell path within three edges is '+path_text(best)+'. '
                  'These small direct shares and signed indirect chains describe the anatomical context of the '
                  'unchanged vpoEN/vpoDN readouts in L5a. They do not explain the dynamic result by themselves: '
                  'the silent baseline prevents observing suppression below zero, and prior saturation flags '
                  'remain applicable. No gain or physiological efficacy follows from these sums.']
    lines += ['', '## Open points and execution limits', '',
              'Literal type overlap is not a homology test. Unnamed cells, unknown sign/NT, source proxies '
              '(including female SAG/SpsP), unequal population contracts, sex and individual differences '
              'remain unresolved. M5 halves need not concatenate into a simple four-edge path. '
              'No dictionary entry or behavioral identity is assigned.',
              'Dictionary API selectors are authoritative. Export counts are shown to expose stale serialized entries.',
              'Clean room: excluded source trees were not inspected; only the supplied runtime dependency directory was used.',
              'No simulation, git add/commit/push, or core/hook/ear/dictionary changes.',
              'Acceptance test and artifact-integrity evidence: records/vpoen_inputs_v1_checks.json.',
              'Deviations: '+json.dumps(record.get('deviations', [])), '',
              '## Preregistration (verbatim)', '', PROTOCOL.read_text(encoding='utf-8')]
    Path(path).write_text('\n'.join(lines), encoding='utf-8')


def run(quick=False):
    started = time.perf_counter()
    if sha(PROTOCOL) != PROTOCOL_HASH:
        raise ValueError('Preregistration SHA-256 mismatch')
    freeze_path = Path(str(PREFIX)+'_freeze.json')
    freeze = json.loads(freeze_path.read_text(encoding='utf-8'))
    if freeze['protocol_sha256'] != PROTOCOL_HASH:
        raise ValueError('Missing or mismatched prior protocol seal')
    graph_hashes = {d: sha(f'build/graph_{d}.npz') for d in ('female', 'banc', 'male')}
    if freeze['graph_sha256'] and freeze['graph_sha256'] != graph_hashes:
        raise ValueError('Graph changed since freeze')
    freeze.update(graph_sha256=graph_hashes, status='sealed',
                  dictionary_sha256={d: sha(f'build/dictionary_{d}.json') for d in graph_hashes})
    if 'inputs_frozen_utc' not in freeze:
        freeze['inputs_frozen_utc'] = datetime.now(timezone.utc).isoformat()
        save(freeze_path, freeze)
    rawdir = RAW/('quick' if quick else 'full')
    rawdir.mkdir(parents=True, exist_ok=True)
    source_paths = [PROTOCOL, Path(__file__).relative_to(Path.cwd()), Path('tests/test_vpoen_inputs.py'),
                    *sorted(Path('flybench/dictionary').glob('*.py')), Path('flybench/graph/select.py'), Path('flybench/graph/schema.py')]
    record = dict(protocol_sha256=PROTOCOL_HASH, graph_sha256=graph_hashes, quick=quick,
                  started_utc=datetime.now(timezone.utc).isoformat(), status='PARTIAL', datasets={},
                  source_sha256={p.as_posix(): sha(p) for p in source_paths},
                  dictionary_sha256=freeze['dictionary_sha256'],
                  environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                                   os=platform.system(), runtime='task-specified CPython and dependency environment',
                                   LC_ALL='C', LANG='C', bytecode=False, pytest_plugin_autoload=False), deviations=[])
    try:
        for d in (('female',) if quick else ('female', 'banc', 'male')):
            record['datasets'][d] = analyze_dataset(d, graph_hashes[d], quick, started+2700, rawdir)
            gc.collect()
        if not quick:
            f, b = record['datasets']['female'], record['datasets']['banc']
            record['M6'] = dict(M1_top20=overlap(f['M1']['vpoEN']['types'], b['M1']['vpoEN']['types'], 20),
                                M5_top20=overlap(f['M5'], b['M5'], 20), M5_all=overlap(f['M5'], b['M5']))
        record['status'] = 'COMPLETE'
    except TimeoutError as exc:
        record['deviations'].append(str(exc))
    record['wall_seconds'] = time.perf_counter()-started
    record['raw_sha256'] = {p.as_posix(): sha(p) for p in sorted(rawdir.glob('*.json'))}
    output = rawdir/'quick' if quick else PREFIX
    Path(str(output)+'_results.json').write_text(json.dumps(summary_record(record), separators=(',', ':'), allow_nan=False)+'\n', encoding='utf-8')
    report(record, str(output)+'_report.md')
    print(json.dumps(dict(status=record['status'], wall_seconds=record['wall_seconds'])), flush=True)
    return 0 if record['status']=='COMPLETE' else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()
    raise SystemExit(run(args.quick))
