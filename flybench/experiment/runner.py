"""Run paired conditions using the existing fast_gpu batch engine."""
import argparse
from dataclasses import asdict
import time
from pathlib import Path
import numpy as np
import torch
from scipy.sparse import csr_matrix
from flybench.graph import load, where
from flybench.dictionary import groups as dictionary_groups
from flybench.sim.fast_gpu import Simulator, Drive
from flybench.sim.params import Parameters
from flybench.song import Song
from flybench.ear import rates, RMS_FULL, JO_MAX_HZ
from .protocol import Protocol
from .record import sha256, environment, write
from .report import write_from_json


class BatchRates:
    """Bridge step-by-target sampling and target-by-batch result layouts."""
    def __init__(self, values, dt):
        self.values = np.asarray(values, dtype=np.float64).reshape(-1)
        if not np.isfinite(self.values).all() or np.any(self.values < 0) or np.any(self.values*dt/1000 > 1):
            raise ValueError("Drive outside grid capacity")

    def __mul__(self, scalar):
        return torch.from_numpy(self.values)*scalar

    def __array__(self, dtype=None, copy=None):
        return np.array(self.values[:, None], dtype=dtype, copy=True)


def select_groups(graph):
    base = dictionary_groups("female", graph=graph)
    selected = {k: base[k] for k in ("JO-A", "JO-B")}
    selected.update(SAG=where(graph, type_re=r"^(?:AN_SMP_2|AN_FLA_SMP_2|ANXXX983)$"),
                    pC1=where(graph, type_re=r"^pC1[a-e]$"),
                    vpoDN=where(graph, type_re=r"^DNp37$"))
    if any(len(v) == 0 for v in selected.values()):
        raise ValueError("Required protocol group is absent")
    return selected


def run(protocol, graph, groups, *, device="cuda", graph_sha="synthetic", progress=False):
    start = time.perf_counter()
    p = protocol
    n = len(graph["body_id"])
    weights = csr_matrix((graph["data"], graph["indices"], graph["indptr"]), shape=(n, n))
    names = ("JO-A", "JO-B", "SAG")
    targets = np.concatenate([groups[k] for k in names])
    if len(np.unique(targets)) != len(targets) or any(not len(groups[k]) for k in (*names, "pC1", "vpoDN")):
        raise ValueError("Drive groups must be nonempty and disjoint; readouts required")
    positions = {}
    offset = 0
    for k in names:
        positions[k] = slice(offset, offset+len(groups[k]))
        offset += len(groups[k])
    config = asdict(p)
    config.update(mode="quick" if p.windows == 6 else "full", duration_ms=p.windows*p.window_ms,
                  steps_per_window=round(p.window_ms/p.dt), measurement_windows=p.windows-p.warmup)
    record = {"schema_version": "1", "protocol": config,
              "graph": {"sha256": graph_sha, "meta": {k: graph["meta"].get(k) for k in ("dataset", "version", "sign_rule", "sign_rule_version", "connectivity_source")}, "neurons": n},
              "dictionary": {"version": "1", "entries_sha256": sha256(Path(__file__).parents[1]/"dictionary"/"entries.py"),
                             "SAG_override": "^(?:AN_SMP_2|AN_FLA_SMP_2|ANXXX983)$",
                             "groups": {k: {"count": len(v), "indices": v.tolist(), "body_ids": graph["body_id"][v].tolist()} for k, v in groups.items()}},
              "environment": environment(device), "ear": {"RMS_FULL": RMS_FULL, "JO_MAX_HZ": JO_MAX_HZ, "padlen": 27, "slice_ms": 5},
              "parameters": asdict(Parameters(dt=p.dt)), "backend": "fast_gpu", "dtype": "float32",
              "source_sha256": {f.name: sha256(f) for f in [Path(__file__), Path(__file__).with_name("protocol.py"), Path(__file__).parents[1]/"song.py", Path(__file__).parents[1]/"ear.py"]},
              "trials": []}
    for kernel in ("shiu", "jump"):
        sim = Simulator(weights, device=device, params=Parameters(dt=p.dt), kernel=kernel,
                        groups=groups, drive=Drive(tuple(targets), 0, "poisson"))
        for condition in p.conditions:
            state = sim.initial_batch_state(p.seeds)
            song = Song(amplitude=1 if condition.endswith("_song") else 0)
            trials = [{"kernel": kernel, "condition": condition, "seed": seed, "windows": []} for seed in p.seeds]
            for window in range(p.windows):
                ear = rates(song.window())
                window_rates = {g: np.zeros(len(p.seeds)) for g in ("vpoDN", "pC1", "network")}
                slices = [[] for _ in p.seeds]
                for i in range(10):
                    requested = np.zeros((len(targets), 1))
                    for k in names:
                        requested[positions[k]] = (50 if condition.startswith("virgin_") else 0) if k == "SAG" else ear[k][i]
                    # Constructor validates scalar Drive; the existing batch loop
                    # samples step-by-target and records target-by-batch rates.
                    # Target order is fixed, including zero-rate targets.
                    sim.drive = Drive(tuple(targets), BatchRates(requested, p.dt), "poisson")
                    result = sim.run_batch(5, state=state)
                    for g in window_rates:
                        window_rates[g] += (result.total_hz_per_neuron if g == "network" else result.group_rates_hz[g])/10
                    for b in range(len(p.seeds)):
                        slices[b].append({label: {k: float(array[groups[k], b].mean()) for k in names}
                                          for label, array in (("requested_hz", result.requested_hz), ("sampled_hz", result.sampled_drive_hz), ("delivered_hz", result.delivered_hz))})
                for b, trial in enumerate(trials):
                    trial["windows"].append({"index": window, "rates_hz": {g: float(v[b]) for g, v in window_rates.items()}, "drive_slices": slices[b]})
            for trial in trials:
                measured = trial["windows"][p.warmup:]
                trial["rates_hz"] = {g: float(np.mean([w["rates_hz"][g] for w in measured])) for g in window_rates}
                trial["ignition_fraction"] = float(np.mean([w["rates_hz"]["network"] > 30 for w in measured]))
            record["trials"].extend(trials)
            if progress:
                print(f"{kernel} {condition}: {len(p.seeds)} seeds complete; {time.perf_counter()-start:.1f} s", flush=True)
        del sim, state, result
    record["elapsed_seconds"] = time.perf_counter()-start
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    protocol = Protocol.read(quick=args.quick)
    path = Path("build/graph_female.npz")
    fingerprint = sha256(path)
    graph = load(path)
    if any(graph["meta"].get(k) != v for k, v in {"dataset": "FAFB", "version": "783", "sign_rule": "shiu2024-parquet", "connectivity_source": "shiu"}.items()):
        raise ValueError("Graph does not match preregistration")
    record = run(protocol, graph, select_groups(graph), graph_sha=fingerprint, progress=True)
    prefix = Path("build/female_no_v1_quick" if args.quick else "records/female_no_v1")
    write(str(prefix)+"_experiment.json", record)
    write_from_json(str(prefix)+"_experiment.json", str(prefix)+"_report.md")


if __name__ == "__main__":
    main()
