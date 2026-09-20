#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OSS_CAD_SUITE_ROOT="${OSS_CAD_SUITE_ROOT:-$HOME/.local/share/from-rtl-to-pixels/oss-cad-suite-current}"
export PATH="$OSS_CAD_SUITE_ROOT/bin:$PATH"
for tool in yosys nextpnr-ecp5 ecppack; do
  command -v "$tool" >/dev/null || { echo "missing $tool" >&2; exit 1; }
  echo "$tool path: $(command -v "$tool")"
done
echo "YOSYS_VERSION=$(yosys -V)"
echo "NEXTPNR_VERSION=$(nextpnr-ecp5 --version)"
echo "ECPPACK_VERSION=$(ecppack --version)"
yosys -Q -T -p 'help synth_ecp5' >/dev/null
nextpnr-ecp5 --45k --package CABGA381 --speed 6 --test
echo "ECP5_IMPLEMENTATION_TOOLCHAIN_CHECK=PASS"
