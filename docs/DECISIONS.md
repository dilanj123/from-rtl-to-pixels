# Adopted decisions for Gate 1

Recorded during Phase 0 on 2026-09-19 from explicit user instructions. These are specification decisions, not implementation evidence. Full Gate-1 documentation remains pending. User clarifications supersede conflicting source wording; the source files remain unchanged.

1. Authority: 00 → 01 → Gate-1 docs → implementation. This inserts the operating instructions into the master plan hierarchy.
2. Output index 0 becomes creatable when input index W+1 is accepted: the W+2-th accepted pixel. This corrects the initial-fill wording in 00 §7.2; final drain remains W+1 logical output positions.
3. Reset: RUN_ENABLE=0; threshold shadow/active=128; bypass shadow/active=0; FRAME_COUNT=0; FRAME_ERROR=0.
4. BUSY covers processing/draining; DRAINING covers end-frame drain only; CONFIG_PENDING derives from shadow != active; FRAME_ERROR is sticky, W1C through STATUS[3].
5. Invalid/misaligned APB accesses complete with PREADY=1, PSLVERR=1; invalid reads return zero, invalid writes have no effect.
6. Malformed metadata aborts the frame, sets FRAME_ERROR, clears in-flight frame state and returns to WAIT_SOF; admission requires a valid SOF.
7. Separate steady-state II/pixels-per-clock from whole-frame throughput including fill/drain.
8. Architecture B is a mandatory controlled pipeline experiment; call it bottleneck-driven optimisation only when Architecture A timing evidence supports that interpretation. This qualifies the bottleneck-dependent framing in 00 and 01; no Architecture B design is authorised in Phase 0.
