"""Torch float64 backend; shared scheduling and host RNG ensure seed parity."""
import torch
from .lif import Simulator as NumpySimulator


class Simulator(NumpySimulator):
    def __init__(self, weights, *, device="cuda", **kwargs):
        self.device = torch.device(device)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA is unavailable")
        super().__init__(weights, **kwargs)

    def _array(self, value):
        return torch.as_tensor(value.copy(), device=self.device)

    def _numpy(self, value):
        return value.detach().cpu().numpy()

    def _where(self, condition, yes, no):
        return torch.where(condition, yes, no)

    def run_batch(self, duration_ms, *, seeds=None, states=None, spike_log=False):
        """Return independent trials in order; batches are scheduled serially."""
        if (seeds is None) == (states is None):
            raise ValueError("Supply exactly one of seeds or states")
        if states is not None:
            return [self.run(duration_ms, state=s, spike_log=spike_log) for s in states]
        return [self.run(duration_ms, seed=s, spike_log=spike_log) for s in seeds]
