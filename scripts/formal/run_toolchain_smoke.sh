#!/usr/bin/env bash

set -euo pipefail

ROOT="$(
    cd "$(dirname "${BASH_SOURCE[0]}")/../.." &&
    pwd
)"

if [[ -n "${FORMAL_TOOLCHAIN_ROOT:-}" ]]; then
    export PATH="${FORMAL_TOOLCHAIN_ROOT}/bin:${PATH}"
fi

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
echo "=== PROVE SMOKE ==="

sby \
    -f \
    -d "$work/prove" \
    "$ROOT/formal/toolchain_smoke_prove.sby"

echo
echo "=== COVER SMOKE ==="

sby \
    -f \
    -d "$work/cover" \
    "$ROOT/formal/toolchain_smoke_cover.sby"

echo
echo "FORMAL_TOOLCHAIN_SMOKE=PASS"
