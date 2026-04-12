# Dual release plan

Ship `bidder` as two independent artifacts from the same repo.
Same contract, same test fixtures, different runtimes.

```
dist/
    bidder/          ← pure Python (existing)
    bidder_c/        ← C library + ctypes wrapper (new)
```


## What already exists

The C implementation is written and tested:

| Layer | C source | Python twin | Cross-check |
|-------|----------|-------------|-------------|
| Speck32/64 | `generator/bidder.c` | `generator/coupler.py` | Hardcoded vectors in both test suites |
| Cycle-walking | `generator/bidder.c` | `generator/coupler.py` | `test_at_crosscheck_{feistel,speck}()` |
| Period-only cipher | `bidder_root.c` | `bidder_block.py` + `api.py` | `test_bidder_root_c.c` ↔ `test_bidder_root.py` |
| Sawtooth closed form | `bidder_root.c` | `sawtooth.py` | Python-computed fixtures in C tests |
| n-prime sieve | `core/acm_core.c` | `core/acm_core.py` | Mirrored test suites |

What does not exist: a shared library build, an opaque C API, a
ctypes wrapper, a `dist/bidder_c/` output from `build.py`, or any
documentation telling a consumer how to use the C path.


### Sawtooth input and output range

Both packages will enforce the same bounds:

- **Inputs:**
  - `n` must be representable as `uint64_t` (at most `2^64 − 1`).
  - `count` must be at most `sys.maxsize` (`2^63 − 1` on 64-bit
    platforms). This is tighter than `uint64_t` because
    `NPrimeSequence.__len__` returns `count`, and `len()` returns
    `Py_ssize_t`, which overflows above `sys.maxsize`. Capping
    `count` here keeps `len()` total across the full valid range.
  - `K` (the index passed to `.at()`) must satisfy `K < count`,
    so `K` is also bounded by `sys.maxsize − 1`.

  Python currently accepts arbitrary-size ints for all three;
  this narrows the input contract. BIDDER.md's "there is no upper
  bound on n or on count" becomes "n must be at most `2^64 − 1`;
  count must be at most `sys.maxsize`."

- **Outputs:** With these input bounds, the closed form
  `n * (K + q + 1)` where `q = K // (n − 1)` has a provable
  maximum of `(2^64 − 1) × (2^64 + 1) = 2^128 − 1` (achieved at
  the widest input combination). The output always fits in 128
  bits. No `OverflowError` path is needed on the output side; the
  math guarantees it.

- **C implementation:** computes in `__int128` (available on
  GCC/Clang arm64) to avoid premature overflow on intermediates.
  Returns the result as a `(lo, hi)` pair of `uint64_t`.

- **Python implementation:** computes in native bignum (always
  exact). Adds input checks: `n.bit_length() > 64` →
  `OverflowError`; `count > sys.maxsize` → `OverflowError`. The
  output `bit_length()` check is present for defense but never
  triggers with valid inputs.

- **Max-range fixture:** `sawtooth(2^64 − 1, 2^63 − 1).at(2^63 − 2)`
  Both packages must return the same value. The C side returns
  `(lo, hi)`. The ctypes wrapper reconstructs `(hi << 64) | lo`.
  The Python side returns the same Python `int`.

Zero behavioral difference on any valid input.


## Build steps

### Step 0. Opaque C API shim

The current C API is struct-based: `bidder_block_ctx` embeds
`bidder_ctx`, which contains a 22-element round-key array, Feistel
key arrays, mode flags, and a counter. Reproducing these layouts
in ctypes is fragile — any field reorder or resize silently
corrupts memory.

Add a thin opaque API in a new file `bidder_opaque.c` /
`bidder_opaque.h`. All exported symbols use the `bdo_` prefix to
avoid collision with the existing `bidder_block_at` etc. in
`bidder_root.c` (both files link into the same `libbidder`):

```c
// bidder_opaque.h — opaque FFI surface for libbidder
typedef struct bdo_block bdo_block;
typedef struct bdo_nprime bdo_nprime;

bdo_block  *bdo_block_create(
    uint64_t period, const uint8_t *key, size_t key_len, int *err);
void        bdo_block_free(bdo_block *h);
uint32_t    bdo_block_at(const bdo_block *h, uint64_t i, int *err);
uint64_t    bdo_block_period(const bdo_block *h);
const char *bdo_block_backend(const bdo_block *h);

bdo_nprime *bdo_nprime_create(uint64_t n, uint64_t count, int *err);
void        bdo_nprime_free(bdo_nprime *h);
int         bdo_nprime_at(const bdo_nprime *h, uint64_t i,
                          uint64_t *out_lo, uint64_t *out_hi);
uint64_t    bdo_nprime_n(const bdo_nprime *h);
uint64_t    bdo_nprime_count(const bdo_nprime *h);
```

Each `_create` function heap-allocates the real struct internally
and returns an opaque pointer. The ctypes wrapper sees only
`c_void_p`. No struct layout crosses the FFI boundary. If the
internal layout changes, only `bidder_opaque.c` must be recompiled;
the Python wrapper is untouched.

`bdo_nprime_at` computes in `__int128` and splits the result into
`(lo, hi)`. With `uint64_t` inputs this never overflows 128 bits,
but a defensive check returns `BIDDER_ROOT_ERR_OVERFLOW` if it
somehow does.

Error codes are the existing `BIDDER_ROOT_ERR_*` enum, returned
via an `int *err` out-parameter. `_create` returns `NULL` on
failure.

This is ~80 lines of C. It calls the existing `bidder_root.c`
functions internally; no duplication of cipher logic.


### Step 1. Makefile for the shared library

A single `Makefile` at the repo root that produces `libbidder.dylib`
(macOS) or `libbidder.so` (Linux) from:

```
bidder_opaque.c
bidder_root.c
generator/bidder.c
```

No external dependencies. No autoconf. No cmake.

macOS (arm64, primary target):

```make
libbidder.dylib: bidder_opaque.c bidder_root.c generator/bidder.c
	cc -O2 -dynamiclib -fPIC \
	   -install_name @rpath/libbidder.dylib \
	   -o $@ $^
```

Linux fallback:

```make
libbidder.so: bidder_opaque.c bidder_root.c generator/bidder.c
	cc -O2 -shared -fPIC -o $@ $^
```

The `Makefile` detects `uname -s` and picks the right target.

Output: `libbidder.dylib` (or `.so`) in the repo root (gitignored).

`core/acm_core.c` is NOT included. It contains sieve and
Champernowne utilities, not part of the shipped API.


### Step 2. ctypes wrapper

A single Python file `_native.py` inside `dist/bidder_c/` that:

1. Loads `libbidder.dylib` (or `.so`) from the same directory as
   `_native.py` via `ctypes.CDLL(os.path.join(HERE, 'libbidder...'))`.
   The library ships adjacent to the wrapper — no `DYLD_LIBRARY_PATH`,
   no loader-path games.
2. Calls the opaque API (`bdo_block_create`, `bdo_block_at`,
   `bdo_block_free`, etc.) through `c_void_p` handles. No struct
   layout is reproduced in Python.
3. Wraps `bdo_block_*` into a `BidderBlock` class with the same
   interface as the Python one (`.at(i)`, `.period`, `__iter__`,
   `__len__`, `__repr__`). The handle is freed in `__del__`.
4. Wraps `bdo_nprime_*` into an `NPrimeSequence` class with the
   same interface. `.at()` receives `(lo, hi)` and returns
   `(hi << 64) | lo` as a Python `int`.
5. Exposes `cipher(period, key)` and `sawtooth(n, count)` at
   module level.
6. Raises the same exceptions (`TypeError`, `ValueError`,
   `UnsupportedPeriodError`) with the same messages. Type checking
   and message formatting happen in Python; the C library returns
   error codes which the wrapper translates.
7. Validates all integer arguments before crossing the FFI
   boundary: `period` and `n` must fit in `uint64_t`; `count`
   must be at most `sys.maxsize`; `.at(i)` and `.at(K)` indices
   must fit in `uint64_t`. Without these guards, oversized Python
   ints would silently truncate in ctypes.

The wrapper is ~150-200 lines. It does no math.


### Step 3. Extend build.py

Add a second output path to `build.py`. The build now produces:

```
dist/
    bidder/           ← existing, unchanged except sawtooth input cap
    bidder_c/
        __init__.py   ← imports from _native, same public surface
        _native.py    ← ctypes wrapper (no source rewriting needed)
        libbidder.dylib  ← copied from repo root after `make`
        BIDDER.md     ← same user guide
```

`build.py` copies `_native.py` as-is (no import rewriting needed —
it uses only stdlib `ctypes` and `os`). It copies the compiled
`libbidder.dylib` from the repo root into the package directory.
If the library doesn't exist (user hasn't run `make`), `build.py`
prints a warning and skips the `bidder_c` output, but still builds
`bidder/` successfully.

The Python `sawtooth.py` gains an input cap (n and count must fit
in `uint64_t`). This is a source-level change applied by
`build.py`'s existing edit mechanism.


### Step 4. Contract test suite

A single test file `tests/test_dual_parity.py` that runs both
packages in **subprocesses with controlled PYTHONPATH and cwd**.

Why subprocesses: the repo root contains `bidder.py`, which shadows
`dist/bidder/` on any sys.path that includes the repo root. Bare
`import bidder` from the test runner would get the wrong module.

Why controlled cwd: Python adds the working directory (or `''`) to
`sys.path[0]` for `-c` scripts. If cwd is the repo root,
`bidder.py` is found there regardless of `PYTHONPATH`. The
subprocess must run with **cwd set to `dist/`**, not the repo root.

```python
DIST = os.path.join(REPO_ROOT, 'dist')

def run_in_dist(code: str) -> str:
    """Run a Python snippet in dist/, importing only shipped packages."""
    result = subprocess.run(
        [sys.executable, '-c', code],
        cwd=DIST,
        env={**os.environ, 'PYTHONPATH': DIST},
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()
```

With `cwd=DIST` and `PYTHONPATH=DIST`, `sys.path[0]` is `dist/`
and `import bidder` resolves to `dist/bidder/__init__.py`. The root
`bidder.py` is never on the path.

Test table:
- Cipher: 10 `(period, key, i)` triples spanning Feistel and
  Speck backends, small and large periods.
- Sawtooth: the 7 fixtures from the C cross-check test, plus the
  max-range anchor: `sawtooth(2^64 − 1, 2^64 − 1).at(2^64 − 2)`
  = `2^128 − 1`.
- Full-permutation: `list(bidder.cipher(P, K)) == list(bidder_c.cipher(P, K))`
  for periods 10, 100, 1000.
- Exception parity: both raise `TypeError` for `period=True`,
  `ValueError` for `period=1`, `UnsupportedPeriodError` for
  `period=2**32`.
- Input cap: both `bidder.sawtooth(1 << 65, 1)` and
  `bidder_c.sawtooth(1 << 65, 1)` raise `OverflowError`
  (n exceeds `uint64_t`). Both `bidder.sawtooth(2, sys.maxsize + 1)`
  and `bidder_c.sawtooth(2, sys.maxsize + 1)` raise `OverflowError`
  (count exceeds `sys.maxsize`).


### Step 4b. Update existing test suites

The contract change (input caps on sawtooth) invalidates some
existing tests. These must be updated in the same step as the
contract change, not deferred to a later "run the full suite"
pass:

- `tests/test_bidder_root_c.c`: the test at line ~237 asserts
  that `sawtooth(UINT64_MAX, 2).at(1)` returns
  `BIDDER_ROOT_ERR_OVERFLOW`. Under the new contract this is a
  valid call returning `2^65 − 2`. Rewrite to expect success and
  check the `(lo, hi)` value. Add the max-range fixture.

- `tests/test_sawtooth.py`: add assertions for the new input cap
  (`n > 2^64 − 1` → `OverflowError`, `count > sys.maxsize` →
  `OverflowError`). These run against the source-tree
  `sawtooth.py`, not the built artifact, so they catch drift
  before `build.py` even runs.

- `tests/test_bidder_root.py`: same input-cap assertions for the
  Python root entry point.

If these tests are not updated before running the full suite in
step 7, the suite will fail and obscure real issues.


### Step 5. Documentation

**BIDDER.md § Performance** (already written): add a paragraph:

> A C implementation with the same contract is available as
> `bidder_c`. It requires compilation (`make`) and exposes the same
> `cipher` and `sawtooth` functions. The C path is roughly 1000x
> faster for `.at()` throughput.

**BIDDER.md § sawtooth:** change "There is no upper bound on `n` or
on `count`" to:

> `n` must be at most `2^64 − 1`. `count` must be at most
> `sys.maxsize` (typically `2^63 − 1`). The result of `.at(K)` is
> exact for all valid inputs.

**AGENTS.md** (already has performance note): add:

> The C implementation lives at `bidder_root.c` +
> `generator/bidder.c`, with an opaque FFI layer in
> `bidder_opaque.c`. Build with `make`. The shared library is
> consumed by `dist/bidder_c/` via ctypes. If you modify the cipher
> backend, you must update both `generator/coupler.py` (Python) and
> `generator/bidder.c` (C), then run `tests/test_dual_parity.py`.


## What does NOT change

- The C source files (`bidder_root.c`, `generator/bidder.c`,
  `generator/bidder.h`, `bidder_root.h`) stay where they are.
  No reorganization.
- The existing C test files stay where they are and keep working
  independently of the dual release.
- `BIDDER.md` remains the single source of truth for the contract.
  Both packages ship the same copy and have identical behavior.

## What does change in dist/bidder/

- `sawtooth.py` gains input caps: `n` must fit in `uint64_t`;
  `count` must be at most `sys.maxsize`. This is a contract
  narrowing. No shipped example or recipe uses values above these
  caps. The `hardy_sidestep.py` demo of `nth_n_prime(2, 2**4096)`
  remains in the repo as a research curiosity but is no longer a
  property of the shipped package.
- The `count` cap at `sys.maxsize` (not `uint64_t`) ensures
  `len(S)` remains total. `Py_ssize_t` overflows above
  `sys.maxsize`; capping `count` there keeps `__len__` in the
  contract for the full valid range.


## Execution order

1. Write `bidder_opaque.c` / `bidder_opaque.h` (opaque API shim
   with `bdo_` prefix). Verify it compiles and the opaque functions
   produce the same values as the struct-based API.
2. Write the `Makefile`. Build `libbidder.dylib`. Verify symbols
   are visible with `nm -gU`.
3. Write `_native.py`. Smoke-test `cipher` and `sawtooth` against
   the shared library by hand.
4. Add input caps to `sawtooth.py` (`n` ≤ `uint64_t`, `count` ≤
   `sys.maxsize`). Add the corresponding edit to `build.py` so
   `dist/bidder/` reflects it.
5. Update existing tests to match the new contract (step 4b):
   rewrite the C overflow test, add input-cap assertions to
   `test_sawtooth.py` and `test_bidder_root.py`. Run the full
   existing suite. All tests must pass before proceeding.
6. Extend `build.py` to emit `dist/bidder_c/` (with the `.dylib`
   copied adjacent).
7. Write `tests/test_dual_parity.py` (subprocess-isolated, cwd =
   `dist/`). Run it. Fix any disagreements.
8. Update docs: BIDDER.md, AGENTS.md.
9. Gitignore `libbidder.*` and `dist/bidder_c/`.


## Why now

The C is written. The fixtures are pinned. The parity matrix is
clean (last gap closed today). Shipping the dual release while
everything is fresh costs an opaque shim, a Makefile, a ctypes
wrapper, and a subprocess-isolated contract test. Shipping it later
means backfilling under pressure when someone actually needs the
speed, with stale fixtures and a drifted codebase.

The Python package is the contract. The C library is the
instrument. The opaque API is the stable ABI. The contract test
is the bridge.
