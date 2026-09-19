# Decisions

`D-001` Single-clock MVP; CDC is follow-on scope.

`D-002` RGB888 input and 8-bit edge output use documented AXI4-Stream-inspired ready/valid semantics, not a full AXI4-Stream compliance claim.

`D-003` Compile-time dimensions; canonical `640x480`; minimum `3x3`.

`D-004` Grayscale is `(77R+150G+29B+128)>>8`.

`D-005` Sobel uses the frozen Gx/Gy equations, L1 magnitude and 8-bit saturation.

`D-006` All four image borders output zero.

`D-007` Stream mapping is `k=n-(W+1)`. Output 0 is creatable when `n=W+1` is accepted, i.e. accepted pixel `W+2`. Final drain remains `W+1` tokens.

`D-008` No frame overlap. New-frame admission waits until final output transfer completes.

`D-009` Reset is synchronous active-high; line-buffer RAM contents are invalidated, not explicitly cleared.

`D-010` Reset defaults: run=0, threshold shadow/active=128, bypass shadow/active=0, frame count=0, frame error=0.

`D-011` Threshold/bypass use shadow→active at accepted SOF. Concurrent write applies to the following frame.

`D-012` Malformed accepted SOF/EOL aborts the frame, sets sticky error, discards remaining in-flight state and requires a new valid SOF.

`D-013` STATUS meanings: BUSY=processing/draining; DRAINING=drain only; CONFIG_PENDING=shadow!=active; FRAME_ERROR=sticky W1C bit3.

`D-014` CSR bit allocation: CONTROL[0]=RUN_ENABLE, CONTROL[1]=BYPASS_THRESHOLD_SHADOW; STATUS[3:0]=FRAME_ERROR/CONFIG_PENDING/DRAINING/BUSY in descending bit order. Reserved reads return zero.

`D-015` Invalid/misaligned APB transfers complete immediately with PSLVERR, zero invalid reads and no-effect invalid writes.

`D-016` Simultaneous FRAME_ERROR set and W1C clear resolves to set, preserving the new diagnostic event.

`D-017` FRAME_COUNT is 32-bit, increments only on final completed-frame output transfer, and wraps naturally.

`D-018` Report steady-state II/pixels-clock separately from whole-frame effective throughput including fill/drain.

`D-019` Architecture A is the compact baseline without performance-motivated internal Sobel arithmetic pipeline stages.

`D-020` Architecture B is mandatory as a controlled arithmetic-pipeline experiment. It is called bottleneck-driven only when A timing evidence supports that claim.

`D-021` Planned controlled implementation target is ECP5 LFE5U-45F/CABGA381/speed-6. Local usability remains unproven until implementation-tool evidence exists.

`D-022` Core accelerator RTL, reference model, verification, formal properties and A/B experiment are original project work. Third-party support reuse requires provenance/licence manifest entries.

`D-023` Authority order is `00_MASTER_PROJECT_PLAN.md → 01_CHATGPT_PROJECT_OPERATING_INSTRUCTIONS.md → Gate-1 docs → implementation`.

`D-024` `make doctor` categories are CORE/GITHUB/SIMULATION/FORMAL/IMPLEMENTATION. Bootstrap failure depends only on CORE; later targets enforce their workflow dependencies.
