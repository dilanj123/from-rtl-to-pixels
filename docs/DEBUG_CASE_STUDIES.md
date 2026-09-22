# Debug Case Studies

All defects documented here were deliberately injected after Gate 4 closed, on dedicated debug branches. No deliberate defect remains on `main`.

## DEBUG-001 — Signedness Loss

### Motivation
Verify that signed arithmetic is treated as part of the module interface contract.

### Injected defect
On `debug/signedness`, commit `2efe6a8`, the signed qualifiers were removed from both `magnitude_clamp` gradient inputs.

### Observed symptom
The magnitude regression failed on sign-sensitive vectors; for `gx=-3, gy=-7`, expected magnitude `(10,10)` but observed `(2038,255)`. The suite reported 7/7 failures.

### Failing regression
`make -f tb/tests/Makefile.magnitude_clamp` with the deliberate branch defect.

### Root cause
Negative two's-complement gradients were interpreted as unsigned values. Bit width alone does not preserve arithmetic semantics.

### Fix
Restored the signed input declarations in commit `0546324`.

### Passing regression
The same focused regression passed 7/7.

### Engineering lesson
Signedness is part of the RTL arithmetic interface contract.

### Evidence
`results/raw/debug-001-signedness-fail.log`, `results/raw/debug-001-signedness-pass.log`

### Branch and commits
`debug/signedness`; defect `2efe6a8`; fix `0546324`; pushed.

## DEBUG-002 — Stalled Output Instability

### Motivation
Verify temporal ready/valid stability under downstream backpressure.

### Injected defect
On `debug/stalled-output`, commit `6ea07f8`, `m_data` was changed to a combinational `s_valid ? s_data : data_q` bypass.

### Observed symptom
`backpressure_holds_output_stable` expected `0x12` but observed `0x34` while `m_valid=1` and `m_ready=0`; randomized transfer checking also failed. The focused suite reported 4/6 pass.

### Failing regression
`make -f tb/tests/Makefile.elastic_stage` with the deliberate branch defect.

### Root cause
A pending valid transaction must remain driven by registered `data_q` for the entire stall. The bypass allowed upstream changes to alter the transaction.

### Fix
Restored `assign m_data = data_q` in commit `26c6af5`.

### Passing regression
The same focused regression passed 6/6.

### Engineering lesson
Ready/valid correctness is temporal: data and metadata remain stable for the complete duration of a stalled valid transaction.

### Evidence
`results/raw/debug-002-stalled-output-fail.log`, `results/raw/debug-002-stalled-output-pass.log`

### Branch and commits
`debug/stalled-output`; defect `6ea07f8`; fix `26c6af5`; pushed.

## DEBUG-003 — Pipeline Metadata Misalignment

### Motivation
Verify that a new arithmetic pipeline transports metadata with its logical token.

### Injected defect
On `debug/metadata-misalignment`, commit `03f2fbb`, SOF/user and EOL/last were swapped in the 28-bit arithmetic token pack order without changing unpacking.

### Observed symptom
The 3x3 Gate-2 suite failed all 4 tests. The first failure was output index 0: expected `m_tuser=1`, observed `0`.

### Failing regression
`make -f tb/tests/Makefile.rtl_to_pixels_top_pipelined` at 3x3 with the deliberate branch defect.

### Root cause
Arithmetic and metadata share one ready/valid token. Changing only the pack order changed the meaning of metadata at the output boundary.

### Fix
Restored the original pack order in commit `44fb4c3`.

### Passing regression
The same 3x3 Gate-2 suite passed 4/4 with zero mismatches and correct SOF/EOL metadata.

### Engineering lesson
Pipeline correctness requires metadata/control to travel with the same logical arithmetic token.

### Evidence
`results/raw/debug-003-metadata-misalignment-fail.log`, `results/raw/debug-003-metadata-misalignment-pass.log`

### Branch and commits
`debug/metadata-misalignment`; defect `03f2fbb`; fix `44fb4c3`; pushed.
