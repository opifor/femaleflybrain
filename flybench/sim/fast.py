"""Vectorized float64 delivery with a target-by-source SciPy CSR matrix."""
import math

import numpy as np

from .lif import Drive, State, Result, Simulator as ReferenceSimulator


class TorchDrive:
    """Seeded CPU Torch generator for paired NumPy/Torch drive experiments.

    Each trial owns its generator. CPU generation makes the stream independent
    of the simulation device; no NumPy randomness is used in this mode.
    """

    def __init__(self, seed):
        import torch
        self.generator = torch.Generator(device="cpu").manual_seed(int(seed))

    def random(self, size):
        import torch
        return torch.rand(size, generator=self.generator, dtype=torch.float64).numpy()


class Simulator(ReferenceSimulator):
    """Drop-in CPU backend; ``rng='torch'`` enables paired CUDA experiments.

    Weights remain signed counts. Scale entries before reduction, just as the
    reference scales each individual synapse before adding it to the target.
    """

    def __init__(self, weights, *, rng="numpy", **kwargs):
        if rng not in ("numpy", "torch"):
            raise ValueError("Unknown drive RNG")
        self.drive_rng = rng
        super().__init__(weights, **kwargs)
        self.delivery = self.weights.T.tocsr()
        self.delivery.data *= self.params.w_syn
        self.delivery.sort_indices()
        if self.release is not None:
            self.release.verify_scaled(self.delivery.indices, self.delivery.data)

    def initial_state(self, seed=0):
        state = super().initial_state(seed)
        if self.drive_rng == "torch":
            state.rng = TorchDrive(seed)
        return state

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
        target = self.targets
        for _ in range(steps):
            active = state.refr <= state.step
            state.v = np.where(active, p.v_rest + (state.v - p.v_rest) * self.em + state.g * self.coupling, state.v)
            state.g = np.where(active, state.g * self.es, state.g)
            fired_drive = np.zeros(len(target), dtype=bool)
            if self.drive:
                fired_drive = state.rng.random(len(target)) < self.drive.rate_hz * p.dt / 1000
                selected = target[fired_drive]
                sampled[selected] += 1
                if self.drive.mode == "poisson":
                    active[target] = True
                    state.v[selected] += p.w_syn * p.drive_scale
                else:
                    state.v[selected] = np.where(active[selected], p.v_th + 1.0, state.v[selected])
            fired = active & (state.v > p.v_th)
            counts += fired
            delivered[target] += fired[target] & fired_drive
            if log is not None:
                log.extend((state.step * p.dt, int(i)) for i in np.flatnonzero(fired))
            events = self.delivery @ fired.astype(np.float64)
            if self.kernel == "shiu":
                destination = (state.cursor + self.delay_steps) % len(state.delay_buffer)
                state.delay_buffer[destination] += events
                if self.release is not None:
                    state.delay_buffer[destination] += self.release.enqueue(
                        state, active, destination, p.dt, p.w_syn)
                state.g += np.where(active, state.delay_buffer[state.cursor], 0.0)
            else:
                state.v += np.where(active, events, 0.0)
            state.delay_buffer[state.cursor] = 0
            state.v[fired] = p.v_reset
            state.g[fired] = 0.0
            state.refr[fired] = state.step + round(p.refractory / p.dt)
            if self.drive and self.drive.mode == "poisson":
                state.refr[target] = 0
            state.step += 1
            state.cursor = (state.cursor + 1) % len(state.delay_buffer)
        seconds = duration_ms / 1000
        requested = np.zeros(self.n)
        if self.drive:
            requested[target] = self.drive.rate_hz
        group_counts = {k: int(counts[v].sum()) for k, v in self.groups.items()}
        group_rates = {k: group_counts[k] / seconds / len(v) if len(v) else 0.0
                       for k, v in self.groups.items()}
        return Result(state, counts, counts / seconds, float(counts.sum() / seconds / self.n),
                      group_counts, group_rates, requested, delivered / seconds,
                      sampled / seconds, log,
                      None if state.dropped_flux is None else state.dropped_flux.copy())


def benchmark():
    """Reproducible synthetic benchmark; run with ``python -m ...fast``.

    Setup is timed separately. Process peak memory includes graph generation
    and construction; CUDA peak memory includes resident sparse weights and
    simulation allocations. No files are written.
    """
    import argparse
    import ctypes
    import gc
    import json
    import platform
    import time
    from scipy.sparse import csr_matrix

    parser = argparse.ArgumentParser(description=benchmark.__doc__)
    parser.add_argument("--backend", choices=("cpu", "cuda"), required=True)
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--neurons", type=int, default=140000)
    parser.add_argument("--degree", type=int, default=350)
    parser.add_argument("--duration-ms", type=float, default=1000)
    args = parser.parse_args()
    if args.batch < 1 or args.neurons < 1000 or not 0 < args.degree < args.neurons:
        parser.error("Require batch >= 1, neurons >= 1000, and 0 < degree < neurons")
    if args.backend == "cpu" and args.batch != 1:
        parser.error("CPU benchmark supports one trial")
    started = time.perf_counter()
    rng = np.random.default_rng(20240916)
    nnz = args.neurons * args.degree
    # Uniform destinations with replacement; duplicates are coalesced by CSR.
    indices = rng.integers(0, args.neurons, nnz, dtype=np.int32)
    data = rng.integers(1, 101, nnz, dtype=np.int16)
    inhibitory = rng.random(nnz, dtype=np.float32) < 0.2
    data[inhibitory] *= -1
    del inhibitory
    weights = csr_matrix((data, indices, np.arange(0, nnz + 1, args.degree, dtype=np.int64)),
                         shape=(args.neurons, args.neurons))
    weights.sum_duplicates()
    weights.eliminate_zeros()
    edge_count = weights.nnz
    drive = Drive(tuple(range(1000)), 100)
    if args.backend == "cuda":
        import torch
        from .fast_gpu import Simulator as CudaSimulator
        torch.set_num_threads(1)
        sim = CudaSimulator(weights, drive=drive)
        name = torch.cuda.get_device_name(sim.device)
        # Initialize sparse kernels outside the measured interval.
        sim.run(0.1, seed=999)
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
    else:
        sim = Simulator(weights, drive=drive)
        name = platform.processor()
        sim.run(0.1, seed=999)
    del weights, data, indices
    gc.collect()
    setup_seconds = time.perf_counter() - started
    print(json.dumps(dict(stage="simulation", backend=args.backend, neurons=args.neurons,
                          edges=edge_count, batch=args.batch, setup_seconds=setup_seconds)), flush=True)
    started = time.perf_counter()
    if args.batch == 1:
        result = sim.run(args.duration_ms, seed=72)
    else:
        result = sim.run_batch(args.duration_ms, seeds=range(72, 72 + args.batch))
    if args.backend == "cuda":
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    if platform.system() == "Windows":
        from ctypes import wintypes

        class MemoryCounters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize",
                    "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(MemoryCounters), wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        counters = MemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        peak_bytes = counters.PeakWorkingSetSize
    else:
        import resource
        peak_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if platform.system() != "Darwin":
            peak_bytes *= 1024
    report = dict(backend=args.backend, device=name, neurons=args.neurons, edges=edge_count,
                  batch=args.batch, duration_ms=args.duration_ms, dt_ms=sim.params.dt,
                  seconds=elapsed, seconds_per_simulated_second=elapsed / (args.duration_ms / 1000),
                  seconds_per_trial_second=elapsed / (args.duration_ms / 1000 * args.batch),
                  process_peak_mib=peak_bytes / 2**20,
                  cuda_peak_allocated_mib=(torch.cuda.max_memory_allocated() / 2**20 if args.backend == "cuda" else None),
                  cuda_peak_reserved_mib=(torch.cuda.max_memory_reserved() / 2**20 if args.backend == "cuda" else None),
                  spikes=int(result.counts.sum()), mean_hz=np.asarray(result.total_hz_per_neuron).tolist(),
                  setup_seconds=setup_seconds)
    print(json.dumps(report, sort_keys=True), flush=True)


if __name__ == "__main__":
    benchmark()
