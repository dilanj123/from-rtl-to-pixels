#!/usr/bin/env python3
import argparse
import csv
import json


def load_json(path):
    with open(path) as handle:
        return json.load(handle)


def extract_cell_counts(stats):
    counts = {}

    def visit(value):
        if isinstance(value, dict):
            cell_counts = value.get("num_cells_by_type")
            if isinstance(cell_counts, dict):
                counts.update(cell_counts)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(stats)
    return counts


def load_frequency_search(path):
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle))


def summarize_frequency_search(rows):
    clean = [row for row in rows if row["timing_status"] == "PASS"]
    failing = [row for row in rows if row["timing_status"] == "FAIL"]
    highest_clean = max(int(row["target_mhz"]) for row in clean)
    lowest_fail = min(int(row["target_mhz"]) for row in failing)
    return {
        "tested": rows,
        "highest_clean": highest_clean,
        "lowest_fail": lowest_fail,
        "bracket_width": lowest_fail - highest_clean,
    }


def build_comparison(args):
    arch_a_cells = extract_cell_counts(load_json(args.a_stat))
    arch_b_cells = extract_cell_counts(load_json(args.b_stat))
    resources = {
        cell_type: {
            "A": arch_a_cells.get(cell_type, 0),
            "B": arch_b_cells.get(cell_type, 0),
            "delta": arch_b_cells.get(cell_type, 0) - arch_a_cells.get(cell_type, 0),
        }
        for cell_type in sorted(set(arch_a_cells) | set(arch_b_cells))
    }

    arch_a_search = summarize_frequency_search(load_frequency_search(args.a_search))
    arch_b_search = summarize_frequency_search(load_frequency_search(args.b_search))
    arch_a_summary = load_json(args.a_summary)
    arch_b_summary = load_json(args.b_summary)
    arch_a_performance = load_json(args.a_perf)
    arch_b_performance = load_json(args.b_perf)

    return {
        "target": {
            "dimensions": "640x480",
            "device": "LFE5U-45F",
            "package": "CABGA381",
            "speed": 6,
            "seed": 1,
        },
        "resources": resources,
        "timing": {
            "A": arch_a_search,
            "B": arch_b_search,
            "A_clean_summary": arch_a_summary,
            "B_clean_summary": arch_b_summary,
            "A_path": arch_a_summary.get("synchronous_critical_path"),
            "B_path": arch_b_summary.get("synchronous_critical_path"),
        },
        "performance": {
            "A": arch_a_performance,
            "B": arch_b_performance,
            "latency_delta": (
                arch_b_performance["first_output_latency_cycles"]
                - arch_a_performance["first_output_latency_cycles"]
            ),
            "frame_cycles_delta": (
                arch_b_performance["frame_completion_cycles"]
                - arch_a_performance["frame_completion_cycles"]
            ),
        },
        "derived": {
            "A_peak_mpixel_s": arch_a_search["highest_clean"] / arch_a_performance["input_ii_max"],
            "B_peak_mpixel_s": arch_b_search["highest_clean"] / arch_b_performance["input_ii_max"],
            "A_frame_s": arch_a_search["highest_clean"] * 1e6 / arch_a_performance["frame_completion_cycles"],
            "B_frame_s": arch_b_search["highest_clean"] * 1e6 / arch_b_performance["frame_completion_cycles"],
            "A_effective_mpixel_s": arch_a_search["highest_clean"] * arch_a_performance["accepted_output_count"] / arch_a_performance["frame_completion_cycles"],
            "B_effective_mpixel_s": arch_b_search["highest_clean"] * arch_b_performance["accepted_output_count"] / arch_b_performance["frame_completion_cycles"],
        },
    }


def parse_args():
    parser = argparse.ArgumentParser()
    for name in (
        "a-stat", "b-stat", "a-summary", "b-summary", "a-search",
        "b-search", "a-perf", "b-perf", "output",
    ):
        parser.add_argument(f"--{name}", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    comparison = build_comparison(args)
    with open(args.output, "w") as handle:
        json.dump(comparison, handle, indent=2)
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
