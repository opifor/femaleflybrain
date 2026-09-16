import copy
import numpy as np
import pytest
from scipy.sparse import csr_matrix
from flybench.experiment.hearing import (choose, summary, seeds_for, conditions,
    condition, run, validate, freeze, scaled_weights, test_result as heldout_result)


def test_freeze_rule_lowest_strict_and_fallback():
    assert choose([dict(dose=180, mean=9, se=1), dict(dose=60, mean=3, se=1)], 720)['dose'] == 60
    assert choose([dict(dose=60, mean=2, se=1), dict(dose=180, mean=3, se=1)], 720)['dose'] == 180
    assert choose([dict(dose=60, mean=0, se=0), dict(dose=180, mean=-3, se=0)], 720) == dict(dose=720, rule='no transfer', fallback=True)
    assert summary([1, 3])['verdict'] == 'not supported'
    assert summary([3, 3])['verdict'] == 'supported'


def test_seed_split_and_frozen_conditions():
    assert seeds_for('quick') == (0, 1)
    assert seeds_for('calibration') == tuple(range(10))
    assert seeds_for('test') == tuple(range(10, 30))
    assert not set(seeds_for('calibration')) & set(seeds_for('test'))
    cfgs = conditions('test', dict(jo=dict(dose=720), vpoEN=dict(dose=60)))
    assert {c['direct_vpoEN_hz'] for c in cfgs} == {0, 60}
    assert {c['jo_max_hz'] for c in cfgs} == {180, 720}
    assert all(condition(state=s, song=a, gain=g) in cfgs for s in ('virgin', 'mated') for a in (False, True) for g in (1., 1.3))


@pytest.fixture(scope='module')
def tiny():
    w = csr_matrix(np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1000], [0, 0, 0, 0, 1500, -7],
        [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1000, 0]]))
    graph = dict(body_id=np.arange(6), data=w.data, indices=w.indices, indptr=w.indptr, meta={})
    groups = {name: np.array([i]) for i, name in enumerate(('JO-A', 'JO-B', 'SAG', 'vpoEN', 'vpoDN', 'pC1'))}
    return graph, run('quick', graph, groups, device='cpu')


def test_gain_only_positive(tiny):
    graph, _ = tiny
    actual = scaled_weights(graph, 1.3).data
    np.testing.assert_array_equal(actual[graph['data'] < 0], graph['data'][graph['data'] < 0])
    np.testing.assert_allclose(actual[graph['data'] > 0], graph['data'][graph['data'] > 0]*1.3)
    assert -7 in graph['data']


def test_record_parameters_cells_and_paired_drive(tiny):
    _, record = tiny
    assert validate(record) is record
    assert record['parameters']['dt'] == .2
    assert record['parameters']['w_syn'] == .275
    assert record['kernel'] == 'shiu'
    assert len(record['protocol']['sha256']) == 64
    for t in record['trials']:
        c = t['condition']
        assert set(c) == {'state', 'song', 'jo_max_hz', 'direct_vpoEN_hz', 'excitatory_gain'}
        for g in ('vpoEN', 'vpoDN', 'pC1'):
            assert t['rates_hz'][g] == pytest.approx(np.mean(t['cell_rates_hz'][g]))
        for w in t['windows']:
            for d in w['drive_slices']:
                assert set(d) == {'requested_hz', 'sampled_hz', 'delivered_hz'}
                assert d['requested_hz']['vpoEN'] == [c['direct_vpoEN_hz']]
                assert d['requested_hz']['SAG'] == [50 if c['state'] == 'virgin' else 0]
                assert max(d['requested_hz']['JO-A']) <= c['jo_max_hz']
    a = next(t for t in record['trials'] if t['condition'] == condition(song=True, jo=60) and t['seed'] == 0)
    b = next(t for t in record['trials'] if t['condition'] == condition(jo=60) and t['seed'] == 0)
    assert [d['sampled_hz']['SAG'] for w in a['windows'] for d in w['drive_slices']] == [d['sampled_hz']['SAG'] for w in b['windows'] for d in w['drive_slices']]
    with pytest.raises(ValueError, match='Only full'):
        freeze(record)
    broken = copy.deepcopy(record)
    broken['seeds'] = [10, 11]
    with pytest.raises(ValueError, match='Seed split'):
        validate(broken)
    broken = copy.deepcopy(record)
    broken['trials'].pop()
    with pytest.raises(ValueError, match='coverage'):
        validate(broken)


def test_heldout_contrasts_use_seed_pairs():
    frozen = dict(jo=dict(dose=720), vpoEN=dict(dose=60))
    record = dict(seeds=list(seeds_for('test')), trials=[])
    for c in conditions('test', frozen):
        for s in seeds_for('test'):
            rate = s + (4 if c['song'] else 0) + (6 if c['state'] == 'virgin' else 2)*bool(c['direct_vpoEN_hz'])
            record['trials'].append(dict(seed=s, condition=c, rates_hz=dict(vpoDN=rate)))
    result = heldout_result(record, frozen)
    assert (result['T1']['mean'], result['T1']['se'], result['T1']['n']) == (4, 0, 20)
    assert result['T2']['mean'] == 6
    assert result['T3']['mean'] == -4
    assert result['T3']['verdict'] == result['T4']['verdict'] == 'descriptive'


def test_freeze_uses_calibration_only(tiny):
    _, quick = tiny
    record = copy.deepcopy(quick)
    record['stage'] = 'calibration'
    record['seeds'] = list(range(10))
    record['trials'] = []
    for cfg in conditions('calibration'):
        template = next(t for t in quick['trials'] if t['condition'] == cfg)
        for seed in range(10):
            trial = copy.deepcopy(template)
            trial['seed'] = seed
            trial['windows'] = (trial['windows']*4)[:20]
            trial['rates_hz']['vpoEN'] = 5 if cfg['song'] and cfg['jo_max_hz'] >= 180 else 0
            threshold = 180 if cfg['state'] == 'virgin' else 60
            trial['rates_hz']['vpoDN'] = 4 if cfg['direct_vpoEN_hz'] >= threshold else 0
            record['trials'].append(trial)
    result = freeze(record)
    assert result['jo']['dose'] == 180 and not result['jo']['fallback']
    assert result['vpoEN']['dose'] == 180 and not result['vpoEN']['fallback']
    assert result['calibration_seeds'] == list(range(10))
    assert result['test_seeds'] == list(range(10, 30))
    record['trials'][0]['seed'] = 10
    with pytest.raises(ValueError, match='coverage'):
        freeze(record)
