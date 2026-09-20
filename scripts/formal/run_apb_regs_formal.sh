#!/usr/bin/env bash

set -euo pipefail

ROOT="$(
    cd "$(dirname "${BASH_SOURCE[0]}")/../.." &&
    pwd
)"

FORMAL_TOOLCHAIN_ROOT="${FORMAL_TOOLCHAIN_ROOT:-$HOME/.local/share/from-rtl-to-pixels/oss-cad-suite-current}"

export FORMAL_TOOLCHAIN_ROOT
export PATH="$FORMAL_TOOLCHAIN_ROOT/bin:$PATH"

"$ROOT/scripts/formal/check_toolchain.sh"

work="$(mktemp -d)"

cleanup() {
    rm -rf "$work"
}

trap cleanup EXIT

cd "$ROOT/formal"

echo
echo "=== APB REGS PROVE ==="
echo "observation=yosys-read_verilog-plus-expose"
echo "engine=smtbmc"
echo "solver=z3"
echo "mode=prove"
echo "depth=24"

sby -f -d "$work/prove" apb_regs_prove.sby
test -f "$work/prove/PASS"

echo
echo "APB_REGS_PROVE=PASS"

echo
echo "=== APB REGS COVER ==="
echo "observation=yosys-read_verilog-plus-expose"
echo "engine=smtbmc"
echo "solver=z3"
echo "mode=cover"
echo "depth=24"

sby -f -d "$work/cover" apb_regs_cover.sby
test -f "$work/cover/PASS"

echo
echo "APB_REGS_COVER=PASS"
echo "Review every named cover in the SBY output."
echo "APB_REGS_FORMAL=PASS"
