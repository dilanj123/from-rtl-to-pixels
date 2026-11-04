# Project state

## Current result

The selected RTL, verification, targeted formal checks and Architecture A/B virtual
ECP5 implementation study are complete. Architecture A is the compact
baseline; Architecture B is the timing-oriented variant. The full evidence
and limitations are linked from the [evidence index](EVIDENCE_INDEX.md).

Current release tags are `v1.0-cv-ready` and the later dependency update
`v1.0.1-dependency-ready`. The tags are immutable release references; see
Git history and the release evidence for their exact contents.

## Verification and implementation

The reference model and recorded RTL regressions pass, including complete
frames, stream backpressure, reset/recovery, APB behavior and A/B image
equivalence. Selected local formal properties pass under the assumptions in
[`FORMAL.md`](FORMAL.md); this is not a whole-accelerator proof.

The controlled single-seed routed comparison reports a 35/40 MHz tested
clean/failing constraint bracket for A and 60/65 MHz for B. These are virtual
ECP5 timing results, not physical FPGA measurements or a statistically robust
Fmax characterization. B adds one ready/valid stage after Sobel Gx/Gy and
uses more logic and registers.

## Scope boundaries

- No physical FPGA demonstration or measured throughput.
- No whole-accelerator formal proof.
- No board-level timing or robust Fmax claim.
- Dimensions are compile-time parameters, with no frame overlap during final
  drain.
- This is not a full AXI4-Stream, framebuffer, DMA, CPU, display or CNN system.

Historical phase and release records remain in Git history and preserved raw
logs. Current technical evidence is indexed in
[`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md).
