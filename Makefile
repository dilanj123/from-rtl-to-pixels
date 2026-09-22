.DEFAULT_GOAL := help
.PHONY: help doctor lint test-unit test test-real-image formal synth timing ppa all clean
help:
	@printf '%s\n' 'Architecture A: implemented, verified, routed baseline' 'Architecture B: functional RTL available after Phase 10' 'Architecture-B functional RTL available; controlled A/B synthesis/timing comparison' 'make help    - show available commands' 'make doctor  - inventory tools; fail for missing/broken CORE dependencies' 'make synth ARCH=compact - synthesize canonical Architecture A' 'make timing ARCH=compact FREQ_MHZ=N SEED=N - route and report one timing point' 'make synth ARCH=compact|pipelined; make timing ARCH=compact|pipelined FREQ_MHZ=N SEED=N; make ppa' 'No automatic installation.'
doctor:
	@command -v python3 >/dev/null 2>&1 || { echo 'CORE python3: MISSING'; exit 1; }
	@python3 scripts/doctor.py
synth:
	@case "$(ARCH)" in compact) scripts/synth/run_arch_synth.sh compact;; pipelined) scripts/synth/run_arch_synth.sh pipelined;; *) echo 'ARCH must be compact or pipelined' >&2; exit 2;; esac

timing:
	@test -n "$(FREQ_MHZ)" || { echo 'FREQ_MHZ is required' >&2; exit 2; }
	@case "$(ARCH)" in compact) scripts/timing/run_arch_route.sh compact "$(FREQ_MHZ)" "$(if $(SEED),$(SEED),1)";; pipelined) scripts/timing/run_arch_route.sh pipelined "$(FREQ_MHZ)" "$(if $(SEED),$(SEED),1)";; *) echo 'ARCH must be compact or pipelined' >&2; exit 2;; esac

ppa:
	@scripts/analysis/run_arch_ab_comparison.sh

lint test-unit test test-real-image formal all clean:
	@echo '$@: NOT IMPLEMENTED (Phase 0 only)' >&2
	@exit 2
