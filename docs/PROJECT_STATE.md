# Project State

Current phase: Phase 2 — Independent Python reference model
Current gate: Gate 1 CLOSED; Gate 2 OPEN
Known-good commit before Phase 2: `2e0873ba61b93d24eee529a3a9e96de58ff6dc87`
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

RTL simulation:
not implemented

Formal:
not run

Synthesis:
not run

Timing:
not run

Known future workflow dependencies:
- Verilator/cocotb for RTL simulation
- Yosys/SBY/formal solver for formal
- nextpnr-ecp5/ECP5 database for implementation

Current bottleneck:
Establish actual Python reference-model evidence.

Next task:
Run focused pytest reference-model verification. Do not implement RTL.
