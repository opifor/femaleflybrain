"""This is a motor map, not a measurement."""
from dataclasses import dataclass
import numpy as np
from flybench.world import constants as C


@dataclass(frozen=True, slots=True)
class Command:
    turn: float
    forward: float


def command(readings):
    def scaled(name):
        return float(np.clip(readings.get(name, 0.0) / C.MOTOR_SCALE_HZ, 0, 1))
    turn = (readings.get("DNa02_R", 0.0)-readings.get("DNa02_L", 0.0)) / C.MOTOR_SCALE_HZ * C.MAX_TURN_RAD_S
    forward = (scaled("DNa01")*C.MAX_FORWARD_MM_S-scaled("MDN")*C.MAX_REVERSE_MM_S) * (1-scaled("DNp09"))
    return Command(turn, forward)
