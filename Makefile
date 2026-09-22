.DEFAULT_GOAL := help
.PHONY: help doctor lint test-unit test test-real-image formal synth timing ppa all clean ci
help:
	@printf '%s\n' 'From RTL to Pixels commands:' 'make doctor - check local tools' 'make lint - strict A/B lint at 3x3 and 640x480' 'make test-unit - primitive and reference regressions' 'make test - integrated A/B small-dimension regressions' 'make test-real-image - canonical 640x480 image A/B' 'make formal - selected targeted formal suite' 'make synth ARCH=compact|pipelined' 'make timing ARCH=compact|pipelined FREQ_MHZ=N SEED=N' 'make ppa - controlled A/B implementation comparison' 'make ci - release smoke suite' 'make all - full local evidence workflow' 'make clean - remove generated build/simulation products'
doctor:
	@python3 scripts/doctor.py
lint:
	@scripts/regression/run_lint.sh
test-unit:
	@scripts/regression/run_unit_regression.sh
test:
	@scripts/regression/run_integration_regression.sh
test-real-image:
	@scripts/regression/run_real_image_regression.sh
formal:
	@scripts/formal/run_selected_formal.sh
synth:
	@case "$(ARCH)" in compact|pipelined) scripts/synth/run_arch_synth.sh "$(ARCH)";; *) echo 'ARCH must be compact or pipelined' >&2; exit 2;; esac
timing:
	@test -n "$(FREQ_MHZ)" || { echo 'FREQ_MHZ is required' >&2; exit 2; }
	@case "$(ARCH)" in compact|pipelined) scripts/timing/run_arch_route.sh "$(ARCH)" "$(FREQ_MHZ)" "$(if $(SEED),$(SEED),1)";; *) echo 'ARCH must be compact or pipelined' >&2; exit 2;; esac
ppa:
	@scripts/analysis/run_arch_ab_comparison.sh
ci:
	@scripts/regression/run_lint.sh
	@PATH="$(CURDIR)/.venv/bin:$$PATH" python -m pytest -q tb/tests/test_reference_model.py
	@tmp=$$(mktemp -d); PATH="$(CURDIR)/.venv/bin:$$PATH" SIM_BUILD=$$tmp COCOTB_RESULTS_FILE=$$tmp/results.xml make -f tb/tests/Makefile.magnitude_clamp; python3 -c 'import shutil,sys; shutil.rmtree(sys.argv[1],ignore_errors=True)' $$tmp
	@tmp=$$(mktemp -d); PATH="$(CURDIR)/.venv/bin:$$PATH" SIM_BUILD=$$tmp COCOTB_RESULTS_FILE=$$tmp/results.xml make -f tb/tests/Makefile.elastic_stage; python3 -c 'import shutil,sys; shutil.rmtree(sys.argv[1],ignore_errors=True)' $$tmp
	@tmp=$$(mktemp -d); PATH="$(CURDIR)/.venv/bin:$$PATH" IMG_WIDTH=5 IMG_HEIGHT=4 SIM_BUILD=$$tmp COCOTB_RESULTS_FILE=$$tmp/results.xml make -f tb/tests/Makefile.rtl_to_pixels_top; python3 -c 'import shutil,sys; shutil.rmtree(sys.argv[1],ignore_errors=True)' $$tmp
	@tmp=$$(mktemp -d); PATH="$(CURDIR)/.venv/bin:$$PATH" IMG_WIDTH=5 IMG_HEIGHT=4 SIM_BUILD=$$tmp COCOTB_RESULTS_FILE=$$tmp/results.xml make -f tb/tests/Makefile.rtl_to_pixels_top_pipelined; python3 -c 'import shutil,sys; shutil.rmtree(sys.argv[1],ignore_errors=True)' $$tmp
	@tmp=$$(mktemp -d); PATH="$(CURDIR)/.venv/bin:$$PATH" IMG_WIDTH=5 IMG_HEIGHT=4 SIM_BUILD=$$tmp COCOTB_RESULTS_FILE=$$tmp/results.xml make -f tb/tests/Makefile.rtl_to_pixels_top_pipelined_streaming; python3 -c 'import shutil,sys; shutil.rmtree(sys.argv[1],ignore_errors=True)' $$tmp
	@echo CI_SMOKE=PASS
all: lint test-unit test test-real-image formal ppa
clean:
	@python3 -c "import shutil; [shutil.rmtree(n, ignore_errors=True) for n in ('build','obj_dir')]"
