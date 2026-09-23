# Project State

## Current status

**Gate 5 CLOSED — CV-ready MVP complete.**

- Architecture A is the compact baseline.
- Architecture B is the retained timing-oriented variant.
- No physical FPGA measurement is claimed.
- Release tag: `v1.0-cv-ready`.

## Final architecture

Both variants implement the same RGB888 streaming Sobel pipeline: grayscale,
two line buffers, a 3×3 window, Sobel Gx/Gy, magnitude/clamp, threshold and
an 11-bit output elastic stage. Architecture B adds one 28-bit ready/valid
stage after Gx/Gy and carries arithmetic plus SOF, EOL, border and final-tag
metadata together.

## Verification status

The reference model and RTL simulation suites passed. Coverage includes
primitive arithmetic and protocol tests, complete frames, source gaps,
destination backpressure, SOF/EOL and drain stalls, reset and malformed
metadata, APB configuration timing, multiple dimensions, 18 deterministic
random frames, the 640×480 public image and direct A/B image equivalence.

Evidence: `results/raw/arch-b-functional-regression.log`,
`results/raw/arch-ab-recovery-precondition-repair.log` and the focused logs in
`results/raw/`.

## Formal status

Selected targeted formal verification is complete for the elastic stage,
APB/configuration, pixel controller, output control and final-token/frame-count
integration properties under their recorded assumptions. Output-control
liveness remains a derived result under downstream fairness. No
whole-accelerator formal proof is claimed.

Evidence: `docs/FORMAL.md` and `results/raw/formal-*.log`.

## Implementation results

| Metric | Architecture A | Architecture B |
|---|---:|---:|
| LUT4 | 665 | 775 |
| TRELLIS_FF | 194 | 223 |
| Clean/fail constraint | 35/40 MHz | 60/65 MHz |
| Synchronous path | 25.731 ns | 16.194 ns |
| First output | 642 cycles | 643 cycles |
| Frame completion | 307842 cycles | 307843 cycles |
| II / pixels per clock | 1 / 1 | 1 / 1 |

The comparison used the virtual LFE5U-45F/CABGA381/speed-6 target, identical
synthesis and routing settings, and seed 1. Throughput figures are derived
from clean routed constraints and measured II. Architecture B is retained as
the timing-oriented variant; Architecture A remains the compact baseline.

Evidence: `docs/ARCHITECTURE_COMPARISON.md` and
`results/raw/arch-ab-comparison.json`.

## Release status

The public repository includes the README, architecture diagram, pinned
Python development dependencies, command runners, GitHub Actions CI and
clean-clone validation. Candidate CI and clean-clone evidence are recorded in
`results/raw/publication-validation.log` and
`results/raw/clean-clone-validation.log`.

## Known limitations

There is no physical FPGA demonstration or physical throughput measurement.
Routed timing is single-seed virtual-device evidence, not a statistically
robust Fmax characterization. Dimensions are compile-time; the design uses a
single clock, does not overlap frames during final drain, and is not a full
AXI4-Stream, framebuffer, DMA, CPU, display or CNN system.

See [Known limitations](KNOWN_LIMITATIONS.md).

## Historical milestone references

Gate and phase history remains in Git history and the preserved raw evidence.
Use [the evidence index](EVIDENCE_INDEX.md) for the traceable record,
[decisions](DECISIONS.md) for architectural rationale and
[formal records](FORMAL.md) for assumptions and proof boundaries.
