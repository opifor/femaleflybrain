"""Synthetic oracles for passive observation and descriptive reductions."""
import copy
import os
import sys

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from flybench.dictionary.entries import entries
from flybench.experiment import female_readouts as fr
from flybench.experiment.protocol import Protocol


def small_graph():
    types = ["JO-A", "JO-B", "ANXXX983", "pC1a", "DNp37", "CB1484", "CB1484x",
             "AVLP008", "CB1385", "DNp13", "oviDNa", "AN_SMP_2", "AN_FLA_SMP_2", "pC1a"]
    n = len(types)
    weights = csr_matrix((np.array([1000., 2000., 3000.]),
                         (np.array([0, 2, 2]), np.array([3, 3, 4]))), shape=(n, n))
    return {"body_id": np.arange(100, 100+n), "type": np.array(types),
            "superclass": np.array(["sensory", "sensory", "ascending", "central_brain_intrinsic",
                                    "descending"]+["central_brain_intrinsic"]*8+["motor"]),
            "class": np.array([""]*n), "nt": np.array([""]*n),
            "data": weights.data, "indices": weights.indices, "indptr": weights.indptr, "meta": {}}


def snapshot(dataset):
    return {"dataset": dataset, "entries": [e.to_dict() for e in entries(dataset)]}


def test_selection_exact_alias_absent_and_original_scope():
    graph = small_graph()
    original, reads = fr.select(graph, snapshot("banc"), "banc")
    assert original["SAG"].tolist() == [2]
    assert original["pC1"].tolist() == [3]
    assert reads["vpoEN-input:CB1484"].tolist() == [5]
    assert reads["AVLP008"].tolist() == [7]
    assert reads["vpoIN"].tolist() == [8]
    assert reads["DNp13/pMN1"].tolist() == [9]
    assert reads["oviDN"].tolist() == [10]
    assert reads["vpoEN-input:WED104"].size == 0
    assert set(reads) == set(fr.GROUPS)
    original, _ = fr.select(graph, snapshot("female"), "female")
    assert original["SAG"].tolist() == [2, 11, 12]
    assert original["pC1"].tolist() == [3, 13]


@pytest.fixture(scope="module")
def executions():
    graph = small_graph()
    original, reads = fr.select(graph, snapshot("female"), "female")
    p = Protocol(seeds=(0, 1), windows=6)
    ordinary = fr.runner.run(p, graph, original, device="cpu")
    observed, observer = fr.observed_run(p, graph, original, reads, device="cpu")
    return p, original, reads, ordinary, observed, observer


def test_passive_observer_preserves_complete_runner_output(executions):
    p, original, reads, ordinary, observed, observer = executions
    assert ordinary["trials"] == observed["trials"]
    assert observed["dictionary"]["groups"].keys() == original.keys()
    assert fr.exact_baseline(observed, ordinary)["passed"]
    assert observer.seen.all()
    assert observer.counts.shape[:4] == (2, 4, 6, 10)
    assert sys.getprofile() is None
    summary, checks = fr.summarize(observer.counts, observer.indices, p, reads, observed)
    assert all(c["equal"] for c in checks)
    assert len(checks) == 32
    assert len(summary["rows"]) == 128
    for row in summary["rows"]:
        if row["group"] == "vpoEN-input:WED104":
            assert row["rate_hz"] is None
            assert row["cell_means_hz"] == []
            assert row["ignition_fraction"] is None
            if "silence" in row:
                assert row["silence"]["within_band"] is None


def test_exact_baseline_detects_one_ulp_missing_duplicate_and_seed_order(executions):
    baseline = executions[3]
    changed = copy.deepcopy(baseline)
    changed["trials"].reverse()
    assert fr.exact_baseline(changed, baseline)["passed"]
    changed["trials"][0]["rates_hz"]["vpoDN"] = np.nextafter(
        changed["trials"][0]["rates_hz"]["vpoDN"], float("inf"))
    assert not fr.exact_baseline(changed, baseline)["passed"]
    changed = copy.deepcopy(baseline)
    changed["trials"].pop()
    assert not fr.exact_baseline(changed, baseline)["passed"]
    changed["trials"].append(changed["trials"][0])
    assert not fr.exact_baseline(changed, baseline)["passed"]


def test_warmup_cell_denominator_pairing_and_strict_ignition():
    p = Protocol(seeds=(7, 2), windows=6)
    reads = {"diagnostic": np.array([10, 20]), "absent": np.array([], dtype=int)}
    counts = np.zeros((2, 4, 6, 10, 2, 2), dtype=np.int64)
    counts[:, :, :4] = 1000  # Would contaminate every result if warm-up leaked.
    # Measured cell Hz in virgin_song: seed7=(20,40), seed2=(40,80).
    counts[:, 0, 4:, 0, :, 0] = [1, 2]
    counts[:, 0, 4:, 0, :, 1] = [2, 4]
    # Mated_song: seed7=(0,20), seed2=(0,40).
    counts[:, 1, 4:, 0, :, 0] = [0, 1]
    counts[:, 1, 4:, 0, :, 1] = [0, 2]
    record = {"trials": [{"kernel": k, "condition": c, "seed": s,
        "rates_hz": {"network": 0}, "ignition_fraction": 0}
        for k in fr.KERNELS for c in p.conditions for s in reversed(p.seeds)]}
    summary, checks = fr.summarize(counts, np.array([10, 20]), p, reads, record)
    first = summary["rows"][0]
    assert first["seed_means_hz"] == [30, 60]
    assert first["rate_hz"] == {"mean": 45, "se": 15, "n": 2}
    assert first["cell_means_hz"] == [30, 60]
    assert first["ignition_fraction"] == .5  # Exactly 30 must not ignite.
    delta = next(r for r in summary["contrasts"] if r["kernel"] == "shiu" and
                 r["group"] == "diagnostic" and r["right"] == "mated_song")
    assert delta["seeds"] == [7, 2]
    assert delta["paired_differences_hz"] == [20, 40]
    assert delta["difference_hz"] == {"mean": 30, "se": 10, "n": 2}
    assert checks == []


@pytest.mark.parametrize("mean,cells,band,zero", [
    (1, [0, 3], True, False), (1.01, [1.01], False, False),
    (1, [0, 3.01], False, False), (0, [0, 0], True, True)])
def test_silence_requires_both_boundaries(mean, cells, band, zero):
    answer = fr.silence_band(mean, cells)
    assert answer["within_band"] is band
    assert answer["all_zero"] is zero


def test_absence_is_not_silence():
    assert fr.silence_band(None, []) == {"status": "absent", "within_band": None,
                                       "max_cell_mean_hz": None, "all_zero": None}


def test_observer_restores_profiler_after_runner_error(monkeypatch):
    def fail(*args, **kwargs):
        raise ValueError("synthetic runner error")
    monkeypatch.setattr(fr.runner, "run", fail)
    with pytest.raises(ValueError, match="synthetic runner error"):
        fr.observed_run(Protocol(seeds=(0, 1), windows=6), {}, {}, {"x": np.array([0])})
    assert sys.getprofile() is None


def test_freeze_uses_lf_and_rejects_tampering(tmp_path):
    text = tmp_path/"input.md"
    text.write_bytes(b"first\r\nsecond\r\n")
    expected = fr.digest(text)
    text.write_bytes(b"first\nsecond\n")
    assert fr.digest(text) == expected
    fr.save_json(tmp_path/fr.FREEZE, {"sha256": {"input.md": expected}})
    fr.verify_freeze(tmp_path)
    text.write_bytes(b"changed\n")
    with pytest.raises(ValueError, match="Frozen input changed"):
        fr.verify_freeze(tmp_path)
    saved = (tmp_path/fr.FREEZE).read_bytes()
    assert not saved.startswith(b"\xef\xbb\xbf") and b"\r" not in saved


def test_deliberate_failure_probe():
    if os.environ.get("FLYBENCH_READOUTS_FAIL_PROBE") != "1":
        pytest.skip("Opt-in harness failure probe")
    assert False, "Intentional failure: harness must return a nonzero exit"
