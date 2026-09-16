import importlib
import os

import numpy as np
import pytest

from flybench.relay_b1 import (Parameters, RelayB1, analytic_metrics, causal_checks,
    continuity_checks, joint_fit, release, sampled_metrics, step_voltage, target_gates)


def test_harness_failure_probe():
    intentional_failure = os.environ.get('E2_INTENTIONAL_FAILURE') == '1'
    assert not intentional_failure, 'Intentional harness failure'


@pytest.mark.skipif(os.environ.get('EAR_V2_E2_GUARDS') != '1', reason='requires the lane-time import/file guards; opt-in')
@pytest.mark.parametrize('name', ['graph', 'dictionary', 'world', 'experiment'])
def test_forbidden_imports_fail_closed(name):
    with pytest.raises((ImportError, ValueError), match='E2 forbidden'):
        importlib.import_module('flybench.'+name)


@pytest.mark.skipif(os.environ.get('EAR_V2_E2_GUARDS') != '1', reason='requires the lane-time import/file guards; opt-in')
@pytest.mark.parametrize('suffix', ['npz','parquet','feather'])
def test_graph_file_reads_fail_closed(suffix):
    with pytest.raises((ImportError, ValueError), match='E2 forbidden'):
        open('build/records-raw/ear_v2_e2_forbidden_probe.'+suffix, 'rb')


def test_causality_and_chunks():
    result = causal_checks(Parameters(d_ms=1.537))
    assert result['prefix_bit_equal']
    assert max(result['chunk_max_errors']) < 1e-9


def test_wt_only_rejected():
    with pytest.raises(ValueError, match='Joint'):
        joint_fit(conditions=('WT',))
    with pytest.raises(ValueError, match='Joint'):
        joint_fit(targets={'H1':1.96})


def test_known_step_oracle_and_four_condition_ratios():
    p = Parameters(g_gap=.74, g_chem=.26, beta=.78, d_ms=1.5)
    metrics, traces = sampled_metrics(p)
    times = np.arange(len(traces['WT']))*.02-10
    for condition, v in traces.items():
        np.testing.assert_allclose(v, step_voltage(times,p,condition), atol=1e-12)
    assert abs(metrics['H3']-.7972)<1e-12
    assert abs(metrics['H4']-.22)<1e-12
    assert abs(metrics['H1']-analytic_metrics(p)['H1'])<.001


def test_equal_time_constant_solution():
    p = Parameters(g_gap=1, tau_m_ms=3, tau_syn_ms=1.5, d_ms=0)
    t = np.arange(1000)*.02
    v = RelayB1(p).process(np.ones(len(t)))['V_B1']
    np.testing.assert_allclose(v,step_voltage(t,p),atol=1e-12)


def test_gate_oracles_reject_named_violations():
    assert all(target_gates({'H1':1.96,'H3':.8,'H4':.22}).values())
    for key, bad, gate in [('H1',2.5,'E2-G2'),('H3',.5,'E2-G3'),('H4',0,'E2-G4')]:
        m = {'H1':1.96,'H3':.8,'H4':.22}
        m[key] = bad
        assert not target_gates(m)[gate]


def test_continuity_no_reset_jump():
    assert continuity_checks(Parameters())['passed']


def test_release_and_e1_adapter():
    np.testing.assert_array_equal(release(np.array([-1,0,2])),[0,0,2])
    x = np.vstack((np.zeros(200), np.ones(200)))
    a = RelayB1().process(r_graded=x,channel=1)
    b = RelayB1().process(x[1])
    np.testing.assert_array_equal(a['V_B1'], b['V_B1'])
    np.testing.assert_array_equal(a['release'],release(a['V_B1']))
    with pytest.raises(ValueError):
        RelayB1().process(r_graded=x)


@pytest.mark.parametrize('x', [[float('nan')], [float('inf')], [[1,2]]])
def test_invalid_input(x):
    with pytest.raises(ValueError):
        RelayB1().process(x)


def test_invalid_parameters_and_empty_state():
    with pytest.raises(ValueError):
        Parameters(beta=1.01)
    with pytest.raises(ValueError):
        Parameters(tau_m_ms=0)
    with pytest.raises(ValueError):
        RelayB1(dt_ms=0)
    m = RelayB1()
    assert len(m.process([])['V_B1']) == 0
    np.testing.assert_array_equal(m.process([1,2])['V_B1'], RelayB1().process([1,2])['V_B1'])
