"""Versioned sign policy.

Shiu et al. (2024), https://doi.org/10.1038/s41586-024-07763-9,
supports treating GABA and glutamate as inhibitory. Unlike that paper's
excitatory treatment of monoamines, flybench v1 assigns them zero by design.
Changing any assignment requires a new version; never silently edit v1.
"""

import numpy as np

SIGN_RULE = "v1"
_ALIASES = {"ach": "acetylcholine", "gaba": "gaba", "glut": "glutamate",
            "da": "dopamine", "ser": "serotonin", "oct": "octopamine"}
_V1 = {"acetylcholine": 1, "gaba": -1, "glutamate": -1,
       "dopamine": 0, "serotonin": 0, "octopamine": 0, "other": 0, "": 0}


def normalize(value):
    """Normalize known abbreviations; retain unknown labels for auditing."""
    value = str(value).strip().lower() if value is not None else ""
    return _ALIASES.get(value, value)


def signs(nt, rule=SIGN_RULE):
    if rule != SIGN_RULE:
        raise ValueError(f"Unknown sign rule: {rule}")
    return np.fromiter((_V1.get(normalize(v), 0) for v in nt), dtype=np.int8,
                       count=len(nt))
