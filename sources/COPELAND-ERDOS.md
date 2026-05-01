# Copeland–Erdős: density implies normality of the concatenation

Source: A. H. Copeland and P. Erdős, "Note on Normal Numbers,"
*Bulletin of the American Mathematical Society* 52 (1946),
857–860.

This document records the theorem statement and proof sketch in
this project's notation, and what it settles for ACM-Champernowne.
It is an internal summary; the user holds the original paper.


## The theorem

Let `A = (a_1 < a_2 < a_3 < …)` be an increasing sequence of
positive integers, and let

    π_A(N) = #{ k : a_k ≤ N }

be its counting function. Suppose

    for every ε > 0,    π_A(N) > N^{1 − ε}    eventually.

Then for every base `b ≥ 2`, the real number

    α_A(b) := 0.a_1 a_2 a_3 …

(concatenation of the `a_k` written in base `b` and placed after
the decimal point) is **normal in base `b`**.

Normal in base `b` means: for every `k ≥ 1` and every length-`k`
digit string `σ ∈ {0, 1, …, b − 1}^k`, the asymptotic frequency
of occurrences of `σ` in the base-`b` digit expansion of `α_A(b)`
equals `b^{−k}`.


## Proof sketch (this project's framing)

The argument proceeds by counting occurrences of length-`k`
digit strings in the base-`b` concatenation. Two contributions:

1. **Internal substrings.** For each `a_i` of digit length `d_i`,
   the base-`b` representation of `a_i` contains `d_i − k + 1`
   length-`k` substrings entirely internal to `a_i`. Summed over
   the sequence up to `N`, these dominate the digit count.

2. **Boundary substrings.** Substrings that straddle the boundary
   between consecutive `a_i, a_{i+1}` contribute `O(k)` per
   element, so the total boundary contribution is `O(k · |A(N)|)`.
   For `k` fixed and `|A(N)| → ∞`, this is `o(D_N)` where `D_N`
   is the total digit count, since the average digit length per
   element grows (`d_i = ⌊log_b a_i⌋ + 1` is unbounded as `i → ∞`).

The internal contribution is controlled by an equidistribution
argument: for "most" large integers `m` written in base `b`,
every length-`k` substring appears at frequency near `b^{−k}`.
The density bound `π_A(N) > N^{1 − ε}` ensures `A` contains
"enough" such large integers — specifically, enough that the
exceptional set (integers whose base-`b` representation is
substantially non-uniform at length `k`) has density too small
to spoil the frequency count.

The result is the asymptotic frequency `b^{−k}` for every length-`k`
string `σ`, in the limit. Normality in base `b`.


## Headline application

The primes `2, 3, 5, 7, 11, …` satisfy the density condition by
the prime number theorem (`π(N) ~ N / log N`, which exceeds
`N^{1 − ε}` for every `ε > 0` eventually). So

    0.235 7 11 13 17 19 23 …    (concatenation of primes in base 10)

is normal in base 10. The result extends to every base, with the
primes written in that base.


## Application to ACM-Champernowne

For prime `n`, the n-prime sequence

    p_K(n) = n · c_K,    c_K = qn + r + 1, (q, r) = divmod(K − 1, n − 1)

has density `(n − 1) / n²` in the integers: the count of n-primes
`≤ N` is

    π_A(N) = (n − 1) N / n² + O(1).

This is *linear* in `N`, far exceeding `N^{1 − ε}` for any `ε > 0`.
Copeland–Erdős applies directly.

**Theorem (C–E applied to ACM-Champernowne, prime `n`).** For
every prime `n ≥ 2` and every base `b ≥ 2`, the real number

    C_b(n) = 0.p_1(n) p_2(n) p_3(n) …

(concatenation of n-primes in base `b`, in increasing order) is
normal in base `b`.

This is the project's first-order normality result. It is *not*
on the open list. The interesting open question — what the
manifesto in `THE-OPEN-HEART.md` commits to — is **absolute
normality**: normality in *every* base, not just the base of
concatenation.


## What it does not settle

- **Absolute normality.** C–E proves normality in the base of
  concatenation only. Classical Champernowne (`0.123456789101112…`)
  is normal in base 10 (Champernowne 1933, recovered by C–E 1946);
  its normality in any other base is *open*. ACM-Champernowne
  inherits the same gap: `C_b(n)` is normal in base `b` (proved
  here), normality in any base `B ≠ b` is open.

- **Refined digit statistics.** Multi-scale correlations,
  entropy bounds, normality at arbitrary block scales beyond the
  `b^{−k}`-frequency claim.

- **Continued-fraction behaviour and irrationality measure.**
  C–E gives no information about the CF expansion of `α_A(b)`.
  The irrationality measure of classical Champernowne (Mahler
  1937, `μ = 10`) is a separate result. The ACM analog —
  conditional `μ = 2 + (b − 1)(b − 2)/b` in
  `experiments/acm/cf/MU-CONDITIONAL.md` — is a separate
  thread, addressed via the spike formula and the off-spike
  denominator process, not through C–E.

- **Substrate-specific structure.** The work in `arguments/*`,
  `algebra/Q-FORMULAS.md`, `core/BLOCK-UNIFORMITY.md`, and the
  empirical phases addresses the n-prime substrate's internal
  structure. C–E proves a digit-frequency claim about the
  concatenated real but does not characterise the substrate.


## Generalisations beyond C–E

The C–E theorem has been extended in several directions over
the decades:

- **B-free integers.** For a set `B ⊆ Z_{≥ 1}`, the integers
  divisible by no element of `B` form a sequence with computable
  density. When the density satisfies the C–E condition, the
  concatenation is normal in any base. ACM n-primes are the
  B-free integers for `B = {n²}` after dividing by `n` — they fit
  this family.

- **Polynomial sequences** `p(n)` for polynomials `p` with
  rational coefficients and integer values — also normal under
  C–E-style density bounds.

- **Smooth numbers** (numbers with no prime factor exceeding a
  given bound) — analogous results hold.

The general pattern: any "sufficiently dense" computable
sequence concatenated produces a normal-in-base-of-concatenation
real. ACM-Champernowne is one entry in this family.


## Cross-references

- `core/HARDY-SIDESTEP.md` — the bijection
  `c_K = qn + r + 1` that makes the n-prime indexing concrete
  and supplies the linear density bound used here.
- `core/BLOCK-UNIFORMITY.md` — the smooth-block n-prime count
  `(b−1) b^{d−1} (n−1)/n²`, of which `(n−1)/n²` is the linear
  density rate.
- `THE-OPEN-HEART.md` — manifesto. Engages C–E directly
  as the precedent for what's settled vs what's open. The
  manifesto's commitment is to *absolute* normality, the
  refinement C–E does not address.
- `experiments/acm/cf/` — CF and irrationality-measure
  work, conditional and not addressed by C–E.
- `sources/BIDDER-AND-SON.md` — the historical lattice of
  multiplicative anatomy that the project inverts; ACM-Champernowne's
  concatenation choice puts it inside C–E's scope, where Bidder's
  multiplication-table approach to logarithms does not apply
  directly.


## Composite-`n` extension

The C–E theorem applies to the `M_n` atom sequence for any
`n ≥ 2`, not only prime `n`. The atoms are `n · c` with `n ∤ c`,
density `(n − 1) / n²` regardless of whether `n` is prime,
prime-power, or composite. Linearity of density holds; C–E
applies; `C_b(n)` is normal in base `b` for every `n ≥ 2`, every
`b ≥ 2`.

The project's panel `n ∈ {2, 3, 4, 5, 6, 10}` is therefore all
inside C–E's scope. The substrate-specific work (Q_n, mult-table,
mega-spike, BLOCK-UNIFORMITY) addresses internal structure of
already-proved-normal reals; the absolute-normality conjecture
in `THE-OPEN-HEART.md` is the genuinely open commitment
the project carries.
