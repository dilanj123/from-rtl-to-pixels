# Known limitations

- No physical FPGA board demonstration or physical throughput measurement.
- Routed timing uses a virtual ECP5 LFE5U-45F / CABGA381 / speed-6 target.
- Timing comparison is single-seed (seed 1), with a 5 MHz clean/fail grid; it is not statistically robust multi-seed Fmax characterization.
- Selected formal verification covers targeted protocol/control properties; no whole-accelerator formal proof is claimed.
- Formal coverage is limited to recorded module elaborations/configurations.
- Image dimensions are compile-time parameters; runtime dimensions are unsupported.
- The design uses one clock domain and no external framebuffer, DMA, CPU/Linux subsystem, HDMI/VGA pipeline, general convolution engine, or CNN acceleration.
- The interface is AXI4-Stream-inspired, not a full AXI4-Stream compliance claim.
- Frames do not overlap during final drain.
- The public demo image is the public-domain Wikimedia Commons Tokinokane2005-1-4.jpg, SHA-256 `8331a2d0edb64057fdf31b1b1385430c58b2698942ef7d29e00e392b7350d5e4`.
- Physical board work is optional follow-on scope after Gate 5.
