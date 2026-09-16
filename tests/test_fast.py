"""Parity, event scheduling, independent trial columns and failure propagation."""
import os

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from flybench.sim.fast import Drive, Simulator
from flybench.sim.lif import Simulator as Reference
from flybench.sim.params import Parameters


def random_graph():
    rng = np.random.default_rng(48)
    weights = rng.integers(-30, 250, (200, 200))
    weights *= rng.random((200, 200)) < 0.05
    return csr_matrix(weights)


@pytest.mark.parametrize("kernel", ["shiu", "jump"])
@pytest.mark.parametrize("mode", ["poisson", "bernoulli"])
def test_cpu_reference(kernel, mode):
    options = dict(kernel=kernel, drive=Drive(tuple(range(20)), 400, mode),
                   groups={"driven": tuple(range(20)), "empty": ()})
    expected = Reference(random_graph(), **options).run(100, seed=29, spike_log=True)
    actual = Simulator(random_graph(), **options).run(100, seed=29, spike_log=True)
    assert len(expected.spikes) > 200
    assert any(i >= 20 for _, i in expected.spikes)
    assert actual.spikes == expected.spikes
    for field in ("counts", "requested_hz", "sampled_drive_hz", "delivered_hz"):
        np.testing.assert_array_equal(getattr(actual, field), getattr(expected, field))
    assert actual.group_counts == expected.group_counts
    assert actual.group_rates_hz == expected.group_rates_hz
    for field in ("v", "g", "delay_buffer"):
        np.testing.assert_allclose(getattr(actual.state, field), getattr(expected.state, field), atol=1e-10, rtol=0)
    print(f"CPU {kernel}/{mode}: {len(actual.spikes)} spikes, exact timestamps")


@pytest.mark.parametrize("kernel", ["shiu", "jump"])
@pytest.mark.parametrize("mode", ["poisson", "bernoulli"])
def test_cpu_continuation(kernel, mode):
    sim = Simulator(random_graph(), kernel=kernel, drive=Drive(tuple(range(20)), 400, mode))
    full = sim.run(100, seed=71, spike_log=True)
    head = sim.run(37.1, seed=71, spike_log=True)
    tail = sim.run(62.9, state=head.state, spike_log=True)
    assert full.spikes == head.spikes + tail.spikes
    np.testing.assert_array_equal(full.counts, head.counts + tail.counts)
    for field in ("v", "g", "refr", "delay_buffer"):
        np.testing.assert_array_equal(getattr(full.state, field), getattr(tail.state, field))
    assert full.state.rng.bit_generator.state == tail.state.rng.bit_generator.state


def torch_sim(device, *args, **kwargs):
    torch = pytest.importorskip("torch")
    if device == "cuda" and not torch.cuda.is_available():
        pytest.skip("CUDA unavailable")
    from flybench.sim.fast_gpu import Simulator as TorchSimulator
    return TorchSimulator(*args, device=device, **kwargs)


@pytest.mark.parametrize("device", ["cpu", "cuda"])
@pytest.mark.parametrize("kernel", ["shiu", "jump"])
@pytest.mark.parametrize("mode", ["poisson", "bernoulli"])
def test_torch_parity_and_batch(device, kernel, mode):
    torch = pytest.importorskip("torch")
    torch.set_num_threads(1)
    options = dict(kernel=kernel, drive=Drive(tuple(range(20)), 400, mode),
                   groups={"driven": tuple(range(20)), "empty": ()})
    cpu = Simulator(random_graph(), rng="torch", **options)
    gpu = torch_sim(device, random_graph(), **options)
    seeds = [7, 11, 7]
    batch = gpu.run_batch(100, seeds=seeds, spike_log=True)
    assert batch.state.v.shape == (200, 3)
    assert batch.state.g.shape == (200, 3)
    assert batch.state.delay_buffer.shape == (19, 200, 3)
    assert batch.spikes[0] == batch.spikes[2]
    assert batch.spikes[0] != batch.spikes[1]
    for column, seed in enumerate(seeds[:2]):
        expected = cpu.run(100, seed=seed, spike_log=True)
        single = gpu.run(100, seed=seed, spike_log=True)
        actual_log = batch.spikes[column]
        difference = abs(len(actual_log) - len(expected.spikes)) / len(expected.spikes)
        assert difference <= 0.01
        assert [(t, i) for t, i in actual_log if t < 50] == [
            (t, i) for t, i in expected.spikes if t < 50]
        assert actual_log == single.spikes
        np.testing.assert_array_equal(batch.counts[:, column], single.counts)
        for field in ("requested_hz", "sampled_drive_hz", "delivered_hz"):
            np.testing.assert_array_equal(getattr(batch, field)[:, column], getattr(expected, field))
        assert batch.group_counts["driven"][column] == single.group_counts["driven"]
        assert batch.group_rates_hz["empty"][column] == 0
        print(f"{device} {kernel}/{mode} seed={seed}: CPU={len(expected.spikes)} Torch={len(actual_log)} delta={difference:.6%}; first 50 ms exact")
    head = gpu.run_batch(37.1, seeds=seeds, spike_log=True)
    tail = gpu.run_batch(62.9, state=head.state, spike_log=True)
    for column in range(3):
        assert batch.spikes[column] == head.spikes[column] + tail.spikes[column]
    for field in ("v", "g", "refr", "delay_buffer"):
        torch.testing.assert_close(getattr(batch.state, field), getattr(tail.state, field), rtol=0, atol=0)
    for a, b in zip(batch.state.rng, tail.state.rng):
        assert torch.equal(a.generator.get_state(), b.generator.get_state())
    first = gpu.run(37.1, seed=7, spike_log=True)
    second = gpu.run(62.9, state=first.state, spike_log=True)
    assert batch.spikes[0] == first.spikes + second.spikes


@pytest.mark.parametrize("backend", ["numpy", "cpu", "cuda"])
@pytest.mark.parametrize("kernel", ["shiu", "jump"])
@pytest.mark.parametrize("dt", [0.1, 0.2])
def test_scheduling(backend, kernel, dt):
    def make(weights, **kwargs):
        opts = dict(params=Parameters(dt=dt), kernel=kernel, **kwargs)
        return Simulator(csr_matrix(weights), **opts) if backend == "numpy" else torch_sim(backend, csr_matrix(weights), **opts)

    sim = make([[0, 1], [0, 0]])
    state = sim.initial_state()
    state.v[0] = -40
    sim.run(dt, state=state)
    if kernel == "jump":
        assert float(state.v[1]) == pytest.approx(-52 + 0.275, abs=1e-5)
    else:
        sim.run(1.8 - dt, state=state)
        assert float(state.g[1]) == 0
        assert float(state.v[1]) == -52
        sim.run(dt, state=state)
        assert float(state.g[1]) == pytest.approx(0.275)
        assert float(state.v[1]) == -52
        sim.run(dt, state=state)
        assert float(state.v[1]) > -52
    frozen = sim.initial_state()
    frozen.v[0] = -40
    frozen.v[1], frozen.g[1], frozen.refr[1] = -50, 2, round(4 / dt)
    frozen.delay_buffer[0, 1] = 10
    sim.run(4, state=frozen)
    assert float(frozen.v[1]) == -50
    assert float(frozen.g[1]) == 2
    sim.run(dt, state=frozen)
    assert float(frozen.g[1]) < 2
    negative = make([[0, -1], [0, 0]])
    state = negative.initial_state()
    state.v[0] = -40
    negative.run(3, state=state)
    assert float(state.v[1]) < -52.01
    driven = make([[0]], drive=Drive((0,), 1000 / dt, "bernoulli"))
    spikes = driven.run(30, spike_log=True).spikes
    np.testing.assert_allclose(np.diff([t for t, _ in spikes]), 2.2, atol=1e-12)
    assert len(spikes) == 14


@pytest.mark.parametrize("backend", ["numpy", "cpu", "cuda"])
def test_validation_and_poisson(backend):
    make = Simulator if backend == "numpy" else lambda w, **kw: torch_sim(backend, w, **kw)
    sim = make(csr_matrix((2, 2)), drive=Drive((0,), 10000))
    result = sim.run(1, seed=7)
    np.testing.assert_array_equal(result.counts, [10, 0])
    np.testing.assert_array_equal(result.requested_hz, result.sampled_drive_hz)
    np.testing.assert_array_equal(result.delivered_hz, result.sampled_drive_hz)
    assert float(result.state.refr[0]) == 0
    other = make(csr_matrix((2, 2)))
    for duration in (0, -1, 0.15, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            sim.run(duration)
    with pytest.raises(ValueError):
        other.run(1, state=result.state)
    for weights, options in ((csr_matrix((2, 3)), {}), (csr_matrix([[np.nan]]), {}),
                             (csr_matrix((2, 2)), {"drive": Drive((2,), 100)}),
                             (csr_matrix((2, 2)), {"drive": Drive((0, 0), 100)})):
        with pytest.raises(ValueError):
            make(weights, **options)


@pytest.mark.skipif(os.environ.get("FLYBENCH_FAIL_PROBE") != "1", reason="Opt-in harness failure probe")
def test_harness_failure_probe():
    pytest.fail("Intentional harness failure")
