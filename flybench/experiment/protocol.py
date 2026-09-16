"""Load the preregistration before simulation and retain its exact text."""
from dataclasses import dataclass, field
from pathlib import Path
import hashlib


@dataclass(frozen=True)
class Protocol:
    name: str = "female_no_v1"
    version: str = "1"
    conditions: tuple = ("virgin_song", "mated_song", "virgin_silence", "mated_silence")
    seeds: tuple = tuple(range(10))
    windows: int = 20
    warmup: int = 4
    window_ms: float = 50.0
    dt: float = 0.2
    predictions: str = ""
    chosen: tuple = ("amplitude=1", "mixture=0.7", "scale=1.0", "JO_MAX_HZ=180", "dt=0.2", "SAG candidate union")
    text: str = ""
    sha256: str = ""

    def __post_init__(self):
        if self.windows <= self.warmup or self.warmup < 0 or len(self.seeds) < 2 or len(set(self.seeds)) != len(self.seeds):
            raise ValueError("Need measurement windows and distinct paired seeds")
        if self.dt not in (0.1, 0.2) or self.window_ms != 50:
            raise ValueError("Unsupported timing")

    @classmethod
    def read(cls, path="experiments/female_no_v1.md", quick=False):
        raw = Path(path).read_bytes()
        text = raw.decode("utf-8")
        return cls(text=text, predictions=text.split("Predictions (registered before data):")[1].split("CHOSEN:")[0],
                   sha256=hashlib.sha256(raw).hexdigest(), seeds=(0, 1) if quick else tuple(range(10)),
                   windows=6 if quick else 20)
