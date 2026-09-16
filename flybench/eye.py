"""Synthetic contralateral retinal columns; geometry alone determines drive."""
from dataclasses import dataclass
import math
import numpy as np
from flybench.world import constants as C


@dataclass(frozen=True, slots=True)
class Column:
    neuron: int
    azimuth: float
    elevation: float = 0.0


def columns(graph, groups):
    result = []
    half = math.radians(C.HORIZONTAL_FOV / 2)
    for name in ("L1", "L2"):
        for side, sign in (("L", -1), ("R", 1)):
            ids = sorted((int(i) for i in groups[name] if graph["side"][i] == side),
                         key=lambda i: int(graph["body_id"][i]))
            for rank, neuron in enumerate(ids):
                result.append(Column(neuron, sign * half * (rank + 0.5) / len(ids)))
    return tuple(result)


def rates(observation, retina, contrast=C.CONTRAST):
    width = math.atan2(C.BODY_WIDTH_MM / 2, observation.distance)
    height = math.atan2(C.BODY_HEIGHT_MM / 2, observation.distance)
    amplitude = C.EYE_MAX_HZ * float(np.clip(contrast, 0, 1))
    return {c.neuron: amplitude if (
        abs(observation.bearing) <= math.radians(C.HORIZONTAL_FOV / 2)
        and abs(c.elevation) <= math.radians(C.VERTICAL_FOV / 2)
        and ((c.azimuth-observation.bearing)/width)**2 + (c.elevation/height)**2 <= 1
    ) else 0.0 for c in retina}
