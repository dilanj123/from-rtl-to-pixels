# Routed timing results

## Current controlled A/B comparison

Both variants were tested at seed 1 for the virtual ECP5 LFE5U-45F,
CABGA381, speed-grade-6 target. The clean/failing values are tested timing
constraints. They bound the tested frontier; they are not a physical-device
Fmax measurement.

| Result | Architecture A | Architecture B |
|---|---:|---:|
| Highest tested timing-clean constraint | 35 MHz | 60 MHz |
| Lowest tested timing-failing constraint | 40 MHz | 65 MHz |
| Post-route synchronous critical path | 25.731 ns | 16.194 ns |
| Tool-reported post-route achieved clock | 38.8636 MHz | 61.7513 MHz |

For A, the critical synchronous path runs from `u_line_buffer.line1_mem.0.0`
port `DOB1` to `m_tdata_TRELLIS_FF_Q_2` port `DI`. Delay is 25.731 ns:
5.830 ns clock-to-Q, 8.033 ns ordinary logic and 11.868 ns routing. For B,
the path runs from a line-buffer EBR output to the new arithmetic elastic
register and is 16.194 ns. These are routed virtual-target reports, not board
measurements.

The single-seed controlled comparison supports the hypothesis that B's
ready/valid register after Sobel Gx/Gy shortens the measured synchronous path
and raises the tested clean/fail constraint bracket. B also costs additional
logic and registers; see [Architecture A/B comparison](ARCHITECTURE_COMPARISON.md)
for resource counts, latency and derived throughput.

## Historical Architecture-A search

The earlier A-only run tested 25, 35 and 50 MHz constraints. Routing completed
at all three points; timing passed at 25 and 35 MHz and failed at 50 MHz. It
reported a 38.8636 MHz post-route achieved clock. Those samples do not form a
5 MHz-resolution search: 35 to 50 MHz is a 15 MHz interval. A refinement
script later had a control-flow defect. The corrected A/B comparison above
uses the actual 5 MHz brackets of 35/40 MHz for A and 60/65 MHz for B.

The synchronous A bottleneck was mixed logic and routing. Routing contributes
11.868 ns (46.1%) of the 25.731 ns path. A separate approximately 32.068 ns
input-to-register path was reported as asynchronous/unconstrained I/O timing;
it is not the synchronous path used for the tested timing frontier.

At the 35 MHz clean constraint, A's one-pixel-per-clock initiation interval
corresponds to a **DERIVED** peak rate of 35 Mpixel/s. It is not a physical
throughput measurement.

## Evidence

- `results/raw/arch-a-implementation-toolchain.log`
- `results/raw/arch-a-synthesis.log`
- `results/raw/arch-a-synthesis-stat.json`
- `results/raw/arch-a-frequency-search.csv`
- `results/raw/arch-a-route-clean.log`
- `results/raw/arch-a-route-clean-report.json`
- `results/raw/arch-a-route-fail.log`
- `results/raw/arch-a-route-fail-report.json`
- `results/raw/arch-a-implementation-baseline.log`
- `results/raw/arch-ab-comparison.json` and `results/raw/arch-ab-comparison.log`

The older A-only sample and its script history remain preserved as historical
evidence; the corrected controlled comparison is the current A/B result.
