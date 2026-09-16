"""Passive, nonspiking B1 candidate. Nominal units; no network dependencies."""
from collections import deque
from dataclasses import asdict, dataclass
from itertools import product
import math

import numpy as np
from scipy.optimize import brentq, least_squares

CONDITIONS = ('WT', 'WT_block', 'shakB', 'shakB_block')
TARGETS = {'H1': 1.96, 'H3': .80, 'H4': .22}
SCALES = np.array([.30, .12, .08])


@dataclass(frozen=True)
class Parameters:
    g_gap: float = 1.
    g_chem: float = .35
    beta: float = .78
    d_ms: float = 1.5
    tau_m_ms: float = 2.
    tau_syn_ms: float = 1.5

    def __post_init__(self):
        if not all(math.isfinite(v) for v in asdict(self).values()):
            raise ValueError('Parameters must be finite')
        if min(self.g_gap, self.g_chem, self.d_ms) < 0:
            raise ValueError('Conductances and delay must be nonnegative')
        if not 0 <= self.beta <= 1 or min(self.tau_m_ms, self.tau_syn_ms) <= 0:
            raise ValueError('Invalid efficiency or time constant')


def conductances(p, condition):
    if condition not in CONDITIONS:
        raise ValueError('Unknown condition')
    gap = 0. if condition.startswith('shakB') else p.g_gap
    chem = p.g_chem * (1 - p.beta if condition.endswith('block') else 1.)
    return gap, chem


def release(voltage):
    """Fixed rectified-linear E5 hook; arbitrary release units, not Hz."""
    return np.maximum(voltage, 0.)


class RelayB1:
    """Exact passive propagation for a zero-order-held, delayed JO signal.

    Output sample n is V at the beginning of sample interval n. A call to
    process advances all states; separate trials require a new instance.
    """

    def __init__(self, parameters=Parameters(), *, dt_ms=.02, condition='WT'):
        if not math.isfinite(dt_ms) or dt_ms <= 0:
            raise ValueError('dt_ms must be positive and finite')
        self.p, self.dt_ms = parameters, dt_ms
        self.gap, self.chem = conductances(parameters, condition)
        delay = parameters.d_ms / dt_ms
        self.lag = math.floor(delay)
        self.fraction = delay - self.lag
        self.history = deque([0.] * (self.lag + 2), maxlen=self.lag + 2)
        self.s = self.v = 0.
        k = (1 + self.gap) / parameters.tau_m_ms
        q = 1 / parameters.tau_syn_ms
        self.a, self.b = math.exp(-q * dt_ms), math.exp(-k * dt_ms)
        self.direct = (self.gap + self.chem) / (1 + self.gap) * (-math.expm1(-k * dt_ms))
        cross = dt_ms * self.b if abs(k-q) < 1e-10 else (self.a-self.b)/(k-q)
        self.cross = self.chem / parameters.tau_m_ms * cross

    def process(self, jo=None, *, r_graded=None, channel=None):
        if (jo is None) == (r_graded is None):
            raise ValueError('Supply exactly one JO proxy or r_graded array')
        x = np.asarray(jo if jo is not None else r_graded, dtype=float)
        if r_graded is not None and x.ndim == 2:
            if not isinstance(channel, int) or not 0 <= channel < len(x):
                raise ValueError('Select an explicit r_graded channel')
            x = x[channel]
        elif channel is not None:
            raise ValueError('Channel selection requires a 2D r_graded array')
        if x.ndim != 1 or not np.all(np.isfinite(x)):
            raise ValueError('Input must be a finite 1D signal')
        v = np.empty(len(x))
        for i, value in enumerate(x):
            self.history.appendleft(float(value))
            u = ((1-self.fraction)*self.history[self.lag]
                 + self.fraction*self.history[self.lag+1])
            v[i] = self.v
            self.v = self.b*self.v + self.direct*u + self.cross*(self.s-u)
            self.s = self.a*self.s + (1-self.a)*u
        return {'V_B1': v, 'release': release(v)}


def step_voltage(t_ms, p, condition='WT'):
    """Continuous unit-step solution, used only by the fit observation model."""
    gap, chem = conductances(p, condition)
    t = np.maximum(np.asarray(t_ms, dtype=float)-p.d_ms, 0)
    k, q = (1+gap)/p.tau_m_ms, 1/p.tau_syn_ms
    cross = t*np.exp(-k*t) if abs(k-q) < 1e-10 else (np.exp(-q*t)-np.exp(-k*t))/(k-q)
    return (gap+chem)/(1+gap)*(-np.expm1(-k*t)) - chem/p.tau_m_ms*cross


def analytic_metrics(p):
    if min(p.g_gap+p.g_chem, p.g_chem) <= 0:
        raise ValueError('Matched control peaks must be positive')
    peak = (p.g_gap+p.g_chem)/(1+p.g_gap)
    latency = brentq(lambda t: float(step_voltage(t, p))-.1*peak,
                     p.d_ms, p.d_ms+1000*max(p.tau_m_ms, p.tau_syn_ms))
    return {'H1': latency,
            'H3': (p.g_gap+p.g_chem*(1-p.beta))/(p.g_gap+p.g_chem),
            'H4': 1-p.beta}


def joint_fit(*, targets=None, conditions=CONDITIONS):
    targets = TARGETS if targets is None else targets
    if set(targets) != set(TARGETS) or set(conditions) != set(CONDITIONS):
        raise ValueError('Joint H1/H3/H4 and all four conditions required; WT-only forbidden')
    y = np.array([targets[k] for k in TARGETS], dtype=float)
    if not np.all(np.isfinite(y)) or y[0] <= 0 or np.any((y[1:] <= 0) | (y[1:] >= 1)):
        raise ValueError('Invalid joint targets')
    def residual(values):
        m = analytic_metrics(Parameters(*values))
        return (np.array([m[k] for k in TARGETS])-y)/SCALES
    result = least_squares(residual, list(asdict(Parameters()).values()),
        bounds=([.01,.001,.01,0,.2,1], [30,30,.99,3,15,2]),
        xtol=1e-12, ftol=1e-12, gtol=1e-12, max_nfev=2000)
    p = Parameters(*result.x)
    return p, {'objective': float(result.fun @ result.fun), 'success': bool(result.success),
               'nfev': result.nfev, 'metrics': analytic_metrics(p)}


def sensitivity_grid(best_objective):
    rows = []
    for gap, fraction, beta, tau, syn in product(
            [.05,.2,1,5,20], [.64,.74,.84], [.70,.78,.86], [.5,1,2,5,10], [1,1.5,2]):
        p = Parameters(gap, gap*(1-fraction)/fraction, beta, 0, tau, syn)
        d = TARGETS['H1']-analytic_metrics(p)['H1']
        valid = 0 <= d <= 3
        if valid:
            p = Parameters(gap, p.g_chem, beta, d, tau, syn)
            m = analytic_metrics(p)
            loss = float(np.sum(((np.array(list(m.values()))-np.array(list(TARGETS.values())))/SCALES)**2))
        else:
            loss = None
        rows.append({'parameters': {**asdict(p), 'd_ms': d}, 'valid': valid, 'objective': loss,
                     'retained': valid and loss <= best_objective+1})
    accepted = [r['parameters'] for r in rows if r['retained']]
    ranges = {k: [min(r[k] for r in accepted), max(r[k] for r in accepted)]
              for k in asdict(Parameters())} if accepted else {}
    return rows, ranges


def sampled_metrics(p, dt_ms=.02):
    t = np.arange(round(210/dt_ms))*dt_ms
    x = (t >= 10).astype(float)
    traces = {c: RelayB1(p, dt_ms=dt_ms, condition=c).process(x)['V_B1'] for c in CONDITIONS}
    peaks = {c: float(v.max()) for c,v in traces.items()}
    v = traces['WT']
    threshold = .1*peaks['WT']
    i = int(np.flatnonzero(v >= threshold)[0])
    latency = t[i-1] + dt_ms*(threshold-v[i-1])/(v[i]-v[i-1])-10
    return {'H1': float(latency), 'H3': peaks['WT_block']/peaks['WT'],
            'H4': peaks['shakB_block']/peaks['shakB'], 'peaks_nominal_mV': peaks}, traces


def target_gates(metrics):
    return {f'E2-G{i+2}': abs(metrics[k]-TARGETS[k]) <= SCALES[i]
            for i,k in enumerate(TARGETS)}


def causal_checks(p):
    rng = np.random.default_rng(2201)
    x = rng.normal(size=2500)
    altered = x.copy()
    altered[1250:] = rng.normal(size=1250)
    a = RelayB1(p).process(x)['V_B1']
    b = RelayB1(p).process(altered)['V_B1']
    prefix = RelayB1(p).process(x[:1250])['V_B1']
    errors = []
    for boundaries in (list(range(0,2501,250)), [0,0,1,17,259,1000,1250,2499,2500]):
        model = RelayB1(p)
        chunks = np.concatenate([model.process(x[lo:hi])['V_B1'] for lo,hi in zip(boundaries,boundaries[1:])])
        errors.append(float(np.max(np.abs(a-chunks))))
    same = np.array_equal(a[:1250],b[:1250]) and np.array_equal(a[:1250],prefix)
    return {'prefix_bit_equal': same, 'chunk_max_errors': errors,
            'passed': same and max(errors)<1e-9}


def continuity_checks(p):
    # Absolute delay is aligned to a common .02-ms boundary for convergence;
    # this isolates membrane continuity from fractional-delay interpolation.
    aligned = Parameters(**{**asdict(p), 'd_ms': round(p.d_ms/.02)*.02})
    traces = [sampled_metrics(aligned, dt)[1]['WT'] for dt in (.02,.01,.005)]
    jumps = [float(np.max(np.abs(np.diff(v)))) for v in traces]
    errors = [float(np.max(np.abs(traces[0]-v[::stride]))) for v,stride in zip(traces[1:],(2,4))]
    return {'max_increments': jumps, 'aligned_max_errors': errors,
            'delay_alignment_ms': aligned.d_ms,
            'passed': jumps[1]<.75*jumps[0] and jumps[2]<.75*jumps[1] and max(errors)<1e-8}


def frequency_response(p):
    t = np.arange(25000)*.02/1000
    keep = t >= .3
    rows = []
    for f in range(100,601,100):
        phase = 2*np.pi*f*t
        v = RelayB1(p).process(np.sin(phase))['V_B1'][keep]
        design = np.column_stack((np.sin(phase[keep]),np.cos(phase[keep]),np.ones(keep.sum())))
        coefs = np.linalg.lstsq(design,v,rcond=None)[0]
        r2 = float(1-np.sum((v-design@coefs)**2)/np.sum((v-v.mean())**2))
        rows.append({'frequency_hz': f, 'amplitude_nominal_mV': float(np.hypot(*coefs[:2])),
                     'phase_rad': float(np.arctan2(coefs[1],coefs[0])), 'r_squared': r2})
    return {'rows': rows, 'passed': all(r['r_squared']>.99 and r['amplitude_nominal_mV']>1e-8 for r in rows),
            'interpretation': 'Descriptive forced phase locking only; no biological tuning validation'}
