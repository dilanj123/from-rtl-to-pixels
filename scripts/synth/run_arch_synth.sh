#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARCH="${1:?architecture compact|pipelined}"
case "$ARCH" in
  compact)
    TOP=rtl_to_pixels_top
    TOPSRC=rtl/rtl_to_pixels_top.sv
    BUILD="$ROOT/build/impl/arch-a/640x480"
    ;;
  pipelined)
    TOP=rtl_to_pixels_top_pipelined
    TOPSRC=rtl/rtl_to_pixels_top_pipelined.sv
    BUILD="$ROOT/build/impl/arch-b/640x480"
    ;;
  *)
    echo "unknown architecture: $ARCH" >&2
    exit 2
    ;;
esac
export OSS_CAD_SUITE_ROOT="${OSS_CAD_SUITE_ROOT:-$HOME/.local/share/from-rtl-to-pixels/oss-cad-suite-current}"
export PATH="$OSS_CAD_SUITE_ROOT/bin:$PATH"
mkdir -p "$BUILD"
cd "$ROOT"

SOURCES=(
  rtl/pixel_pkg.sv
  rtl/rgb_to_gray.sv
  rtl/elastic_stage.sv
  rtl/apb_regs.sv
  rtl/pixel_control.sv
  rtl/line_buffer.sv
  rtl/window_3x3.sv
  rtl/sobel_compact.sv
  rtl/magnitude_clamp.sv
  rtl/threshold_stage.sv
  rtl/output_control.sv
  "$TOPSRC"
)

yosys -l "$BUILD/yosys.log" -p "read_verilog -sv ${SOURCES[*]}; chparam -set IMG_WIDTH 640 -set IMG_HEIGHT 480 $TOP; hierarchy -check -top $TOP; synth_ecp5 -top $TOP -json $BUILD/netlist.json; check"
yosys -p "read_json $BUILD/netlist.json; stat -json -top $TOP" > "$BUILD/stat.raw"
python3 - "$BUILD/stat.raw" "$BUILD/yosys-stat.json" <<'PY'
import json
import sys

with open(sys.argv[1]) as handle:
    text = handle.read()
start = text.find("{\n")
end = text.find("\n\nEnd of script", start)
assert start >= 0 and end >= 0
with open(sys.argv[2], "w") as handle:
    json.dump(json.loads(text[start:end]), handle, indent=2)
PY
test -s "$BUILD/netlist.json"
test -s "$BUILD/yosys-stat.json"
echo "ARCH_SYNTHESIS=PASS architecture=$ARCH"
