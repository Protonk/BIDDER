# BIDDER

`bidder` is a Python module that constructs two kinds of integer
sequences and returns them as stateless random-access objects:

- `bidder.cipher(period, key)` returns a `BidderBlock`: a keyed
  permutation of `[0, period)`.
- `bidder.sawtooth(n, count)` returns an `NPrimeSequence`: the first
  `count` positive multiples of `n` that are not multiples of `n*n`,
  in ascending order.

Both object types expose the same method shape: `.at(i)`, `.period`,
`len()`, `iter()`, `repr()`.

```python
import bidder

B = bidder.cipher(period=10, key=b'doc')
S = bidder.sawtooth(n=3, count=10)
```


## Installing

`bidder` is a single Python package with no dependencies outside the
standard library. It is not distributed as a wheel and there is no
build step on the consumer side.

To use it: place the `bidder/` directory inside a directory on your
`PYTHONPATH`, or add the parent directory that contains `bidder/` to
`PYTHONPATH`. A typical placement is a `vendor/`, `third_party/`, or
project-source subdirectory:

```
your_project/
    your_code.py
    vendor/
        bidder/
            __init__.py
            BIDDER.md
            ...
```

With `vendor/` on `PYTHONPATH`:

```python
import bidder

B = bidder.cipher(period=10, key=b'doc')
```

Python 3.9 or newer. No native compilation. No configuration.


## Surface

The public API is exactly `bidder.__all__`. Every name below is part
of the contract. Any other attribute reachable via `dir(bidder)` is
internal and may not be relied on.

| Name                            | Kind      | Summary                                                        |
|---------------------------------|-----------|----------------------------------------------------------------|
| `bidder.cipher`                 | function  | Construct a `BidderBlock` from `(period, key)`.                |
| `bidder.sawtooth`               | function  | Construct an `NPrimeSequence` from `(n, count)`.               |
| `bidder.BidderBlock`            | class     | Keyed permutation of `[0, period)`.                            |
| `bidder.NPrimeSequence`         | class     | Ascending enumeration of n-primes.                             |
| `bidder.MAX_PERIOD_V1`          | int       | Upper bound on `period`. Value: `4294967295`.                  |
| `bidder.UnsupportedPeriodError` | exception | Raised when `period` exceeds `bidder.MAX_PERIOD_V1`.           |


## Shared interface

`BidderBlock` and `NPrimeSequence` share the same method shape:

| Expression      | `BidderBlock`                                               | `NPrimeSequence`                                       |
|-----------------|-------------------------------------------------------------|--------------------------------------------------------|
| `obj.at(i)`     | `int` in `[0, period)`; i-th element of the keyed permutation | `int`; i-th n-prime in ascending order                |
| `obj.period`    | `int`; equals the `period` passed to `bidder.cipher`        | `int`; equals the `count` passed to `bidder.sawtooth` |
| `len(obj)`      | `int`; equals `obj.period`                                  | `int`; equals `obj.period`                             |
| `iter(obj)`     | fresh generator yielding every element of `[0, period)` exactly once | fresh generator yielding n-primes in strictly ascending order |
| `repr(obj)`     | `str`; debug-only, format is not part of the contract       | `str`; debug-only, format is not part of the contract  |

Neither object implements `__next__`; calling `next(obj)` raises
`TypeError`. Neither object has a `reset` method. Instances are
immutable with respect to their public interface: repeated calls to
`.at(i)` with the same `i` return the same value.


## `bidder.cipher`

```python
bidder.cipher(period: int, key: bytes | bytearray) -> BidderBlock
```

Construct a keyed permutation of `[0, period)`. The returned
`BidderBlock` is a pure function of `(period, key)`: two calls with
equal arguments yield two instances whose `.at(i)` outputs agree on
every `i`.

**Arguments**

- `period` — `int`. Must satisfy `2 <= period <= 4294967295`. The
  type check is strict: `bool` is rejected even though `bool` is a
  subclass of `int`.
- `key` — `bytes` or `bytearray`. Any length is accepted, including
  the empty byte string `b''`. The exact byte content is the full
  key input; no normalization, hashing, or padding is applied by the
  caller-visible contract.

**Returns** a `BidderBlock`.

**Raises**

- `TypeError` — `period` is not exactly `int`, or `key` is not
  `bytes`/`bytearray`.
- `ValueError` — `period < 2`.
- `bidder.UnsupportedPeriodError` — `period > 4294967295`.
  `UnsupportedPeriodError` is a subclass of `ValueError`.

**Example**

```python
import bidder

B = bidder.cipher(period=10, key=b'doc')
print(list(B))
print(B.at(0), B.at(9), len(B), B.period)
```

Output:

```
[0, 4, 8, 1, 7, 6, 9, 3, 2, 5]
0 5 10 10
```


## `bidder.sawtooth`

```python
bidder.sawtooth(n: int, count: int) -> NPrimeSequence
```

Construct an ascending enumeration of the first `count` n-primes.
The n-primes of `n` are the positive multiples of `n` that are not
multiples of `n*n`. For `n = 3` the sequence begins
`3, 6, 12, 15, 21, 24, 30, 33, 39, 42, ...`: every positive multiple
of `3`, with every third term (`9, 18, 27, ...`) deleted.

The returned `NPrimeSequence` is a pure function of `(n, count)`.
There is no key.

**Arguments**

- `n` — `int`. Must satisfy `n >= 2`. Strict: `bool` rejected.
- `count` — `int`. Must satisfy `count >= 1`. Strict: `bool`
  rejected.

`n` must be at most `2^64 − 1`. `count` must be at most
`sys.maxsize` (typically `2^63 − 1`). The underlying computation
is `O(1)` integer arithmetic per `.at(K)` call, so large `count`
and large `K` are supported within these bounds.

**Returns** an `NPrimeSequence`.

**Raises**

- `TypeError` — `n` or `count` is not exactly `int`.
- `ValueError` — `n < 2`, or `count < 1`.
- `OverflowError` — `n` exceeds `2^64 − 1`, or `count` exceeds
  `sys.maxsize`.

**Example**

```python
import bidder

S = bidder.sawtooth(n=3, count=10)
print(list(S))
print(S.at(0), S.at(9), len(S), S.period, S.n, S.count)
```

Output:

```
[3, 6, 12, 15, 21, 24, 30, 33, 39, 42]
3 42 10 10 3 10
```


## `BidderBlock`

A keyed permutation of `[0, period)`. An instance holds only the
`(period, key)` captured at construction; it has no mutable public
state.

### `bidder.BidderBlock(period, key)`

```python
bidder.BidderBlock(period: int, key: bytes | bytearray)
```

Direct constructor. Accepts the same arguments as `bidder.cipher`,
raises the same exceptions, and returns an instance with the same
contract. `bidder.cipher(period, key)` and
`bidder.BidderBlock(period, key)` are equivalent; callers may use
either form.

### `BidderBlock.at(i) -> int`

Return the `i`-th element of the permutation.

- `i` — any object accepted by `operator.index` (so `int`, `bool`,
  or any type defining `__index__`). Must satisfy
  `0 <= i < B.period`. Negative indices are not accepted.
- Return: an `int` in `[0, B.period)`.

Raises `TypeError` if `i` is not index-like (for example `float` or
`str`). Raises `ValueError` if `i` is out of range.

Pure in `(period, key, i)`: repeated calls return equal values.

### `BidderBlock.period -> int`

Read-only property. The `period` argument passed to `bidder.cipher`.

### `iter(B)`

Each call returns a fresh independent generator that yields
`B.at(0), B.at(1), ..., B.at(B.period - 1)` in that order. Two
iterators obtained from the same `BidderBlock` share no state;
advancing one does not advance the other.

Iterating a `BidderBlock` yields every integer in `[0, B.period)`
exactly once.

### `len(B) -> int`

Returns `B.period`.

### `repr(B) -> str`

Returns a string intended for debugging. The exact format is not
part of the contract and callers must not parse it.

### `next(B)`

Raises `TypeError`. `BidderBlock` is iterable but is not itself an
iterator; obtain an iterator with `iter(B)` first.


## `NPrimeSequence`

An ascending enumeration of the first `count` n-primes. An instance
holds only the `(n, count)` captured at construction; it has no
mutable public state.

### `bidder.NPrimeSequence(n, count)`

```python
bidder.NPrimeSequence(n: int, count: int)
```

Direct constructor. Accepts the same arguments as `bidder.sawtooth`,
raises the same exceptions, and returns an instance with the same
contract. `bidder.sawtooth(n, count)` and
`bidder.NPrimeSequence(n, count)` are equivalent; callers may use
either form.

### `NPrimeSequence.at(K) -> int`

Return the `K`-th n-prime (0-indexed) in ascending order.

- `K` — any object accepted by `operator.index`. Must satisfy
  `0 <= K < S.count`. Negative indices are not accepted.
- Return: an `int` satisfying

  ```python
  q, r = divmod(K, S.n - 1)
  S.at(K) == S.n * (q * S.n + r + 1)
  ```

  equivalently: the `(K + 1)`-th smallest positive multiple of
  `S.n` that is not a multiple of `S.n * S.n`.

Raises `TypeError` if `K` is not index-like. Raises `ValueError` if
`K` is out of range.

Pure in `(n, K)`: the value does not depend on `count` beyond the
`K < count` validity check. Constant-time integer arithmetic.

### `NPrimeSequence.n -> int`

Read-only property. The `n` argument passed to `bidder.sawtooth`.

### `NPrimeSequence.count -> int`

Read-only property. The `count` argument passed to
`bidder.sawtooth`.

### `NPrimeSequence.period -> int`

Read-only property. Equal to `NPrimeSequence.count`. Present so
`BidderBlock` and `NPrimeSequence` expose the same attribute name
for their length.

### `iter(S)`

Each call returns a fresh independent generator that yields
`S.at(0), S.at(1), ..., S.at(S.count - 1)` in strictly ascending
order.

### `len(S) -> int`

Returns `S.count`.

### `repr(S) -> str`

Returns a string intended for debugging. The exact format is not
part of the contract and callers must not parse it.

### `next(S)`

Raises `TypeError`. `NPrimeSequence` is iterable but is not itself
an iterator; obtain an iterator with `iter(S)` first.


## Constants

### `bidder.MAX_PERIOD_V1 -> int`

Value: `4294967295`. The largest value accepted for the `period`
argument of `bidder.cipher`. A call with `period > MAX_PERIOD_V1`
raises `bidder.UnsupportedPeriodError`.


## Exceptions

All exception types raised by `bidder` are listed below. Message
strings are reproduced verbatim as the module emits them;
placeholders in braces are filled at runtime with the offending
value or type name.

### `TypeError`

| Trigger                                                           | Message                                          |
|-------------------------------------------------------------------|--------------------------------------------------|
| `bidder.cipher(period, key)` with `type(period) is not int`       | `period must be int, got {typename}`             |
| `bidder.cipher(period, key)` with `key` not `bytes`/`bytearray`   | `key must be bytes or bytearray, got {typename}` |
| `bidder.sawtooth(n, count)` with `type(n) is not int`             | `n must be int, got {typename}`                  |
| `bidder.sawtooth(n, count)` with `type(count) is not int`         | `count must be int, got {typename}`              |
| `BidderBlock.at(i)` with `i` not accepted by `operator.index`     | `index must be an integer, got {typename}`      |
| `NPrimeSequence.at(K)` with `K` not accepted by `operator.index`  | `index must be an integer, got {typename}`      |
| `next(B)` where `B` is a `BidderBlock`                            | `'BidderBlock' object is not an iterator`        |
| `next(S)` where `S` is an `NPrimeSequence`                        | `'NPrimeSequence' object is not an iterator`     |

### `ValueError`

| Trigger                                                           | Message                                                                              |
|-------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `bidder.cipher(period, key)` with `period < 2`                    | `period must be >= 2`                                                                |
| `bidder.sawtooth(n, count)` with `n < 2`                          | `n must be >= 2`                                                                     |
| `bidder.sawtooth(n, count)` with `count < 1`                      | `count must be >= 1`                                                                 |
| `BidderBlock.at(i)` with `i` outside `[0, period)`                | `index {i} out of range [0, {period})`                                               |
| `NPrimeSequence.at(K)` with `K` outside `[0, count)`              | `index {K} out of range [0, {count})`                                                |

### `bidder.UnsupportedPeriodError`

Subclass of `ValueError`. An `except ValueError:` clause catches it;
an `except bidder.UnsupportedPeriodError:` clause catches only this
specific case.

| Trigger                                                          | Message                                                                 |
|------------------------------------------------------------------|-------------------------------------------------------------------------|
| `bidder.cipher(period, key)` with `period > 4294967295`          | `period {period} exceeds maximum of 4294967295`                         |

### `OverflowError`

| Trigger                                                          | Message                                                                 |
|------------------------------------------------------------------|-------------------------------------------------------------------------|
| `bidder.sawtooth(n, count)` with `n > 2^64 − 1`                  | `n must fit in a 64-bit unsigned integer, got {n}`                     |
| `bidder.sawtooth(n, count)` with `count > sys.maxsize`            | `count must be at most sys.maxsize ({sys.maxsize}), got {count}`       |


## Invariants

These are positive guarantees the caller may rely on. Each is a
statement about the public interface, not about internal state.

1. `bidder.cipher(period, key).at(i)` is a pure function of
   `(period, key, i)` for all valid arguments. Two calls with equal
   `(period, key, i)` return equal `int` values.
2. `bidder.sawtooth(n, count).at(K)` is a pure function of `(n, K)`
   for all valid arguments. The value does not depend on `count`
   beyond the `K < count` validity check.
3. For any valid `B = bidder.cipher(period, key)`:
   `sorted(list(B)) == list(range(period))`. Iterating a
   `BidderBlock` yields a permutation of `[0, period)`.
4. For any valid `S = bidder.sawtooth(n, count)`:
   `list(S)` is strictly increasing.
5. For any valid `S = bidder.sawtooth(n, count)` and any `K` in
   `[0, count)`: `S.at(K) % n == 0` and `S.at(K) % (n * n) != 0`.
6. `len(obj) == obj.period` for both object types.
7. `iter(obj)` returns a fresh generator on every call. Two
   generators obtained from the same object advance independently.
8. `next(obj)` raises `TypeError` for both object types.
9. `.at(i)` is deterministic across repeated calls on the same
   instance, and across distinct instances constructed with equal
   arguments.
10. `BidderBlock` and `NPrimeSequence` instances hold no mutable
    public state; there is no method that causes a subsequent call
    with the same arguments to return a different value.


## Performance

`bidder` is pure Python. There is no C extension, no NumPy
dependency, and no JIT. Each `.at(i)` call runs several rounds of
a Feistel cipher in interpreted Python.

For small to moderate workloads — iterating a `BidderBlock` of
period 10,000, or calling `.at(i)` in a loop up to a few million
times — this is fast enough to be imperceptible. For workloads
that call `.at()` hundreds of millions of times (for example,
using a `BidderBlock` as a per-element random number source for a
large Monte Carlo simulation), the per-call overhead adds up.
Generating 20,000 full permutations of period 20,000 takes
roughly 20 minutes on a 2020-era laptop.

This is a known property of the implementation, not a bug. The
design trades speed for simplicity: no compilation step, no
platform-specific binaries, no build dependencies. If a workload
is bottlenecked on `.at()` throughput, the correct response is to
restructure the workload (precompute and cache with `list(B)`,
reduce the number of calls, or batch with `iter(B)`), not to
rewrite the cipher backend.

A C implementation with the same contract is available as
`bidder_c`. It requires compilation (`make`) and exposes the same
`cipher` and `sawtooth` functions via a ctypes wrapper. The C path
is roughly 1000x faster for `.at()` throughput. Both packages ship
the same `BIDDER.md` and have identical behavior on all valid
inputs.


## Recipes

Patterns built on the primitive surface. Each recipe is fully
specified by `bidder`'s public contract — no hidden state, no
additional runtime assumptions — and its correctness follows from the
invariants above.

### Uniform symbols over a chosen alphabet

To obtain a keyed, deterministic sequence of symbols drawn from an
alphabet of size `k`, where every symbol appears exactly `m` times and
the order is a keyed permutation: pick `period = k * m`, construct a
`BidderBlock`, and reduce each output modulo `k`.

```python
import bidder

k = 9
m = 1000
B = bidder.cipher(period=k * m, key=b'instrument-check')
symbols = [(B.at(i) % k) + 1 for i in range(B.period)]
assert len(symbols) == k * m
assert all(1 <= s <= k for s in symbols)
for s in range(1, k + 1):
    assert symbols.count(s) == m
print("ok")
```

Output:

```
ok
```

Why this works: `B.at` is a bijection on `[0, k*m)` (invariant 3), so
the preimage of each residue class modulo `k` has exactly `m`
elements. Reducing modulo `k` therefore yields each of the `k`
residues exactly `m` times. Adding `1` shifts the alphabet to
`{1, 2, ..., k}`; the `+ 1` is a presentation choice, not a
correctness requirement.

The order in which symbols appear is a keyed permutation: different
keys give different orders, and a fresh `BidderBlock` constructed
with the same `(period, key)` reproduces the same order exactly.

The construction requires `k * m <= bidder.MAX_PERIOD_V1`. Any `k`
and `m` with `k >= 2`, `m >= 1`, and `k * m <= 4294967295` are
accepted.


## Examples

Every example below is runnable verbatim in a Python process that
has `bidder` importable. The printed output shown is exact.

### Example 1 — build and iterate both paths

```python
import bidder

B = bidder.cipher(period=10, key=b'doc')
S = bidder.sawtooth(n=2, count=5)
print(list(B))
print(list(S))
```

Output:

```
[0, 4, 8, 1, 7, 6, 9, 3, 2, 5]
[2, 6, 10, 14, 18]
```

### Example 2 — random access

```python
import bidder

B = bidder.cipher(period=50, key=b'mix')
S = bidder.sawtooth(n=7, count=50)
print(B.at(0), S.at(0))
```

Output:

```
7 7
```

Both values are `7` for the specific arguments shown. `S.at(0)`
equals `n` for every call to `bidder.sawtooth` because the smallest
positive multiple of `n` that is not a multiple of `n*n` is `n`
itself. `B.at(0)` depends on the key and has no analogous identity.

### Example 3 — sawtooth at large index

```python
import bidder

S = bidder.sawtooth(n=2, count=2**40)
print(S.at(2**40 - 1))
```

Output:

```
4398046511102
```

The `(2**40)`-th 2-prime, computed by constant-time integer
arithmetic; no enumeration of preceding elements.

### Example 4 — concurrent independent iteration

```python
import bidder

B = bidder.cipher(period=5, key=b'iter')
it1 = iter(B)
it2 = iter(B)
print(next(it1), next(it1), next(it2))
```

Output:

```
0 1 0
```

`it1` and `it2` are independent generators: advancing `it1` twice
did not advance `it2`, so `next(it2)` returned the first element
again.

### Example 5 — period above the cap is refused

```python
import bidder

try:
    bidder.cipher(period=2**32, key=b'doc')
except bidder.UnsupportedPeriodError as e:
    print(type(e).__name__, "|", str(e))
```

Output:

```
UnsupportedPeriodError | period 4294967296 exceeds maximum of 4294967295
```

### Example 6 — permutation invariant

```python
import bidder

B = bidder.cipher(period=16, key=b'pi')
assert sorted(B) == list(range(16))
print("ok")
```

Output:

```
ok
```

### Example 7 — sawtooth ascending and divisibility invariants

```python
import bidder

S = bidder.sawtooth(n=5, count=20)
lst = list(S)
assert lst == sorted(lst)
assert all(x % 5 == 0 and x % 25 != 0 for x in lst)
print("ok")
```

Output:

```
ok
```
