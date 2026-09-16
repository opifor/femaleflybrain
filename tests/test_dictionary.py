"""Selection boundaries and measured graph smoke checks."""

import json
import os
from pathlib import Path

import numpy as np
import pytest

from flybench.dictionary import drive_targets, groups
from flybench.dictionary.build import audit, build, markdown_table
from flybench.dictionary.entries import DATASETS, P1_TYPES, Selector, entries
from flybench.graph.schema import load


@pytest.fixture
def graph():
    types = ["JO-A", "JO-A1", "JO-A-unclear", "JO-AB", "JO-B", "XJO-A", "JO-B4_b",
             "pC1_1a", "pC1_9a", "pC1_2a/2b", "pC1x_a", "P1-9", "DNp37",
             "ORN_VA1v", "ORN_DA1", "ORN_VA1d", "Or47b", "Gr32a", "",
             "SpsP", "IbSpsP", "ANXXX983", "LC10c-1", "LC10c-2", "LC10_unclear",
             "KCg-m", "KC_bad", "MBON01", "MBON15-like", "MBON25,MBON34",
             "PS1", "PS100", "ps1 MN", "i1 MN", "iii1", "TN1a_a", "TN1c_a"]
    n = len(types)
    return {"body_id": np.arange(1001, 1001 + n, dtype=np.int64),
            "type": np.array(types), "side": np.array(["L", "R", ""] + ["L"] * (n - 3)),
            "superclass": np.array(["cb_intrinsic"] * 30 + ["motor", "motor", "vnc_motor", "vnc_motor", "motor", "vnc_intrinsic", "vnc_intrinsic"]),
            "class": np.array([""] * 30 + ["wing_motor_neuron"] * 5 + [""] * 2),
            "nt": np.array(["acetylcholine"] * 18 + ["serotonin", "octopamine", "tyramine"] + [""] * (n - 21))}


def test_and_filters_and_missing_metadata(graph):
    np.testing.assert_array_equal(Selector(r"^JO-A[1]?$", side="R", superclass="cb_intrinsic").select(graph), [1])
    np.testing.assert_array_equal(Selector(r"^JO-A[1]?$", side="L", superclass="motor").select(graph), [])
    np.testing.assert_array_equal(Selector(nt="serotonin").select(graph), [18])
    np.testing.assert_array_equal(Selector(superclass="motor", cell_class="wing_motor_neuron").select(graph), [30, 31, 34])
    with pytest.raises(ValueError):
        Selector(side="left").select(graph)
    with pytest.raises(KeyError):
        Selector(nt="serotonin").select({k: v for k, v in graph.items() if k != "nt"})
    with pytest.raises(KeyError):
        Selector(superclass="motor").select({k: v for k, v in graph.items() if k != "superclass"})


@pytest.mark.parametrize("dataset", DATASETS)
def test_boundary_matches(graph, dataset):
    selected = groups(dataset, graph=graph)
    expected = {"JO-A": [0, 1], "JO-B": [4, 6], "Or47b": [13], "Or67d": [14],
                "Or*": [16], "Gr32a": [17], "serotonin": [18], "octopamine": [19],
                "LC10c": [22, 23], "KC": [25], "MBON": [27], "vpoDN": [12],
                "TN1A": [35]}
    for name, indices in expected.items():
        np.testing.assert_array_equal(selected[name], indices, err_msg=name)
        assert selected[name].dtype == np.dtype("int64")
    np.testing.assert_array_equal(selected["P1"], [7] if dataset == "male" else [])
    np.testing.assert_array_equal(selected["SAG"], {"male": [], "female": [19], "banc": [21]}[dataset])
    np.testing.assert_array_equal(selected["ps1_MN"], [32] if dataset == "male" else [30])
    np.testing.assert_array_equal(drive_targets(dataset, "JO-A", graph=graph), [0, 1])
    with pytest.raises(ValueError, match="absent"):
        drive_targets(dataset, "ppk25", graph=graph)
    with pytest.raises(KeyError, match="unknown"):
        drive_targets(dataset, "not-a-group", graph=graph)


def test_audit_distributions_and_absence(graph):
    records = {r["name"]: r for r in audit("male", graph)}
    record = records["JO-A"]
    assert record["count"] == 2
    assert record["example_body_ids"] == [1001, 1002]
    assert record["matched_types"] == {"JO-A": 1, "JO-A1": 1}
    assert record["side_distribution"] == {"L": 1, "R": 1}
    assert record["nt_distribution"] == {"acetylcholine": 2}
    assert records["ppk25"]["status"] == "absent"
    assert records["ppk25"]["example_body_ids"] == []
    assert records["ppk25"]["nt_distribution"] == {}
    assert len(records["ORN"]["example_body_ids"]) == 3
    assert "absent is not evidence" in records["ppk25"]["notes"]


def test_example_limit_and_missing_side_bucket(graph):
    graph["type"][:] = "JO-A"
    record = audit("male", graph)[0]
    assert record["example_body_ids"] == [1001, 1002, 1003, 1004, 1005]
    assert record["side_distribution"][""] == 1


def test_snapshot_export_and_api_paths(graph, tmp_path, monkeypatch):
    graph["meta"] = np.array(json.dumps({"dataset": "test", "schema_version": "1"}))
    np.savez(tmp_path / "graph_male.npz", **graph)
    monkeypatch.setenv("FLYBENCH_DATA", str(tmp_path))
    np.testing.assert_array_equal(groups("male")["JO-A"], [0, 1])
    np.testing.assert_array_equal(drive_targets("male", "JO-A", data_dir=tmp_path), [0, 1])
    report = build("male", out_dir=tmp_path)
    raw = (tmp_path / "dictionary_male.json").read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert json.loads(raw) == report
    assert len(report["graph"]["sha256"]) == 64
    assert report["graph"]["meta"]["dataset"] == "test"
    assert "0 (absent)" in markdown_table([report])
    assert "&#124;" in markdown_table([report])
    with pytest.raises(FileNotFoundError):
        groups("banc", data_dir=tmp_path)


def test_definition_contract():
    for dataset in DATASETS:
        definitions = entries(dataset)
        assert len({entry.name for entry in definitions}) == len(definitions)
        assert {entry.role for entry in definitions} == {"sensory_input", "readout", "motor", "state", "modulatory"}
        assert all(entry.confidence in ("exact", "family", "proxy") for entry in definitions)
        assert all(entry.literature and entry.source.startswith("https://") for entry in definitions)
    assert "pC1_2a/2b" not in P1_TYPES
    assert "pC1_9a" not in P1_TYPES
    with pytest.raises(ValueError):
        groups("unknown", graph={})


def test_simulator_accepts_groups(graph):
    from scipy.sparse import csr_matrix
    from flybench.sim import Simulator

    n = len(graph["body_id"])
    result = Simulator(csr_matrix((n, n)), groups=groups("male", graph=graph)).run(1, seed=1)
    assert result.group_rates_hz["JO-A"] == 0


@pytest.mark.parametrize("dataset", DATASETS)
def test_real_graph_smoke(dataset, record_property):
    path = Path(__file__).resolve().parents[1] / "build" / f"graph_{dataset}.npz"
    if not path.exists():
        pytest.skip(f"optional graph is unavailable: {path.name}")
    graph = load(path)
    selected = groups(dataset, graph=graph)
    if dataset == "female":
        assert len(selected["JO-A"]) > 0
        assert len(selected["JO-B"]) > 0
        # Report the observation; two cells is not an acceptance oracle.
        record_property("vpoDN_count", len(selected["vpoDN"]))
        print(f"FAFB vpoDN observed count: {len(selected['vpoDN'])}")
    if dataset == "male":
        assert len(selected["P1"]) > 0
    # Independently compare written counts with recomputed index populations.
    report_path = Path(__file__).parent / "fixtures" / "graph" / f"dictionary_{dataset}.json"
    assert report_path.exists(), "regenerate dictionary snapshots with fixtures/graph/generate.py"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert {r["name"]: r["count"] for r in report["entries"]} == {k: len(v) for k, v in selected.items()}
        for record in report["entries"]:
            indices = selected[record["name"]]
            assert record["example_body_ids"] == graph["body_id"][indices[:5]].tolist()


@pytest.mark.skipif(os.environ.get("FLYBENCH_DICTIONARY_FAIL_PROBE") != "1", reason="opt-in failure probe")
def test_harness_failure_probe():
    assert False, "deliberate dictionary harness failure"


# Explicit acceptance counts supplied by the E3 brief. Never replace these
# with observations when an acceptance mismatch occurs.
E3_BRIEF_COUNTS = {
    "female": {"AMMC-B1-candidate": 39, "AMMC-B1-candidate-graph": 23,
               "A2-candidate": 4, "vpoIN": 6, "aLN-m": 2},
    "banc": {"AMMC-B1-candidate": 38, "AMMC-B1-candidate-graph": 26,
             "A2-candidate": 2, "vpoIN": 4},
    "male": {"AMMC-B1-candidate": 12, "aLN-m": 2, "vpoIN": 5},
}
# The brief supplies no numeric expectation for these combinations. Freeze
# separately labelled graph observations; they do not invent brief claims.
E3_OBSERVED_COUNTS = {
    "female": {"vpoDN-GABA-input": 10},
    "banc": {"vpoDN-GABA-input": 8, "aLN-m": 2},
    "male": {"AMMC-B1-candidate-graph": 11, "A2-candidate": 0,
             "vpoDN-GABA-input": 0},
}


@pytest.fixture(scope="module", params=DATASETS)
def e3_snapshot(request):
    dataset = request.param
    path = Path(__file__).resolve().parents[1] / "build" / f"graph_{dataset}.npz"
    if not path.exists():
        pytest.skip(f"optional E3 graph unavailable: {path.name}")
    graph = load(path)
    return dataset, graph, groups(dataset, graph=graph)


@pytest.mark.parametrize("name", ["AMMC-B1-candidate", "AMMC-B1-candidate-graph",
                                  "A2-candidate", "vpoIN", "vpoDN-GABA-input", "aLN-m"])
def test_e3_snapshot_counts(e3_snapshot, name):
    dataset, _, selected = e3_snapshot
    expected = E3_BRIEF_COUNTS[dataset] | E3_OBSERVED_COUNTS[dataset]
    assert len(selected[name]) == expected[name], (dataset, name, "E3 count mismatch")


def test_e3_snapshot_boundaries(e3_snapshot):
    dataset, graph, selected = e3_snapshot
    assert np.intersect1d(selected["AMMC-B1-candidate"],
                          selected["AMMC-B1-candidate-graph"]).size == 0
    if dataset in ("female", "banc"):
        assert len(selected["vpoIN"]) > 0
        assert len(Selector(r"^vpoIN$").select(graph)) == 0
    if dataset == "banc":
        assert graph["side"][selected["A2-candidate"]].tolist() == ["R", "R"]
    assert set(graph["nt"][selected["aLN-m"]]) == {"gaba"}


@pytest.mark.parametrize("dataset", DATASETS)
def test_e3_a2_drive_rejected_for_present_and_absent_population(dataset):
    # A present cell prevents an ordinary absence error from masquerading as
    # the diagnostic guard. An absent population must use the same guard.
    for types in (["CB1817a", "CB1817b"], ["unrelated"]):
        graph = {"type": np.array(types), "body_id": np.arange(len(types))}
        with pytest.raises(ValueError, match="read-only diagnostic population"):
            drive_targets(dataset, "A2-candidate", graph=graph)


@pytest.mark.parametrize("dataset", DATASETS)
def test_e3_selector_definitions_and_exact_boundaries(dataset):
    definitions = {entry.name: entry for entry in entries(dataset)}
    patterns = {
        "AMMC-B1-candidate": r"^(?:CB1078|CB1542|SAD053)$",
        "AMMC-B1-candidate-graph": r"^(?:CB1076|CB1125|CB2789)$",
        "A2-candidate": r"^CB1817[ab]$",
        "vpoIN": r"^vpoIN$" if dataset == "male" else r"^CB1385$",
        "vpoDN-GABA-input": r"^AVLP008$",
        "aLN-m": r"^WED191$" if dataset == "male" else r"^CB3880$",
    }
    for name, pattern in patterns.items():
        entry = definitions[name]
        assert entry.selector.type_re == pattern
        assert entry.evidence_class in ("annotation crosswalk, external report, REPORTED",
                                         "graph connectivity, lane k2")
        assert entry.notes
        types = ["CB10780", "CB1076-like", "CB1817c", "CB1385a", "AVLP008-like",
                 "WED191a", "CB38800", "xSAD053", "AMMC-A2", "vpoIN-like"]
        assert entry.selector.select({"type": np.array(types),
                                      "body_id": np.arange(len(types))}).size == 0
    assert definitions["A2-candidate"].read_only
    assert not definitions["AMMC-B1-candidate"].read_only
    assert "0 cells in FAFB v783 and BANC v888; renamed 2026-09-16" in definitions["vpoIN"].notes
