#!/usr/bin/env bash
set -euo pipefail
[ "$#" -eq 2 ] || { echo "usage: $0 <frequency_MHz> <seed>" >&2; exit 2; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export OSS_CAD_SUITE_ROOT="${OSS_CAD_SUITE_ROOT:-$HOME/.local/share/from-rtl-to-pixels/oss-cad-suite-current}"
export PATH="$OSS_CAD_SUITE_ROOT/bin:$PATH"
FREQ="$1"; SEED="$2"; BUILD="$ROOT/build/impl/arch-a/640x480"; OUT="$BUILD/route/freq-${FREQ}MHz-seed-${SEED}"
mkdir -p "$OUT"
nextpnr-ecp5 --45k --package CABGA381 --speed 6 --json "$BUILD/arch-a.json" --freq "$FREQ" --seed "$SEED" --timing-allow-fail --lpf-allow-unconstrained --report "$OUT/nextpnr-report.json" --detailed-timing-report --textcfg "$OUT/route.config" > "$OUT/nextpnr.log" 2>&1
printf 'ROUTE_STATUS=PASS\n' | tee "$OUT/status.txt"
python3 "$ROOT/scripts/analysis/summarize_ecp5_impl.py" --dimensions 640x480 --device LFE5U-45F --package CABGA381 --speed 6 --seed "$SEED" --target-mhz "$FREQ" --yosys-stat "$BUILD/yosys-stat.json" --report "$OUT/nextpnr-report.json" --log "$OUT/nextpnr.log" --output "$OUT/summary.json"
python3 - "$OUT/summary.json" "$OUT/status.txt" <<'PY'
import json,sys
s=json.load(open(sys.argv[1])); timing=bool(s.get('timing_clean'))
with open(sys.argv[2],'a') as f: f.write('TIMING_STATUS='+('PASS' if timing else 'FAIL')+'\n')
print('TIMING_STATUS='+('PASS' if timing else 'FAIL'))
PY
