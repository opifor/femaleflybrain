"""Measure all selectors against three graph snapshots and write JSON reports."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from flybench.graph.schema import load
from .api import graph_path
from .entries import DATASETS, entries


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def distribution(values):
    return dict(sorted(Counter(str(value) for value in values).items()))


def audit(dataset, graph):
    """Produce JSON-ready measurements, including explicit absent records."""
    records = []
    for definition in entries(dataset):
        indices = definition.selector.select(graph)
        record = definition.to_dict()
        record.update(count=int(len(indices)), status="present" if len(indices) else "absent",
                      example_body_ids=[int(v) for v in graph["body_id"][indices[:5]]],
                      side_distribution=distribution(graph["side"][indices]),
                      nt_distribution=distribution(graph["nt"][indices]),
                      matched_types=distribution(graph["type"][indices]))
        if not len(indices):
            record["notes"] = (record["notes"] + " No match in this graph snapshot; absent is not evidence of biological absence.").strip()
        records.append(record)
    return records


def build(dataset, data_dir=None, out_dir="build"):
    path = graph_path(dataset, data_dir)
    graph = load(path)
    report = {"dictionary_version": "1", "dataset": dataset,
              "graph": {"file": path.name, "sha256": sha256(path),
                        "neuron_count": len(graph["body_id"]), "meta": graph["meta"]},
              "entries": audit(dataset, graph)}
    destination = Path(out_dir) / f"dictionary_{dataset}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".json.partial")
    temporary.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return report


def markdown_table(reports):
    """Render the measured table used in docs/dictionary.md."""
    lines = ["| Group | Dataset | Selector (AND) | Count | Confidence | Source |",
             "| --- | --- | --- | ---: | --- | --- |"]
    for report in reports:
        for entry in report["entries"]:
            selector = json.dumps({key: value for key, value in entry["selector"].items()
                                   if value is not None}, ensure_ascii=True).replace("|", "&#124;")
            count = str(entry["count"]) if entry["count"] else "0 (absent)"
            lines.append(f"| {entry['name']} | {entry['dataset']} | `{selector}` | {count} | "
                         f"{entry['confidence']} | [{entry['literature']}]({entry['source']}) |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, help="Graph directory; default FLYBENCH_DATA or build")
    parser.add_argument("--out", type=Path, default=Path("build"))
    parser.add_argument("--dataset", choices=DATASETS, action="append")
    parser.add_argument("--table", type=Path, help="Optional measured Markdown table")
    args = parser.parse_args()
    reports = []
    for dataset in args.dataset or DATASETS:
        report = build(dataset, args.data, args.out)
        reports.append(report)
        present = sum(entry["status"] == "present" for entry in report["entries"])
        print(f"{dataset}: {present} present, {len(report['entries']) - present} absent")
    if args.table:
        args.table.parent.mkdir(parents=True, exist_ok=True)
        args.table.write_text(markdown_table(reports), encoding="utf-8")


if __name__ == "__main__":
    main()
