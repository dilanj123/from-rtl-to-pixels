#!/usr/bin/env bash

set -euo pipefail

if [[ -n "${FORMAL_TOOLCHAIN_ROOT:-}" ]]; then
    export PATH="${FORMAL_TOOLCHAIN_ROOT}/bin:${PATH}"
fi

required_tools=(
    yosys
    sby
    yosys-smtbmc
    z3
)

echo "Formal toolchain check"

for tool in "${required_tools[@]}"; do
    path="$(command -v "$tool" || true)"

    if [[ -z "$path" ]]; then
        echo "MISSING: $tool" >&2
        exit 1
    fi

    echo "$tool: $path"
done

echo
echo "Versions:"

yosys -V
sby --version
z3 --version

echo
echo "yosys-smtbmc:"
command -v yosys-smtbmc

echo
echo "FORMAL_TOOLCHAIN_ROOT=${FORMAL_TOOLCHAIN_ROOT:-<PATH>}"
echo "FORMAL_TOOLCHAIN_CHECK=PASS"
