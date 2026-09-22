#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARCH="${1:?compact|pipelined}"; FREQ="${2:?frequency MHz}"; SEED="${3:?seed}"
case "$ARCH" in
 compact) LABEL='A / compact'; BUILD="$ROOT/build/impl/arch-a/640x480";;
 pipelined) LABEL='B / post-GxGy elastic'; BUILD="$ROOT/build/impl/arch-b/640x480";;
 *) echo "unknown architecture: $ARCH" >&2; exit 2;;
esac
export OSS_CAD_SUITE_ROOT="${OSS_CAD_SUITE_ROOT:-$HOME/.local/share/from-rtl-to-pixels/oss-cad-suite-current}"; export PATH="$OSS_CAD_SUITE_ROOT/bin:$PATH"
OUT="$BUILD/route/freq-${FREQ}MHz-seed-${SEED}"; mkdir -p "$OUT"
set +e
nextpnr-ecp5 --45k --package CABGA381 --speed 6 --json "$BUILD/netlist.json" --freq "$FREQ" --seed "$SEED" --timing-allow-fail --lpf-allow-unconstrained --report "$OUT/nextpnr-report.json" --detailed-timing-report --textcfg "$OUT/route.config" > "$OUT/nextpnr.log" 2>&1
RC=$?
set -e
if [ "$RC" -ne 0 ]; then echo "ROUTE_STATUS=FAIL" > "$OUT/status.txt"; echo "TIMING_STATUS=FAIL" >> "$OUT/status.txt"; exit "$RC"; fi
echo "ROUTE_STATUS=PASS" > "$OUT/status.txt"
python3 "$ROOT/scripts/analysis/summarize_ecp5_impl.py" --architecture "$LABEL" --dimensions 640x480 --device LFE5U-45F --package CABGA381 --speed 6 --seed "$SEED" --target-mhz "$FREQ" --yosys-stat "$BUILD/yosys-stat.json" --report "$OUT/nextpnr-report.json" --log "$OUT/nextpnr.log" --output "$OUT/summary.json"
python3 - "$OUT/summary.json" "$OUT/status.txt" <<'PY'
import json,sys
s=json.load(open(sys.argv[1])); print('TIMING_STATUS='+('PASS' if s.get('timing_clean') else 'FAIL'))
with open(sys.argv[2],'a') as f: f.write('TIMING_STATUS='+('PASS' if s.get('timing_clean') else 'FAIL')+'\n')
PY
