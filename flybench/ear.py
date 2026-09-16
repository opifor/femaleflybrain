"""Windowed acoustic energy mapping, not a fitted auditory transducer."""
import numpy as np
from scipy.signal import butter, sosfiltfilt
from .song import Song, SAMPLE_RATE

JO_MAX_HZ = 180.0  # engineering ceiling, not calibrated; see README "Scope note on the ear"
BANDS = {"JO-A": (100, 500), "JO-B": (500, 2500)}
FILTERS = {name: butter(4, band, btype="bandpass", fs=SAMPLE_RATE, output="sos")
           for name, band in BANDS.items()}


def filtered(wave, name):
    return sosfiltfilt(FILTERS[name], wave, padlen=27)


RMS_FULL = float(np.sqrt(np.mean(filtered(Song(mixture=1).window(1), "JO-A")**2)))


def rates(wave, jo_max_hz=JO_MAX_HZ):
    wave = np.asarray(wave, dtype=float)
    if wave.ndim != 1 or len(wave) not in (1102, 1103) or not np.isfinite(wave).all():
        raise ValueError("Expected a finite 50 ms waveform at 22050 Hz")
    if not np.isfinite(jo_max_hz) or jo_max_hz < 0:
        raise ValueError("Invalid JO maximum")
    edges = np.rint(np.linspace(0, len(wave), 11)).astype(int)
    return {name: np.array([jo_max_hz*np.clip(np.sqrt(np.mean(band[a:b]**2))/RMS_FULL, 0, 1)
                           for a, b in zip(edges[:-1], edges[1:])])
            for name in BANDS for band in [filtered(wave, name)]}
