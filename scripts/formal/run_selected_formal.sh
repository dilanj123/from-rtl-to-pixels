#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
for s in run_elastic_stage_formal.sh run_apb_regs_formal.sh run_pixel_control_formal.sh run_output_control_formal.sh run_frame_completion_formal.sh; do "$ROOT/scripts/formal/$s"; done
echo SELECTED_FORMAL_REGRESSION=PASS
