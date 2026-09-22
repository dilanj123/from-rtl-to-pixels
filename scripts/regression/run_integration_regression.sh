#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$ROOT"
run(){ local mf="$1"; local w="$2"; local h="$3"; local t; t=$(mktemp -d); PATH="$ROOT/.venv/bin:$PATH" IMG_WIDTH="$w" IMG_HEIGHT="$h" SIM_BUILD="$t" COCOTB_RESULTS_FILE="$t/results.xml" make -f "$mf"; python3 - "$t" <<'PY'
import shutil,sys; shutil.rmtree(sys.argv[1],ignore_errors=True)
PY
}
for arch in rtl_to_pixels_top rtl_to_pixels_top_pipelined; do
 for d in '3 3' '5 4' '8 5'; do set -- $d; run tb/tests/Makefile.${arch} "$1" "$2"; run tb/tests/Makefile.${arch}_streaming "$1" "$2"; run tb/tests/Makefile.${arch}_recovery "$1" "$2"; run tb/tests/Makefile.${arch}_config "$1" "$2"; done
done
echo INTEGRATION_REGRESSION=PASS
