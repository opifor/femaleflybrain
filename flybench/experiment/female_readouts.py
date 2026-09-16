"""Descriptive cell readouts observed from the unchanged female protocol."""
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

from flybench.dictionary import groups as dictionary_groups
from flybench.dictionary.entries import entries
from flybench.graph import load
from . import runner, two_female as tf
from .protocol import Protocol
from .record import sha256, validate

ROOT = Path(__file__).resolve().parents[2]
NAME = "female_readouts_v1"
PREREG = f"experiments/{NAME}.md"
FREEZE = f"records/{NAME}_freeze.json"
EXPERIMENT = f"records/{NAME}_experiment.json"
CHECKS = f"records/{NAME}_checks.json"
REPORT = f"records/{NAME}_report.md"
RAW = f"build/records-raw/{NAME}"
GROUPS = ("vpoDN", "pC1", "vpoEN", "vpoIN", "AVLP008", "DNp13/pMN1", "oviDN",
          "vpoEN-input:CB1484", "vpoEN-input:CB2364", "vpoEN-input:CB1383",
          "vpoEN-input:WED104", "vpoEN-input-top10", "vpoEN-gate:AVLP083",
          "AMMC-B1-candidate", "AMMC-B1-candidate-graph", "A2-candidate")
KERNELS = ("shiu", "jump")
CONDITIONS = Protocol().conditions
BASELINES = {"female": tf.BASELINE, "banc": "records/two_female_v1_experiment.json"}
INPUTS = tuple(dict.fromkeys((*tf.INPUTS, PREREG, BASELINES["banc"],
    "flybench/experiment/female_readouts.py", "tests/test_female_readouts.py",
    "flybench/dictionary/api.py", "flybench/sim/lif.py", "flybench/sim/fast.py",
    "flybench/sim/release.py")))


def now():
    return datetime.now(timezone.utc).isoformat()


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n",
                    encoding="utf-8", newline="\n")


def digest(path):
    path = Path(path)
    if path.suffix == ".npz":
        return sha256(path)
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def select(graph, snapshot, dataset):
    original = tf.select_groups(graph, snapshot, dataset)
    api = dictionary_groups(dataset, graph=graph)
    for name in ("JO-A", "JO-B", "vpoDN"):
        if not np.array_equal(original[name], api[name]):
            raise ValueError(f"API selector mismatch: {name}")
    if dataset == "banc" and not np.array_equal(original["SAG"], api["SAG"]):
        raise ValueError("API SAG mismatch")
    pc1 = np.sort(np.concatenate([api["pC1"+c] for c in "abcde"]))
    if dataset == "banc":
        pc1 = pc1[graph["superclass"][pc1] == "central_brain_intrinsic"]
    if not np.array_equal(original["pC1"], pc1):
        raise ValueError("API pC1 mismatch")
    reads = {g: original[g] if g in original else
             api["vpoDN-GABA-input" if g == "AVLP008" else g] for g in GROUPS}
    return original, reads


def population(graph, snapshot, dataset):
    original, reads = select(graph, snapshot, dataset)
    identities = tf.identities(graph, reads)
    definitions = {e.name: e.to_dict() for e in entries(dataset)}
    for name, info in identities.items():
        entry = "vpoDN-GABA-input" if name == "AVLP008" else name
        info["status"] = "present" if info["count"] else "absent"
        info["selector"] = ([definitions["pC1"+c]["selector"] for c in "abcde"]
                            if name == "pC1" else definitions[entry]["selector"])
        info["dictionary_name"] = entry
        if name == "pC1" and dataset == "banc":
            info["additional_filter"] = "superclass=central_brain_intrinsic"
    return {"groups": identities, "original_groups": tf.identities(graph, original),
            "neurons": len(graph["body_id"]), "population": graph["meta"]["population"],
            "sign_rule": graph["meta"]["sign_rule"],
            "outside_population_synapses": graph["meta"]["outside_population_synapses"]}


def freeze(root=ROOT):
    if (root/FREEZE).exists():
        raise FileExistsError("Freeze already exists")
    pops = {}
    for dataset in BASELINES:
        graph = load(root/f"build/graph_{dataset}.npz")
        snapshot = tf.read_json(root/f"build/dictionary_{dataset}.json")
        graph_hash = sha256(root/f"build/graph_{dataset}.npz")
        baseline = tf.read_json(root/BASELINES[dataset])
        if graph_hash != snapshot["graph"]["sha256"] or graph_hash != baseline["graph"]["sha256"]:
            raise ValueError("Graph fingerprint mismatch")
        pops[dataset] = population(graph, snapshot, dataset)
        for name, info in pops[dataset]["original_groups"].items():
            if info["body_ids"] != baseline["dictionary"]["groups"][name]["body_ids"]:
                raise ValueError(f"Historical identities differ: {dataset} {name}")
    frozen = {"schema_version": NAME+".freeze.1", "created_utc": now(),
              "hash_basis": "lf", "binary_hash_basis": "original bytes",
              "sha256": {p: digest(root/p) for p in INPUTS}, "populations": pops}
    save_json(root/FREEZE, frozen)
    return frozen


def verify_freeze(root=ROOT):
    frozen = tf.read_json(root/FREEZE)
    for path, expected in frozen["sha256"].items():
        if digest(root/path) != expected:
            raise ValueError(f"Frozen input changed: {path}")
    return frozen


def protocol(root=ROOT, quick=False):
    text = (root/PREREG).read_text(encoding="utf-8")
    return replace(Protocol(), name=NAME, text=text, sha256=digest(root/PREREG),
                   seeds=(0, 1) if quick else tuple(range(10)), windows=6 if quick else 20)


class Observer:
    """Copy returned counts, never simulator state or random generators."""
    def __init__(self, p, reads):
        self.p = p
        self.indices = np.unique(np.concatenate(list(reads.values())))
        self.counts = np.zeros((2, len(p.conditions), p.windows, 10,
                                len(self.indices), len(p.seeds)), dtype=np.int64)
        self.seen = np.zeros(self.counts.shape[:4], dtype=bool)
        self.code = runner.Simulator.run_batch.__code__
        self.caller = runner.run.__code__

    def __call__(self, frame, event, result):
        if event != "return" or frame.f_code is not self.code:
            return
        parent = frame.f_back
        if parent is None or parent.f_code is not self.caller:
            return
        context = parent.f_locals
        key = (KERNELS.index(context["kernel"]), self.p.conditions.index(context["condition"]),
               context["window"], context["i"])
        if self.seen[key] or result is None:
            raise ValueError("Duplicate or failed observed slice")
        counts = result.counts[self.indices]
        if counts.shape != self.counts[key].shape or np.any(counts < 0) or np.any(counts != np.floor(counts)):
            raise ValueError("Invalid observed counts")
        self.counts[key] = counts
        self.seen[key] = True


def observed_run(p, graph, original, reads, **kwargs):
    if sys.getprofile() is not None:
        raise RuntimeError("An active profiler would be displaced")
    observer = Observer(p, reads)
    previous = sys.getprofile()
    try:
        sys.setprofile(observer)
        record = runner.run(p, graph, original, **kwargs)
    finally:
        sys.setprofile(previous)
    validate(record)
    if not observer.seen.all():
        raise ValueError("Incomplete observed slice coverage")
    return record, observer


def silence_band(group_mean, cell_means):
    if not len(cell_means):
        return {"status": "absent", "within_band": None, "max_cell_mean_hz": None,
                "all_zero": None}
    maximum = float(np.max(cell_means))
    return {"status": "present", "within_band": bool(group_mean <= 1 and maximum <= 3),
            "max_cell_mean_hz": maximum, "all_zero": bool(maximum == 0)}


def summarize(counts, indices, p, reads, record):
    expected = (2, len(p.conditions), p.windows, 10, len(indices), len(p.seeds))
    if counts.shape != expected or not np.isfinite(counts).all() or np.any(counts < 0):
        raise ValueError("Invalid raw count coverage")
    rows, contrasts, observer_checks = [], [], []
    lookup = {(t["kernel"], t["condition"], t["seed"]): t for t in record["trials"]}
    seed_rates = {}
    for ki, kernel in enumerate(KERNELS):
        for ci, condition in enumerate(p.conditions):
            measured = counts[ki, ci, p.warmup:]
            for group, ix in reads.items():
                row = {"kernel": kernel, "condition": condition, "group": group,
                       "count": len(ix), "status": "present" if len(ix) else "absent"}
                if not len(ix):
                    row.update(rate_hz=None, seed_means_hz=[], cell_means_hz=[],
                               ignition_fraction=None)
                else:
                    positions = np.searchsorted(indices, ix)
                    if not np.array_equal(indices[positions], ix):
                        raise ValueError("Raw cell identity mismatch")
                    selected = measured[:, :, positions, :]
                    # Mirror only the arithmetic of the existing readout reducer.
                    # Simulation, ear, input generation and state remain in runner.run.
                    windows = np.zeros((p.windows-p.warmup, len(p.seeds)))
                    for s in range(10):
                        windows += selected[:, s].sum(axis=1) / .005 / len(ix) / 10
                    means = windows.mean(axis=0)
                    cell_means = selected.sum(axis=(0, 1, 3)) / ((p.windows-p.warmup)*.05*len(p.seeds))
                    seed_rates[kernel, condition, group] = dict(zip(p.seeds, map(float, means)))
                    row.update(rate_hz=tf.stats(means), seed_means_hz=means.tolist(),
                               cell_means_hz=cell_means.tolist(),
                               ignition_fraction=float(np.mean(windows > 30)))
                    if group in ("vpoDN", "pC1"):
                        for seed, value in zip(p.seeds, means):
                            expected_rate = lookup[kernel, condition, seed]["rates_hz"][group]
                            observer_checks.append({"kernel": kernel, "condition": condition,
                                "seed": seed, "group": group, "observed": float(value),
                                "runner": expected_rate, "equal": bool(value == expected_rate)})
                if condition.endswith("_silence"):
                    row["silence"] = silence_band(row["rate_hz"]["mean"] if row["rate_hz"] else None,
                                                  row["cell_means_hz"])
                rows.append(row)
        pairs = (("virgin_song", "virgin_silence"), ("mated_song", "mated_silence"),
                 ("virgin_song", "mated_song"), ("virgin_silence", "mated_silence"))
        for left, right in pairs:
            for group, ix in reads.items():
                differences = ([seed_rates[kernel, left, group][s]-seed_rates[kernel, right, group][s]
                                for s in p.seeds] if len(ix) else [])
                contrasts.append({"kernel": kernel, "group": group, "left": left, "right": right,
                    "status": "present" if len(ix) else "absent", "seeds": list(p.seeds),
                    "paired_differences_hz": differences,
                    "difference_hz": tf.stats(differences) if differences else None})
    network = [{"kernel": k, "condition": c,
        "rate_hz": tf.stats([lookup[k, c, s]["rates_hz"]["network"] for s in p.seeds]),
        "ignition_fraction": float(np.mean([lookup[k, c, s]["ignition_fraction"] for s in p.seeds]))}
        for k in KERNELS for c in p.conditions]
    return {"rows": rows, "contrasts": contrasts, "network": network}, observer_checks


def exact_baseline(record, baseline):
    old = {(t["kernel"], t["condition"], t["seed"]): t for t in baseline["trials"]}
    current = {(t["kernel"], t["condition"], t["seed"]): t for t in record["trials"]}
    coverage = (set(old) == set(current) and len(old) == len(baseline["trials"])
                and len(current) == len(record["trials"]))
    rows = []
    for key, trial in current.items():
        for group in ("vpoDN", "pC1"):
            expected = old.get(key, {}).get("rates_hz", {}).get(group)
            actual = trial["rates_hz"][group]
            rows.append({"kernel": key[0], "condition": key[1], "seed": key[2],
                         "group": group, "actual": actual, "expected": expected,
                         "equal": actual == expected})
    return {"coverage_equal": coverage, "comparisons": rows,
            "passed": coverage and all(row["equal"] for row in rows)}


def fmt(value):
    return "absent" if value is None else f"{value['mean']:.6g} +/- {value['se']:.6g}"


def render(result):
    lines = ["# Female readout baselines", "", "Descriptive; no behavioral decision.", "",
             "## Preregistration (verbatim)", "", result["preregistration"], "",
             "## Execution and selectors", "",
             f"Preregistration SHA-256 (LF): `{result['preregistration_sha256']}`.",
             f"Full execution including I/O: {result['elapsed_seconds']:.3f} s. "
             "CUDA fast_gpu float32; two graphs, two kernels, four conditions, ten seeds (160 trials).",
             "Cell arrays follow the body IDs and indices in populations.groups; raw NPZ axes are "
             "kernel, condition, window, 5 ms slice, selected cell, seed.", "",
             "| Group | FAFB count | BANC count | FAFB selector | BANC selector |",
             "|---|---:|---:|---|---|"]
    for g in GROUPS:
        infos = [result["populations"][d]["groups"][g] for d in BASELINES]
        selectors = [json.dumps(i["selector"]).replace("|", "&#124;") for i in infos]
        lines.append(f"| {g} | {infos[0]['count']} | {infos[1]['count']} | `{selectors[0]}` | `{selectors[1]}` |")
    lines += ["", "BANC pC1 also requires central_brain_intrinsic. Counts include every selected cell, "
              "including cells without a direct vpoEN edge. All 16 groups remain in the denominator; "
              "absent is not a zero-rate measurement. Groups overlap."]
    for dataset, data in result["datasets"].items():
        lines += ["", f"## {dataset}: condition means", "", "Hz/cell +/- SE across ten seeds; warm-up excluded.", "",
                  "| Kernel | Group | virgin_song | mated_song | virgin_silence | mated_silence |",
                  "|---|---|---:|---:|---:|---:|"]
        lookup = {(r["kernel"], r["condition"], r["group"]): r for r in data["summary"]["rows"]}
        for k in KERNELS:
            for g in GROUPS:
                lines.append(f"| {k} | {g} | " + " | ".join(fmt(lookup[k, c, g]["rate_hz"]) for c in CONDITIONS)+" |")
        lines += ["", f"## {dataset}: silent baseline", "",
                  "Band: group mean <=1 Hz AND every cell mean <=3 Hz; cell means average seeds and measured windows.", "",
                  "| Kernel | Condition | Group | Group mean Hz | Maximum cell mean Hz | Within band | Exactly zero |",
                  "|---|---|---|---:|---:|---|---|"]
        for r in data["summary"]["rows"]:
            if "silence" in r:
                s = r["silence"]
                values = ["absent"]*4 if r["status"] == "absent" else [
                    f"{r['rate_hz']['mean']:.6g}", f"{s['max_cell_mean_hz']:.6g}", str(s['within_band']), str(s['all_zero'])]
                lines.append(f"| {r['kernel']} | {r['condition']} | {r['group']} | " + " | ".join(values)+" |")
        lines += ["", f"## {dataset}: paired differences", "", "Descriptive, no threshold; Hz/cell +/- paired SE.", "",
                  "| Kernel | Group | Left minus right | Mean +/- SE |", "|---|---|---|---:|"]
        for r in data["summary"]["contrasts"]:
            lines.append(f"| {r['kernel']} | {r['group']} | {r['left']} - {r['right']} | {fmt(r['difference_hz'])} |")
        lines += ["", f"## {dataset}: ignition", "",
                  "Fraction of measured seed-windows with mean strictly >30 Hz/neuron (network) or Hz/cell (group).", "",
                  "| Kernel | Population | virgin_song | mated_song | virgin_silence | mated_silence |",
                  "|---|---|---:|---:|---:|---:|"]
        for k in KERNELS:
            values = [r["ignition_fraction"] for r in data["summary"]["network"] if r["kernel"] == k]
            lines.append(f"| {k} | network | " + " | ".join(f"{v:.6g}" for v in values)+" |")
            for g in GROUPS:
                values = [lookup[k, c, g]["ignition_fraction"] for c in CONDITIONS]
                lines.append(f"| {k} | {g} | " + " | ".join("absent" if v is None else f"{v:.6g}" for v in values)+" |")
    lines += ["", "## Equality, scope and deviations", "",
              f"Exact historical vpoDN/pC1 equality: {result['equality_passed']}. "
              "Both kernels, all conditions and seeds; observer-to-runner equality and raw reconstruction "
              "are recorded in records/female_readouts_v1_checks.json.",
              "The existing runner.run, simulator, hook, ear and dictionary files are unchanged. "
              "Only JO-A, JO-B and SAG received external drive. The return-event observer did not replace a function.",
              "Population scope and sign sources differ; BANC includes ventral nerve cord cells and excludes "
              "4,344,932 synapses outside its construction population. Absent labels do not imply biological absence.",
              "these readouts do not establish hearing, refusal or mating", "the ear is not calibrated",
              "Clean room: no restricted source tree was inspected; only the supplied runtime dependency directory was used. "
              "No git write commands were executed.",
              "Deviations: " + ("; ".join(result["deviations"]) if result["deviations"] else "none."), ""]
    return "\n".join(lines)


def execute(root=ROOT, quick=False):
    started = time.perf_counter()
    if not (root/FREEZE).exists():
        freeze(root)
    frozen = verify_freeze(root)
    stage = "quick" if quick else "full"
    if not quick:
        preliminary = tf.read_json(root/RAW/"quick_summary.json")
        if preliminary["freeze_sha256"] != sha256(root/FREEZE) or not preliminary["equality_passed"]:
            raise ValueError("Quick observation must pass under the same freeze")
    p = protocol(root, quick)
    result = {"schema_version": NAME+".summary.1", "started_utc": now(), "mode": stage,
              "preregistration": p.text, "preregistration_sha256": p.sha256, "hash_basis": "lf",
              "freeze_sha256": sha256(root/FREEZE), "populations": frozen["populations"],
              "seeds": list(p.seeds), "datasets": {}, "deviations": []}
    checks = {"schema_version": NAME+".checks.1", "mode": stage, "datasets": {}}
    for dataset in (("female",) if quick else tuple(BASELINES)):
        graph = load(root/f"build/graph_{dataset}.npz")
        original, reads = select(graph, tf.read_json(root/f"build/dictionary_{dataset}.json"), dataset)
        record, observer = observed_run(p, graph, original, reads, device="cuda",
            graph_sha=frozen["sha256"][f"build/graph_{dataset}.npz"], progress=True)
        stem = f"{RAW}/{stage}_{dataset}"
        save_json(root/(stem+"_runner.json"), record)
        np.savez_compressed(root/(stem+"_counts.npz"), counts=observer.counts, indices=observer.indices,
                            seeds=np.array(p.seeds), kernels=np.array(KERNELS), conditions=np.array(p.conditions))
        saved_record = tf.read_json(root/(stem+"_runner.json"))
        with np.load(root/(stem+"_counts.npz"), allow_pickle=False) as archive:
            summary, observed_checks = summarize(archive["counts"], archive["indices"], p, reads, saved_record)
        direct, _ = summarize(observer.counts, observer.indices, p, reads, record)
        dc = {"slice_coverage": bool(observer.seen.all()), "raw_reconstruction_equal": summary == direct,
              "observer_comparisons": observed_checks,
              "observer_equal": all(r["equal"] for r in observed_checks)}
        if not quick:
            dc["historical"] = exact_baseline(saved_record, tf.read_json(root/BASELINES[dataset]))
            if dataset == "female":
                old = tf.read_json(root/BASELINES["banc"])["FAFB_source"]["condition_summaries"]
                dc["two_female_embedded_fafb_equal"] = tf.summarize(saved_record) == old
        dc["passed"] = (dc["slice_coverage"] and dc["raw_reconstruction_equal"] and dc["observer_equal"]
                        and dc.get("historical", {"passed": True})["passed"]
                        and dc.get("two_female_embedded_fafb_equal", True))
        checks["datasets"][dataset] = dc
        result["datasets"][dataset] = {"summary": summary, "environment": record["environment"],
            "ear": record["ear"], "parameters": record["parameters"], "elapsed_seconds": record["elapsed_seconds"],
            "raw": {suffix: {"path": stem+suffix, "sha256": sha256(root/(stem+suffix))}
                    for suffix in ("_runner.json", "_counts.npz")}}
        save_json(root/RAW/(stage+"_checks.json"), checks)
        if not dc["passed"]:
            checks["status"] = "FAIL-CLOSED: equality or coverage mismatch"
            save_json(root/CHECKS, checks)
            raise ValueError(checks["status"])
    verify_freeze(root)
    checks.update(frozen_inputs_unchanged=True, equality_passed=True, completed_utc=now())
    result.update(elapsed_seconds=time.perf_counter()-started, completed_utc=now(), equality_passed=True)
    if quick:
        save_json(root/RAW/"quick_checks.json", checks)
        save_json(root/RAW/"quick_summary.json", result)
    else:
        result["quick_elapsed_seconds"] = preliminary["elapsed_seconds"]
        save_json(root/EXPERIMENT, result)
        save_json(root/CHECKS, checks)
        (root/REPORT).write_text(render(tf.read_json(root/EXPERIMENT)), encoding="utf-8", newline="\n")
    print(json.dumps({"mode": stage, "elapsed_seconds": result["elapsed_seconds"],
                      "equality_passed": True}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    if args.freeze:
        print(freeze()["sha256"][PREREG])
    else:
        execute(quick=args.quick)


if __name__ == "__main__":
    main()
