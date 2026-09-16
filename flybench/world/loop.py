"""Sensory evidence -> persistent brain -> command -> action -> contact.

Controllers receive immutable observations, never another controller or a log.
"""
from dataclasses import asdict
from types import SimpleNamespace
import numpy as np
import torch
from scipy.sparse import csr_matrix
from flybench.dictionary import groups
from flybench.dictionary.entries import entries
from flybench.sim.fast_gpu import Simulator
from flybench.sim.params import Parameters
from flybench import eye, scent, motor, ear
from flybench.song import Song, SAMPLE_RATE
from .arena import Arena
from . import constants as C


class _TargetRates:
    """Bridge backend sampling [time,target] and reporting [target,trial].

    Restricted to single-trial run; simulator source remains unchanged.
    """
    def __init__(self, rates):
        self.values = np.asarray(rates, dtype=float)

    def __mul__(self, factor):
        return torch.as_tensor(self.values, dtype=torch.float64) * factor

    def __array__(self, dtype=None, copy=None):
        return np.array(self.values[:, None], dtype=dtype, copy=True)


class Brain:
    """Own graph and state only; missing populations remain explicit in metadata."""
    def __init__(self, graph, dataset, seed=0, device="cuda", params=None):
        self.groups = groups(dataset, graph=graph)
        self.groups["pC1"] = np.unique(np.concatenate([self.groups["pC1"+s] for s in "abcde"]))
        for side in ("L", "R"):
            ids = self.groups["DNa02"]
            self.groups["DNa02_"+side] = ids[graph["side"][ids] == side]
        self.retina = eye.columns(graph, self.groups)
        n = len(graph["body_id"])
        weights = csr_matrix((graph["data"], graph["indices"], graph["indptr"]), shape=(n, n))
        self.sim = Simulator(weights, groups=self.groups, device=device, params=params or Parameters())
        targets = sorted(set(i for name in ("Or47b", C.CONTACT_GROUP, "L1", "L2", "JO-A", "JO-B") for i in self.groups[name]))
        self.sim.targets = np.asarray(targets, dtype=np.int64)
        self.sim.target = torch.as_tensor(self.sim.targets, device=self.sim.device)
        self.state = self.sim.initial_state(seed)
        self.metadata = {"dataset": dataset, "seed": seed,
                         "parameters": asdict(self.sim.params),
                         "missing_groups": [k for k, v in self.groups.items() if not len(v)],
                         "scent": next(e.to_dict() for e in entries(dataset) if e.name == "Or47b"),
                         "retina": [asdict(c) for c in self.retina]}

    def run(self, observation):
        chemical = scent.rates(observation)
        visual = eye.rates(observation, self.retina)
        wave = observation.sound or (0.0,) * round(SAMPLE_RATE*C.WINDOW_MS/1000)
        auditory = ear.rates(wave)
        counts = np.zeros(self.sim.n)
        for slot in range(round(C.WINDOW_MS / C.EAR_BIN_MS)):
            drive = np.zeros(self.sim.n)
            for name, hz in chemical.items():
                drive[self.groups[name]] += hz
            for neuron, hz in visual.items():
                drive[neuron] += hz
            for name, hz in auditory.items():
                drive[self.groups[name]] += hz[slot]
            selected = drive[self.sim.targets]
            if np.any(selected * self.sim.params.dt / 1000 > 1):
                raise ValueError("Combined sensory drive exceeds grid capacity")
            self.sim.drive = SimpleNamespace(mode="poisson", rate_hz=_TargetRates(selected))
            result = self.sim.run(C.EAR_BIN_MS, state=self.state)
            self.state = result.state
            counts += result.counts
        rates = counts / (C.WINDOW_MS/1000)
        readings = {name: float(rates[idx].mean()) if len(idx) else 0.0 for name, idx in self.groups.items()}
        return readings, {"scent_hz": chemical, "delivered_wave_rms": float(np.sqrt(np.mean(np.square(wave)))),
                          "drive_hz": {"chemical": chemical, "visual": visual,
                                       "auditory": {k: v.tolist() for k, v in auditory.items()}}}


class Loop:
    def __init__(self, male, female, seed=0):
        if male is female or male.sim is female.sim:
            raise ValueError("Two independent brains required")
        if male.sim.params.refractory <= 0:
            raise ValueError("Song amplitude requires positive refractory time")
        self.brains = (male, female)
        self.arena = Arena(seed)
        self.song = Song(amplitude=0)
        self.records = []
        self.metadata = {"chosen": C.chosen(), "geometry_seed": seed,
                         "brains": [b.metadata for b in self.brains],
                         "motor": "This is a motor map, not a measurement.",
                         "sound_delay_windows": 1, "female_song_hz": 0,
                         "ear": {"JO_MAX_HZ": ear.JO_MAX_HZ, "bands": ear.BANDS},
                         "song_sample_rate": SAMPLE_RATE}

    def step(self):
        observations = tuple(self.arena.observe(i) for i in (0, 1))
        results = [b.run(o) for b, o in zip(self.brains, observations)]
        readings = [r[0] for r in results]
        commands = [motor.command(r) for r in readings]
        male = readings[0]
        ceiling = 1000 / self.brains[0].sim.params.refractory
        self.song.amplitude = float(np.clip(male["pIP10"] / ceiling, 0, 1))
        pulse, sine = male[C.PULSE_GROUP], male[C.SINE_GROUP]
        self.song.mixture = pulse/(pulse+sine) if pulse+sine > 0 else 0.0
        wave = self.song.window(C.WINDOW_MS/1000)
        if pulse+sine == 0:
            wave[:] = 0  # No fabricated song mode when motor evidence is absent.
        self.arena.advance(commands, wave)
        record = {"window": len(self.records), "time_ms": (len(self.records)+1)*C.WINDOW_MS,
                  "bodies": [asdict(b) for b in self.arena.bodies],
                  "distance": self.arena.observe(0).distance,
                  "contact": self.arena.observe(0).contact,
                  "observations": [asdict(o) for o in observations],
                  "commands": [asdict(c) for c in commands],
                  "sensory": [r[1] for r in results],
                  "female": {k: readings[1][k] for k in ("vpoDN", "pC1")},
                  "male": {k: male[k] for k in ("P1", "pIP10", "LC10a", "DNa02", "DNa02_L", "DNa02_R")},
                  "song": {"amplitude": self.song.amplitude, "pulse_fraction": self.song.mixture,
                           "emitted_rms": float(np.sqrt(np.mean(wave**2))), "female_song_hz": 0}}
        self.records.append(record)
        return record

    def run(self, windows):
        if not isinstance(windows, int) or windows < 1:
            raise ValueError("Expected a positive window count")
        return [self.step() for _ in range(windows)]
