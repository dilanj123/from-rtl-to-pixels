# Agent Rules

Read authority in this order:

1. `00_MASTER_PROJECT_PLAN.md`
2. `01_CHATGPT_PROJECT_OPERATING_INSTRUCTIONS.md`
3. `docs/REQUIREMENTS.md`
4. `docs/MICROARCHITECTURE.md`
5. `docs/VERIFICATION_PLAN.md`
6. `docs/DECISIONS.md`
7. `docs/PROJECT_STATE.md`
8. `docs/EVIDENCE_INDEX.md`
9. implementation

Never resolve contradictions silently.

Engineering sequence:

specify → reference model → verified primitives → compact baseline → deep verification → formal → synthesis/P&R → measured bottleneck → controlled pipeline change → re-verify → compare → conclude.

Rules:
- Do not claim PASS, proof, zero mismatches, synthesis, timing closure, Fmax, resource counts or improvement without actual tool evidence.
- Distinguish SPECIFIED, ASSUMED, HYPOTHESISED, REFERENCE-MODEL VERIFIED, RTL SIMULATION VERIFIED, FORMALLY CHECKED, SYNTHESISED, PLACED/ROUTED, TIMING-CLEAN, DERIVED and PHYSICALLY MEASURED.
- Keep changes narrow and reviewable.
- No unrelated refactors or silent dependency upgrades.
- Do not install dependencies unless the task explicitly authorises it.
- Do not modify frozen interfaces/behaviour without updating requirements, tests and decisions.
- Preserve known-good `main`.
- Every discovered functional defect requires a regression.
- Core accelerator RTL/reference/verification/formal/A-B experiment must be original.
- Third-party reuse requires provenance/licence records.
- Architecture B starts only after Architecture-A functional and implementation evidence exists.
- Return exact commands, exit codes, relevant logs, diff/stat and status for local tasks.

Current restriction:
Gate 1 and Gate 2 are recorded closed in docs/PROJECT_STATE.md; Gate 3 remains open. Keep work scoped to the authorised verification task. Do not change production RTL during verification-only tasks; report any detected RTL failure before proceeding. Architecture B remains gated on Architecture-A functional and implementation evidence.
