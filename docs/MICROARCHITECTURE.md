# Microarchitecture

## Data path

`RGB stream`
→ ingress/control
→ integer grayscale
→ two line buffers + horizontal shifts
→ 3x3 window/token coordinate
→ Sobel arithmetic
→ magnitude/clamp
→ threshold/bypass
→ elastic output
→ 8-bit output stream

Configuration is provided by a same-clock APB register block.

## Control states

### WAIT_SOF
No frame active.

A new frame may begin only when:
- `RUN_ENABLE=1`;
- a valid SOF is offered;
- downstream/internal capacity permits acceptance.

Non-SOF traffic is not admitted as a new frame.

### RUN
Real pixels are accepted only on `s_tvalid && s_tready`.

Only acceptance may update:
- input coordinate/count;
- grayscale line-buffer contents;
- real window state.

Accepted metadata is checked against authoritative coordinates.

A metadata violation aborts the frame, clears remaining in-flight frame tokens, sets `FRAME_ERROR`, and returns to `WAIT_SOF`.

After the final valid input pixel, enter `DRAIN`.

### DRAIN
No new real input/frame is accepted.

Generate the final `W+1` logical output positions. They are border-zero positions.

The drain cursor advances only when its generated token is admitted into the downstream ready/valid pipeline.

Return to `WAIT_SOF` only after the final output pixel transfers.

## Window alignment

For accepted real input index `n`, normal output coordinate/token index is:

`k = n-(W+1)`

The first output token is creatable while accepting `n=W+1`.

Window and line-buffer state shall stall whenever real input acceptance stalls.

Already-created downstream tokens may continue draining during source gaps.

## Output metadata

Generate SOF/EOL from output token index/coordinate, not delayed frame-sized marker storage.

- SOF iff output coordinate is `(0,0)`.
- EOL iff output column is `W-1`.

Data and metadata share the same ready/valid transaction.

## Configuration

Threshold and bypass have shadow and active copies.

At accepted SOF:

`active <= pre-edge shadow`

`RUN_ENABLE` is not frame-shadowed; it controls only admission of a new frame.

## Architecture A

Compact baseline.

No performance-motivated internal arithmetic pipeline registers shall be inserted inside the Sobel→magnitude→clamp→threshold arithmetic region beyond registers required for correct elastic protocol boundaries.

Architecture A must be fully verified and routed before Architecture-B boundaries are selected.

## Architecture B

Mandatory controlled timing-oriented pipeline experiment.

B shares with A:
- external interfaces;
- grayscale/window infrastructure;
- borders;
- configuration;
- controller;
- dimensions;
- reference model/tests;
- target/tool/settings/measurement flow.

B differs only through intended arithmetic pipeline boundaries.

Selected first boundary: one ready/valid elastic stage immediately after Sobel Gx/Gy. The conceptual 28-bit token carries `{final_tag, user, last, border, gx, gy}`. Its ready propagates from the existing output elastic stage through magnitude/clamp/threshold back to output_control. No other arithmetic pipeline boundary is added in the initial B experiment.

This boundary is selected from the corrected synchronous Architecture-A path: line-buffer EBR output through the Sobel-to-magnitude/clamp/threshold cone to the final output elastic FF.

If the change directly addresses the measured A bottleneck it may be described as a bottleneck-driven optimisation. Otherwise it shall be described only as a controlled pipeline experiment.

A and B shall produce bit-identical completed output images.

### Architecture-B implementation status

The initial Architecture-B experiment is implemented as one ready/valid elastic stage immediately after Sobel Gx/Gy. The exact 28-bit token mapping is:

- `[27]` final tag
- `[26]` SOF/user
- `[25]` EOL/last
- `[24]` border
- `[23:12]` Gx
- `[11:0]` Gy

The existing output elastic `s_ready` drives the arithmetic stage `m_ready`; the arithmetic stage `s_ready` drives `output_control.output_ready_i`. No additional arithmetic pipeline stage has been introduced. Functional regression evidence is recorded in `results/raw/arch-b-functional-regression.log`; Architecture-B synthesis, P&R and timing remain deferred to Phase 11.
