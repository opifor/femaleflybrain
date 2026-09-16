"""Small synthetic oracles for repeat comparisons and reduction."""
import os

import numpy as np
import pytest

from flybench.experiment import jump_repeat as jr


def test_equal_totals_do_not_hide_redistributed_spikes():
    a = np.array([[[1, 0]]], dtype=np.int64)
    b = np.array([[[0, 1]]], dtype=np.int64)
    matrix = jr.equality_matrix([a, a.copy(), b])
    assert matrix == [[True, True, False], [True, True, False], [False, False, True]]
    assert jr.differences(a, b) == {"changed_bins": 2, "l1_spikes": 2,
        "max_abs_bin_spikes": 1, "signed_total_spikes": 0}
    assert jr.classify(matrix, [True]*3, [True]*3) == "run-to-run divergent"


def test_exact_comparison_and_classification():
    a = np.array([30.0])
    b = np.array([np.nextafter(30.0, np.inf)])
    assert jr.equality_matrix([a, b])[0][1] is False
    assert jr.equality_matrix([a, a.astype(np.float32)])[0][1] is False
    assert jr.equality_matrix([a, a.reshape(1, 1)])[0][1] is False
    assert jr.classify([[True]], [False], [True]) == "session-stable, historical-divergent"
    assert jr.classify([[True]], [True], [False]) == "session-stable, historical-divergent"
    assert jr.classify([[True]], [True], [True]) == "fully reproducible"


def test_warmup_denominator_and_strict_ignition():
    counts = np.zeros((6, 10, 3), dtype=np.int64)
    counts[:4] = 1000
    counts[4:, 0, :2] = [[1, 2], [2, 4]]
    counts[4:, 0, 2] = [0, 1]
    result = jr.reduce_counts(counts, np.array([2, 5, 9]),
                              {"vpoDN": np.array([2, 5]), "pC1": np.array([9])})
    assert result == {"vpoDN": {"rate_hz": 45.0, "spikes": 9, "ignition_fraction": .5},
                      "pC1": {"rate_hz": 10.0, "spikes": 1, "ignition_fraction": 0.0}}
    with pytest.raises(ValueError):
        jr.reduce_counts(counts.astype(float), np.array([2, 5, 9]), {})


def test_deliberate_failure_probe():
    if os.environ.get("FLYBENCH_JUMP_REPEAT_FAIL_PROBE") != "1":
        pytest.skip("Opt-in harness failure probe")
    assert False, "Intentional failure: harness must return a nonzero exit"


def test_full_protocol_coverage_and_missing_repeats():
    assert len(jr.PAIRS) == 40
    assert len(set(jr.PAIRS)) == 40
    assert jr.LABELS == ["inproc1", "inproc2", "inproc3", "separate1", "separate2", "separate3"]
    with pytest.raises(ValueError, match="coverage"):
        jr.summarize_runs([], {})


def test_kernel_classification_sees_raw_only_divergence():
    matrix = [[True]*6 for _ in range(6)]
    raw = [row.copy() for row in matrix]
    raw[0][1] = raw[1][0] = False
    row = dict(kernel="jump", condition="virgin_song", seed=4,
               raw_equality_matrix=raw, rate_equality_matrix=matrix,
               historical_equal=[True]*6, readouts_equal=[True]*6,
               historical={g: 10.0 for g in jr.GROUPS},
               readouts={g: 10.0 for g in jr.GROUPS},
               runs=[{"groups": {g: {"rate_hz": 10.0} for g in jr.GROUPS}} for _ in range(6)])
    summary = jr.kernel_summary([row], "jump")
    assert summary["classification"] == "run-to-run divergent"
    assert summary["rate_equality_matrix"] == matrix
    assert summary["mismatches"] == []
    row["runs"][2]["groups"]["pC1"]["rate_hz"] = 11.0
    summary = jr.kernel_summary([row], "jump")
    assert len(summary["mismatches"]) == 7
    assert {m["group"] for m in summary["mismatches"]} == {"pC1"}
