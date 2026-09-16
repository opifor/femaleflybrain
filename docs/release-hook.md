# Graded release hook

This is a diagnostic-class substitution, not an electrical synapse model.
The caller computes the voltage-to-release law. The hook accepts its output;
it does not compute voltage, clip release, set a ceiling, or sample randomness.
Neuron equations, parameters, connectivity destinations, existing drive modes,
Shiu delay, and the synaptic filter are unchanged.

```python
from flybench.sim.lif import Simulator
from flybench.sim.release import GradedRelease

release = GradedRelease(source_rows=[0], flux=[[0.2], [0.4], [0.1]])
sim = Simulator([[0, 3], [1, 0]], kernel="shiu", release=release)
head = sim.run(0.1)
tail = sim.run(0.2, state=head.state)
```

The same `release=` argument is accepted by `fast.Simulator` and
`fast_gpu.Simulator`. Omission and `release=None` retain the original path.
Passing a hook to the jump kernel raises `ValueError` before simulation.

## Inputs and installation

`source_rows` is a one-dimensional array of unique, in-range integer source
indices. `flux` is a finite, nonnegative array of shape `[T_steps, n_source]`,
in spike-equivalents per millisecond. Time and `dt` use milliseconds. No
particular voltage-to-release function is imposed.

The constructor copies and canonicalizes the supplied final graph, whose CSR
rows are sources and columns are targets. Installation retains the original
signed outgoing rows in `sim.release.original_rows`, zeros their data, and
removes their stored entries. Other rows are identical, including incoming
edges to source cells from other neurons. A source self-edge is an outgoing
edge and is therefore removed as well. The caller's graph and unbound hook
are not modified; each simulator owns a bound hook copy.

`sim.release.counts` contains structural outgoing entry counts after removal:
`counts[source_rows] == 0`. `scaled_source_counts` repeats the zero check on
the final delivery data after `w_syn` scaling, including the actual resident
Torch CSR values. Construction raises if this invariant fails. The parity
record includes both checks. These counts are graph counts, distinct from
`Result.counts`: source neurons still integrate, receive input, and may spike,
but their ordinary network output is inert.

## Scheduling and continuation

At each absolute `state.step`, for each saved signed edge count `c`, the hook
adds `c * w_syn * flux[state.step, source] * dt` to the ordinary destination
slot of the delay ring. It uses the existing Shiu delivery eligibility mask,
including existing drive semantics. The default delay is 1.8 ms and the
default filter time constant is 5 ms. Delivery and reset order are unchanged:
integrate, drive, detect spikes, enqueue, deliver to eligible targets, reset.
A write to a neuron firing on the current step is followed by the ordinary
reset; that reset is not a refractory drop.

Flux uses absolute time, never a local run or chunk offset. Keep the returned
state when calling `run` again (for example every 5 ms); provide one flux table
covering the entire timeline. The existing simulator ownership check applies
to resumed states. Insufficient flux coverage raises before any state update.
Torch's 256-step drive chunks do not change release indexing. GPU batches
broadcast the same supplied flux to every trial column; per-trial refractory
eligibility and dropped mass remain independent.

## Dropped flux

`Result.dropped_flux` is a snapshot of cumulative dropped release from the
start of the state, shaped `[n]` or `[n, batch]`. It is `None` with the hook
disabled. It sums `abs(c) * flux * dt` for each release event whose target is
refractory when that event arrives, in count-weighted spike-equivalents.
Multiplication by `w_syn` converts this mass to absolute synaptic increment
units. Excitatory and inhibitory contributions cannot cancel this counter.
Only hook traffic is counted; ordinary network or drive traffic is excluded.
Pending release mass has a separate ring in the state so attribution survives
continuation and accounts for the eligibility at arrival, not at enqueue.
As these counters are cumulative, do not sum snapshots from successive calls.

For `c=2`, `F=0.5`, `dt=0.1`, each arriving event carries 0.1 spike-equivalents.
A target firing at step 0 rejects arrivals at steps 18 through 21, producing
`dropped_flux[target] = 0.4`; step 22 accepts an increment of 0.0275.

## Analytic and numerical validation

For one non-firing target receiving constant flux, write `q=c*w_syn*F`,
`a=exp(-dt/tau_s)`, and `m=steps-delay_steps`. After `m` arrivals the exact
discrete recurrence gives `g_grid=q*dt*(1-a**m)/(1-a)`. Compare it to the
continuous-flow endpoint `g_cont=q*tau_s*(1-exp(-m*dt/tau_s))`. This endpoint
aligns the delivered bins; the first bin arrives at `delay_steps`.
The exact quadrature error is
`g_cont * ((dt/tau_s)/(1-exp(-dt/tau_s))-1)`, approximately
`g_cont*dt/(2*tau_s)`. Tests use this derived error bound, with rounding
allowance 1e-12 for float64 or 2e-6 for CUDA float32, and require halving `dt`
from 0.2 to 0.1 ms to reduce error by at least a factor of 1/0.51.

The parity fixture checks every post-step `g` over 800 steps on a signed
four-neuron graph with varying flux and actual spikes. Its float64 tolerance
is 1e-10 and float32 tolerance is 1e-4; observed differences are recorded in
`records/release_hook_parity_report.md`. Continuation compares full state,
spike logs, pending mass, and dropped mass for 50- and 256-step chunks.
A deliberately substituted modulo-50 index is rejected by the continuation
oracle on all three backends. Disabled-path tests also compare the sealed
pre-hook implementation, loaded in memory from git, against both omission
and explicit `None` for both kernels and both drive modes.

The diagnostic CUDA hook currently assembles its release vectors and mass
accounting in float64 on the host, then transfers release increments to the
simulation dtype. Eligibility is read back per step. This favors auditable
parity over throughput; performance at connectome scale has not been measured.
