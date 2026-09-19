# Requirements

## Scope

The MVP is a single-clock synthesizable SystemVerilog Sobel accelerator using an AXI4-Stream-inspired pixel interface and same-clock APB3-style configuration.

Canonical dimensions are `640x480`; legal elaboration-time dimensions require `IMG_WIDTH >= 3` and `IMG_HEIGHT >= 3`.

Out of scope before Gate 5: CDC, multiple clocks, async FIFOs, DMA, external framebuffer memory, CPU/Linux, dynamic dimensions, additional filters, CNN/DNN acceleration, overlapping frames, mandatory display output, and mandatory FPGA hardware.

## Stream interface

Input:
- `s_tdata[23:16]=R`
- `s_tdata[15:8]=G`
- `s_tdata[7:0]=B`
- `s_tvalid`, `s_tready`
- `s_tuser`: SOF
- `s_tlast`: EOL

Output:
- `m_tdata[7:0]`
- `m_tvalid`, `m_tready`
- `m_tuser`: SOF
- `m_tlast`: EOL

A transfer occurs only on `valid && ready`.

While `m_tvalid && !m_tready`, `m_tdata`, `m_tuser`, and `m_tlast` shall remain stable.

Only `s_tvalid && s_tready` may advance real image state.

## Frame/metadata

Pixels are raster ordered left-to-right, then top-to-bottom.

A valid frame contains exactly `IMG_WIDTH*IMG_HEIGHT` accepted input pixels and produces exactly the same number of accepted output pixels.

Expected input metadata:
- SOF only on the first accepted frame pixel.
- EOL only on the final accepted pixel of each row.

Internal coordinates are authoritative.

Malformed accepted metadata shall:
1. abort the current frame;
2. set sticky `FRAME_ERROR`;
3. clear remaining in-flight frame state;
4. return control to `WAIT_SOF`;
5. require a valid SOF before another frame is admitted.

Already transferred output pixels from an aborted frame cannot be recalled; consumers/tests shall discard the incomplete frame.

## Arithmetic

Grayscale:

`Y = (77*R + 150*G + 29*B + 128) >> 8`

Use an unsigned 16-bit accumulator and unsigned 8-bit result.

Sobel:

`Gx = -p00 + p02 - 2*p10 + 2*p12 - p20 + p22`

`Gy = -p00 - 2*p01 - p02 + p20 + 2*p21 + p22`

Use signed 12-bit Gx/Gy intermediates.

Magnitude:

`M = abs(Gx) + abs(Gy)`

Use unsigned 11-bit `M`.

Clamp:

`M8 = min(M,255)`

Threshold:
- bypass=1 → output `M8`
- bypass=0 and `M8 < active_threshold` → `0`
- otherwise → `M8`

## Borders

Top row, bottom row, left column, and right column shall output zero.

## Stream alignment and drain

For zero-based linear indices:

`k = n - (IMG_WIDTH + 1)`

Output index 0 becomes creatable when zero-based input index `IMG_WIDTH+1` is accepted, i.e. on the `IMG_WIDTH+2`-th accepted input pixel.

After the final real input pixel, exactly `IMG_WIDTH+1` logical output positions remain.

The accelerator shall enter `DRAIN`, admit no new frame, generate those remaining border-zero tokens, drain downstream pipeline state, and return to `WAIT_SOF` only after the final output token transfers.

Frames shall not overlap.

## Reset

`rst` is synchronous, active-high, and common to the MVP.

Reset shall:
- clear stream/pipeline valid state;
- reset coordinates/controller to `WAIT_SOF`;
- abandon a partial frame;
- deassert `m_tvalid`;
- invalidate rather than physically clear line-buffer memory;
- restore:

`RUN_ENABLE=0`  
threshold shadow/active=`128`  
bypass shadow/active=`0`  
`FRAME_COUNT=0`  
`FRAME_ERROR=0`

After reset, a new frame requires valid SOF.

## APB/configuration

No-wait-state APB3-style interface.

Register map:

| Addr | Register | Fields |
|---|---|---|
| `0x00` | CONTROL | bit0 `RUN_ENABLE`, bit1 `BYPASS_THRESHOLD_SHADOW` |
| `0x04` | THRESHOLD | bits7:0 `THRESHOLD_SHADOW` |
| `0x08` | STATUS | bit0 `BUSY`, bit1 `DRAINING`, bit2 `CONFIG_PENDING`, bit3 `FRAME_ERROR` |
| `0x0C` | FRAME_COUNT | completed frames |

Reserved read bits return zero.

`STATUS[3]` is W1C. Other STATUS writes have no effect. If a new frame error and a W1C clear occur on the same edge, setting the error wins.

`FRAME_COUNT` is read-only and increments on transfer of the final pixel of a complete output frame. Overflow wraps modulo `2^32`.

Invalid or non-32-bit-aligned accesses:
- complete with `PREADY=1`;
- assert `PSLVERR=1`;
- invalid reads return zero;
- invalid writes have no effect.

Valid accesses assert no error.

Threshold and threshold bypass are shadow/active configuration. Shadow copies atomically to active on accepted SOF.

If an APB configuration write and accepted SOF occur on the same edge, that frame uses the pre-edge shadow value; the write applies to the following frame.

`RUN_ENABLE` controls admission of a new frame. Clearing it during a frame does not abort that frame.

Status:
- `BUSY`: frame processing or draining.
- `DRAINING`: end-of-frame drain only.
- `CONFIG_PENDING`: threshold shadow != active OR bypass shadow != active.
- `FRAME_ERROR`: sticky diagnostic described above.

## Performance terminology

Without stalls, target steady-state initiation interval is one pixel/token per cycle after fill.

Report separately:
- arithmetic/pipeline latency;
- steady-state initiation interval;
- steady-state pixels/clock;
- total unstalled frame cycles;
- whole-frame effective pixels/clock including fill/drain.

Latency and throughput shall be measured or derived from evidence, never assumed.
