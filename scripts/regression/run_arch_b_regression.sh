#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG="$ROOT/results/raw/arch-b-functional-regression.log"
mkdir -p "$ROOT/results/raw" "$ROOT/results/processed/arch-b"
: > "$LOG"
exec_cmd() {
    echo >> "$LOG"
    echo "=== $* ===" | tee -a "$LOG"
    "$@" 2>&1 | tee -a "$LOG"
}
run_sim() {
    local makefile="$1" width="$2" height="$3" label="$4"
    shift 4
    local sim_build
    sim_build="$(mktemp -d)"
    echo >> "$LOG"
    echo "=== $label ${width}x${height} ===" | tee -a "$LOG"
    set +e
    env PATH="$ROOT/.venv/bin:$PATH" IMG_WIDTH="$width" IMG_HEIGHT="$height" SIM_BUILD="$sim_build" COCOTB_RESULTS_FILE="$sim_build/results.xml" "$@" make -f "$ROOT/tb/tests/$makefile" 2>&1 | tee -a "$LOG"
    local rc=${PIPESTATUS[0]}
    set -e
    rm -rf "$sim_build"
    test "$rc" -eq 0
}
SOURCE_LIST=(
    "$ROOT/rtl/pixel_pkg.sv" "$ROOT/rtl/rgb_to_gray.sv" "$ROOT/rtl/elastic_stage.sv"
    "$ROOT/rtl/apb_regs.sv" "$ROOT/rtl/pixel_control.sv" "$ROOT/rtl/line_buffer.sv"
    "$ROOT/rtl/window_3x3.sv" "$ROOT/rtl/sobel_compact.sv" "$ROOT/rtl/magnitude_clamp.sv"
    "$ROOT/rtl/threshold_stage.sv" "$ROOT/rtl/output_control.sv"
    "$ROOT/rtl/rtl_to_pixels_top_pipelined.sv"
)
for dims in 3x3 5x4 8x5 640x480; do
    width="${dims%x*}"; height="${dims#*x}"
    exec_cmd verilator --lint-only -Wall --top-module rtl_to_pixels_top_pipelined -GIMG_WIDTH="$width" -GIMG_HEIGHT="$height" "${SOURCE_LIST[@]}"
done

tmp_stage="$(mktemp -d)"
cat > "$tmp_stage/Makefile" <<'EOF2'
TOPLEVEL_LANG = verilog
SIM ?= verilator
THIS_DIR := __ROOT__/tb/tests/
ROOT := __ROOT__
VERILOG_SOURCES = $(ROOT)/rtl/elastic_stage.sv
TOPLEVEL = elastic_stage
COCOTB_TEST_MODULES = test_elastic_stage
COMPILE_ARGS += -GDATA_WIDTH=28
export PYTHONPATH := $(ROOT):$(THIS_DIR):$(PYTHONPATH)
include $(shell cocotb-config --makefiles)/Makefile.sim
EOF2
python3 - "$tmp_stage/Makefile" "$ROOT" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
path.write_text(path.read_text().replace("__ROOT__", sys.argv[2]))
PY
stage_build="$(mktemp -d)"
echo "=== elastic_stage DATA_WIDTH=28 ===" | tee -a "$LOG"
set +e
env PATH="$ROOT/.venv/bin:$PATH" SIM_BUILD="$stage_build" COCOTB_RESULTS_FILE="$stage_build/results.xml" make -f "$tmp_stage/Makefile" 2>&1 | tee -a "$LOG"
stage_rc=${PIPESTATUS[0]}
set -e
rm -rf "$stage_build" "$tmp_stage"
test "$stage_rc" -eq 0

for dims in 3x3 5x4 8x5; do
    width="${dims%x*}"; height="${dims#*x}"
    run_sim Makefile.rtl_to_pixels_top_recovery "$width" "$height" ARCH_A_RECOVERY_REVALIDATION
    run_sim Makefile.rtl_to_pixels_top_pipelined "$width" "$height" GATE2_B
    run_sim Makefile.rtl_to_pixels_top_pipelined_streaming "$width" "$height" STREAMING_B
    run_sim Makefile.rtl_to_pixels_top_pipelined_recovery "$width" "$height" RECOVERY_B
    run_sim Makefile.rtl_to_pixels_top_pipelined_config "$width" "$height" CONFIG_B
done
for dims in 4x4 5x5 3x7 7x3 16x9 31x17; do
    width="${dims%x*}"; height="${dims#*x}"
    run_sim Makefile.rtl_to_pixels_top_pipelined_dimension_image "$width" "$height" RANDOM_DIMENSION_B CASE_KIND=random RESULTS_DIR="$ROOT/results/processed/arch-b"
done
run_sim Makefile.rtl_to_pixels_top_pipelined_dimension_image 640 480 CANONICAL_B CASE_KIND=real IMAGE_PATH="$ROOT/tb/images/Tokinokane2005-1-4.jpg" RESULTS_DIR="$ROOT/results/processed/arch-b"
"$ROOT/.venv/bin/python" - "$ROOT" <<'PY' 2>&1 | tee -a "$LOG"
import hashlib, sys
from pathlib import Path
import numpy as np
from PIL import Image
root = Path(sys.argv[1])
image = root / "tb/images/Tokinokane2005-1-4.jpg"
assert hashlib.sha256(image.read_bytes()).hexdigest() == "8331a2d0edb64057fdf31b1b1385430c58b2698942ef7d29e00e392b7350d5e4"
a = np.asarray(Image.open(root / "results/processed/gate3-real-rtl.png").convert("L"))
b = np.asarray(Image.open(root / "results/processed/arch-b/gate3-real-rtl.png").convert("L"))
assert a.shape == b.shape == (480, 640)
diff = np.abs(a.astype(np.int16) - b.astype(np.int16))
Image.fromarray(diff.astype(np.uint8), mode="L").save(root / "results/processed/arch-b/arch-a-vs-b-diff.png")
print(f"ARCH_A_B_CANONICAL_IMAGE_EQUIVALENCE=PASS diff_nonzero={int(np.count_nonzero(diff))} max_abs_diff={int(diff.max())}")
PY
exec_cmd "$ROOT/.venv/bin/python" -m pytest -q "$ROOT/tb/tests/test_reference_model.py"
echo "ARCH_B_FUNCTIONAL_REGRESSION=PASS" | tee -a "$LOG"
