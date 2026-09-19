# Verification Plan

## Principle

Correctness requires automated evidence. A plausible image is not a pass criterion.

The independent Python model defines pixel mathematics, not RTL cycle structure.

## Reference model

Verify exact:
- RGB→gray integer arithmetic;
- zero borders;
- Gx/Gy;
- L1 magnitude;
- saturation;
- threshold;
- bypass.

Produce expected array/image, mismatch count/coordinates, and diff image.

## Simulation

Primary planned tools: Verilator, cocotb, pytest, NumPy, Pillow.

### Arithmetic
Test black/white/R/G/B, rounding boundaries, signed extrema, flat windows, vertical/horizontal edges and polarities, maximum gradient, clamp, threshold below/equal/above, bypass.

### Geometry
Run small dimensions including `3x3`, `4x4`, `5x5`, and non-square.

Verify:
- borders;
- EOL transitions;
- `W+1` mapping;
- first creatable output;
- exact output count;
- final `W+1` drain.

### Streaming
Test:
- continuous flow;
- source gaps;
- random gaps;
- one-cycle/long/random output stalls;
- SOF/EOL stalls;
- drain stalls;
- combined gaps/backpressure.

Assert stalled output stability.

### Reset
Test idle, before frame, first pixel, mid-line, EOL, late frame, drain, and successful new frame after reset.

### Configuration/APB
Test:
- reset defaults;
- valid/invalid/misaligned accesses;
- STATUS W1C;
- writes idle/mid-frame;
- threshold/bypass changes;
- same-edge APB-write/SOF priority;
- `CONFIG_PENDING`;
- `RUN_ENABLE`;
- frame completion/count.

### Malformed metadata
Inject incorrect SOF/EOL positions and verify:
- abort;
- sticky error;
- in-flight discard;
- no completed-frame count;
- restart only on valid SOF.

## Scoreboard

For each completed frame record:
- accepted input count;
- accepted output count;
- expected count;
- mismatch count;
- first mismatch coordinates/values;
- SOF position;
- EOL positions.

## Formal scope

Target only tractable control/protocol properties:
- elastic-stage stalled stability/no overwrite/token conservation under assumptions;
- APB legal/error accesses and shadow/active semantics;
- same-edge config priority;
- controller legal states/counter bounds;
- no new frame during DRAIN;
- drain completion under fairness assumptions;
- frame-count increment condition;
- selected metadata/valid invariants.

Every proof record shall include property, assumptions, engine, depth/mode, result, vacuity/cover review, and limitations.

Do not claim whole-accelerator formal verification.

## Traceability

| Requirement | Main evidence |
|---|---|
| pixel arithmetic | reference tests + RTL simulation |
| exact counts/no loss | frame/stream regression |
| stalled stability | simulation + selected formal |
| borders/W+1/drain | labelled geometry tests |
| reset abort/restart | reset matrix |
| frame-consistent config | config tests + selected formal |
| malformed metadata | protocol-error tests |
| Architecture A/B equivalence | identical full regression |
| latency/II/frame throughput | measured simulation |
| resources/timing | synthesis/routed reports |

Every discovered functional defect gains a regression test before or with its fix.
