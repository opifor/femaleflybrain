"""FlyWire FAFB v783 builder; sum neuropil rows before min_syn filtering."""

import time
import numpy as np
import pandas as pd
from ._build import build_graph, cli, data_root, frame, edge_batches
from .signs import normalize


def build(data_dir, out, min_syn=1, *, source="shiu", shiu_data=None, sign_rule="shiu2024"):
    started = time.perf_counter()
    root = data_root(data_dir)
    names = ["connections_princeton.csv.gz", "neurons.csv.gz", "classification.csv.gz", "consolidated_cell_types.csv.gz"]
    nodes = frame(root / names[1], ["root_id", "nt_type", "nt_type_score"], "root_id", optional=["nt_type_score"])
    nodes = nodes.rename(columns={"nt_type": "nt", "nt_type_score": "nt_conf"})
    classes = frame(root / names[2], ["root_id", "side", "super_class", "class"], "root_id",
                    optional=["side", "super_class", "class"])
    types = frame(root / names[3], ["root_id", "primary_type"], "root_id")
    nodes = nodes.join(classes.rename(columns={"super_class": "superclass"}), how="outer")
    nodes = nodes.join(types.rename(columns={"primary_type": "type"}), how="outer")
    extra = {"connectivity_source": source}
    edge_name, edge_columns = names[0], ["pre_root_id", "post_root_id", "syn_count"]
    if source == "shiu":
        if sign_rule != "shiu2024":
            raise ValueError("Shiu source requires parquet signs; use codex for a selectable NT rule")
        shiu_root = (data_root(shiu_data) if shiu_data is not None else root).resolve()
        edge_name = shiu_root / "Connectivity_783.parquet"
        completeness = shiu_root / "Completeness_783.csv"
        universe = frame(completeness, ["Unnamed: 0"], "Unnamed: 0").index
        parts = []
        for batch in edge_batches(edge_name, ["Presynaptic_ID", "Excitatory"]):
            parts.append(batch.to_pandas().drop_duplicates())
        sign_pairs = pd.concat(parts, ignore_index=True).drop_duplicates()
        if sign_pairs.isna().any().any() or not sign_pairs.Excitatory.isin([-1, 1]).all():
            raise ValueError("Invalid parquet Excitatory sign")
        inconsistent = int(sign_pairs.Presynaptic_ID.value_counts().gt(1).sum())
        if inconsistent:
            raise ValueError(f"Inconsistent parquet signs for {inconsistent} neurons")
        known = sign_pairs.set_index("Presynaptic_ID").Excitatory
        extra["unmatched_codex_neurons"] = int((~universe.isin(frame(root / names[1], ["root_id"], "root_id").index)).sum())
        nodes = nodes.reindex(universe)
        nodes["sign"] = known.reindex(universe).fillna(0).astype(np.int8)
        audit = pd.DataFrame({"nt": nodes.nt.fillna("").map(normalize), "sign": known.reindex(universe)})
        extra["parquet_nt_sign_distribution"] = {
            nt: {str(int(s)): int(v) for s, v in group.sign.value_counts().items()}
            for nt, group in audit.groupby("nt")}
        extra["inconsistent_sign_neurons"] = inconsistent
        extra["neurons_without_outgoing_sign"] = int(known.reindex(universe).isna().sum())
        names = names[1:] + [edge_name, completeness]
        edge_columns = ["Presynaptic_ID", "Postsynaptic_ID", "Connectivity"]
        sign_rule = "shiu2024-parquet"
    elif source != "codex":
        raise ValueError("source must be shiu or codex")
    return build_graph(root=root, out=out, dataset="FAFB", version="783", nodes=nodes,
                       edge_name=edge_name, edge_columns=edge_columns,
                       source_names=names, min_syn=min_syn, started=started,
                       population=("Completeness_783 IDs; induced graph" if source == "shiu" else
                                   "union of Codex annotation IDs; upstream threshold >=5 in official export"),
                       sign_rule=sign_rule, extra_meta=extra,
                       details={"label": "neurons.nt_type", "confidence": "neurons.nt_type_score"})


if __name__ == "__main__":
    cli(build, __doc__)
