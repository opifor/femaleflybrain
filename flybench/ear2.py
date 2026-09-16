"""Causal stateful graded transduction; no calibrated JO rates or spikes.

Channel parameters must be supplied explicitly. The round-2 conditional bank
places reported functional preferences without claiming resolved anatomy.
Input samples already carry the physical units named by ``input_mode``.
"""
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from scipy.signal import bilinear, lfilter

from .song import SAMPLE_RATE

InputMode = Literal["particle_velocity_mm_s", "arista_displacement_um"]
INPUT_MODES = ("particle_velocity_mm_s", "arista_displacement_um")
FAMILIES = ("legacy", "energy_feedback", "asymmetric_energy")


def _mode(mode: str) -> str:
    if mode not in INPUT_MODES:
        raise ValueError(f"Explicit input mode required; choose one of {INPUT_MODES}")
    return mode


def convert_input_units(waveform, source_mode: str, target_mode: str):
    """Only identity copies exist; cross-mode conversion is unmeasured."""
    _mode(source_mode)
    _mode(target_mode)
    if source_mode != target_mode:
        raise ValueError("Velocity/displacement conversion not in ledger")
    return np.array(waveform, dtype=np.float64, copy=True)


@dataclass(frozen=True)
class Channel:
    """An explicitly chosen filter, not an inferred biological subtype."""

    name: str
    center_hz: float
    q: float
    gain: float
    subtype: str | None = None
    ledger_id: str | None = None

    def __post_init__(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Channel name must be a nonempty string")
        if not np.isfinite(self.center_hz) or not 0 < self.center_hz < SAMPLE_RATE / 2:
            raise ValueError("Center must be finite and strictly below Nyquist")
        if not np.isfinite(self.q) or self.q <= 0:
            raise ValueError("Q must be finite and positive")
        if not np.isfinite(self.gain) or self.gain <= 0:
            raise ValueError("Gain must be finite and positive")
        if self.subtype is not None and self.subtype.upper() in ("F", "JO-F"):
            raise ValueError("F channel is not supported in E1")

    @property
    def omega_rad_s(self):
        """Prewarped analog center used by the bilinear transform."""
        return float(2 * SAMPLE_RATE * np.tan(np.pi * self.center_hz / SAMPLE_RATE))

    def coefficients(self):
        omega = self.omega_rad_s
        return bilinear([self.gain * omega / self.q, 0.0],
                        [1.0, omega / self.q, omega * omega], fs=SAMPLE_RATE)


@dataclass(frozen=True)
class Config:
    """Defaults are the conditional round-2 grid winner, not measured constants.

    Legacy round-1 initialization is explicit: family="legacy",
    tau_sub_ms=30, tau_div_ms=50. Up/down constants are used only by
    asymmetric_energy; tau_div_ms is unused by that family.
    """

    tau_sub_ms: float = 5.0
    tau_div_ms: float = 10.0
    family: str = "energy_feedback"
    tau_up_ms: float = 5.0
    tau_down_ms: float = 20.0
    strength: float = 1.0
    jo_absolute_rate_calibrated: bool = field(default=False, init=False)
    jo_rate_ceiling_hz: None = field(default=None, init=False)
    jo_refractory_ms: None = field(default=None, init=False)
    allow_uncalibrated_spike_drive: bool = field(default=False, init=False)

    def __post_init__(self):
        if self.family not in FAMILIES:
            raise ValueError(f"Unknown adaptation family: {self.family}")
        for tau in (self.tau_sub_ms, self.tau_div_ms, self.tau_up_ms, self.tau_down_ms):
            if not np.isfinite(tau) or tau <= 0:
                raise ValueError("Adaptation times must be finite and positive")
        if not np.isfinite(self.strength) or self.strength <= 0:
            raise ValueError("Feedback strength must be finite and positive")


def reported_channels():
    """Conditional target placement; Q/gain and B association are provisional.

    Calcium functional classes do not uniquely map to anatomical A/B cells.
    The aggregate A edges are reported response extents, not measured -3 dB
    points; using them as design edges is declared in the round-2 amendment.
    """
    edges = 2*SAMPLE_RATE*np.tan(np.pi*np.array([100., 1200.])/SAMPLE_RATE)
    omega = float(np.sqrt(np.prod(edges)))
    center = float(SAMPLE_RATE/np.pi*np.arctan(omega/(2*SAMPLE_RATE)))
    functional = tuple(Channel(f"functional_{f}", f, 1., 1., ledger_id=f"R6_{i:03d}")
                       for i, f in enumerate((100, 125, 225, 600), 8))
    return functional + (Channel("A_aggregate", center, omega/float(np.diff(edges)[0]),
                                 1., subtype="A", ledger_id="R6_001"),)


@dataclass(frozen=True)
class GradedResponse:
    r_graded: np.ndarray
    phase_sign: np.ndarray
    channel_names: tuple[str, ...]
    input_mode: str
    start_sample: int

    @property
    def r_signed(self):
        return self.r_graded * self.phase_sign


class Ear2:
    """Persistent second-order filter bank followed by two adaptation stages.

    ``process`` accepts arbitrary chunk lengths, including empty chunks.
    Only ``reset`` starts a new trial. No window size affects the equations.
    Each physical input mode needs its own instance and calibration; equal
    numeric inputs do not establish a physical conversion between modes.
    """

    def __init__(self, *, input_mode: InputMode, channels=None, config=None):
        self._input_mode = _mode(input_mode)
        if channels is None:
            raise ValueError("Resolved channel anatomy/gains not in ledger; explicit channels required")
        self._channels = tuple(channels)
        if len(self._channels) < 4 or not all(isinstance(c, Channel) for c in self._channels):
            raise ValueError("At least four explicit Channel objects required")
        if len({c.name for c in self._channels}) != len(self._channels):
            raise ValueError("Channel names must be unique")
        self._config = Config() if config is None else config
        if not isinstance(self._config, Config):
            raise ValueError("config must be Config")
        self._coefficients = tuple(c.coefficients() for c in self._channels)
        self._a_sub = np.exp(-1000.0 / (SAMPLE_RATE * self.config.tau_sub_ms))
        self._a_div = np.exp(-1000.0 / (SAMPLE_RATE * self.config.tau_div_ms))
        self._a_up = np.exp(-1000.0 / (SAMPLE_RATE * self.config.tau_up_ms))
        self._a_down = np.exp(-1000.0 / (SAMPLE_RATE * self.config.tau_down_ms))
        self.reset()

    @property
    def input_mode(self):
        return self._input_mode

    @property
    def channels(self):
        return self._channels

    @property
    def config(self):
        return self._config

    @property
    def samples_processed(self):
        return self._sample

    def reset(self):
        count = len(self.channels)
        self._filter_state = np.zeros((count, 2), dtype=np.float64)
        self._sub_state = np.zeros((count, 1), dtype=np.float64)
        self._div_state = np.zeros((count, 1), dtype=np.float64)
        self._sample = 0

    def process(self, waveform, *, input_mode: InputMode):
        """Return graded magnitudes and pre-rectification signs, never Hz.

        A repeated explicit mode prevents accidentally feeding samples from
        the other physical contract into an existing state's history.
        Invalid input is rejected before any state is advanced.
        """
        if _mode(input_mode) != self.input_mode:
            raise ValueError("Input mode mismatch; conversion not in ledger")
        if np.iscomplexobj(waveform):
            raise ValueError("Waveform must be real")
        wave = np.asarray(waveform, dtype=np.float64)
        if wave.ndim != 1 or not np.isfinite(wave).all():
            raise ValueError("Waveform must be one-dimensional and finite")
        start = self._sample
        if wave.size == 0:
            graded = np.empty((len(self.channels), 0), dtype=np.float64)
            signs = graded.copy()
        else:
            filtered = np.empty((len(self.channels), wave.size), dtype=np.float64)
            filter_state = self._filter_state.copy()
            for k, (b, a) in enumerate(self._coefficients):
                filtered[k], filter_state[k] = lfilter(b, a, wave, zi=filter_state[k])
            baseline, sub_state = lfilter([1 - self._a_sub], [1, -self._a_sub],
                                         filtered, axis=-1, zi=self._sub_state)
            residual = filtered - baseline
            signs = np.sign(residual)
            rectified = np.abs(residual)
            if self.config.family == "legacy":
                divisor, div_state = lfilter([1 - self._a_div], [1, -self._a_div],
                                            rectified, axis=-1, zi=self._div_state)
                graded = rectified / (1.0 + divisor)
            elif self.config.family == "energy_feedback":
                divisor, div_state = lfilter([1 - self._a_div], [1, -self._a_div],
                                            filtered**2, axis=-1, zi=self._div_state)
                graded = np.abs(residual / (1.0 + self.config.strength * divisor))
            else:
                # This family's state stores d itself, not lfilter's scaled zi.
                divisor = np.empty_like(filtered)
                div_state = self._div_state.copy()
                for k, row in enumerate(filtered**2):
                    d = float(div_state[k, 0])
                    for n, energy in enumerate(row):
                        a = self._a_up if energy > d else self._a_down
                        d = a*d + (1-a)*energy
                        divisor[k, n] = d
                    div_state[k, 0] = d
                graded = np.abs(residual / (1.0 + self.config.strength * divisor))
            if not (np.isfinite(graded).all() and np.isfinite(filter_state).all()
                    and np.isfinite(sub_state).all() and np.isfinite(div_state).all()):
                raise ValueError("Numerical overflow; state was not advanced")
            self._filter_state = filter_state
            self._sub_state = sub_state
            self._div_state = div_state
            self._sample += wave.size
        return GradedResponse(graded, signs, tuple(c.name for c in self.channels),
                              self.input_mode, start)
