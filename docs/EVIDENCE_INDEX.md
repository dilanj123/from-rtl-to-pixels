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

Claim: Production Architecture A integrates RGB input, metadata/control, `pixel_control`, grayscale, line/window generation, compact Sobel, magnitude/clamp, threshold/bypass, W+1 output control, elastic data/metadata output, APB configuration and externally qualified frame completion.
Git commit: the commit adding this entry (`Integrate Architecture A and close Gate 2`).
Command: composed production-top lint; temporary-build `make -f tb/tests/Makefile.rtl_to_pixels_top` at 3x3, 5x4, and 8x5; `.venv/bin/python -m pytest -q tb/tests/test_reference_model.py`.
Evidence: `results/raw/gate2-top-cocotb.log`
Conditions: Verilator 5.052; cocotb 2.1.0; 4 production-top tests at 3x3, 5x4, and 8x5; complete deterministic RGB frames; independent `sobel_rgb` comparison; exact input/output counts; SOF/EOL checks; final-output stall/completion check; APB RUN_ENABLE/config/frame-count checks.
Classification: `RTL SIMULATION VERIFIED`
Gate 2 CLOSED for the tested MVP simulation configurations: complete RTL RGB frames were reconstructed automatically, input/output counts were exact, and completed outputs matched the independent Python reference bit-exactly with zero mismatches.
Limitations at the Gate-2 milestone (streaming coverage subsequently extended below): randomized source gaps in the production top; randomized downstream backpressure; reset matrix; malformed metadata recovery regression; mid-frame configuration-write regression; same-edge APB-write/SOF integration regression; broad dimension sweep/canonical 640x480; random RGB frames; real-image regression; requirements traceability closure. Gate-4 work: formal; synthesis; P&R; timing; Architecture B.

Claim: Historical production Architecture A streaming stress regression exercised source gaps and backpressure with bit-exact completed frames at 3x3, 5x4 and 8x5. Review found that valid persistence was not asserted and aggregate stall counts did not guarantee SOF/every-EOL coverage. Use the strengthened evidence below for those claims.
Git commit: the commit adding this entry (`Add production streaming stress regression`).
Command: `python3 -m py_compile tb/tests/test_rtl_to_pixels_top_streaming.py`; strict production-top lint; temporary-build `make -f tb/tests/Makefile.rtl_to_pixels_top_streaming` at 3x3, 5x4, and 8x5; `.venv/bin/python -m pytest -q tb/tests/test_reference_model.py`.
Evidence: `results/raw/gate3-streaming-stress-cocotb.log`
Classification: `RTL SIMULATION VERIFIED`
Conditions: Verilator 5.052; cocotb 2.1.0; 5 streaming-stress tests at each dimension; deterministic random RGB frames; independent `sobel_rgb` comparison. Actual frame comparisons reported mismatch_count=0 throughout, with exact W×H input/output counts and nonzero aggregate gap/stall counters.
Gate 3 remains open. At this milestone, reset, malformed metadata and configuration timing were still pending; those categories are covered by the later recovery and configuration-timing evidence below. Remaining work is broader legal dimensions, canonical 640x480, additional random frames, real-image regression and requirements traceability closure. Gate-4 work: formal; synthesis; P&R; timing; Architecture B.

Claim: Strengthened production streaming regression checks pending output valid/data/SOF/EOL through acceptance and guarantees targeted metadata/drain stalls at every intended output index.
Git baseline: `a73be9929b6f73329e86790e7726eef8dae4e62d`; exact test patch recorded in the evidence log.
Command: monitor negative checks; strict production-top lint; temporary-build `make -f tb/tests/Makefile.rtl_to_pixels_top_streaming` at 3x3, 5x4 and 8x5; `.venv/bin/python -m pytest -q -p no:cacheprovider tb/tests/test_reference_model.py`. Exact invocations, build paths and exit codes are in the log.
Evidence: `results/raw/gate3-streaming-monitor-coverage.log`
Classification: `RTL SIMULATION VERIFIED` for the listed simulations; monitor negative checks are Python-level checks, not RTL fault injection or formal proof.
Conditions: Verilator 5.052; cocotb 2.1.0; 5/5 tests passed at each dimension; all frame comparisons reported zero mismatches and exact W×H counts. Metadata mode asserts two stalled cycles at SOF and every EOL. Drain mode asserts three at the first final-drain position, four at the final output, and one at each other final-drain position. Per-index expected/observed counts are logged. Valid-drop and data/SOF/EOL-change samples were rejected by the monitor; idle cycles did not consume the ready generator's stall budget. Strict lint and 13 reference tests passed. Production RTL is unchanged from the baseline.
Limitations: bounded deterministic seeds/small dimensions; no reset/abort/config-timing coverage added. Gate 3 remains OPEN; formal and implementation remain Gate-4 work.

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

Claim: Production Architecture A reset/malformed-metadata recovery regression exercises synchronous reset from idle, pre-frame, first-pixel, mid-line, EOL, late-frame and DRAIN states, plus accepted early/missing EOL and unexpected SOF metadata errors. Under the tested 3x3, 5x4 and 8x5 configurations, reset restored the frozen defaults and clean-frame recovery remained bit-exact. Malformed accepted metadata aborted incomplete frames, set sticky FRAME_ERROR, prevented aborted-frame completion counting, required a new valid SOF, and allowed a subsequent bit-exact complete frame.
Git baseline: `e5288ddcdc45ffe4e3f28a9645ca40630ad55ea0`; commit adding this entry (`Add production reset and metadata recovery regression`).
Command: `python3 -m py_compile tb/tests/test_rtl_to_pixels_top_recovery.py`; strict production-top `verilator --lint-only -Wall` at 5x4; fresh temporary-build `make -f tb/tests/Makefile.rtl_to_pixels_top_recovery` in order at 3x3, 5x4 and 8x5; `.venv/bin/python -m pytest -q tb/tests/test_reference_model.py`. Exact invocations, simulator output and exit codes are in the log.
Evidence: results/raw/gate3-reset-metadata-cocotb.log
Classification: `RTL SIMULATION VERIFIED`
Conditions: Verilator 5.052; cocotb 2.1.0; 11 focused recovery tests at 3x3, 11 at 5x4 and 11 at 8x5; independent `sobel_rgb` comparisons. All 33 recovery frames reported mismatch_count=0 and exact W*H input/output counts with checked SOF/EOL metadata. Syntax, warning-free strict lint, all dimension runs and 13 reference tests passed with exit 0.
Reset evidence: seven reset positions per dimension checked cleared output valid, APB reset defaults, disabled admission until RUN_ENABLE was restored, and successful clean-frame recovery. Line/window history recovery is checked through output comparisons; no physical RAM clearing is claimed.
Metadata evidence: four accepted malformed-token cases per dimension checked output flush, sticky FRAME_ERROR, zero aborted-frame count, rejection of non-SOF restart, a bit-exact recovered frame counted once, error persistence through recovery and STATUS[3] W1C. Unexpected-SOF cases recorded one prior output transfer at each dimension; missing-final-EOL cases recorded 4, 13 and 30 respectively. Those already transferred pixels belong to discarded incomplete frames and are not recalled.
Limitations: bounded small dimensions and deterministic seeds; production RTL and established tests/Makefiles unchanged. Gate 3 remains OPEN. The later configuration-timing regression covers mid-frame writes, same-edge APB-write/SOF integration, CONFIG_PENDING integration and RUN_ENABLE mid-frame behavior. Remaining work: broader legal dimensions; canonical 640x480; additional random frames; real-image regression; requirements traceability closure. Formal, synthesis, P&R, timing and Architecture B remain unverified.

Claim: Production Architecture A configuration-timing regression verifies shadow/active threshold and bypass semantics through the complete production datapath, including idle CONFIG_PENDING activation, mid-frame deferred writes, same-edge APB-write/SOF pre-edge priority, and RUN_ENABLE new-frame-only admission behavior. Under the tested 3x3, 5x4 and 8x5 configurations, current and following frames matched the independent Python reference under their expected active configuration.
Git baseline: `3eb109b229e751e53af3b838cda560a426a74550`; commit adding this entry: `Add production configuration timing regression`.
Command: `python3 -m py_compile tb/tests/test_rtl_to_pixels_top_config.py`; strict production-top `verilator --lint-only -Wall` at 5x4; fresh temporary-build `make -f tb/tests/Makefile.rtl_to_pixels_top_config` in order at 3x3, 5x4 and 8x5; `.venv/bin/python -m pytest -q tb/tests/test_reference_model.py`.
Evidence: `results/raw/gate3-config-timing-cocotb.log`
Classification: `RTL SIMULATION VERIFIED`
Conditions: Verilator 5.052; cocotb 2.1.0; 6 configuration-timing tests at 3x3, 5x4 and 8x5; independent `sobel_rgb` comparison. All emitted configuration-frame comparisons reported exact W×H accepted input/output counts and `mismatch_count=0`.
Evidence covers idle shadow writes and CONFIG_PENDING, SOF activation, mid-frame threshold and bypass deferral, same-edge APB-write/SOF pre-edge priority, and RUN_ENABLE clearing during an active frame with new-frame blocking and re-enable. Gate 3 remains OPEN. Remaining Gate-3 work: broader legal dimensions, canonical 640x480, additional random frames, real-image regression and requirements traceability closure. Formal, synthesis, P&R, timing and Architecture B remain unverified.

Claim: Production Architecture A broader-dimension and complete-image regression exercises deterministic random complete RGB frames at 4x4, 5x5, 3x7, 7x3, 16x9 and 31x17, plus the canonical 640x480 public-domain photograph. Complete RTL frames were reconstructed and compared automatically with the independent Python Sobel model.
Git baseline: `9a1dc4d4148af59226cac9e0344b2a751a71ef2d`; commit adding this entry: `Close Gate 3 with dimension and image regression`.
Evidence: `results/raw/gate3-dimension-image-cocotb.log`
Classification: `RTL SIMULATION VERIFIED`
Conditions: Verilator 5.052; cocotb 2.1.0; 18 additional deterministic random frames across six dimensions; one canonical 640x480 public-domain image; exact input/output counts; all recorded mismatch_count=0; independent `sobel_rgb` comparison.
Public image provenance is recorded in `THIRD_PARTY_NOTICES.md` and `docs/THIRD_PARTY_MANIFEST.md`. Generated artifacts are `results/processed/gate3-real-reference.png`, `results/processed/gate3-real-rtl.png`, and `results/processed/gate3-real-diff.png`; all are 640x480 and the diff has zero nonzero pixels.

## Gate 3 requirements traceability

| Requirement area | Evidence | Classification / status |
|---|---|---|
| RGB/grayscale/Sobel/magnitude/clamp/threshold arithmetic | reference-model-pytest, rgb-to-gray, sobel-compact, magnitude-clamp, threshold-stage, Gate-2 complete-frame evidence | RTL simulation/reference verified for recorded tests |
| exact accepted input/output counts | Gate-2, streaming stress/strengthened streaming, reset recovery, config timing, dimension/image regression | RTL simulation verified |
| SOF/EOL output metadata | Gate-2, streaming monitor coverage, reset recovery, dimension/image regression | RTL simulation verified |
| stalled output stability | strengthened streaming monitor coverage | RTL simulation verified for tested conditions |
| source gaps/backpressure | strengthened streaming regression | RTL simulation verified |
| borders/W+1 alignment/drain | output-control, Architecture-A alignment, Gate-2, streaming regression | RTL simulation verified |
| reset abort/restart | gate3-reset-metadata | RTL simulation verified |
| malformed metadata abort/restart | gate3-reset-metadata | RTL simulation verified |
| APB reset/default/access/W1C/frame-count rollover behavior | apb-regs focused regression | RTL simulation verified at block level |
| shadow/active configuration timing | gate3-config-timing | production-top RTL simulation verified |
| same-edge APB-write/SOF priority | gate3-config-timing | production-top RTL simulation verified |
| RUN_ENABLE admission behavior | Gate-2 plus gate3-config-timing | production-top RTL simulation verified |
| legal dimensions / 4x4 / 5x5 / non-square | gate3-dimension-image | RTL simulation verified |
| deterministic random complete frames | strengthened streaming plus gate3-dimension-image | RTL simulation verified |
| canonical 640x480 | gate3-dimension-image | RTL simulation verified; 307200 input/output transfers, mismatch_count=0 |
| real/public image | gate3-dimension-image plus provenance records | RTL simulation verified; public-domain source and SHA-256 recorded |
| selected formal properties | none yet | deferred to Gate 4 |
| synthesis/resources | none yet | deferred to Gate 4 |
| place/route/timing | none yet | deferred to Gate 4 |
| Architecture A/B comparison | none yet | deferred to Gate 4 |

Known-defect regression audit: final external-token completion has dedicated Gate-2 coverage; the strengthened streaming monitor covers the earlier valid-persistence and targeted-stall monitoring gap; malformed metadata recovery has dedicated reset/abort/restart regression; shadow/active and same-edge APB-write/SOF behavior has dedicated configuration-timing regression. The repository records no unresolved known functional defect without regression evidence. Formal, synthesis, P&R, timing and Architecture B remain unverified.

Claim: Phase-7 formal environment bootstrap established a runnable Yosys/SymbiYosys/Z3 flow on the recorded Apple-Silicon environment. A generic prove/cover smoke harness passed and demonstrates toolchain execution only. No production RTL property was formally checked by this milestone.
Evidence: `results/raw/formal-toolchain-bootstrap.log`
Classification: `FORMAL TOOLCHAIN SMOKE VERIFIED`
Conditions: pinned YosysHQ OSS CAD Suite 2026-09-20, verified archive SHA-256, Yosys 0.69+75, SBY v0.69, Z3 4.15.5; generic `formal_toolchain_smoke` prove depth 12 and cover depth 12 both passed, with the cover statement reached at step 6.
Limitation: this is environment evidence and must not be described as formal verification of the accelerator. No production RTL property has yet been checked.

Claim: The production-used `DATA_WIDTH=11` `elastic_stage` configuration has targeted formal evidence for stalled output stability, prevention of input acceptance/overwrite while an output token is stalled, and a one-entry accepted-minus-transferred ghost occupancy/data invariant. The prove job passed under the documented initialization assumption, and cover checks exercised occupied, stalled, stall-release, empty-accept and simultaneous pop/push states.
Evidence: `results/raw/formal-elastic-stage.log`
Classification: `FORMAL PROPERTY PASSED UNDER DOCUMENTED ASSUMPTIONS`
Conditions: Yosys 0.69+75; SymbiYosys v0.69; Z3 4.15.5; `smtbmc z3`; prove and cover depth 20; first sampled edge reset asserted; all later reset and source/destination stimulus arbitrary; no fairness or source-hold assumptions.
Limitations: `DATA_WIDTH=11` only, matching the production Architecture-A instance; not a universal parameter proof and not whole-accelerator formal verification. Synthesis, P&R and timing remain unverified.
