#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
expected_sha="8331a2d0edb64057fdf31b1b1385430c58b2698942ef7d29e00e392b7350d5e4"
actual_sha="$(shasum -a 256 tb/images/Tokinokane2005-1-4.jpg | awk '{print $1}')"
test "$actual_sha" = "$expected_sha"

for arch in rtl_to_pixels_top rtl_to_pixels_top_pipelined; do
  sim_build=$(mktemp -d)
  output_dir="$ROOT/results/processed/public-$arch"
  mkdir -p "$output_dir"
  PATH="$ROOT/.venv/bin:$PATH" \
    IMG_WIDTH=640 IMG_HEIGHT=480 CASE_KIND=real \
    IMAGE_PATH="$ROOT/tb/images/Tokinokane2005-1-4.jpg" \
    RESULTS_DIR="$output_dir" SIM_BUILD="$sim_build" \
    COCOTB_RESULTS_FILE="$sim_build/results.xml" \
    make -f "tb/tests/Makefile.${arch}_dimension_image"
  rm -rf "$sim_build"
done
echo REAL_IMAGE_REGRESSION=PASS
