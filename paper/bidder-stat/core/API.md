# BIDDER core API

The user-facing reference for the period-only BIDDER API. Each
function appears in three layers:

- **Natural language** — what the function does, in user terms.
- **Python** — the actual signature and a runnable example, against
  the implementation in `core/api.py` and `generator/bidder_block.py`.
- **BQN** — a representation of what the call corresponds to in the
  ACM-Champernowne world. The BQN is documentation of the math layer
  the API sits on top of, not metadata returned by any call. The
  cipher itself is out of scope for BQN per `BQN-AGENT.md`.

For the proofs that back the math, see
`core/BLOCK-UNIFORMITY.md` and `core/HARDY-SIDESTEP.md`.


## Overview

The core API is two names: `fulfill` and `BidderBlock`. You ask
`fulfill` for a keyed permutation of `[0, period)` and you get back a
`BidderBlock` whose `.at(i)` returns the i-th element of that
permutation in `O(log period)` cipher work. The `BidderBlock` is
stateless from the caller's view — random access, fresh iteration,
no cursor.

What the API does **not** do, in v1: certify leading-digit
uniformity in any base, search a `(b, n, d)` catalogue, compose
blocks, or accept periods larger than `2^32 - 1`. See "What is not
yet supported" at the bottom.


## Quick start

```python
# Make sure core/ is on sys.path before this import. The repo is not
# packaged; the convention is sys.path.insert(0, '<path-to>/core').
from api import fulfill

B = fulfill(period=10, key=b'doc')
print(B.period)        # 10
print(B.at(0))         # 0
print(list(B))         # [0, 4, 8, 1, 7, 6, 9, 3, 2, 5]
```

A `BidderBlock` of period 10 keyed by `b'doc'`. The output is a
specific permutation of `[0, 10)` determined by the key.


## The primitive: `BidderBlock`

A keyed permutation of `[0, period)`. Stateless random access via
`at(i)`; iterable; no cursor.

### Construction

`BidderBlock(period, key)` builds the permutation. `period` must be
an integer in `[2, MAX_PERIOD_V1]`; `key` must be `bytes` or
`bytearray`. Construction is `O(log period)` work.

**Python.**

```python
class BidderBlock:
    def __init__(self, period: int, key: bytes) -> None: ...
```

```python
from api import BidderBlock

B = BidderBlock(period=10, key=b'doc')
```

**BQN.**

In ACM-Champernowne notation, `BidderBlock(P, key)` corresponds to a
keyed permutation of the integer block at the `d=1` case of the
integer-block lemma in `core/BLOCK-UNIFORMITY.md`. With `b = P+1`
and `d = 1`, the integer-block expression is

```bqn
b⋆d-1 + ↕ (b-1)×b⋆d-1
```

which substitutes to

```bqn
1 + ↕ P
```

— the integers `⟨1, 2, …, P⟩`. The `BidderBlock` adapter shifts the
output range from `{1, …, P}` to `[0, P)` by subtracting 1, so the
set being permuted is, externally,

```bqn
↕ P
```

The keying picks one specific permutation of this set. BQN does not
model which one; the cipher is out of scope per
`BQN-AGENT.md`.


### Random access: `at(i)`

Return the i-th element of the permutation. Stateless: no cursor,
no internal counter, no order dependency. Constant amortized work
per call (one cipher invocation plus a fixed number of cycle-walk
retries).

**Python.**

```python
class BidderBlock:
    def at(self, i: int) -> int: ...
```

```python
from api import BidderBlock

B = BidderBlock(period=100, key=b'doc')

B.at(0)    # 20
B.at(50)   # 13
B.at(99)   # 1
B.at(25)   # 70
B.at(73)   # 29
```

`at(i)` raises `ValueError` for `i ∉ [0, period)` and `TypeError`
for non-integer indices (`float`, `str`, `None`, etc.). Booleans
pass through as `int` per Python's `__index__` convention.

**BQN.**

The corresponding operator is dyadic pick. For any list `L` that
is a permutation of `↕ P`, the i-th element is

```bqn
i ⊑ L
```

`at(i)` is exactly that operator applied to whichever permutation
of `↕ P` the key selects. BQN does not represent the keyed
permutation itself — the cipher is out of scope per
`BQN-AGENT.md` — but the operator that the API exposes is
just `⊑`.


### Iteration

`BidderBlock` is iterable but **not** its own iterator. Each call
to `iter(B)` returns a fresh independent generator over `[0, period)`,
walking the underlying `at(i)` from `0` to `period - 1`. Two
simultaneous loops over the same block do not share state.

**Python.**

```python
class BidderBlock:
    def __iter__(self) -> Iterator[int]: ...
```

```python
from api import BidderBlock

B = BidderBlock(period=10, key=b'doc')

# list(B) walks 0..period-1 via at(i)
list(B)                # [0, 4, 8, 1, 7, 6, 9, 3, 2, 5]

# iter(B) is fresh each call: two independent walks
it1 = iter(B)
it2 = iter(B)
next(it1), next(it2)   # (0, 0)   — both at index 0
next(it1), next(it2)   # (4, 4)   — both at index 1
```

`next(B)` itself raises `TypeError`: `BidderBlock` is iterable, not
an iterator. There is no `reset()` method, because there is no
object-level cursor to reset.

**BQN.**

In BQN there is no separate "iteration" concept; a list is its own
sequence. For any length-P list `L`, the iteration of `L` is just
`L`, and its length is

```bqn
≠ L
```

`iter(B)` corresponds to walking the keyed permutation of `↕ P`
end-to-end. BQN does not name the permutation, but `≠ L = P` is
what `len(B)` returns.


### Properties

**Python.**

```python
class BidderBlock:
    @property
    def period(self) -> int: ...
    @property
    def cipher(self) -> str: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
```

| Python      | Returns                                  | BQN analog                                          |
|-------------|------------------------------------------|-----------------------------------------------------|
| `B.period`  | the requested period `P`                 | `≠ L` for any list `L` of length `P`                |
| `len(B)`    | the requested period `P`                 | `≠ L`                                               |
| `B.cipher`  | `'speck32'` or `'feistel'`               | (no analog — diagnostic, not part of the contract)  |
| `repr(B)`   | `BidderBlock(period=P, cipher=...)`      | (no analog)                                         |


### Errors

| Exception                  | Cause                                                             | BQN analog                                                          |
|----------------------------|-------------------------------------------------------------------|---------------------------------------------------------------------|
| `TypeError`                | `period` not `int`; `key` not `bytes`/`bytearray`; `at(i)` non-integer index | (no analog — Python runtime type system)                  |
| `ValueError` (range)       | `at(i)` index out of `[0, period)`                                | `i ⊑ L` is undefined for `i ∉ ↕ ≠L` (BQN raises an index error)     |
| `ValueError` (degenerate)  | `period < 2`                                                      | the integer block `1 + ↕ P` collapses for `P < 2`; the API rejects it |
| `UnsupportedPeriodError`   | `period > MAX_PERIOD_V1`. `ValueError` subclass                   | BQN imposes no upper bound on `P`; the cap is cipher-side           |

`UnsupportedPeriodError` is mathematically unrelated to
ACM-Champernowne — the math allows arbitrarily large periods. The
exception reflects a limit of the v1 cipher backend, not of the
lemma. See `MAX_PERIOD_V1` below.


## The orchestrator: `fulfill`

The public entry point. In v1 it is a single-line wrapper around
`BidderBlock(period, key)`; the constructor handles all validation
and refusal. `fulfill` exists as the named entry point so that
future composition / catalogue work can extend it without changing
caller code.

**Python.**

```python
def fulfill(period: int, key: bytes) -> BidderBlock: ...
```

```python
from api import fulfill

B = fulfill(period=10, key=b'doc')
B.period       # 10
B.at(0)        # 0
```

**BQN.**

`fulfill` is mathematically transparent in v1: it returns the same
`BidderBlock` as direct construction, so the BQN representation is
identical to `BidderBlock(period, key)`. See the construction
section above.


## Constants and exceptions

### `MAX_PERIOD_V1`

**Python.**

```python
MAX_PERIOD_V1: int   # 4294967295
```

```python
from api import MAX_PERIOD_V1

MAX_PERIOD_V1   # 4294967295  ( = 2**32 - 1)
```

**BQN.**

```bqn
(2⋆32) - 1
# 4294967295
```

The largest period the v1 cipher backend supports. The bound is not
arbitrary: `BidderBlock(period, key)` is implemented as
`Bidder(base=period+1, digit_class=1, key)` from
`generator/bidder.py`, and that legacy primitive caps `base` at
`2^32` (see `generator/AGENTS.md`, "Feature set"). With `digit_class
= 1`, the largest legal `base` is `2^32`, which gives a maximum
`period` of `2^32 - 1`.

The math layer imposes no analogous bound — the integer-block lemma
in `core/BLOCK-UNIFORMITY.md` and the Hardy closed form in
`core/HARDY-SIDESTEP.md` work for any `P`. Lifting the cap is a
backend question — wider cipher variants in `generator/`, or the
deferred CRT composition path described in "What is not yet
supported."

### `UnsupportedPeriodError`

A `ValueError` subclass raised when the requested period is in the
mathematically valid range (`>= 2`) but exceeds the v1 cipher
backend.

**Python.**

```python
class UnsupportedPeriodError(ValueError): ...
```

```python
from api import fulfill, UnsupportedPeriodError

try:
    fulfill(period=2**32, key=b'doc')
except UnsupportedPeriodError as e:
    print(e)
    # period 4294967296 exceeds maximum of 4294967295
```

Catching `ValueError` also works (it is the parent class), but
`UnsupportedPeriodError` lets callers distinguish "the math is fine,
the cipher backend cannot handle it" from "the request was
invalid."

**BQN.**

In BQN there is no analogous exception; the math layer accepts any
`P ≥ 2`. The exception is purely a property of the cipher backend
and signals only that the v1 implementation has run out of cipher
width.


## What is happening in ACM-Champernowne world

The API call `BidderBlock(P, key)` selects a single point on the
parameter lattice of the integer-block lemma in
`core/BLOCK-UNIFORMITY.md`. This section names that point precisely
in BQN.

**Lattice point.** With base `b = P + 1` and digit class `d = 1`,
the integer block in BQN is

```bqn
b⋆d-1 + ↕ (b-1)×b⋆d-1
```

which evaluates to

```bqn
1 + ↕ P
```

That is, the integers `⟨1, 2, …, P⟩`. Every integer in this block
is a single base-`(P+1)` digit and is its own leading digit. The
integer-block lemma's per-leading-digit count `b⋆d-1` evaluates to
`(P+1)⋆0 = 1`, so each of the `P` leading digits appears exactly
once. This is the trivial degenerate case of the lemma — exact
uniformity is automatic.

**The shift.** The `BidderBlock` adapter subtracts 1 from each
output, mapping `{1, …, P}` to `[0, P)`. Externally the set being
permuted is

```bqn
↕ P
```

**The permutation.** The keying picks one bijection from the
symmetric group on `↕ P`. BQN does not represent which one — the
cipher is out of scope per `BQN-AGENT.md`'s hard boundary.
For the BQN-side reader, the API's contract is purely "a
permutation of `↕ P`."

**Random access.** `at(i)` is one Python call into the cipher,
which runs constant-amortized cycle-walked Speck32/64 (or Feistel
for small blocks). The cost story is the same shape as the closed
form `NthNPn2` from `core/HARDY-SIDESTEP.md`:

```bqn
NthNPn2 ← {𝕨 × 1 + ((𝕨-1)|𝕩-1) + 𝕨 × ⌊(𝕩-1)÷𝕨-1}
```

— `O(log period)` bit operations on a stateless input. The
difference: `NthNPn2` is the math layer's analog (random access into
the n-prime sequence of one monoid) and is not actually invoked by
the v1 API. `BidderBlock.at(i)` runs the cipher; `NthNPn2` is the
mathematical conscience that says "polylog-time random access is the
right cost story for problems of this shape."

**What we are not yet using.** The proofs in
`core/BLOCK-UNIFORMITY.md` and `core/HARDY-SIDESTEP.md` cover much
more than the `d=1` integer block. Specifically:

- The smooth-family lemma (`n² | b^(d-1)` ⇒ exact uniform n-primes
  in the block) and the Family E lemma (`b^(d-1) ≤ n ≤ ⌊(b^d−1)/(b−1)⌋`
  ⇒ one n-prime per leading digit) define a much richer parameter
  lattice that the v1 API does not visit. Both lemmas live alongside
  the integer lemma in `core/BLOCK-UNIFORMITY.md`. The n-prime
  BIDDER variant that would use them is not built — see "What is
  not yet supported."
- `NthNPn2` from `core/HARDY-SIDESTEP.md` gives O(1) bignum random
  access into the K-th n-prime of any monoid `nZ+` for `n ≥ 2`.
  The v1 API does not invoke this either, because v1 permutes
  contiguous integers, not n-primes. The closed form is the math
  the n-prime variant would inherit.

**Underneath.** `BidderBlock` is a Python adapter; the cipher work
goes through `Bidder.at(i)` in `generator/bidder.py` (with a C twin
in `generator/bidder.c`). That random-access method is the only new
feature added to the legacy class to support `BidderBlock`. See
`generator/bidder.py` and `generator/bidder.h` for the entry points;
see `generator/AGENTS.md` for the parity rules.


## Examples

### Example 1: build and iterate

```python
from api import fulfill

B = fulfill(period=10, key=b'doc')

print(B.period)             # 10
print(list(B))              # [0, 4, 8, 1, 7, 6, 9, 3, 2, 5]
print(sorted(list(B)))      # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

The third print confirms the output is a permutation of `[0, 10)`:
every element appears exactly once.

### Example 2: random access

```python
from api import fulfill

B = fulfill(period=100, key=b'doc')

# Pull elements out of order — the cost is the same as sequential access.
B.at(0)     # 20
B.at(50)    # 13
B.at(99)    # 1
B.at(25)    # 70
B.at(73)    # 29
```

### Example 3: two independent iterators

```python
from api import fulfill

B = fulfill(period=10, key=b'doc')

it1 = iter(B)
it2 = iter(B)

next(it1), next(it2)   # (0, 0)   — both yield B.at(0)
next(it1), next(it2)   # (4, 4)   — both yield B.at(1)
```

`iter(B)` returns a fresh generator each call. The two iterators
share no state, so `it1` and `it2` walk the period independently.

### Example 4: refusal at the cipher backend cap

```python
from api import fulfill, UnsupportedPeriodError

try:
    fulfill(period=2**32, key=b'doc')
except UnsupportedPeriodError as e:
    print(e)
    # period 4294967296 exceeds maximum of 4294967295
```

The math allows `period = 2^32`, but the v1 cipher backend caps at
`2^32 - 1`. Future work (CRT composition or a wider cipher) would
lift this.


## What is not yet supported

| Item                              | Why deferred                                                          |
|-----------------------------------|-----------------------------------------------------------------------|
| Periods `> 2^32 - 1`              | Cipher backend cap. Needs wider Speck or CRT composition.             |
| CRT composition (`CRTComposite`)  | Lemma not yet written. Will live in `core/COMPOSITION.md`.            |
| Alphabet-pinned mode              | Out of v1 scope; needs a `(b, n, d)` catalogue search.                |
| n-prime BIDDER variant            | Math is in `core/BLOCK-UNIFORMITY.md` + `core/HARDY-SIDESTEP.md`; cipher path not built. |
| Statistical-uniformity (`'iid'`)  | No use case yet.                                                      |

The math machinery in `core/BLOCK-UNIFORMITY.md` and
`core/HARDY-SIDESTEP.md` is ready for the n-prime variant; only the
cipher-side construction is missing. The CRT composition path is
the only deferred item that requires a new proof (one paragraph,
elementary, sketched in earlier conversations).


## See also

- `core/BLOCK-UNIFORMITY.md` — the integer-block lemma (cited above
  at `d=1`), the smooth and Family E sieved lemmas, the spread bound.
- `core/HARDY-SIDESTEP.md` — the closed form `NthNPn2` for the K-th
  n-prime of monoid `nZ+`.
- `core/ACM-CHAMPERNOWNE.md` — the construction of the
  n-Champernowne reals.
- `core/ABDUCTIVE-KEY.md` — the rank-1 lemma and the
  leaky-parameterization theme.
- `BQN-AGENT.md` — canonical BQN names used in this doc.
- `generator/AGENTS.md` — cipher feature set and parity rules.
- `generator/BIDDER.md` — cipher design notes and findings.
