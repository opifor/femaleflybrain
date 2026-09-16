import numpy as np
import pytest
from scipy.signal import find_peaks
from flybench.song import Song, SAMPLE_RATE
from flybench.ear import rates, RMS_FULL


def test_clock_phase_and_bound():
    song = Song()
    windows = [song.window() for _ in range(20)]
    assert {len(w) for w in windows} == {1102, 1103}
    assert np.array_equal(np.concatenate(windows), Song().window(1))
    assert max(abs(np.concatenate(windows))) <= 1
    assert not Song(amplitude=0).window().any()
    with pytest.raises(ValueError):
        Song(amplitude=1.01)


def test_pulse_ipi_width_carrier():
    wave = Song(mixture=1).window(1)
    t = np.arange(len(wave))/SAMPLE_RATE
    phase = t % .035
    active = phase < .004
    expected = (.5-.5*np.cos(2*np.pi*phase[active]/.004))*np.sin(2*np.pi*250*t[active])
    np.testing.assert_allclose(wave[active], expected, atol=1e-12)
    assert np.max(abs(wave[~active])) == 0
    starts = np.flatnonzero(np.diff(active.astype(int)) == 1)+1
    np.testing.assert_allclose(np.diff(starts)/SAMPLE_RATE, .035, atol=1/SAMPLE_RATE)
    sine = Song(mixture=0).window(1)
    assert np.argmax(abs(np.fft.rfft(sine))) == 150
    # The repeating two-pulse carrier phase yields a spectral peak near 250 Hz.
    frequencies = np.fft.rfftfreq(len(wave), 1/SAMPLE_RATE)
    peak = frequencies[np.argmax(abs(np.fft.rfft(wave)))]
    assert 230 < peak < 270


def test_ear_selectivity_and_silence():
    pulse = rates(Song(mixture=1).window())
    assert pulse["JO-A"].mean() > pulse["JO-B"].mean()
    t = np.arange(1102)/SAMPLE_RATE
    high = rates(.1*np.sin(2*np.pi*1000*t))
    assert high["JO-B"].mean() > high["JO-A"].mean()
    assert all(not x.any() for x in rates(np.zeros(1103)).values())
    assert 0 < RMS_FULL < 1
    assert all(np.max(v) <= 90 for v in rates(np.ones(1102), 90).values())
    with pytest.raises(ValueError):
        rates(np.zeros(10))
