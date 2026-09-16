"""Synthetic selectors, paired decisions, missingness and runner failure probe."""
import copy
import os
import numpy as np
import pytest
from flybench.experiment.water_dose import REF, conditions, mn9_other, evaluate
from flybench.experiment.benchmarks import summary


def test_condition_grid():
    assert list(conditions().items()) == [('baseline', (None, 0)), ('water100', ('water', 100)),
        ('water160', ('water', 160)), ('water200', ('water', 200)), ('water260', ('water', 260)),
        ('sugar100', ('sugar', 100)), ('sugar200', ('sugar', 200))]


def test_opposite_exact_type_all_cells():
    g = dict(body_id=np.array([REF, 2, 3, 4, 5, 6]), type=np.array(['MN9', 'MN9', 'MN9', 'MN9x', 'MN9', 'MN9']),
             side=np.array(['L', 'R', 'L', 'R', 'R', '']))
    assert mn9_other(g).tolist() == [1, 4]
    g['side'][0] = 'R'
    assert mn9_other(g).tolist() == [2]
    g['side'][0] = ''
    assert mn9_other(g).tolist() == []
    g['side'][0] = 'L'
    g['type'][0] = ''
    assert mn9_other(g).tolist() == []
    g['body_id'][0] = 7
    with pytest.raises(ValueError, match='MN9_ref'):
        mn9_other(g)


def fixture(other=True):
    r = dict(stage='full', seeds=list(range(10)), groups={'MN9_other': {'count': int(other)}}, trials=[])
    for c in conditions():
        for s in r['seeds']:
            ref = {'water100': 1, 'water160': 3, 'water200': 4, 'water260': 5, 'sugar100': 63.4, 'sugar200': 90}.get(c, 0)
            r['trials'].append(dict(condition=c, seed=s, rates_hz={'MN9_ref': ref, 'MN9_other': ref}, delivered_grn_hz=0))
    return r


def test_known_decisions_and_strict_se():
    out = evaluate(fixture())
    assert out['W1']['mean'] == 3 and out['W1']['supported']
    assert out['W2'] == {'MN9_ref': True, 'MN9_other': True}
    assert out['W3'] == 'no laterality signal'
    assert out['W4']['passed']
    assert summary([1, 3])['se'] == 1
    assert not summary([1, 3])['supported']
    assert summary([2, 4])['supported']


def test_laterality_and_bilateral_silence():
    r = fixture()
    for t in r['trials']:
        if t['condition'] == 'water160':
            t['rates_hz']['MN9_other'] += 2
    assert evaluate(r)['W3'] == 'laterality mismatch SUSPECTED'
    for t in r['trials']:
        if t['condition'].startswith('water'):
            t['rates_hz'] = {'MN9_ref': 0, 'MN9_other': 0}
    out = evaluate(r)
    assert out['W3'] == 'pathway silent at all tested doses'
    assert not out['W1']['supported'] and not out['W2']['MN9_ref']


def test_absence_never_zero():
    out = evaluate(fixture(False))
    assert out['W3'] == 'not evaluable: MN9_other absent'
    assert out['W2']['MN9_other'] is None
    assert all(row['MN9_other'] is None for row in out['table'].values())


@pytest.mark.parametrize('value,passed', [(63.4*.85, True), (63.4*1.15, True), (53., False), (74., False)])
def test_w4_band(value, passed):
    r = fixture()
    for t in r['trials']:
        if t['condition'] == 'sugar100':
            t['rates_hz']['MN9_ref'] = value
    assert evaluate(r)['W4']['passed'] == passed
    assert evaluate(r)['status'] == ('PASS' if passed else 'FAIL-CLOSED')


def test_pairing_and_invalid_coverage():
    r = fixture()
    for t in r['trials']:
        if t['condition'] in ('baseline', 'water160'):
            t['rates_hz']['MN9_ref'] += t['seed'] * 100
    r['trials'].reverse()
    assert evaluate(r)['W1']['se'] == 0
    bad = copy.deepcopy(r)
    bad['trials'].append(bad['trials'][0])
    with pytest.raises(ValueError, match='coverage'):
        evaluate(bad)
    r['trials'].pop()
    with pytest.raises(ValueError, match='coverage'):
        evaluate(r)


@pytest.mark.skipif(os.environ.get('WATER_DOSE_FAIL_PROBE') != '1', reason='opt-in failure probe')
def test_intentional_failure_probe():
    assert False, 'Intentional harness failure'
