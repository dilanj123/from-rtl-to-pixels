# Project State

Current phase: Phase 9 — Bottleneck review
Current gate: Gate 3 CLOSED; Gate 4 OPEN
Historical known-good commit before Phase 5: `597af7f8c0edfac2dfb2763e042a7d17acf17b8d`
Streaming baseline commit: `a73be9929b6f73329e86790e7726eef8dae4e62d`; subsequent monitor/coverage strengthening is recorded in results/raw/gate3-streaming-monitor-coverage.log.
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
Evidence: results/raw/gate3-streaming-stress-cocotb.log (historical; targeted metadata coverage and valid persistence were not fully asserted).
Strengthened streaming checks: 5/5 tests passed at each of 3x3, 5x4 and 8x5, with zero mismatches. Pending stalled transactions require valid and unchanged data/SOF/EOL through transfer. Per-output counters assert two stalls at SOF and each EOL, and the specified stalls at every final W+1 drain position (including four on the final output). Monitor negative checks reject injected valid/data/SOF/EOL violations; idle cycles do not consume targeted stall budgets.
Evidence: results/raw/gate3-streaming-monitor-coverage.log; strict lint and all 13 reference tests also passed.
Previously verified reference-model and primitive evidence remains established. The reference suite passed all 13 tests; established RTL/test/Makefile sources were unchanged. The approved accelerated isolated-leaf policy was used, without rebuilding historical RTL regressions.
Deferred full accumulated checkpoint: all established primitive/reference regressions passed after the compact arithmetic leaves; evidence: results/raw/arithmetic-checkpoint-regression.log. This verifies individual regressions only, not integrated geometry plus arithmetic or a complete RTL frame.
Production Architecture A reset/malformed-metadata recovery regression exercises synchronous reset from idle, pre-frame, first-pixel, mid-line, EOL, late-frame and DRAIN states, plus accepted early/missing EOL and unexpected SOF metadata errors. Under the tested 3x3, 5x4 and 8x5 configurations, reset restored the frozen defaults and clean-frame recovery remained bit-exact. Malformed accepted metadata aborted incomplete frames, set sticky FRAME_ERROR, prevented aborted-frame completion counting, required a new valid SOF, and allowed a subsequent bit-exact complete frame.
Evidence: results/raw/gate3-reset-metadata-cocotb.log
Classification: RTL SIMULATION VERIFIED.
Conditions: Verilator 5.052; cocotb 2.1.0; 11 focused recovery tests at each of 3x3, 5x4 and 8x5; independent `sobel_rgb` comparisons. All 33 recovered frames reported zero mismatches, exact W*H input/output counts and correct metadata. Strict lint passed without warnings; reference pytest passed all 13 tests. Partial outputs before abort are discarded, not recalled; physical RAM clearing is not claimed.
Random source gaps and backpressure are already RTL SIMULATION VERIFIED by the strengthened streaming regression above. The production top is simulation-verified only under the recorded small-dimension configurations and deterministic seeds.
Production Architecture A configuration timing regression verifies shadow/active threshold and bypass semantics through the complete production datapath, including idle CONFIG_PENDING activation, mid-frame deferred writes, same-edge APB-write/SOF pre-edge priority, and RUN_ENABLE new-frame-only admission behavior. At 3x3, 5x4 and 8x5, all six focused tests per dimension passed with independent `sobel_rgb` mismatch_count=0 and exact input/output counts.
Evidence: results/raw/gate3-config-timing-cocotb.log
Classification: RTL SIMULATION VERIFIED.
Conditions: Verilator 5.052; cocotb 2.1.0; 6 configuration-timing tests at each of 3x3, 5x4 and 8x5; independent `sobel_rgb` comparison.
Production Architecture A dimension/image regression adds 18 deterministic random complete frames at 4x4, 5x5, 3x7, 7x3, 16x9 and 31x17, plus a canonical 640x480 public-domain image frame. All recorded comparisons have exact input/output counts and mismatch_count=0; processed reference, RTL and diff artifacts are recorded.
Evidence: results/raw/gate3-dimension-image-cocotb.log
Classification: RTL SIMULATION VERIFIED.
Conditions: Verilator 5.052; cocotb 2.1.0; six legal dimensions with three random frames each; one 640x480 public-domain photograph; independent `sobel_rgb` comparison.
Gate 3 CLOSED — verified regression evidence now covers streaming stress, reset/malformed-metadata recovery, configuration timing, multiple legal dimensions, deterministic random frames, a canonical 640x480 public real-image frame, and requirements traceability.
Remaining Gate-3 work: none unresolved in the audited categories. Selected formal scope is complete. Architecture-A synthesis and routed timing evidence are recorded below; Architecture B remains unstarted.
`pixel_control.accept_i` represents accepted input; that primitive does not generate ready or implement RUN_ENABLE/DRAIN admission.

Formal:
SELECTED TARGETED FORMAL COMPLETE.

Passed under documented assumptions:
- F-ELASTIC-001
- F-ELASTIC-002
- F-ELASTIC-003
- F-APB-001
- F-APB-002
- F-CTRL-001 at 3x3 and 5x4
- F-OUT-001 at 3x3 and 5x4
- F-OUT-002 drain transition mechanics at 3x3 and 5x4
- F-FRAME-001 narrow completion integration at 3x3 and 5x4

Elastic-stage, APB/configuration, pixel-controller, output-control and final-token/frame-completion cover/vacuity checks are recorded.

F-FRAME-001 proves external final-token qualification of FRAME_COUNT in the narrow integration harness.

No whole-accelerator formal verification is claimed.

F-OUT-002 eventual drain completion is derived from the formally checked
transition mechanics under an explicit downstream fairness condition.

Evidence:
results/raw/formal-elastic-stage.log
results/raw/formal-apb-regs.log
results/raw/formal-pixel-control.log
results/raw/formal-output-control.log
results/raw/formal-frame-completion.log

No whole-accelerator formal verification is claimed.

Synthesis:
SYNTHESISED (Architecture A, canonical 640x480)

Place/route:
PLACED/ROUTED timing-clean at 35 MHz, seed 1; timing-failing at 50 MHz, seed 1

Timing:
35 MHz clean / 50 MHz fail, 5 MHz resolution, seed 1

Known future workflow dependencies:
- Yosys/SBY/formal solver for formal
- nextpnr-ecp5/ECP5 database for implementation

Current bottleneck:
Measured routed critical path is a routing-dominated mixed arithmetic path spanning rgb_to_gray, magnitude_clamp and threshold_stage; inspect this path before selecting Architecture-B pipeline boundaries.

Next task:
P9-ARCH-A-BOTTLENECK-001

Formal toolchain:
FORMAL TOOLCHAIN SMOKE VERIFIED.

A generic prove and cover smoke job passed with the recorded Yosys,
SymbiYosys and Z3 versions. The first targeted elastic-stage project
formal properties have since passed at DATA_WIDTH=11; whole-accelerator
formal verification is not claimed.

The targeted APB/configuration properties have also passed under documented
assumptions using formal-netlist-only Yosys expose observation of the actual
APB state wires. Evidence: results/raw/formal-apb-regs.log

Synthesis: Architecture A synthesised
Place/route: Architecture A routed; 35 MHz clean, 50 MHz fail, seed 1
Timing: routed timing evidence recorded
Architecture B: not started


Architecture-A implementation baseline:
SYNTHESISED. Canonical 640x480 placed/routed timing-clean at 35 MHz, seed 1; timing-failing at 50 MHz. Highest tested clean=35 MHz, lowest tested fail=50 MHz, resolution=5 MHz. Mapped resources: LUT4=665, TRELLIS_FF=194, CCU2C=113, DP16KD=2, MULT18X18D=3, PFUMX=102, L6MUX21=48. Critical path measured at 32.068 ns total (12.306 ns logic, 19.762 ns routing), a routing-dominated mixed arithmetic path spanning grayscale, magnitude/clamp and threshold logic.

Current bottleneck:
Measured routed critical path is a routing-dominated mixed arithmetic path spanning rgb_to_gray, magnitude_clamp and threshold_stage; inspect this path before selecting Architecture-B pipeline boundaries.

Phase 9 next task:
P9-ARCH-A-BOTTLENECK-001

Physical board: not run
Physical measurement: none
