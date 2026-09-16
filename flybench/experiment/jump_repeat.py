"""Descriptive within-session repeatability; no calibration."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

from . import female_readouts as fr, two_female as tf

ROOT = Path(__file__).resolve().parents[2]
NAME = "jump_repeat_v1"
RAW = f"build/records-raw/{NAME}"
PAIRS = tuple((c, s) for c in fr.CONDITIONS for s in range(10))
LABELS = [f"inproc{i}" for i in range(1, 4)] + [f"separate{i}" for i in range(1, 4)]
GROUPS = ("vpoDN", "pC1")
PREREG = f"experiments/{NAME}.md"
FREEZE = f"records/{NAME}_freeze.json"


def input_paths():
    paths = {PREREG, "build/graph_female.npz", "build/dictionary_female.json",
             tf.BASELINE, "records/female_readouts_v1_checks.json",
             "records/female_readouts_v1_experiment.json", "tests/test_jump_repeat.py",
             "experiments/female_no_v1.md"}
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/"flybench").rglob("*.py"))
    return sorted(paths)


def verify_freeze():
    frozen = tf.read_json(ROOT/FREEZE)
    for path, expected in frozen["sha256"].items():
        if fr.digest(ROOT/path) != expected:
            raise ValueError(f"Frozen input changed: {path}")
    return frozen


def freeze():
    if (ROOT/FREEZE).exists():
        return verify_freeze()
    from flybench.experiment.record import environment
    graph = fr.load(ROOT/"build/graph_female.npz")
    snapshot = tf.read_json(ROOT/"build/dictionary_female.json")
    groups = tf.select_groups(graph, snapshot, "female")
    historical = tf.read_json(ROOT/tf.BASELINE)
    graph_sha = fr.digest(ROOT/"build/graph_female.npz")
    if graph_sha != historical["graph"]["sha256"] or graph_sha != snapshot["graph"]["sha256"]:
        raise ValueError("Graph identity mismatch")
    if graph["meta"]["dataset"] != "FAFB" or graph["meta"]["version"] != "783":
        raise ValueError("Unexpected graph release")
    identities = tf.identities(graph, groups)
    for group in groups:
        if identities[group]["body_ids"] != historical["dictionary"]["groups"][group]["body_ids"]:
            raise ValueError("Historical group identity mismatch")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()
    if head != "2817d540673b0100ac1c5e007c2dc09036f69f13":
        raise ValueError("Unexpected HEAD")
    driver = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version",
                             "--format=csv,noheader"], capture_output=True, text=True, check=True)
    frozen = {"schema_version": NAME+".freeze.1", "created_utc": fr.now(),
        "head": head, "hash_basis": "lf", "binary_hash_basis": "original bytes",
        "sha256": {p: fr.digest(ROOT/p) for p in input_paths()},
        "groups": identities, "environment": environment("cuda"),
        "gpu_driver": driver.stdout.strip(), "batch_width": 10,
        "pairs": [list(p) for p in PAIRS]}
    fr.save_json(ROOT/FREEZE, frozen)
    return frozen


def equality_matrix(arrays):
    """Compare dtype, shape and bytes, without tolerances or total-only checks."""
    def equal(a, b):
        return a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()
    return [[equal(a, b) for b in arrays] for a in arrays]


def differences(a, b):
    if a.shape != b.shape or a.dtype != np.int64 or b.dtype != np.int64:
        raise ValueError("Aligned int64 count arrays required")
    delta = b - a
    return {"changed_bins": int(np.count_nonzero(delta)),
            "l1_spikes": int(np.abs(delta).sum()),
            "max_abs_bin_spikes": int(np.abs(delta).max(initial=0)),
            "signed_total_spikes": int(delta.sum())}


def classify(matrix, historical_equal, readouts_equal):
    if not all(all(row) for row in matrix):
        return "run-to-run divergent"
    if not all(historical_equal) or not all(readouts_equal):
        return "session-stable, historical-divergent"
    return "fully reproducible"


def reduce_counts(counts, indices, groups, warmup=4):
    """Use exactly the existing slice-to-window arithmetic."""
    if counts.ndim != 3 or counts.shape[1] != 10 or counts.dtype != np.int64:
        raise ValueError("Expected window, slice, selected-cell int64 counts")
    if np.any(counts < 0) or not 0 <= warmup < len(counts):
        raise ValueError("Invalid counts or measurement interval")
    answer = {}
    for group in GROUPS:
        positions = np.searchsorted(indices, groups[group])
        if not np.array_equal(indices[positions], groups[group]):
            raise ValueError("Cell identity mismatch")
        selected = counts[warmup:, :, positions]
        windows = np.zeros(len(selected))
        for s in range(10):
            windows += selected[:, s].sum(axis=1) / .005 / len(positions) / 10
        answer[group] = {"rate_hz": float(windows.mean()),
                         "spikes": int(selected.sum()),
                         "ignition_fraction": float(np.mean(windows > 30))}
    return answer


def baseline_values(kernel, condition, seed):
    historical = tf.read_json(ROOT/tf.BASELINE)
    trial = next(t for t in historical["trials"] if
                 (t["kernel"], t["condition"], t["seed"]) == (kernel, condition, seed))
    readouts = tf.read_json(ROOT/"records/female_readouts_v1_experiment.json")
    rows = readouts["datasets"]["female"]["summary"]["rows"]
    current = {g: next(t["seed_means_hz"][seed] for t in rows if
        (t["kernel"], t["condition"], t["group"]) == (kernel, condition, g)) for g in GROUPS}
    comparisons = tf.read_json(ROOT/"records/female_readouts_v1_checks.json")["datasets"]["female"]["historical"]["comparisons"]
    old = {g: trial["rates_hz"][g] for g in GROUPS}
    if any(next(t["expected"] for t in comparisons if
        (t["kernel"], t["condition"], t["seed"], t["group"]) ==
        (kernel, condition, seed, g)) != old[g] for g in GROUPS):
        raise ValueError("Historical comparison record disagrees with source")
    if any(next(t["actual"] for t in comparisons if
        (t["kernel"], t["condition"], t["seed"], t["group"]) ==
        (kernel, condition, seed, g)) != current[g] for g in GROUPS):
        raise ValueError("Readouts comparison record disagrees with source")
    return old, current


def summarize_runs(runs, groups):
    rows = []
    for kernel in ("jump", "shiu"):
        for condition, seed in PAIRS:
            selected = [r for r in runs if (r["kernel"], r["condition"], r["seed"]) ==
                        (kernel, condition, seed)]
            expected_labels = LABELS
            if [r["repeat"] for r in selected] != expected_labels:
                raise ValueError("Missing, duplicated or misordered run coverage")
            arrays = []
            for r in selected:
                with np.load(ROOT/r["raw_counts"]) as raw:
                    counts, indices = raw["counts"], raw["indices"]
                    rebuilt = reduce_counts(counts, indices, groups)
                    if rebuilt != r["groups"]:
                        raise ValueError("Raw-to-summary reconstruction differs")
                    arrays.append(counts)
            matrix = equality_matrix(arrays)
            rates = [np.array([r["groups"][g]["rate_hz"] for g in GROUPS], dtype=np.float64)
                     for r in selected]
            historical, readouts = baseline_values(kernel, condition, seed)
            historical_equal = [all(r["groups"][g]["rate_hz"] == historical[g] for g in GROUPS)
                                for r in selected]
            readouts_equal = [all(r["groups"][g]["rate_hz"] == readouts[g] for g in GROUPS)
                              for r in selected]
            deltas = [{"left": selected[i]["repeat"], "right": selected[j]["repeat"],
                       "all_windows": differences(arrays[i], arrays[j]),
                       "measurement_windows": differences(arrays[i][4:], arrays[j][4:])}
                      for i in range(len(arrays)) for j in range(i+1, len(arrays))]
            baseline_delta = [{"repeat": r["repeat"], "group": g,
                "historical_delta_hz": r["groups"][g]["rate_hz"]-historical[g],
                "readouts_delta_hz": r["groups"][g]["rate_hz"]-readouts[g],
                "historical_implied_spike_delta":
                    r["groups"][g]["spikes"]-round(historical[g]*.8*len(groups[g])),
                "readouts_implied_spike_delta":
                    r["groups"][g]["spikes"]-round(readouts[g]*.8*len(groups[g]))}
                for r in selected for g in GROUPS]
            rows.append({"kernel": kernel, "condition": condition, "seed": seed,
                "historical": historical, "readouts": readouts, "runs": selected,
                "repeat_labels": expected_labels, "raw_equality_matrix": matrix,
                "rate_equality_matrix": equality_matrix(rates),
                "historical_equal": historical_equal, "readouts_equal": readouts_equal,
                "pairwise_spike_differences": deltas, "baseline_differences": baseline_delta,
                "classification": classify(matrix, historical_equal, readouts_equal)})
    return rows


def render(result):
    def pair(values):
        return "/".join(f"{values[g]:.6g}" for g in GROUPS)
    lines = ["# jump_repeat_v1", "", "no calibration; descriptive", "",
        f"Source HEAD: `{result['head']}`. hash_basis: lf.",
        f"Preregistration SHA-256: `{result['preregistration_sha256']}`.",
        f"Execution elapsed: {result['elapsed_seconds']:.3f} s.",
        "Values are vpoDN/pC1 Hz per cell, one seed, measurement windows 4-19.", "",
        "| Condition | Seed | Kernel | Historical | Readouts | In 1 | In 2 | In 3 | Separate 1 | Separate 2 | Separate 3 |",
        "|---|---:|---|---|---|---|---|---|---|---|---|"]
    for row in result["rows"]:
        values = [pair({g: r["groups"][g]["rate_hz"] for g in GROUPS}) for r in row["runs"]]
        lines.append(f"| {row['condition']} | {row['seed']} | {row['kernel']} | " +
                     " | ".join([pair(row["historical"]), pair(row["readouts"]), *values])+" |")
    lines += ["", "Both kernels have six complete repeats, each with ten seed columns.", "",
              f"Jump classification: **{result['kernels']['jump']['classification']}**.",
              f"Shiu classification: **{result['kernels']['shiu']['classification']}**.", "",
              "Equality refers to selected-cell integer counts in each 5 ms slice and exact float64 "
              "readout bytes. It does not assert equality of every internal voltage or spike timestamp."]
    for row in result["rows"]:
        lines += ["", f"## {row['kernel']} {row['condition']} seed {row['seed']}", "",
                  f"Class: {row['classification']}.",
                  "Raw equality matrix (rows and columns: " + ", ".join(row["repeat_labels"])+").",
                  "```text", *[" ".join("1" if v else "0" for v in r) for r in row["raw_equality_matrix"]], "```"]
        for r in row["runs"]:
            group_text = "; ".join(f"{g}: {r['groups'][g]['spikes']} spikes, ignition "
                         f"{r['groups'][g]['ignition_fraction']:.4g}" for g in GROUPS)
            lines.append(f"- {r['repeat']}: {group_text}; network ignition {r['network_ignition_fraction']:.4g}.")
        deltas = row["pairwise_spike_differences"]
        if deltas:
            lines.append("Maximum pairwise measured-bin L1 spike difference: " +
                         str(max(d["measurement_windows"]["l1_spikes"] for d in deltas))+".")
        for group in GROUPS:
            ds = [d for d in row["baseline_differences"] if d["group"] == group]
            lines.append(f"{group} implied measured-total spike deltas: historical " +
                str([d["historical_implied_spike_delta"] for d in ds])+"; readouts " +
                str([d["readouts_implied_spike_delta"] for d in ds])+".")
    lines += ["", "## Interpretation and scope", "",
        "A run-to-run divergent result is not bitwise reproducible in this session. "
        "Floating-point reduction order is a candidate mechanism, not an isolated causal measurement. "
        "Stable repeats with historical differences are consistent with execution-context differences; "
        "driver, build and session effects cannot be separated here. Historical and current runs "
        "both use ten seed columns. This observation does not isolate atomic addition order.",
        "Ignition is the measured-window fraction strictly above 30 Hz/cell (groups) or "
        "30 Hz/neuron (network). Historical spike deltas are inferred from saved rates and group "
        "denominators, not historical raw spike timestamps. Raw count axes: window, 5 ms slice, "
        "selected cell; graph indices and body IDs are stored alongside counts.",
        "The unchanged return-event Observer reads run_batch results without changing state, "
        "RNG or drive. Source files for runner, simulator, hook, ear and dictionary remain unchanged.",
        "Deviations: " + "; ".join(result["deviations"]), ""]
    return "\n".join(lines)


def kernel_summary(rows, kernel):
    selected = [r for r in rows if r["kernel"] == kernel]
    matrix = [[all(r["raw_equality_matrix"][i][j] and
                   r["rate_equality_matrix"][i][j] for r in selected)
               for j in range(6)] for i in range(6)]
    rate_matrix = [[all(r["rate_equality_matrix"][i][j] for r in selected)
                    for j in range(6)] for i in range(6)]
    historical = [all(r["historical_equal"][i] for r in selected) for i in range(6)]
    readouts = [all(r["readouts_equal"][i] for r in selected) for i in range(6)]
    mismatches = []
    for row in selected:
        for g in GROUPS:
            values = [r["groups"][g]["rate_hz"] for r in row["runs"]]
            for i, label in enumerate(LABELS):
                for reference, value in [("historical", row["historical"][g]),
                                         ("readouts", row["readouts"][g])]:
                    if values[i] != value:
                        mismatches.append(dict(condition=row["condition"], seed=row["seed"],
                            group=g, left=reference, right=label, left_hz=value,
                            right_hz=values[i], delta_hz=values[i]-value))
                for j in range(i+1, 6):
                    if values[i] != values[j]:
                        mismatches.append(dict(condition=row["condition"], seed=row["seed"],
                            group=g, left=label, right=LABELS[j], left_hz=values[i],
                            right_hz=values[j], delta_hz=values[j]-values[i]))
    return dict(classification=classify(matrix, historical, readouts),
                equality_matrix=matrix, rate_equality_matrix=rate_matrix,
                historical_equal=historical, readouts_equal=readouts,
                seed_group_values_per_repeat=len(selected)*len(GROUPS), mismatches=mismatches)


def collect(label):
    frozen = verify_freeze()
    p = fr.Protocol.read(ROOT/"experiments/female_no_v1.md")
    graph = fr.load(ROOT/"build/graph_female.npz")
    groups = tf.select_groups(graph, tf.read_json(ROOT/"build/dictionary_female.json"), "female")
    reads = {g: groups[g] for g in GROUPS}
    record, observer = fr.observed_run(p, graph, groups, reads,
        graph_sha=frozen["sha256"]["build/graph_female.npz"], device="cuda", progress=True)
    summary, checks = fr.summarize(observer.counts, observer.indices, p, reads, record)
    if not all(c["equal"] for c in checks):
        raise ValueError("Observer-to-runner disagreement")
    stem = ROOT/RAW/label
    stem.mkdir(parents=True, exist_ok=False)
    fr.save_json(stem/"runner.json", record)
    trials = {(t["kernel"], t["condition"], t["seed"]): t for t in record["trials"]}
    runs = []
    for ki, kernel in enumerate(fr.KERNELS):
        for ci, condition in enumerate(p.conditions):
            for si, seed in enumerate(p.seeds):
                counts = observer.counts[ki, ci, :, :, :, si]
                path = stem/f"{kernel}_{condition}_{seed}.npz"
                np.savez_compressed(path, counts=counts, indices=observer.indices,
                                    body_ids=graph["body_id"][observer.indices])
                reduced = reduce_counts(counts, observer.indices, groups)
                trial = trials[kernel, condition, seed]
                if any(reduced[g]["rate_hz"] != trial["rates_hz"][g] for g in GROUPS):
                    raise ValueError("Per-seed raw reduction disagrees")
                runs.append(dict(repeat=label, kernel=kernel, condition=condition, seed=seed,
                    groups=reduced, network_ignition_fraction=trial["ignition_fraction"],
                    raw_counts=path.relative_to(ROOT).as_posix(), raw_sha256=fr.digest(path)))
    verify_freeze()
    fr.save_json(stem/"summary.json", dict(repeat=label, pid=os.getpid(),
        completed_utc=fr.now(), elapsed_seconds=record["elapsed_seconds"],
        environment=record["environment"], freeze_sha256=fr.digest(ROOT/FREEZE),
        observer_equal=True, slice_coverage=bool(observer.seen.all()), runs=runs))
    print(f"Completed {label}: {record['elapsed_seconds']:.3f} seconds", flush=True)


def finalize(elapsed):
    frozen = verify_freeze()
    batches = [tf.read_json(ROOT/RAW/label/"summary.json") for label in LABELS]
    if len({b["pid"] for b in batches[:3]}) != 1 or len({b["pid"] for b in batches[3:]}) != 3:
        raise ValueError("Process coverage mismatch")
    if any(b["pid"] == batches[0]["pid"] for b in batches[3:]):
        raise ValueError("Separate repeat used in-process PID")
    if any(b["freeze_sha256"] != fr.digest(ROOT/FREEZE) or
           b["environment"] != frozen["environment"] for b in batches):
        raise ValueError("Environment or freeze mismatch")
    runs = [r for b in batches for r in b["runs"]]
    for r in runs:
        if fr.digest(ROOT/r["raw_counts"]) != r["raw_sha256"]:
            raise ValueError("Raw hash mismatch")
    groups = {g: np.array(frozen["groups"][g]["indices"]) for g in GROUPS}
    rows = summarize_runs(runs, groups)
    kernels = {k: kernel_summary(rows, k) for k in fr.KERNELS}
    result = dict(schema_version=NAME+".results.2", head=frozen["head"], hash_basis="lf",
        preregistration_sha256=frozen["sha256"][PREREG], freeze_sha256=fr.digest(ROOT/FREEZE),
        elapsed_seconds=elapsed, completed_utc=fr.now(), completed_repeats=6,
        repeat_labels=LABELS, kernels=kernels, rows=rows,
        deviations=["The requested 160 values per kernel is arithmetically 80: four conditions x ten seeds x two groups; 160 across both kernels."])
    fr.save_json(ROOT/f"records/{NAME}_results.json", result)
    checks = dict(schema_version=NAME+".checks.2", completed_repeats=6,
        frozen_inputs_unchanged=True, raw_hashes_equal=True, raw_reconstruction_equal=True,
        observer_equal=all(b["observer_equal"] for b in batches),
        slice_coverage=all(b["slice_coverage"] for b in batches),
        process_ids={b["repeat"]: b["pid"] for b in batches}, kernels=kernels,
        status="Complete descriptive measurement; equality outcomes are not acceptance gates")
    fr.save_json(ROOT/f"records/{NAME}_checks.json", checks)
    report = render(result)
    report += "\n## Kernel-wide comparisons\n\nMatrix order: " + ", ".join(LABELS) + ".\n"
    for k, data in kernels.items():
        report += f"\n### {k}\n\nClass: {data['classification']}.\n\nRaw counts and rates equality:\n\n```text\n"
        report += "\n".join(" ".join(str(int(v)) for v in row) for row in data["equality_matrix"])+"\n```\n"
        report += "\nRate-only equality:\n\n```text\n"
        report += "\n".join(" ".join(str(int(v)) for v in row) for row in data["rate_equality_matrix"])+"\n```\n"
        report += "\nAll differing condition/seed/group comparisons (right minus left):\n\n"
        report += "| Condition | Seed | Group | Left | Right | Delta Hz |\n|---|---:|---|---|---|---:|\n"
        for m in data["mismatches"]:
            report += f"| {m['condition']} | {m['seed']} | {m['group']} | {m['left']} | {m['right']} | {m['delta_hz']:.9g} |\n"
    (ROOT/f"records/{NAME}_report.md").write_text(report, encoding="utf-8", newline="\n")
    print({k: d["classification"] for k, d in kernels.items()}, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--child", choices=LABELS[3:])
    args = parser.parse_args()
    if args.freeze:
        print(freeze()["sha256"][PREREG])
    elif args.child:
        collect(args.child)
    else:
        started = time.perf_counter()
        verify_freeze()
        for label in LABELS[:3]:
            collect(label)
        for label in LABELS[3:]:
            subprocess.run([sys.executable, "-B", "-m", "flybench.experiment.jump_repeat",
                            "--child", label], cwd=ROOT, check=True)
        finalize(time.perf_counter()-started)


if __name__ == "__main__":
    main()
