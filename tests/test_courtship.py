"""Courtship wiring, heterogeneous batch and decision oracles."""
import os
from dataclasses import fields
import numpy as np
import pytest
from scipy.sparse import csr_matrix
from flybench.experiment.courtship import BatchBrain, ColumnRates, sensory, emit, verdicts, CONDITIONS
from flybench.sim.fast_gpu import Simulator, Drive
from flybench.sim.params import Parameters
from flybench.song import Song
from flybench.world.arena import Arena, Observation
from flybench.world import constants as C


def test_mute_preserves_readout_and_amplitude():
    readings = {'pIP10': 100., C.PULSE_GROUP: 50., C.SINE_GROUP: 20.}
    live, a = emit(Song(), readings, False, 2.2)
    mute, b = emit(Song(), readings, True, 2.2)
    assert np.any(live != 0) and np.all(mute == 0)
    assert readings['pIP10'] == 100 and a['amplitude'] == b['amplitude'] == pytest.approx(.22)
    assert a['pulse_fraction'] == b['pulse_fraction'] == pytest.approx(5/7)


def test_observable_only_and_female_wiring():
    arena = Arena(4)
    obs = arena.observe(0)
    assert {f.name for f in fields(Observation)} == {'distance', 'bearing', 'other_speed', 'contact', 'sound'}
    male = sensory(obs, 'male', [])
    with pytest.raises(ValueError):
        sensory(obs, 'male', [], 50)
    assert 'vpoDN' not in str(male)
    assert male['chemical']['Or47b'] == pytest.approx(180/(1+(6/5)**2))
    for virgin, expected in ((True, 50), (False, 0)):
        female = sensory(obs, 'female', [], expected)
        assert female['chemical'] == {} and female['visual'] == {} and female['sag_hz'] == expected
        assert all(np.all(np.array(v) == 0) for v in female['auditory'].values())
    with pytest.raises((AttributeError, TypeError)):
        obs.vpoDN = 100


def test_column_adapter_matches_independent_streams_and_continuation():
    weights = csr_matrix(np.array([[0., 100.], [0., 0.]]))
    sim = Simulator(weights, device='cpu', params=Parameters(dt=.2), kernel='shiu', drive=Drive((0, 1), 0))
    state = sim.initial_batch_state((3, 7))
    batches = []
    for rates in (np.array([[5000., 0.], [0., 5000.]]), np.array([[123., 987.], [456., 321.]])):
        adapter = ColumnRates(rates)
        sim.drive = Drive((0, 1), adapter)
        result = sim.run_batch(5, state=state)
        assert adapter.calls == 2
        np.testing.assert_array_equal(result.requested_hz, rates)
        batches.append(result.counts.copy())
    for j, seed in enumerate((3, 7)):
        single = Simulator(weights, device='cpu', params=Parameters(dt=.2), kernel='shiu', drive=Drive((0, 1), 0))
        one = single.initial_batch_state((seed,))
        for i, rates in enumerate((np.array([[5000., 0.], [0., 5000.]]), np.array([[123., 987.], [456., 321.]]))):
            single.drive = Drive((0, 1), ColumnRates(rates[:, j:j+1]))
            result = single.run_batch(5, state=one)
            np.testing.assert_array_equal(result.counts[:, 0], batches[i][:, j])
        np.testing.assert_array_equal(one.v[:, 0].numpy(), state.v[:, j].numpy())
    assert batches[0][0, 0] == 25 and batches[0][0, 1] == 0


def fake():
    return [dict(condition=c, seed=s, pIP10=5., rms=1. if c.endswith('live') else 0.,
                 vpoDN=10. if c.startswith('virgin') else 0.) for c in CONDITIONS for s in range(10)]


def test_verdict_positive_zero_threshold_and_incomplete():
    data = fake()
    result = verdicts(data, True)
    assert result['C1']['verdict'] == result['C2']['verdict'] == 'supported'
    assert result['C3']['verdict'] == result['C4']['verdict'] == result['C5']['verdict'] == 'descriptive'
    assert verdicts(data, False)['C1']['verdict'] == 'unassessed'
    for t in data:
        t['rms'] = 0
        t['vpoDN'] = 0
    result = verdicts(data, True)
    assert result['C1']['verdict'] == result['C2']['verdict'] == 'not supported'
    with pytest.raises(ValueError):
        verdicts(data[:-1], True)


def test_verdict_seed_count_and_noisy_difference():
    data = fake()
    for t in data:
        if t['condition'] == 'mated_live' and t['seed'] < 3:
            t['pIP10'] = 0
        if t['condition'] == 'virgin_live':
            t['vpoDN'] = 100 if t['seed'] == 0 else 0
    result = verdicts(data, True)
    assert result['C1']['verdict'] == result['C2']['verdict'] == 'not supported'
    assert result['C1']['pIP10_positive_seeds']['mated_live'] == 7


def test_brain_world_inputs_and_hidden_state_isolation():
    from test_world import graph
    male = BatchBrain(graph(), 'male', device='cpu')
    female_graph = graph()
    female_graph['type'] = female_graph['type'].astype('U40')
    female_graph['type'][18] = 'DNp37'
    female_graph['type'][11] = 'AN_SMP_2'
    female = BatchBrain(female_graph, 'female', device='cpu')
    male.reset([0, 1]); female.reset([0, 1])
    arenas = [Arena(s) for s in (0, 1)]
    before = [sensory(a.observe(0), 'male', male.retina) for a in arenas]
    female.state.v[female.groups['vpoDN']] = 123
    after = [sensory(a.observe(0), 'male', male.retina) for a in arenas]
    assert before == after
    with pytest.raises(ValueError):
        male.reset([0, 1], sag_hz=50)
    readings, inputs, cells = male.run([a.observe(0) for a in arenas])
    assert male.state.step == 250 and female.state.step == 0
    assert any(r['pIP10'] > 0 for r in readings)
    for reading, cell in zip(readings, cells):
        assert reading['pIP10'] == np.mean(cell['pIP10'])
        wave, _ = emit(Song(), reading, True, 2.2)
        assert np.all(wave == 0)
    for virgin in (True, False):
        female.reset([0, 1], sag_hz=50 if virgin else 0)
        _, inputs, _ = female.run([a.observe(1) for a in arenas])
        assert all(i['sag_hz'] == (50 if virgin else 0) and not i['chemical'] and not i['visual'] for i in inputs)


@pytest.mark.skipif(os.environ.get('FLYBENCH_FAIL_PROBE') != '1', reason='Opt-in harness probe')
def test_harness_failure_probe():
    assert False, 'Deliberate failure must return exit 1'
