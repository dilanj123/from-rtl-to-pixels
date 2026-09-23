#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
run() {
  local makefile="$1"
  local width="${2:-}"
  local height="${3:-}"
  local sim_build

  sim_build=$(mktemp -d)
  PATH="$ROOT/.venv/bin:$PATH" \
    IMG_WIDTH="$width" IMG_HEIGHT="$height" \
    SIM_BUILD="$sim_build" COCOTB_RESULTS_FILE="$sim_build/results.xml" \
    make -f "$makefile"
  rm -rf "$sim_build"
}

PATH="$ROOT/.venv/bin:$PATH" .venv/bin/python -m pytest -q tb/tests/test_reference_model.py
run tb/tests/Makefile.rgb_to_gray
run tb/tests/Makefile.elastic_stage
run tb/tests/Makefile.apb_regs
for x in 3 5; do run tb/tests/Makefile.pixel_control $x $x; done
for x in 3 7; do run tb/tests/Makefile.line_buffer $x; done
for dimensions in '3 3' '5 4' '8 5'; do
  set -- $dimensions
  run tb/tests/Makefile.window_3x3 "$1" "$2"
  run tb/tests/Makefile.output_control "$1" "$2"
done
run tb/tests/Makefile.sobel_compact
run tb/tests/Makefile.magnitude_clamp
run tb/tests/Makefile.threshold_stage
echo UNIT_REGRESSION=PASS
