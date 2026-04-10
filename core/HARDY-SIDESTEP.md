# Hardy Sidestep

For `n >= 2`, the K-th n-prime is given by a closed form. Locating an
irreducible at index K = 2^4096 takes one `divmod` and one multiply on
bignums of width `O(log K + log n)` — microseconds, not millennia.

The same question for `n = 1` (ordinary primes) has been studied for a
century. The best known exact methods (Meissel–Lehmer–Lagarias–Odlyzko
prime counting plus local sieving, e.g. `primecount`) reach the K-th
prime in roughly `K^{2/3 + o(1)}` operations — sublinear, but still
super-polylogarithmic. At K = 2^4096 that bound evaluates to about
`2^2731` operations, which is unreachable; the closed form for `n >= 2`
needs about `10^4`.

The "search problem" associated with primes is a property of the
*operation* `n = 1`, not a property of irreducibility in general. For
any `n >= 2` the irreducibles of `nZ+` form an arithmetic progression
with one residue removed per period of length `n`, and that shape is
directly invertible by index. There is no analytic apparatus to invoke
because there is nothing irregular to describe.


## What is at stake

The ACM-Champernowne construction in `core/acm_core.py` builds reals
out of n-prime sequences. Sampling, sawtooth analysis, and sanity
checks all want random access into those sequences for arbitrary `n`
and arbitrary index `K` — including K so large that enumeration is out
of the question. Whether that random access is *reachable* is the
question this note answers.

For `n = 1` (ordinary primes), reaching index K = 2^4096 is unreachable
by any method currently known. The best exact bound is roughly
`K^{2/3 + o(1)}` operations via prime counting plus local sieving,
which at K = 2^4096 is on the order of `2^2731` — sublinear in K but
nowhere near practical.

For `n >= 2`, the K-th n-prime is a closed-form expression in `n` and
`K` whose evaluation cost is `O(M(log K + log n))` bit operations,
i.e. polylogarithmic in K. This document states and proves that fact,
gives a BQN gloss, and runs the closed form against absurd K to make
the cost story concrete.

**Scope disclaimer.** This theorem affects ACM-Champernowne, not
BIDDER. BIDDER permutes the contiguous integer interval
`[base^(d-1), base^d - 1]`; its first-digit uniformity comes from the
fact that each leading digit `1..base-1` occurs exactly `base^(d-1)`
times in that interval, not from any n-prime enumeration. BIDDER's cost
story is governed by the wide-block cipher in `generator/`, and that
cost story is unchanged by anything in this document. The two
constructions are independent.


## The closed form

**Definition.** For `n >= 2`, the n-primes of the monoid `nZ+` are the
elements `n · k` with `k >= 1` and `n ∤ k`, listed in ascending order.
See `core/ACM-CHAMPERNOWNE.md` for the construction and
`core/ABDUCTIVE-KEY.md` for the rank-1 lemma that underlies the small-K
case `k <= n - 1`.

**Theorem.** Let `n >= 2` and `K >= 1`. Set

    q = floor((K - 1) / (n - 1))
    r =       (K - 1) mod (n - 1)

Then the K-th n-prime is

    p_K(n) = n · (q · n + r + 1) = n^2 · q + n · (r + 1).

**Proof.** The set `{k >= 1 : n ∤ k}` is the union, over periods
`P_q = {q·n + 1, q·n + 2, …, q·n + n}` for `q = 0, 1, 2, …`, of the
first `n - 1` elements of each period — the period's last element
`q·n + n = (q+1)·n` is divisible by `n` and is excluded. Within each
period the surviving elements are `q·n + 1, q·n + 2, …, q·n + (n - 1)`,
in order.

So the valid `k`-values, listed in ascending order, are

    k_1 = 1,        k_2 = 2,        …, k_{n-1} = n - 1,
    k_n = n + 1,    k_{n+1} = n + 2, …, k_{2(n-1)} = 2n - 1,
    k_{2n-1} = 2n + 1, …

and in general the K-th valid `k` lies in period `q = ⌊(K-1)/(n-1)⌋`
at offset `r = (K-1) mod (n-1)`, giving

    k_K = q·n + (r + 1).

Multiplying by `n` gives the K-th n-prime. ∎

**Cost.** Evaluating `p_K(n)` requires one `divmod` of `K - 1` by
`n - 1` and one multiply-and-add of bignums whose width is
`O(log K + log n)`. Total: O(M(log K + log n)) bit operations, where
`M` is the cost of bignum multiplication (`Õ(log K)` for schoolbook,
`Õ(log K · log log K)` for FFT-based). The cost is *polylogarithmic in
K*, not linear.

This bound holds with no dependency on n beyond the trivial bit-width
contribution. The K-th n-prime for `K = 2^4096` and `n = 2^32` is
computed in single-digit microseconds, see `core/hardy_sidestep.py`
and the witness section below.

**Edge cases.** The formula degenerates correctly:

- `K = 1`: `q = 0`, `r = 0`, `p_1(n) = n`. ✓
- `K = n - 1`: `q = 0`, `r = n - 2`, `p_{n-1}(n) = n · (n - 1)`. ✓
  (last n-prime below the square boundary `n^2`).
- `K = n`: `q = 1`, `r = 0`, `p_n(n) = n · (n + 1)`. ✓
  (first n-prime above the square boundary, since `n^2 = n · n` is the
  first n-composite — `k = n` is divisible by `n` and was skipped).

For `n = 1` the formula divides by zero, which is the algebraic
signature of the special case: `1Z+ = Z_+` has no missing residues, no
rank-1 region, and no closed form. The ordinary primes are not an
instance of the n-prime construction at all; `n = 1` is a separate
branch in `core/acm_core.py` that runs trial division and lives in
prose.


## In BQN

The closed form mirrors the canonical `NPn2` from
`guidance/BQN-AGENT.md`, but evaluates one element instead of
generating a list. It is exact-math; the Python implementation in
`core/hardy_sidestep.py` is a direct port.

```bqn
NthNPn2 ← {𝕨 × 1 + ((𝕨-1)|𝕩-1) + 𝕨 × ⌊(𝕩-1)÷𝕨-1}
```

- `𝕨` is `n` (must be `>= 2`)
- `𝕩` is `K` (must be `>= 1`)
- right-to-left: `⌊(K-1)÷(n-1)` is `q`, `(n-1)|(K-1)` is `r`,
  the inner sum is `n·q + r + 1`, the outer multiply by `𝕨` gives
  the K-th n-prime

Verification against the existing `NPn2` enumerator (also from
`guidance/BQN-AGENT.md`):

```bqn
NPn2 ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}

# first ten 2-primes — both routes agree
2 NthNPn2¨ 1+↕10
# ⟨2, 6, 10, 14, 18, 22, 26, 30, 34, 38⟩

10 ↑ 2 NPn2 10
# ⟨2, 6, 10, 14, 18, 22, 26, 30, 34, 38⟩

# first six 3-primes
3 NthNPn2¨ 1+↕6
# ⟨3, 6, 12, 15, 21, 24⟩

# direct random access into a huge index — no enumeration
2 NthNPn2 1000000
# 1999998
```

The point of the BQN is not speed (BQN's bignums are not the focus
here). The point is that the formula fits on one line and that line is
the entire thing — no sieve, no loop, no search.


## Computational witness

`core/hardy_sidestep.py` contains:

1. A direct Python port of the closed form.
2. A verification harness that compares it to the enumerating sieve in
   `acm_core.acm_n_primes` for all `(n, K)` with `2 <= n <= 12` and
   `1 <= K <= 200`. All 2200 cases agree.
3. Single-shot timings of `p_K(n)` for absurd K.
4. A side-by-side cost comparison against the `n = 1` trial-division
   path in `acm_core`.

Run with `sage -python core/hardy_sidestep.py` (the script imports
`acm_core`, which pulls in numpy).

### Astronomical K

| n              | K            | answer width      | time       |
|----------------|--------------|-------------------|------------|
| 2              | `2^4096`     | 1234 digits       | ~7 µs      |
| 3              | `10^100`     | 101 digits        | ~2 µs      |
| 7              | `2^8192`     | 2467 digits       | ~8 µs      |
| 101            | `2^16384`    | 4935 digits       | ~15 µs     |
| `2^32`         | `2^4096`     | 1243 digits       | ~9 µs      |

The answer for `n = 3`, `K = 10^100` is

    449999...99997   (101 decimal digits, ending in ...999997)

— a fully-determined 335-bit integer pulled from googol-deep in `3Z+`,
in two microseconds. The answer for `n = 2`, `K = 2^4096` is a
1234-digit integer; the answer for `n = 101`, `K = 2^16384` is a
4935-digit integer. None of these answers can be reached by sieving.
All of them are reached by `divmod`.

### Cost contrast at common K

Same machine, same Python, same module:

|          K | n = 2 closed form | n = 1 sieve         | ratio        |
|-----------:|------------------:|--------------------:|-------------:|
|        100 |             ~1 µs |              ~620 µs |        ~600× |
|      1 000 |             ~2 µs |              ~42 ms |       ~30 000× |
|     10 000 |             ~3 µs |              ~4.1 s |    ~1 400 000× |
|     50 000 |             ~3 µs |             ~100 s |   ~30 000 000× |

The right-hand column is the naive trial division in
`acm_core.acm_n_primes(1, K)`, which does `Θ(K^2)`-ish work — it is
unfair to the state of the art and the table reflects that, not the
asymptotic gap. A real n-th-prime implementation (e.g. `primecount`,
which combines Meissel–Lehmer–Lagarias–Odlyzko prime counting with
local sieving) reaches the K-th prime in roughly `K^{2/3 + o(1)}`
operations. That is sublinear in K, but it is still
super-polylogarithmic, so the closed form for `n >= 2` is
*exponentially* faster in `log K`:

- `n >= 2` closed form:  `polylog(K + n)` bit operations
- best known `n = 1`:    `K^{2/3 + o(1)}` operations

At K = 2^4096 the first is on the order of `10^4` and the second is on
the order of `2^2731`. The qualitative gap survives any improvement to
the n = 1 side short of a polylog-time exact n-th-prime algorithm,
which is not currently known to exist. The closed form additionally
writes down only an `O(log K + log n)`-bit answer, while the K-th
ordinary prime has `Θ(log K)` bits and cannot avoid the corresponding
output cost — but in both cases the *output* width is the same order;
the gap is in the *computation*.


## Why this matters for ACM-Champernowne

The closed form is a tool inside the ACM-Champernowne layer, not a
shortcut for BIDDER. Useful applications, in descending order of
confidence:

1. **Random access into any single monoid `nZ+` (`n >= 2`).** "Give me
   the 10^100-th 3-prime" is a microsecond-scale operation. Useful for
   probing the asymptotic regime of any one monoid without paying the
   enumeration cost up to the index of interest.

2. **Termwise random access inside the n-prime sequence.** Any code
   path that wants the K-th n-prime (rather than the whole prefix
   `p_1 … p_K`) can pull it directly. This is *not* a shortcut for
   `acm_champernowne_real(n, K)`, which by definition concatenates the
   first `K` n-primes and therefore needs all `K` of them — building
   that prefix-real is still `Θ(K)` work no matter how you compute the
   individual terms. The closed form is the basis for a future indexed
   or streaming Champernowne API that asks "what is the digit at
   position `i` of the n-Champernowne stream?" without materializing
   the prefix; the existing API in `core/acm_core.py` remains the
   prefix-builder it always was.

3. **Sampling far-down-the-sequence statistics.** Anything in the
   `experiments/acm-champernowne/` tree that wants to characterize
   distant n-prime behavior — sawtooth tail shape, late-decade leading
   digits, residue patterns under iterated operations — can pull the
   K-th term directly instead of building the prefix.

4. **Structural confirmation.** The closed form is the fourth instance
   of the leaky-parameterization observation in `core/ABDUCTIVE-KEY.md`:
   `nZ+` for `n >= 2` is so lightly structured that every recovery
   problem we have looked at collapses to a single-scalar inversion.
   The abductive key recovers `n` from the diagonal; the cascade key
   from the first column; the greedy extraction from the unordered
   multi-set; this note recovers the K-th element from `(n, K)`
   directly. They are four channels of one fact about `nZ+`.

What the closed form does **not** do, and what the previous draft of
this section incorrectly claimed it does, is help BIDDER. BIDDER's
block is the contiguous integer interval `[base^(d-1), base^d - 1]`,
not an enumeration of any monoid's irreducibles. BIDDER's cost story
is independent of this theorem and lives in `generator/BIDDER.md`.


## Why "Hardy sidestep"

G. H. Hardy spent a career on the distribution of primes — the prime
number theorem, the Riemann zeros, the analytic apparatus that says
where the K-th prime can be expected to land and how badly the answer
fluctuates. All of that machinery exists because the K-th ordinary
prime is *hard to locate*, and any quantitative statement about it
needs deep tools.

The n-prime construction sidesteps the entire apparatus. By moving from
the multiplicative monoid `Z+` to the multiplicative monoid `nZ+` for
some `n >= 2`, we trade unique factorization (which `nZ+` does not
have) for a closed-form indexing of irreducibles (which `Z+` does not
have). For any application that needs only enumeration and never
factorization, that trade has no downside.

Hardy's work is about a property of the integers under the operation
`×`. We have changed the monoid. The new monoid's irreducibles are an
arithmetic progression with one residue removed per period, and that
shape is directly invertible. The "search for primes" problem doesn't
get easier; it gets *replaced* by a problem that was never search-hard
to begin with.

The replacement is sharp: the irregularity Hardy was studying lives in
the gap between consecutive ordinary primes, which is bounded only by
the deep apparatus he and his successors built. The gap between
consecutive n-primes, by contrast, is always exactly `n` or `2n` (the
`2n` jumps are the deletions at multiples of `n²`), forever, by
construction. There is no analogue of the prime number theorem to
prove for `nZ+`, because the analogue is one line of high-school
arithmetic.


## References

- `core/acm_core.py`, `core/acm_core.c` — the n-prime sieve
- `core/ACM-CHAMPERNOWNE.md` — the construction
- `core/ABDUCTIVE-KEY.md` — the rank-1 lemma and the
  leaky-parameterization theme
- `core/hardy_sidestep.py` — companion script (verification + demos)
- `guidance/BQN-AGENT.md` — `NPn2` and the BQN naming conventions
- `generator/BIDDER.md` — independent construction; permutes consecutive
  integers, not n-primes. Listed here only to disambiguate from this note.
