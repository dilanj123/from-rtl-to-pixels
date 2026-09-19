# Bootstrap evidence index

Classification: local bootstrap checks only. No accelerator verification claim.
Commit: the single bootstrap commit containing these logs (`git log --reverse --oneline`). Pre-commit logs necessarily precede its hash.
Conditions: arm64 macOS 26.4.1, current PATH and system Python, 2026-09-19.

| Claim / check | Commands and evidence |
|---|---|
| Source provenance | `results/raw/bootstrap-sources.log`: read-only source SHA-256 hashes |
| Host and executable inventory | `results/raw/bootstrap-checks.log`: exact commands, stdout/stderr, exit codes; `make help` and `make doctor` exit 0 |
| Unimplemented work fails | Same log: `make test` exit 2 |
| Missing/broken CORE fails | `results/raw/bootstrap-negative-checks.log`: isolated PATH and exit-9 stub probes |
| Initial directory / Git setup | `results/raw/bootstrap-inspection.log` |
| Staged review | `results/raw/bootstrap-staged-review.log`; excludes itself because recorded after the first staging |
| Commit / final working tree | Local ignored `results/raw/bootstrap-postcommit.log`, produced after the only commit; contains commit hash and final status |

Gate 0 audit: OS/architecture and CORE paths/versions recorded; gh, Verilator, Yosys, SBY, solvers and nextpnr-ecp5 recorded as unavailable on PATH. Doctor works, repository initialized, bootstrap commit recorded in post-commit evidence. Public remote conditional action blocked by unavailable gh. ECP5 support required by 00 §21.1 remains unconfirmed. Gate 0 stays OPEN.
