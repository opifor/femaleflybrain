"""Cartesian millimetres; positive bearing and rotation mean left (CCW)."""
from dataclasses import dataclass, replace
import math
import numpy as np
from . import constants as C


def wrap(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi


@dataclass(frozen=True, slots=True)
class Body:
    x: float
    y: float
    heading: float
    speed: float = 0.0


@dataclass(frozen=True, slots=True)
class Observation:
    distance: float
    bearing: float
    other_speed: float
    contact: bool
    sound: tuple[float, ...]


class Arena:
    __slots__ = ("bodies", "sound", "size")

    def __init__(self, seed=0):
        rng = np.random.default_rng(seed)
        self.size = C.ARENA_MM
        angle = rng.uniform(-C.INITIAL_HALF_ANGLE, C.INITIAL_HALF_ANGLE)
        center = self.size / 2
        self.bodies = (Body(center, center, 0.0),
                       Body(center + C.INITIAL_DISTANCE_MM * math.cos(angle),
                            center + C.INITIAL_DISTANCE_MM * math.sin(angle),
                            rng.uniform(-math.pi, math.pi)))
        self.sound = ()

    def observe(self, index):
        if index not in (0, 1):
            raise ValueError("Expected body index 0 or 1")
        own, other = self.bodies[index], self.bodies[1-index]
        dx, dy = other.x-own.x, other.y-own.y
        distance = math.hypot(dx, dy)
        return Observation(distance, wrap(math.atan2(dy, dx)-own.heading),
                           other.speed, distance <= C.CONTACT_MM,
                           self.sound if index == 1 else ())

    def advance(self, commands, emitted_wave):
        if len(commands) != 2:
            raise ValueError("Two motor commands required")
        updated = []
        for body, command in zip(self.bodies, commands):
            heading = wrap(body.heading + command.turn * C.WINDOW_MS / 1000)
            x = body.x + command.forward * math.cos(heading) * C.WINDOW_MS / 1000
            y = body.y + command.forward * math.sin(heading) * C.WINDOW_MS / 1000
            hit = not (0 <= x <= self.size and 0 <= y <= self.size)
            updated.append(replace(body, x=float(np.clip(x, 0, self.size)),
                                   y=float(np.clip(y, 0, self.size)), heading=heading,
                                   speed=0.0 if hit else command.forward))
        # Propagation uses emission geometry, before movement; delivered next window.
        from flybench.scent import falloff
        gain = falloff(self.observe(0).distance)
        self.sound = tuple(float(x) * gain for x in emitted_wave)
        self.bodies = tuple(updated)
