# Timing

## Architecture-A implementation baseline

Classification: `SYNTHESISED`; `PLACED/ROUTED TIMING-CLEAN AT 35 MHz, SEED 1`.

Architecture: A / compact
Top: `rtl_to_pixels_top`
Dimensions: `640x480`
Target: LFE5U-45F / CABGA381 / speed grade 6
Seed: 1

Tool versions: Yosys 0.69+75; nextpnr-ecp5 0.11.1-30-g3e53a0bf; Project Trellis ecppack 1.4-82-g3afe7b5.

Synthesis used the complete production RTL source set and the default
`synth_ecp5` mapping without retiming or resource-suppression options. Yosys
checks passed. Mapped cells were LUT4=665, TRELLIS_FF=194, CCU2C=113,
DP16KD=2, MULT18X18D=3, PFUMX=102 and L6MUX21=48. No distributed/LUT RAM
cells were mapped; the line-buffer storage mapped to DP16KD in this run.

nextpnr used `--45k --package CABGA381 --speed 6 --seed 1
--timing-allow-fail --detailed-timing-report --lpf-allow-unconstrained`.
The tested single-seed constraint frontier is:

| Target constraint | Route | Achieved clock | Timing |
|---:|---|---:|---|
| 25 MHz | PASS | 38.8636 MHz | PASS |
| 35 MHz | PASS | 38.8636 MHz | PASS |
| 50 MHz | PASS | 38.8636 MHz | FAIL |

Highest tested timing-clean target: **35 MHz**. Lowest tested timing-failing
target: **50 MHz**. Search resolution: **5 MHz**. This is routed timing
evidence for seed 1, not a statistically robust FPGA Fmax.

The synchronous critical path is `u_line_buffer.line1_mem.0.0` port `DOB1`
(clock-to-clock) to `m_tdata_TRELLIS_FF_Q_2` port `DI`, with total delay
25.731 ns: clk-to-q 5.830 ns, ordinary logic 8.033 ns and routing 11.868 ns.
This is a mixed line-buffer/output arithmetic cone through the Sobel,
magnitude/clamp and threshold path. Routing contributes 46.1% and the
registered-source plus ordinary logic contribution 53.9%, so the measured
synchronous bottleneck is mixed logic/routing rather than purely
routing-dominated.

### Unconstrained I/O timing

The approximately 32.068 ns path from `s_tdata[15]$tr_io` to the same output
data endpoint is an `<async>` to clock path. It includes source-side logic
and is preserved as separate unconstrained I/O timing evidence; it is not the
synchronous Fmax path.

The logs contain two frequency lines: the earlier placement-stage estimate
is 36.47 MHz and the later post-route result is 38.86 MHz. The latter is the
routed achieved result used above.

The design specifies up to one accepted pixel per clock. At the 35 MHz clean
routed target, the corresponding **DERIVED** peak rate is 35 Mpixel/s. This is
not a physical throughput measurement. No physical board was used.

Evidence:
- `results/raw/arch-a-implementation-toolchain.log`
- `results/raw/arch-a-synthesis.log`
- `results/raw/arch-a-synthesis-stat.json`
- `results/raw/arch-a-frequency-search.csv`
- `results/raw/arch-a-route-clean.log`
- `results/raw/arch-a-route-clean-report.json`
- `results/raw/arch-a-route-fail.log`
- `results/raw/arch-a-route-fail-report.json`
- `results/raw/arch-a-implementation-baseline.log`

## Phase-11 controlled A/B comparison

The Phase-8 25/35/50 MHz measurements remain valid; the original refinement script had a control-flow defect, so its claimed 5 MHz resolution was superseded. The corrected seed-1 search gives Architecture A 35 MHz clean / 40 MHz failing and Architecture B 60 MHz clean / 65 MHz failing, each with a 5 MHz bracket. A post-route synchronous path is 25.731 ns for A and 16.194 ns for B; the B path is line-buffer EBR output to the new arithmetic elastic register. Canonical no-stall simulation measured first-output latency 642 cycles for A and 643 for B, frame completion 307842 and 307843 cycles, and II=1 for input and output in both.

B resources are LUT4=775, TRELLIS_FF=223, CCU2C=110, DP16KD=2, MULT18X18D=3, PFUMX=171, L6MUX21=88 versus A LUT4=665, FF=194, CCU2C=113, DP16KD=2, MULT18X18D=3, PFUMX=102, L6MUX21=48. This is routed timing evidence for one seed, not a physical measurement.
