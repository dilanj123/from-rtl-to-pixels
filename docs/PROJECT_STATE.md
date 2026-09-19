# Project State

Current phase: Phase 3 — Simulation-toolchain bootstrap
Current gate: Gate 1 CLOSED; Gate 2 OPEN
Known-good commit before Phase 3: `57fa1f438e23015f50ad91fb0e2faf0582cac18c`
Current architecture: frozen single-clock streaming Sobel specification; no accelerator RTL implemented

Gate 0:
CLOSED — environment/repository/bootstrap established.

Gate 1:
CLOSED — project contract, interfaces, arithmetic, alignment, drain, reset,
configuration, verification strategy, formal scope, A/B experiment and reuse
policy are frozen and synchronized.

Reference model:
REFERENCE-MODEL VERIFIED by the focused Phase-2 pytest suite.
Evidence: results/raw/reference-model-pytest.log

Phase 3 simulation toolchain:
Verilator 5.052 and cocotb 2.1.0 installed and smoke-checked using a temporary non-project XOR fixture.
Evidence: results/raw/sim-toolchain-smoke.log

RTL simulation:
Project RTL not yet implemented or verified.

Formal:
not run

Synthesis:
not run

Timing:
not run

Known future workflow dependencies:
- Yosys/SBY/formal solver for formal
- nextpnr-ecp5/ECP5 database for implementation

Current bottleneck:
First primitive RTL specification and verification remain pending.

Next task:
Specify and verify the first primitive RTL: `pixel_pkg`, then `rgb_to_gray`. This bootstrap adds no accelerator RTL.
