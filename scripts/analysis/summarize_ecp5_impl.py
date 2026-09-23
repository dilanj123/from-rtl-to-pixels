#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def timing_domain(value):
    if value == "<async>":
        return "async"
    if isinstance(value, str) and value.startswith("posedge "):
        return "clock"
    return "other"


def summarize_path(path, kind):
    segments = path.get("path", [])
    annotations = []
    for segment in segments:
        annotations.extend(segment.get("sources", []))

    def delay_for(segment_types):
        return sum(
            float(segment.get("delay", 0))
            for segment in segments
            if segment.get("type") in segment_types
        )

    source = segments[0].get("from") if segments else None
    sink = segments[-1].get("to") if segments else None
    return {
        "kind": kind,
        "from": path.get("from"),
        "to": path.get("to"),
        "from_domain": timing_domain(path.get("from")),
        "to_domain": timing_domain(path.get("to")),
        "source": source,
        "sink": sink,
        "total_delay_ns": sum(float(segment.get("delay", 0)) for segment in segments),
        "clk_to_q_delay_ns": delay_for({"clk-to-q"}),
        "logic_delay_ns": delay_for({"logic"}),
        "routing_delay_ns": delay_for({"routing"}),
        "setup_delay_ns": delay_for({"setup"}),
        "source_annotations": list(dict.fromkeys(annotations)),
        "raw_path": path,
    }


def extract_cell_counts(stats):
    cells = {}

    def visit(value):
        if isinstance(value, dict):
            counts = value.get("num_cells_by_type")
            if isinstance(counts, dict):
                cells.update(counts)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(stats)
    return cells


def parse_args():
    parser = argparse.ArgumentParser()
    for name in (
        "dimensions", "device", "package", "speed", "seed", "yosys-stat",
        "report", "log", "output",
    ):
        parser.add_argument(f"--{name}", required=True)
    parser.add_argument("--target-mhz", required=True, type=float)
    parser.add_argument("--architecture", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    with open(args.yosys_stat) as handle:
        stats = json.load(handle)
    with open(args.report) as handle:
        report = json.load(handle)
    log = Path(args.log).read_text(errors="replace")

    clocks = [
        {
            "clock": name,
            "constraint_mhz": values.get("constraint"),
            "achieved_mhz": values.get("achieved"),
        }
        for name, values in report.get("fmax", {}).items()
        if isinstance(values, dict)
    ]
    critical_paths = report.get("critical_paths", [])
    clock_name = next(iter(report.get("fmax", {})), None)
    synchronous_paths = []
    async_to_clock_paths = []
    if clock_name:
        synchronous_paths = [
            path for path in critical_paths
            if path.get("from") == f"posedge {clock_name}"
            and path.get("to") == f"posedge {clock_name}"
        ]
        async_to_clock_paths = [
            path for path in critical_paths
            if path.get("from") == "<async>"
            and path.get("to") == f"posedge {clock_name}"
        ]

    def longest(paths):
        return max(
            paths,
            key=lambda path: sum(
                float(segment.get("delay", 0)) for segment in path.get("path", [])
            ),
        )

    synchronous_path = (
        summarize_path(longest(synchronous_paths), "clock_to_clock")
        if synchronous_paths else None
    )
    async_path = (
        summarize_path(longest(async_to_clock_paths), "async_to_clock")
        if async_to_clock_paths else None
    )
    output = {
        "architecture": args.architecture,
        "dimensions": args.dimensions,
        "device": args.device,
        "package": args.package,
        "speed_grade": args.speed,
        "seed": int(args.seed),
        "target_mhz": args.target_mhz,
        "yosys_mapped_cells": extract_cell_counts(stats),
        "nextpnr_utilization": report.get("utilization", report.get("utilisation", {})),
        "clocks": clocks,
        "timing_clean": bool(clocks) and all(
            clock.get("achieved_mhz") is not None
            and clock["achieved_mhz"] >= args.target_mhz
            for clock in clocks
        ),
        "critical_path_kind": "clock_to_clock" if synchronous_path else None,
        "critical_path": synchronous_path,
        "synchronous_critical_path": synchronous_path,
        "async_to_clock_critical_path": async_path,
        "clock_to_async_critical_path": None,
        "async_to_async_critical_path": None,
        "critical_path_log_lines": [
            line for line in log.splitlines()
            if "critical path" in line.lower() or "Max frequency for clock" in line
        ],
        "raw_report": report,
    }
    with open(args.output, "w") as handle:
        json.dump(output, handle, indent=2)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
