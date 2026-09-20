# Project State

Current phase: Phase 5 — Production Architecture A / Gate 2
Current gate: Gate 2 CLOSED; Gate 3 OPEN
Known-good commit before Phase 5: `597af7f8c0edfac2dfb2763e042a7d17acf17b8d`
Current architecture: frozen single-clock streaming Sobel specification with production `rtl_to_pixels_top` and verified Architecture-A datapath integration at tested small dimensions

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
`threshold_stage`: RTL SIMULATION VERIFIED under the focused four-test regression; 70668 checks were derived from the exact test construction.
Evidence: results/raw/threshold-stage-cocotb.log
Architecture-A alignment harness: RTL SIMULATION VERIFIED under 5 tests at each of 3x3, 5x4, and 8x5. The test-only harness composes geometry and arithmetic paths and checks labelled windows, W+1 mapping, borders, source gaps, live/drain stalls, thresholding, and consecutive frames without reset.
Evidence: results/raw/architecture-a-alignment-cocotb.log
Production Architecture A: RTL SIMULATION VERIFIED under 4 complete deterministic RGB-frame tests at each of 3x3, 5x4, and 8x5. Exact accepted input/output counts, SOF/EOL metadata, independent Python comparisons with zero mismatches, APB configuration, frame count, and final external-token completion behavior passed.
Evidence: results/raw/gate2-top-cocotb.log
Production Architecture A streaming stress: RTL SIMULATION VERIFIED at 3x3, 5x4, and 8x5. Five tests per dimension exercised deterministic random RGB frames, source gaps, random and targeted backpressure, SOF/EOL stalls, drain stalls, output stability, exact counts, and independent `sobel_rgb` comparison with mismatch_count=0.
Evidence: results/raw/gate3-streaming-stress-cocotb.log
Previously verified reference-model and primitive evidence remains established. The reference suite passed all 13 tests; established RTL/test/Makefile sources were unchanged. The approved accelerated isolated-leaf policy was used, without rebuilding historical RTL regressions.
Deferred full accumulated checkpoint: all established primitive/reference regressions passed after the compact arithmetic leaves; evidence: results/raw/arithmetic-checkpoint-regression.log. This verifies individual regressions only, not integrated geometry plus arithmetic or a complete RTL frame.
The production top is verified only for the tested deterministic configurations. Randomized source gaps/backpressure, reset, malformed metadata, mid-frame configuration timing, same-edge APB-write/SOF integration, broad dimensions/canonical 640x480, random/real frames, traceability, formal, synthesis, P&R, timing, and Architecture B remain unverified.
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
Review the accumulated primitive checkpoint before Architecture-A integration/alignment verification.

Next task:
P6 reset + malformed-metadata production-top regression.
