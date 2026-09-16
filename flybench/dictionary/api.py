"""Return CSR indices, never body IDs, for the graph used by a simulation."""

import os
from pathlib import Path

from flybench.graph.schema import load
from .entries import DATASETS, entries


def graph_path(dataset, data_dir=None):
    if dataset not in DATASETS:
        raise ValueError(f"dataset must be one of {DATASETS}, got {dataset!r}")
    root = Path(data_dir if data_dir is not None else os.environ.get("FLYBENCH_DATA", "build"))
    return root / f"graph_{dataset}.npz"


def groups(dataset, *, data_dir=None, graph=None):
    """Map every group name to increasing int64 CSR indices (absent => empty).

    Use FLYBENCH_DATA for the directory containing graph_*.npz, or data_dir.
    A preloaded graph avoids repeat I/O and must be the simulator's graph.
    Groups can overlap; they are not a partition of the neuron population.
    """
    definitions = entries(dataset)
    if graph is None:
        graph = load(graph_path(dataset, data_dir))
    return {entry.name: entry.selector.select(graph) for entry in definitions}


def drive_targets(dataset, name, *, data_dir=None, graph=None):
    """Return a group's indices; raise KeyError for unknown, ValueError for absent.

    All roles are addressable for perturbation experiments. Callers decide
    whether a proxy is appropriate; confidence is in entries/build reports.
    """
    definition = next((entry for entry in entries(dataset) if entry.name == name), None)
    if definition is None:
        raise KeyError(f"unknown dictionary group {name!r} for {dataset}")
    if graph is None:
        graph = load(graph_path(dataset, data_dir))
    indices = definition.selector.select(graph)
    if not len(indices):
        raise ValueError(f"dictionary group {name!r} is absent in {dataset}")
    return indices
