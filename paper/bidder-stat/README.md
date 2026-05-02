# bidder-stat

Replication archive for the JStatSoft submission *BIDDER: Exact
Leading-Digit Sampling with Keyed Random Access* (working title).

This is the carved subset of the upstream BIDDER repo containing
exactly what the paper needs: `core/` (substrate), `generator/`
(cipher path), `tests/` (proof + property + theory tests), the C
kernel, the Python wrapper, and `replication/` (the measurement
scripts and use-case demonstrations).

## Build, test, replicate

From a clean clone:

```
make venv        # bootstrap .venv/ and install pinned requirements
make build       # compile libbidder.dylib (or .so)
make test        # run the full test suite (Python + theory)
make replicate   # build, test, and run M1-M4 + D4 + use cases
```

`make replicate` produces every figure and table referenced in the
paper.

### Python environment

All Python work runs in `.venv/` against pinned versions in
`requirements.txt`. The minimal set is small on purpose: `numpy`
(measurement scripts and tests) and `pycryptodome` (AES primitive
for the FF1 reference comparator in §7.4 / D1). The kernel itself
has zero C dependencies; the Python wrappers depend only on the
standard library.

`make venv` is idempotent and only re-runs the install when
`requirements.txt` changes. `make distclean` removes `.venv/`.

## C-primary API

The paper presents the C surface (`bidder_root.h`) as the primary
API. The two public functions are:

```c
// Keyed permutation of [0, period).
bdo_block_t * bdo_block_create(uint64_t period,
                                const char *key, size_t key_len,
                                int *err);
int           bdo_block_at(bdo_block_t *b, uint64_t i, uint32_t *out);
uint64_t      bdo_block_period(bdo_block_t *b);
const char *  bdo_block_backend(bdo_block_t *b);   // "speck32" or "feistel"
void          bdo_block_free(bdo_block_t *b);

// First `count` n-primes (multiples of n not divisible by n²) in
// ascending order.
bdo_nprime_t * bdo_nprime_create(uint64_t n, uint64_t count, int *err);
int            bdo_nprime_at(bdo_nprime_t *s, uint64_t i, uint64_t *out);
void           bdo_nprime_free(bdo_nprime_t *s);
```

Full contract in `BIDDER.md` and `core/API.md`. The Python wrapper
`bidder_c_native.py` is a thin ctypes binding example; users
wanting peak throughput call the C kernel directly.

## What's where

| path | contents |
|---|---|
| `core/` | substrate: M_n monoid, n-primes, block-uniformity lemma, Hardy random-access, API surface |
| `generator/` | cipher path: Speck32/64, Feistel fallback, BIDDER block generator, structural Riemann-sum identity |
| `tests/` | unit + property tests for the C and Python paths |
| `tests/theory/` | the three structural-claim tests (Riemann property, quadrature rates, FPC shape) |
| `replication/` | M1–M4 measurement scripts + use-case demonstrations |
| `bidder.py` / `bidder_c_native.py` | Python wrappers (pure-Python and C-backed respectively) |
| `bidder_root.{c,h}` / `bidder_opaque.{c,h}` | top-level C kernel |
| `BIDDER.md` | API contract and usage guide |

## API stability

The C API surface above is the version this paper describes and
will be tagged as `bidder-stat-v1.0` once the JStatSoft submission
is in. Future versions will preserve binary compatibility across
patch releases; minor releases may add to the surface but will not
break existing call sites.

## Test-time contract

`make test` runs:

- `tests/test_*.py` — Python-side unit tests for `bidder.cipher` and
  `bidder.sawtooth` covering input validation, bijectivity, period
  exhaustion, key sensitivity, and C/Python parity.
- `tests/test_acm_core.py` — block-uniformity proofs (the integer
  lemma at `d ∈ {2, 3, 4}` plus the sieved version's smooth family,
  Family E, spread bound, and lucky-cancellation witnesses).
- `tests/theory/` — three structural-claim tests gating §3 / §4
  theorems:
  - `test_riemann_property.py` — `E_P(key) = R` (the §4.4 identity).
  - `test_quadrature_rates.py` — left-rule Euler-Maclaurin rates
    (the quadrature layer for §4.4 / §7).
  - `test_fpc_shape.py` — the FPC layer at `N < P` (the §4.5 shape
    plus the cipher's measured gap from ideal).

## What's *not* here

- The `algebra/` work (Q_n, OGFs, kernel zeros, wonders).
- The probes framework (`experiments/probes/`).
- The acm-flow CF / mult-table empirics.
- The `arguments/` directory.
- Anything touching absolute normality / `μ` / cross-base questions.

These are excluded from the paper's scope; the upstream repo
contains them but they aren't required to build, test, or
replicate this paper.
