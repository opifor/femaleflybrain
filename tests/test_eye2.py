"""Synthetic temporal and spatial oracles for the graded front end."""
import os

import numpy as np
import pytest

from flybench.eye2 import CHANNEL_NAMES, Config, Eye2, project_objects
from flybench.retinotopy import Column, ColumnMap


def retina():
    return ColumnMap(tuple(Column(h, i, p, q, -.5, 0)
                           for h in ("left", "right")
                           for i, (p, q) in enumerate(((0, 0), (1, 0), (0, 2), (3, 0)))))


def data(mode, n=200):
    rng = np.random.default_rng(2801)
    if mode == "column_luminance":
        return rng.random((n, len(retina().columns)))
    return np.column_stack([rng.uniform(-7, 7, n), rng.uniform(-2, 2, n),
                            rng.uniform(1, 6, n), rng.uniform(1, 5, n), rng.uniform(-1, 1, n)])


@pytest.mark.parametrize("mode", ["column_luminance", "object_parametric"])
def test_causal_prefix_and_irregular_chunks(mode):
    x = data(mode)
    def eye():
        return Eye2(retina(), input_mode=mode)
    whole = eye().process(x, input_mode=mode)
    changed = x.copy()
    changed[100:] = x[:100]
    alternate = eye().process(changed, input_mode=mode)
    prefix = eye().process(x[:100], input_mode=mode)
    e = eye()
    chunks = []
    boundaries = [0, 1, 1, 7, 23, 24, 80, 131, 199, 200]
    for lo, hi in zip(boundaries[:-1], boundaries[1:]):
        r = e.process(x[lo:hi], input_mode=mode)
        assert r.start_sample == lo
        chunks.append(r)
    assert e.samples_processed == len(x)
    for k in CHANNEL_NAMES:
        assert whole.r_graded[k][:, :100].tobytes() == alternate.r_graded[k][:, :100].tobytes()
        assert whole.r_graded[k][:, :100].tobytes() == prefix.r_graded[k].tobytes()
        assert whole.polarity_sign[k][:, :100].tobytes() == prefix.polarity_sign[k].tobytes()
        np.testing.assert_array_equal(whole.r_graded[k][:, :100], alternate.r_graded[k][:, :100])
        np.testing.assert_array_equal(whole.r_graded[k][:, :100], prefix.r_graded[k])
        np.testing.assert_array_equal(whole.polarity_sign[k][:, :100], prefix.polarity_sign[k])
        assert np.max(np.abs(whole.r_signed[k] - np.concatenate([r.r_signed[k] for r in chunks], axis=1))) < 1e-9
        np.testing.assert_array_equal(whole.polarity_sign[k], np.concatenate([r.polarity_sign[k] for r in chunks], axis=1))
    e.reset()
    np.testing.assert_array_equal(e.process(x, input_mode=mode).r_graded["outer"], whole.r_graded["outer"])


def test_independent_scalar_recurrence_and_class_contract():
    x = np.array([[0.0]*8, [1.0]*8, [0.25]*8, [0.0]*8])
    c = Config(sample_rate_hz=500, tau_lowpass_ms=7, tau_sub_ms=30, tau_div_ms=90, strength=3)
    out = Eye2(retina(), input_mode="column_luminance", config=c).process(x, input_mode="column_luminance")
    f = b = d = 0.0
    expected = []
    import math
    af, ab, ad = [math.exp(-1/(500*t/1000)) for t in (7, 30, 90)]
    for value in x[:, 0]:
        f = af*f+(1-af)*value
        b = ab*b+(1-ab)*f
        d = ad*d+(1-ad)*f*f
        expected.append((f-b)/(1+3*d))
    for k in CHANNEL_NAMES:
        np.testing.assert_allclose(out.r_signed[k][0], expected, rtol=1e-14, atol=1e-16)
        np.testing.assert_array_equal(out.r_graded[k], out.r_graded["outer"])
    assert out.column_ids == retina().keys
    assert out.eye_absolute_rate_calibrated is False and out.eye_rate_ceiling_hz is None
    out.r_graded["R7"][:] = -99
    assert (out.r_graded["outer"] >= 0).all()


def test_projection_exact_rectangle_and_contrast():
    m = retina()
    # azimuths left=[1,3,3,7], elevations=[0,0,sqrt(12),0].
    objects = np.array([[2, 0, 2, 1, 1], [3, np.sqrt(12), 1, .1, -1], [2, 0, 2, 1, 0]])
    expected = np.full((3, 8), .5)
    expected[0, :2] = 1
    expected[1, 2] = 0
    np.testing.assert_array_equal(project_objects(objects, m), expected)
    a = Eye2(m, input_mode="object_parametric").process(objects, input_mode="object_parametric")
    b = Eye2(m, input_mode="column_luminance").process(expected, input_mode="column_luminance")
    np.testing.assert_array_equal(a.r_signed["outer"], b.r_signed["outer"])


def test_spatial_oracle_rejects_scrambled_coordinates():
    m = retina()
    objects = np.array([[1, 0, 1, 20, 1]])
    expected = np.array([True, False, False, False, False, False, False, False])
    intact = project_objects(objects, m)[0] > .5
    np.testing.assert_array_equal(intact, expected)
    # Reverse coordinate pairs across fixed identities, including side.
    az, el = m.angles()
    class Scrambled:
        def angles(self, step):
            return az[::-1], el[::-1]
    corrupt = project_objects(objects, Scrambled())[0] > .5
    assert np.count_nonzero(corrupt & ~expected) == 1
    assert np.count_nonzero(expected & ~corrupt) == 1
    assert corrupt.sum() == intact.sum()


@pytest.mark.parametrize("values", [np.zeros((2, 7)), [[np.nan]*8], [[1.01]*8],
                                      [[-.01]*8], [[1j]*8], np.zeros(8)])
def test_rejected_input_does_not_advance(values):
    e = Eye2(retina(), input_mode="column_luminance")
    x = data("column_luminance", 3)
    e.process(x, input_mode="column_luminance")
    prior = e._state.copy()
    with pytest.raises(ValueError):
        e.process(values, input_mode="column_luminance")
    assert e.samples_processed == 3
    np.testing.assert_array_equal(e._state, prior)


@pytest.mark.parametrize("obj", [[[0, 0, 0, 1, 1]], [[0, 0, 1, -1, 1]],
                                  [[0, 0, 1, 1, 1.1]], [[0, np.inf, 1, 1, 1]]])
def test_invalid_object_is_atomic(obj):
    e = Eye2(retina(), input_mode="object_parametric")
    with pytest.raises(ValueError):
        e.process(obj, input_mode="object_parametric")
    assert e.samples_processed == 0 and not e._state.any()


@pytest.mark.parametrize("name", ["sample_rate_hz", "hex_step_deg", "tau_lowpass_ms", "tau_sub_ms", "tau_div_ms", "strength"])
@pytest.mark.parametrize("value", [0, -1, np.nan, np.inf])
def test_invalid_config(name, value):
    with pytest.raises(ValueError):
        Config(**{name: value})


def test_mode_mismatch_and_empty_call():
    with pytest.raises(ValueError):
        Eye2(retina(), input_mode="automatic")
    e = Eye2(retina(), input_mode="column_luminance")
    with pytest.raises(ValueError, match="conversion not in ledger"):
        e.process([[0, 0, 1, 1, 1]], input_mode="object_parametric")
    r = e.process(np.empty((0, 8)), input_mode="column_luminance")
    assert r.r_graded["outer"].shape == (8, 0) and e.samples_processed == 0


def test_temporal_oracle_detects_reset_per_chunk():
    x = np.ones((20, 8))
    e = Eye2(retina(), input_mode="column_luminance")
    whole = e.process(x, input_mode="column_luminance").r_graded["outer"]
    wrong = np.concatenate([Eye2(retina(), input_mode="column_luminance").process(x[:10], input_mode="column_luminance").r_graded["outer"] for _ in range(2)], axis=1)
    assert np.max(np.abs(whole-wrong)) > 1e-3


def test_light_offset_preserves_negative_polarity():
    x = np.concatenate([np.ones((300, 8)), np.zeros((200, 8))])
    r = Eye2(retina(), input_mode="column_luminance").process(x, input_mode="column_luminance")
    for k in CHANNEL_NAMES:
        assert (r.polarity_sign[k][:, :20] > 0).all()
        assert (r.polarity_sign[k][:, 350:400] < 0).all()
        np.testing.assert_array_equal(np.abs(r.r_signed[k]), r.r_graded[k])


def test_harness_failure_probe():
    if os.environ.get("FLYBENCH_EYE_FAIL_PROBE") == "1":
        pytest.fail("Intentional harness failure")
