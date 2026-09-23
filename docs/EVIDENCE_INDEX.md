# Evidence index

This is the map from project claims to the logs, reports and images that
support them. Historical milestone records remain in Git history and in the
raw logs; this file keeps the current evidence easy to scan.

## Functional verification

| Claim | Classification | Evidence | Conditions / limits |
|---|---|---|---|
| Independent Sobel reference model passes | REFERENCE-MODEL VERIFIED | `results/raw/reference-model-pytest.log` | 13 pytest tests |
| Primitive RTL passes: grayscale, elastic stage, APB, pixel control, line buffer, window, output control, Sobel, magnitude/clamp and threshold | RTL SIMULATION VERIFIED | `results/raw/*-cocotb.log`, `results/raw/arithmetic-checkpoint-regression.log` | Focused recorded dimensions and seeds |
| Architecture-A alignment and complete-frame behavior | RTL SIMULATION VERIFIED | `results/raw/architecture-a-alignment-cocotb.log`, `results/raw/gate2-top-cocotb.log` | 3x3, 5x4 and 8x5 |
| Streaming gaps, backpressure, stalled metadata and drain stability | RTL SIMULATION VERIFIED | `results/raw/gate3-streaming-monitor-coverage.log`, `results/raw/gate3-streaming-stress-cocotb.log` | Strengthened monitor is authoritative; earlier stress log is historical |
| Reset and malformed metadata recovery | RTL SIMULATION VERIFIED | `results/raw/gate3-reset-metadata-cocotb.log` | 11 tests at 3x3, 5x4 and 8x5 |
| Configuration timing and same-edge APB/SOF priority | RTL SIMULATION VERIFIED | `results/raw/gate3-config-timing-cocotb.log` | 6 tests at 3x3, 5x4 and 8x5 |
| Broader dimensions and canonical public image | RTL SIMULATION VERIFIED | `results/raw/gate3-dimension-image-cocotb.log`, `results/processed/` | 18 random frames plus 640x480 image; zero mismatches |
| Architecture B integrated regression and A/B image equivalence | RTL SIMULATION VERIFIED | `results/raw/arch-b-functional-regression.log`, `results/raw/arch-ab-recovery-precondition-repair.log`, `results/processed/arch-b/` | One post-Gx/Gy 28-bit elastic stage; B synthesis evidence is separate |

Historical early Gate-2/Gate-3 entries in the raw logs preserve what was
unknown at those milestones. They are not current status statements.

## Formal verification

| Claim | Classification | Evidence | Conditions / limits |
|---|---|---|---|
| Elastic-stage properties | FORMAL PROPERTY PASSED UNDER DOCUMENTED ASSUMPTIONS | `results/raw/formal-elastic-stage.log` | DATA_WIDTH=11; selected properties only |
| APB/configuration properties | FORMAL PROPERTY PASSED UNDER DOCUMENTED ASSUMPTIONS | `results/raw/formal-apb-regs.log` | Local block proof with formal observation wiring |
| Pixel-control properties | FORMAL PROPERTY PASSED UNDER DOCUMENTED ASSUMPTIONS | `results/raw/formal-pixel-control.log` | 3x3 and 5x4 |
| Output-control safety and transition mechanics | FORMAL PROPERTY PASSED UNDER DOCUMENTED ASSUMPTIONS | `results/raw/formal-output-control.log` | 3x3 and 5x4; eventual drain remains derived under fairness |
| Final-token/frame-count integration | FORMAL PROPERTY PASSED UNDER DOCUMENTED ASSUMPTIONS | `results/raw/formal-frame-completion.log` | Narrow integration at 3x3 and 5x4 |

The selected formal set is targeted; no whole-accelerator formal proof is
claimed. Formal toolchain bootstrap evidence is preserved in
`results/raw/formal-toolchain-bootstrap.log`.

## Architecture A implementation

| Claim | Classification | Evidence |
|---|---|---|
| Canonical synthesis/resource map | SYNTHESISED | `results/raw/arch-a-synthesis.log`, `results/raw/arch-a-synthesis-stat.json` |
| Routed timing frontier | PLACED/ROUTED TIMING EVIDENCE | `results/raw/arch-a-frequency-search.csv`, `results/raw/arch-a-route-clean-report.json`, `results/raw/arch-a-route-fail-report.json` |
| Timing-domain-correct bottleneck review | DERIVED FROM ROUTED TIMING EVIDENCE | `results/raw/arch-a-bottleneck-review.log` |

A uses the virtual LFE5U-45F/CABGA381/speed-6 target, seed 1, and the
recorded 35/40 MHz clean/fail frontier. It has 665 LUT4, 194 FF and a
25.731 ns synchronous path. The preserved raw Phase-8 reports and logs are
historical evidence, not rewritten results.

## Architecture B / A-B comparison

The controlled comparison is recorded in `docs/ARCHITECTURE_COMPARISON.md`
and `results/raw/arch-ab-comparison.json`/`.log`.

- A: 35/40 MHz clean/fail, 25.731 ns synchronous path, 642-cycle first output.
- B: 60/65 MHz clean/fail, 16.194 ns synchronous path, 643-cycle first output.
- Both sustain II=1 and one pixel/clock; B is retained as the timing-oriented variant.
- Throughput values are derived from routed constraints and measured II.

## Debug case studies

Classification: DEBUG CASE STUDY VERIFIED. Deliberate defects were injected
and restored on isolated branches; none remains on `main`.

- `docs/DEBUG_CASE_STUDIES.md`
- `results/raw/debug-case-studies-summary.log`
- `results/raw/debug-001-*`, `debug-002-*`, `debug-003-*`

## Publication / reproducibility

| Claim | Classification | Evidence |
|---|---|---|
| Public command surface and CI | REPRODUCIBLE WORKFLOW | `Makefile`, `.github/workflows/ci.yml`, `results/raw/publication-validation.log` |
| Original architecture diagram and demo assets | PUBLICATION ASSETS VERIFIED | `docs/assets/architecture.svg`, `tb/images/Tokinokane2005-1-4.jpg`, `tb/images/gradient-grid-640x480.png`, `results/processed/`, `results/raw/public-gradient-image-regression.log`, `scripts/analysis/check_publication_assets.py` |
| Fresh-clone reproduction | CLEAN-CHECKOUT REPRODUCTION VERIFIED | `results/raw/clean-clone-validation.log` |
| Gate-5 audit | GATE5_RELEASE_AUDIT=PASS | `results/raw/gate5-release-audit.log` |

The clean clone validated commit `f9598f3a92a998a416c08ca36653ed8bf73bf5d8`
with the documented external OSS CAD Suite. GitHub Actions run
[35800586342](https://github.com/dilanj123/from-rtl-to-pixels/actions/runs/35800586342)
passed for that candidate; the final commit run is recorded in the release
history.

## Requirements traceability

| Requirement area | Evidence |
|---|---|
| RGB/grayscale/Sobel/magnitude/clamp/threshold arithmetic | Reference model, primitive logs and complete-frame logs |
| Exact transfers, SOF/EOL, stalls, borders and W+1 drain | Gate-2, strengthened streaming and output-control logs |
| Reset, malformed metadata and recovery | `results/raw/gate3-reset-metadata-cocotb.log` |
| APB access, W1C, frame count and configuration timing | `results/raw/apb-regs-cocotb.log`, `results/raw/gate3-config-timing-cocotb.log` |
| Formal assumptions and boundaries | `docs/FORMAL.md` |
| Frozen requirements and architecture | `docs/REQUIREMENTS.md`, `docs/MICROARCHITECTURE.md` |
