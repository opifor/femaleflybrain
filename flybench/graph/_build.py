"""Shared column-projected readers and exact-count CSR construction."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as parquet
from scipy.sparse import coo_matrix

from .schema import SCHEMA_VERSION, validate
from .signs import SIGN_RULE, normalize, signs

CHUNK = 1_000_000
INT32_MAX = np.iinfo(np.int32).max


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def data_root(data_dir):
    value = data_dir if data_dir is not None else os.environ.get("FLYBENCH_DATA")
    if not value:
        raise ValueError("Specify data_dir/--data or FLYBENCH_DATA")
    return Path(value)


def frame(path, columns, id_column, optional=()):
    """Read only requested columns; reject ambiguous annotation identities."""
    if optional:
        if path.suffix == ".feather":
            with pa.memory_map(str(path), "r") as handle:
                available = pa.ipc.open_file(handle).schema.names
        else:
            available = pd.read_csv(path, nrows=0).columns
        columns = [c for c in columns if c not in optional or c in available]
    if path.suffix == ".feather":
        result = feather.read_table(path, columns=columns, memory_map=True).to_pandas()
    else:
        result = pd.read_csv(path, usecols=columns, dtype={id_column: "int64"})
    result[id_column] = result[id_column].astype("int64")
    if result[id_column].duplicated().any():
        raise ValueError(f"Duplicate {id_column} in {path.name}")
    return result.set_index(id_column)


def edge_batches(path, columns):
    """Bounded CSV/parquet batches; Feather explicitly projects columns."""
    if path.suffix == ".feather":
        table = feather.read_table(path, columns=columns, memory_map=True)
        yield from table.to_batches(max_chunksize=CHUNK)
    elif path.suffix == ".parquet":
        yield from parquet.ParquetFile(path).iter_batches(batch_size=CHUNK, columns=columns)
    else:
        for batch in pd.read_csv(path, usecols=columns, dtype={c: "int64" for c in columns},
                                 chunksize=CHUNK):
            yield pa.RecordBatch.from_pandas(batch[columns], preserve_index=False)


def canonical_side(value):
    return {"l": "L", "left": "L", "r": "R", "right": "R", "m": "M",
            "midline": "M", "center": "M", "central": "M"}.get(str(value).strip().lower(), "")


def peak_rss_bytes():
    """OS process high-water RSS/working set (includes imports, not just builder)."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (key, ctypes.c_size_t) for key in (
                    "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
        counter = Counters()
        counter.cb = ctypes.sizeof(counter)
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counter), counter.cb):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(counter.PeakWorkingSetSize)
    import resource
    import sys
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024))


def build_graph(*, root, out, dataset, version, nodes, edge_name, edge_columns,
                source_names, min_syn, started, population, details=None):
    if isinstance(min_syn, bool) or not isinstance(min_syn, (int, np.integer)) or min_syn < 1:
        raise ValueError("min_syn must be an integer >= 1")
    out = Path(out)
    if out.suffix != ".npz":
        raise ValueError("out must end in .npz")
    sources = [root / name for name in source_names]
    if out.exists() and any(os.path.samefile(out, p) for p in sources):
        raise ValueError("Output aliases an input file")
    # Universe is explicit and stays fixed across min_syn thresholds.
    nodes = nodes.sort_index()
    ids = nodes.index.to_numpy(dtype=np.int64)
    n = len(ids)
    if not n or n > INT32_MAX:
        raise ValueError("Neuron count outside int32 CSR capacity")
    graph = {"body_id": ids}
    for key in ("type", "side", "nt", "superclass", "class"):
        values = nodes[key].fillna("").astype(str) if key in nodes else pd.Series("", index=nodes.index)
        if key == "nt":
            values = values.map(normalize)
        elif key == "side":
            values = values.map(canonical_side)
        graph[key] = values.to_numpy(dtype=str)
    graph["sign"] = signs(graph["nt"])
    if "nt_conf" in nodes:
        graph["nt_conf"] = nodes["nt_conf"].to_numpy(dtype=np.float32)
    rows, cols, counts = [], [], []
    input_rows = input_synapses = outside_rows = outside_synapses = 0
    for batch in edge_batches(root / edge_name, edge_columns):
        pre, post, weight = [batch.column(batch.schema.get_field_index(c)).cast(pa.int64()).to_numpy()
                             for c in edge_columns]
        if any(batch.column(batch.schema.get_field_index(c)).null_count for c in edge_columns):
            raise ValueError("Null endpoint/count in connectivity")
        if np.any(weight < 1) or np.any(weight > INT32_MAX):
            raise ValueError("Raw counts must be positive int32 values")
        src, dst = np.searchsorted(ids, pre), np.searchsorted(ids, post)
        keep = (src < n) & (dst < n)
        keep &= (ids[np.minimum(src, n - 1)] == pre) & (ids[np.minimum(dst, n - 1)] == post)
        input_rows += len(weight)
        input_synapses += int(weight.sum(dtype=np.int64))
        outside_rows += int((~keep).sum())
        outside_synapses += int(weight[~keep].sum(dtype=np.int64))
        rows.append(src[keep].astype(np.int32))
        cols.append(dst[keep].astype(np.int32))
        counts.append(weight[keep].astype(np.int32))
    row = np.concatenate(rows) if rows else np.empty(0, np.int32)
    col = np.concatenate(cols) if cols else np.empty(0, np.int32)
    raw = np.concatenate(counts) if counts else np.empty(0, np.int32)
    del rows, cols, counts
    if len(raw) > INT32_MAX:
        raise ValueError("Edge count outside int32 CSR capacity")
    # int64 accumulation catches duplicate-pair overflow before final int32 cast.
    matrix = coo_matrix((raw.astype(np.int64), (row, col)), shape=(n, n)).tocsr()
    del row, col, raw
    if matrix.nnz and matrix.data.max() > INT32_MAX:
        raise ValueError("Aggregated synapse count overflows int32")
    before_edges = matrix.nnz
    before_synapses = int(matrix.data.sum(dtype=np.int64))
    matrix.data[matrix.data < min_syn] = 0
    matrix.eliminate_zeros()
    graph["indptr"] = matrix.indptr.astype(np.int32, copy=False)
    graph["indices"] = matrix.indices.astype(np.int32, copy=False)
    graph["count"] = matrix.data.astype(np.int32)
    del matrix
    graph["data"] = graph["count"].copy()
    for start in range(0, len(graph["data"]), CHUNK):
        stop = min(start + CHUNK, len(graph["data"]))
        src = np.searchsorted(graph["indptr"], np.arange(start, stop), side="right") - 1
        graph["data"][start:stop] *= graph["sign"][src]
    nt_names, nt_counts = np.unique(graph["nt"], return_counts=True)
    meta = dict(schema_version=SCHEMA_VERSION, dataset=dataset, version=version,
                min_syn=int(min_syn), sign_rule=SIGN_RULE,
                created_utc=datetime.now(timezone.utc).isoformat(),
                neuron_count=n, edge_count=len(graph["count"]),
                synapse_count=int(graph["count"].sum(dtype=np.int64)),
                nt_distribution=dict(zip(nt_names.tolist(), nt_counts.tolist())),
                type_labeled_fraction=float(np.count_nonzero(graph["type"] != "") / n),
                population=population, input_rows=input_rows, input_synapses=input_synapses,
                outside_population_rows=outside_rows, outside_population_synapses=outside_synapses,
                below_min_syn_edges=before_edges - len(graph["count"]),
                below_min_syn_synapses=before_synapses - int(graph["count"].sum(dtype=np.int64)),
                aggregated_duplicate_rows=input_rows - outside_rows - before_edges,
                sources=[dict(name=p.name, sha256=sha256(p)) for p in sources],
                nt_policy=details or {}, license="CC-BY-4.0")
    validate(graph)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Append metadata after writing arrays, so elapsed includes compression and I/O.
    import zipfile
    import io
    temporary = out.with_name(out.name + ".partial")
    try:
        with open(temporary, "wb") as handle:
            np.savez_compressed(handle, **graph)
        meta["elapsed_seconds"] = time.perf_counter() - started
        meta["peak_rss_bytes"] = peak_rss_bytes()
        meta["memory_measurement"] = "OS process lifetime peak RSS/working set; fresh CLI process recommended"
        encoded = io.BytesIO()
        np.save(encoded, np.asarray(json.dumps(meta, ensure_ascii=False, sort_keys=True)), allow_pickle=False)
        with zipfile.ZipFile(temporary, "a", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("meta.npy", encoded.getvalue())
        os.replace(temporary, out)
    finally:
        if temporary.exists():
            temporary.unlink()
    return meta


def cli(builder, description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--data", help="Data directory; defaults to FLYBENCH_DATA")
    parser.add_argument("--out", required=True)
    parser.add_argument("--min-syn", type=int, default=1)
    args = parser.parse_args()
    print(json.dumps(builder(args.data, args.out, args.min_syn), ensure_ascii=False, indent=2))
