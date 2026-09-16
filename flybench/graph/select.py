"""Select CSR neuron indices, with AND semantics and regex search."""

import re
import numpy as np


def where(graph, *, type_re=None, side=None, superclass=None):
    """Return ordered int64 indices matching all supplied predicates.

    graph is a mapping returned by schema.load or an open numpy NpzFile.
    Missing superclass metadata raises KeyError instead of matching everything.
    """
    mask = np.ones(len(graph["body_id"]), dtype=bool)
    if type_re is not None:
        pattern = re.compile(type_re)
        mask &= np.fromiter((pattern.search(str(v)) is not None for v in graph["type"]),
                            dtype=bool, count=len(mask))
    if side is not None:
        if side not in ("L", "R", "M", ""):
            raise ValueError("side must be L, R, M, or empty")
        mask &= graph["side"] == side
    if superclass is not None:
        mask &= graph["superclass"] == superclass
    return np.flatnonzero(mask)
