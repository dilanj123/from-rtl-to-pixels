# Project state

Current phase: Phase 0 local bootstrap only.
Current gate: Gate 0 OPEN; ECP5 support and GitHub publication unresolved.
Known-good commit: none before bootstrap; identify the single bootstrap commit with `git log -1`. This validates only bootstrap, never accelerator functionality.
Current architecture: none implemented.
Functional regression / formal / synthesis / timing: not run; no implementation exists.
Latest strong evidence: bootstrap help/doctor and negative dependency checks in results/raw/.
Open bugs: none established; accelerator remains unimplemented.
Open decisions: full Gate-1 specifications and tested dependency versions pending.
Current bottleneck: gh and EDA tools absent from PATH; ECP5 target/database support unproven.
Next task: make GitHub CLI available, run `gh auth login` then `gh auth status`; inspect the authenticated account for an existing from-rtl-to-pixels repository before any creation. Resume the authorised public creation/push only after confirming no conflict. Review missing EDA dependencies separately, without automatic installation. Then author Gate-1 documents incorporating DECISIONS.md.

No remote has been created, inspected on GitHub, or pushed because gh is unavailable. No credentials handled. No dependencies installed. Source files remain read-only. No RTL, reference model, or Project F content added.
