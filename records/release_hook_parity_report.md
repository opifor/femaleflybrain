# Graded release parity report

Date: 2026-09-16. Baseline: `002da1d473017729c18889bddc8f3e9ffb91345e`.
Classification: diagnostic-class substitution, not an electrical synapse model.

## Acceptance environment

The requested CPython 3.12.14 runtime and supplied dependency environment were
used directly, without an environment substitution. Torch 2.6.0+cu124 ran on
an NVIDIA GeForce RTX 4090 with CUDA available. CPU backends used float64;
fast_gpu used its default float32. NumPy 2.4.2, SciPy 1.17.1, and pytest 9.1.1
were loaded. Bytecode writing and pytest's cache provider
were disabled. No machine-specific paths are embedded in this record.

Commands (with `python` denoting that runtime and its supplied PYTHONPATH):

```text
python -m pytest tests/test_release_hook.py -q -p no:cacheprovider
python -m pytest tests -q -rs -rx -p no:cacheprovider
python -c "import runpy; runpy.run_path('tests/test_release_hook.py', run_name='__main__')"
```

## Measured parity

Fixture: 4 neurons, 800 steps, dt=0.1 ms, source row 0, varying nonnegative
flux, positive and negative outgoing counts, intact non-source network edges.
The comparison covers every post-step `g`, not just the final value. Neuron
identities and order match across spike logs, so timestamp comparison is paired.

| Backend | Spikes | Max spike time difference vs lif (ms) | Max g difference vs lif |
| --- | ---: | ---: | ---: |
| lif | 16 | 0 | 0 |
| fast | 16 | 0 | 0 |
| fast_gpu, CUDA float32 | 16 | 0 | 0.00003006778224090567 |

Acceptance bounds: CPU g absolute error <1e-10; CUDA g absolute error <1e-4;
spike identities and times exact on this fixture. These are fixture-specific
measurements, not a universal guarantee near a firing threshold.

| Backend | Chunk steps | Max final g difference | Max v difference | Max ring difference | Max dropped-flux difference | Spike time difference (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| lif | 50 | 0 | 0 | 0 | 0 | 0 |
| lif | 256 | 0 | 0 | 0 | 0 | 0 |
| fast | 50 | 0 | 0 | 0 | 0 | 0 |
| fast | 256 | 0 | 0 | 0 | 0 | 0 |
| fast_gpu | 50 | 0 | 0 | 0 | 0 | 0 |
| fast_gpu | 256 | 0 | 0 | 0 | 0 | 0 |

Both chunk lengths use the same absolute flux sequence as the single call.
CPU equality is exact; measured CUDA float32 chunk error is also zero, and
tests require exact equality for this continuation fixture. A nonzero CPU/GPU
parity allowance is unnecessary for comparisons within the same backend here.

All three backends report source structural counts `[0]` and final scaled
source nonzero counts `[0]`. Other rows and incoming edges are preserved.

Cumulative dropped flux on the parity fixture, identical across backends:
`[0.0, 2382.5663710367858, 0.0, 199.4749518520806]` count-weighted
spike-equivalents. Independent forced-spike example: a target firing at step 0
rejects four arriving bins (steps 18..21), each of mass 0.1, giving 0.4 total;
step 22 accepts g=0.0275. Opposite signed inputs cancel g while both still
contribute to dropped mass (0.8 in the two-source test).

## Test evidence

Initial focused run: **46 passed**, exit 0, 11.78 s (before adding six further
source-output and signed-cancellation cases and one CSR storage case).
One Torch sparse CSR beta warning.

Harness negative control: `RELEASE_HOOK_FAILURE_PROBE=1` with only
`test_harness_failure_probe` selected produced **1 failed**, exit **1**, 0.27 s.
The pass/fail summary and process exit were both inspected.

The tests cover row removal and post-scaling checks, sealed-baseline disabled
regression (12 combinations), analytic convergence at two dt values, 5 ms and
256-step continuation, refractory accounting, signed cancellation, source
spike output suppression, jump rejection, absolute coverage, RNG independence,
invalid inputs, full trajectory parity, and CUDA batch continuation. Three
local-offset mutants are required to fail their numerical oracle.

Final full suite: **255 passed, 11 skipped, 3 xfailed**, exit **0**, 64.43 s.
All **53 hook tests passed** within that run; no hook case was skipped.
The three expected failures are the existing ear2 G3 adaptation, G5 continuous,
and G7 phase fixtures. The 11 skipped cases are excluded from acceptance
claims. The sole warning is Torch's existing sparse CSR beta warning.

The final changes also passed `git diff --check`; all seven delivery files
decoded as strict UTF-8 and had no UTF-8 BOM. Git status showed exactly the
seven authorized paths, and HEAD remained the baseline commit above.

## Scope and limitations

Only the authorized hook, simulator additions, tests, documentation, and this
record were changed. Git was read-only; no staging, commit, or push was run.
Excluded clean-room trees were not inspected; the expressly supplied dependency
directory was used only through PYTHONPATH for imports. No neuron equation,
parameter, drive mode, ear implementation, or experiment runner was changed.
The host-side CUDA hook has not been benchmarked at connectome scale.

## Scale cost (independent audit, 2026-09-16)

Measured on the FAFB female graph (n = 139,255, about 3.0 M edges), 500 steps on `fast_gpu`: 0.25 s without the hook, 0.72 s with a four-source hook (about 2.9 times). The cost comes from the per-step host synchronisation at the `active` mask transfer in `fast_gpu.py`; at n = 20,000 the difference is negligible (0.28 vs 0.27 s). The world loop's 5 ms cadence inherits this cost when the hook is enabled. Not a contract violation; recorded so that E5 budgets account for it.
