# Trade-offs

Architecture A is the compact baseline: 665 LUT4, 194 flip-flops, a 35/40 MHz seed-1 clean/fail constraint frontier, and a 25.731 ns synchronous path. Architecture B adds one 28-bit ready/valid boundary after Sobel Gx/Gy. It uses 775 LUT4 and 223 flip-flops, adds one cycle of first-output latency, and preserves II=1 and one pixel per clock.

Under identical 640x480 ECP5 conditions, B reaches a 60/65 MHz clean/fail frontier and has a 16.194 ns synchronous path. Derived peak rates are 35 and 60 Mpixel/s at the clean constraints; these are not physical measurements. The controlled result supports retaining B as the timing-oriented variant while A remains the compact baseline.

Evidence: `results/raw/arch-ab-comparison.json`, `docs/ARCHITECTURE_COMPARISON.md`, and `results/raw/p11-arch-a-performance.json` / `p11-arch-b-performance.json`.
