"""FlyWire FAFB v783 builder; sum neuropil rows before min_syn filtering."""

import time
from ._build import build_graph, cli, data_root, frame


def build(data_dir, out, min_syn=1):
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
    return build_graph(root=root, out=out, dataset="FAFB", version="783", nodes=nodes,
                       edge_name=names[0], edge_columns=["pre_root_id", "post_root_id", "syn_count"],
                       source_names=names, min_syn=min_syn, started=started,
                       population="union of neurons, classification and consolidated_cell_types IDs; induced graph",
                       details={"label": "neurons.nt_type", "confidence": "neurons.nt_type_score"})


if __name__ == "__main__":
    cli(build, __doc__)
