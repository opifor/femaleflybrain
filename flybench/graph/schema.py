"""NPZ schema v1; CSR rows are presynaptic, values are signed counts."""

import json
import numpy as np

SCHEMA_VERSION = "1"


def load(path):
    """Load without pickle; decode scalar JSON metadata into a dictionary."""
    with np.load(path, allow_pickle=False) as archive:
        graph = {key: archive[key] for key in archive.files}
    graph["meta"] = json.loads(str(graph["meta"]))
    return graph


def validate(graph):
    """Check structural and count/sign invariants without a dense matrix."""
    n = len(graph["body_id"])
    ptr, idx, count = (graph[k] for k in ("indptr", "indices", "count"))
    if graph["body_id"].dtype != np.dtype("int64"):
        raise ValueError("body_id must be int64")
    if n > 1 and np.any(graph["body_id"][1:] <= graph["body_id"][:-1]):
        raise ValueError("body_id must be sorted and unique")
    if ptr.dtype != np.dtype("int32") or idx.dtype != np.dtype("int32"):
        raise ValueError("CSR indices must be int32")
    if count.dtype != np.dtype("int32") or graph["data"].dtype != np.dtype("int32"):
        raise ValueError("counts and signed data must be int32")
    if len(ptr) != n + 1 or ptr[0] != 0 or ptr[-1] != len(idx) or np.any(np.diff(ptr) < 0):
        raise ValueError("invalid CSR indptr")
    if len(count) != len(idx) or len(graph["data"]) != len(idx):
        raise ValueError("edge arrays differ in length")
    if len(idx) and (idx.min() < 0 or idx.max() >= n):
        raise ValueError("CSR column out of bounds")
    for key in ("sign", "type", "side", "nt", "nt_conf", "superclass", "class"):
        if key in graph and len(graph[key]) != n:
            raise ValueError(f"wrong neuron array length: {key}")
    if not np.isin(graph["sign"], [-1, 0, 1]).all():
        raise ValueError("invalid sign")
    if not np.isin(graph["side"], ["L", "R", "M", ""]).all():
        raise ValueError("invalid side")
    if np.any(count < 1):
        raise ValueError("counts must be positive")
    # Bound temporary memory even for very large segment-level graphs.
    for start in range(0, len(idx), 1_000_000):
        stop = min(start + 1_000_000, len(idx))
        src = np.searchsorted(ptr, np.arange(start, stop), side="right") - 1
        if not np.array_equal(graph["data"][start:stop], graph["sign"][src] * count[start:stop]):
            raise ValueError("signed data does not equal sign[src] * count")
    return True
