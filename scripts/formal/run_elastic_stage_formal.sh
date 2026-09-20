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

work="$(
    mktemp -d
)"

cleanup() {
    rm -rf "$work"
}

trap cleanup EXIT

cd "$ROOT/formal"

echo
echo "=== ELASTIC STAGE PROVE ==="
echo "DATA_WIDTH=11"
echo "engine=smtbmc"
echo "solver=z3"
echo "mode=prove"
echo "depth=20"

sby \
    -f \
    -d "$work/prove" \
    elastic_stage_prove.sby

test -f "$work/prove/PASS"

echo
echo "ELASTIC_STAGE_PROVE=PASS"

echo
echo "=== ELASTIC STAGE COVER ==="
echo "DATA_WIDTH=11"
echo "engine=smtbmc"
echo "solver=z3"
echo "mode=cover"
echo "depth=20"

sby \
    -f \
    -d "$work/cover" \
    elastic_stage_cover.sby

test -f "$work/cover/PASS"

echo
echo "ELASTIC_STAGE_COVER=PASS"
echo
echo "All named cover statements must be reviewed in the SBY output."
echo "ELASTIC_STAGE_FORMAL=PASS"
