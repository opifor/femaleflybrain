"""Stateful graded visual front end, with no neuron-drive or spike interface."""
from dataclasses import dataclass, field

import numpy as np

from .retinotopy import ColumnMap, EYE_HEX_STEP_DEG

INPUT_MODES = ("column_luminance", "object_parametric")
CHANNEL_NAMES = ("outer", "R7", "R8")


def _mode(value):
    if value not in INPUT_MODES:
        raise ValueError(f"Explicit input mode required: {INPUT_MODES}")
    return value


@dataclass(frozen=True)
class Config:
    """Every numerical default is a design constant; no biological source."""
    hex_step_deg: float = EYE_HEX_STEP_DEG
    sample_rate_hz: float = 1000.0
    tau_lowpass_ms: float = 5.0
    tau_sub_ms: float = 50.0
    tau_div_ms: float = 100.0
    strength: float = 1.0
    eye_absolute_rate_calibrated: bool = field(default=False, init=False)
    eye_rate_ceiling_hz: None = field(default=None, init=False)

    def __post_init__(self):
        for name in ("hex_step_deg", "sample_rate_hz", "tau_lowpass_ms", "tau_sub_ms", "tau_div_ms", "strength"):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True)
class GradedVisualResponse:
    """Each dictionary value has shape (column, sample), arbitrary graded units."""
    r_graded: dict[str, np.ndarray]
    polarity_sign: dict[str, np.ndarray]
    column_ids: tuple[tuple[str, int], ...]
    input_mode: str
    start_sample: int
    channel_names: tuple[str, ...] = CHANNEL_NAMES
    eye_absolute_rate_calibrated: bool = field(default=False, init=False)
    eye_rate_ceiling_hz: None = field(default=None, init=False)

    @property
    def r_signed(self):
        return {k: self.r_graded[k] * self.polarity_sign[k] for k in self.channel_names}


def _matrix(values, width):
    if np.iscomplexobj(values):
        raise ValueError("Input must be real")
    result = np.asarray(values, dtype=np.float64)
    if result.ndim != 2 or result.shape[1] != width or not np.isfinite(result).all():
        raise ValueError(f"Input must be finite with shape (time, {width})")
    return result


def project_objects(objects, column_map, *, config=None):
    """Explicit rectangle projection; columns follow column_map.keys order.

    Rows: bearing_deg, elevation_deg, full width_deg, full height_deg, contrast.
    Background=.5; inside=.5+.5*contrast. No wrapping, normalization or clipping.
    """
    config = Config() if config is None else config
    obj = _matrix(objects, 5)
    if (obj[:, 2:4] <= 0).any() or (np.abs(obj[:, 4]) > 1).any():
        raise ValueError("Object extents must be positive and contrast in [-1,1]")
    az, el = column_map.angles(config.hex_step_deg)
    inside = ((np.abs(az[None, :] - obj[:, 0, None]) <= obj[:, 2, None] / 2)
              & (np.abs(el[None, :] - obj[:, 1, None]) <= obj[:, 3, None] / 2))
    return .5 + .5 * obj[:, 4, None] * inside


class Eye2:
    """Persistent low-pass, subtractive and divisive states shared by class names.

    R1-6 pooled outer, R7 and R8 have identical temporal behavior by declaration.
    This does not instantiate photoreceptor cells or infer missing anatomy.
    """
    def __init__(self, column_map, *, input_mode, config=None):
        if not isinstance(column_map, ColumnMap):
            raise ValueError("An explicit ColumnMap is required")
        self._column_map = column_map
        self._input_mode = _mode(input_mode)
        self._config = Config() if config is None else config
        if not isinstance(self._config, Config):
            raise ValueError("config must be Config")
        column_map.angles(self.config.hex_step_deg)
        self._decays = tuple(float(np.exp(-1000 / self.config.sample_rate_hz / tau))
                             for tau in (self.config.tau_lowpass_ms, self.config.tau_sub_ms,
                                         self.config.tau_div_ms))
        self.reset()

    @property
    def column_map(self):
        return self._column_map

    @property
    def input_mode(self):
        return self._input_mode

    @property
    def config(self):
        return self._config

    @property
    def samples_processed(self):
        return self._sample

    def reset(self):
        self._state = np.zeros((3, len(self.column_map.columns)))
        self._sample = 0

    def process(self, values, *, input_mode):
        if _mode(input_mode) != self.input_mode:
            raise ValueError("Input mode mismatch; conversion not in ledger")
        if self.input_mode == "object_parametric":
            lum = project_objects(values, self.column_map, config=self.config)
        else:
            lum = _matrix(values, len(self.column_map.columns))
            if (lum < 0).any() or (lum > 1).any():
                raise ValueError("Column luminance must be in [0,1]")
        start = self._sample
        state = self._state.copy()
        signed = np.empty((len(self.column_map.columns), len(lum)))
        low, sub, div = state
        af, ab, ad = self._decays
        for n, value in enumerate(lum):
            low[:] = af * low + (1-af) * value
            sub[:] = ab * sub + (1-ab) * low
            div[:] = ad * div + (1-ad) * low * low
            signed[:, n] = (low-sub) / (1+self.config.strength*div)
        if not np.isfinite(signed).all() or not np.isfinite(state).all():
            raise ValueError("Numerical overflow; state not advanced")
        self._state = state
        self._sample += len(lum)
        magnitude, signs = np.abs(signed), np.sign(signed)
        return GradedVisualResponse({k: magnitude.copy() for k in CHANNEL_NAMES},
                                    {k: signs.copy() for k in CHANNEL_NAMES},
                                    self.column_map.keys, self.input_mode, start)
