#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
mkdir -p results/raw
exec > >(tee results/raw/arch-ab-comparison.log) 2>&1
scripts/synth/check_ecp5_toolchain.sh

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
)

verilator --lint-only -Wall --top-module rtl_to_pixels_top \
  -GIMG_WIDTH=640 -GIMG_HEIGHT=480 "${SOURCES[@]}" rtl/rtl_to_pixels_top.sv
verilator --lint-only -Wall --top-module rtl_to_pixels_top_pipelined \
  -GIMG_WIDTH=640 -GIMG_HEIGHT=480 "${SOURCES[@]}" \
  rtl/rtl_to_pixels_top_pipelined.sv
scripts/synth/run_arch_synth.sh compact
scripts/synth/run_arch_synth.sh pipelined
python3 scripts/timing/search_arch_frequency.py --architecture compact
python3 scripts/timing/search_arch_frequency.py --architecture pipelined
printf 'ARCH_AB_CONTROLLED_COMPARISON=PASS\n'
