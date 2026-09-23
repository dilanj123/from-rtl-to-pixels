#!/usr/bin/env python3
import argparse
import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SEED = 1
GRID_MHZ = 5


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--architecture", choices=["compact", "pipelined"], required=True)
    return parser.parse_args()


def route_result(architecture, frequency_mhz, cache, rows):
    if frequency_mhz in cache:
        return cache[frequency_mhz]

    script = ROOT / "scripts/timing/run_arch_route.sh"
    arch_dir = "arch-a" if architecture == "compact" else "arch-b"
    output_dir = (
        ROOT / "build/impl" / arch_dir / "640x480"
        / f"route/freq-{frequency_mhz}MHz-seed-{SEED}"
    )
    result = subprocess.run(
        [str(script), architecture, str(frequency_mhz), str(SEED)],
        capture_output=True,
        text=True,
    )
    status_path = output_dir / "status.txt"
    status = status_path.read_text() if status_path.exists() else ""
    route_passed = "ROUTE_STATUS=PASS" in status
    summary_path = output_dir / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    clocks = summary.get("clocks", [])
    clock = clocks[0] if clocks else {}
    timing_passed = route_passed and summary.get("timing_clean", False)
    rows.append(
        {
            "target_mhz": frequency_mhz,
            "seed": SEED,
            "route_status": "PASS" if route_passed else "FAIL",
            "reported_clock": clock.get("clock", ""),
            "achieved_mhz": clock.get("achieved_mhz"),
            "timing_status": "PASS" if timing_passed else "FAIL",
            "log_path": str(output_dir / "nextpnr.log"),
            "report_path": str(output_dir / "nextpnr-report.json"),
        }
    )
    if not route_passed:
        raise RuntimeError(
            f"route failure at {frequency_mhz} MHz\n"
            f"{result.stdout}\n{result.stderr}"
        )
    cache[frequency_mhz] = timing_passed
    return timing_passed


def refine_bracket(architecture, low, high, cache, rows):
    while high - low > GRID_MHZ:
        midpoint = (low + high) / 2
        frequency = int(midpoint // GRID_MHZ) * GRID_MHZ
        if frequency <= low:
            frequency = low + GRID_MHZ
        if frequency >= high:
            frequency = high - GRID_MHZ
        if route_result(architecture, frequency, cache, rows):
            low = frequency
        else:
            high = frequency
    return low, high


def find_bracket(architecture):
    rows = []
    cache = {}
    if route_result(architecture, 25, cache, rows):
        low = 25
        high = None
        for frequency in (50, 100, 200, 400):
            if route_result(architecture, frequency, cache, rows):
                low = frequency
            else:
                high = frequency
                break
    else:
        high = 25
        low = None
        for frequency in (10, 5):
            if route_result(architecture, frequency, cache, rows):
                low = frequency
                break
        if low is None:
            raise RuntimeError("5 MHz not timing-clean")

    if high is None:
        result = {
            "highest_clean": low,
            "lowest_fail": None,
            "bracket_width": None,
            "open_upper_bound": True,
        }
    else:
        low, high = refine_bracket(architecture, low, high, cache, rows)
        result = {
            "highest_clean": low,
            "lowest_fail": high,
            "bracket_width": high - low,
        }
    return rows, result


def main():
    args = parse_args()
    rows, bracket = find_bracket(args.architecture)
    arch_dir = "arch-a" if args.architecture == "compact" else "arch-b"
    output_path = ROOT / "build/impl" / arch_dir / "640x480/frequency-search.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({
        "architecture": args.architecture,
        "seed": SEED,
        "grid_mhz": GRID_MHZ,
        "tested": rows,
        **bracket,
    }, indent=2))


if __name__ == "__main__":
    main()
