# Makefile for bidder-stat (the JStatSoft replication archive).
#
# Top-level targets:
#   make build       compile the C kernel into libbidder.dylib (or .so)
#   make test        run the Python + C test suite
#   make replicate   build, test, and run all six use cases for §7
#   make clean       remove build artefacts
#
# The replication archive contains a single carved subset of the
# upstream BIDDER repo: core/ + generator/ + tests/ + the C kernel +
# the Python wrapper. The paper's measurements (M1-M4) live in
# replication/; the use cases (§7.1-§7.6) also live there.

UNAME := $(shell uname -s)
CC ?= cc
CFLAGS ?= -O2 -fPIC

# Use sage -python when available (per AGENTS.md in upstream repo) so
# numpy + matplotlib are on the path for tests and replications. Fall
# back to plain python3 for environments without sage.
HAS_SAGE := $(shell command -v sage >/dev/null 2>&1 && echo yes)
ifeq ($(HAS_SAGE),yes)
PY = sage -python
else
PY = python3
endif

SRCS = bidder_opaque.c bidder_root.c generator/bidder.c

ifeq ($(UNAME),Darwin)
TARGET = libbidder.dylib
LDFLAGS = -dynamiclib -install_name @rpath/libbidder.dylib
else
TARGET = libbidder.so
LDFLAGS = -shared
endif

.PHONY: build test replicate clean

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

build: $(TARGET)

test: build
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

replicate: build test
	@echo "=== Replication archive: measurements ==="
	./replication/replicate.sh

clean:
	rm -f libbidder.dylib libbidder.so
	rm -rf __pycache__ */__pycache__ */*/__pycache__
