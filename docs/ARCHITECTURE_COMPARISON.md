# Architecture A/B Comparison

## Controlled variables
640x480, LFE5U-45F CABGA381 speed-6, seed 1, identical Yosys/nextpnr options and 5 MHz search grid.

## Architecture A
Compact production top, no post-Gx/Gy arithmetic elastic boundary.

## Architecture B
One DATA_WIDTH=28 ready/valid elastic boundary after Sobel Gx/Gy; all other RTL shared.

## Functional equivalence
Canonical no-stall simulation produced 307200 accepted inputs and outputs for both, FRAME_COUNT=1, zero metadata errors, and direct completed-image mismatch 0.

## Resources and routed timing

| Metric | Architecture A | Architecture B | Delta |
|---|---:|---:|---:|
| LUT4 | 665 | 775 | +110 |
| TRELLIS_FF | 194 | 223 | +29 |
| CCU2C | 113 | 110 | -3 |
| DP16KD | 2 | 2 | 0 |
| MULT18X18D | 3 | 3 | 0 |
| PFUMX | 102 | 171 | +69 |
| L6MUX21 | 48 | 88 | +40 |
| Highest clean MHz | 35 | 60 | +25 |
| Lowest fail MHz | 40 | 65 | +25 |
| Sync path delay ns | 25.731 | 16.194 | -9.537 |
| First output latency cycles | 642 | 643 | +1 |
| Frame completion cycles | 307842 | 307843 | +1 |
| Input II | 1 | 1 | 0 |
| Output II | 1 | 1 | 0 |
| Pixels/clock | 1 | 1 | 0 |
| Derived peak Mpixel/s | 35 | 60 | +25 |

## Critical paths
A: line-buffer EBR DOB1 to final output elastic FF DI, 25.731 ns. B: line-buffer EBR DOB3 to arithmetic elastic FF M, 16.194 ns. The original A cone is split by the new boundary.

## Latency, initiation interval, and derived throughput
A first output is 642 cycles; B is 643. Both sustain II=1. Derived complete-frame rates at clean targets are 113.695 and 194.905 frames/s respectively; effective complete-frame pixel rates are 34.927 and 59.875 Mpixel/s. These are derived, not physical measurements.

## Hypothesis evaluation
The timing hypothesis is SUPPORTED in this single-seed controlled experiment: the frontier moves upward by five or more MHz and the synchronous path shortens. The latency and II hypotheses are also supported.

## Trade-off and engineering decision
RETAIN. B costs 110 LUT4 and 29 FF while adding one cycle, and materially improves routed timing. A remains the compact baseline.

## Limitations
One seed and one canonical dimension; no board measurement; no statistically robust Fmax; no whole-accelerator formal claim.
