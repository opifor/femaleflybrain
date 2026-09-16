"""Versioned JSON records and content fingerprints."""
import hashlib
import json
from pathlib import Path
import platform
import numpy as np
import scipy
import torch

SCHEMA_VERSION = "1"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def environment(device):
    return {"python": platform.python_version(), "numpy": np.__version__,
            "scipy": scipy.__version__, "torch": torch.__version__,
            "cuda": torch.version.cuda, "device": device,
            "gpu": torch.cuda.get_device_name() if device == "cuda" else None}


def validate(record):
    required = {"schema_version", "protocol", "graph", "dictionary", "environment", "ear", "trials", "elapsed_seconds"}
    if not required <= record.keys() or record["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Invalid record schema")
    p = record["protocol"]
    expected = {(k, c, s) for k in ("shiu", "jump") for c in p["conditions"] for s in p["seeds"]}
    found = [(t["kernel"], t["condition"], t["seed"]) for t in record["trials"]]
    if len(found) != len(expected) or set(found) != expected:
        raise ValueError("Missing or duplicate paired trials")
    for t in record["trials"]:
        if len(t["windows"]) != p["windows"] or set(t["rates_hz"]) != {"vpoDN", "pC1", "network"}:
            raise ValueError("Invalid trial outputs")
        for w in t["windows"]:
            if len(w["drive_slices"]) != 10:
                raise ValueError("Missing 5 ms drive slices")
            for drive in w["drive_slices"]:
                if set(drive) != {"requested_hz", "sampled_hz", "delivered_hz"}:
                    raise ValueError("Missing drive statistics")
        if not all(np.isfinite(list(t["rates_hz"].values()))):
            raise ValueError("Nonfinite rates")
    json.dumps(record, allow_nan=False)
    return record


def write(path, record):
    validate(record)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(record, indent=2, allow_nan=False)+"\n", encoding="utf-8")
