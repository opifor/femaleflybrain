"""All numerical report content is derived from the saved JSON record."""
import json
from pathlib import Path
import numpy as np
from .record import validate


def mean_se(values):
    x = np.asarray(values, dtype=float)
    return float(x.mean()), float(x.std(ddof=1)/np.sqrt(len(x)))


def contrast(record, group, left, right, left_kernel="shiu", right_kernel="shiu", descriptive=False):
    values = {(t["kernel"], t["condition"], t["seed"]): t["rates_hz"][group] for t in record["trials"]}
    delta = [values[left_kernel, left, s]-values[right_kernel, right, s] for s in record["protocol"]["seeds"]]
    mean, se = mean_se(delta)
    return mean, se, "descriptive" if descriptive else ("supported" if mean > 2*se else "not supported")


def render(record):
    validate(record)
    p = record["protocol"]
    lines = ["# Experiment report", "", "## Preregistration (verbatim)", "", p["text"], "", "## Recorded execution", "",
             f"Protocol SHA256: {p['sha256']}. Graph SHA256: {record['graph']['sha256']}.",
             f"Mode: {p['mode']}; elapsed: {record['elapsed_seconds']:.3f} s. Units: Hz per cell.", "",
             "| Kernel | Condition | Seed | vpoDN | pC1 | Network | Ignition fraction |", "|---|---|---:|---:|---:|---:|---:|"]
    for t in record["trials"]:
        r = t["rates_hz"]
        lines.append(f"| {t['kernel']} | {t['condition']} | {t['seed']} | {r['vpoDN']:.6g} | {r['pC1']:.6g} | {r['network']:.6g} | {t['ignition_fraction']:.6g} |")
    lines += ["", "## Condition summaries", "", "| Kernel | Condition | vpoDN mean ± SE | pC1 mean ± SE | Network mean ± SE | Ignition fraction |", "|---|---|---:|---:|---:|---:|"]
    for k in ("shiu", "jump"):
        for c in p["conditions"]:
            ts = [t for t in record["trials"] if t["kernel"] == k and t["condition"] == c]
            stats = ["%.6g ± %.6g" % mean_se([t["rates_hz"][g] for t in ts]) for g in ("vpoDN", "pC1", "network")]
            lines.append(f"| {k} | {c} | " + " | ".join(stats) + f" | {np.mean([t['ignition_fraction'] for t in ts]):.6g} |")
    lines += ["", "## Paired contrasts", "", "| Prediction / contrast | Difference ± SE | Verdict |", "|---|---:|---|"]
    verdicts = []
    for label, g, a, b in (("P1", "vpoDN", "virgin_song", "mated_song"), ("P2", "vpoDN", "virgin_song", "virgin_silence"), ("P3", "pC1", "virgin_song", "mated_song")):
        m, s, v = contrast(record, g, a, b)
        verdicts.append(f"{label}: {v}")
        lines.append(f"| {label} ({g}) | {m:.6g} ± {s:.6g} | {v} |")
    for g in ("vpoDN", "pC1"):
        for k in ("shiu", "jump"):
            m, s, v = contrast(record, g, "mated_song", "mated_silence", k, k, True)
            lines.append(f"| P4 {k} {g}: mated song minus silence | {m:.6g} ± {s:.6g} | {v} |")
        for c in p["conditions"]:
            m, s, v = contrast(record, g, c, c, "jump", "shiu", True)
            lines.append(f"| P4 {c} {g}: jump minus shiu | {m:.6g} ± {s:.6g} | {v} |")
    lines += ["", "## Result", "", "; ".join(verdicts)+" under the preregistered Shiu criterion.",
              "Quick results are preliminary." if p["mode"] == "quick" else "The full paired-seed execution is reported above.",
              "Kernel differences and ignition fractions are descriptive. No calibration was applied.",
              "These isolated-brain neuronal outputs do not demonstrate behavioural refusal or mating.", ""]
    hearing = contrast(record, "vpoDN", "virgin_song", "virgin_silence")
    lines += [f"Adding song to the virgin condition changed vpoDN by {hearing[0]:.6g} ± {hearing[1]:.6g} Hz/cell (paired SE).",
              "The auditory prediction was not supported; reproductive-state effects alone do not establish song-dependent receptivity."
              if hearing[2] == "not supported" else "The auditory prediction met the preregistered neuronal criterion.", ""]
    return "\n".join(lines)


def write_from_json(source, destination):
    record = json.loads(Path(source).read_text(encoding="utf-8"))
    Path(destination).write_text(render(record), encoding="utf-8")
