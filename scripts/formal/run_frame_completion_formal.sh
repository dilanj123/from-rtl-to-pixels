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
cleanup() { rm -rf "$work"; }
trap cleanup EXIT

cd "$ROOT/formal"

run_job() {
    local label="$1" file="$2" dir="$3"
    echo
    echo "=== $label ==="
    echo "engine=smtbmc"
    echo "solver=z3"
    echo "depth=64"
    sby -f -d "$work/$dir" "$file"
    test -f "$work/$dir/PASS"
    echo "$label=PASS"
}

run_job FRAME_COMPLETION_3X3_PROVE frame_completion_3x3_prove.sby 3x3-prove
run_job FRAME_COMPLETION_3X3_COVER frame_completion_3x3_cover.sby 3x3-cover
run_job FRAME_COMPLETION_5X4_PROVE frame_completion_5x4_prove.sby 5x4-prove
run_job FRAME_COMPLETION_5X4_COVER frame_completion_5x4_cover.sby 5x4-cover

echo
echo "FRAME_COMPLETION_FORMAL=PASS"
