"""Descriptive second-female execution through the unchanged experiment runner."""
import argparse
from collections import Counter
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np

from flybench.dictionary.entries import Selector
from flybench.graph import load, where
from . import runner
from .protocol import Protocol
from .record import sha256, validate, write
from .report import mean_se, contrast

ROOT = Path(__file__).resolve().parents[2]
LABEL = "descriptive replication on a second individual"
GROUPS = ("JO-A", "JO-B", "SAG", "pC1", "vpoDN")
CONDITIONS = Protocol().conditions
PREREG = "experiments/two_female_v1.md"
FREEZE = "records/two_female_v1_freeze.json"
BASELINE = "records/female_no_v1_experiment.json"
RAW = "build/records-raw/two_female_v1"
INPUTS = (PREREG, BASELINE, "experiments/female_no_v1.md",
          "build/graph_female.npz", "build/graph_banc.npz",
          "build/dictionary_female.json", "build/dictionary_banc.json",
          "flybench/experiment/two_female.py", "flybench/experiment/runner.py",
          "flybench/experiment/protocol.py", "flybench/experiment/record.py",
          "flybench/experiment/report.py", "flybench/song.py", "flybench/ear.py",
          "flybench/sim/fast_gpu.py", "flybench/sim/params.py",
          "flybench/dictionary/entries.py")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def select_groups(graph, snapshot, dataset):
    """Use frozen dictionary selectors; retain the registered FAFB SAG union."""
    if snapshot["dataset"] != dataset:
        raise ValueError("Dictionary dataset mismatch")
    entries = {e["name"]: e for e in snapshot["entries"]}

    def select(name):
        return Selector(**entries[name]["selector"]).select(graph)

    selected = {name: select(name) for name in ("JO-A", "JO-B")}
    selected["SAG"] = (select("SAG") if dataset == "banc" else
                       where(graph, type_re=r"^(?:AN_SMP_2|AN_FLA_SMP_2|ANXXX983)$"))
    selected["pC1"] = np.sort(np.concatenate([select("pC1"+c) for c in "abcde"]))
    if dataset == "banc":
        ix = selected["pC1"]
        selected["pC1"] = ix[graph["superclass"][ix] == "central_brain_intrinsic"]
    selected["vpoDN"] = np.intersect1d(select("vpoDN"), where(graph, type_re=r"^DNp37$"))
    for name in ("JO-A", "JO-B", "SAG", "pC1"):
        if not len(selected[name]):
            raise ValueError(f"Required group absent: {name}")
    return selected


def identities(graph, selected):
    return {name: {"count": len(ix), "indices": ix.tolist(),
                   "body_ids": graph["body_id"][ix].tolist(),
                   "types": dict(Counter(map(str, graph["type"][ix]))),
                   "superclasses": dict(Counter(map(str, graph["superclass"][ix])))}
            for name, ix in selected.items()}


def inspect(root=ROOT):
    result = {}
    baseline = read_json(root/BASELINE)
    validate(baseline)
    for dataset, title, version in (("female", "FAFB", "783"), ("banc", "BANC", "888")):
        path = root/f"build/graph_{dataset}.npz"
        graph = load(path)
        snapshot = read_json(root/f"build/dictionary_{dataset}.json")
        digest = sha256(path)
        if snapshot["graph"]["sha256"] != digest:
            raise ValueError("Dictionary graph fingerprint mismatch")
        if graph["meta"]["dataset"] != title or graph["meta"]["version"] != version:
            raise ValueError("Graph release mismatch")
        selected = select_groups(graph, snapshot, dataset)
        ids = identities(graph, selected)
        if dataset == "female":
            if baseline["graph"]["sha256"] != digest:
                raise ValueError("Baseline graph fingerprint mismatch")
            for name in GROUPS:
                if ids[name]["body_ids"] != baseline["dictionary"]["groups"][name]["body_ids"]:
                    raise ValueError("Baseline selector identity mismatch")
        result[dataset] = {"sha256": digest, "neurons": len(graph["body_id"]),
                           "population": graph["meta"]["population"],
                           "population_filter": graph["meta"].get("population_filter"),
                           "outside_population_synapses": graph["meta"]["outside_population_synapses"],
                           "superclasses": dict(Counter(map(str, graph["superclass"]))),
                           "sign_rule": graph["meta"]["sign_rule"], "groups": ids}
    return result


def selector_table(populations, include_ids=True):
    lines = ["| Group | FAFB count | BANC count | FAFB body IDs | BANC body IDs |",
             "|---|---:|---:|---|---|"]
    for name in GROUPS:
        a, b = (populations[d]["groups"][name] for d in ("female", "banc"))
        lines.append(f"| {name} | {a['count']} | {b['count']} | " +
                     ", ".join(map(str, a["body_ids"])) + " | " +
                     ", ".join(map(str, b["body_ids"])) + " |")
    return "\n".join(lines)


def freeze(root=ROOT):
    target = root/FREEZE
    if target.exists():
        raise FileExistsError("Freeze already exists")
    populations = inspect(root)
    prereg = root/PREREG
    text = prereg.read_text(encoding="utf-8")
    if "## Frozen input identities" in text:
        raise ValueError("Identity appendix already exists")
    appendix = "\n## Frozen input identities\n\n" + selector_table(populations) + "\n\n"
    for dataset, details in populations.items():
        appendix += f"{dataset} graph SHA-256: `{details['sha256']}`. "
        appendix += f"Population: {details['population']}. Neurons: {details['neurons']}.\n\n"
    prereg.write_text(text+appendix, encoding="utf-8")
    frozen = {"schema_version": "two_female_v1.freeze.1", "created_utc": datetime.now(timezone.utc).isoformat(),
              "label": LABEL, "sha256": {p: sha256(root/p) for p in INPUTS},
              "populations": populations, "runner_refactor": "no refactor"}
    save_json(target, frozen)
    return frozen


def verify_freeze(root=ROOT):
    frozen = read_json(root/FREEZE)
    for path, digest in frozen["sha256"].items():
        if sha256(root/path) != digest:
            raise ValueError(f"Frozen input changed: {path}")
    return frozen


def protocol(root=ROOT, quick=False):
    return replace(Protocol.read(root/PREREG, quick=quick), name="two_female_v1",
                   chosen=("amplitude=1", "mixture=0.7", "scale=1.0", "JO_MAX_HZ=180",
                           "dt=0.2", "BANC SAG=ANXXX983"))


def stats(values):
    mean, se = mean_se(values)
    return {"mean": mean, "se": se, "n": len(values)}


def summarize(record):
    return [{"kernel": k, "condition": c,
             "rates_hz": {g: stats([t["rates_hz"][g] for t in record["trials"]
                                    if t["kernel"] == k and t["condition"] == c])
                          for g in ("vpoDN", "pC1", "network")},
             "ignition_fraction": float(np.mean([t["ignition_fraction"] for t in record["trials"]
                                                   if t["kernel"] == k and t["condition"] == c]))}
            for k in ("shiu", "jump") for c in CONDITIONS]


def comparisons(female, banc):
    lookup = [{(t["kernel"], t["condition"], t["seed"]): t for t in r["trials"]}
              for r in (female, banc)]
    if list(female["protocol"]["seeds"]) != list(banc["protocol"]["seeds"]):
        raise ValueError("Comparison needs identical seed coverage")
    rows = []
    for kernel in ("shiu", "jump"):
        for condition in CONDITIONS:
            for group in ("vpoDN", "pC1"):
                values = [[table[kernel, condition, seed]["rates_hz"][group]
                           for seed in banc["protocol"]["seeds"]] for table in lookup]
                delta = np.asarray(values[0])-np.asarray(values[1])
                mean, se = mean_se(delta)
                rows.append({"kernel": kernel, "condition": condition, "readout": group,
                             "FAFB": stats(values[0]), "BANC": stats(values[1]),
                             "paired_difference": stats(delta),
                             "absolute_difference_over_paired_se": abs(mean)/se if se else None,
                             "ratio_status": "finite" if se else ("undefined: 0/0" if mean == 0 else "unbounded: nonzero/0"),
                             "label": "descriptive; no threshold"})
    return rows


def contrasts(record):
    specs = [("P1", "vpoDN", "virgin_song", "mated_song", "shiu", "shiu"),
             ("P2", "vpoDN", "virgin_song", "virgin_silence", "shiu", "shiu"),
             ("P3", "pC1", "virgin_song", "mated_song", "shiu", "shiu")]
    for group in ("vpoDN", "pC1"):
        specs += [("P4 mated song minus silence", group, "mated_song", "mated_silence", k, k)
                  for k in ("shiu", "jump")]
        specs += [("P4 jump minus shiu", group, c, c, "jump", "shiu") for c in CONDITIONS]
    rows = []
    for name, group, left, right, lk, rk in specs:
        m, s, _ = contrast(record, group, left, right, lk, rk, descriptive=True)
        values = {(t['kernel'], t['condition'], t['seed']): t['rates_hz'][group]
                  for t in record['trials']}
        rows.append({"name": name, "readout": group, "left": [lk, left], "right": [rk, right],
                     "mean": m, "se": s, "label": LABEL,
                     "paired_differences": [{"seed": seed, "difference": values[lk, left, seed]-values[rk, right, seed]}
                                            for seed in record['protocol']['seeds']]})
    return rows


def save_execution(record, frozen, root=ROOT, quick=False):
    """Validate complete raw coverage before writing compact seed summaries."""
    validate(record)
    stage = "quick" if quick else "full"
    raw_path = f"{RAW}/{stage}_experiment.json"
    write(root/raw_path, record)
    saved = read_json(root/raw_path)
    compact = {k: v for k, v in saved.items() if k != "trials"}
    compact["schema_version"] = "two_female_v1.summary.1"
    compact["trials"] = [{k: v for k, v in t.items() if k != "windows"} for t in saved["trials"]]
    compact.update(label=LABEL, raw_record={"path": raw_path, "sha256": sha256(root/raw_path)},
                   freeze_sha256=sha256(root/FREEZE), populations=frozen["populations"],
                   condition_summaries=summarize(saved), descriptive_contrasts=contrasts(saved))
    if not quick:
        baseline = read_json(root/BASELINE)
        compact["FAFB_source"] = {"path": BASELINE, "sha256": sha256(root/BASELINE),
                                  "condition_summaries": summarize(baseline)}
        compact["comparisons"] = comparisons(baseline, saved)
        compact["quick"] = {"elapsed_seconds": read_json(root/f"{RAW}/quick_summary.json")["elapsed_seconds"]}
    destination = f"{RAW}/quick_summary.json" if quick else "records/two_female_v1_experiment.json"
    save_json(root/destination, compact)
    return compact


def render(record):
    def fmt(value):
        return f"{value['mean']:.6g} +/- {value['se']:.6g}"

    lines = ["# Two female individuals: descriptive baseline", "", LABEL, "",
             "## Preregistration (verbatim)", "", record["protocol"]["text"], "",
             "## Execution", "", f"Quick: {record['quick']['elapsed_seconds']:.3f} s. "
             f"Full: {record['elapsed_seconds']:.3f} s. CUDA fast_gpu; both kernels; 80 full trials.",
             f"Preregistration SHA-256: `{record['protocol']['sha256']}`.",
             f"Raw windows and drive slices: `{record['raw_record']['path']}` "
             f"(SHA-256 `{record['raw_record']['sha256']}`).", "",
             "## Selectors in both graphs", "", selector_table(record["populations"]), "",
             "## Condition summaries and network ignition", "",
             "Hz per cell; network Hz per neuron. SE is across seeds. Warm-up excluded.", "",
             "| Dataset | Kernel | Condition | vpoDN mean +/- SE | pC1 mean +/- SE | Network mean +/- SE | Ignition fraction |",
             "|---|---|---|---:|---:|---:|---:|"]
    for dataset, summaries in (("FAFB", record["FAFB_source"]["condition_summaries"]),
                                ("BANC", record["condition_summaries"])):
        for row in summaries:
            rates = row["rates_hz"]
            lines.append(f"| {dataset} | {row['kernel']} | {row['condition']} | " +
                         " | ".join(fmt(rates[g]) for g in ("vpoDN", "pC1", "network")) +
                         f" | {row['ignition_fraction']:.6g} |")
    lines += ["", "## FAFB versus BANC", "",
              "Paired SE uses differences at the same seed number. The ratio is descriptive, without a threshold.",
              "Seed pairing is a computational convention, not paired biological replication; graph sizes and target counts differ.", "",
              "| Kernel | Condition | Readout | FAFB mean +/- SE | BANC mean +/- SE | FAFB - BANC +/- paired SE | Absolute difference / paired SE |",
              "|---|---|---|---:|---:|---:|---:|"]
    for row in record["comparisons"]:
        ratio = row["absolute_difference_over_paired_se"]
        lines.append(f"| {row['kernel']} | {row['condition']} | {row['readout']} | {fmt(row['FAFB'])} | "
                     f"{fmt(row['BANC'])} | {fmt(row['paired_difference'])} | " +
                     (f"{ratio:.6g}" if ratio is not None else row["ratio_status"]) + " |")
    lines += ["", "## BANC paired contrasts", "", LABEL, "",
              "| Contrast | Readout | Left | Right | Difference +/- SE | Label |", "|---|---|---|---|---:|---|"]
    for row in record["descriptive_contrasts"]:
        lines.append(f"| {row['name']} | {row['readout']} | {' '.join(row['left'])} | {' '.join(row['right'])} | "
                     f"{fmt(row)} | descriptive |")
    lines += ["", "## Scope, deviations and verification", "",
              "The specified BANC NPZ was retained intact. central_brain_intrinsic filters pC1 only; "
              "JO-A/B are sensory, SAG is ascending and DNp37 is descending. "
              "The graph contains other superclasses, including ventral nerve cord cells.",
              "The cited central_brain_intrinsic note was absent from the local dictionary E3 report. "
              "The stored population contract is proofread OR roughly_proofread with status/glia exclusions. "
              "4,344,932 BANC synapses were outside that population. Raw synapse totals are not compared as equal coverage.",
              "FAFB uses four SAG candidates (AN_SMP_2 and AN_FLA_SMP_2); BANC uses two ANXXX983 cells. "
              "BANC DNp37 is present (two cells). Population, annotation and sign-source differences confound attribution "
              "of any output difference to an individual alone.",
              "Song conditions are stress tests of the existing ear front end, not measurements of female hearing. "
              "No calibration or gain changes were made.",
              "these readouts do not establish hearing, refusal or mating", "",
              "The original FAFB result was read from its saved JSON and was not rerun. "
              "No runner refactor; the existing runner.run is called directly. "
              "No restricted source tree was inspected; only the specified dependency directory was used by the runtime. "
              "No git writes were executed.",
              "Acceptance commands, intentional-failure probe, exit codes, pass/fail counts and file integrity checks "
              "are in records/two_female_v1_checks.json.", ""]
    return "\n".join(lines)


def execute(root=ROOT, quick=False):
    frozen = verify_freeze(root)
    if not quick:
        preliminary = read_json(root/f"{RAW}/quick_summary.json")
        if preliminary["freeze_sha256"] != sha256(root/FREEZE):
            raise ValueError("Quick record belongs to another freeze")
    graph = load(root/"build/graph_banc.npz")
    selected = select_groups(graph, read_json(root/"build/dictionary_banc.json"), "banc")
    if not len(selected["vpoDN"]):
        raise ValueError("Frozen BANC DNp37 unexpectedly absent; readout unavailable")
    started = datetime.now(timezone.utc).isoformat()
    result = runner.run(protocol(root, quick), graph, selected, device="cuda",
                        graph_sha=frozen["populations"]["banc"]["sha256"], progress=True)
    result["started_utc"] = started
    result["completed_utc"] = datetime.now(timezone.utc).isoformat()
    result["dictionary"]["SAG_override"] = "^ANXXX983$"
    result["dictionary"]["snapshot_sha256"] = frozen["sha256"]["build/dictionary_banc.json"]
    result["source_sha256"]["two_female.py"] = sha256(Path(__file__))
    compact = save_execution(result, frozen, root, quick)
    if not quick:
        (root/"records/two_female_v1_report.md").write_text(
            render(read_json(root/"records/two_female_v1_experiment.json")), encoding="utf-8")
    print(json.dumps({"mode": "quick" if quick else "full", "elapsed_seconds": compact["elapsed_seconds"]}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    stage = parser.add_mutually_exclusive_group()
    stage.add_argument("--freeze", action="store_true")
    stage.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    if args.freeze:
        frozen = freeze()
        print("Preregistration frozen:", frozen["sha256"][PREREG])
    else:
        execute(quick=args.quick)


if __name__ == "__main__":
    main()
