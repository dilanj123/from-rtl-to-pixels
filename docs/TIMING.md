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

The reported critical path is `s_tdata[15]$tr_io` output to
`m_tdata_TRELLIS_FF_Q_2` data input, with total delay 32.068 ns, logic delay
12.306 ns and routing delay 19.762 ns. Source references include
`rgb_to_gray.sv`, `magnitude_clamp.sv` and `threshold_stage.sv`; the measured
path is classified descriptively as a routing-dominated mixed arithmetic path.

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
