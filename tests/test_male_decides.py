import os
import pytest
from flybench.experiment.male_decides import freeze_choice, ignition_threshold, SEEDS, stats, contrast


def row(dose, mean, se, ignition=0):
    return {'dose': dose, **{k: {'mean': mean, 'se': se} for k in ('P1', 'LC10a', 'pIP10')}, 'ignition': {'mean': ignition}}


def test_freeze_strict_boundary_and_ignition_exclusion():
    rows = [row(30, 2, 1), row(60, 3, 1, .51), row(120, 3, 1, .5), row(240, 4, 1)]
    assert freeze_choice(rows[::-1], 'A')['dose'] == 120
    assert freeze_choice(rows, 'B')['dose'] == 60
    assert freeze_choice([row(0, 0, 0), row(30, 1, 0)], 'C')['dose'] == 30
    assert freeze_choice([row(0, 1, 0), row(30, 2, 0)], 'C')['dose'] == 0


def test_no_qualifying_dose():
    rows = [row(30, 0, 0), row(960, 4, 1, 1)]
    assert freeze_choice(rows, 'A')['dose'] == 960
    assert freeze_choice(rows, 'A')['fallback'] is True
    for arm in ('B', 'C'):
        assert freeze_choice([row(30, 0, 0)], arm)['dose'] is None


def test_ignition_first_crossing_strict():
    assert ignition_threshold([row(120, 0, 0, 1), row(30, 0, 0, .5), row(60, 0, 0, .6)]) == 60
    assert ignition_threshold([row(30, 0, 0, .5)]) is None


def test_seed_split():
    assert SEEDS['calibration'] == tuple(range(10))
    assert SEEDS['test'] == tuple(range(10, 30))
    assert not set(SEEDS['quick']) & (set(SEEDS['calibration']) | set(SEEDS['test']))


def test_paired_se_is_across_seed_differences():
    trials = [{'condition': c, 'seed': s, 'metrics': {'P1': s + (2 if c == 'A' else 0)}} for s in SEEDS['test'] for c in ('zero', 'A')]
    assert contrast(trials, 'A', 'P1') == {'mean': 2., 'se': 0., 'n': 20, 'verdict': 'supported'}
    with pytest.raises(ValueError):
        contrast(trials[:-1], 'A', 'P1')
    assert stats([1, 3])['se'] == pytest.approx(1)


def test_batch_rates_match_independent_scalar_runs():
    import numpy as np
    from scipy.sparse import csr_matrix
    from flybench.experiment.male_decides import BatchRates
    from flybench.sim.fast_gpu import Simulator, Drive
    from flybench.sim.params import Parameters
    sim = Simulator(csr_matrix((2, 2)), device='cpu', params=Parameters(dt=.2), kernel='shiu',
                    drive=Drive((0, 1), 60), groups={'target': [0, 1]})
    expected = [sim.run(50, seed=s).counts for s in (10, 11)]
    sim.drive = Drive((0, 1), BatchRates([60, 60], 2))
    result = sim.run_batch(50, seeds=(10, 11))
    np.testing.assert_array_equal(result.counts, np.stack(expected, axis=1))
    np.testing.assert_array_equal(result.requested_hz, np.full((2, 2), 60))


@pytest.mark.skipif(os.environ.get('FLYBENCH_FAIL_PROBE') != '1', reason='Opt-in harness probe')
def test_harness_failure_probe():
    assert False, 'Deliberate failure must return exit 1'
