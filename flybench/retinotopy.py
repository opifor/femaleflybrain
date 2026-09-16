"""Exact-ID FAFB column join and an explicitly declared angular convention.

Published hex assignments are preserved. Angles and laterality are design
conventions, not measured optical geometry. No graph edges are read or written.
"""
from dataclasses import dataclass
import re

import numpy as np
import pandas as pd

EYE_HEX_STEP_DEG = 2.0  # Design constant; no biological source.
SIDES = {"left": "L", "right": "R"}


def _integers(values, name):
    """Never route root IDs through floats, including already-rounded floats."""
    result = []
    for value in values:
        if isinstance(value, (bool, float, np.floating)) or not re.fullmatch(
                r"[+-]?\d+", str(value)):
            raise ValueError(f"{name} must contain exact integers")
        number = int(value)
        if not np.iinfo(np.int64).min <= number <= np.iinfo(np.int64).max:
            raise ValueError(f"{name} outside int64")
        result.append(number)
    return np.asarray(result, dtype=np.int64)


@dataclass(frozen=True)
class Column:
    hemisphere: str
    column_id: int
    p: int
    q: int
    u0: float
    v0: float

    @property
    def key(self):
        return self.hemisphere, self.column_id


@dataclass(frozen=True)
class ColumnMap:
    columns: tuple[Column, ...]

    def __post_init__(self):
        object.__setattr__(self, "columns", tuple(self.columns))
        if not self.columns or not all(isinstance(c, Column) for c in self.columns):
            raise ValueError("A nonempty sequence of Column objects is required")
        if len(set(self.keys)) != len(self.columns):
            raise ValueError("Duplicate column keys")
        for c in self.columns:
            if c.hemisphere not in SIDES:
                raise ValueError("Hemisphere must be left or right")
            _integers([c.column_id, c.p, c.q], "column geometry")
            if not np.isfinite([c.u0, c.v0]).all():
                raise ValueError("Column origins must be finite")

    @property
    def keys(self):
        return tuple(c.key for c in self.columns)

    def angles(self, step_deg=EYE_HEX_STEP_DEG):
        """Return azimuth/elevation degrees; declared convention, uncalibrated."""
        if not np.isfinite(step_deg) or step_deg <= 0:
            raise ValueError("Hex step must be finite and positive")
        az, el = [], []
        for c in self.columns:
            sign = 1 if c.hemisphere == "left" else -1
            az.append(sign * (c.p + c.q / 2 - c.u0) * step_deg)
            el.append((np.sqrt(3) * c.q / 2 - c.v0) * step_deg)
        result = np.asarray(az), np.asarray(el)
        if not all(np.isfinite(a).all() for a in result):
            raise ValueError("Angular geometry overflow")
        return result


@dataclass
class Retinotopy:
    cells: pd.DataFrame
    column_map: ColumnMap
    coverage: dict


def read_assignments(path):
    """Read compressed publication CSV with root IDs kept as decimal strings."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _ranges(frame):
    return {f"{name}_range": ([int(frame[name].min()), int(frame[name].max())]
                              if len(frame) else None)
            for name in ("column_id", "p", "q")}


def join_columns(graph, assignments, visual_types=None):
    """Join annotations by ID without changing graph labels or filling gaps.

    Graph coverage groups use graph type/side. Assignment coverage groups use
    publication labels. Disagreements are counted separately, never reconciled.
    visual_types optionally supplies the publication's candidate inventory.
    """
    required = {"root_id", "hemisphere", "type", "column_id", "x", "y", "p", "q"}
    if not required <= set(assignments.columns):
        raise ValueError("Missing assignment columns")
    a = assignments[list(sorted(required))].copy()
    for name in ("root_id", "column_id", "x", "y", "p", "q"):
        a[name] = _integers(a[name], name)
    if a.root_id.duplicated().any():
        raise ValueError("Duplicate assignment root IDs")
    if not a.hemisphere.isin(SIDES).all() or a["type"].isna().any() or (a["type"] == "").any():
        raise ValueError("Missing or invalid assignment labels")
    if (a.groupby(["hemisphere", "column_id"])[["p", "q"]].nunique() > 1).any().any():
        raise ValueError("Conflicting hex coordinates for column key")
    ids = _integers(graph["body_id"], "body_id")
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate graph body IDs")
    g = pd.DataFrame({"root_id": ids, "graph_index": np.arange(len(ids)),
                      "graph_type": graph["type"], "graph_side": graph["side"]})
    if g[["graph_type", "graph_side"]].isna().any().any():
        raise ValueError("Graph labels must use empty strings for missing values")
    if not g.graph_side.isin(("L", "R", "M", "")).all():
        raise ValueError("Invalid graph side")
    # Keep integer coordinates exact even in the left join's missing rows.
    for name in ("column_id", "x", "y", "p", "q"):
        a[name] = a[name].astype("Int64")
    cells = g.merge(a, on="root_id", how="left", validate="one_to_one", sort=False)
    cells["assigned"] = cells.hemisphere.notna()
    matched = a[a.root_id.isin(ids)]
    graph_rows = []
    for (typ, side), group in cells.groupby(["graph_type", "graph_side"], sort=True):
        hit = group[group.assigned]
        graph_rows.append({"type": str(typ), "hemisphere": {"L": "left", "R": "right"}.get(side, side),
                           "graph_cells": len(group), "assigned": len(hit),
                           "unassigned": len(group) - len(hit), **_ranges(hit)})
    assignment_rows = []
    for (typ, hemi), group in a.groupby(["type", "hemisphere"], sort=True):
        count = int(group.root_id.isin(ids).sum())
        assignment_rows.append({"type": str(typ), "hemisphere": str(hemi),
                                "file_cells": len(group), "graph_matched": count,
                                "outside_graph": len(group) - count, **_ranges(group)})
    column_records = a.drop_duplicates(["hemisphere", "column_id"])
    matched_keys = set(zip(matched.hemisphere, matched.column_id))
    columns, origins = [], {}
    for hemi, group in column_records.groupby("hemisphere", sort=True):
        u = group.p.astype(float) + group.q.astype(float) / 2
        v = np.sqrt(3) * group.q.astype(float) / 2
        u0, v0 = float(u.min() - .5), float((v.min() + v.max()) / 2)
        origins[hemi] = {"u0": u0, "v0": v0}
        for row in group.sort_values("column_id").itertuples():
            if (hemi, row.column_id) in matched_keys:
                columns.append(Column(hemi, int(row.column_id), int(row.p), int(row.q), u0, v0))
    assigned = cells[cells.assigned]
    publication_candidates = set()
    if visual_types is not None:
        if not {"root_id", "type", "category"} <= set(visual_types.columns):
            raise ValueError("Missing visual inventory columns")
        visual_ids = _integers(visual_types.root_id, "visual root_id")
        mask = np.isin(visual_ids, ids) & visual_types.category.isin(("intrinsic", "retinal"))
        publication_candidates = set(visual_types.loc[mask, "type"])
    named_candidates = {str(t) for t in g.graph_type.unique()
                        if re.match(r"^(?:R|L|Mi|Tm|T4|T5|C|T)\d", str(t))}
    available = set(a["type"])
    missing_candidates = []
    for typ in sorted((publication_candidates | named_candidates) - available):
        subset = g[g.graph_type == typ]
        if subset.empty:
            continue
        missing_candidates.append({"type": typ, "graph_cells": len(subset),
                                   "publication_intrinsic_or_retinal": typ in publication_candidates,
                                   "name_pattern_candidate": typ in named_candidates})
    coverage = {"graph_cells": len(g), "assignment_rows": len(a),
                "matched_cells": len(matched), "assignment_outside_graph": len(a)-len(matched),
                "graph_unassigned_all_types": len(g)-len(matched),
                "assignment_type_count": int(a["type"].nunique()),
                "matched_assignment_type_count": int(matched["type"].nunique()),
                "mapped_columns": len(columns), "origins_full_assignment": origins,
                "type_disagreements": int((assigned.graph_type != assigned["type"]).sum()),
                "side_disagreements": int((assigned.graph_side != assigned.hemisphere.map(SIDES)).sum()),
                "graph_type_hemisphere": graph_rows, "assignment_type_hemisphere": assignment_rows,
                "columnar_candidates_absent_from_assignment": missing_candidates,
                "candidate_inventory_note": "Intrinsic includes non-columnar cells; naming is heuristic. Neither inventory establishes columnar anatomy.",
                "angular_convention": "declared convention, uncalibrated",
                "laterality": "declared, unverified", **_ranges(a)}
    return Retinotopy(cells, ColumnMap(tuple(columns)), coverage)
