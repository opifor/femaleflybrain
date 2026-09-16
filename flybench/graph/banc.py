"""BANC v888 builder, keyed by banc_888_id (not later root_id mappings)."""

import time
from ._build import build_graph, cli, data_root, frame


def build(data_dir, out, min_syn=1, *, sign_rule="shiu2024"):
    started = time.perf_counter()
    root = data_root(data_dir)
    names = ["banc_888_edgelist_simple_v3.feather", "banc_888_meta.feather"]
    nodes = frame(root / names[1], ["banc_888_id", "proofread", "roughly_proofread", "status", "cell_type", "side", "super_class", "cell_class",
                                  "neurotransmitter_predicted", "neurotransmitter_score"], "banc_888_id",
                  optional=["cell_type", "side", "super_class", "cell_class", "neurotransmitter_score"])
    proof = nodes.proofread.astype(str).str.upper().eq("TRUE")
    rough = nodes.roughly_proofread.astype(str).str.upper().eq("TRUE")
    excluded = nodes.status.fillna("").str.upper().str.contains("NOT_A_NEURON|GLIA|TOO_SMALL|UNROOTED")
    if "super_class" in nodes:
        excluded |= nodes.super_class.fillna("").str.lower().eq("glia")
    audit = dict(proofread_count=int(proof.sum()), roughly_proofread_count=int(rough.sum()),
                 proofread_union_count=int((proof | rough).sum()), excluded_from_union=int(((proof | rough) & excluded).sum()))
    nodes = nodes[(proof | rough) & ~excluded]
    nodes = nodes.rename(columns={"cell_type": "type", "super_class": "superclass", "cell_class": "class",
                                  "neurotransmitter_predicted": "nt", "neurotransmitter_score": "nt_conf"})
    return build_graph(root=root, out=out, dataset="BANC", version="888", nodes=nodes,
                       edge_name=names[0], edge_columns=["pre", "post", "count"],
                       source_names=names, min_syn=min_syn, started=started,
                       population="proofread OR roughly_proofread; excludes forbidden statuses and glia; induced graph",
                       sign_rule=sign_rule, extra_meta={"population_filter": audit},
                       details={"label": "neurotransmitter_predicted", "confidence": "neurotransmitter_score",
                                "verified": "not used: verified labels can be multi-transmitter"})


if __name__ == "__main__":
    cli(build, __doc__)
