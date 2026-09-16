"""Exact subthreshold integration with deterministic, grid-based events."""
from dataclasses import dataclass
import math
import numpy as np
from scipy.sparse import csr_matrix
from .params import Parameters


@dataclass(frozen=True)
class Drive:
    targets: tuple[int, ...]
    rate_hz: float
    mode: str = "poisson"


@dataclass
class State:
    v: object
    refr: object
    g: object
    delay_buffer: object
    cursor: int
    rng: np.random.Generator
    step: int = 0
    owner: object = None
    release_pending: object = None
    dropped_flux: object = None


@dataclass
class Result:
    state: State
    counts: np.ndarray
    rates_hz: np.ndarray
    total_hz_per_neuron: float
    group_counts: dict
    group_rates_hz: dict
    requested_hz: np.ndarray
    delivered_hz: np.ndarray
    sampled_drive_hz: np.ndarray
    spikes: list | None
    dropped_flux: np.ndarray | None = None


class Simulator:
    """CSR entries are signed synapse counts: row=source, column=target.

    Each step integrates, applies external drive, detects spikes, delivers
    network events, then resets. Synaptic writes to refractory targets are
    suppressed, matching the source's conditional state variables.
    """

    def __init__(self, weights, *, params=None, kernel="shiu", drive=None,
                 groups=None, release=None):
        self.params = params or Parameters()
        if kernel not in ("shiu", "jump"):
            raise ValueError("Unknown kernel")
        self.kernel = kernel
        self.weights = csr_matrix(weights, dtype=np.float64, copy=True)
        self.weights.sum_duplicates()
        self.weights.sort_indices()
        self.n = self.weights.shape[0]
        if self.weights.shape != (self.n, self.n) or self.n == 0:
            raise ValueError("Weights must be nonempty and square")
        if not np.isfinite(self.weights.data).all():
            raise ValueError("Weights must be finite")
        self.release = None
        if release is not None:
            if kernel != "shiu":
                raise ValueError("Graded release requires the shiu kernel")
            self.weights, self.release = release.bind(self.weights)
        self.drive = drive
        self.targets = self._indices(drive.targets if drive else ())
        if drive and (drive.mode not in ("poisson", "bernoulli") or
                      not math.isfinite(drive.rate_hz) or
                      not 0 <= drive.rate_hz * self.params.dt / 1000 <= 1):
            raise ValueError("Invalid drive mode or rate outside grid capacity")
        self.groups = {k: self._indices(v) for k, v in (groups or {}).items()}
        self.delay_steps = round(self.params.delay / self.params.dt)
        self.em = math.exp(-self.params.dt / self.params.tau_m)
        self.es = math.exp(-self.params.dt / self.params.tau_s)
        self.coupling = self.params.tau_s / (self.params.tau_m - self.params.tau_s) * (self.em - self.es)
        if self.release is not None:
            self.release.verify_scaled(
                np.repeat(np.arange(self.n), np.diff(self.weights.indptr)),
                self.weights.data * self.params.w_syn)

    def _indices(self, values):
        raw = np.asarray(tuple(values))
        if raw.size and (raw.dtype.kind not in "iu" or
                         np.any(raw < 0) or np.any(raw >= self.n)):
            raise ValueError("Invalid neuron indices")
        result = raw.astype(np.int64)
        if len(np.unique(result)) != len(result):
            raise ValueError("Duplicate neuron indices")
        return result

    def _array(self, value):
        return np.array(value, copy=True)

    def _numpy(self, value):
        return np.asarray(value)

    def _where(self, condition, yes, no):
        return np.where(condition, yes, no)

    def initial_state(self, seed=0):
        return State(self._array(np.full(self.n, self.params.v_rest)),
                     self._array(np.zeros(self.n, dtype=np.int64)),
                     self._array(np.zeros(self.n)),
                     self._array(np.zeros((self.delay_steps + 1, self.n))),
                     0, np.random.default_rng(seed), owner=self)

    def run(self, duration_ms, *, state=None, seed=0, spike_log=False):
        p = self.params
        if not math.isfinite(duration_ms) or duration_ms <= 0:
            raise ValueError("Duration must be positive and finite")
        steps = round(duration_ms / p.dt)
        if not math.isclose(steps * p.dt, duration_ms, abs_tol=1e-10):
            raise ValueError("Duration must be an integer number of steps")
        state = self.initial_state(seed) if state is None else state
        if state.owner is not self:
            raise ValueError("State belongs to another simulator")
        if self.release is not None:
            self.release.validate_run(state, steps)
        counts = np.zeros(self.n, dtype=np.int64)
        sampled = np.zeros(self.n, dtype=np.int64)
        delivered = np.zeros(self.n, dtype=np.int64)
        log = [] if spike_log else None
        target = self._array(self.targets)
        for _ in range(steps):
            active = state.refr <= state.step
            state.v = self._where(active, p.v_rest + (state.v - p.v_rest) * self.em + state.g * self.coupling, state.v)
            state.g = self._where(active, state.g * self.es, state.g)
            fired_drive = np.zeros(len(self.targets), dtype=bool)
            if self.drive:
                # N=1 PoissonInput has a Bernoulli rate*dt draw on the grid.
                fired_drive = state.rng.random(len(self.targets)) < self.drive.rate_hz * p.dt / 1000
                selected = self._array(self.targets[fired_drive])
                sampled[self.targets[fired_drive]] += 1
                if self.drive.mode == "poisson":
                    active[target] = True
                    state.v[selected] += p.w_syn * p.drive_scale
                else:
                    eligible = active[selected]
                    state.v[selected] = self._where(eligible, p.v_th + 1.0, state.v[selected])
            fired = self._numpy(active & (state.v > p.v_th)).astype(bool)
            ids = np.flatnonzero(fired)
            counts += fired
            delivered[self.targets] += fired[self.targets] & fired_drive
            if log is not None:
                log.extend((state.step * p.dt, int(i)) for i in ids)
            # Ordered CSR row updates avoid nondeterministic parallel reductions.
            destination = (state.cursor + self.delay_steps) % len(state.delay_buffer)
            for source in ids:
                lo, hi = self.weights.indptr[source:source + 2]
                cols = self._array(self.weights.indices[lo:hi].astype(np.int64))
                values = self._array(self.weights.data[lo:hi] * p.w_syn)
                if self.kernel == "shiu":
                    state.delay_buffer[destination, cols] += values
                else:
                    state.v[cols] += self._where(active[cols], values, values * 0)
            if self.kernel == "shiu":
                if self.release is not None:
                    state.delay_buffer[destination] += self.release.enqueue(
                        state, active, destination, p.dt, p.w_syn)
                state.g += self._where(active, state.delay_buffer[state.cursor], state.g * 0)
            state.delay_buffer[state.cursor] = 0
            index = self._array(ids)
            state.v[index] = p.v_reset
            state.g[index] = 0.0
            state.refr[index] = state.step + round(p.refractory / p.dt)
            if self.drive and self.drive.mode == "poisson":
                state.refr[target] = 0
            state.step += 1
            state.cursor = (state.cursor + 1) % len(state.delay_buffer)
        seconds = duration_ms / 1000
        requested = np.zeros(self.n)
        if self.drive:
            requested[self.targets] = self.drive.rate_hz
        group_counts = {k: int(counts[v].sum()) for k, v in self.groups.items()}
        group_rates = {k: group_counts[k] / seconds / len(v) if len(v) else 0.0
                       for k, v in self.groups.items()}
        return Result(state, counts, counts / seconds, float(counts.sum() / seconds / self.n),
                      group_counts, group_rates, requested, delivered / seconds,
                      sampled / seconds, log,
                      None if state.dropped_flux is None else state.dropped_flux.copy())
