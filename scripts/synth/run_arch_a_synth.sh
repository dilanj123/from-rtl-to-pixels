#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export OSS_CAD_SUITE_ROOT="${OSS_CAD_SUITE_ROOT:-$HOME/.local/share/from-rtl-to-pixels/oss-cad-suite-current}"
export PATH="$OSS_CAD_SUITE_ROOT/bin:$PATH"
IMG_WIDTH="${IMG_WIDTH:-640}"; IMG_HEIGHT="${IMG_HEIGHT:-480}"
BUILD="$ROOT/build/impl/arch-a/${IMG_WIDTH}x${IMG_HEIGHT}"
mkdir -p "$BUILD"
cd "$ROOT"
"$ROOT/scripts/synth/check_ecp5_toolchain.sh" > "$BUILD/toolchain-check.log"
SOURCES="rtl/pixel_pkg.sv rtl/rgb_to_gray.sv rtl/elastic_stage.sv rtl/apb_regs.sv rtl/pixel_control.sv rtl/line_buffer.sv rtl/window_3x3.sv rtl/sobel_compact.sv rtl/magnitude_clamp.sv rtl/threshold_stage.sv rtl/output_control.sv rtl/rtl_to_pixels_top.sv"
yosys -l "$BUILD/yosys.log" -p "read_verilog -sv $SOURCES; chparam -set IMG_WIDTH $IMG_WIDTH -set IMG_HEIGHT $IMG_HEIGHT rtl_to_pixels_top; hierarchy -check -top rtl_to_pixels_top; synth_ecp5 -top rtl_to_pixels_top -json $BUILD/arch-a.json; check" 
# Re-read the mapped JSON for machine-readable post-synthesis statistics.
yosys -p "read_json $BUILD/arch-a.json; stat -json -top rtl_to_pixels_top" > "$BUILD/yosys-stat.raw"
python3 - "$BUILD/yosys-stat.raw" "$BUILD/yosys-stat.json" <<'PY'
import json,sys
text=open(sys.argv[1]).read()
start=text.find("{\n")
assert start >= 0, "stat JSON not found"
end=text.find("\n\nEnd of script", start)
assert end >= 0, "stat JSON terminator not found"
obj=json.loads(text[start:end])
json.dump(obj,open(sys.argv[2],"w"),indent=2)
PY
test -s "$BUILD/arch-a.json"; test -s "$BUILD/yosys-stat.json"
echo "ARCH_A_SYNTHESIS=PASS"
