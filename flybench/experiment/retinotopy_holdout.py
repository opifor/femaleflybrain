"""Preregistered anatomical coordinate holdout; no network dynamics."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy
from scipy.sparse import csr_matrix

from flybench.retinotopy import join_columns, read_assignments


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "build/records-raw/eye_v2_e1b"
RECORDS = ROOT / "records"
DIRECTIONS = ("both", "incoming", "outgoing")


def sha256(path, lf=False):
    digest = hashlib.sha256()
    if lf:
        digest.update(Path(path).read_bytes().replace(b"\r\n", b"\n"))
    else:
        with Path(path).open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n",
                          encoding="utf-8", newline="\n")


def check_freeze():
    frozen = json.loads((RECORDS / "eye_v2_e1b_freeze.json").read_text())
    for name in ("preregistration", "graph", "csv"):
        item = frozen[name]
        if sha256(ROOT / item["path"], lf=name == "preregistration") != item["sha256"]:
            raise ValueError(f"Frozen {name} hash mismatch")
    return frozen


def make_folds(n, seed=3801):
    folds = np.empty(n, dtype=np.int8)
    for k, group in enumerate(np.array_split(np.random.default_rng(seed).permutation(n), 5)):
        folds[group] = k
    return folds


def weighted_median(values, weights):
    """Lower weighted median, retaining an observed integer coordinate."""
    values, weights = np.asarray(values), np.asarray(weights, dtype=np.int64)
    if len(values) == 0 or len(values) != len(weights) or np.any(weights <= 0):
        raise ValueError("Nonempty equally sized positive weights required")
    order = np.argsort(values, kind="stable")
    cumulative = np.cumsum(weights[order], dtype=np.int64)
    index = np.searchsorted(cumulative, (int(cumulative[-1]) + 1) // 2, side="left")
    return values[order[index]]


def hex_distance(predicted, reference):
    delta = np.asarray(predicted, dtype=float) - np.asarray(reference, dtype=float)
    return (np.abs(delta[..., 0]) + np.abs(delta[..., 1])
            + np.abs(delta[..., 0] + delta[..., 1])) / 2


def prepare_neighbors(outgoing, hemispheres, folds):
    """Return eligible CSR rows and cross-side incidence/weight accounting."""
    outgoing = outgoing.astype(np.int64).tocsr(copy=True)
    outgoing.data[outgoing.data <= 0] = 0
    outgoing.eliminate_zeros()
    outgoing.sum_duplicates()
    incoming = outgoing.T.tocsr()
    matrices, accounting = {}, {}
    n = len(hemispheres)
    for name, matrix in (("outgoing", outgoing), ("incoming", incoming)):
        rows = np.repeat(np.arange(n), np.diff(matrix.indptr))
        cols = matrix.indices
        cross = hemispheres[rows] != hemispheres[cols]
        training = folds[rows] != folds[cols]
        accounting[name] = {}
        for label, mask in (("all", cross), ("training", cross & training)):
            counts = np.bincount(rows[mask], minlength=n).astype(np.int64)
            weights = np.zeros(n, dtype=np.int64)
            np.add.at(weights, rows[mask], matrix.data[mask])
            accounting[name][label + "_edge_incidences"] = counts
            accounting[name][label + "_synapses"] = weights
        keep = ~cross & training
        matrices[name] = csr_matrix((matrix.data[keep], (rows[keep], cols[keep])), shape=(n, n))
    matrices["both"] = (matrices["outgoing"] + matrices["incoming"]).tocsr()
    accounting["both"] = {key: accounting["incoming"][key] + accounting["outgoing"][key]
                          for key in accounting["incoming"]}
    return matrices, accounting


def predict(matrix, coordinates, targets):
    prediction = np.full((len(targets), 2), np.nan)
    for pos, cell in enumerate(targets):
        start, end = matrix.indptr[cell:cell + 2]
        if start == end:
            continue
        neighbors, weights = matrix.indices[start:end], matrix.data[start:end]
        for axis in (0, 1):
            prediction[pos, axis] = weighted_median(coordinates[neighbors, axis], weights)
    return prediction


def metrics(distances):
    d = np.asarray(distances, dtype=float)
    if np.any(np.isnan(d)) or np.any(d < 0):
        raise ValueError("Distances must be nonnegative or positive infinity")
    finite = d[np.isfinite(d)]
    n = len(d)
    median = float(np.median(d)) if n else float("nan")
    mean = float(np.mean(d)) if n else float("nan")
    return {"n": n, "predictable": len(finite), "unpredictable": n - len(finite),
            "median_d": median if np.isfinite(median) else None,
            "mean_d": mean if np.isfinite(mean) else None,
            "median_nonfinite": not bool(np.isfinite(median)),
            "mean_nonfinite": not bool(np.isfinite(mean)),
            "finite_median_d": float(np.median(finite)) if len(finite) else None,
            "finite_mean_d": float(np.mean(finite)) if len(finite) else None,
            "le1_count": int(np.sum(d <= 1)), "le2_count": int(np.sum(d <= 2)),
            "le1_fraction": float(np.sum(d <= 1) / n) if n else None,
            "le2_fraction": float(np.sum(d <= 2) / n) if n else None}


def summarize(distances, types, hemispheres, folds):
    return {"overall": metrics(distances),
            "by_type": {str(t): metrics(distances[types == t]) for t in sorted(set(types))},
            "by_hemisphere": {str(h): metrics(distances[hemispheres == h])
                              for h in sorted(set(hemispheres))},
            "by_fold": {str(f): metrics(distances[folds == f]) for f in sorted(set(folds))}}


def permute_coordinates(coordinates, hemispheres, rng):
    result = coordinates.copy()
    for hemi in sorted(set(hemispheres)):
        members = np.flatnonzero(hemispheres == hemi)
        result[members] = coordinates[rng.permutation(members)]
    return result


def rank_surrogate(ids, types, hemispheres, coordinates):
    result = np.zeros_like(coordinates)
    for hemi in sorted(set(hemispheres)):
        side = hemispheres == hemi
        lo, hi = coordinates[side, 0].min(), coordinates[side, 0].max()
        for typ in sorted(set(types[side])):
            group = np.flatnonzero(side & (types == typ))
            group = group[np.argsort(ids[group], kind="stable")]
            p = np.linspace(lo, hi, len(group)) if len(group) > 1 else np.array([(lo + hi) / 2])
            result[group, 0] = np.floor(p + .5).astype(np.int64)
    return result


def gate(real, controls, quick=False):
    medians = [c["median_d"] for c in controls]
    passed = (not quick and len(controls) == 5 and real["median_d"] is not None
              and all(m is not None for m in medians)
              and real["median_d"] < min(medians)
              and real["le2_fraction"] is not None and real["le2_fraction"] >= .5)
    return "quick only; not evaluated" if quick else ("map wiring-consistent" if passed else "not shown")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    started = time.perf_counter()
    freeze = check_freeze()
    RAW.mkdir(parents=True, exist_ok=True)
    with np.load(ROOT / freeze["graph"]["path"], allow_pickle=False) as source:
        graph = {key: source[key] for key in ("body_id", "type", "side")}
        mapping = join_columns(graph, read_assignments(ROOT / freeze["csv"]["path"]))
        coverage = mapping.coverage
        if (coverage["matched_cells"], coverage["matched_assignment_type_count"],
                coverage["mapped_columns"], coverage["type_disagreements"],
                coverage["side_disagreements"]) != (45528, 31, 1581, 0, 0):
            raise ValueError("Unexpected assignment coverage or labels")
        cells = mapping.cells.loc[mapping.cells.assigned].sort_values("graph_index")
        selected = cells.graph_index.to_numpy(dtype=np.int64)
        n = len(graph["body_id"])
        full = csr_matrix((source["count"].astype(np.int64), source["indices"], source["indptr"]),
                          shape=(n, n))
        outgoing = full[selected][:, selected].tocsr()
        del full
    coordinates = cells[["p", "q"]].to_numpy(dtype=np.int64)
    hemispheres = cells.hemisphere.to_numpy(dtype=str)
    types = cells["type"].to_numpy(dtype=str)
    ids = cells.root_id.to_numpy(dtype=np.int64)
    folds = make_folds(len(cells))
    targets = np.arange(len(cells))
    if args.quick:
        targets = targets[(folds == 0) & np.isin(types, ["L1", "Mi1", "T4a"])]
    matrices, accounting = prepare_neighbors(outgoing, hemispheres, folds)
    prefix = "quick" if args.quick else "full"
    raw = {"body_id": ids, "graph_index": selected, "type": types,
           "hemisphere": hemispheres, "fold": folds, "published_pq": coordinates,
           "target_assigned_index": targets}
    results = {"mode": prefix, "started_utc": datetime.now(timezone.utc).isoformat(),
               "preregistration_sha256": freeze["preregistration"]["sha256"],
               "population": {"assigned": len(cells), "types": len(set(types)),
                              "columns": len(mapping.column_map.columns),
                              "scored": len(targets), "fold_sizes": np.bincount(folds).tolist()},
               "versions": {"python": platform.python_version(), "numpy": np.__version__,
                            "scipy": scipy.__version__},
               "cross_hemisphere": {}, "real": {}, "permutations": [],
               "rank_surrogate": {}, "deviations": []}
    for direction in DIRECTIONS:
        results["cross_hemisphere"][direction] = {
            key: {"overall": int(value[targets].sum()),
                  "by_type": {str(t): int(value[targets][types[targets] == t].sum())
                              for t in sorted(set(types[targets]))}}
            for key, value in accounting[direction].items()}
        for key, value in accounting[direction].items():
            raw[f"cross_{direction}_{key}"] = value

    def evaluate(coords, label):
        answer = {}
        raw[label + "_coordinates"] = coords
        for direction in DIRECTIONS:
            prediction = predict(matrices[direction], coords, targets)
            distance = np.full(len(targets), np.inf)
            valid = np.isfinite(prediction).all(axis=1)
            distance[valid] = hex_distance(prediction[valid], coords[targets][valid])
            answer[direction] = summarize(distance, types[targets], hemispheres[targets], folds[targets])
            raw[f"{label}_{direction}_prediction"] = prediction
            raw[f"{label}_{direction}_distance"] = distance
        print(label, json.dumps(answer["both"]["overall"], allow_nan=False), flush=True)
        return answer

    results["real"] = evaluate(coordinates, "real")
    rng = np.random.default_rng(3802)
    for replicate in range(5):
        results["permutations"].append(evaluate(
            permute_coordinates(coordinates, hemispheres, rng), f"permutation_{replicate + 1}"))
    rank = rank_surrogate(ids, types, hemispheres, coordinates)
    results["rank_surrogate"] = evaluate(rank, "rank_surrogate")
    results["rank_surrogate_to_publication"] = summarize(
        hex_distance(rank[targets], coordinates[targets]), types[targets], hemispheres[targets], folds[targets])
    results["legacy_eye"] = "not comparable: azimuth output has no p,q; surrogate is descriptive only"
    results["gate"] = gate(results["real"]["both"]["overall"],
                           [r["both"]["overall"] for r in results["permutations"]], args.quick)
    results["distance_missing_policy"] = "Unpredictable = positive infinity; fractions include all targets"
    results["interpretation"] = "consistency, not independent validation"
    np.savez_compressed(RAW / f"{prefix}_cells.npz", **raw)
    check_freeze()
    results["elapsed_seconds"] = time.perf_counter() - started
    write_json(RAW / f"{prefix}_results.json", results)
    if not args.quick:
        write_json(RECORDS / "eye_v2_e1b_results.json", results)
    print("gate:", results["gate"], "seconds:", results["elapsed_seconds"], flush=True)


if __name__ == "__main__":
    main()
