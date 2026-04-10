# BIDDER

The root API for the BIDDER project. Two construction functions,
two object types, one file.

Each function is documented in three layers:

- **Natural language** — what the function does.
- **Python** — the actual signature and a runnable example.
- **BQN** — what the call corresponds to in the ACM-Champernowne
  world. BQN is documentation of the math layer; the cipher itself
  is out of scope for BQN per `guidance/BQN-AGENT.md`.


## Quick start

```python
import bidder

# Cipher path: keyed permutation of [0, period)
B = bidder.cipher(period=10, key=b'doc')
print(list(B))           # [0, 4, 8, 1, 7, 6, 9, 3, 2, 5]

# Sawtooth path: deterministic n-prime sequence
S = bidder.sawtooth(n=3, count=10)
print(list(S))           # [3, 6, 12, 15, 21, 24, 30, 33, 39, 42]
```


## `bidder.cipher`

Return a keyed permutation of `[0, period)`. The order of the
outputs is determined by the key; the contents are all integers in
`[0, period)`, each appearing exactly once.

**Python.**

```python
def cipher(period: int, key: bytes) -> BidderBlock: ...
```

```python
import bidder

B = bidder.cipher(period=10, key=b'doc')
B.period       # 10
B.at(0)        # 0
B.at(9)        # 5
list(B)        # [0, 4, 8, 1, 7, 6, 9, 3, 2, 5]
```

**BQN.**

`bidder.cipher(P, key)` constructs a keyed permutation of `↕ P`.
Internally this is the `d = 1` case of the integer-block lemma in
`core/BLOCK-UNIFORMITY.md`:

```bqn
b⋆d-1 + ↕ (b-1)×b⋆d-1
```

With `b = P + 1` and `d = 1`, this evaluates to `1 + ↕ P`. The
adapter shifts by `−1` so the external set is `↕ P`. The keying
picks which permutation of this set is returned; BQN does not
represent the keyed choice.

See `core/API.md` for the full cipher-path reference.


## `bidder.sawtooth`

Return the first `count` n-primes of monoid `nZ+` for `n ≥ 2`, in
ascending order. Deterministic — no key. Random access via the
Hardy closed form.

**Python.**

```python
def sawtooth(n: int, count: int) -> NPrimeSequence: ...
```

```python
import bidder

S = bidder.sawtooth(n=3, count=10)
S.n            # 3
S.count        # 10
S.at(0)        # 3
S.at(9)        # 42
list(S)        # [3, 6, 12, 15, 21, 24, 30, 33, 39, 42]
```

The 3-primes are the multiples of 3 that are not multiples of 9:
`3, 6, 12, 15, 21, 24, 30, 33, 39, 42, …` — every third integer
with one deletion per period of length 3 (see
`core/ACM-CHAMPERNOWNE.md`).

**BQN.**

The Hardy closed form from `core/HARDY-SIDESTEP.md`:

```bqn
NthNPn2 ← {𝕨 × 1 + ((𝕨-1)|𝕩-1) + 𝕨 × ⌊(𝕩-1)÷𝕨-1}
```

`sawtooth(n, count).at(K)` for `K ∈ [0, count)` is exactly

```bqn
n NthNPn2 K+1
```

— the `(K+1)`-th n-prime (1-indexed in the BQN convention) of
monoid `nZ+`. The closed form is `O(1)` bignum work per call:
one `divmod` and one multiply on `O(log K + log n)`-wide integers.

The n-prime enumerator `NPn2` from `guidance/BQN-AGENT.md` generates
the same sequence:

```bqn
NPn2 ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}
```

The difference: `NPn2` generates a prefix by sieving; `NthNPn2`
gives random access by index.


## Shared interface shape

Both objects returned by `cipher` and `sawtooth` satisfy the same
method set:

| Method / property | `BidderBlock`                         | `NPrimeSequence`                      |
|-------------------|---------------------------------------|---------------------------------------|
| `.at(i)`          | i-th element of the keyed permutation | K-th n-prime via Hardy closed form    |
| `.period`         | the requested period `P`              | the requested count                   |
| `len(B)`          | `P`                                   | `count`                               |
| `iter(B)`         | fresh generator over `[0, P)`         | fresh generator over n-primes         |
| `repr(B)`         | `BidderBlock(period=P, cipher=...)`   | `NPrimeSequence(n=N, count=C)`       |

Both raise `TypeError` for non-integer indices and `ValueError` for
out-of-range indices. Neither implements `__next__` on the object
itself — `next(B)` raises `TypeError`. There is no `reset()` method.

The shared shape means the same mental model works for both objects
and the same `for x in obj` / `obj.at(i)` / `len(obj)` code works
for both. The semantic difference — shuffle vs ascending sequence — is
the caller's responsibility to know.


## Constants and exceptions

```python
import bidder

bidder.MAX_PERIOD_V1            # 4294967295  ( = 2**32 - 1)
bidder.UnsupportedPeriodError   # ValueError subclass
```

`MAX_PERIOD_V1` is the largest period the cipher path supports in v1.
The bound comes from the existing cipher backend in
`generator/coupler.py`, which caps `base` at `2^32` (see
`generator/AGENTS.md`). The sawtooth path has no analogous cap — the
Hardy closed form works for any `n` and `count`.

**BQN.**

```bqn
(2⋆32) - 1
# 4294967295
```

The math layer imposes no upper bound on `P`. The cap is a property
of the cipher backend, not of the integer-block lemma or the Hardy
closed form.


## Examples

### Build and iterate both paths

```python
import bidder

B = bidder.cipher(period=10, key=b'doc')
S = bidder.sawtooth(n=2, count=5)
print(list(B))            # [0, 4, 8, 1, 7, 6, 9, 3, 2, 5]
print(list(S))            # [2, 6, 10, 14, 18]
```

The cipher output is a shuffle of `[0, 10)`. The sawtooth output is
the first five 2-primes in ascending order.

### Random access

```python
import bidder

B = bidder.cipher(period=50, key=b'mix')
S = bidder.sawtooth(n=7, count=50)
B.at(0)        # 7
S.at(0)        # 7
```

Both `.at(0)` calls return `7` — a coincidence of the parameters,
not a guarantee. The cipher path's output depends on the key; the
sawtooth path's output depends on `n`.

### Sawtooth at astronomical depth

```python
import bidder

S = bidder.sawtooth(n=2, count=2**40)
S.at(2**40 - 1)     # 4398046511102  ( = 2**42 - 2)
```

The `(2^40)`-th 2-prime, computed in microseconds via the Hardy
closed form. No enumeration of the preceding 10^12 elements.

### Cipher refusal at the backend cap

```python
import bidder
from bidder import UnsupportedPeriodError

try:
    bidder.cipher(period=2**32, key=b'doc')
except UnsupportedPeriodError as e:
    print(e)
    # period 4294967296 exceeds v1 cipher backend cap of 4294967295
```

The sawtooth path has no cap.


## What is not yet supported

| Item                                  | Reason                                           |
|---------------------------------------|--------------------------------------------------|
| Cipher periods `> 2^32 − 1`          | Cipher backend cap. Needs wider Speck or CRT.    |
| CRT composition                      | Lemma not yet written.                           |
| Alphabet-pinned cipher               | Use legacy `Bidder` in `generator/coupler.py`.   |
| n-prime BIDDER variant                | Math ready; cipher path not built.               |
| `n = 1` (ordinary primes)            | Hardy closed form requires `n ≥ 2`.              |
| Infinite sawtooth iteration           | `count` is mandatory.                            |
| Running mean / Champernowne real      | Derived properties; see `core/acm_core.py`.      |


## See also

- `core/API.md` — detailed cipher-path reference (three-layer format).
- `core/HARDY-SIDESTEP.md` — the closed form `NthNPn2` for the
  K-th n-prime, proof, and computational witness.
- `core/BLOCK-UNIFORMITY.md` — the integer-block lemma, the smooth
  and Family E sieved lemmas, and the spread bound.
- `core/ACM-CHAMPERNOWNE.md` — the construction of the
  n-Champernowne reals.
- `core/ABDUCTIVE-KEY.md` — the rank-1 lemma and the
  leaky-parameterization theme.
- `guidance/BQN-AGENT.md` — canonical BQN names (`NPn2`, `NthNPn2`,
  `Digits10`, `LeadingInt10`).
- `generator/AGENTS.md` — cipher feature set, parity rules, the
  `coupler.py` rename.
