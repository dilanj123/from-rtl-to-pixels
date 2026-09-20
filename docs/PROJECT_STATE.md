# Project State

Current phase: Phase 5 — Magnitude and clamp arithmetic
Current gate: Gate 1 CLOSED; Gate 2 OPEN
Known-good commit before Phase 5: `597af7f8c0edfac2dfb2763e042a7d17acf17b8d`
Current architecture: frozen single-clock streaming Sobel specification; pixel types, combinational RGB-to-grayscale primitive, one-entry elastic stage, APB CSR primitive, accepted-input coordinate/metadata control, two-row vertical-history line buffer, 3x3 window primitive, logical output-position/drain controller, compact combinational Sobel Gx/Gy primitive, and compact magnitude/clamp primitive implemented

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
`pixel_control`: RTL SIMULATION VERIFIED under the focused 3x3 and 5x4 regressions (7 tests each).
Evidence: results/raw/pixel-control-cocotb.log
`line_buffer`: RTL SIMULATION VERIFIED under the focused width-3 and width-7 regressions (7 tests each), checking pre-write same-column history, commit-only updates, and frame/reset invalidation.
Evidence: results/raw/line-buffer-cocotb.log
`window_3x3`: RTL SIMULATION VERIFIED under the focused 3x3, 5x4, and 8x5 regressions (7 tests each), using supplied pre-write vertical-history inputs.
Evidence: results/raw/window-3x3-cocotb.log
`output_control`: RTL SIMULATION VERIFIED under the focused 3x3, 5x4, and 8x5 regressions (7 tests each). W+1 logical mapping and final-drain control now have focused simulation evidence, under `pixel_commit_i -> input_allow_o`.
Evidence: results/raw/output-control-cocotb.log
`sobel_compact`: RTL SIMULATION VERIFIED under the focused seven-test arithmetic regression (4369 windows), with strict lint clean.
Evidence: results/raw/sobel-compact-cocotb.log
`magnitude_clamp`: RTL SIMULATION VERIFIED under the focused seven-test arithmetic regression. The initial lint defect was corrected before verification, without lint suppression; the reference suite passed all 13 tests.
Evidence: results/raw/magnitude-clamp-cocotb.log
Previously verified reference-model and primitive evidence remains established. The reference suite passed all 13 tests; established RTL/test/Makefile sources were unchanged. The approved accelerated isolated-leaf policy was used, without rebuilding historical RTL regressions.
Sobel and magnitude/clamp are not yet integrated with window/control. No threshold integration or top-level exists. Output pixel values and top-level stream protocol are not verified.
`pixel_control.accept_i` represents accepted input; that primitive does not generate ready or implement RUN_ENABLE/DRAIN admission.

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
Review the focused magnitude/clamp arithmetic evidence before the next arithmetic primitive.

Next task:
Next arithmetic primitive: `threshold_stage`, pending ChatGPT review. Full accumulated RTL regression remains scheduled after `threshold_stage`, immediately before Architecture-A integration.
