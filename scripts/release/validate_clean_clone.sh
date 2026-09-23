#!/usr/bin/env bash
set -euo pipefail
REPO="${1:?repository URL}"; REF="${2:?commit/ref}"; ROOT=$(mktemp -d)
cleanup(){ rm -rf "$ROOT"; }; trap cleanup EXIT
git clone "$REPO" "$ROOT/repo" >/dev/null; cd "$ROOT/repo"; git checkout --detach "$REF" >/dev/null; test "$(git rev-parse HEAD)" = "$(git rev-parse "$REF")"; test -z "$(git status --porcelain)"
python3 -m venv .venv; source .venv/bin/activate; python -m pip install --upgrade pip; python -m pip install -r requirements-dev.txt
FORMAL_TOOLCHAIN_ROOT="${FORMAL_TOOLCHAIN_ROOT:-$HOME/.local/share/from-rtl-to-pixels/oss-cad-suite-current}"
export FORMAL_TOOLCHAIN_ROOT
export PATH="$FORMAL_TOOLCHAIN_ROOT/bin:$PATH"
make help; make doctor; make lint; make test-unit; make test; make test-real-image; make formal; make synth ARCH=compact; make synth ARCH=pipelined; make timing ARCH=compact FREQ_MHZ=35 SEED=1; make timing ARCH=pipelined FREQ_MHZ=60 SEED=1; python scripts/analysis/check_publication_assets.py; make ppa
git diff --exit-code -- rtl tb/reference tb/tests
printf 'validated commit=%s\npython=%s\nverilator=%s\nyosys=%s\nsby=%s\nz3=%s\nnextpnr=%s\n' "$(git rev-parse HEAD)" "$(python --version 2>&1)" "$(verilator --version 2>&1 | head -1)" "$(yosys -V 2>&1 | head -1)" "$(sby --version 2>&1 | head -1)" "$(z3 --version 2>&1 | head -1)" "$(nextpnr-ecp5 --version 2>&1 | head -1)"
echo CLEAN_CLONE_VALIDATION=PASS
