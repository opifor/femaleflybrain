import os
import numpy as np
import pytest
from scipy.sparse import csr_matrix
from flybench.experiment.male_route import (
    lesion_outgoing, random_cells, route_rule, analyze, SEEDS, top_paths, summarize)


def graph_from_dense(values):
    matrix = csr_matrix(values)
    n = matrix.shape[0]
    return {'indptr': matrix.indptr, 'indices': matrix.indices,
            'data': matrix.data.copy(), 'count': abs(matrix.data),
            'body_id': np.arange(n), 'type': np.array(['cell']*n)}


def test_lesion_outgoing_only_and_original_unchanged():
    graph = graph_from_dense([[0, 2, 3], [-4, 0, -5], [6, 7, 8]])
    original = {k: v.copy() for k, v in graph.items()}
    changed = lesion_outgoing(graph, [1])
    for key in ('count', 'data'):
        np.testing.assert_array_equal(graph[key], original[key])
        for row in range(3):
            span = slice(graph['indptr'][row], graph['indptr'][row+1])
            if row == 1:
                assert np.count_nonzero(changed[key][span]) == 0
                assert changed[key][span].sum() == 0
            else:
                np.testing.assert_array_equal(changed[key][span], graph[key][span])
    np.testing.assert_array_equal(changed['indices'], graph['indices'])
    np.testing.assert_array_equal(changed['indptr'], graph['indptr'])
    assert changed['data'][0] == 2  # Incoming edge 0 -> 1 survives.
    with pytest.raises(ValueError):
        lesion_outgoing(graph, [3])


@pytest.mark.parametrize('lesion,mean,se,expected', [
    (4.9, 5.1, 1, 'route through P1 SUPPORTED'),
    (5, 5, 1, 'inconclusive'),
    (4, 6, 3, 'inconclusive'),
    (8, 2, 0, 'inconclusive'),
    (8.01, 1.99, 0, 'P1 bypass SUPPORTED')])
def test_r1_strict_boundaries(lesion, mean, se, expected):
    assert route_rule(10, lesion, {'mean': mean, 'se': se}) == expected
    assert route_rule(10, lesion, {'mean': mean, 'se': se}, r0=False) == 'unassessed'
    assert route_rule(10, lesion, {'mean': mean, 'se': se}, r2=False) == 'unassessed'


def test_seed_split_and_random_control():
    assert SEEDS == {'quick': (100, 101), 'test': tuple(range(20))}
    assert set(SEEDS['quick']).isdisjoint(SEEDS['test'])
    p1 = np.arange(46)
    for seed in SEEDS['test']:
        cells = random_cells(100, p1, seed)
        expected = np.sort(np.random.default_rng(seed+1000).choice(np.arange(46, 100), 46, replace=False))
        np.testing.assert_array_equal(cells, expected)
        assert len(set(cells)) == 46 and not set(cells) & set(p1)


def test_paired_analysis_and_coverage_gates():
    trials = [{'seed': s, 'network': n, 'drive': d, 'metrics': {'pIP10': s+(v if d != 'zero' else 0)}}
              for s in SEEDS['test'] for n, v in [('intact', 10), ('p1_lesion', 2), ('random_lesion', 9)]
              for d in ('zero', 'scent240', 'scent960')]
    result = analyze(trials)
    assert result['difference_of_differences'] == {'mean': 8., 'se': 0., 'n': 20}
    assert result['R0'] == result['R2'] == 'supported'
    assert result['R1'] == 'route through P1 SUPPORTED'
    for t in trials:
        if t['network'] == 'random_lesion' and t['drive'] != 'zero':
            t['metrics']['pIP10'] -= 1
    assert analyze(trials)['R2'] == 'not supported'  # Exactly 80% fails.
    assert analyze(trials)['R1'] == 'unassessed'
    for t in trials:
        if t['network'] == 'intact' and t['drive'] != 'zero':
            t['metrics']['pIP10'] -= 10
    assert analyze(trials)['R0'] == 'not supported'
    assert analyze(trials)['R2'] == 'unassessed'
    with pytest.raises(ValueError):
        analyze(trials[:-1])
    with pytest.raises(ValueError):
        analyze(trials+[trials[0]])


def test_top_paths_exact_bottleneck_and_cycle_exclusion():
    graph = graph_from_dense([[0, 9, 5, 0], [9, 0, 8, 3], [0, 0, 0, 6], [0, 0, 0, 0]])
    found = top_paths(graph, [0], [3], 2)
    assert [(p['indices'], p['bottleneck']) for p in found] == [([0, 2, 3], 5), ([0, 1, 3], 3)]
    assert top_paths(graph, [0], [3], 3)[0]['indices'] == [0, 1, 2, 3]
    assert top_paths(graph, [0], [3], 4) == []


def test_summary_preserves_network_identity_and_rate():
    rows = [{'network': 'intact', 'drive': 'zero', 'seed': seed,
             'metrics': {'network': value, 'pIP10': 0}} for seed, value in [(0, 1), (1, 3)]]
    result = summarize(rows)[0]
    assert result['network_kind'] == 'intact'
    assert result['network'] == {'mean': 2., 'se': 1., 'n': 2}


@pytest.mark.skipif(os.environ.get('FLYBENCH_FAIL_PROBE') != '1', reason='Opt-in harness probe')
def test_harness_failure_probe():
    assert False, 'Deliberate failure must return exit 1'
