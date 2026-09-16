# flybench

A small NumPy/SciPy simulator for signed connectome networks, with an optional
Torch backend. No connectome data are bundled. Parameters and equations follow
Shiu et al. (2024); see NOTICE and the source-line citations in sim/params.py.

The default `kernel="shiu"` integrates exactly between grid events:

```text
dv/dt = (v_rest - v + g) / tau_m
dg/dt = -g / tau_s
```

Voltage is in mV and time in ms. A spike adds signed synapse count times
0.275 mV to g after 1.8 ms. Both v and g freeze during the 2.2 ms refractory
period; incoming writes during that period are discarded. Spikes require
v > -45 mV and reset v to -52 mV and g to zero. The membrane and synaptic
time constants are 20 and 5 ms. dt is 0.1 ms by default, or 0.2 ms.

`kernel="jump"` is a comparison-only model: each spike adds its weight
directly to the postsynaptic voltage without filtering or delay. It is not
the Shiu synaptic model.

Each step integrates, applies drive, detects spikes, delivers network events,
then resets. Spike timestamps label the grid step; delayed g increments start
affecting voltage on the next integration. Jump increments occur immediately
in the delivery phase; threshold detection follows on the next step.

`Drive(..., mode="poisson")` uses the reference's N=1 grid Poisson input:
a Bernoulli draw with probability rate*dt/1000, a 250*w_syn voltage pulse,
and zero refractory period for driven neurons. `mode="bernoulli"` instead
sets eligible targets above threshold and preserves their refractory period.
Both allow at most one input per target per step and reject rates above grid
capacity. Inhibition can prevent delivery. Every result reports requested,
sampled, and delivered drive Hz per target; delivered means a sampled input
matched an actual spike. Total output rates also include network spikes.

```python
from scipy.sparse import csr_matrix
from flybench.sim import Simulator, Drive

network = Simulator(csr_matrix([[0, 100], [-10, 0]]),
                    drive=Drive((0,), 150), groups={"output": (1,)})
first = network.run(500, seed=7, spike_log=True)
second = network.run(500, state=first.state, spike_log=True)
print(second.group_rates_hz)
```

CSR rows are presynaptic neurons, columns are postsynaptic neurons, and values
are signed synapse counts. Results contain per-call counts and rates, group
counts and mean Hz per group neuron, overall mean Hz per neuron, and optional
(absolute time in ms, neuron index) spike tuples. State is mutated in place and
contains v, g, refractory eligibility steps, delay ring and cursor, absolute
step, and RNG. Resume with the same simulator; retain logs before continuation.

Install with `python -m pip install -e ".[test]"`, or `".[test,gpu]"` for Torch.
`flybench.sim.lif_gpu.Simulator` defaults to CUDA and also accepts `device="cpu"`.
It uses float64, the same host RNG, and ordered CSR updates for parity.
`run_batch(duration_ms, seeds=[7, 11])` returns independent seeded trials;
`states=[...]` resumes them. Trials are scheduled serially; this backend favors
reproducibility over throughput and synchronizes with the host each step.

Run `python -m pytest -q -p no:cacheprovider tests`.
CUDA checks skip when CUDA is unavailable. To verify failure propagation, set
`FLYBENCH_FAIL_PROBE=1` and run only `tests/test_lif.py::test_harness_failure_probe`;
the expected result is one failure and exit code 1. Unset it for acceptance.
