# Evidence index

Classification: bootstrap checks, Gate-1 documentation, focused reference-model verification, and accumulated primitive regression evidence. Focused `rgb_to_gray`, `elastic_stage`, `apb_regs`, `pixel_control`, `line_buffer`, `window_3x3`, `output_control`, `sobel_compact`, `magnitude_clamp`, and `threshold_stage` RTL simulation evidence is recorded below; no formal, synthesis, or timing evidence exists yet.
Bootstrap commit: `f540928c1d04e0ae191236fb44c326404c70e755`. Pre-commit logs necessarily precede its hash.
Published Phase-0 baseline: `6bd14fca23b7f74e74fbe18f911d718478f49bbb`.
Gate-1 documentation commit: `a19678a45e5bbf4dad3ee5e250b7dfcbcddbd1a1` (`Freeze Gate 1 project contract`); specifications only; subsequently frozen by the Phase-2 task.
Conditions: arm64 macOS 26.4.1, current PATH and system Python, 2026-09-19.

| Claim / check | Commands and evidence |
|---|---|
| Source provenance | `results/raw/bootstrap-sources.log`: read-only source SHA-256 hashes |
| Host and executable inventory | `results/raw/bootstrap-checks.log`: exact commands, stdout/stderr, exit codes; `make help` and `make doctor` exit 0 |
| Unimplemented work fails | Same log: `make test` exit 2 |
| Missing/broken CORE fails | `results/raw/bootstrap-negative-checks.log`: isolated PATH and exit-9 stub probes |
| Initial directory / Git setup | `results/raw/bootstrap-inspection.log` |
| Staged review | `results/raw/bootstrap-staged-review.log`; excludes itself because recorded after the first staging |
| Commit / final working tree | Local ignored `results/raw/bootstrap-postcommit.log`, produced after the bootstrap commit; contains commit hash and final status |

Gate 0 evidence: the bootstrap logs record the original OS/architecture, CORE paths/versions and then-missing tools. GitHub CLI is now available and authenticated as `dilanj123`; the public origin is `https://github.com/dilanj123/from-rtl-to-pixels.git`. Check current state with `gh auth status`, `gh repo view --json url,visibility`, and `git remote -v`; historical bootstrap logs remain unchanged. `make doctor` works under the CORE-only bootstrap policy. Verilator and cocotb are now installed and smoke-checked (see `results/raw/sim-toolchain-smoke.log`); Yosys, SBY, formal solvers and nextpnr-ecp5 remain unavailable on PATH. ECP5 usability remains unproven.

Gate 1 was closed by the Phase-2 task. Only the focused `rgb_to_gray`, `elastic_stage`, `apb_regs`, `pixel_control`, `line_buffer`, `window_3x3`, `output_control`, and `sobel_compact` primitives have RTL simulation evidence; no complete accelerator, formal, synthesis, or timing results are claimed.

Claim: Independent Python Sobel reference-model focused suite passes.
Git commit: `57fa1f438e23015f50ad91fb0e2faf0582cac18c`
Command: `.venv/bin/python -m pytest -q tb/tests/test_reference_model.py`
Evidence: `results/raw/reference-model-pytest.log`
Conditions: Python 3.14.0; NumPy 2.5.3; Pillow 12.3.0; pytest 9.1.1; 13 focused tests.
Classification: `REFERENCE-MODEL VERIFIED`

Claim: `rgb_to_gray` matches the independent Python grayscale oracle across the focused primitive regression.
Git commit: the commit adding this entry (`Add verified RGB to grayscale primitive`).
Command: temporary-build `make -f tb/tests/Makefile.rgb_to_gray`
Evidence: `results/raw/rgb-to-gray-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; 13 directed + 256 grayscale-identity + 2048 deterministic-random RGB vectors.
Classification: `RTL SIMULATION VERIFIED`

Claim: `threshold_stage` implements the frozen threshold-only bypass rule: bypass returns M8 unchanged; otherwise M8<threshold -> 0, and M8>=threshold -> M8.
Git commit: the commit adding this entry (`Add verified threshold stage and regression checkpoint`).
Command: `verilator --lint-only -Wall rtl/threshold_stage.sv --top-module threshold_stage`; temporary-build `make -f tb/tests/Makefile.threshold_stage`.
Evidence: `results/raw/threshold-stage-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; 4 focused tests; 70668 checked combinations derived from the exact test construction, including the complete 256x256 non-bypass domain, 1024 bypass checks, and 4096 deterministic mixed-mode checks.
Classification: `RTL SIMULATION VERIFIED`

Claim: All established primitive and reference regressions pass after completion of the compact arithmetic leaves.
Command: the accumulated runner recorded each configured invocation in sequence and stopped on nonzero exit.
Evidence: `results/raw/arithmetic-checkpoint-regression.log`
Conditions: 17 cases passed: reference pytest; rgb_to_gray; elastic_stage; apb_regs; pixel_control 3x3 and 5x4; line_buffer width 3 and 7; window_3x3 3x3, 5x4, and 8x5; output_control 3x3, 5x4, and 8x5; sobel_compact; magnitude_clamp; threshold_stage.
Classification: `RTL SIMULATION VERIFIED`
Limitations: This proves the individual established regressions pass in their isolated configurations. It does not prove integrated geometry plus arithmetic, a complete RTL frame, deep backpressure integration, formal properties, synthesis, P&R, timing, or Architecture B.

Claim: The Architecture-A geometry/arithmetic alignment harness composes `line_buffer`, `window_3x3`, `output_control`, `sobel_compact`, `magnitude_clamp` and `threshold_stage` with transfer-qualified image state. Under the tested small-frame configurations, logical output coordinates, labelled interior windows, arithmetic results, borders, W+1 drain, source gaps, live stalls and drain stalls remain aligned.
Git commit: the commit adding this entry (`Add verified Architecture A alignment harness`).
Command: composed `verilator --lint-only -Wall` followed by temporary-build `make -f tb/tests/Makefile.architecture_a_alignment` at 3x3, 5x4, and 8x5; `.venv/bin/python -m pytest -q tb/tests/test_reference_model.py`.
Evidence: `results/raw/architecture-a-alignment-cocotb.log`
Classification: `RTL SIMULATION VERIFIED`
Conditions: Verilator 5.052; cocotb 2.1.0; 5 focused tests at 3x3; 5 focused tests at 5x4; 5 focused tests at 8x5; independent labelled-window and Sobel arithmetic scoreboard.
Limitations: This is a test-only composition harness. It does not prove production `rtl_to_pixels_top` integration, RGB stream integration, `pixel_control` integration, APB integration, active/shadow configuration interaction in the complete datapath, elastic output metadata/data coupling, malformed-frame top-level recovery, complete RGB frame versus the Python reference, Gate 2 closure, formal, synthesis, P&R, timing, or Architecture B.

Claim: `elastic_stage` satisfies the focused one-entry ready/valid regression.
Git commit: the commit adding this entry (`Add verified elastic ready-valid stage`).
Command: temporary-build `make -f tb/tests/Makefile.elastic_stage`
Evidence: `results/raw/elastic-stage-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; six focused tests including randomized token conservation.
Classification: `RTL SIMULATION VERIFIED`

Claim: `apb_regs` satisfies the focused APB CSR regression.
Git commit: the commit adding this entry (`Add verified APB register block`).
Command: temporary-build `make -f tb/tests/Makefile.apb_regs`
Evidence: `results/raw/apb-regs-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; seven focused tests. FRAME_COUNT rollover uses test-only VPI preload of internal `frame_count_q` to `0xFFFFFFFF`, then the normal increment and APB readback paths; this is not an APB-visible write feature.
Classification: `RTL SIMULATION VERIFIED`

Claim: `pixel_control` tracks accepted input coordinates and validates SOF/EOL metadata under the focused legal-dimension regressions.
Git commit: the commit adding this entry (`Add verified pixel position control`).
Command: temporary-build `make -f tb/tests/Makefile.pixel_control` with IMG_WIDTH/IMG_HEIGHT set to 3/3, then 5/4.
Evidence: `results/raw/pixel-control-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; 7 tests at 3x3 plus 7 tests at 5x4.
Classification: `RTL SIMULATION VERIFIED`

Claim: `line_buffer` supplies correct same-column one-row/two-row history with commit-only updates and frame/reset invalidation.
Git commit: the commit adding this entry (`Add verified two-row line buffer`).
Command: temporary-build `make -f tb/tests/Makefile.line_buffer` with IMG_WIDTH=3, then IMG_WIDTH=7.
Evidence: `results/raw/line-buffer-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; 7 tests at IMG_WIDTH=3; 7 tests at IMG_WIDTH=7. History taps are checked before the committing rising edge.
Classification: `RTL SIMULATION VERIFIED`

Claim: `window_3x3` assembles exact 3x3 labelled neighborhoods from current-pixel and two-row-history inputs, with correct horizontal ordering, row-boundary clearing, commit-only updates and frame/reset invalidation.
Git commit: the commit adding this entry (`Add verified 3x3 window generator`).
Command: temporary-build `make -f tb/tests/Makefile.window_3x3` at IMG_WIDTH/IMG_HEIGHT 3/3, 5/4, and 8/5.
Evidence: `results/raw/window-3x3-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; 7 tests at 3x3; 7 tests at 5x4; 7 tests at 8x5. Tests supply vertical-history inputs and inspect the window before the committing edge; no integrated line-buffer/window verification is claimed.
Classification: `RTL SIMULATION VERIFIED`

Claim: `output_control` implements the frozen W+1 input/output alignment, sequential logical output positions, border classification, exact W+1 final drain, drain backpressure stability, no-frame-overlap admission, and final-output completion event.
Git commit: the commit adding this entry (`Add verified W+1 output drain control`).
Command: temporary-build `make -f tb/tests/Makefile.output_control` at IMG_WIDTH/IMG_HEIGHT 3/3, 5/4, and 8/5.
Evidence: `results/raw/output-control-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; 7 tests at 3x3; 7 tests at 5x4; 7 tests at 8x5. Integration assumes `pixel_commit_i -> input_allow_o`; evidence covers logical positions, not pixel values or top-level stream protocol.
Classification: `RTL SIMULATION VERIFIED`

Claim: `sobel_compact` implements the frozen compact Architecture-A Sobel Gx/Gy equations with signed 12-bit outputs.
Git commit: the commit adding this entry (`Add verified compact Sobel arithmetic`).
Command: `verilator --lint-only -Wall rtl/sobel_compact.sv --top-module sobel_compact`; temporary-build `make -f tb/tests/Makefile.sobel_compact`; `.venv/bin/python -m pytest -q tb/tests/test_reference_model.py`.
Evidence: `results/raw/sobel-compact-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; strict lint exit 0 without warnings; 7 focused tests; 4369 checked Sobel windows, including 256 exhaustive binary-extreme patterns and 4096 deterministic random windows; reference pytest 13 passed. All commands exited 0.
Classification: `RTL SIMULATION VERIFIED`
Limitations: focused arithmetic evidence only; not yet integrated with `window_3x3`; no magnitude/clamp or threshold in this block; no complete-frame RTL evidence; no formal, synthesis/P&R, or timing evidence for this block. The approved isolated-leaf policy was used: established RTL/test/Makefile sources were unchanged, so historical RTL regressions were not rebuilt.

Claim: `magnitude_clamp` implements the frozen L1 Sobel magnitude `abs(Gx)+abs(Gy)`, full unsigned 11-bit 0..2040 magnitude, and exact 8-bit saturation at 255 for valid ±1020 Sobel inputs.
Git commit: the commit adding this entry (`Add verified magnitude clamp stage`).
Command: `verilator --lint-only -Wall rtl/magnitude_clamp.sv --top-module magnitude_clamp`; temporary-build `make -f tb/tests/Makefile.magnitude_clamp`; `.venv/bin/python -m pytest -q tb/tests/test_reference_model.py`.
Evidence: `results/raw/magnitude-clamp-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; 7 focused cocotb tests passed; 8220 checked gradient pairs derived from test construction, including complete Gx/Gy axis sweeps and 4096 deterministic random pairs. The initial lint defect was corrected without suppression. This is focused arithmetic evidence only: no window/control integration, threshold, complete-frame RTL, formal, synthesis, P&R, or timing evidence. The isolated-leaf policy was used; established RTL/test files were unchanged.
Classification: `RTL SIMULATION VERIFIED`
