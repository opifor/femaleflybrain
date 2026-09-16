"""Versioned sign policy.

Shiu et al. (2024), https://doi.org/10.1038/s41586-024-07763-9,
supports inhibitory GABA/glutamate and excitatory dopamine/serotonin/octopamine.
shiu2024 version 1 implements these assignments; monoamine-zero version 1
retains the legacy v1 policy. Histamine/tyramine/unclear are unverified by the
Codex-to-parquet audit and conservatively receive zero, not an inferred sign.
Changing any assignment requires a new version; never silently edit a policy.
"""

import numpy as np

SIGN_RULE = "shiu2024"
SIGN_RULE_VERSION = "1"
_ALIASES = {"ach": "acetylcholine", "gaba": "gaba", "glut": "glutamate",
            "da": "dopamine", "ser": "serotonin", "oct": "octopamine"}
_V1 = {"acetylcholine": 1, "gaba": -1, "glutamate": -1,
       "dopamine": 0, "serotonin": 0, "octopamine": 0, "other": 0, "": 0}


def normalize(value):
    """Normalize known abbreviations; retain unknown labels for auditing."""
    value = str(value).strip().lower() if value is not None else ""
    return _ALIASES.get(value, value)


def signs(nt, rule=SIGN_RULE):
    if rule not in ("shiu2024", "monoamine-zero", "v1"):
        raise ValueError(f"Unknown sign rule: {rule}")
    policy = dict(_V1)
    if rule == "shiu2024":
        policy.update(dopamine=1, serotonin=1, octopamine=1)
    return np.fromiter((policy.get(normalize(v), 0) for v in nt), dtype=np.int8,
                       count=len(nt))
