import os
import math
import numpy as np
import pytest
from scipy.sparse import csr_matrix
from flybench.sim import Parameters, Drive, Simulator


@pytest.mark.parametrize("dt", [0.1, 0.2])
def test_a_single_synapse(dt):
    p = Parameters(dt=dt)
    net = Simulator(csr_matrix([[0, 1], [0, 0]]), params=p)
    state = net.initial_state()
    state.v[0] = -40
    values = []
    times = []
    for _ in range(round(30 / dt)):
        net.run(dt, state=state)
        values.append(state.v[1] - p.v_rest)
        times.append((state.step - 1) * dt)
    peak_index = int(np.argmax(values))
    t = p.tau_m * p.tau_s / (p.tau_m - p.tau_s) * math.log(p.tau_m / p.tau_s)
    analytic = p.w_syn * p.tau_s / (p.tau_m - p.tau_s) * (math.exp(-t / p.tau_m) - math.exp(-t / p.tau_s))
    print(f"dt={dt}: peak={values[peak_index]:.9f} mV at {times[peak_index]:.3f} ms; analytic={analytic:.9f} mV at {t+p.delay:.6f} ms")
    assert values[peak_index] == pytest.approx(analytic, rel=0.03)
    assert times[peak_index] == pytest.approx(t + p.delay, rel=0.03)
    assert np.all(np.asarray(values)[np.asarray(times) <= p.delay] == 0)
    jump = Simulator(csr_matrix([[0, 1], [0, 0]]), kernel="jump", params=p)
    state = jump.initial_state()
    state.v[0] = -40
    jump.run(dt, state=state)
    assert state.v[1] - p.v_rest == pytest.approx(0.275)
    assert np.all(state.g == 0)


@pytest.mark.parametrize("dt", [0.1, 0.2])
def test_b_refractory(dt):
    net = Simulator(csr_matrix((1, 1)), params=Parameters(dt=dt),
                    drive=Drive((0,), 1000 / dt, "bernoulli"))
    result = net.run(30, spike_log=True)
    intervals = np.diff([t for t, _ in result.spikes])
    assert len(intervals) >= 10
    assert np.all(intervals >= 2.2 - 1e-12)
    assert intervals == pytest.approx(np.full(len(intervals), 2.2))


def test_b_frozen_state_and_arrivals():
    net = Simulator(csr_matrix((1, 1)))
    state = net.initial_state()
    state.v[0], state.g[0], state.refr[0] = -50, 2, 22
    state.delay_buffer[0, 0] = 10
    net.run(2.2, state=state)
    assert state.v[0] == -50
    assert state.g[0] == 2
    net.run(0.1, state=state)
    assert state.g[0] < 2


@pytest.mark.parametrize("kernel", ["shiu", "jump"])
@pytest.mark.parametrize("mode", ["poisson", "bernoulli"])
def test_c_continuation(kernel, mode):
    net = Simulator(csr_matrix([[0, 400], [-10, 0]]), kernel=kernel,
                    drive=Drive((0,), 800, mode), groups={"all": (0, 1)})
    full = net.run(100, seed=29, spike_log=True)
    first = net.run(50, seed=29, spike_log=True)
    first_log = list(first.spikes)
    second = net.run(50, state=first.state, spike_log=True)
    assert full.spikes and any(i == 1 for _, i in full.spikes)
    assert full.spikes == first_log + second.spikes
    for field in ("v", "g", "refr", "delay_buffer"):
        np.testing.assert_array_equal(getattr(full.state, field), getattr(second.state, field))
    assert full.state.cursor == second.state.cursor
    assert full.state.rng.bit_generator.state == second.state.rng.bit_generator.state
    np.testing.assert_array_equal(full.counts, first.counts + second.counts)
    np.testing.assert_allclose(full.delivered_hz, (first.delivered_hz + second.delivered_hz) / 2)
    assert full.group_counts["all"] == full.counts.sum()
    assert full.group_rates_hz["all"] == full.total_hz_per_neuron


@pytest.mark.parametrize("device", ["cpu", "cuda"])
@pytest.mark.parametrize("kernel", ["shiu", "jump"])
def test_d_torch_parity(device, kernel):
    torch = pytest.importorskip("torch")
    if device == "cuda" and not torch.cuda.is_available():
        pytest.skip("CUDA unavailable")
    from flybench.sim.lif_gpu import Simulator as TorchSimulator
    rng = np.random.default_rng(48)
    weights = rng.integers(-30, 250, (8, 8)) * (rng.random((8, 8)) < 0.3)
    options = dict(kernel=kernel, drive=Drive((0, 2), 400), groups={"pair": (1, 3)})
    cpu = Simulator(csr_matrix(weights), **options)
    gpu = TorchSimulator(csr_matrix(weights), device=device, **options)
    batch = gpu.run_batch(20, seeds=[7, 11], spike_log=True)
    for seed, actual in zip([7, 11], batch):
        expected = cpu.run(20, seed=seed, spike_log=True)
        assert actual.spikes == expected.spikes
        np.testing.assert_array_equal(actual.counts, expected.counts)
        np.testing.assert_array_equal(actual.delivered_hz, expected.delivered_hz)
        for field in ("v", "g", "delay_buffer", "refr"):
            np.testing.assert_allclose(getattr(actual.state, field).cpu().numpy(), getattr(expected.state, field), atol=1e-11, rtol=0)
    split = gpu.run(10, seed=7, spike_log=True)
    tail = gpu.run_batch(10, states=[split.state], spike_log=True)[0]
    assert batch[0].spikes == split.spikes + tail.spikes


@pytest.mark.parametrize("dt", [0.1, 0.2])
def test_e_poisson_rate(dt):
    net = Simulator(csr_matrix((4, 4)), params=Parameters(dt=dt),
                    drive=Drive((0, 1, 2, 3), 150))
    result = net.run(20000, seed=72)
    assert result.requested_hz == pytest.approx(np.full(4, 150))
    assert result.delivered_hz == pytest.approx(np.full(4, 150), rel=0.1)
    np.testing.assert_array_equal(result.rates_hz, result.delivered_hz)
    np.testing.assert_array_equal(result.sampled_drive_hz, result.delivered_hz)
    assert np.all(result.state.refr == 0)


@pytest.mark.parametrize("kernel", ["shiu", "jump"])
def test_f_inhibitory(kernel):
    net = Simulator(csr_matrix([[0, -1], [0, 0]]), kernel=kernel)
    state = net.initial_state()
    state.v[0] = -40
    net.run(3, state=state)
    assert state.v[1] < -52.01


def test_validation():
    with pytest.raises(ValueError):
        Parameters(dt=0.3)
    with pytest.raises(ValueError):
        Simulator(csr_matrix((2, 3)))
    with pytest.raises(ValueError):
        Simulator(csr_matrix((2, 2)), drive=Drive((0,), 20000))
    net = Simulator(csr_matrix((1, 1)))
    with pytest.raises(ValueError):
        net.run(0.15)


@pytest.mark.skipif(os.environ.get("FLYBENCH_FAIL_PROBE") != "1", reason="Opt-in harness failure probe")
def test_harness_failure_probe():
    pytest.fail("Intentional harness failure")
