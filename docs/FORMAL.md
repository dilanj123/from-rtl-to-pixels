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

## Current formal status

No production RTL property has yet been formally checked in Phase 7.

The next formal task is:

`P7-ELASTIC-FORMAL-001`

covering `F-ELASTIC-001`, `F-ELASTIC-002`, and `F-ELASTIC-003`.
