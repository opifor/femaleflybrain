"""Observable distance/contact to sensory drive; Or47b is a proxy."""
import math
from flybench.world import constants as C


def falloff(d_mm):
    if not math.isfinite(d_mm) or d_mm < 0:
        raise ValueError("Distance must be finite and nonnegative")
    return 1 / (1 + (d_mm / C.SCENT_D0_MM)**2)


def rates(observation):
    return {"Or47b": C.SMELL_MAX_HZ * falloff(observation.distance),
            C.CONTACT_GROUP: C.CONTACT_MAX_HZ if observation.contact else 0.0}
