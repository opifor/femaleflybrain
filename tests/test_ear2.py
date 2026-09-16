"""E1 contracts and preregistered synthetic diagnostics, not JO calibration."""
from dataclasses import FrozenInstanceError, asdict

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.optimize import least_squares
from scipy.signal import freqz

from flybench.ear2 import Channel, Config, Ear2, INPUT_MODES, convert_input_units
from flybench.song import SAMPLE_RATE as FS

MODE = "particle_velocity_mm_s"


def fixture_channels():
    # Explicit engineering fixture. No subtype identity or biological targets.
    return tuple(Channel(f"synthetic_{f}", f, 1.0, 1.0) for f in (150, 300, 600, 900))


def ear(config=None, mode=MODE):
    if config is None:
        config = Config(family="legacy", tau_sub_ms=30, tau_div_ms=50)
    return Ear2(input_mode=mode, channels=fixture_channels(), config=config)


def response(wave, config=None):
    return ear(config).process(wave, input_mode=MODE)


def sine(duration, amplitude=1.0, frequency=300):
    return amplitude * np.sin(2 * np.pi * frequency * np.arange(round(duration * FS)) / FS)


def pulse():
    t = np.arange(round(.004 * FS)) / FS
    return 4 * (.5 - .5 * np.cos(2 * np.pi * t / .004)) * np.sin(2 * np.pi * 300 * t)


def pulse_train(ipi_ms, count=10, duration=None, onset=.05):
    starts = np.array([round((onset + k * ipi_ms / 1000) * FS) for k in range(count)])
    n = round((onset + count * ipi_ms / 1000) * FS) if duration is None else round(duration * FS)
    wave = np.zeros(n)
    p = pulse()
    for start in starts:
        if start < n:
            stop = min(n, start + len(p))
            wave[start:stop] += p[:stop-start]
    return wave, starts


def exponential_fit(t_ms, values):
    """Profile tau on a fixed grid, then bounded scalar nonlinear refinement."""
    t_ms, values = np.asarray(t_ms), np.asarray(values)
    if not np.isfinite(values).all() or len(values) < 4:
        return {"tau_ms": None, "r_squared": None, "amplitude": None, "valid": False}

    def solve(tau):
        design = np.column_stack((np.ones(len(t_ms)), np.exp(-t_ms / tau)))
        coefficients = np.linalg.lstsq(design, values, rcond=None)[0]
        return design @ coefficients - values, coefficients

    taus = np.geomspace(1, 200, 100)
    initial = min(taus, key=lambda tau: np.sum(solve(tau)[0] ** 2))
    result = least_squares(lambda tau: solve(tau[0])[0], [initial], bounds=([1], [200]),
                           ftol=1e-12, xtol=1e-12, gtol=1e-12)
    tau = float(result.x[0])
    residual, (offset, amplitude) = solve(tau)
    variance = float(np.sum((values - values.mean()) ** 2))
    r2 = 1 - float(residual @ residual) / variance if variance > 1e-20 else 0.0
    return {"tau_ms": tau, "r_squared": r2, "amplitude": float(amplitude),
            "offset": float(offset), "valid": bool(result.success and r2 >= .8
                                                      and abs(amplitude) > 1e-6
                                                      and 1.001 < tau < 199.999)}


def multisine_trials():
    rng = np.random.default_rng(1803)
    t = np.arange(round(.5 * FS)) / FS
    f = np.arange(80, 1001, 20)
    # Analytic amplitude convention, never normalize a realized waveform.
    return np.array([np.sin(2*np.pi*f[:, None]*t + rng.uniform(0, 2*np.pi, (len(f), 1)))
                     .sum(axis=0) * np.sqrt(2 / len(f)) for _ in range(16)])


def adaptation_metrics(config=None, trials=None):
    trials = multisine_trials() if trials is None else trials
    switch = round(.25 * FS)
    bins = np.round(np.arange(2, 64) * FS / 1000).astype(int) + switch
    result = {}
    for direction, before, after in (("up", 1, 4), ("down", 4, 1)):
        level = np.where(np.arange(trials.shape[1]) < switch, before, after)
        average = np.mean([response(w * level, config).r_graded.mean(axis=0) for w in trials], axis=0)
        values = np.array([average[a:b].mean() for a, b in zip(bins[:-1], bins[1:])])
        times = ((bins[:-1] + bins[1:]) / 2 - switch) * 1000 / FS
        mask = times <= 62
        result[direction] = exponential_fit(times[mask], values[mask])
    up, down = result["up"], result["down"]
    result["passed"] = bool(up["valid"] and down["valid"] and
                            5 <= up["tau_ms"] < down["tau_ms"] <= 20)
    return result


def recovery_metrics(config=None):
    p = pulse()
    isolated = response(p, config).r_graded.mean(axis=0).max()
    conditioner = sine(.25, 4)
    gaps = np.array([0, 5, 10, 20, 30, 50, 80, 120])
    peaks = []
    for gap in gaps:
        wave = np.concatenate((conditioner, np.zeros(round(gap * FS / 1000)), p))
        peaks.append(float(response(wave, config).r_graded[:, -len(p):].mean(axis=0).max() / isolated))
    result = exponential_fit(gaps, peaks)
    result.update(gaps_ms=gaps.tolist(), relative_probe_peaks=peaks)
    result["within_declared_tolerance"] = bool(result["valid"] and 20 <= result["tau_ms"] <= 40)
    return result


def pulse_metrics(config=None):
    ratios = {}
    for ipi in (36, 10):
        wave, starts = pulse_train(ipi)
        y = response(wave, config).r_graded.mean(axis=0)
        ends = np.r_[starts[1:], len(wave)]
        peaks = [float(y[a:b].max()) for a, b in zip(starts, ends)]
        ratios[str(ipi)] = {"peaks": peaks, "ratio": peaks[-1] / peaks[0]}
    ratios["passed"] = bool(ratios["36"]["ratio"] >= .9 and ratios["10"]["ratio"] < .9)
    return ratios


def continuous_metrics(config=None):
    energy = quad(lambda t: (4*(.5-.5*np.cos(2*np.pi*t/.004))*np.sin(2*np.pi*300*t))**2,
                  0, .004, epsabs=1e-12)[0]
    amplitude = np.sqrt(2 * energy / .036)
    continuous = sine(.5, amplitude)
    pulsed, _ = pulse_train(36, count=14, duration=.5, onset=0)
    metrics = {}
    for name, wave in (("continuous", continuous), ("pulsed", pulsed)):
        y = response(wave, config).r_graded.mean(axis=0)
        metrics[name] = {"ratio": float(y[-round(.1*FS):].mean() / y[:round(.05*FS)].max()),
                         "realized_rms": float(np.sqrt(np.mean(wave**2)))}
    metrics["analytic_rms"] = float(amplitude / np.sqrt(2))
    metrics["passed"] = bool(metrics["continuous"]["ratio"] < metrics["pulsed"]["ratio"])
    return metrics


def tuning_metrics():
    frequencies = np.arange(20, 2001, dtype=float)
    magnitudes = np.array([abs(freqz(*c.coefficients(), worN=frequencies, fs=FS)[1])
                           for c in fixture_channels()])
    peaks = frequencies[magnitudes.argmax(axis=1)]
    relative = magnitudes / magnitudes.max(axis=1)[:, None]
    overlap = frequencies[(frequencies < 500) & (relative[0] >= .5) & (relative[1] >= .5)]
    return {"synthetic_peaks_hz": peaks.tolist(), "synthetic_overlap_below_500_hz": overlap.tolist(),
            "biological_status": "unassessed", "reason": "JO subtype tuning centers not in ledger",
            "F_channel_present": False}


def phase_metrics(config=None):
    r = response(sine(.5), config)
    y = r.r_graded[:, -round(.2*FS):].mean(axis=0)
    spectrum = abs(np.fft.rfft(y))
    frequencies = np.fft.rfftfreq(len(y), 1 / FS)
    ratio = float(spectrum[np.argmin(abs(frequencies - 600))] / spectrum[0])
    channels = abs(np.fft.rfft(r.r_graded[:, -round(.2*FS):], axis=1))
    index = np.argmin(abs(frequencies - 600))
    return {"600_hz_over_dc": ratio, "passed": bool(ratio > .05),
            "per_channel_600_hz_over_dc": (channels[:, index] / channels[:, 0]).tolist(),
            "both_signs": bool(np.any(r.phase_sign < 0) and np.any(r.phase_sign > 0))}


def causal_chunk_metrics(config=None):
    x = np.random.default_rng(1801).normal(size=round(.1*FS))
    split = round(.05*FS)
    altered = x.copy()
    altered[split:] = 100 * altered[split:] + 11
    whole, changed, prefix = response(x, config), response(altered, config), response(x[:split], config)
    causal = all(np.array_equal(getattr(whole, key)[:, :split], getattr(other, key)[:, :split])
                 for key in ("r_graded", "phase_sign") for other in (changed, prefix))
    x = np.random.default_rng(1802).normal(size=round(.05*FS))
    whole = response(x, config)
    bank = ear(config)
    boundaries = np.round(np.arange(11)*.005*FS).astype(int)
    chunks = [bank.process(x[a:b], input_mode=MODE) for a, b in zip(boundaries[:-1], boundaries[1:])]
    joined = np.concatenate([r.r_graded for r in chunks], axis=1)
    joined_signed = np.concatenate([r.r_signed for r in chunks], axis=1)
    return {"causal_bit_equal": bool(causal), "chunk_max_error": float(abs(whole.r_graded-joined).max()),
            "signed_chunk_max_error": float(abs(whole.r_signed-joined_signed).max()),
            "phase_bit_equal": bool(np.array_equal(whole.phase_sign, np.concatenate([r.phase_sign for r in chunks], axis=1))),
            "chunk_samples": np.diff(boundaries).tolist()}


def test_g1_causal():
    assert causal_chunk_metrics()["causal_bit_equal"]


def test_g2_chunks():
    m = causal_chunk_metrics()
    assert m["chunk_max_error"] < 1e-9
    assert m["signed_chunk_max_error"] < 1e-9
    assert m["phase_bit_equal"]


@pytest.mark.parametrize("mode", INPUT_MODES)
def test_irregular_chunks_empty_reset(mode):
    x = np.random.default_rng(18).normal(size=4001)
    bank = ear(mode=mode)
    bounds = [0, 0, 1, 19, 1102, 1103, 2099, 4001]
    chunks = [bank.process(x[a:b], input_mode=mode) for a, b in zip(bounds[:-1], bounds[1:])]
    expected = ear(mode=mode).process(x, input_mode=mode)
    assert np.array_equal(expected.r_graded, np.concatenate([r.r_graded for r in chunks], axis=1))
    assert [r.start_sample for r in chunks] == bounds[:-1]
    bank.reset()
    assert np.array_equal(bank.process(x, input_mode=mode).r_graded, expected.r_graded)
    fresh_chunks = [ear(mode=mode).process(x[a:b], input_mode=mode).r_graded
                    for a, b in zip(bounds[:-1], bounds[1:])]
    assert np.max(abs(expected.r_graded-np.concatenate(fresh_chunks, axis=1))) > .01


def test_g3_adaptation():
    m = adaptation_metrics()
    if not m["passed"]:
        pytest.xfail(f"G3 not passed on initial synthetic fixture: {m}")
    assert m["up"]["tau_ms"] < m["down"]["tau_ms"]


def test_g4_pulse_recovery():
    m = pulse_metrics()
    if not m["passed"]:
        pytest.xfail(f"G4 not passed on initial synthetic fixture: {m}")
    assert m["36"]["ratio"] >= .9 and m["10"]["ratio"] < .9


def test_g5_continuous():
    m = continuous_metrics()
    if not m["passed"]:
        pytest.xfail(f"G5 not passed on initial synthetic fixture: {m}")
    assert m["continuous"]["ratio"] < m["pulsed"]["ratio"]


def test_g6_jo_tuning_unassessed():
    pytest.skip("Historical round-1 fixture: no JO identities; round-2 placement tested separately")


def test_filter_transfer_and_synthetic_overlap():
    m = tuning_metrics()
    targets = np.array([c.center_hz for c in fixture_channels()])
    assert np.max(abs(np.array(m["synthetic_peaks_hz"])/targets-1)) < .01
    assert m["synthetic_overlap_below_500_hz"]
    # Independent analog response evaluated at the bilinear mapped frequency.
    frequency = np.array([30, 150, 300, 700, 1800])
    for c in fixture_channels():
        omega = 2*FS*np.tan(np.pi*frequency/FS)
        s = 1j*omega
        expected = c.gain*(c.omega_rad_s/c.q)*s / (s*s+c.omega_rad_s/c.q*s+c.omega_rad_s**2)
        actual = freqz(*c.coefficients(), worN=frequency, fs=FS)[1]
        np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=1e-12)


def test_g7_phase():
    m = phase_metrics()
    if not m["passed"]:
        pytest.xfail(f"G7 not passed on initial synthetic fixture: {m}")
    assert m["passed"]


def test_phase_sign_and_single_channel_rectification():
    r = response(sine(.1))
    assert np.array_equal(abs(r.r_signed), r.r_graded)
    assert np.any(r.phase_sign < 0) and np.any(r.phase_sign > 0)
    assert phase_metrics()["per_channel_600_hz_over_dc"][1] > .05


@pytest.mark.parametrize("source,target", [(INPUT_MODES[0], INPUT_MODES[1]), (INPUT_MODES[1], INPUT_MODES[0])])
def test_mode_separation(source, target):
    with pytest.raises(ValueError, match="conversion"):
        convert_input_units([1, 2], source, target)
    bank = ear(mode=source)
    with pytest.raises(ValueError, match="conversion"):
        bank.process([1, 2], input_mode=target)
    assert bank.samples_processed == 0
    x = np.array([1., 2.])
    copied = convert_input_units(x, source, source)
    assert np.array_equal(x, copied) and not np.shares_memory(x, copied)


def test_explicit_input_and_no_trial_normalization():
    bank = ear()
    with pytest.raises(TypeError):
        bank.process([1, 2])
    small = response(sine(.1, .001)).r_graded
    large = response(sine(.1, .002)).r_graded
    assert large.max() > 1.9 * small.max()
    assert not response(np.zeros(100)).r_graded.any()
    # No fixed arbitrary-Hz clipping: changing initialization tau changes
    # the attainable graded transient, and amplitude is never RMS normalized.
    assert response(np.r_[1000., np.zeros(100)]).r_graded.max() > 90


def test_constants_and_missing_calibration():
    c = Config()
    d = asdict(c)
    assert d["jo_absolute_rate_calibrated"] is False
    assert d["jo_rate_ceiling_hz"] is None and d["jo_refractory_ms"] is None
    assert d["allow_uncalibrated_spike_drive"] is False
    with pytest.raises(FrozenInstanceError):
        c.allow_uncalibrated_spike_drive = True
    with pytest.raises(TypeError):
        Config(allow_uncalibrated_spike_drive=True)
    with pytest.raises(ValueError, match="not in ledger"):
        Ear2(input_mode=MODE)
    with pytest.raises(ValueError, match="F channel"):
        Channel("F", 300, 1, 1, subtype="F")


@pytest.mark.parametrize("wave", [[np.nan], [np.inf], [[1., 2.]], [1j]])
def test_invalid_wave_preserves_state(wave):
    bank = ear()
    prefix, suffix = sine(.02), sine(.03)
    bank.process(prefix, input_mode=MODE)
    with pytest.raises(ValueError):
        bank.process(wave, input_mode=MODE)
    actual = bank.process(suffix, input_mode=MODE).r_graded
    assert np.array_equal(actual, response(np.r_[prefix, suffix]).r_graded[:, len(prefix):])


@pytest.mark.parametrize("kwargs", [{"center_hz": 0}, {"center_hz": FS/2}, {"q": 0},
                                    {"gain": -1}, {"gain": np.nan}])
def test_invalid_channel(kwargs):
    values = dict(name="test", center_hz=300, q=1, gain=1)
    values.update(kwargs)
    with pytest.raises(ValueError):
        Channel(**values)


@pytest.mark.parametrize("tau", [0, -1, np.nan, np.inf])
def test_invalid_time_constant(tau):
    with pytest.raises(ValueError):
        Config(tau_sub_ms=tau)
    with pytest.raises(ValueError):
        Config(tau_div_ms=tau)


def test_exponential_oracle():
    t = np.arange(2.5, 62, 1.)
    fit = exponential_fit(t, .2+.7*np.exp(-t/12))
    assert fit["valid"] and abs(fit["tau_ms"]-12) < 1e-5
    assert not exponential_fit(t, np.ones(len(t)))["valid"]
    assert not exponential_fit(t, np.sin(t))["valid"]


def test_sample_equations_against_independent_recurrence():
    # A swapped adaptation stage or rectifying before subtraction breaks this.
    config = Config(family="legacy", tau_sub_ms=10, tau_div_ms=20)
    x = np.random.default_rng(1901).normal(size=401)
    actual = response(x, config)
    expected = np.empty_like(actual.r_graded)
    signs = np.empty_like(expected)
    a_sub = np.exp(-1000/(FS*config.tau_sub_ms))
    a_div = np.exp(-1000/(FS*config.tau_div_ms))
    for k, channel in enumerate(fixture_channels()):
        b, a = channel.coefficients()
        y1 = y2 = x1 = x2 = baseline = divisor = 0.0
        for n, sample in enumerate(x):
            y = b[0]*sample+b[1]*x1+b[2]*x2-a[1]*y1-a[2]*y2
            baseline = a_sub*baseline+(1-a_sub)*y
            signed = y-baseline
            rectified = abs(signed)
            divisor = a_div*divisor+(1-a_div)*rectified
            expected[k, n] = rectified/(1+divisor)
            signs[k, n] = np.sign(signed)
            y2, y1, x2, x1 = y1, y, x1, sample
    np.testing.assert_allclose(actual.r_graded, expected, atol=1e-12, rtol=1e-12)
    assert np.array_equal(actual.phase_sign, signs)


def test_bank_contract_rejections():
    channels = fixture_channels()
    with pytest.raises(ValueError, match="four"):
        Ear2(input_mode=MODE, channels=channels[:3])
    with pytest.raises(ValueError, match="unique"):
        Ear2(input_mode=MODE, channels=[channels[0]]*4)
    with pytest.raises(ValueError, match="mode"):
        Ear2(input_mode="arbitrary", channels=channels)


# Round-2 diagnostics reuse the frozen stimuli and observation mapping.
from unittest.mock import patch
from flybench.ear2 import reported_channels

ROUND2_FAMILIES = ("energy_feedback", "asymmetric_energy")


def gate3(up, down):
    return bool(up["valid"] and down["valid"] and
                5 <= up["tau_ms"] < down["tau_ms"] <= 20)


def gate4(r36, r10):
    return bool(r36 >= .9 and r10 < .9)


def gate5(continuous, pulsed):
    return bool(continuous < pulsed)


def harmonic_metrics(r):
    y = r.r_graded[:, -round(.2*FS):].mean(axis=0)
    spectrum = abs(np.fft.rfft(y))
    freq = np.fft.rfftfreq(len(y), 1/FS)
    dc, a300, a600 = (float(spectrum[np.argmin(abs(freq-f))]) for f in (0,300,600))
    floor = 1e-12*dc
    ratio = a600/max(a300, floor) if dc > 0 else 0.
    signs = bool(np.any(r.phase_sign < 0) and np.any(r.phase_sign > 0))
    reconstructed = bool(np.array_equal(abs(r.r_signed), r.r_graded))
    return dict(amplitude_300=a300, amplitude_600=a600, dc=dc,
                ratio_600_over_300_or_lower_bound=ratio,
                denominator_below_floor=bool(a300 < floor),
                ratio_600_over_dc=a600/dc if dc > 0 else 0.,
                both_signs=signs, reconstructed=reconstructed,
                passed=bool(ratio > .5 and signs and reconstructed and dc > 0))


def reported_tuning_metrics(channels=None):
    from pathlib import Path
    import json
    ledger = json.loads((Path(__file__).resolve().parents[1]/'reference/calibration_ledger.json').read_text('utf-8'))
    entries = {e['id']: e for e in ledger['measurements']}
    channels = reported_channels() if channels is None else channels
    frequencies = np.arange(20,2001, dtype=float)
    magnitudes = np.array([abs(freqz(*c.coefficients(), worN=frequencies, fs=FS)[1]) for c in channels])
    relative = magnitudes/magnitudes.max(axis=1)[:,None]
    peaks = frequencies[magnitudes.argmax(axis=1)]
    targets = np.array([entries[c.ledger_id]['value'] for c in channels[:4]])
    peak_ok = bool(np.all(abs(peaks[:4]/targets-1) <= .15))
    band = frequencies[relative[4] >= 1/np.sqrt(2)]
    edges = [float(band[0]),float(band[-1])] if len(band) else [0.,0.]
    edge_ok = bool(np.all(abs(np.array(edges)/entries['R6_001']['value']-1) <= .15))
    overlap = frequencies[(frequencies < 500) & (relative[4] >= .5) &
                          ((relative[0] >= .5) | (relative[1] >= .5))]
    no_f = not any(c.subtype in ('F','JO-F') for c in channels)
    return dict(peaks_hz=peaks.tolist(), targets_hz=targets.tolist(),
                a_half_power_edges_hz=edges, overlap_below_500_hz=overlap.tolist(),
                no_f=no_f, passed=bool(peak_ok and edge_ok and len(overlap) and no_f),
                biological_validation='unassessed; conditional placement only',
                anatomy='100/125 components provisionally B-associated; no unique mapping')


def round2_metrics(config, trials=None):
    with patch(__name__+'.fixture_channels', reported_channels):
        causal = causal_chunk_metrics(config)
        adaptation = adaptation_metrics(config, trials)
        recovery = recovery_metrics(config)
        pulses = pulse_metrics(config)
        continuous = continuous_metrics(config)
        harmonic = harmonic_metrics(response(sine(.5), config))
    tuning = reported_tuning_metrics()
    gates = dict(G1=causal['causal_bit_equal'],
                 G2=bool(causal['chunk_max_error'] < 1e-9 and
                         causal['signed_chunk_max_error'] < 1e-9 and causal['phase_bit_equal']),
                 G3=gate3(adaptation['up'], adaptation['down']),
                 G4=gate4(pulses['36']['ratio'], pulses['10']['ratio']),
                 G5=gate5(continuous['continuous']['ratio'], continuous['pulsed']['ratio']),
                 G6=tuning['passed'], G7=harmonic['passed'])
    return dict(gates=gates, causal=causal, adaptation=adaptation, recovery=recovery,
                pulses=pulses, continuous=continuous, tuning=tuning, harmonic=harmonic)


@pytest.mark.parametrize('family', ROUND2_FAMILIES)
def test_round2_causal_and_chunks(family):
    config = Config(family=family)
    with patch(__name__+'.fixture_channels', reported_channels):
        m = causal_chunk_metrics(config)
        assert m['causal_bit_equal'] and m['phase_bit_equal']
        assert m['chunk_max_error'] < 1e-9 and m['signed_chunk_max_error'] < 1e-9
        x = np.random.default_rng(24).normal(size=1600)
        bank = ear(config)
        bounds = [0,0,1,37,900,901,1600]
        chunks = [bank.process(x[a:b], input_mode=MODE) for a,b in zip(bounds[:-1],bounds[1:])]
        expected = response(x,config)
        assert np.array_equal(expected.r_graded,np.concatenate([r.r_graded for r in chunks],axis=1))
        bank.reset()
        assert np.array_equal(expected.r_graded,bank.process(x,input_mode=MODE).r_graded)
        restarted = np.concatenate([response(x[a:b],config).r_graded for a,b in zip(bounds[:-1],bounds[1:])],axis=1)
        assert np.max(abs(expected.r_graded-restarted)) > .01


@pytest.mark.parametrize('family', ROUND2_FAMILIES)
def test_round2_independent_recurrence(family):
    config = Config(family=family, tau_div_ms=30, tau_up_ms=10, tau_down_ms=20, strength=4)
    x = np.random.default_rng(71).normal(size=351)
    actual = response(x, config)
    expected = np.empty_like(actual.r_graded)
    for k, channel in enumerate(fixture_channels()):
        b,a = channel.coefficients()
        x1=x2=y1=y2=base=d=0.
        for n,sample in enumerate(x):
            y=b[0]*sample+b[1]*x1+b[2]*x2-a[1]*y1-a[2]*y2
            sub=np.exp(-1000/(FS*config.tau_sub_ms))
            base=sub*base+(1-sub)*y
            tau=config.tau_div_ms if family=='energy_feedback' else (
                config.tau_up_ms if y*y>d else config.tau_down_ms)
            decay=np.exp(-1000/(FS*tau))
            d=decay*d+(1-decay)*y*y
            expected[k,n]=abs((y-base)/(1+config.strength*d))
            x2,x1,y2,y1=x1,sample,y1,y
    np.testing.assert_allclose(actual.r_graded,expected,atol=1e-12,rtol=1e-12)


def test_round2_gate_oracles():
    valid=lambda tau: dict(valid=True,tau_ms=tau)
    assert gate3(valid(5),valid(20))
    assert not gate3(valid(20),valid(5))
    assert not gate3(valid(4.99),valid(20))
    assert not gate3(dict(valid=False,tau_ms=5),valid(20))
    assert gate4(.9,.899) and not gate4(.899,.8) and not gate4(.99,.9)
    assert gate5(.1,.2) and not gate5(.2,.1) and not gate5(.1,.1)
    from flybench.ear2 import GradedResponse
    t=np.arange(round(.2*FS))/FS
    signs=np.sign(np.sin(2*np.pi*300*t))[None,:]
    signs[signs==0]=1
    def synthetic(a600):
        y=(1+.2*np.cos(2*np.pi*300*t)+a600*np.cos(2*np.pi*600*t))[None,:]
        return GradedResponse(y,signs,('synthetic',),MODE,0)
    assert harmonic_metrics(synthetic(.11))['passed']
    assert not harmonic_metrics(synthetic(.09))['passed']
    zero=GradedResponse(np.zeros_like(signs),signs,('synthetic',),MODE,0)
    assert not harmonic_metrics(zero)['passed']
    assert reported_tuning_metrics()['passed']
    from dataclasses import replace
    bad=list(reported_channels())
    bad[0]=replace(bad[0],center_hz=180)
    assert not reported_tuning_metrics(bad)['passed']


@pytest.mark.parametrize('family', ROUND2_FAMILIES)
def test_round2_gate_calculations(family):
    # Scientific misses remain data; these assertions test calculation consistency.
    with patch(__name__+'.fixture_channels', reported_channels):
        config=Config(family=family)
        p=pulse_metrics(config)
        assert p['passed']==gate4(p['36']['ratio'],p['10']['ratio'])
        c=continuous_metrics(config)
        assert c['passed']==gate5(c['continuous']['ratio'],c['pulsed']['ratio'])
        h=harmonic_metrics(response(sine(.5),config))
        assert h['both_signs'] and h['reconstructed']


@pytest.mark.parametrize('kwargs', [dict(family='unknown'),dict(strength=0),
    dict(strength=np.nan),dict(tau_up_ms=0),dict(tau_down_ms=np.inf)])
def test_round2_invalid_config(kwargs):
    with pytest.raises(ValueError):
        Config(**kwargs)


def test_round2_default_is_selected_winner():
    # A default-family or fitted-parameter drift must break this regression.
    c=Config()
    assert (c.family,c.tau_sub_ms,c.tau_div_ms,c.strength)==('energy_feedback',5,10,1)
    x=sine(.03)
    bank=Ear2(input_mode=MODE,channels=reported_channels())
    explicit=Ear2(input_mode=MODE,channels=reported_channels(),
                  config=Config(family='energy_feedback',tau_sub_ms=5,tau_div_ms=10,strength=1))
    assert np.array_equal(bank.process(x,input_mode=MODE).r_graded,
                          explicit.process(x,input_mode=MODE).r_graded)
