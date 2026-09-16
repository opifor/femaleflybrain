import os

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from flybench.experiment.direction_probe import (
    PROTOCOL, PROTOCOL_HASH, arrived_mass, classify, flux_table, grid,
    paired, sha, source_rows, stats,
)
from flybench.sim.release import GradedRelease


@pytest.mark.parametrize('cells,expected', [
    ([-2,-2], 'suppression'), ([-1,-1], 'equivalence-zero'),
    ([1,1], 'equivalence-zero'), ([1.01,1.01], 'unexplained increase'),
    ([-8,4], 'unclassified (cell heterogeneity)'),
    ([-4,4], 'unclassified (cell heterogeneity)'),
    ([-3,3], 'equivalence-zero'), ([-6,3], 'suppression'),
])
def test_classes(cells, expected):
    assert classify(cells) == expected


def test_flux_absolute_onset_and_clipping():
    points = grid()
    assert len(points)==18 and len({p['flux'] for p in points})==8
    assert [p['ceiling'] for p in points[:6]] == ['uncapped']*6
    assert points[10]['flux']==1/2.2 and points[-1]['flux']==.2
    flux = flux_table(.3,2)
    assert flux.shape==(5000,2)
    assert np.count_nonzero(flux[:1000])==0
    np.testing.assert_array_equal(flux[1000:], np.full((4000,2), .3))


def test_dictionary_sources_are_used_without_substitution():
    dictionary = {'AMMC-B1-candidate': [1,4], 'AMMC-B1-candidate-graph': [2]}
    np.testing.assert_array_equal(source_rows(dictionary,'K1'), [1,4])
    np.testing.assert_array_equal(source_rows(dictionary,'K2'), [2])
    hook = GradedRelease(source_rows(dictionary,'K1'), flux_table(.1,2))
    np.testing.assert_array_equal(hook.source_rows, [1,4])
    with pytest.raises(KeyError):
        source_rows({},'K1')


def test_paired_seed_means_and_rejected_reordering():
    delta = paired([[3,9],[5,7]], [[1,5],[1,3]], [0,1],[0,1])
    np.testing.assert_array_equal(delta, [[2,4],[4,4]])
    assert stats(delta.mean(axis=0)) == {'mean':3.5, 'se':.5}
    with pytest.raises(ValueError, match='Seed'):
        paired([[3,9]],[[1,5]],[0,1],[1,0])


def test_mass_excludes_pending_delay_and_pre_onset():
    rows = csr_matrix([[0,2,-3]])
    np.testing.assert_array_equal(arrived_mass(rows,.5,1009), [0,0,0])
    np.testing.assert_allclose(arrived_mass(rows,.5,1010), [0,.2,.3])
    np.testing.assert_allclose(arrived_mass(rows,.5,5000), [0,798.2,1197.3])


def test_hook_onset_across_continuation():
    from flybench.sim.lif import Simulator
    from flybench.sim.params import Parameters
    sim = Simulator([[0,2],[0,0]], params=Parameters(dt=.2), kernel='shiu',
                    release=GradedRelease([0], flux_table(.1,1)))
    head = sim.run(200)
    assert head.state.step == 1000 and head.counts.sum() == 0
    assert np.count_nonzero(head.state.g) == 0
    before_arrival = sim.run(1.8, state=head.state)
    assert np.count_nonzero(before_arrival.state.g) == 0
    arrived = sim.run(.2, state=before_arrival.state)
    assert arrived.state.g[1] == pytest.approx(2*.275*.1*.2)


def test_preregistration_seal():
    assert sha(PROTOCOL)==PROTOCOL_HASH


def test_harness_failure_probe():
    assert os.environ.get('DIRECTION_PROBE_FORCE_FAIL') != '1', 'Intentional harness failure'
