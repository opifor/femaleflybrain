"""Torch CSR delivery for simultaneous, independently seeded trial columns."""
import math

import numpy as np
import torch

from .fast import Drive, State, Result, TorchDrive
from .lif import Simulator as ReferenceSimulator


class Simulator(ReferenceSimulator):
    """Float32 sparse matrix/dense batch multiplication, with no spike loop.

    ``run`` follows the reference's one-trial contract. ``run_batch`` returns
    one Result whose neuron arrays have shape [n, B], state ring [delay+1,n,B],
    total/group statistics [B], and optional list of B spike logs. Resume a
    batch with ``run_batch(..., state=result.state)``. Each column owns a CPU
    Torch generator; its stream is invariant to batching and continuation.
    """

    def __init__(self, weights, *, device="cuda", dtype=torch.float32, **kwargs):
        self.device = torch.device(device)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA is unavailable")
        if dtype not in (torch.float32, torch.float64):
            raise ValueError("dtype must be float32 or float64")
        self.dtype = dtype
        super().__init__(weights, **kwargs)
        delivery = self.weights.T.tocsr()
        delivery.sort_indices()
        self.delivery = torch.sparse_csr_tensor(
            torch.as_tensor(delivery.indptr, device=self.device),
            torch.as_tensor(delivery.indices, device=self.device),
            torch.as_tensor(delivery.data * self.params.w_syn, dtype=dtype, device=self.device),
            size=delivery.shape, device=self.device)
        self.target = torch.as_tensor(self.targets, device=self.device)

    def initial_state(self, seed=0):
        return self._initial((seed,), single=True)

    def initial_batch_state(self, seeds):
        seeds = tuple(seeds)
        if not seeds:
            raise ValueError("Supply at least one seed")
        return self._initial(seeds, single=False)

    def _initial(self, seeds, single):
        shape = (self.n,) if single else (self.n, len(seeds))
        rng = tuple(TorchDrive(seed) for seed in seeds)
        return State(torch.full(shape, self.params.v_rest, dtype=self.dtype, device=self.device),
                     torch.zeros(shape, dtype=torch.int64, device=self.device),
                     torch.zeros(shape, dtype=self.dtype, device=self.device),
                     torch.zeros((self.delay_steps + 1, *shape), dtype=self.dtype, device=self.device),
                     0, rng[0] if single else rng, owner=self)

    def run(self, duration_ms, *, state=None, seed=0, spike_log=False):
        state = self.initial_state(seed) if state is None else state
        if state.v.ndim != 1:
            raise ValueError("Use run_batch for a batch state")
        return self._run(duration_ms, state, spike_log)

    def run_batch(self, duration_ms, *, seeds=None, state=None, spike_log=False):
        if (seeds is None) == (state is None):
            raise ValueError("Supply exactly one of seeds or state")
        state = self.initial_batch_state(seeds) if state is None else state
        if state.v.ndim != 2:
            raise ValueError("Batch state must have shape [n, B]")
        return self._run(duration_ms, state, spike_log)

    @torch.no_grad()
    def _run(self, duration_ms, state, spike_log):
        p = self.params
        if not math.isfinite(duration_ms) or duration_ms <= 0:
            raise ValueError("Duration must be positive and finite")
        steps = round(duration_ms / p.dt)
        if not math.isclose(steps * p.dt, duration_ms, abs_tol=1e-10):
            raise ValueError("Duration must be an integer number of steps")
        if state.owner is not self:
            raise ValueError("State belongs to another simulator")
        single = state.v.ndim == 1
        v = state.v[:, None] if single else state.v
        g = state.g[:, None] if single else state.g
        refr = state.refr[:, None] if single else state.refr
        ring = state.delay_buffer[..., None] if single else state.delay_buffer
        generators = (state.rng,) if single else state.rng
        batch = v.shape[1]
        counts = torch.zeros_like(refr)
        sampled = torch.zeros((len(self.targets), batch), dtype=torch.int64, device=self.device)
        delivered = torch.zeros_like(sampled)
        logs = [[] for _ in range(batch)] if spike_log else None
        # Bounded chunks avoid a duration-sized drive allocation. Each stream
        # consumes step-major samples, including across continuation boundaries.
        chunk_size = 256
        draws = None
        for offset in range(steps):
            if self.drive and offset % chunk_size == 0:
                length = min(chunk_size, steps - offset)
                draws = torch.stack([
                    torch.rand((length, len(self.targets)), generator=rng.generator,
                               dtype=torch.float64) < self.drive.rate_hz * p.dt / 1000
                    for rng in generators], dim=2).to(self.device)
            active = refr <= state.step
            v = torch.where(active, p.v_rest + (v - p.v_rest) * self.em + g * self.coupling, v)
            g = torch.where(active, g * self.es, g)
            if self.drive:
                fired_drive = draws[offset % chunk_size]
                sampled += fired_drive
                tv = v[self.target]
                if self.drive.mode == "poisson":
                    active[self.target] = True
                    v[self.target] = tv + fired_drive.to(self.dtype) * (p.w_syn * p.drive_scale)
                else:
                    v[self.target] = torch.where(fired_drive & active[self.target], p.v_th + 1.0, tv)
            fired = active & (v > p.v_th)
            counts += fired
            if self.drive:
                delivered += fired[self.target] & fired_drive
            if logs is not None:
                for neuron, column in fired.nonzero().cpu().tolist():
                    logs[column].append((state.step * p.dt, neuron))
            events = torch.sparse.mm(self.delivery, fired.to(self.dtype))
            if self.kernel == "shiu":
                destination = (state.cursor + self.delay_steps) % len(ring)
                ring[destination] += events
                g += torch.where(active, ring[state.cursor], 0.0)
            else:
                v += torch.where(active, events, 0.0)
            ring[state.cursor].zero_()
            v.masked_fill_(fired, p.v_reset)
            g.masked_fill_(fired, 0.0)
            refr.masked_fill_(fired, state.step + round(p.refractory / p.dt))
            if self.drive and self.drive.mode == "poisson":
                refr[self.target] = 0
            state.step += 1
            state.cursor = (state.cursor + 1) % len(ring)
        state.v = v[:, 0] if single else v
        state.g = g[:, 0] if single else g
        seconds = duration_ms / 1000
        counts = counts.cpu().numpy()
        sampled_full = np.zeros((self.n, batch))
        delivered_full = np.zeros_like(sampled_full)
        requested = np.zeros_like(sampled_full)
        sampled_full[self.targets] = sampled.cpu().numpy() / seconds
        delivered_full[self.targets] = delivered.cpu().numpy() / seconds
        if self.drive:
            requested[self.targets] = self.drive.rate_hz
        if single:
            counts, sampled_full, delivered_full, requested = (
                a[:, 0] for a in (counts, sampled_full, delivered_full, requested))
        group_counts = {k: counts[idx].sum(axis=0) for k, idx in self.groups.items()}
        if single:
            group_counts = {k: int(value) for k, value in group_counts.items()}
        group_rates = {k: group_counts[k] / seconds / len(idx) if len(idx) else
                       (0.0 if single else np.zeros(batch)) for k, idx in self.groups.items()}
        total = counts.sum(axis=0) / seconds / self.n
        return Result(state, counts, counts / seconds, float(total) if single else total,
                      group_counts, group_rates, requested, delivered_full, sampled_full,
                      (logs[0] if single else logs) if logs is not None else None)
