#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
test "$(shasum -a 256 tb/images/Tokinokane2005-1-4.jpg | awk '{print $1}')" = 8331a2d0edb64057fdf31b1b1385430c58b2698942ef7d29e00e392b7350d5e4
for arch in rtl_to_pixels_top rtl_to_pixels_top_pipelined; do t=$(mktemp -d); out="$ROOT/results/processed/public-$arch"; mkdir -p "$out"; PATH="$ROOT/.venv/bin:$PATH" IMG_WIDTH=640 IMG_HEIGHT=480 CASE_KIND=real IMAGE_PATH="$ROOT/tb/images/Tokinokane2005-1-4.jpg" RESULTS_DIR="$out" SIM_BUILD="$t" COCOTB_RESULTS_FILE="$t/results.xml" make -f "tb/tests/Makefile.${arch}_dimension_image"; python3 - "$t" <<'PY'
import shutil,sys; shutil.rmtree(sys.argv[1],ignore_errors=True)
PY
done
echo REAL_IMAGE_REGRESSION=PASS
