.DEFAULT_GOAL := help
.PHONY: help doctor lint test-unit test test-real-image formal synth timing ppa all clean
help:
	@printf '%s\n' 'Phase 0 bootstrap' 'make help    - show available commands' 'make doctor  - inventory tools; fail for missing/broken CORE dependencies' 'CORE: git python3 make; optional at bootstrap: GITHUB SIMULATION FORMAL IMPLEMENTATION' 'Not implemented: lint test-unit test test-real-image formal synth timing ppa all clean' 'Later workflow targets must enforce their own dependencies. No automatic installation.'
doctor:
	@command -v python3 >/dev/null 2>&1 || { echo 'CORE python3: MISSING'; exit 1; }
	@python3 scripts/doctor.py
lint test-unit test test-real-image formal synth timing ppa all clean:
	@echo '$@: NOT IMPLEMENTED (Phase 0 only)' >&2
	@exit 2
