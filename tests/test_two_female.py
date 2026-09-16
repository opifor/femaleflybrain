"""Synthetic selection, paired statistics and saved-record wiring checks."""
import copy
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from flybench.dictionary.entries import entries
from flybench.experiment import two_female as tf
from flybench.experiment.protocol import Protocol
from flybench.experiment.record import sha256


@pytest.fixture
def graph():
    types = ['JO-A', 'JO-B', 'ANXXX983', 'pC1a', 'DNp37',
             'JO-A-unclear', 'pC1a', 'pC1x', 'AN_SMP_2', 'AN_FLA_SMP_2']
    n = len(types)
    weights = csr_matrix((np.array([1000, 2000, 3000]),
                          (np.array([0, 2, 2]), np.array([3, 3, 4]))), shape=(n, n))
    return {'body_id': np.arange(100, 100+n, dtype=np.int64), 'type': np.array(types),
            'superclass': np.array(['sensory', 'sensory', 'ascending', 'central_brain_intrinsic',
                                    'descending', 'sensory', 'motor', 'central_brain_intrinsic',
                                    'ascending', 'ascending']),
            'data': weights.data, 'indices': weights.indices, 'indptr': weights.indptr, 'meta': {}}


def snapshot(dataset):
    return {'dataset': dataset, 'entries': [e.to_dict() for e in entries(dataset)]}


def test_selectors_alias_scope_and_identity(graph):
    groups = tf.select_groups(graph, snapshot('banc'), 'banc')
    for name, expected in {'JO-A': [0], 'JO-B': [1], 'SAG': [2], 'pC1': [3], 'vpoDN': [4]}.items():
        assert groups[name].tolist() == expected
    ids = tf.identities(graph, groups)
    assert ids['SAG']['body_ids'] == [102]
    assert ids['pC1']['superclasses'] == {'central_brain_intrinsic': 1}
    female = tf.select_groups(graph, snapshot('female'), 'female')
    assert female['SAG'].tolist() == [2, 8, 9]
    assert female['pC1'].tolist() == [3, 6]
    missing = copy.deepcopy(graph)
    missing['type'][4] = 'missing'
    assert tf.select_groups(missing, snapshot('banc'), 'banc')['vpoDN'].size == 0
    missing['type'][2] = 'missing'
    with pytest.raises(ValueError, match='SAG'):
        tf.select_groups(missing, snapshot('banc'), 'banc')
    with pytest.raises(ValueError, match='dataset'):
        tf.select_groups(graph, snapshot('female'), 'banc')


@pytest.fixture(scope='module')
def small_record():
    n = 5
    weights = csr_matrix((np.array([1000, 2000, 3000]),
                          (np.array([0, 2, 2]), np.array([3, 3, 4]))), shape=(n, n))
    graph = {'body_id': np.arange(n), 'data': weights.data, 'indices': weights.indices,
             'indptr': weights.indptr, 'meta': {}}
    groups = {name: np.array([i]) for i, name in enumerate(('JO-A', 'JO-B', 'SAG', 'pC1', 'vpoDN'))}
    return tf.runner.run(Protocol(name='two_female_v1', seeds=(0, 1), windows=6), graph, groups, device='cpu')


def test_saved_record_path_and_exact_windows(small_record, tmp_path):
    frozen = {'populations': {}}
    tf.save_json(tmp_path/tf.FREEZE, frozen)
    compact = tf.save_execution(small_record, frozen, tmp_path, quick=True)
    path = tmp_path/compact['raw_record']['path']
    assert path.relative_to(tmp_path).as_posix() == tf.RAW+'/quick_experiment.json'
    assert tf.read_json(path)['trials'] == small_record['trials']
    assert compact['raw_record']['sha256'] == sha256(path)
    assert all('windows' not in t for t in compact['trials'])
    assert len(compact['trials']) == 16
    assert tf.read_json(tmp_path/tf.RAW/'quick_summary.json') == compact
    assert not path.read_bytes().startswith(b'\xef\xbb\xbf')
    assert not (tmp_path/tf.BASELINE).exists()
    broken = copy.deepcopy(small_record)
    broken['trials'].pop()
    with pytest.raises(ValueError, match='Missing or duplicate'):
        tf.save_execution(broken, frozen, tmp_path, quick=True)


def test_pair_by_seed_se_and_zero_denominator(small_record):
    a, b = copy.deepcopy(small_record), copy.deepcopy(small_record)
    for t in a['trials']:
        t['rates_hz'] = {'vpoDN': 3 if t['seed'] == 0 else 7, 'pC1': 0, 'network': 0}
    for t in b['trials']:
        t['rates_hz'] = {'vpoDN': 1 if t['seed'] == 0 else 3, 'pC1': 0, 'network': 0}
    b['trials'].reverse()
    rows = tf.comparisons(a, b)
    assert rows[0]['paired_difference'] == {'mean': 3, 'se': 1, 'n': 2}
    assert rows[0]['absolute_difference_over_paired_se'] == 3
    assert rows[1]['absolute_difference_over_paired_se'] is None
    assert rows[1]['ratio_status'] == 'undefined: 0/0'
    for t in a['trials']:
        t['rates_hz']['pC1'] = 2
    assert tf.comparisons(a, b)[1]['ratio_status'] == 'unbounded: nonzero/0'
    assert all(c['label'] == tf.LABEL for c in tf.contrasts(a))
    b['protocol']['seeds'] = [1, 2]
    with pytest.raises(ValueError, match='seed coverage'):
        tf.comparisons(a, b)


def test_ignition_and_warmup_are_from_runner(small_record):
    for trial in small_record['trials']:
        measured = trial['windows'][4:]
        assert trial['rates_hz']['network'] == np.mean([w['rates_hz']['network'] for w in measured])
        assert trial['ignition_fraction'] == np.mean([w['rates_hz']['network'] > 30 for w in measured])
        if trial['condition'] == 'mated_silence':
            assert trial['rates_hz'] == {'vpoDN': 0, 'pC1': 0, 'network': 0}


def test_freeze_tampering_is_rejected(tmp_path):
    path = tmp_path/'input.txt'
    path.write_text('original', encoding='utf-8')
    tf.save_json(tmp_path/tf.FREEZE, {'sha256': {'input.txt': sha256(path)}})
    assert tf.verify_freeze(tmp_path)['sha256']['input.txt'] == sha256(path)
    path.write_text('changed', encoding='utf-8')
    with pytest.raises(ValueError, match='Frozen input changed'):
        tf.verify_freeze(tmp_path)
