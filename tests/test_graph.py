"""Synthetic-only acceptance tests. No real connectome paths or downloads."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd
import pyarrow.feather as feather
import pyarrow.parquet as parquet
import pytest

from flybench.graph import banc, female, male, load, where
from flybench.graph._build import edge_batches
from flybench.graph.schema import validate
from flybench.graph.signs import signs

FIXTURE = Path(__file__).parent / "fixtures" / "graph"
BUILDERS = [male, female, banc]


@pytest.mark.parametrize("module", BUILDERS, ids=["male", "female", "banc"])
@pytest.mark.parametrize("threshold,edges,total", [(1, 7, 18), (2, 5, 16), (3, 3, 12), (100, 0, 0)])
def test_build(module, threshold, edges, total, tmp_path):
    name = module.__name__.rsplit(".", 1)[1]
    root = FIXTURE / name
    path = tmp_path / "graph.npz"
    meta = module.build(root, path, min_syn=threshold)
    graph = load(path)
    assert graph["meta"] == meta
    assert validate(graph)
    assert meta["neuron_count"] == 6
    assert meta["edge_count"] == edges
    assert meta["synapse_count"] == total
    assert meta["input_rows"] == 9
    assert meta["input_synapses"] == 25
    assert meta["outside_population_rows"] == 1
    assert meta["outside_population_synapses"] == 7
    assert meta["aggregated_duplicate_rows"] == 1
    assert meta["below_min_syn_synapses"] == 18 - total
    assert meta["min_syn"] == threshold
    assert meta["sign_rule"] == ("shiu2024-parquet" if module is female else "shiu2024")
    assert meta["schema_version"] == "1"
    assert meta["dataset"] == {male: "MaleCNS", female: "FAFB", banc: "BANC"}[module]
    assert meta["version"] == {male: "1.0", female: "783", banc: "888"}[module]
    assert meta["created_utc"].endswith("+00:00")
    assert meta["elapsed_seconds"] > 0 and meta["peak_rss_bytes"] > 0
    assert meta["type_labeled_fraction"] == 5 / 6
    assert meta["nt_distribution"] == dict.fromkeys(
        ["acetylcholine", "gaba", "glutamate", "dopamine", "serotonin", "octopamine"], 1)
    for source in meta["sources"]:
        assert source["sha256"] == hashlib.sha256((root / source["name"]).read_bytes()).hexdigest()
    np.testing.assert_array_equal(graph["sign"], [1, -1, -1, 1, 1, 0] if module is female else [1, -1, -1, 1, 1, 1])
    np.testing.assert_array_equal(graph["side"], ["L", "R", "M", "", "L", "R"])
    np.testing.assert_array_equal(graph["type"], ["A_L", "A_R", "B", "", "C", "D"])
    np.testing.assert_array_equal(graph["body_id"], np.array([10, 20, 30, 40, 50, 60], np.int64)
                                  + (0 if module is male else 720575940000000000))
    assert graph["nt_conf"].dtype == np.float32
    assert all(graph[key].dtype.kind == "U" for key in ["type", "nt", "side", "superclass", "class"])
    if module is male:
        assert np.isnan(graph["nt_conf"][-1])
    # Oracle is a hand-specified sparse matrix, including self loop and zero-sign edges.
    expected = {(0, 1): 3, (0, 2): 1, (1, 0): 2, (2, 2): 2,
                (2, 3): 4, (3, 4): 5, (4, 0): 1}
    expected = {key: value for key, value in expected.items() if value >= threshold}
    actual, signed = {}, {}
    for row in range(6):
        for j in range(graph["indptr"][row], graph["indptr"][row+1]):
            actual[(row, int(graph["indices"][j]))] = int(graph["count"][j])
            signed[(row, int(graph["indices"][j]))] = int(graph["data"][j])
    assert actual == expected
    assert signed == {key: value * ([1, -1, -1, 1, 1, 0] if module is female else [1, -1, -1, 1, 1, 1])[key[0]] for key, value in expected.items()}
    assert graph["indptr"][-2] == graph["indptr"][-1]  # isolated sixth neuron survives
    if threshold == 1:
        np.testing.assert_array_equal(graph["indptr"], [0, 2, 3, 5, 6, 7, 7])
        np.testing.assert_array_equal(graph["indices"], [1, 2, 0, 2, 3, 4, 0])


def test_selector(tmp_path):
    male.build(FIXTURE / "male", tmp_path / "g.npz")
    g = load(tmp_path / "g.npz")
    np.testing.assert_array_equal(where(g, type_re="^A_"), [0, 1])
    np.testing.assert_array_equal(where(g, type_re="A", side="L", superclass="sensory"), [0])
    np.testing.assert_array_equal(where(g, side="M"), [2])
    np.testing.assert_array_equal(where(g, type_re="^$"), [3])
    assert len(where(g, type_re="no-match")) == 0
    with pytest.raises(ValueError):
        where(g, side="left")


def test_sign_policy():
    np.testing.assert_array_equal(signs(["ACH", "GABA", "GLUT", "DA", "SER", "OCT", "other", "", "unknown"]),
                                  [1, -1, -1, 1, 1, 1, 0, 0, 0])
    with pytest.raises(ValueError):
        signs(["ACH"], rule="v2")


@pytest.mark.parametrize("bad", [0, -1, 1.5, True])
def test_bad_threshold(bad, tmp_path):
    with pytest.raises(ValueError, match="min_syn"):
        male.build(FIXTURE / "male", tmp_path / "g.npz", bad)


def test_parquet_comparison(tmp_path):
    female.build(FIXTURE / "female", tmp_path / "g.npz")
    g = load(tmp_path / "g.npz")
    columns = ["Presynaptic_ID", "Postsynaptic_ID", "Connectivity"]
    batches = list(edge_batches(FIXTURE / "Connectivity_783.parquet", columns))
    expected = parquet.read_table(FIXTURE / "Connectivity_783.parquet").to_pandas()
    assert sum(len(b) for b in batches) == 7
    for row in expected.itertuples(index=False):
        src, dst = np.searchsorted(g["body_id"], [row.Presynaptic_ID, row.Postsynaptic_ID])
        a, b = g["indptr"][src:src+2]
        found = np.flatnonzero(g["indices"][a:b] == dst)
        assert found.size == 1
        assert g["count"][a + found[0]] == row.Connectivity


def test_cli_env(tmp_path):
    env = dict(os.environ, FLYBENCH_DATA=str(FIXTURE / "female"))
    out = tmp_path / "cli.npz"
    result = subprocess.run([sys.executable, "-m", "flybench.graph.female", "--out", str(out), "--min-syn", "3"],
                            env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["synapse_count"] == 12
    assert load(out)["meta"]["edge_count"] == 3


def test_duplicate_count_overflow(tmp_path):
    root = tmp_path / "male"
    shutil.copytree(FIXTURE / "male", root)
    pd.DataFrame(dict(body_pre=[10, 10], body_post=[20, 20], weight=[2147483647, 1])).to_feather(root / "connectome-weights.feather")
    with pytest.raises(ValueError, match="overflows"):
        male.build(root, tmp_path / "g.npz")
    assert not (tmp_path / "g.npz").exists()


def test_validation_detects_broken_sign(tmp_path):
    male.build(FIXTURE / "male", tmp_path / "g.npz")
    g = load(tmp_path / "g.npz")
    g["data"][2] = 2  # inhibitory edge corrupted to excitatory
    with pytest.raises(ValueError, match="sign"):
        validate(g)


@pytest.mark.parametrize("module", BUILDERS, ids=["male", "female", "banc"])
def test_optional_annotations(module, tmp_path):
    name = module.__name__.rsplit(".", 1)[1]
    root = tmp_path / name
    shutil.copytree(FIXTURE / name, root)
    if module is male:
        path = root / "body-annotations.feather"
        feather.write_feather(feather.read_table(path).drop(["superclass", "class"]), path)
        path = root / "body-neurotransmitters.feather"
        feather.write_feather(feather.read_table(path).drop(["predicted_nt_confidence"]), path)
    elif module is banc:
        path = root / "banc_888_meta.feather"
        feather.write_feather(feather.read_table(path).drop(["super_class", "cell_class", "neurotransmitter_score"]), path)
    else:
        path = root / "classification.csv.gz"
        pd.read_csv(path).drop(columns=["super_class", "class"]).to_csv(path, index=False)
        path = root / "neurons.csv.gz"
        pd.read_csv(path).drop(columns=["nt_type_score"]).to_csv(path, index=False)
    out = tmp_path / "g.npz"
    module.build(root, out)
    g = load(out)
    assert "nt_conf" not in g
    np.testing.assert_array_equal(g["superclass"], [""] * 6)
    np.testing.assert_array_equal(g["class"], [""] * 6)
    assert g["meta"]["synapse_count"] == 18


def test_harness_failure_probe():
    assert os.environ.get("FLYBENCH_GRAPH_FAIL_PROBE") != "1", "deliberate graph harness failure"


def test_both_sign_rules():
    labels = ["ACH", "GABA", "GLUT", "DA", "SER", "OCT", "histamine", "tyramine", "unclear"]
    np.testing.assert_array_equal(signs(labels, "shiu2024"), [1, -1, -1, 1, 1, 1, 0, 0, 0])
    np.testing.assert_array_equal(signs(labels, "monoamine-zero"), [1, -1, -1, 0, 0, 0, 0, 0, 0])


def test_male_status(tmp_path):
    root = tmp_path / "male"
    shutil.copytree(FIXTURE / "male", root)
    path = root / "body-annotations.feather"
    nodes = pd.read_feather(path)
    nodes.loc[1, "status"] = "Orphan"
    nodes.to_feather(path)
    meta = male.build(root, tmp_path / "g.npz")
    assert meta["neuron_count"] == 5
    assert meta["synapse_count"] == 13
    assert meta["outside_population_synapses"] == 12
    assert male.build(root, tmp_path / "all.npz", status=["Traced", "Orphan"])["synapse_count"] == 18


@pytest.mark.parametrize("field,value", [("status", "NOT_A_NEURON"), ("status", "X,GLIA"),
    ("status", "TOO_SMALL"), ("status", "UNROOTED"), ("super_class", "glia"), ("proofread", "FALSE")])
def test_banc_filter(field, value, tmp_path):
    root = tmp_path / "banc"
    shutil.copytree(FIXTURE / "banc", root)
    path = root / "banc_888_meta.feather"
    nodes = pd.read_feather(path)
    nodes.loc[1, field] = value
    nodes.to_feather(path)
    meta = banc.build(root, tmp_path / "g.npz")
    assert meta["neuron_count"] == 5  # roughly-proofread isolated node remains
    assert meta["synapse_count"] == 13
    assert meta["outside_population_synapses"] == 12


def test_shiu_sign_conflict_and_missing_labels(tmp_path):
    root = tmp_path / "female"
    shutil.copytree(FIXTURE / "female", root)
    path = root / "neurons.csv.gz"
    pd.read_csv(path).iloc[1:].to_csv(path, index=False)
    meta = female.build(root, tmp_path / "g.npz")
    assert meta["unmatched_codex_neurons"] == 1
    assert meta["inconsistent_sign_neurons"] == 0
    assert load(tmp_path / "g.npz")["sign"][0] == 1
    path = root / "Connectivity_783.parquet"
    edges = pd.read_parquet(path)
    edges.loc[1, "Excitatory"] = -1
    edges.to_parquet(path)
    with pytest.raises(ValueError, match="Inconsistent.*1 neurons"):
        female.build(root, tmp_path / "bad.npz")
    assert not (tmp_path / "bad.npz").exists()


def test_codex_source_and_zero_rule(tmp_path):
    meta = female.build(FIXTURE / "female", tmp_path / "g.npz", source="codex", sign_rule="monoamine-zero")
    assert meta["sign_rule"] == "monoamine-zero"
    np.testing.assert_array_equal(load(tmp_path / "g.npz")["sign"], [1, -1, -1, 0, 0, 0])


def test_cli_multiple_statuses(tmp_path):
    out = tmp_path / "g.npz"
    result = subprocess.run([sys.executable, "-m", "flybench.graph.male", "--data", str(FIXTURE / "male"),
        "--out", str(out), "--status", "Traced", "Orphan", "--status", "Assign"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert load(out)["meta"]["selected_status"] == ["Traced", "Orphan", "Assign"]
    assert load(out)["meta"]["synapse_count"] == 18


def test_shiu_rule_override_rejected(tmp_path):
    with pytest.raises(ValueError, match="requires parquet signs"):
        female.build(FIXTURE / "female", tmp_path / "g.npz", sign_rule="monoamine-zero")
    assert not (tmp_path / "g.npz").exists()
