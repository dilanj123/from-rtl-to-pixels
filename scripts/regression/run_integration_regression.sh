#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
run() {
  local makefile="$1"
  local width="$2"
  local height="$3"
  local sim_build

  sim_build=$(mktemp -d)
  PATH="$ROOT/.venv/bin:$PATH" \
    IMG_WIDTH="$width" IMG_HEIGHT="$height" \
    SIM_BUILD="$sim_build" COCOTB_RESULTS_FILE="$sim_build/results.xml" \
    make -f "$makefile"
  rm -rf "$sim_build"
}

for arch in rtl_to_pixels_top rtl_to_pixels_top_pipelined; do
  for dimensions in '3 3' '5 4' '8 5'; do
    set -- $dimensions
    run "tb/tests/Makefile.${arch}" "$1" "$2"
    run "tb/tests/Makefile.${arch}_streaming" "$1" "$2"
    run "tb/tests/Makefile.${arch}_recovery" "$1" "$2"
    run "tb/tests/Makefile.${arch}_config" "$1" "$2"
  done
done
echo INTEGRATION_REGRESSION=PASS
