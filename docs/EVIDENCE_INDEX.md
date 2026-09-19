# Evidence index

Classification: bootstrap checks, Gate-1 documentation, and focused reference-model verification. No project RTL simulation, formal, synthesis, or timing evidence exists yet.
Bootstrap commit: `f540928c1d04e0ae191236fb44c326404c70e755`. Pre-commit logs necessarily precede its hash.
Published Phase-0 baseline: `6bd14fca23b7f74e74fbe18f911d718478f49bbb`.
Gate-1 documentation commit: `a19678a45e5bbf4dad3ee5e250b7dfcbcddbd1a1` (`Freeze Gate 1 project contract`); specifications only; subsequently frozen by the Phase-2 task.
Conditions: arm64 macOS 26.4.1, current PATH and system Python, 2026-09-19.

| Claim / check | Commands and evidence |
|---|---|
| Source provenance | `results/raw/bootstrap-sources.log`: read-only source SHA-256 hashes |
| Host and executable inventory | `results/raw/bootstrap-checks.log`: exact commands, stdout/stderr, exit codes; `make help` and `make doctor` exit 0 |
| Unimplemented work fails | Same log: `make test` exit 2 |
| Missing/broken CORE fails | `results/raw/bootstrap-negative-checks.log`: isolated PATH and exit-9 stub probes |
| Initial directory / Git setup | `results/raw/bootstrap-inspection.log` |
| Staged review | `results/raw/bootstrap-staged-review.log`; excludes itself because recorded after the first staging |
| Commit / final working tree | Local ignored `results/raw/bootstrap-postcommit.log`, produced after the bootstrap commit; contains commit hash and final status |

Gate 0 evidence: the bootstrap logs record the original OS/architecture, CORE paths/versions and then-missing tools. GitHub CLI is now available and authenticated as `dilanj123`; the public origin is `https://github.com/dilanj123/from-rtl-to-pixels.git`. Check current state with `gh auth status`, `gh repo view --json url,visibility`, and `git remote -v`; historical bootstrap logs remain unchanged. `make doctor` works under the CORE-only bootstrap policy. Verilator and cocotb are now installed and smoke-checked (see `results/raw/sim-toolchain-smoke.log`); Yosys, SBY, formal solvers and nextpnr-ecp5 remain unavailable on PATH. ECP5 usability remains unproven.

Gate 1 was closed by the Phase-2 task. No accelerator implementation or project RTL simulation/formal/synthesis/timing results are claimed.

Claim: Independent Python Sobel reference-model focused suite passes.
Git commit: `57fa1f438e23015f50ad91fb0e2faf0582cac18c`
Command: `.venv/bin/python -m pytest -q tb/tests/test_reference_model.py`
Evidence: `results/raw/reference-model-pytest.log`
Conditions: Python 3.14.0; NumPy 2.5.3; Pillow 12.3.0; pytest 9.1.1; 13 focused tests.
Classification: `REFERENCE-MODEL VERIFIED`
