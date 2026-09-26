# RTL Schematic Review

## Source baseline

The diagrams were reviewed against the two top-level RTL modules and every instantiated production module at the `640x480` default configuration. The machine-readable inventory is `docs/assets/rtl-interface-inventory.json`.

## Top-level interfaces reviewed

Clock/reset, RGB streaming input, 8-bit output stream, and the APB-style configuration/status ports were checked against both top-level declarations.

## Modules reviewed

`pixel_control`, `rgb_to_gray`, `line_buffer`, `window_3x3`, `sobel_compact`, `magnitude_clamp`, `threshold_stage`, `output_control`, `elastic_stage`, `apb_regs`, and the `pixel_pkg` typedef source.

## Architecture A connectivity

The compact path shows grayscale feeding both line history and the 3×3 window, window taps feeding Sobel, then magnitude/clamp, threshold, border override and the 11-bit output elastic stage. `output_control` is shown as parallel control and geometry logic.

## Architecture B connectivity

The only architectural difference is the `DATA_WIDTH=28` elastic stage immediately after Sobel Gx/Gy. Its token carries final tag, SOF, EOL, border, Gx and Gy; the downstream arithmetic and 11-bit output buffer are unchanged.

## Top-level glue represented

Input admission, `input_accept`, `frame_abort_q`, pipeline flush, metadata generation, border-zero selection, `final_pending_q`, `frame_done_external`, and `draining_status` are represented as top-level glue rather than hidden inside module boxes.

## Widths represented

Parameter-dependent `ROW_W` and `COL_W` expressions are retained in the inventory, with canonical `640x480` values of 9 and 10. Data widths include RGB 24, grayscale/taps 8, signed Gx/Gy 12, magnitude 11, B token 28, and output token 11.

## Signals intentionally grouped

Clock/reset, coordinate/control, data, metadata, configuration, status and ready/backpressure are grouped to keep the integration pages readable. Page 4 expands the module ports.

## Module outputs shown as unused/observability-only

`window_valid_o`, `window_row_o`, `window_col_o`, `p11_o`, and `magnitude_o` are identified as observable outputs that are not consumed by the production top.

## Diagram files

- `docs/assets/rtl-architecture.drawio` — editable five-page source.
- `docs/assets/rtl-system-context.svg` — system context.
- `docs/assets/rtl-architecture-a.svg` — Architecture A interconnect.
- `docs/assets/rtl-architecture-b.svg` — Architecture B interconnect.
- `docs/assets/rtl-module-interfaces.svg` — module interfaces.
- `docs/assets/rtl-control-flow.svg` — ready/valid and frame control.

## Validation

`check_rtl_schematic.py` validates the inventory, token mappings, required pages and assets. `check_publication_assets.py` validates XML/SVG structure and repository links.
