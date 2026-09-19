# Project State

Current phase: Phase 1 — Gate-1 specification freeze  
Current gate: Gate 1 — OPEN  
Known-good commit before Phase 1: `6bd14fca23b7f74e74fbe18f911d718478f49bbb`  
Current architecture: specified single-clock streaming Sobel; no accelerator RTL implemented

Repository:
- local: `/Users/Dilan/Projects/from-rtl-to-pixels`
- branch: `main`
- remote: `https://github.com/dilanj123/from-rtl-to-pixels.git`

Gate 0 evidence:
- macOS arm64 environment identified
- CORE Git/Python/Make available
- GitHub CLI installed/authenticated
- public remote created
- `make doctor` bootstrap policy operational

Functional regression: not implemented  
Formal: not run  
Synthesis: not run  
Timing: not run

Known missing future workflow dependencies:
- Verilator
- cocotb/pytest/NumPy/Pillow
- Yosys/SBY/formal solver
- nextpnr-ecp5/ECP5 support

Latest strong evidence:
Phase-0 bootstrap repository committed and pushed with clean working tree.

Open bugs:
none known; no accelerator implementation exists.

Open decisions:
none currently blocking Gate 1.

Current bottleneck:
Gate-1 documents must be applied and consistency-reviewed before reference-model implementation.

Next task:
Apply/review the Gate-1 document set. Do not begin RTL.
