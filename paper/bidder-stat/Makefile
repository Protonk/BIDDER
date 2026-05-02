# Makefile for bidder-stat (the JStatSoft replication archive).
#
# Top-level targets:
#   make venv        bootstrap .venv/ and install pinned requirements
#   make build       compile the C kernel into libbidder.dylib (or .so)
#   make test        run the Python + C test suite (via .venv)
#   make bench-c     build and run the D4 C-direct throughput benchmark
#   make replicate   build, test, run M1-M4 + D4, and the §7 use cases
#   make clean       remove build artefacts (keeps .venv)
#   make distclean   also remove .venv
#
# All Python work runs in .venv/. Versions pinned in requirements.txt
# (numpy, pycryptodome). Run `make venv` once before anything else.

UNAME := $(shell uname -s)
CC ?= cc
CFLAGS ?= -O2 -fPIC

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

SRCS = bidder_opaque.c bidder_root.c generator/bidder.c

ifeq ($(UNAME),Darwin)
TARGET = libbidder.dylib
LDFLAGS = -dynamiclib -install_name @rpath/libbidder.dylib
else
TARGET = libbidder.so
LDFLAGS = -shared
endif

.PHONY: venv build test replicate bench-c use-cases use_case_02 use_case_03 use_case_04 use_case_06 clean distclean

$(VENV)/.installed.stamp: requirements.txt
	@if [ ! -d $(VENV) ]; then \
	    echo "creating $(VENV)"; \
	    python3 -m venv $(VENV); \
	    $(PIP) install --upgrade pip; \
	fi
	$(PIP) install -r requirements.txt
	@touch $(VENV)/.installed.stamp

venv: $(VENV)/.installed.stamp
	@echo "venv ready: $(VENV)"
	@$(PY) -c "import numpy, Crypto; print('  numpy', numpy.__version__); print('  pycryptodome', Crypto.__version__)"

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

build: $(TARGET)

# D4: C-direct throughput benchmark (no ctypes overhead).
# Builds replication/bench_c against libbidder, runs it, and writes
# the markdown results file alongside the other M*_results.md files.
bench-c: build
	$(CC) -O2 -I. -Igenerator replication/bench_c.c $(TARGET) \
	    -Wl,-rpath,@loader_path/.. -Wl,-rpath,$(CURDIR) \
	    -o replication/bench_c
	./replication/bench_c replication/d4_results.md

test: venv build
	@echo "=== Python tests ==="
	$(PY) tests/test_acm_core.py
	$(PY) tests/test_api.py
	$(PY) tests/test_bidder.py
	$(PY) tests/test_bidder_block.py
	$(PY) tests/test_bidder_root.py
	$(PY) tests/test_sawtooth.py
	$(PY) tests/test_speck.py
	@echo "=== Theory tests ==="
	$(PY) tests/theory/test_riemann_property.py
	$(PY) tests/theory/test_quadrature_rates.py
	$(PY) tests/theory/test_fpc_shape.py

use_case_02: venv build
	$(PY) replication/use_case_02_benford_null.py

use_case_03: venv build
	$(PY) replication/use_case_03_cross_validation.py

use_case_04: venv build
	$(PY) replication/use_case_04_fpe.py

use_case_06: venv build
	$(PY) replication/use_case_06_variance_mc.py

use-cases: use_case_02 use_case_03 use_case_04 use_case_06

replicate: venv build test bench-c
	@echo "=== Replication archive: measurements ==="
	./replication/replicate.sh

clean:
	rm -f libbidder.dylib libbidder.so
	rm -f replication/bench_c
	rm -rf replication/bench_c.dSYM
	rm -rf __pycache__ */__pycache__ */*/__pycache__

distclean: clean
	rm -rf $(VENV)
