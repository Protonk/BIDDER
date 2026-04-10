# API Plan

A small, honest API for requesting BIDDER blocks by period only.

## Goal

The user asks for an integer `P` and a key, and receives an object
that exposes a keyed permutation of `[0, P)` via random access. The
i-th output is computed in `O(log P)` cipher operations, with no
ordering or cursor state required. The user can iterate, index,
parallelize, or compose at the call site.


## Decisions made in the thread that produced this plan

1. **`at(i)` is the load-bearing primitive.** `BidderBlock` is
   iterable but **not its own iterator**: `__iter__` returns a fresh
   independent generator over `at(i)` each time it is called, and
   there is **no `__next__`** on the object, no internal counter,
   and no `reset()`. Consumers who want stateful counter semantics
   build them on top of `at(i)` themselves. See the primitive sketch
   and tests below for the locked-in contract.
2. **Out-of-range raises.** Calling `at(i)` with `i ∉ [0, period)`
   raises `ValueError`. Wrap-around is the consumer's problem; if they
   want it, `at(i % period)` is one line.
3. **Period-only mode.** No alphabet pinning. The user asks for a
   period; the output is an integer in `[0, period)`. There is no
   leading-digit guarantee in this mode and no `(b, n, d)` to choose.
4. **Composition is deferred** until the CRT lemma is proved (sketch
   below). Until then `fulfill` only assembles single-block constructions.
5. **v1 supported period range is `[2, 2^32 − 1]`.** This is the limit
   of the existing cipher backend in `generator/bidder.py` and
   `generator/bidder.c` (`base ≤ 2^32`, `block_size ≤ 2^32`). v1
   delivers any period in this range and **refuses any period outside
   it** with an `UnsupportedPeriodError`. Lifting the upper bound is a
   backend extension (wider Speck variants or a wide-block Feistel),
   not a math change. The refusal path exists from day one — it is not
   gated on the future composition lemma.


## What this API is not

- It does not certify leading-digit uniformity in any base. The math
  in `core/BLOCK-UNIFORMITY.md` is not load-bearing for period-only
  mode — it is the certification layer for *future* alphabet-pinned
  mode and for the n-prime BIDDER variant.
- It does not search a `(b, n, d)` catalogue. There is nothing to
  search in period-only mode.
- It does not compose blocks. Composition needs the CRT lemma below.
- It does not pick a Speck variant by mathematical necessity — only
  by cipher implementation budget. That choice lives in the cipher
  layer, not in the math layer.
- It is **not period-unbounded.** v1 caps at `2^32 − 1` because the
  existing cipher backend caps there. Any larger period raises
  `UnsupportedPeriodError`. Lifting the cap requires either a wider
  cipher backend (out of v1 scope) or the deferred CRT composition.


## Layer cake

```
+----------------------------------------+
|  core/api.py                            |  fulfill(period, key)  -> BidderBlock
|  (validation, refusal, future orchestration)
+----------------------------------------+
|  generator/bidder_block.py              |  BidderBlock(period, key)
|  (Python-only adapter; period -> base)  |    .at(i)               primitive
|                                         |    .__iter__            fresh iter
|                                         |    .period
+----------------------------------------+
|  generator/bidder.py     (existing+)    |  Bidder(base, digit_class, key)
|  generator/bidder.h/.c   (existing+)    |    +  .at(i)            new (parity)
|  generator/speck.py      (existing)     |  full Speck family
+----------------------------------------+
```

`BidderBlock` is a thin Python adapter, not a new cipher primitive.
It maps `period -> Bidder(base=period+1, digit_class=1, key)` and
exposes random access by calling the underlying `Bidder.at(i)`. The
adapter has no C twin because it does no cipher work — it only
translates parameters and shifts the output range from `{1, …, P}`
(the existing alphabet contract) to `[0, P)` (the period-only mode
contract).

The actual *new feature* is `at(i)` on the existing `Bidder` class:
random-access into the keyed permutation at any index, returning the
same shape as `next()`. This is a small extension that **must** land
in both Python and C simultaneously per the parity rule in
`generator/AGENTS.md`. Sketch and tests below.

The existing `Bidder` class remains parameterized by `(base, digit_class)`
so the experiment scripts that import it keep working unchanged.
`Bidder.next()`, `Bidder.reset()`, and the iterator dunders are
untouched. Only `Bidder.at(i)` is added.


## The primitive

```python
import operator

MAX_PERIOD_V1 = (1 << 32) - 1   # backend cap from generator/bidder.py


class UnsupportedPeriodError(ValueError):
    """Requested period is mathematically valid but exceeds the v1
    cipher backend's supported range. Lifting this requires either a
    wider cipher backend or the deferred CRT composition lemma."""


class BidderBlock:
    """A keyed permutation of [0, period). Random-access primitive.

    Period-only mode: callers ask for an integer period, get back a
    stateless object whose .at(i) returns the i-th element of the
    permutation. No leading-digit guarantees, no alphabet structure,
    no counter state on the object.

    The object is iterable: each call to iter(B) returns a fresh
    independent iterator over [0, period). There is no shared cursor.
    """

    def __init__(self, period: int, key: bytes):
        if type(period) is not int:
            raise TypeError(
                f"period must be int, got {type(period).__name__}")
        if period < 2:
            raise ValueError("period must be >= 2")
        if period > MAX_PERIOD_V1:
            raise UnsupportedPeriodError(
                f"period {period} exceeds v1 cipher backend cap of "
                f"{MAX_PERIOD_V1}")
        if not isinstance(key, (bytes, bytearray)):
            raise TypeError(
                f"key must be bytes or bytearray, got {type(key).__name__}")

        self._period = period
        # Map period P -> Bidder(base=P+1, digit_class=1, key).
        # Underlying block is [1, P]; .at(i) returns i-th element of
        # the keyed permutation in {1, ..., P}; we shift to [0, P).
        from bidder import Bidder       # local import to keep core/ light
        self._bidder = Bidder(base=period + 1, digit_class=1, key=key)

    def at(self, i: int) -> int:
        """Return the i-th element of the permutation in [0, period).

        Raises:
            TypeError: if i is not an integer.
            ValueError: if i is not in [0, period).
        """
        # operator.index() accepts int and any __index__-conforming type
        # (e.g., numpy ints) and rejects float/str/bool-via-strict-check.
        try:
            i = operator.index(i)
        except TypeError as e:
            raise TypeError(
                f"index must be an integer, got {type(i).__name__}") from e
        if not (0 <= i < self._period):
            raise ValueError(
                f"index {i} out of range [0, {self._period})")
        # Underlying Bidder.at returns in {1, ..., period}; shift to [0, P)
        return self._bidder.at(i) - 1

    @property
    def period(self) -> int:
        return self._period

    @property
    def cipher(self) -> str:
        """Diagnostic: which cipher backend is wired in
        (e.g., 'speck32' or 'feistel'). Used in tests, not in
        correctness arguments.
        """
        return self._bidder._mode_name  # to be added to Bidder

    def __iter__(self):
        """Return a fresh independent iterator over [0, period).

        Calling iter(B) twice gives two independent walks; they do
        not share a cursor.
        """
        return (self.at(i) for i in range(self._period))

    def __len__(self) -> int:
        return self._period

    def __repr__(self) -> str:
        return f"BidderBlock(period={self._period}, cipher={self.cipher!r})"
```

**Iterator semantics, settled.** `BidderBlock` does **not** implement
`__next__`. It is not its own iterator. Each call to `iter(B)` (or
`for x in B`) returns a fresh generator that walks `range(self._period)`
through `at(i)`. Two simultaneous loops over the same block do not
interfere because they each have their own generator. There is no
`reset()` because there is no object-level cursor to reset. Consumers
who want a stateful counter form can build it trivially on top of
`at(i)`:

```python
def cursor(B):
    i = 0
    while i < B.period:
        yield B.at(i)
        i += 1
```

**Cipher selection.** The internal cipher choice (Speck32/64 vs.
small-block Feistel) lives entirely inside the existing `Bidder` class
and is unchanged by this plan. `BidderBlock` is a parameter adapter,
not a cipher choice point. Periods that exceed the existing backend
raise `UnsupportedPeriodError` at construction; lifting that limit is
backend work, not API work.


## The existing-backend extension (parity work)

`BidderBlock` requires random access on the underlying `Bidder` class.
`Bidder` currently exposes only sequential `next()`. Adding `at(i)` is
a real new feature, not a Pythonic convenience, so per the parity rule
in `generator/AGENTS.md` it must land in both Python and C in the same
change.

### Python addition: `Bidder.at(i)`

```python
def at(self, i: int) -> int:
    """Stateless random access: return the i-th output of the keyed
    permutation. Same shape as next() (an element of {1, ..., base-1})
    but without touching self.counter.

    Raises ValueError if i is not in [0, period).
    """
    if not (0 <= i < self.block_size):
        raise ValueError(
            f"index {i} out of range [0, {self.block_size})")
    perm = self._permute(i)
    n = self.block_start + perm
    b = self.base
    while n >= b:
        n //= b
    return n
```

This is `next()` with the counter increment removed and the index
parameterized. `_permute` is already stateless (cycle-walks Speck32 or
Feistel based on the block size); we are just exposing it through a
public entry point.

### C addition: `bidder_at(ctx, i)`

```c
/*
 * Stateless random access: return the i-th output of the keyed
 * permutation, in {1, ..., base-1}. Does not touch ctx->counter.
 *
 * Returns 0 if i is out of range [0, period). (0 is never a valid
 * output, so the caller can use it as a sentinel.)
 */
uint32_t bidder_at(const bidder_ctx *ctx, uint64_t i);
```

The implementation mirrors `bidder_next` minus the counter increment.
`bidder_at` takes `ctx` as `const` because random access does not
mutate state.

### Parity test

`tests/test_bidder.py` and `tests/test_bidder_c.c` both gain a
cross-language fixture: for a fixed key and a fixed `(base, digit_class)`,
assert that `Bidder.at(i)` and `bidder_at(ctx, i)` agree on a sample
of indices, and that both agree with the existing `next()` sequence
(i.e., `[B.at(i) for i in range(period)] == [B.next() for _ in range(period)]`
on a fresh `B`).


## The orchestration

```python
# core/api.py

import os
import sys

# Put generator/ on sys.path so `import bidder_block` resolves. This
# matches the existing cross-directory import convention in
# tests/test_acm_core.py, core/hardy_sidestep.py, and the experiment
# scripts — the repo is not packaged, and callers that import core/api
# are expected to have put core/ on their own sys.path already.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, '..', 'generator'))

from bidder_block import BidderBlock, UnsupportedPeriodError  # noqa: E402


def fulfill(period: int, key: bytes) -> BidderBlock:
    """Build a BidderBlock for the requested period.

    In v1 this is the BidderBlock constructor under another name. The
    constructor handles all validation and refusal — fulfill exists as
    the public API entry point so that future composition / catalogue
    work can extend it without changing call sites.

    Raises:
        TypeError: if period or key has the wrong type.
        ValueError: if period < 2.
        UnsupportedPeriodError: if period exceeds the v1 backend cap.
    """
    return BidderBlock(period, key)
```

**Import strategy, explicit.** This repo is not a Python package —
there is no `setup.py`, no `pyproject.toml`, no `__init__.py` files
anywhere under `core/` or `generator/`. Cross-directory imports work
by each file inserting its sibling directories onto `sys.path` at the
top of the file. This is the same pattern used by
`tests/test_acm_core.py`, `core/hardy_sidestep.py`, and every
experiment script under `experiments/`.

Three consequences for the new files:

1. **`core/api.py`** inserts `generator/` onto `sys.path` at the top
   (shown above) so it can `import bidder_block`.
2. **`generator/bidder_block.py`** does `from bidder import Bidder`
   with **no** `sys.path` manipulation — `bidder.py` is in the same
   directory as `bidder_block.py`, and whoever imported `bidder_block`
   must already have `generator/` on the path, so `bidder` resolves
   from the same directory.
3. **Callers of `core/api.py`** must have `core/` on `sys.path`
   before `import api` resolves. The tests in `tests/test_api.py`
   and `tests/test_bidder_block.py` do this with the same
   `sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))`
   pattern as `tests/test_acm_core.py`.

Packaging the repo (adding `pyproject.toml` and `__init__.py`s) would
make all of this unnecessary, but it is out of scope for the API plan
— this doc treats packaging as a separate future concern, not a v1
dependency.

That is the entire orchestration layer in v1. It is intentionally
trivial. When composition arrives, `fulfill` keeps the same single-object
return contract — it just gains the ability to assemble a *composite*
block-like object internally:

```python
class CompositeBidderBlock:
    """Same interface as BidderBlock: .at(i), .period, __iter__, __len__.
    Internally a composition (CRT or other) of two or more BidderBlocks.
    The composition method is opaque to the caller; .info exposes it for
    debugging."""
    def at(self, i: int) -> int: ...
    @property
    def period(self) -> int: ...
    @property
    def info(self) -> dict: ...   # e.g. {'method': 'CRT', 'factors': [p1, p2]}
```

Future `fulfill` returns either a `BidderBlock` or a
`CompositeBidderBlock`; both satisfy the same `.at(i)` / `.period`
contract, so callers do not need to know which one they got. **The
composition path returns a single composite object, not a list of
factor blocks.** Recombination always happens inside the API, never on
the caller. This is the only return-shape contract `fulfill` ever has.


## Deferred proof: CRT composition lemma

The immediate API does not need new math. The composition path does.

### Why composition matters

For very large periods (e.g., `P > 2^60`) the cipher layer faces a
choice: either widen Speck (cycle-walk Speck128/256, paying a large
ratio) or build a wide-block Feistel from SHA-256/BLAKE3 (paying many
hash invocations per `at(i)`). A third option, cheaper than either
when `P` factors nicely, is to express `P` as a product of coprime
factors `P = p_1 · p_2 · …` and run one BIDDER block per factor on a
narrow cipher, recombining via CRT. The per-call cipher cost becomes
the sum of per-factor cycle-walked Speck calls, which can be much
smaller than the wide-block alternatives.

The mathematical question this raises is: **does composing per-factor
permutations via CRT yield a permutation of the product index space?**
The answer is yes, and the proof is two paragraphs.

### Sketch

**Lemma (CRT composition).** Let `B_1` and `B_2` be BIDDER blocks
with coprime periods `p_1, p_2`. Define the composite block `B` of
period `p_1 · p_2` by

    B.at(i) = CRT( B_1.at(i mod p_1),  B_2.at(i mod p_2) )

where `CRT(a, b)` is the unique integer in `[0, p_1·p_2)` satisfying
`x ≡ a (mod p_1)` and `x ≡ b (mod p_2)`. Then `B.at` is a permutation
of `[0, p_1·p_2)`.

**Proof.** Three bijections compose to one:

1. `i ↦ (i mod p_1, i mod p_2)` is a bijection
   `[0, p_1·p_2) → [0, p_1) × [0, p_2)` by the Chinese Remainder
   Theorem (which requires `gcd(p_1, p_2) = 1`).
2. `(a, b) ↦ (B_1.at(a), B_2.at(b))` is a bijection
   `[0, p_1) × [0, p_2) → [0, p_1) × [0, p_2)` because each component
   `B_k.at` is a permutation of `[0, p_k)` by hypothesis.
3. `(a', b') ↦ CRT(a', b')` is the inverse of step 1, again by CRT.

The composition of three bijections is a bijection. ∎

The lemma generalizes to any finite list of pairwise coprime periods
by induction on the number of factors.

**Edge cases:**
- `gcd(p_1, p_2) > 1`: step 1 fails. The composition is not defined
  by this lemma. A practical implementation should reject the
  composition request and tell the caller.
- `p_1 = 1` or `p_2 = 1`: degenerate; the composite collapses to the
  other factor. Allow but special-case.

### Where the proof will go

A new file `core/COMPOSITION.md`, structured to mirror
`core/BLOCK-UNIFORMITY.md`:

1. Lemma statement
2. Proof
3. Edge cases (`gcd > 1`, degenerate factors)
4. Multi-factor generalization (induction)
5. Connection back to `core/API-PLAN.md` and the `fulfill` function
6. Verification (test description)

The doc will not include BQN. The lemma is purely about index-space
bijections; it does not touch the n-prime or leading-digit machinery
in `core/BLOCK-UNIFORMITY.md` or `core/HARDY-SIDESTEP.md`.

### How the proof will be tested

A new test file `tests/test_composition.py`:

1. **Bijection on small coprime pairs.** Sweep `(p_1, p_2)` with
   `p_1, p_2 ∈ [2, 30]` and `gcd(p_1, p_2) = 1`. For each, build
   `B_1, B_2` with a fixed key, build the composite `B`, and assert
   that `[B.at(i) for i in range(p_1 * p_2)]` is a permutation of
   `[0, p_1 * p_2)` (i.e., contains every value exactly once).
2. **Period correctness.** For the same sweep, assert
   `B.period == p_1 * p_2`.
3. **Determinism under key.** For each `(p_1, p_2)`, build the
   composite twice with the same key and assert pointwise equality
   on a sample of indices.
4. **Key sensitivity.** Build with two different keys and assert that
   at least one index differs (with overwhelming probability — this
   is a smoke test, not a security claim).
5. **Non-coprime rejection.** For `(p_1, p_2)` with `gcd > 1`, assert
   that the composition constructor raises `ValueError`.
6. **Multi-factor.** For three pairwise-coprime factors
   `(p_1, p_2, p_3)`, build the composite and assert bijection on the
   product range.
7. **Larger smoke test.** With `p_1 = 2^16 − 1`, `p_2 = 2^16 + 1`
   (coprime, product `~ 2^32`), build the composite and assert
   `B.at(i)` is in range and that `[B.at(i) for i in random sample]`
   has no duplicates.

The first six tests are exhaustive for the small ranges. The seventh
is a sanity check for periods large enough to exercise the cipher
selection without being so large that exhaustive enumeration is
infeasible.


### Composite block class

When the lemma lands, the composite is wrapped in a class that
satisfies the same interface as `BidderBlock`:

```python
class CRTComposite:
    """Same .at(i) / .period / __iter__ / __len__ contract as BidderBlock.
    The caller cannot tell the two apart from the public interface;
    .info exposes the composition method for debugging."""

    def __init__(self, B1, B2):
        if math.gcd(B1.period, B2.period) != 1:
            raise ValueError("CRT composition requires coprime periods")
        self._B1, self._B2 = B1, B2
        self._period = B1.period * B2.period
        self._inv1 = pow(B2.period, -1, B1.period)
        self._inv2 = pow(B1.period, -1, B2.period)

    def at(self, i: int) -> int:
        # same type-and-range checks as BidderBlock.at
        ...
        a = self._B1.at(i % self._B1.period)
        b = self._B2.at(i % self._B2.period)
        return (a * self._B2.period * self._inv1 +
                b * self._B1.period * self._inv2) % self._period

    @property
    def period(self) -> int: return self._period

    @property
    def info(self) -> dict:
        return {'method': 'CRT',
                'factors': [self._B1.period, self._B2.period]}

    def __iter__(self):
        return (self.at(i) for i in range(self._period))

    def __len__(self) -> int:
        return self._period
```

`fulfill` returns either a `BidderBlock` or a `CRTComposite` (or a
chain of them for multi-factor compositions). Both satisfy the same
`.at(i)` / `.period` / `__iter__` / `__len__` contract. Callers never
see the parts list.


## Tests for the immediate API

The immediate API needs its own tests too, even though no new math
is involved.

### `tests/test_bidder_block.py`

1. **Period property.** For a sweep of small periods
   `P ∈ {2, 3, 5, 8, 100, 1000, 65535}`, build `BidderBlock(P, key)`
   and assert `.period == P` and `len(B) == P`.
2. **Permutation.** For small `P` (say `P ≤ 10000`), assert
   `sorted(B.at(i) for i in range(P)) == list(range(P))`. Output
   range is `[0, P)`, never includes `P`.
3. **Out-of-range raises ValueError.** Assert `B.at(P)`, `B.at(P+1)`,
   `B.at(-1)`, and `B.at(2**40)` all raise `ValueError`.
4. **Non-integer index raises TypeError.** Assert `B.at(1.5)`,
   `B.at("3")`, and `B.at(None)` raise `TypeError`. Booleans pass
   (Python convention: `True`/`False` *are* `int` for `__index__`).
   Numpy ints pass via `operator.index`.
5. **Non-bytes key raises TypeError.** `BidderBlock(100, "string")`
   and `BidderBlock(100, 12345)` raise `TypeError`. `bytes` and
   `bytearray` are accepted.
6. **`period < 2` raises ValueError.** `BidderBlock(1, key)`,
   `BidderBlock(0, key)`, `BidderBlock(-1, key)` raise `ValueError`.
7. **`period > 2^32 − 1` raises UnsupportedPeriodError.**
   `BidderBlock(2**32, key)` and `BidderBlock(2**40, key)` raise
   `UnsupportedPeriodError` (a `ValueError` subclass).
8. **Determinism under key.** Two `BidderBlock(P, k)` instances with
   the same key produce identical sequences.
9. **Key sensitivity.** Two `BidderBlock(P, k1)` and `BidderBlock(P, k2)`
   with different keys differ at at least one index (smoke test, not
   a security claim).
10. **`iter(B)` is fresh each time.** Construct `B`, call `iter(B)`
    twice (`it1`, `it2`), advance `it1` by 5 elements, then assert
    `next(it2)` equals `B.at(0)`. Two iterators share no state.
11. **Iteration matches indexing.** `list(B) == [B.at(i) for i in range(P)]`.
12. **No `__next__` on `B` itself.** Assert `next(B)` raises `TypeError`
    (`BidderBlock` is iterable but not its own iterator). Locks in the
    iterator-model decision.
13. **No `reset()` method.** Assert `not hasattr(B, 'reset')`.
14. **Cipher selection diagnostic.** For a couple of periods on either
    side of the Speck32/Feistel boundary in `Bidder`, assert `B.cipher`
    reports the expected variant. Documents the selection rule; not a
    correctness test.

### `tests/test_api.py`

1. **`fulfill(P, key).period == P`** for a sweep of valid periods,
   including the boundary `P = 2`, a small `P = 100`, and the upper
   boundary `P = 2**32 - 1`.
2. **`fulfill(1, key)`, `fulfill(0, key)`, `fulfill(-5, key)` all
   raise `ValueError`.**
3. **`fulfill(2**32, key)` raises `UnsupportedPeriodError`.**
4. **`fulfill('100', key)` and `fulfill(1.5, key)` raise `TypeError`.**
5. **`fulfill(100, 'string')` raises `TypeError`.**
6. **Returned object behaves as a `BidderBlock`** (smoke test:
   `.at(0)`, `.at(P-1)`, `iter(B)`, `len(B)`, `.period`).

### Parity test additions to existing files

`tests/test_bidder.py` (Python) and `tests/test_bidder_c.c` (C) both
gain a fixture for the new `Bidder.at(i)` / `bidder_at(ctx, i)`:

- **`at(i)` matches the i-th `next()`.** For a fixed key and a small
  block, assert `[B.at(i) for i in range(period)]` equals
  `[B.next() for _ in range(period)]` from a fresh `B`.
- **Cross-language `at(i)`.** Same fixture as the existing
  cross-language check, but using `at(i)` on both sides.
- **`at(i)` is stateless.** Calling `at(i)` does not advance the
  internal counter — interleave `at(i)` and `next()` and assert
  `next()` still returns the original sequence.
- **C `bidder_at` out-of-range returns 0.** Assert
  `bidder_at(&ctx, period)` and `bidder_at(&ctx, UINT64_MAX)` return 0.

All test files run under `python3` (no numpy import in
`bidder_block.py` or `core/api.py`). The C tests build with
`gcc -O2 ...` per the existing pattern in `AGENTS.md`.


## What is deferred

| Item | Reason | Lives in |
|------|--------|----------|
| CRT composition | Lemma not yet proved | `core/COMPOSITION.md` (future) |
| `CRTComposite` class | Needs the lemma | `generator/bidder_block.py` (future) |
| Wider cipher backends | Implementation work; lifts `MAX_PERIOD_V1` | `generator/` (future) |
| Alphabet-pinned mode | User explicitly dropped from v1 scope | future API addition |
| n-prime BIDDER variant | Math ready (BLOCK-UNIFORMITY + HARDY-SIDESTEP); cipher not | future generator |
| Statistical-uniformity (`'iid'`) support | No use case yet | not on the roadmap |

CRT composition and wider cipher backends are **two independent axes**
for lifting the `MAX_PERIOD_V1 = 2^32 − 1` cap. They can land in
either order (or both). v1 ships without either; large periods raise
`UnsupportedPeriodError` until one of them lands.

The deferred items do not block v1. v1 is the parity-extended primitive
plus a Python adapter plus a validating wrapper, with the math
machinery in `core/BLOCK-UNIFORMITY.md` and `core/HARDY-SIDESTEP.md`
sitting unused until the deferred items pull it in.


## Build order

The v1 deliverable starts with the parity work because everything
above it depends on `Bidder.at(i)` existing in both languages.

1. **Add `Bidder.at(i)` in Python.** Edit `generator/bidder.py`:
   add the `at(i)` method described in the parity-work section. Do
   not change `next()`, `reset()`, or any existing behavior.
2. **Add `bidder_at()` in C.** Edit `generator/bidder.h` and
   `generator/bidder.c`: add the `bidder_at` function with the
   signature in the parity-work section. Mirror the Python
   implementation exactly.
3. **Extend the cross-language test.** Update `tests/test_bidder.py`
   and `tests/test_bidder_c.c` with the four parity fixtures listed
   in the test plan. Run both suites to confirm Python and C agree
   on `at(i)`.
4. **Implement `generator/bidder_block.py`.** The `BidderBlock`
   adapter, `MAX_PERIOD_V1`, and `UnsupportedPeriodError`. No cipher
   work — purely parameter translation and output shifting on top of
   the now-extended `Bidder`.
5. **Write `tests/test_bidder_block.py`.** All 14 tests in the test
   plan. Confirm green.
6. **Implement `core/api.py:fulfill`.** A 2-line wrapper around
   `BidderBlock`. The validation lives in `BidderBlock.__init__`;
   `fulfill` is just the public entry point name.
7. **Write `tests/test_api.py`.** All 6 tests in the test plan.
   Confirm green.

Steps 1–7 are the v1 deliverable. Each one is small.

8. (Deferred) Prove the CRT composition lemma in `core/COMPOSITION.md`.
9. (Deferred) Implement `CRTComposite` in `generator/bidder_block.py`
   and add `tests/test_composition.py`.
10. (Deferred) Extend `fulfill` to recognize when a requested period
    factors cheaply as a product of coprime smaller periods and to
    assemble a `CRTComposite` instead of a direct `BidderBlock`. The
    return type contract does not change — the caller still gets a
    single block-shaped object.
11. (Deferred) Wider cipher backends in `generator/` to lift the
    `MAX_PERIOD_V1` cap. This is independent of CRT composition; the
    two are alternative ways to support larger periods.

Steps 8–11 are future work. None of them block v1.
