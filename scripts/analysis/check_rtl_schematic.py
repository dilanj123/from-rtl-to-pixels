"""Validate the reviewed RTL schematic inventory and its required assets."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "docs/assets"
REQUIRED_MODULES = {
    "pixel_control", "rgb_to_gray", "line_buffer", "window_3x3",
    "sobel_compact", "magnitude_clamp", "threshold_stage",
    "output_control", "elastic_stage", "apb_regs",
    "rtl_to_pixels_top", "rtl_to_pixels_top_pipelined", "pixel_pkg",
}
REQUIRED_PAGES = {
    "System Context", "Architecture A", "Architecture B",
    "Module Interfaces", "Ready-Valid and Frame Control",
}


def main():
    inventory_path = ASSETS / "rtl-interface-inventory.json"
    drawio_path = ASSETS / "rtl-architecture.drawio"
    inventory = json.loads(inventory_path.read_text())
    assert REQUIRED_MODULES <= set(inventory["modules"])
    assert set(inventory["connections"]) == {
        "rtl_to_pixels_top", "rtl_to_pixels_top_pipelined"
    }
    widths = inventory["canonical_configuration"]["widths"]
    assert widths["Architecture-B token"] == 28
    assert widths["final output token"] == 11
    assert inventory["token_mappings"]["architecture_b"] == {
        "27": "final_tag", "26": "user/SOF", "25": "last/EOL",
        "24": "border", "23:12": "gx signed[11:0]", "11:0": "gy signed[11:0]",
    }
    assert inventory["token_mappings"]["output"] == {
        "10": "final_tag", "9": "user/SOF", "8": "last/EOL", "7:0": "edge data",
    }
    root = ET.parse(drawio_path).getroot()
    assert root.tag == "mxfile"
    pages = {diagram.get("name") for diagram in root.findall("diagram")}
    assert REQUIRED_PAGES <= pages
    for name in [
        "rtl-system-context.svg", "rtl-architecture-a.svg",
        "rtl-architecture-b.svg", "rtl-module-interfaces.svg",
        "rtl-control-flow.svg",
    ]:
        svg = ET.parse(ASSETS / name).getroot()
        assert svg.tag.endswith("svg") and svg.get("viewBox")
    print("RTL_SCHEMATIC=PASS")


if __name__ == "__main__":
    main()
