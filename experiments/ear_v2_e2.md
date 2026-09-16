# E2 preregistration: passive AMMC-B1 candidate relay

Frozen before model implementation and fitting, 2026-09-16. Budget 45 minutes.
Task A precedes this freeze: ledger 1.2 appends R3_009--R3_012 with operator
full-text evidence. R3_003 and every prior record remain unchanged. The supplied
quotes are transcribed verbatim; no independent full-text verification claimed.
The task authorizes this fit despite unchanged snapshot fit_allowed policies.

## Model and observation contract

No graphs, network simulation or imports of flybench.graph, dictionary, world,
experiment. No graph npz/parquet/feather file reads. A runtime guard in the
isolated runner rejects those imports and file opens. Tests prove rejection.
No edits outside the task allowlist; no git writes. Raw scripts and arrays only
under build/records-raw. Initial build directory was absent.

Voltage is deviation from resting voltage in nominal mV. Fix leak g_L=1 nS
as an arbitrary gauge and C=tau_m*g_L in pF; neither R nor C is in ledger.
C*dV/dt = -g_L*V + g_gap*(x_delayed-V) + g_chem_eff*s.
tau_syn*ds/dt=x_delayed-s. JO unit amplitude maps to nominal 1 mV; this
mapping and all absolute voltages are uncalibrated, amplitude held out.
g_gap and g_chem are nominal nS under this convention. Chemical drive s has
nominal mV units. Common delay d precedes both paths. Exact two-state
zero-order-hold propagation, causal linear fractional-sample delay, persistent
filter/membrane/delay state; output at sample boundaries before propagation.
All states start at zero. Empty and irregular chunks must preserve state.
Input is a finite 1D synthetic JO proxy or explicit E1 r_graded channel (2D
channel arrays require channel selection). No E1 package import needed.
release=max(V,0), fixed slope 1 arbitrary release unit/mV; no scale fit or
E5 connection. No spike threshold, resets, noise or spike generation.

Conditions: WT (both paths); WT_block (chemical times 1-beta); shakB (gap=0);
shakB_block (gap=0, chemical times 1-beta). Block efficiency beta is fitted,
not complete chemical deletion. For a long step H4=1-beta, and H3=
(g_gap+g_chem*(1-beta))/(g_gap+g_chem); electrical loading cancels within
matched WT ratios. These formulas guide interpretation, not substitute tests.

Synthetic step onset 10 ms, duration 200 ms, dt=0.02 ms; unit amplitude.
Exact experimental step amplitude/duration and blockade analysis window:
not in ledger. Supplementary R3_004 sweep amplitudes are not substituted.
Latency maps onset to 10% WT peak (an explicit observation-model assumption;
the original physiological latency estimator is not established here).
Frequency diagnostic: 100,200,300,400,500,600 Hz unit sine, 500 ms, final
200 ms; least-squares sine/cosine/DC estimate amplitude, phase and R-squared.

## Joint fit and uncertainty

Targets H1=1.96 ms (reported spread .05 ms, n=24), H3=.80 (spread .06),
H4=.22 (spread .04). Objective sum of squared residuals scaled respectively
by .30,.12,.08. No absolute mV fitting. H2 physiological jitter .21+/-.02 ms
(n=24) is unassessed: deterministic repeat jitter=0, not a biological match.
H5 no spikes is structural, supported by R3_011 (17 recordings).
Only joint calls containing H1,H3,H4 and all four conditions are accepted;
WT-only fit calls raise ValueError.

Joint least squares over g_gap,g_chem,beta,d,tau_m,tau_syn. Bounds respectively
[.01,30],[.001,30],[.01,.99],[0,3],[.2,15],[1,2]. Initial values
[1,.35,.78,1.5,2,1.5] are design choices, not Azevedo model constants.
R, C and tau_syn constants: not in ledger; tau_syn is free in [1,2] ms.
Use exact analytical step trajectory and scalar root at 10% asymptote for
optimization; verify finite-window sampled measurements afterward. No target
or tolerance changes after freeze. Three observations cannot identify six
parameters; fitting success is conditional compatibility only.

Sensitivity grid: gap=[.05,.2,1,5,20], gap fraction=[.64,.74,.84],
beta=[.70,.78,.86], tau_m=[.5,1,2,5,10], tau_syn=[1,1.5,2].
Set chem=gap*(1-fraction)/fraction; profile d=1.96-undelayed 10% latency,
retain only d within [0,3]. Report ranges across grid candidates with
objective<=joint_minimum+1, plus all grid points in raw JSON. These are
grid sensitivity ranges, NOT confidence intervals (güven aralığı değil).
No bootstrap cells are fabricated; no frequency diagnostic enters loss.

## Gates and tests

E2-G1: altered-future prefix and prefix-alone bit equality (seed 2201);
whole/chunk max error <1e-9 on 50 ms Gaussian proxy, 5 ms and irregular chunks.
E2-G2: |sampled latency-1.96|<=.30 ms.
E2-G3: |WT_block peak/WT peak-.80|<=.12.
E2-G4: |shakB_block peak/shakB peak-.22|<=.08.
E2-G5: continuous passive trajectory: halving dt from .02 to .01 and .005 ms
must reduce maximum adjacent WT step increments (ratios <.75); aligned
trajectories max error <1e-8 at common boundaries. A threshold/reset jump
breaks this test. This is a structural/numerical check, not spike physiology.
E2-G6: descriptive phase locking: all six sine regressions R-squared>.99
and amplitude>1e-8 nominal mV. Forced deterministic locking is not biological
frequency-tuning validation. Report amplitudes and phases without fit.
Failed gates stay 'not passed' with reasons. If H3/H4 cannot jointly pass,
report explicitly that the E5 no-go trigger is active.

Run isolated pytest before fit: causality/chunks, WT-only rejection, all
prohibited import rejections, analytical-vs-sampled gates, continuous response,
release mapping and invalid inputs. Intentional-fail probe must show one
failed test and nonzero exit; passing harness requires count line and exit 0.

## Delivery and limitations

Freeze preregistration and ledger SHA-256 before model code. Record environment,
portable commands, accessed files, guard denials, no graph reads, timing and
UTF-8 without BOM. Exact authorized interpreter/dependency chain is used;
dependency resolution is the sole authorized use of the supplied site-packages
location, with no source-tree inspection. Record paths relative to repository
or runtime labels, never host paths. Locale C, no bytecode/plugin autoload/cache.
conditional_on: E1 bank not fitted; E1 G3/G5 open. Synthetic proxy fit does
not certify E1 integration or E5 readiness. Summary records <=2 MB.
