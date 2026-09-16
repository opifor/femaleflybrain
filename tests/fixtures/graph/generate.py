"""Recreate synthetic fixtures or explicitly requested real-graph dictionary snapshots."""

from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as parquet

ROOT = Path(__file__).parent


def write_feather(path, values):
    feather.write_feather(pa.Table.from_pydict(values), path)


def generate():
    ids = [10, 20, 30, 40, 50, 60]
    offset = 720575940000000000
    large_ids = [offset + i for i in ids]
    pre = [10, 10, 10, 20, 30, 40, 50, 30, 999]
    post = [20, 20, 30, 10, 40, 50, 10, 30, 10]
    count = [1, 2, 1, 2, 4, 5, 1, 2, 7]
    types = ["A_L", "A_R", "B", None, "C", "D"]
    sides = ["left", "right", "midline", None, "L", "R"]
    classes = ["sensory", "motor", "sensory", None, "motor", None]
    nts = ["acetylcholine", "gaba", "glutamate", "dopamine", "serotonin", "octopamine"]
    confidence = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
    for name in ("male", "female", "banc"):
        (ROOT / name).mkdir(exist_ok=True)
    write_feather(ROOT / "male/connectome-weights.feather", dict(body_pre=pre, body_post=post, weight=count))
    write_feather(ROOT / "male/body-annotations.feather", dict(bodyId=ids, status=["Traced"]*6, type=types, somaSide=sides,
                                                              superclass=classes, **{"class": classes}))
    write_feather(ROOT / "male/body-neurotransmitters.feather", dict(body=ids, consensus_nt=nts,
                   predicted_nt=nts[:-1]+["acetylcholine"], predicted_nt_confidence=confidence))
    write_feather(ROOT / "banc/banc_888_edgelist_simple_v3.feather",
                  dict(pre=[str(offset+i) for i in pre], post=[str(offset+i) for i in post], count=count))
    write_feather(ROOT / "banc/banc_888_meta.feather", dict(banc_888_id=list(map(str, large_ids)),
                  root_id=[str(i+1000) for i in large_ids], proofread=["TRUE"]*5+["FALSE"],
                  roughly_proofread=["FALSE"]*5+["TRUE"], status=[""]*6, cell_type=types, side=sides, super_class=classes,
                  cell_class=classes, neurotransmitter_predicted=nts, neurotransmitter_score=confidence))
    frames = {
        "connections_princeton": dict(pre_root_id=[offset+i for i in pre], post_root_id=[offset+i for i in post],
                                      syn_count=count, neuropil=["A", "B"]+["A"]*7, nt_type=["ACH"]*9),
        "neurons": dict(root_id=large_ids, nt_type=["ACH", "GABA", "GLUT", "DA", "SER", "OCT"], nt_type_score=confidence),
        "classification": dict(root_id=large_ids, side=sides, super_class=classes, **{"class": classes}),
        "consolidated_cell_types": dict(root_id=large_ids, primary_type=types),
    }
    for name, values in frames.items():
        pd.DataFrame(values).to_csv(ROOT / f"female/{name}.csv.gz", index=False,
                                   compression={"method": "gzip", "mtime": 0})
    # Independent expected pairs, using Shiu comparison-data column names.
    parquet.write_table(pa.Table.from_pydict(dict(
        Presynaptic_ID=[large_ids[i] for i in [0, 0, 1, 2, 2, 3, 4]],
        Postsynaptic_ID=[large_ids[i] for i in [1, 2, 0, 2, 3, 4, 0]],
        Connectivity=[3, 1, 2, 2, 4, 5, 1])), ROOT / "Connectivity_783.parquet")
    parquet.write_table(pa.Table.from_pydict(dict(
        Presynaptic_ID=[offset+i for i in pre], Postsynaptic_ID=[offset+i for i in post],
        Connectivity=count, Excitatory=[1, 1, 1, -1, -1, 1, 1, -1, 1])),
        ROOT / "female/Connectivity_783.parquet")
    pd.DataFrame({"Unnamed: 0": large_ids, "Completed": [True]*6}).to_csv(
        ROOT / "female/Completeness_783.csv", index=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dictionary-snapshots", action="store_true")
    args = parser.parse_args()
    if args.dictionary_snapshots:
        from flybench.dictionary.build import build

        for dataset in ("female", "banc", "male"):
            build(dataset, data_dir="build", out_dir=ROOT)
    else:
        generate()
