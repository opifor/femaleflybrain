"""Synthetic mapping oracles; no real graph or network simulation."""
import numpy as np
import pandas as pd
import pytest

from flybench.retinotopy import Column, ColumnMap, join_columns, read_assignments


def fixture():
    # Adjacent integers above float64's exact-integer range must remain distinct.
    base = 720575940596125868
    graph = {"body_id": np.array([base+2, base, base+1, base+3], dtype=np.int64),
             "type": np.array(["R1", "L1", "L1", "Tm7"]),
             "side": np.array(["R", "L", "R", "L"])}
    a = pd.DataFrame([
        [str(base), "left", "L1", 9, 0, 0, 0, 0],
        [str(base+1), "right", "L2", 9, 1, 0, 1, 0],
        [str(base+99), "left", "L1", 3, -2, 0, -2, 0],
    ], columns=["root_id", "hemisphere", "type", "column_id", "x", "y", "p", "q"])
    return graph, a


def test_exact_id_join_and_denominators():
    g, a = fixture()
    result = join_columns(g, a)
    assert result.cells.root_id.tolist() == g["body_id"].tolist()
    assert result.cells.assigned.tolist() == [False, True, True, False]
    assert result.cells.loc[1, "column_id"] == 9
    c = result.coverage
    assert (c["matched_cells"], c["assignment_outside_graph"], c["graph_unassigned_all_types"]) == (2, 1, 2)
    assert c["type_disagreements"] == 1 and c["side_disagreements"] == 0
    assert sum(r["assigned"] for r in c["graph_type_hemisphere"]) == 2
    assert {r["type"] for r in c["columnar_candidates_absent_from_assignment"]} == {"R1", "Tm7"}
    assert result.column_map.keys == (("left", 9), ("right", 9))
    az, el = result.column_map.angles()
    # Unmatched column anchors the left origin, rather than the matched subset.
    np.testing.assert_array_equal(az, [5, -1])
    np.testing.assert_array_equal(el, [0, 0])


def test_row_order_does_not_define_geometry():
    g, a = fixture()
    x = join_columns(g, a).column_map
    y = join_columns(g, a.iloc[::-1]).column_map
    assert x == y
    np.testing.assert_array_equal(x.angles(4)[0], 2*x.angles(2)[0])


@pytest.mark.parametrize("column,value", [("root_id", 1.0), ("p", 0.5),
                                           ("hemisphere", "unknown"), ("type", "")])
def test_invalid_assignment_rejected(column, value):
    g, a = fixture()
    a[column] = a[column].astype(object)
    a.loc[0, column] = value
    with pytest.raises(ValueError):
        join_columns(g, a)


def test_duplicate_id_and_conflicting_column_rejected():
    g, a = fixture()
    with pytest.raises(ValueError, match="Duplicate assignment"):
        join_columns(g, pd.concat([a, a.iloc[:1]]))
    a.loc[2, "column_id"] = 9
    with pytest.raises(ValueError, match="Conflicting hex"):
        join_columns(g, a)
    g, a = fixture()
    g["body_id"][1] = g["body_id"][0]
    with pytest.raises(ValueError, match="Duplicate graph"):
        join_columns(g, a)


def test_missing_schema_and_empty_mapping_rejected():
    g, a = fixture()
    with pytest.raises(ValueError, match="Missing assignment"):
        join_columns(g, a.drop(columns="q"))
    a.root_id = ["1", "2", "3"]
    with pytest.raises(ValueError, match="nonempty"):
        join_columns(g, a)


def test_side_mismatch_and_publication_inventory():
    g, a = fixture()
    g["side"][1] = "R"
    v = pd.DataFrame({"root_id": [str(g["body_id"][3])], "type": ["Tm7"], "category": ["intrinsic"]})
    c = join_columns(g, a, v).coverage
    assert c["side_disagreements"] == 1
    row = next(r for r in c["columnar_candidates_absent_from_assignment"] if r["type"] == "Tm7")
    assert row["publication_intrinsic_or_retinal"] and row["graph_cells"] == 1


def test_csv_reader_preserves_ids():
    # In-memory file avoids pytest temporary writes outside the delivery scope.
    from io import StringIO
    a = read_assignments(StringIO("root_id,p\n720575940596125869,1\n"))
    assert a.root_id.iloc[0] == "720575940596125869"


def test_hex_metric_and_invalid_maps():
    m = ColumnMap((Column("left", 1, 0, 0, -.5, 0),
                   Column("left", 2, 0, 1, -.5, 0),
                   Column("left", 3, 1, 0, -.5, 0)))
    az, el = m.angles(2)
    assert np.hypot(az[1]-az[0], el[1]-el[0]) == pytest.approx(2)
    assert np.hypot(az[2]-az[0], el[2]-el[0]) == pytest.approx(2)
    with pytest.raises(ValueError, match="Duplicate"):
        ColumnMap((m.columns[0], m.columns[0]))
    for step in (0, -1, np.nan, np.inf):
        with pytest.raises(ValueError):
            m.angles(step)
