.DEFAULT_GOAL := help
.PHONY: help doctor lint test-unit test test-real-image formal synth timing ppa all clean
help:
	@printf '%s\n' 'Architecture-A implementation baseline' 'make help    - show available commands' 'make doctor  - inventory tools; fail for missing/broken CORE dependencies' 'make synth ARCH=compact - synthesize canonical Architecture A' 'make timing ARCH=compact FREQ_MHZ=N SEED=N - route and report one timing point' 'ARCH=pipelined is intentionally unavailable until Phase 9 bottleneck review' 'No automatic installation.'
doctor:
	@command -v python3 >/dev/null 2>&1 || { echo 'CORE python3: MISSING'; exit 1; }
	@python3 scripts/doctor.py
synth:
	@test "$(ARCH)" = compact || { echo 'Architecture B is not implemented; Phase 9 bottleneck review must occur first.' >&2; exit 2; }
	@scripts/synth/run_arch_a_synth.sh

timing:
	@test "$(ARCH)" = compact || { echo 'Architecture B is not implemented; Phase 9 bottleneck review must occur first.' >&2; exit 2; }
	@test -n "$(FREQ_MHZ)" || { echo 'FREQ_MHZ is required' >&2; exit 2; }
	@scripts/timing/run_arch_a_route.sh "$(FREQ_MHZ)" "$(if $(SEED),$(SEED),1)"

lint test-unit test test-real-image formal ppa all clean:
	@echo '$@: NOT IMPLEMENTED (Phase 0 only)' >&2
	@exit 2
