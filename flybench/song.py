"""Courtship synthesis; choices, not brain measurements.

Sources supplied by protocol: von Philipsborn 2011 Neuron 69:509;
Clemens/Murthy 2018 Nat Commun (carriers); Zhou 2015 eLife 4:e08477 (IPI).
"""
import numpy as np

SAMPLE_RATE = 22050


class Song:
    """Absolute sample clock prevents rounding drift between windows."""
    def __init__(self, amplitude=1.0, mixture=0.7):
        if not (0 <= amplitude <= 1 and 0 <= mixture <= 1):
            raise ValueError("Amplitude and mixture must be in [0,1]")
        self.amplitude, self.mixture = amplitude, mixture
        self.elapsed = 0.0
        self.sample = 0

    def window(self, seconds=0.05):
        if not np.isfinite(seconds) or seconds <= 0:
            raise ValueError("Duration must be positive")
        self.elapsed += seconds
        end = round(self.elapsed * SAMPLE_RATE)
        t = np.arange(self.sample, end) / SAMPLE_RATE
        self.sample = end
        phase = np.remainder(t, 0.035)
        envelope = np.where(phase < 0.004, 0.5 - 0.5*np.cos(2*np.pi*phase/0.004), 0)
        pulse = envelope * np.sin(2*np.pi*250*t)
        sine = np.sin(2*np.pi*150*t)
        return self.amplitude * (self.mixture*pulse + (1-self.mixture)*sine)
