# Project State

Current phase: Phase 3 — Primitive RTL
Current gate: Gate 1 CLOSED; Gate 2 OPEN
Known-good commit before Phase 3: `57fa1f438e23015f50ad91fb0e2faf0582cac18c`
Current architecture: frozen single-clock streaming Sobel specification; pixel types, combinational RGB-to-grayscale primitive, one-entry elastic stage, and APB CSR primitive implemented

Gate 0:
CLOSED — environment/repository/bootstrap established.

Gate 1:
CLOSED — project contract, interfaces, arithmetic, alignment, drain, reset,
configuration, verification strategy, formal scope, A/B experiment and reuse
policy are frozen and synchronized.

Reference model:
REFERENCE-MODEL VERIFIED by the focused Phase-2 pytest suite.
Evidence: results/raw/reference-model-pytest.log

Phase 3 simulation toolchain:
Verilator 5.052 and cocotb 2.1.0 installed and smoke-checked using a temporary non-project XOR fixture.
Evidence: results/raw/sim-toolchain-smoke.log

RTL simulation:
`rgb_to_gray`: RTL SIMULATION VERIFIED under the focused regression: 3 tests, 2317 RGB vectors against the independent Python grayscale oracle.
Evidence: results/raw/rgb-to-gray-cocotb.log
`elastic_stage`: RTL SIMULATION VERIFIED under the six-test focused one-entry ready/valid regression.
Evidence: results/raw/elastic-stage-cocotb.log
`apb_regs`: RTL SIMULATION VERIFIED under the seven-test focused APB regression, including test-only VPI preload for FRAME_COUNT rollover.
Evidence: results/raw/apb-regs-cocotb.log
Previously verified reference-model, RGB-to-grayscale, and elastic-stage evidence remains established; all regressions still pass.
No frame controller, Sobel, line-buffer/window, or top-level integration exists.

Formal:
not run

Synthesis:
not run

Timing:
not run

Known future workflow dependencies:
- Yosys/SBY/formal solver for formal
- nextpnr-ecp5/ECP5 database for implementation

Current bottleneck:
Review the focused APB register evidence before selecting the next primitive.

Next task:
Next primitive pending ChatGPT review.
