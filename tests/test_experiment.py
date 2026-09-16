import copy
import hashlib
import os
from pathlib import Path
import numpy as np
import pytest
from scipy.sparse import csr_matrix
from flybench.experiment.protocol import Protocol
from flybench.experiment.runner import run
from flybench.experiment.record import validate, write
from flybench.experiment.report import render, contrast, write_from_json
from flybench.experiment.runner import BatchRates
from flybench.sim.fast_gpu import Simulator, Drive
from flybench.sim.params import Parameters
import torch


@pytest.fixture(scope="module")
def result():
    weights = csr_matrix(np.array([[0, 0, 0, 1000, 0], [0, 0, 0, 0, 1000],
                                   [0, 0, 0, 2000, 3000], [0, 0, 0, 0, 1000], [0, 0, 0, 0, 0]]))
    graph = {"body_id": np.arange(5), "data": weights.data, "indices": weights.indices,
             "indptr": weights.indptr, "meta": {}}
    groups = {k: np.array([i]) for i, k in enumerate(("JO-A", "JO-B", "SAG", "pC1", "vpoDN"))}
    return run(Protocol.read(quick=True), graph, groups, device="cpu")


def test_paired_seeds_schema_and_drive(result):
    assert validate(result) is result
    for kernel in ("shiu", "jump"):
        for condition in result["protocol"]["conditions"]:
            assert [t["seed"] for t in result["trials"] if t["kernel"] == kernel and t["condition"] == condition] == [0, 1]
    lookup = {(t["kernel"], t["condition"], t["seed"]): t for t in result["trials"]}
    for seed in (0, 1):
        a = lookup["shiu", "virgin_song", seed]
        b = lookup["shiu", "virgin_silence", seed]
        # Identical SAG random draws despite changed auditory rates.
        assert [s["sampled_hz"]["SAG"] for w in a["windows"] for s in w["drive_slices"]] == [s["sampled_hz"]["SAG"] for w in b["windows"] for s in w["drive_slices"]]
        silent = lookup["shiu", "mated_silence", seed]
        assert silent["rates_hz"] == {"vpoDN": 0, "pC1": 0, "network": 0}
        assert all(s["requested_hz"] == {"JO-A": 0, "JO-B": 0, "SAG": 0} for w in silent["windows"] for s in w["drive_slices"])
        for t in (a, b):
            for g in t["rates_hz"]:
                assert t["rates_hz"][g] == np.mean([w["rates_hz"][g] for w in t["windows"]][4:])
    broken = copy.deepcopy(result)
    broken["trials"].pop()
    with pytest.raises(ValueError):
        validate(broken)


def test_report_verbatim_json_and_verdict(result, tmp_path):
    report = render(result)
    raw = Path("experiments/female_no_v1.md").read_bytes()
    assert raw.decode("utf-8") in report
    assert result["protocol"]["sha256"] == hashlib.sha256(raw).hexdigest()
    source, dest = tmp_path/"record.json", tmp_path/"report.md"
    write(source, result)
    write_from_json(source, dest)
    assert dest.read_text(encoding="utf-8") == report
    assert not source.read_bytes().startswith(b"\xef\xbb\xbf")
    fake = copy.deepcopy(result)
    for t in fake["trials"]:
        t["rates_hz"]["vpoDN"] = 4 if t["condition"] == "virgin_song" else 0
    assert contrast(fake, "vpoDN", "virgin_song", "mated_song") == (4, 0, "supported")
    assert contrast(fake, "vpoDN", "mated_song", "virgin_song") == (-4, 0, "not supported")
    assert contrast(fake, "vpoDN", "mated_song", "mated_silence") == (0, 0, "not supported")
    assert contrast(fake, "vpoDN", "virgin_song", "mated_song", descriptive=True)[2] == "descriptive"
    for t in fake["trials"]:
        if t["condition"] == "virgin_song":
            t["rates_hz"]["vpoDN"] = 1 if t["seed"] == 0 else 3
    # Difference 2, SE 1: exact boundary is not supported.
    assert contrast(fake, "vpoDN", "virgin_song", "mated_song") == (2, 1, "not supported")


def test_protocol_rejects_invalid_timing():
    with pytest.raises(ValueError):
        Protocol(windows=4)
    with pytest.raises(ValueError):
        Protocol(seeds=(0, 0))


@pytest.mark.parametrize("device", ["cpu", "cuda"])
@pytest.mark.parametrize("dt", [.1, .2])
def test_rate_adapter_matches_seed_draws_and_continuation(device, dt):
    if device == "cuda" and not torch.cuda.is_available():
        pytest.skip("CUDA unavailable")
    values = np.array([0., 180., 50.])
    sim = Simulator(csr_matrix((3, 3)), device=device, params=Parameters(dt=dt), drive=Drive((0, 1, 2), 0))
    sim.drive = Drive((0, 1, 2), BatchRates(values, dt))
    state = sim.initial_batch_state([0, 1])
    generators = [torch.Generator().manual_seed(seed) for seed in (0, 1)]
    for _ in range(2):
        result = sim.run_batch(5, state=state)
        expected = np.column_stack([(torch.rand((round(5/dt), 3), generator=g, dtype=torch.float64)
                                    < torch.from_numpy(values)*dt/1000).sum(0).numpy()/0.005 for g in generators])
        np.testing.assert_array_equal(result.sampled_drive_hz, expected)
        np.testing.assert_array_equal(result.delivered_hz, expected)
        np.testing.assert_array_equal(result.requested_hz, np.repeat(values[:, None], 2, axis=1))
    assert state.step == round(10/dt)
    with pytest.raises(ValueError):
        BatchRates([float("nan")], dt)


@pytest.mark.skipif(os.environ.get("FLYBENCH_FAIL_PROBE") != "1", reason="opt-in failure probe")
def test_harness_failure_probe():
    assert False, "Intentional failure: harness must return exit 1"
