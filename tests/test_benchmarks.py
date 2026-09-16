"""Selection, paired decisions, drive statistics and fail-closed coverage."""
import copy
import os

import numpy as np
import pytest

from flybench.experiment.benchmarks import (
    SHIU_IDS, conditions, select_groups, second_order, summary, evaluate, drive_audit,
)
from flybench.sim.fast_gpu import Simulator, Drive
from flybench.sim.params import Parameters
from scipy.sparse import csr_matrix


def test_literal_selectors_and_missing_ids():
    ids = sorted({v for values in SHIU_IDS.values() for v in values})
    graph = dict(body_id=np.array(ids + [1, 2]),
                 type=np.array([''] * len(ids) + ['JO-A1', 'JO-B2']))
    for k in ('side', 'superclass', 'nt', 'class'):
        graph[k] = np.array([''] * len(graph['body_id']))
    selected, audit = select_groups(graph)
    assert {k: len(selected[k]) for k in SHIU_IDS} == {k: len(v) for k, v in SHIU_IDS.items()}
    assert all(len(v) > 0 for v in selected.values())
    assert all(not v['missing_ids'] for v in audit.values())
    missing = SHIU_IDS['sugar'][0]
    graph['body_id'][ids.index(missing)] = -1
    selected, audit = select_groups(graph)
    assert audit['sugar']['missing_ids'] == [missing]
    assert len(selected['sugar']) == 20
    graph['body_id'][ids.index(SHIU_IDS['MN9'][0])] = -2
    with pytest.raises(ValueError, match='MN9'):
        select_groups(graph)


def synthetic_record():
    r = dict(seeds=[0, 1, 2], trials=[])
    for c in conditions():
        for s in r['seeds']:
            mn = {'sugar10': 1, 'sugar50': 5, 'sugar100': 10, 'sugar200': 20,
                  'sugar100_bitter100': 2, 'sugar100_Ir94e100': 4, 'water100': 6}.get(c, 0)
            bn = {'JO-CE100': 20, 'JO-F100': 2}.get(c, 0)
            r['trials'].append(dict(condition=c, seed=s, rates_hz=dict(MN9=mn, aBN1=bn)))
    return r


def test_paired_gate_known_answers():
    r = synthetic_record()
    out = evaluate(r)
    assert out['robustness_gate']
    assert out['B1']['bitter_suppression']['values'] == [8, 8, 8]
    assert out['B2']['CE_minus_F']['mean'] == 18
    assert out['B1']['dose_200_minus_100']['mean'] == 10
    for t in r['trials']:
        if t['condition'] == 'JO-F100':
            t['rates_hz']['aBN1'] = 21
    assert not evaluate(r)['passed']['B2']
    assert not evaluate(r)['robustness_gate']


def test_each_dose_and_suppression_are_required():
    for c, value in [('sugar50', 0), ('sugar100_bitter100', 11)]:
        r = synthetic_record()
        for t in r['trials']:
            if t['condition'] == c:
                t['rates_hz']['MN9'] = value
        assert not evaluate(r)['passed']['B1']


def test_se_strict_boundary_and_invalid_values():
    assert summary([1, 3])['se'] == 1
    assert not summary([1, 3])['supported']  # mean exactly 2 SE
    assert summary([2, 4])['supported']
    assert not summary([0, 0])['supported']
    for x in ([1], [1, np.nan], [1, np.inf]):
        with pytest.raises(ValueError):
            summary(x)


def test_seed_coverage_and_actual_pairing():
    r = synthetic_record()
    for t in r['trials']:
        if t['condition'] in ('JO-CE100', 'JO-F100'):
            t['rates_hz']['aBN1'] += 100 * t['seed']
    r['trials'].reverse()
    assert evaluate(r)['B2']['CE_minus_F']['se'] == 0
    bad = copy.deepcopy(r)
    bad['trials'].append(bad['trials'][0])
    with pytest.raises(ValueError, match='coverage'):
        evaluate(bad)
    r['trials'].pop()
    with pytest.raises(ValueError, match='coverage'):
        evaluate(r)


def test_second_order_uses_raw_counts_excludes_drive_and_breaks_ties():
    weights = csr_matrix(np.array([[9, 0, 3, 4, 2], [0, 0, 1, 0, 0],
                                  [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]))
    graph = dict(body_id=np.arange(5), type=np.array(['JO-A', 'JO-B', 'z', 'a', '']),
                 count=weights.data, indices=weights.indices, indptr=weights.indptr)
    groups, audit = second_order(graph, {'JO-A': np.array([0]), 'JO-B': np.array([1])})
    assert [r['type'] for r in audit['JO-AB']['top20']] == ['a', 'z']
    assert audit['JO-AB']['untyped_synapses'] == 2
    assert groups['JO-AB:z'].tolist() == [2]
    assert audit['JO-A']['top20'][0]['synapses'] == 4


def test_real_result_drive_audit_and_warmup():
    sim = Simulator(csr_matrix((2, 2)), device='cpu', params=Parameters(dt=.2), drive=Drive((0,), 100))
    head = sim.run_batch(200, seeds=[0, 1])
    tail = sim.run_batch(800, state=head.state)
    audit = drive_audit(head, tail, np.array([0]), 0)
    expected_count = head.counts[0, 0] + tail.counts[0, 0]
    assert audit['full_1s']['total_spike_hz'] == pytest.approx(expected_count)
    assert audit['full_1s']['delivered_hz'] == pytest.approx(expected_count)
    assert audit['full_1s']['sampled_hz'] == pytest.approx(expected_count)
    assert audit['measurement_800ms']['total_spike_hz'] == tail.counts[0, 0] / .8
    assert tail.counts[1, 0] == 0


@pytest.mark.skipif(os.environ.get('FLYBENCH_FAIL_PROBE') != '1', reason='opt-in failure probe')
def test_intentional_failure_probe():
    assert False, 'Intentional harness failure'
