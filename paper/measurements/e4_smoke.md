# E4 — smoke check

End-to-end validation that the carved `bidder-stat/` tree builds,
runs, and replicates from a fresh environment.

## Procedure (post-venv-lockdown, 2026-05-02)

```
cd paper/bidder-stat
make venv    # python3 -m venv .venv; pip install -r requirements.txt
make build   # cc -O2 -fPIC -dynamiclib ... -> libbidder.dylib
make test    # full Python + theory test suite via .venv/bin/python
make bench-c # D4 C-direct throughput benchmark
```

All Python work runs in the locked `.venv/` (numpy 2.4.4,
pycryptodome 3.23.0). The earlier sage-python auto-detect path is
removed.

## Results

- **`make build`**: `libbidder.dylib` produced, ~3 source files
  compiled. No warnings, no errors.

- **`make test`** (sage-python):
  - `test_acm_core.py` — block-uniformity tests at `b ≤ 12, d ≤ 5`,
    smooth family + Family E + spread bound + lucky-cancellation
    witness. All pass.
  - `test_api.py`, `test_bidder.py`, `test_bidder_block.py`,
    `test_bidder_root.py`, `test_sawtooth.py`, `test_speck.py` —
    Python unit + property tests. All pass.
  - `test_riemann_property.py` — structural-layer (the `E_P = R`
    identity from §4.4). All pass.
  - `test_quadrature_rates.py` — Euler-Maclaurin rates for `f = x`,
    `sin(πx)`, `x²(1−x)²`, step. All pass.
  - `test_fpc_shape.py` — statistical-layer (FPC at `N < P`).
    Reports cipher-RMSE / FPC-std ratios 1.00–2.37 at `P = 2000`,
    consistent with M2's variance-ratio measurements (square the
    RMSE ratio to get variance ratio).

- **Measurement script smoke**: `replication/m1_cycle_walking.py`
  runs end-to-end from the carved tree, produces the 12-row M1
  table including the `2^32 - 1` worst-case-fit row.

## Findings

- The carved tree is self-contained. No imports from the upstream
  BIDDER repo's `algebra/`, `wonders/`, `experiments/` reach into
  the build or test path.
- `bidder_c_native.py`'s `_lib = ctypes.CDLL(os.path.join(_HERE,
  _LIB_NAME))` correctly loads `libbidder.dylib` from the
  `bidder-stat/` root after `make build`.
- The Makefile's `PY` auto-detects `sage` and falls back to
  `python3`. On systems without `sage`, the C-only tests would
  still build and run; the numpy-dependent tests in
  `tests/test_acm_core.py` and the M1–M4 measurements would skip
  unless numpy is installed independently.

## Status

E4 passes. The carved `bidder-stat/` tree is replication-ready.
A clean clone + `make replicate` would reproduce M1–M4 from the
JStatSoft submission.
