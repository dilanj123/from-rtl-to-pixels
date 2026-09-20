# Formal Verification

## Status

Phase 7 is active.

The formal scope is intentionally targeted. Whole-accelerator formal
verification is not a project requirement and shall not be claimed.

Toolchain smoke evidence establishes only that the selected Yosys/SBY/solver
flow executes prove and cover jobs correctly. It does not establish any
property of production RTL.

## Principles

Formal claims shall be local, explicit, reproducible, and assumption-bounded.

Every property record shall identify:

- property ID;
- target RTL;
- property statement;
- environment assumptions;
- engine;
- solver;
- mode/depth;
- result;
- cover/vacuity review;
- limitations;
- evidence path.

A passing assertion without reviewed assumptions and reachability evidence is
not sufficient for a strong project claim.

Use only syntax supported by the actually installed open-source frontend.

## Planned property set

| ID | Target | Intended property | Key assumptions / notes |
|---|---|---|---|
| F-ELASTIC-001 | `elastic_stage` | While output is valid and downstream is stalled, output valid and data remain stable. | Reset disables the obligation. Inputs remain arbitrary. |
| F-ELASTIC-002 | `elastic_stage` | A stored output token is not overwritten before it is accepted. | Arbitrary source valid/data and downstream ready. |
| F-ELASTIC-003 | `elastic_stage` | Accepted-minus-transferred token occupancy remains legal and matches the one-entry stage state. | Use a small formal ghost occupancy model. No fairness required for safety. |
| F-APB-001 | `apb_regs` | Legal/invalid access behavior and read-only/error semantics are preserved. | Constrain APB transaction shape only as necessary for same-clock APB-style accesses. |
| F-APB-002 | `apb_regs` | Shadow configuration activates only on SOF; same-edge write/SOF uses pre-edge shadow. | Explicit simultaneous write/SOF cover required. |
| F-CTRL-001 | `pixel_control` | Accepted-pixel row/column state remains within legal bounds. | Legal elaboration dimensions. |
| F-OUT-001 | `output_control` | No new frame is admitted while final drain is active. | Safety property; no downstream fairness needed. |
| F-OUT-002 | `output_control` | Drain reaches completion when downstream acceptance is eventually provided. | Requires an explicit fairness/progress assumption and must be labelled assumption-dependent. |
| F-FRAME-001 | completion/control integration | Frame completion/count event occurs only on transfer of the complete external final token. | Prefer a narrow harness rather than whole-datapath proof. |

## Execution order

Formal work shall proceed in this order:

1. `elastic_stage`;
2. `apb_regs`;
3. controller/output-control safety properties;
4. selected completion/metadata invariants.

Do not begin with a whole-accelerator proof.

## Vacuity and cover policy

Every material proof task must include at least one relevant cover or
reachability check where practical.

Examples include:

- elastic stage becomes occupied;
- an occupied stage is stalled;
- a stalled token is later accepted;
- APB write and SOF occur on the same edge;
- output control enters DRAIN;
- final-drain completion is reachable under documented progress assumptions.

A proof whose triggering state cannot be reached must not be presented as
meaningful verification.

## Evidence classification

Use:

`FORMAL PROPERTY PASSED UNDER DOCUMENTED ASSUMPTIONS`

only for an actual production/project RTL property that has passed its recorded
formal job and assumption/vacuity review.

Toolchain smoke results are classified separately as:

`FORMAL TOOLCHAIN SMOKE VERIFIED`

The latter is environment evidence, not design proof.

## Elastic-stage proof record

Target:
`rtl/elastic_stage.sv`

Configuration:
`DATA_WIDTH=11`

Evidence:
`results/raw/formal-elastic-stage.log`

Engine:
`smtbmc`

Solver:
`Z3`

### F-ELASTIC-001

Result:
`FORMAL PROPERTY PASSED UNDER DOCUMENTED ASSUMPTIONS`

Property:
A valid output token remains valid with stable data while stalled.

### F-ELASTIC-002

Result:
`FORMAL PROPERTY PASSED UNDER DOCUMENTED ASSUMPTIONS`

Property:
A stalled stored token cannot be replaced by a newly accepted input
before the stored token is transferred.

### F-ELASTIC-003

Result:
`FORMAL PROPERTY PASSED UNDER DOCUMENTED ASSUMPTIONS`

Property:
The ghost accepted-minus-transferred occupancy remains legal for the
one-entry stage and agrees with the RTL valid/data state.

### Assumptions

The first sampled edge is constrained to synchronous reset.

After initialization, `rst`, `s_valid`, `s_data`, and `m_ready` are
otherwise arbitrary.

No source or destination fairness is assumed.

No source-valid or source-data hold behavior is assumed while not ready.

### Vacuity / cover review

The cover job reached:

- stage occupied;
- output stalled;
- stalled token subsequently accepted;
- empty stage accepting a token;
- simultaneous pop/push.

### Limitations

The proof is elaborated at `DATA_WIDTH=11`, matching the production
Architecture-A output elastic stage.

This is a local control/protocol proof. It is not whole-accelerator formal
verification.

The next formal task is:

`P7-APB-FORMAL-001`

covering `F-APB-001` and `F-APB-002`.
