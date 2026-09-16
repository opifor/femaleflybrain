"""Synthetic graded-release acceptance tests and reproducible parity report."""
import json
import os
import subprocess
import sys
import types

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from flybench.sim.lif import Drive, Simulator as Reference
from flybench.sim.fast import Simulator as Fast
from flybench.sim.params import Parameters
from flybench.sim.release import GradedRelease, zero_source_rows


BACKENDS = ("lif", "fast", "fast_gpu")


def simulator(backend, weights, **kwargs):
    if backend == "lif":
        return Reference(weights, **kwargs)
    if backend == "fast":
        return Fast(weights, **kwargs)
    import torch
    from flybench.sim.fast_gpu import Simulator
    if not torch.cuda.is_available():
        pytest.skip("CUDA required for release parity")
    torch.set_num_threads(1)
    return Simulator(weights, device="cuda", **kwargs)


def array(value):
    return value.detach().cpu().numpy() if hasattr(value, "detach") else np.asarray(value)


def graph_and_flux():
    weights = np.array([[0, 120, -35, 25], [0, 0, 8, 0],
                        [0, 0, 0, -4], [12, 0, 7, 0]], dtype=float)
    step = np.arange(800)
    flux = (0.7 + 0.5 * np.sin(step * 0.071) + 0.15 * (step % 37 == 0))[:, None]
    return csr_matrix(weights), flux


def make_release_sim(backend):
    weights, flux = graph_and_flux()
    return simulator(backend, weights, release=GradedRelease([0], flux))


def run_chunks(sim, chunk, seed=11):
    state = None
    logs = []
    counts = np.zeros(sim.n, dtype=np.int64)
    remaining = len(sim.release.flux)
    while remaining:
        length = min(chunk, remaining)
        result = sim.run(length * sim.params.dt, state=state, seed=seed, spike_log=True)
        state = result.state
        logs.extend(result.spikes)
        counts += result.counts
        remaining -= length
    return result, logs, counts


@pytest.mark.parametrize("backend", BACKENDS)
def test_rows_and_scaled_check(backend):
    weights, flux = graph_and_flux()
    before = weights.copy()
    zeroed, original = zero_source_rows(weights, np.array([0]))
    np.testing.assert_array_equal(original.toarray(), before.toarray()[[0]])
    np.testing.assert_array_equal(zeroed.toarray()[1:], before.toarray()[1:])
    np.testing.assert_array_equal(zeroed.toarray()[:, 0], before.toarray()[:, 0])
    assert zeroed.getrow(0).nnz == 0
    np.testing.assert_array_equal(weights.toarray(), before.toarray())
    sim = simulator(backend, weights, release=GradedRelease([0], flux))
    assert sim.release.counts[0] == 0
    assert not np.any(sim.weights.getrow(0).data)
    np.testing.assert_array_equal(sim.release.scaled_source_counts, [0])
    with pytest.raises(ValueError, match="Scaled"):
        sim.release.verify_scaled(np.array([0]), np.array([1.0]))


def test_non_source_storage_preserved():
    # Preserve explicit zeros and ordering in rows not selected for removal.
    weights = csr_matrix((np.array([5., 0., 3.]), np.array([1, 1, 0]),
                          np.array([0, 1, 3])), shape=(2, 2))
    zeroed, original = zero_source_rows(weights, np.array([0]))
    np.testing.assert_array_equal(zeroed.data, [0, 3])
    np.testing.assert_array_equal(zeroed.indices, [1, 0])
    np.testing.assert_array_equal(zeroed.indptr, [0, 0, 2])
    np.testing.assert_array_equal(original.data, [5])


def baseline_classes():
    """Load the sealed pre-hook sources in memory; git remains read-only."""
    modules = {}
    for name in ("lif", "fast", "fast_gpu"):
        source = subprocess.run(
            ["git", "show", f"002da1d:flybench/sim/{name}.py"],
            capture_output=True, check=True, encoding="utf-8").stdout
        source = source.replace("from .lif import", "from ._release_baseline_lif import")
        source = source.replace("from .fast import", "from ._release_baseline_fast import")
        fullname = f"flybench.sim._release_baseline_{name}"
        module = types.ModuleType(fullname)
        module.__package__ = "flybench.sim"
        sys.modules[fullname] = module
        exec(compile(source, f"<baseline-{name}>", "exec"), module.__dict__)
        modules[name] = module.Simulator
    return modules


@pytest.fixture(scope="module")
def baselines():
    return baseline_classes()


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("kernel", ("shiu", "jump"))
@pytest.mark.parametrize("mode", ("poisson", "bernoulli"))
def test_disabled_bit_equal(backend, kernel, mode, baselines):
    rng = np.random.default_rng(274)
    weights = rng.integers(-40, 180, (12, 12)) * (rng.random((12, 12)) < 0.3)
    kwargs = dict(kernel=kernel, drive=Drive((0, 1, 2), 500, mode))
    a = simulator(backend, weights, **kwargs).run(30, seed=41, spike_log=True)
    b = simulator(backend, weights, release=None, **kwargs).run(30, seed=41, spike_log=True)
    old_kwargs = dict(kwargs)
    if backend == "fast_gpu":
        old_kwargs["device"] = "cuda"
    old = baselines[backend](weights, **old_kwargs).run(30, seed=41, spike_log=True)
    assert a.spikes and a.spikes == b.spikes == old.spikes
    for field in ("counts", "sampled_drive_hz", "delivered_hz"):
        np.testing.assert_array_equal(getattr(a, field), getattr(b, field))
        np.testing.assert_array_equal(getattr(a, field), getattr(old, field))
    for field in ("v", "g", "refr", "delay_buffer"):
        np.testing.assert_array_equal(array(getattr(a.state, field)), array(getattr(b.state, field)))
        np.testing.assert_array_equal(array(getattr(a.state, field)), array(getattr(old.state, field)))


@pytest.mark.parametrize("backend", BACKENDS)
def test_constant_flux_analytic(backend):
    errors = []
    for dt in (0.2, 0.1):
        p = Parameters(dt=dt)
        steps = round(20 / dt)
        sim = simulator(backend, [[0, 2], [0, 0]], params=p,
                        release=GradedRelease([0], np.full((steps, 1), 0.3)))
        result = sim.run(20, spike_log=True)
        assert result.spikes == []
        arrivals = steps - sim.delay_steps
        q = 2 * p.w_syn * 0.3
        continuous = q * p.tau_s * (1 - np.exp(-arrivals * dt / p.tau_s))
        discrete = q * dt * (1 - sim.es ** arrivals) / (1 - sim.es)
        actual = array(result.state.g)[1]
        numerical = 2e-6 if backend == "fast_gpu" else 1e-12
        assert abs(actual - discrete) < numerical
        bound = continuous * ((dt / p.tau_s) / (1 - sim.es) - 1)
        assert abs(actual - continuous) <= bound + numerical
        errors.append(abs(actual - continuous))
    assert errors[1] < 0.51 * errors[0]


@pytest.mark.parametrize("backend", BACKENDS)
@pytest.mark.parametrize("chunk", (50, 256))
def test_continuation(backend, chunk):
    sim = make_release_sim(backend)
    full, logs, counts = run_chunks(sim, 800)
    split, split_logs, split_counts = run_chunks(sim, chunk)
    assert logs and logs == split_logs
    np.testing.assert_array_equal(counts, split_counts)
    for field in ("v", "g", "refr", "delay_buffer", "release_pending", "dropped_flux"):
        np.testing.assert_array_equal(array(getattr(full.state, field)), array(getattr(split.state, field)))


@pytest.mark.parametrize("backend", BACKENDS)
def test_offset_mutant_is_detected(backend, monkeypatch):
    expected, _, _ = run_chunks(make_release_sim(backend), 800)
    sim = make_release_sim(backend)
    original = sim.release.enqueue
    def local_offset(state, active, destination, dt, w_syn):
        absolute = state.step
        state.step %= 50
        try:
            return original(state, active, destination, dt, w_syn)
        finally:
            state.step = absolute
    monkeypatch.setattr(sim.release, "enqueue", local_offset)
    mutant, _, _ = run_chunks(sim, 50)
    with pytest.raises(AssertionError):
        np.testing.assert_allclose(array(mutant.state.g), array(expected.state.g), rtol=0, atol=1e-4)


@pytest.mark.parametrize("backend", BACKENDS)
def test_refractory_drop(backend):
    # The target fires at step 0 and is refractory at steps 18..21 when release arrives.
    sim = simulator(backend, [[0, 2], [0, 0]],
                    release=GradedRelease([0], np.full((23, 1), 0.5)))
    state = sim.initial_state()
    state.v[1] = -40
    result = sim.run(2.3, state=state, spike_log=True)
    assert result.spikes == [(0.0, 1)]
    np.testing.assert_allclose(result.dropped_flux, [0, 0.4], rtol=0, atol=1e-15)
    assert abs(array(result.state.g)[1] - 0.0275) < 1e-8


@pytest.mark.parametrize("backend", BACKENDS)
def test_signed_cancellation_still_counts_drops(backend):
    sim = simulator(backend, [[0, 0, 2], [0, 0, -2], [0, 0, 0]],
                    release=GradedRelease([0, 1], np.full((23, 2), 0.5)))
    state = sim.initial_state()
    state.v[2] = -40
    head = sim.run(2, state=state, spike_log=True)
    snapshot = head.dropped_flux.copy()
    tail = sim.run(0.3, state=head.state, spike_log=True)
    np.testing.assert_allclose(head.dropped_flux, [0, 0, 0.4], atol=1e-15, rtol=0)
    np.testing.assert_array_equal(head.dropped_flux, snapshot)
    np.testing.assert_allclose(tail.dropped_flux, [0, 0, 0.8], atol=1e-15, rtol=0)
    assert array(tail.state.g)[2] == 0


@pytest.mark.parametrize("backend", BACKENDS)
def test_source_spike_has_no_network_output(backend):
    sim = simulator(backend, [[0, 100], [1, 0]],
                    release=GradedRelease([0], np.zeros((30, 1))))
    state = sim.initial_state()
    state.v[0] = -40
    result = sim.run(3, state=state, spike_log=True)
    assert result.spikes == [(0.0, 0)]
    assert result.counts[0] == 1  # Spike statistics remain ordinary LIF statistics.
    assert array(result.state.g)[1] == 0
    assert array(result.state.v)[1] == sim.params.v_rest
    assert sim.weights[1, 0] == 1


@pytest.mark.parametrize("backend", BACKENDS)
def test_rng_independence(backend):
    sim = make_release_sim(backend)
    a, logs_a, counts_a = run_chunks(sim, 800, seed=1)
    b, logs_b, counts_b = run_chunks(sim, 800, seed=98765)
    assert logs_a == logs_b
    np.testing.assert_array_equal(counts_a, counts_b)
    np.testing.assert_array_equal(array(a.state.g), array(b.state.g))
    if backend == "fast_gpu":
        import torch
        assert torch.equal(a.state.rng.generator.get_state(), sim.initial_state(1).rng.generator.get_state())
    else:
        assert a.state.rng.bit_generator.state == sim.initial_state(1).rng.bit_generator.state


@pytest.mark.parametrize("backend", BACKENDS)
def test_jump_and_absolute_coverage(backend):
    release = GradedRelease([0], [[1], [2]])
    with pytest.raises(ValueError, match="shiu"):
        simulator(backend, [[0, 1], [0, 0]], kernel="jump", release=release)
    sim = simulator(backend, [[0, 1], [0, 0]], release=release)
    state = sim.initial_state()
    state.step = 2
    before = array(state.v).copy()
    with pytest.raises(ValueError, match="absolute"):
        sim.run(0.1, state=state)
    np.testing.assert_array_equal(array(state.v), before)


@pytest.mark.parametrize("rows,flux", [([0.5], [[1]]), ([0, 0], [[1, 1]]),
    ([-1], [[1]]), ([0], [[-1]]), ([0], [[np.nan]]), ([0], [1]), ([0], [[1, 2]])])
def test_invalid_release(rows, flux):
    with pytest.raises(ValueError):
        GradedRelease(rows, flux)


def test_harness_failure_probe():
    assert os.environ.get("RELEASE_HOOK_FAILURE_PROBE") != "1", "Intentional harness failure"


def measure():
    measurements = {}
    traces = {}
    for backend in BACKENDS:
        sim = make_release_sim(backend)
        state = None
        trace = []
        spikes = []
        for _ in range(800):
            result = sim.run(0.1, state=state, spike_log=True)
            state = result.state
            trace.append(array(state.g).copy())
            spikes.extend(result.spikes)
        traces[backend] = (np.array(trace), spikes)
        full, full_logs, _ = run_chunks(sim, 800)
        chunk_metrics = {}
        for chunk in (50, 256):
            split, split_logs, _ = run_chunks(sim, chunk)
            assert split_logs == full_logs
            chunk_metrics[str(chunk)] = {
                field: float(np.max(np.abs(array(getattr(full.state, field)) - array(getattr(split.state, field)))))
                for field in ("g", "v", "delay_buffer", "dropped_flux")}
            chunk_metrics[str(chunk)]["spike_time_ms"] = 0.0
        measurements[backend] = dict(chunks=chunk_metrics, spikes=len(spikes),
            dropped_flux=result.dropped_flux.tolist(),
            source_counts=sim.release.counts[sim.release.source_rows].tolist(),
            scaled_source_counts=sim.release.scaled_source_counts.tolist())
    ref_g, ref_spikes = traces["lif"]
    for backend in BACKENDS:
        g, spikes = traces[backend]
        assert [i for _, i in spikes] == [i for _, i in ref_spikes]
        measurements[backend]["max_g_difference"] = float(np.max(np.abs(g - ref_g)))
        measurements[backend]["max_spike_time_difference_ms"] = max(
            (abs(t - r) for (t, _), (r, _) in zip(spikes, ref_spikes)), default=0.0)
    return measurements


def test_three_backend_trajectory_parity():
    metrics = measure()
    assert metrics["fast"]["max_g_difference"] < 1e-10
    assert metrics["fast_gpu"]["max_g_difference"] < 1e-4
    for backend in BACKENDS:
        assert metrics[backend]["spikes"] > 0
        assert metrics[backend]["max_spike_time_difference_ms"] == 0


def test_gpu_batch_release():
    sim = make_release_sim("fast_gpu")
    full = sim.run_batch(80, seeds=(1, 9), spike_log=True)
    first = sim.run_batch(5, seeds=(1, 9), spike_log=True)
    tail = sim.run_batch(75, state=first.state, spike_log=True)
    single = sim.run(80, seed=1, spike_log=True)
    for column in range(2):
        assert full.spikes[column] == first.spikes[column] + tail.spikes[column]
        assert full.spikes[column] == single.spikes
        np.testing.assert_array_equal(array(full.state.g)[:, column], array(single.state.g))
        np.testing.assert_array_equal(full.dropped_flux[:, column], single.dropped_flux)
    np.testing.assert_array_equal(array(full.state.g), array(tail.state.g))
    np.testing.assert_array_equal(full.dropped_flux, tail.dropped_flux)


if __name__ == "__main__":
    print(json.dumps(measure(), indent=2))
