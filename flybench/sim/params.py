"""Units: milliseconds and millivolts; source: Shiu et al. (2024).

Line references refer to the supplied upstream model.py.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Parameters:
    v_rest: float = -52.0  # model.py:22
    v_reset: float = -52.0  # model.py:23
    v_th: float = -45.0  # model.py:24,50 (strict comparison)
    tau_m: float = 20.0  # model.py:25
    tau_s: float = 5.0  # model.py:28
    delay: float = 1.8  # model.py:34,175
    refractory: float = 2.2  # model.py:31
    w_syn: float = 0.275  # model.py:37,183
    drive_scale: float = 250.0  # model.py:41,85-92
    dt: float = 0.1  # Local sampling choice; upstream uses linear integration.

    def __post_init__(self):
        if not all(math.isfinite(x) for x in vars(self).values()):
            raise ValueError("Parameters must be finite")
        if self.dt not in (0.1, 0.2):
            raise ValueError("dt must be 0.1 or 0.2 ms")
        if self.tau_m <= 0 or self.tau_s <= 0 or self.tau_m == self.tau_s:
            raise ValueError("Time constants must be positive and distinct")
        if self.delay < 0 or self.refractory < 0:
            raise ValueError("Delay and refractory period must be nonnegative")
        for value in (self.delay, self.refractory):
            if not math.isclose(value / self.dt, round(value / self.dt)):
                raise ValueError("Timing must be an integer number of steps")
