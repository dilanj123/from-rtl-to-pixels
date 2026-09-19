# From RTL to Pixels — Master Project Plan and Replication Playbook

**Version:** 1.0
**Project repository:** `from-rtl-to-pixels`
**Project type:** Public RTL/SoC/FPGA engineering portfolio project
**Primary development host:** Apple Silicon Mac
**MVP hardware spend:** £0 preferred
**Status:** Authoritative plan to upload into a new ChatGPT Project before implementation

---

# 0. Purpose of this document

This document is the master project contract and execution plan for **From RTL to Pixels**.

It is deliberately more detailed than a normal project proposal because it must be usable in two ways:

1. by a person, to understand exactly what is being built, why, how it will be tested, what evidence must exist, and what counts as complete; and
2. by a fresh ChatGPT Project, so that ChatGPT can lead the work consistently without having to reconstruct the original planning conversation.

The project follows the engineering method proven in the earlier CPU summer project:

> **Define a measurable problem → build the simplest complete baseline → verify it → implement it → measure it → identify the limiting mechanism → make one controlled architectural change → re-verify → re-measure → retain/modify/reject → compare → conclude.**

The final edge-detected image is a demonstration.
The **engineering process and evidence** are the project.

---

# 1. Authority and document hierarchy

The following hierarchy must be used if project files ever disagree.

1. This master project plan (`00_MASTER_PROJECT_PLAN.md`).
2. `01_CHATGPT_PROJECT_OPERATING_INSTRUCTIONS.md`.
3. Gate-1 docs: `docs/REQUIREMENTS.md`, `docs/MICROARCHITECTURE.md`, `docs/VERIFICATION_PLAN.md`, `docs/DECISIONS.md`, `docs/PROJECT_STATE.md`, and `AGENTS.md`.
4. Implementation (RTL/test/build files).

Authority: **00 → 01 → Gate-1 docs → implementation**. Earlier planning/handoff notes are background only.

A contradiction must never be resolved silently.

When a contradiction is found:

1. identify it;
2. decide which behaviour is intended;
3. update the authoritative specification;
4. record the decision in `docs/DECISIONS.md`;
5. update tests before or with the RTL change.

---

# 2. Executive project definition

## 2.1 Title

**From RTL to Pixels**

## 2.2 Main objective

Build a production-style, synthesizable SystemVerilog image-processing accelerator that accepts a raster-ordered RGB image as a ready/valid pixel stream, processes every pixel through a fixed-point Sobel edge-detection datapath, handles backpressure and runtime configuration correctly, and reconstructs the RTL output into a real image that can be compared automatically with an independent Python reference implementation.

The design will then be used for a controlled microarchitecture experiment comparing:

- **Architecture A:** compact/lower-register Sobel arithmetic;
- **Architecture B:** more deeply pipelined/timing-oriented Sobel arithmetic.

The two versions must remain functionally equivalent.

## 2.3 Main engineering question

> **How do alternative pipeline boundaries in a streaming Sobel image-processing accelerator affect correctness, deterministic latency, sustainable throughput, critical path, routed clock frequency, resource use, and control/verification complexity when functionality and implementation conditions are held constant?**

## 2.4 Why Sobel

Sobel is deliberately narrow enough to finish, but rich enough to exercise:

- fixed-point arithmetic;
- signed arithmetic;
- line buffers;
- 3×3 neighbourhood generation;
- state/coordinate tracking;
- streaming protocols;
- backpressure;
- pipelining;
- metadata alignment;
- reset;
- runtime configuration;
- formal properties;
- synthesis;
- place-and-route;
- timing/PPA trade-offs;
- real visual outputs.

**Sobel is the workload; RTL engineering is the project.**

---

# 3. Scope

## 3.1 MVP includes

The MVP shall contain:

- one clock domain;
- synchronous active-high reset;
- RGB888 raster input stream;
- 8-bit grayscale edge output stream;
- AXI4-Stream-inspired ready/valid handshake;
- SOF and EOL metadata;
- compile-time image width and height;
- fixed-point RGB-to-grayscale;
- two line buffers;
- 3×3 window generator;
- Sobel Gx/Gy;
- L1 magnitude;
- 8-bit saturation;
- programmable threshold;
- threshold bypass;
- small same-clock APB3-style register interface;
- frame-consistent configuration;
- complete-frame Python reference comparison;
- random source gaps;
- random output backpressure;
- reset tests;
- configuration tests;
- requirements-to-test traceability;
- selected formal verification;
- synthesis and routed timing;
- Architecture A/B controlled comparison;
- CI;
- reproducible public GitHub presentation.

## 3.2 Explicitly out of scope before Gate 5

Do not add these to the MVP:

- independent clock domains;
- asynchronous FIFO;
- CDC/RDC complexity;
- external DDR/SDRAM framebuffer;
- AXI4 memory-mapped DMA;
- complete AXI4-Stream compliance claim;
- CPU/software subsystem;
- Linux;
- general programmable convolution;
- CNN/DNN acceleration;
- multiple image-processing algorithms;
- dynamic run-time image dimensions;
- simultaneous/overlapped frames during final drain;
- mandatory HDMI/VGA output;
- mandatory physical FPGA board;
- paid/proprietary EDA requirement.

These are extension ideas, not MVP requirements.

## 3.3 Follow-on project

After the single-clock project reaches Gate 5:

**From RTL to Pixels: Multi-Clock CDC and Reset Extension**

Possible topics:

- async FIFO;
- single-bit synchronisers;
- pulse crossing;
- multi-bit coherency;
- Gray-code pointers;
- independent resets;
- reset release;
- one-sided reset;
- recovery/flush policy;
- intentionally unsafe CDC/RDC variants;
- formal/static reasoning.

Do not contaminate the first project with these before it is stable.

---

# 4. Project F reuse, licensing, and authorship policy

## 4.1 Reuse principle

Project F may be used as:

- a technical reference;
- a source of selected MIT-licensed platform/support infrastructure;
- a future display/board integration reference.

Project F must **not** become a hidden implementation of the core accelerator.

## 4.2 Final repository rule

Do not copy the entire `projf-explore` repository into the final project and then modify it broadly.

A separate local clone may be kept for reference.

The final repository should contain:

- original project code;
- only the specific third-party files that are actually needed.

## 4.3 Core project code that should be original

Write these specifically for this project:

- pixel stream ingress/control;
- ready/valid/backpressure logic;
- RGB-to-grayscale;
- line-buffer controller;
- 3×3 window generator;
- compact Sobel arithmetic;
- pipelined Sobel arithmetic;
- magnitude/clamp;
- threshold;
- elastic stage;
- APB registers;
- shadow/active configuration;
- reference model;
- cocotb driver/monitor/tests;
- formal properties;
- PPA/timing scripts;
- analysis scripts;
- documentation and diagrams.

## 4.4 Project F code that may reasonably be reused later

Potentially useful third-party items:

- board constraints;
- board/device clock-generation helper;
- DVI/VGA output support for an optional hardware extension;
- generic board/platform helpers;
- a genuinely generic memory helper where reuse is technically justified.

## 4.5 Third-party manifest

For every copied or derived third-party file record:

- upstream project;
- repository URL;
- upstream file path;
- upstream commit/tag;
- original copyright;
- licence;
- whether unmodified or derived;
- local file path;
- project modifications.

Create:

- `THIRD_PARTY_NOTICES.md`
- `docs/THIRD_PARTY_MANIFEST.md`

Retain copyright/licence notices in copied or substantially derived files.

Renaming signals, formatting, moving a file, or modifying it does not erase the original licence/attribution requirement.

## 4.6 Blog/media rule

Repository source code and blog/media content are not assumed to have identical reuse terms.

Do not copy Project F blog prose, diagrams, screenshots, or photographs into the project unless their specific licence allows it.

Prefer:

- original diagrams;
- original screenshots;
- original waveforms;
- original project explanations;
- links to references.

## 4.7 Project licence

Original project work may be released under MIT.

A top-level MIT licence does not remove third-party copyright from reused MIT material.

---

# 5. Frozen functional interface

## 5.1 Clock and reset

```systemverilog
input logic clk;
input logic rst;
```

`rst` shall be:

- synchronous;
- active-high;
- common to the entire MVP accelerator.

## 5.2 Input stream

AXI4-Stream-inspired subset:

```systemverilog
input  logic [23:0] s_tdata;
input  logic        s_tvalid;
output logic        s_tready;
input  logic        s_tuser;   // SOF
input  logic        s_tlast;   // EOL
```

Frozen RGB packing:

```text
s_tdata[23:16] = R
s_tdata[15:8]  = G
s_tdata[7:0]   = B
```

The project must not claim full AXI4-Stream compliance unless a later audit demonstrates it. Documentation should say:

> **AXI4-Stream-inspired ready/valid pixel interface with documented subset semantics.**

## 5.3 Output stream

```systemverilog
output logic [7:0] m_tdata;
output logic       m_tvalid;
input  logic       m_tready;
output logic       m_tuser;    // output SOF
output logic       m_tlast;    // output EOL
```

## 5.4 Transfer rule

A transaction transfers only on:

```text
valid && ready
```

Real input pixel acceptance:

```text
accept_pixel = s_tvalid && s_tready
```

When:

```text
m_tvalid = 1
m_tready = 0
```

`m_tdata`, `m_tuser`, and `m_tlast` must remain stable.

---

# 6. Image dimensions and frame contract

## 6.1 Parameters

Canonical values:

```systemverilog
parameter int IMG_WIDTH  = 640;
parameter int IMG_HEIGHT = 480;
```

Unit/regression tests may override these at elaboration time.

Minimum supported dimensions:

```text
IMG_WIDTH  >= 3
IMG_HEIGHT >= 3
```

## 6.2 Raster order

Pixels are accepted:

- left-to-right;
- then top-to-bottom;
- one complete frame contains exactly `IMG_WIDTH * IMG_HEIGHT` accepted pixels.

## 6.3 Input metadata

Expected input metadata:

- `s_tuser=1` only with the first accepted pixel of a frame;
- `s_tlast=1` only with the final accepted pixel of each row.

Internal coordinate counters are authoritative.

Malformed metadata shall set a sticky protocol/frame error.

Recommended MVP recovery:

1. mark the current frame invalid/aborted;
2. discard remaining in-flight state;
3. wait for a new valid SOF.

This policy must be verified before implementation is considered complete.

---

# 7. Exact streaming alignment

## 7.1 Linear indexing

For input coordinate `(r,c)`:

```text
n = r * IMG_WIDTH + c
```

A centred 3×3 Sobel result for output coordinate `(r,c)` needs input coordinate `(r+1,c+1)` to be known.

Therefore, for normal stream alignment:

```text
output_index k = input_index n - (IMG_WIDTH + 1)
```

## 7.2 Initial fill

No corresponding output token is available until the required future row/column context exists.

Output index 0 becomes creatable when zero-based input index `IMG_WIDTH + 1` is accepted, i.e. on accepted pixel `IMG_WIDTH + 2`. Final drain remains `IMG_WIDTH + 1` logical output positions.

## 7.3 Steady state

After fill, without downstream backpressure:

- accept up to one real input pixel per clock;
- produce up to one output token per clock;
- border coordinates output zero;
- interior coordinates use a valid 3×3 window.

There is no need for a deliberate bubble at each EOL.

## 7.4 End-of-frame drain

After the last real input pixel:

- `IMG_WIDTH + 1` logical output positions remain;
- these positions are border outputs;
- enter a `DRAIN` state;
- stop admitting a new frame;
- generate remaining border/output tokens;
- drain downstream pipeline stages;
- return to `WAIT_SOF` only after the final output token is accepted.

No frame overlap in the MVP.

## 7.5 Output-count invariant

For every completed valid frame:

```text
accepted_input_pixels  == IMG_WIDTH * IMG_HEIGHT
accepted_output_pixels == IMG_WIDTH * IMG_HEIGHT
```

Backpressure must never cause loss or duplication.

---

# 8. Border policy

Frozen policy:

```text
top row    -> 0
bottom row -> 0
left col   -> 0
right col  -> 0
```

Do not silently use replicate, mirror, wrap, or undefined borders.

---

# 9. RGB-to-grayscale arithmetic

Use:

```text
Y = (77*R + 150*G + 29*B + 128) >> 8
```

Where:

- `R/G/B` are unsigned 8-bit;
- coefficients are integer constants;
- `+128` performs round-to-nearest before division by 256;
- output is unsigned 8-bit.

Maximum accumulator:

```text
77*255 + 150*255 + 29*255 + 128 = 65408
```

A 16-bit unsigned accumulator is sufficient.

No floating point in RTL.

---

# 10. Sobel arithmetic

For:

```text
p00 p01 p02
p10 p11 p12
p20 p21 p22
```

Use:

```text
Gx = -p00 + p02 - 2*p10 + 2*p12 - p20 + p22
Gy = -p00 - 2*p01 - p02 + p20 + 2*p21 + p22
```

Bounds:

```text
-1020 <= Gx <= +1020
-1020 <= Gy <= +1020
```

Use signed 12-bit intermediates.

Magnitude:

```text
M = abs(Gx) + abs(Gy)
```

Bound:

```text
0 <= M <= 2040
```

Use an 11-bit unsigned magnitude intermediate.

Clamp:

```text
if M > 255:
    M8 = 255
else:
    M8 = M
```

Threshold:

```text
if M8 < active_threshold:
    output = 0
else:
    output = M8
```

Threshold bypass:

```text
if active_bypass_threshold:
    output = M8
```

Border classification overrides the arithmetic result and outputs zero.

---

# 11. Configuration interface

## 11.1 Interface

Same-clock APB3-style, no-wait-state CSR slave:

```systemverilog
input  logic        psel;
input  logic        penable;
input  logic        pwrite;
input  logic [7:0]  paddr;
input  logic [31:0] pwdata;
output logic [31:0] prdata;
output logic        pready;
output logic        pslverr;
```

## 11.2 Minimum register map

| Address | Register | Required fields |
|---|---|---|
| `0x00` | CONTROL | `RUN_ENABLE`, `BYPASS_THRESHOLD_SHADOW` |
| `0x04` | THRESHOLD | `THRESHOLD_SHADOW[7:0]` |
| `0x08` | STATUS | `BUSY`, `DRAINING`, `CONFIG_PENDING`, `FRAME_ERROR` |
| `0x0C` | FRAME_COUNT | completed output frames |

Avoid decorative registers without a verification/use case.

## 11.3 Shadow/active configuration

Frame-consistent fields:

- threshold;
- threshold bypass.

Writes update shadow registers.

At **accepted SOF**, shadow configuration copies atomically to active configuration.

Same-edge priority:

> If an APB configuration write and an accepted SOF occur on the same rising edge, the new frame uses the shadow value that existed before the edge. The concurrent write applies to the following frame.

## 11.4 RUN_ENABLE

`RUN_ENABLE` controls admission of a new frame.

When idle:

- `RUN_ENABLE=0`: do not accept a new frame;
- `RUN_ENABLE=1`: a valid SOF may start a frame.

If software clears `RUN_ENABLE` during a frame:

- current frame completes;
- next frame is not admitted.

## 11.5 FRAME_COUNT

Increment when the last output pixel of a complete frame is actually transferred:

```text
m_tvalid && m_tready && last_output_pixel
```

---

# 12. Reset policy

On synchronous active-high reset:

- clear stream valid state;
- clear pipeline token-valid state;
- reset coordinate counters;
- reset controller state to `WAIT_SOF`;
- abandon any partial frame;
- deassert `m_tvalid`;
- restore documented configuration defaults;
- clear or preserve diagnostic counters according to explicit requirements.

Do **not** require resetting every line-buffer memory cell.

RAM contents are treated as invalid until sufficient new-frame data has overwritten/validated them.

Reset during a partial frame means:

- already consumed downstream pixels cannot be recalled;
- all remaining partial-frame state is discarded;
- downstream software/testbench must discard that incomplete frame;
- restart only on a new valid SOF.

---

# 13. Backpressure microarchitecture

## 13.1 Real image state

Only `accept_pixel` may:

- advance input row/column;
- write a real grayscale pixel into line-buffer state;
- advance accepted-pixel count;
- update real input window state.

## 13.2 Post-window arithmetic

Use elastic ready/valid stages where practical.

Already-created tokens may continue to move when:

```text
s_tvalid = 0
```

Source gaps must not force a global freeze if downstream work can legally drain.

## 13.3 Backpressure propagation

When downstream capacity is exhausted:

- ready propagates upstream;
- eventually `s_tready=0`;
- real input/window/line-buffer state stops.

## 13.4 Stability invariant

If:

```text
m_tvalid && !m_tready
```

then:

- `m_tdata` stable;
- `m_tuser` stable;
- `m_tlast` stable.

This needs random simulation stress and formal proof where tractable.

---

# 14. Output metadata

Generate output SOF/EOL from output token coordinate/index.

Required:

```text
m_tuser = 1 only for output (row=0,col=0)
m_tlast = 1 only for output col=IMG_WIDTH-1
```

Metadata is part of the same output transaction and must stall with the data.

Do not implement frame-sized delay lines only to delay marker bits.

---

# 15. Microarchitecture modules

Recommended original RTL files:

```text
rtl/
  pixel_pkg.sv
  stream_ingress.sv
  rgb_to_gray.sv
  line_buffer.sv
  window_3x3.sv
  sobel_compact.sv
  sobel_pipelined.sv
  magnitude_clamp.sv
  threshold_stage.sv
  elastic_stage.sv
  pixel_control.sv
  apb_regs.sv
  rtl_to_pixels_top.sv
```

Responsibilities must remain clear.

Do not prematurely collapse modules into one file.

---

# 16. Architecture A and Architecture B

## 16.1 Shared infrastructure

Both variants must share:

- input stream semantics;
- grayscale;
- line buffer/window generation;
- controller;
- border behaviour;
- APB/config;
- output protocol;
- dimensions;
- test/reference model;
- target device;
- synthesis/P&R flow.

## 16.2 Architecture A — compact

Hypotheses:

- fewer arithmetic pipeline registers;
- lower pipeline latency;
- fewer FFs;
- longer combinational path;
- lower routed Fmax.

These are hypotheses, not results.

## 16.3 Architecture B — timing-oriented

Architecture B is a mandatory controlled pipeline experiment. Select arithmetic pipeline boundaries after Architecture A functional and routed timing evidence exists. Describe B as bottleneck-driven optimisation only when Architecture A timing evidence supports that interpretation; otherwise describe it as a controlled pipeline experiment.

Possible boundaries:

1. Gx/Gy;
2. abs/magnitude;
3. clamp/threshold.

Exact boundaries are decided after Architecture A implementation evidence exists.

Hypotheses:

- more FFs;
- greater latency;
- more valid/ready/control state;
- shorter critical path;
- higher routed frequency.

## 16.4 Equivalence requirement

For identical accepted input frames and configuration:

> Architecture A and Architecture B must produce bit-identical complete output images.

---

# 17. Independent Python reference model

## 17.1 Purpose

The Python reference model defines intended pixel mathematics independently of RTL structure.

## 17.2 Required capabilities

- load/generate RGB images;
- exact integer grayscale;
- zero-border Sobel;
- L1 magnitude;
- clamp;
- threshold;
- threshold bypass;
- save expected image;
- compare arrays;
- produce diff image;
- report mismatch coordinates.

## 17.3 Independence

Do not implement the reference as a line-by-line cycle model of the RTL.

A separate optional cycle model may exist later, but the golden model should answer:

> What should each output pixel be?

---

# 18. Verification environment

## 18.1 Main tools

- Verilator;
- cocotb;
- pytest;
- NumPy;
- Pillow.

## 18.2 Verification components

Recommended structure:

```text
tb/
  reference/
  drivers/
  monitors/
  tests/
  images/
```

## 18.3 Required arithmetic tests

Include:

- black;
- white;
- R/G/B primaries;
- grayscale rounding boundaries;
- min/max/intermediate values;
- flat windows;
- vertical edge;
- horizontal edge;
- both edge polarities;
- maximum Sobel gradient;
- threshold exactly equal;
- below threshold;
- above threshold;
- saturation.

## 18.4 Required stream tests

Include:

- continuous input/ready;
- source gaps;
- random source gaps;
- one-cycle output stall;
- long output stall;
- random output backpressure;
- stall on SOF;
- stall on EOL;
- stall during drain;
- mixed source gaps and output backpressure.

## 18.5 Required geometry tests

Compile at several legal small dimensions:

- 3×3;
- 4×4;
- 5×5;
- 8×6 or similar;
- non-square dimensions.

Verify:

- first row;
- bottom row;
- left/right borders;
- EOL transitions;
- frame end;
- W+1 delayed mapping.

## 18.6 Reset tests

Include:

- idle reset;
- reset immediately before frame;
- reset after first accepted pixel;
- mid-line reset;
- EOL reset;
- late-frame reset;
- reset during drain;
- new valid frame after reset.

## 18.7 Configuration tests

Include:

- write while idle;
- write mid-frame;
- threshold change;
- bypass change;
- write immediately before SOF;
- APB write same edge as SOF;
- current-frame consistency;
- next-frame activation.

## 18.8 Complete-image tests

At least:

- deterministic synthetic patterns;
- random generated frames;
- one self-created or clearly licensed public image;
- canonical 640×480 representative run.

## 18.9 Scoreboard

For each completed frame report:

- accepted input count;
- accepted output count;
- expected output count;
- mismatch count;
- first N mismatch coordinates;
- expected/actual values;
- SOF location;
- EOL positions.

A plausible-looking picture is not a pass criterion.

## 18.10 Defect rule

Every functional bug discovered must gain a regression test before or with its fix.

---

# 19. Requirements-to-test traceability

`docs/VERIFICATION_PLAN.md` must contain a matrix like:

| Requirement | Simulation test | Formal property | Evidence |
|---|---|---|---|
| exact output count | frame-count tests | optional | regression log |
| no loss/duplication | backpressure tests | elastic/token properties | log/proof |
| stalled output stable | stall tests | yes | log/proof |
| zero borders | geometry tests | optional | output arrays |
| frame config | config tests | selected property | logs |
| reset abort | reset matrix | optional | logs |
| throughput target | performance test | n/a | measured sim |
| deterministic latency | latency test | n/a | measured sim |

Every material requirement must have an evidence path.

---

# 20. Formal verification

Do not try to prove the entire accelerator first.

Priority targets:

## 20.1 Elastic stage

Properties:

- stalled output stable;
- no illegal overwrite;
- valid/data relationship;
- token conservation under documented assumptions.

## 20.2 APB/config

Properties:

- legal register reads/writes;
- shadow/active separation;
- SOF activation;
- same-edge write/SOF priority.

## 20.3 Controller/counters

Properties:

- legal states;
- row/column bounds;
- drain reaches completion under fairness assumptions;
- no new frame while draining;
- frame count increments only at completed output frame.

## 20.4 Metadata/simple pipeline valid

Properties where tractable:

- SOF only at output index zero;
- EOL only at final column;
- valid propagation invariants.

## 20.5 Formal evidence record

Each proof must document:

- property;
- assumptions;
- engine;
- mode/depth;
- result;
- cover/vacuity considerations;
- known limitations.

Use only syntax supported by the actual installed open-source frontend.

Do not claim the entire accelerator is “formally verified” because a few local properties pass.

---

# 21. Open-source synthesis/timing target

## 21.1 Planned virtual target

Initial controlled target:

```text
Family:      Lattice ECP5
Device:      LFE5U-45F
Package:     CABGA381
Speed grade: 6
```

Bootstrap must confirm the installed Yosys/nextpnr flow supports the intended target.

If not, revise transparently.

## 21.2 Physical board not required

The MVP may use a virtual device target for:

- synthesis;
- placement;
- routing;
- resource counts;
- critical-path/timing comparison.

Never call this a board measurement.

## 21.3 Controlled A/B variables

Hold constant:

- device;
- package;
- speed grade;
- top wrapper;
- image parameters;
- tool versions;
- synthesis options;
- P&R options;
- timing constraints;
- seed policy;
- resource accounting boundary;
- measurement script.

## 21.4 Metrics

Record:

- cells/LUTs;
- FFs;
- EBR/BRAM;
- DSP/multiplier usage;
- target clock;
- worst slack;
- critical path;
- routed timing;
- latency;
- initiation interval;
- sustainable pixels/clock;
- derived pixel/s when justified.

## 21.5 Fmax procedure

Do not call one arbitrary run “Fmax”.

Use a repeatable search:

1. find a clearly timing-clean constraint;
2. raise frequency;
3. bracket pass/fail;
4. refine to the chosen frequency resolution;
5. preserve run records.

If seed variance matters, use a documented small seed set rather than silently choosing a favourable route.

---

# 22. Evidence classification

Use these categories:

1. **Specified**
2. **Reference-model verified**
3. **RTL simulation verified**
4. **Formal property passed under documented assumptions**
5. **Synthesised**
6. **Placed/routed timing-failing**
7. **Placed/routed timing-clean at stated constraint**
8. **Derived**
9. **Physically board-demonstrated**

Examples:

Correct:
> The routed ECP5 implementation met the stated clock constraint in this run.

Not correct without hardware:
> The FPGA was measured at that frequency.

Correct:
> Throughput is derived from timing-clean frequency and initiation interval.

Not correct:
> Throughput was physically measured, unless it was.

---

# 23. Repository structure

```text
from-rtl-to-pixels/
├── .github/
│   └── workflows/
├── rtl/
├── tb/
│   ├── reference/
│   ├── drivers/
│   ├── monitors/
│   ├── tests/
│   └── images/
├── formal/
├── constraints/
├── scripts/
│   ├── sim/
│   ├── formal/
│   ├── synth/
│   ├── timing/
│   └── analysis/
├── reports/
│   └── reference/
├── results/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── assets/
│   ├── debug/
│   ├── REQUIREMENTS.md
│   ├── MICROARCHITECTURE.md
│   ├── VERIFICATION_PLAN.md
│   ├── FORMAL.md
│   ├── TIMING.md
│   ├── TRADEOFFS.md
│   ├── DECISIONS.md
│   ├── KNOWN_LIMITATIONS.md
│   ├── PROJECT_STATE.md
│   ├── EVIDENCE_INDEX.md
│   └── THIRD_PARTY_MANIFEST.md
├── examples/
├── THIRD_PARTY_NOTICES.md
├── AGENTS.md
├── Makefile
├── pyproject.toml
├── .gitignore
├── LICENSE
└── README.md
```

---

# 24. What the user needs

## 24.1 Hardware

Required:

- Apple Silicon Mac.

Not required for MVP:

- FPGA development board;
- display;
- proprietary JTAG programmer.

Do not buy hardware before Gate 5 unless a specific blocker/benefit justifies it.

## 24.2 Accounts

Required:

- GitHub account;
- GitHub CLI authentication performed by the user.

No AI tool should request, store, or fabricate credentials.

## 24.3 Local software

Bootstrap shall detect:

- `git`;
- `gh`;
- `python3`;
- `make`;
- `verilator`;
- `yosys`;
- `sby`;
- formal solver(s);
- `nextpnr-ecp5`;
- ECP5 database/tool support.

Recommended EDA bundle:

- OSS CAD Suite Darwin ARM64, if current bootstrap compatibility is confirmed.

Python project environment should contain:

- cocotb;
- pytest;
- numpy;
- Pillow.

Pin versions after a known-good combination is established.

Avoid accidentally mixing the Python packaged inside OSS CAD Suite with the project Python venv unless intentionally documented.

## 24.4 Demo image

Use:

- an image created by the user; or
- a clearly licensed public image.

Record provenance.

Synthetic test images should be generated by code.

---

# 25. Standard command contract

Target user interface:

```text
make help
make doctor
make lint
make test-unit
make test
make test-real-image
make formal
make synth ARCH=compact
make synth ARCH=pipelined
make timing ARCH=compact
make timing ARCH=pipelined
make ppa
make all
make clean
```

`make doctor` must print:

- exact executable path;
- version;
- required/optional classification.

It must fail non-zero if a requested mandatory workflow cannot run.

---

# 26. Git/GitHub process

## 26.1 Main

`main` should remain known-good and reproducible.

## 26.2 Branches

Use narrow branches such as:

```text
feat/reference-model
feat/rgb-gray
feat/elastic-stage
feat/window-engine
feat/compact-sobel
feat/backpressure-tests
feat/formal-elastic
exp/pipeline-b
debug/metadata-misalignment
```

## 26.3 Commits

Commit meaningful, reviewable states.

Do not manufacture commit history later.

## 26.4 Suggested tags

Only apply when evidence exists:

- `v0.1-contract`
- `v0.2-mvp`
- `v0.3-verified`
- `v0.4-formal`
- `v0.5-implementation`
- `v1.0-cv-ready`

---

# 27. CI

CI should grow with the project.

Minimum early CI:

- lint/compile;
- fast unit tests.

Then:

- full regression.

Later:

- selected formal checks;
- synthesis smoke.

Long P&R/Fmax sweeps can remain manual or scheduled if runtime is excessive.

A clean CI pass is independent reproducibility evidence, not a substitute for timing/hardware evidence.

---

# 28. Run record template

Every meaningful implementation experiment records:

```text
Experiment ID:
Date:
Git commit:

Question:
Hypothesis:

Architecture:
Image dimensions:
Configuration:

Python:
Simulator:
Yosys:
nextpnr:
Target device/package/speed:
Top:
Synthesis options:
P&R options:
Seed:

Functional regression:
Formal status:

Latency:
Initiation interval:
Frame cycles:
Accepted inputs:
Accepted outputs:

Resources:
LUT/cells:
FF:
EBR:
DSP:

Timing:
Constraint:
Worst slack:
Critical path:
Classification:

Derived throughput:

Physical test:
not run / passed / failed

Decision:
retain / modify / reject / inconclusive

Reason:

Evidence files:
```

---

# 29. Decision log template

For major decisions:

```text
Decision ID:
Date:
Problem:
Available evidence:
Options:
Chosen approach:
Reason:
Expected trade-off:
Result:
Retained/rejected:
```

Important decisions to record include:

- L1 magnitude;
- zero borders;
- threshold-only bypass;
- fixed compile-time dimensions;
- W+1 stream alignment;
- drain/no frame overlap;
- reset method;
- APB same-edge priority;
- Architecture A/B boundary;
- ECP5 target;
- third-party reuse.

---

# 30. Risk register

| Risk | Consequence | Mitigation |
|---|---|---|
| Apple/tool incompatibility | blocks execution | Phase 0 smoke test before RTL |
| Backpressure corrupts window | incorrect frames | transfer-qualified state + stress + formal |
| Window off-by-one | wrong Sobel image | tiny labelled images and coordinate scoreboard |
| signed/width bug | wrong gradients | explicit widths + extrema tests |
| border/drain mismatch | count/alignment error | dedicated W+1/end-frame tests |
| config changes mid-frame | nondeterminism | shadow/active config |
| RAM reset breaks inference | poor implementation | reset validity, not memory contents |
| A/B changes too many variables | invalid comparison | shared front-end/build flow |
| Project F reuse ambiguity | portfolio/licence issue | selective reuse + manifest |
| formal vacuity | false confidence | document assumptions + cover |
| lucky P&R seed | misleading timing | documented seed methodology |
| scope creep | delayed completion | Gate 5 before extensions |
| unclear image licence | publication risk | self-created/licensed image |

---

# 31. Project gates

## Gate 0 — Environment known

Required evidence:

- OS/architecture;
- actual tool paths/versions;
- Git status;
- GitHub authentication state;
- working repository;
- `make doctor`.

No accelerator RTL yet.

## Gate 1 — Architecture frozen

Must have coherent:

- requirements;
- interfaces;
- arithmetic widths;
- border policy;
- stream alignment;
- drain behaviour;
- reset;
- APB/config;
- verification plan;
- formal scope;
- Architecture A/B experiment;
- third-party policy.

## Gate 2 — MVP

Must:

- process complete RTL image;
- reconstruct output;
- compare automatically to Python;
- demonstrate exact pixel count;
- have no known basic functional defect.

## Gate 3 — Verified

Must include:

- random source gaps;
- random backpressure;
- reset matrix;
- config tests;
- multiple dimensions;
- random frames;
- requirements traceability;
- regression for known bugs.

## Gate 4 — Engineering depth

Must include:

- targeted formal;
- synthesis;
- routed timing;
- Architecture A implementation baseline;
- evidence-driven Architecture B;
- controlled A/B comparison;
- documented trade-off.

## Gate 5 — Public/CV-ready

Must include:

- strong README;
- original block diagram;
- input/reference/RTL/diff imagery;
- exact commands;
- CI;
- evidence index;
- limitations;
- third-party notices;
- clean-checkout validation.

Physical FPGA is optional after Gate 5.

---

# 32. Detailed phase plan

## Phase 0 — Bootstrap

Work:

- inspect Mac and repository;
- create repo if needed;
- configure local Git identity;
- verify GitHub CLI auth;
- create skeleton;
- create `make doctor`;
- detect tools;
- make bootstrap commit;
- create/push public repo only if authenticated.

Do not:

- implement accelerator RTL;
- invent tool results;
- install large tools blindly.

Deliverable:

- exact bootstrap evidence.

## Phase 1 — Gate-1 documents

Create/freeze:

- `docs/REQUIREMENTS.md`
- `docs/MICROARCHITECTURE.md`
- `docs/VERIFICATION_PLAN.md`
- `docs/DECISIONS.md`
- `AGENTS.md`
- `docs/PROJECT_STATE.md`

Gate:

- no unresolved behavioural contradictions.

## Phase 2 — Python golden model

Implement exact arithmetic and border behaviour.

Tests:

- directed pixels/windows;
- synthetic images;
- deterministic output.

Gate:

- reference behaviour is stable and documented.

## Phase 3 — Primitive RTL

Recommended order:

1. `pixel_pkg.sv`
2. `rgb_to_gray.sv`
3. `elastic_stage.sv`
4. `apb_regs.sv`
5. simple counters/control helpers

Each module receives self-checking verification before integration.

## Phase 4 — Line-buffer/window engine

Implement:

- coordinates;
- two line buffers;
- horizontal shift/window;
- W+1 delayed mapping;
- border classification;
- drain controller.

Use labelled small frames first.

Gate:

- every generated window/output coordinate matches software expectation.

## Phase 5 — Architecture A integration

Integrate compact Sobel pipeline.

Gate 2 evidence:

- complete output frame;
- exact input/output counts;
- bit-exact comparison on deterministic images.

## Phase 6 — Deep regression

Add:

- gaps;
- stalls;
- reset;
- config;
- multiple dimensions;
- random images;
- real image;
- traceability.

Gate 3:

- verified regression based on actual tool logs.

## Phase 7 — Formal

Prove selected high-value control/protocol properties.

Gate:

- documented property/assumption/results.

## Phase 8 — Compact implementation baseline

Run:

- synthesis;
- place/route;
- resource extraction;
- timing;
- critical-path analysis.

Gate:

- reproducible Architecture A implementation evidence.

## Phase 9 — Bottleneck review

Do not start B until:

- Architecture A critical path is measured;
- measured limiting path is described;
- proposed stage boundaries have a written hypothesis.

## Phase 10 — Architecture B

Implement only intended pipeline changes.

Re-use the full functional regression.

Gate:

- bit-exact functional equivalence.

## Phase 11 — Controlled A/B comparison

Same target/settings.

Measure:

- resources;
- timing;
- latency;
- initiation interval;
- derived throughput.

Gate 4:

- quantitative trade-off conclusion.

## Phase 12 — Debug case studies

Intentionally inject a few defects only on dedicated branches.

Good candidates:

- signedness;
- insufficient width;
- metadata misalignment;
- stalled-output instability;
- line-buffer off-by-one;
- reset-valid corruption.

Document:

- symptom;
- failing test;
- root cause;
- fix;
- regression.

No deliberate bug remains on `main`.

## Phase 13 — Publication

README should show:

- project problem;
- architecture;
- protocol;
- input image;
- reference output;
- RTL output;
- diff;
- verification evidence;
- formal evidence;
- A/B PPA results;
- exact commands;
- limitations;
- original/third-party boundary.

Perform clean-checkout validation.

Tag `v1.0-cv-ready` only after this succeeds.

## Phase 14 — Optional physical FPGA

Only after Gate 5.

Board choice must be justified by:

- cost;
- tool support;
- what new evidence it adds.

If Project F board/display code is used:

- preserve attribution;
- add third-party manifest entry.

---

# 33. Milestone evidence checklist

A milestone is not “worked on X”.

A milestone is an evidence state.

Examples:

Bad:
> implemented line buffer.

Good:
> line-buffer/window engine passes labelled 3×3/4×4/5×5 coordinate/window tests under source gaps and output stalls.

Bad:
> pipelined Sobel done.

Good:
> timing-oriented Sobel is bit-equivalent to compact architecture across the full regression, with measured additional latency recorded.

Bad:
> timing optimized.

Good:
> routed critical path and slack improved under identical ECP5 flow while resources and latency were recorded.

---

# 34. Final deliverables

The finished project should contain:

## Engineering
- requirements;
- microarchitecture;
- original synthesizable RTL;
- reference model;
- cocotb regression;
- formal harnesses;
- build system;
- synthesis/timing scripts;
- A/B architecture results;
- decision log;
- limitations.

## Evidence
- selected regression logs;
- selected formal reports;
- reference implementation reports;
- timing summaries;
- utilization/resources;
- critical-path reports;
- result tables;
- input/reference/RTL/diff images.

## Public presentation
- GitHub README;
- architecture diagram;
- reproducible commands;
- CI status;
- licence;
- third-party notices;
- CV-ready project summary.

---

# 35. Final project narrative

The final report/README should tell a causal story:

1. define exact streaming/image requirements;
2. build an independent software oracle;
3. build and verify primitive RTL;
4. solve line buffering/window alignment;
5. integrate the compact baseline;
6. stress protocol/reset/config;
7. strengthen selected claims formally;
8. synthesize and route the verified baseline;
9. inspect the real critical path;
10. perform the mandatory controlled pipeline experiment, calling it bottleneck-driven only when Architecture A timing evidence supports that interpretation;
11. re-run identical verification;
12. compare both versions under controlled conditions;
13. explain the timing/area/latency/throughput trade-off;
14. publish reproducible evidence.

This is the same evidence-driven engineering pattern that made the earlier CPU project valuable.
