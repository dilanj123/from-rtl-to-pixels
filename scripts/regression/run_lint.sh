#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
SOURCES="rtl/pixel_pkg.sv rtl/rgb_to_gray.sv rtl/elastic_stage.sv rtl/apb_regs.sv rtl/pixel_control.sv rtl/line_buffer.sv rtl/window_3x3.sv rtl/sobel_compact.sv rtl/magnitude_clamp.sv rtl/threshold_stage.sv rtl/output_control.sv"
for cfg in "rtl_to_pixels_top rtl/rtl_to_pixels_top.sv 3 3" "rtl_to_pixels_top rtl/rtl_to_pixels_top.sv 640 480" "rtl_to_pixels_top_pipelined rtl/rtl_to_pixels_top_pipelined.sv 3 3" "rtl_to_pixels_top_pipelined rtl/rtl_to_pixels_top_pipelined.sv 640 480"; do
 set -- $cfg; verilator --lint-only -Wall --top-module "$1" -GIMG_WIDTH="$3" -GIMG_HEIGHT="$4" $SOURCES "$2"; done
echo RELEASE_LINT=PASS
