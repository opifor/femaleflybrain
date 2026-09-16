"""MaleCNS v1.0 builder (official annotated-body population)."""

import time
from ._build import build_graph, cli, data_root, frame


def build(data_dir, out, min_syn=1):
    started = time.perf_counter()
    root = data_root(data_dir)
    names = ["connectome-weights.feather", "body-annotations.feather", "body-neurotransmitters.feather"]
    nodes = frame(root / names[1], ["bodyId", "type", "somaSide", "superclass", "class"], "bodyId",
                  optional=["type", "somaSide", "superclass", "class"])
    nodes = nodes.rename(columns={"somaSide": "side"})
    nt = frame(root / names[2], ["body", "consensus_nt", "predicted_nt", "predicted_nt_confidence"], "body",
               optional=["predicted_nt", "predicted_nt_confidence"])
    nt["nt"] = nt["consensus_nt"]
    # Per-body prediction confidence is not confidence in a different consensus label.
    if {"predicted_nt", "predicted_nt_confidence"} <= set(nt.columns):
        nt["nt_conf"] = nt["predicted_nt_confidence"].where(nt["consensus_nt"] == nt["predicted_nt"])
    nodes = nodes.join(nt[[key for key in ("nt", "nt_conf") if key in nt]])
    return build_graph(root=root, out=out, dataset="MaleCNS", version="1.0", nodes=nodes,
                       edge_name=names[0], edge_columns=["body_pre", "body_post", "weight"],
                       source_names=names, min_syn=min_syn, started=started,
                       population="all body-annotations IDs; induced graph; no status/type filter",
                       details={"label": "consensus_nt", "confidence": "predicted_nt_confidence only when predicted_nt equals consensus_nt"})


if __name__ == "__main__":
    cli(build, __doc__)
