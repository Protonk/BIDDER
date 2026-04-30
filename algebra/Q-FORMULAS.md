# Q-Formulas

This is the algebraic core behind `algebra/FINITE-RANK-EXPANSION.md`.
It records exact formulas for

    Q_n(m) = Λ_n(m) / log(m)

inside the ACM monoid `M_n = {1} ∪ nZ_{>0}`. The formulas are local
and base-agnostic. They do not see digit concatenation, cutoff effects,
or continued-fraction geometry.


## Object

The monoid `M_n = {1} ∪ nZ_{>0}` has Dirichlet series

    ζ_{M_n}(s) = Σ_{m ∈ M_n} m^{-s} = 1 + n^{-s} ζ(s).

`Q_n` is the log-coefficient of this generating function:

    Q_n(m) = [m^{-s}] log ζ_{M_n}(s)
           = [m^{-s}] log(1 + n^{-s} ζ(s)).

This is the `M_n`-monoid analog of the classical fact

    Λ(n) / log n = [n^{-s}] log ζ(s).

The formulas in the rest of this document are evaluations of that one
coefficient at specific `m`, obtained by Mercator expansion of the log
and multiplicativity of the resulting `τ_j` coefficients at the primes
of `n`.

Caveat. `ζ_{M_n}(s) = 1 + n^{-s} ζ(s)` does not have an Euler product
over the atoms of `M_n` (the monoid is not UF — e.g. `36 = 6·6 = 2·18`
in `M_2`). Formal Mercator manipulations carry over from classical
`Λ / log` for free; deeper analytic content (Tauberian theorems beyond
the formal level, residue arguments, sieve identities exploiting
multiplicativity at the prime level) needs individual translation, not
free analogy. The right literature for sharpening the analytic
mileage of `Q_n` is non-UF arithmetic semigroup theory — Beurling
generalised primes, Diamond–Zhang on arithmetic semigroups — rather
than classical multiplicative number theory, which assumes the Euler
product the M_n monoid does not provide.


## Universal Formula

Let `m ∈ M_n` have exact height

    h = ν_n(m),

so `m = n^h k` with `n ∤ k`. Then

    Q_n(m) =
        Σ_{j=1}^h (-1)^(j-1) τ_j(m / n^j) / j.

Here `τ_j(x)` is the ordered `j`-fold divisor function:

- `τ_1(x) = 1`.
- `τ_2(x) = d(x)`, the usual divisor count.
- `τ_j` is multiplicative on coprime factors.
- For prime powers, `τ_j(p^e) = C(e + j - 1, j - 1)`.

This already gives the finite-rank closure: no term above `j = h`
can occur.


## Master Expansion

Factor

    n = p_1^{a_1} p_2^{a_2} ... p_r^{a_r}

and decompose the payload relative to these primes:

    k = p_1^{t_1} p_2^{t_2} ... p_r^{t_r} k',
    gcd(k', n) = 1.

The exact-height condition `n ∤ k` means at least one `t_i < a_i`.
The other `t_i` may be arbitrarily large.

For each `j`,

    m / n^j =
        p_1^{a_1(h-j)+t_1} ... p_r^{a_r(h-j)+t_r} k',

so multiplicativity gives

    τ_j(m / n^j)
        = τ_j(k') ·
          ∏_{i=1}^r C(a_i(h-j) + t_i + j - 1, j - 1).

Therefore

    Q_n(m)
        = Σ_{j=1}^h (-1)^(j-1)
            [∏_{i=1}^r C(a_i(h-j) + t_i + j - 1, j - 1)]
            · τ_j(k') / j.

Every formula below is this master expansion with specific
`(a_i, t_i)`.


### BQN Annotation

The master expansion as small specialisations. The general form
`Qn` is in `algebra/FINITE-RANK-EXPANSION.md` ("BQN Annotation");
this block adds the specific row formulas tabulated above as
short one-liners. They are implementation mirrors of the
corresponding rows of `algebra/predict_q.py:q_value_by_class`.

Assume `Tau` is in scope from `algebra/FINITE-RANK-EXPANSION.md`
(ordered divisor count, `2 Tau x = d(x)`).

```bqn
# Universal cliff at h = 2 (any n, any k):
#   Q_n(n²k) = 1 - d(k)/2.
H2 ← {1 - (2 Tau 𝕩) ÷ 2}

# Prime n at h = 3 with gcd(p, k) = 1:
#   Q_p(p³k) = 1 - d(k) + τ_3(k)/3.
PrimeH3 ← {(1 - 2 Tau 𝕩) + (3 Tau 𝕩) ÷ 3}

# Binomial coefficient C(𝕩, 𝕨), used in master-expansion derivations.
Choose ← {(!𝕩) ÷ (!𝕨) × !𝕩-𝕨}
```

Status:

- These specialisations return floats; the rationals in the
  tables above (e.g. `Q_3(3³ · 1) = 1/3`) are computed by
  `algebra/predict_q.py` over `Fraction`. The BQN block matches
  the algebra, not the arithmetic precision.
- The factored class form (with `shape` of `n` and τ-signature of
  `k'` as keys) is intrinsically multi-argument and reads more
  cleanly as `q_value_by_class(shape, h, tau_sig)` in Python than
  as a BQN one-liner. This block does not attempt the general
  factored evaluator — `algebra/predict_q.py` is the canonical
  implementation. BQN here is for the displayed row formulas.

Reference values (verify against `algebra/test_anchors.py` or
the Prime-n table at `h = 3`):

- `H2 1` = `0.5`  (universal cliff at `k = 1`:
  `1 - d(1)/2 = 1 - 1/2 = 1/2`).
- `H2 6` = `−1`  (universal cliff at `k = 6`:
  `1 - d(6)/2 = 1 - 4/2 = -1`).
- `PrimeH3 1` = `0.33...`  (prime-row identity
  `Q_p(p³ · 1) = 1/h = 1/3`).
- `PrimeH3 2` = `0`  (low-payload zero band, `k = q` for any
  prime `q ≠ p`: `1 - d(2) + τ_3(2)/3 = 1 - 2 + 3/3 = 0`,
  matching the prime row of the `h = 3` table).
- `PrimeH3 4` = `0`  (`k = q²` zero, `τ_3(4) = C(2+2, 2) = 6`:
  `1 - 3 + 6/3 = 0`).
- `PrimeH3 6` = `0`  (`k = qr` zero, `τ_3(6) = τ_3(2)·τ_3(3) =
  9`: `1 - 4 + 9/3 = 0`).


## Integer-Language Reading

The master expansion has a clean combinatorial interpretation.
`τ_j(m / n^j)` counts ordered j-tuples `(d_1, …, d_j)` with
`d_1 · … · d_j = m / n^j`, equivalently ordered j-tuples
`(n d_1, …, n d_j)` with product `m` whose every factor is a multiple
of `n`. So:

    Q_n(m) = Σ_{j=1}^{ν_n(m)}
             (-1)^(j-1) · #{ordered factorisations of m into j multiples of n} / j.

`Q_n(m)` is a signed Möbius-style count of ordered factorisations of
`m` into multiples of `n`, alternating by tuple length, weighted
`1/j`. The master expansion above is just this count reorganised by
sorting `m` into `(h, t_1, …, t_r, k')` and using multiplicativity of
`τ_j`. The two readings — generating-function log-coefficient and
signed factorisation count — are the same fact in two languages. Pick
whichever serves the next move (analytic / combinatorial).


## Prime n

If `n = p`, exact height forces `p ∤ k`, so `k = k'` and

    Q_p(p^h k)
        = Σ_{j=1}^h
            (-1)^(j-1) C(h - 1, j - 1) τ_j(k) / j,
        gcd(p, k) = 1.

Direct expansion gives:

| h | Q_p(p^h k) | sign profile |
|---|---|---|
| 1 | `1` | positive |
| 2 | `1 - d(k)/2` | negative iff `d(k) >= 3` |
| 3 | `1 - d(k) + τ_3(k)/3` | always `>= 0` |
| 4 | `1 - 3d(k)/2 + τ_3(k) - τ_4(k)/4` | mixed |
| 5 | `1 - 2d(k) + 2τ_3(k) - τ_4(k) + τ_5(k)/5` | mixed |

At `h = 3`, prime rows have the low-payload zero band seen in the
experiments:

| k | Q_p(p³k) |
|---|---|
| `1` | `1/3` |
| `q`, `q²`, or `qr` with primes `q,r != p` | `0` |
| larger coprime payloads | non-negative |


## Prime Powers

Let `n = p^a`, `a >= 2`. Write `k = p^t k'` with `0 <= t < a` and
`gcd(p, k') = 1`. Then

    Q_{p^a}(p^{ah+t} k')
        = Σ_{j=1}^h (-1)^(j-1)
            C(a(h-j) + t + j - 1, j - 1) τ_j(k') / j.

For the panel case `n = 4 = 2²`:

| h | t | Q_4 |
|---|---|---|
| 1 | 0 | `1` |
| 1 | 1 | `1` |
| 2 | 0 | `1 - d(k')/2` |
| 2 | 1 | `1 - d(k')` |
| 3 | 0 | `1 - 3d(k')/2 + τ_3(k')/3` |
| 3 | 1 | `1 - 2d(k') + τ_3(k')` |
| 4 | 0 | `1 - 5d(k')/2 + 2τ_3(k') - τ_4(k')/4` |
| 4 | 1 | `1 - 3d(k') + 10τ_3(k')/3 - τ_4(k')` |

The `t = 1` rows look sharper because the formula is written in the
reduced coprime payload `k'`. Against the full payload `k`, the
rank-2 identity is universal:

    Q_n(n²k) = 1 - d(k)/2.

At `h = 3`, `n = 4` already differs from the prime case:

| payload case | Q_4 |
|---|---|
| `t = 0, k' = 1` | `-1/6` |
| `t = 0, k' = q` | `-1` |
| `t = 1, k' = 1` | `0` |
| `t = 1, k' = q` | `0` |


## Squarefree Multi-Prime n

Let `n = p_1 ... p_r` be squarefree with `r >= 2`. The exact-height
condition says at least one `t_i = 0`. The master expansion becomes

    Q_n(m)
        = Σ_{j=1}^h (-1)^(j-1)
            [∏_{i=1}^r C(h + t_i - 1, j - 1)]
            · τ_j(k') / j.

For the panel cases `n = 6` and `n = 10`, `r = 2`.

At `h = 2` all sub-cases reduce to the universal cliff:

    Q_n(n²k) = 1 - d(k)/2.

At `h = 3`:

| overlap case | Q_n |
|---|---|
| `(0, 0)` | `1 - 2d(k') + τ_3(k')/3` |
| `(t, 0)`, `t >= 1` | `1 - (t+2)d(k') + ((t+2)(t+1)/2) τ_3(k')/3` |
| `(0, t)`, `t >= 1` | symmetric |

In the coprime-payload case `(0,0)`, small payloads are negative:

| k' | Q_n |
|---|---|
| `1` | `-2/3` |
| `q` | `-2` |
| `q²` | `-3` |
| `qr` | `-4` |

Overlap cases with large `t` can transition, so the correct statement
is not global nonpositivity. It is that low-overlap squarefree
multi-prime rows are negative-dominated at `h = 3`.

At `h = 4` for `r = 2`:

| overlap case | Q_n |
|---|---|
| `(0, 0)` | `1 - 9d(k')/2 + 3τ_3(k') - τ_4(k')/4` |
| `(t, 0)`, `t >= 1` | `1 - 3(t+3)d(k')/2 + ((t+3)(t+2)/2)τ_3(k') - ((t+3)(t+2)(t+1)/24)τ_4(k')` |
| `(0, t)`, `t >= 1` | symmetric |


## Panel Reading

The Phase 1 prime / prime-power / multi-prime split at `h = 3` is a
corollary of these formulas.

| n type | h = 3 behaviour |
|---|---|
| prime (`2,3,5`) | `Q_p >= 0`, with a low-payload zero band |
| prime power (`4`) | negative or zero in the first `t` sub-cases |
| squarefree multi-prime (`6,10`) | negative in low-overlap payloads; overlap can transition |

The trichotomy reflects the structure of `τ_j` localised at the primes
of `n`: one binomial factor when `n` is prime; one binomial with `a` in
its index when `n = p^a`; a product of binomials when `n` is multi-prime.
The displayed sign profiles are evaluations of those specialisations at
small payloads.


## Scope

The master expansion covers all heights and all factorizations of `n`.
The displayed tables cover the current panel: primes, `n = 4`, and
squarefree two-prime rows through `h = 4`. Height `h = 5` and mixed
exponent multi-prime examples such as `n = 12` require no new formula,
but they are not tabulated here.

`experiments/acm-flow/q_n_verify.py` verifies exact Fraction equality
between the master expansion and `payload_q_scan.csv`, followed by
table checks for the displayed specialisations. On the current CSV
(`n ∈ {2,3,4,5,6,10}`), the master expansion and declared
specialisations have zero mismatches.

The formulas in this document and their algebraic claims are checked
in **exact Python `Fraction` arithmetic** by
`algebra/predict_q.py` and `algebra/test_anchors.py` — no floats, no
`mpmath`, no `sympy`. Every rational displayed in this sheet is
either typed by hand against a `Fraction` value, or copied from a
`Fraction` printout of the master expansion at that cell. The chain
from the formula sheet to the implementation to the anchor harness
is rational-only.

This document is not a sign-classification theorem and not a statement
about normality. It is the local algebraic formula sheet for `Q_n`.

The formulas here compute `Q_n` at a *single* `m`. Global observables
that aggregate over many `m` — multiplication-table counts on `M_n`,
continued-fraction expansions of digit concatenations, Walsh / wavelet
readings of streams — are governed by different generating-function
objects and require their own analyses. `Q_n`'s local rank-h structure
informs those observables but does not predict them automatically. See
`experiments/acm-flow/mult-table/` and
`experiments/acm-flow/cf/` for the empirical state of those
couplings; the connections are real but at the prefactor /
sub-leading level, not at the leading exponent level.


## Pending Tables

The master expansion is universal; the displayed-table coverage in
this document is not. A future agent extending the formula sheet
should know which cells are still un-tabulated. Each gap below has
been verified to be reachable by `predict_q.q_value_by_class`
(returning exact `Fraction`s); only the human-readable table is
missing.

- **Prime n at `h = 5`.** `Q_p(p^5 k) = Σ_{j=1}^5 (-1)^{j-1}
  C(4, j-1) τ_j(k) / j` for `gcd(p, k) = 1`. Worth tabulating
  alongside the `h = 1..4` entries in §"Prime n", with an
  explicit note on the alternating-binomial kernel
  `Σ_j (-1)^{j-1} C(4, j-1) j^d = 0` for `0 ≤ d ≤ 3` (the source
  of the kernel-zero band visible in
  `q_h5_shape_tau_matrix.png`).

- **Prime n at `h = 6, 7, 8`.** Companion entries to the `h = 5`
  table. The kernel-zero set widens with `h`; the master
  expansion makes this mechanical.

- **Prime power `n = p^a`, `a = 3` (i.e. `n = 8, 27, …`).**
  `Q_{p^3}(p^{3h+t} k')` for `t ∈ {0, 1, 2}`, `gcd(p, k') = 1`.
  The §"Prime Powers" table covers `n = 4 = 2²` only.

- **Squarefree multi-prime `n` at `h = 5+`.** §"Squarefree
  Multi-Prime n" tabulates `r = 2` through `h = 4`. `h ≥ 5` and
  `r ≥ 3` (e.g. `n = 30 = 2·3·5`) follow from the master
  expansion with no new mechanism.

- **Mixed-exponent `n` such as `n = 12 = 2² · 3`.** Currently
  flagged "require no new formula, but they are not tabulated
  here." The master expansion gives them; the displayed tables
  do not.

- **The 8 × 6 (shape, τ-signature) matrix at higher `h`.** The
  matrix at `h = 5` is the canonical algebraic fingerprint
  (frozen in `algebra/test_anchors.py`). Computing the same matrix
  at `h = 6, 7, 8` and observing how the kernel-zero set evolves
  is the natural extension; this is what `algebra/HIGHER-H` —
  not yet started — would address.

- **`Q_n(n^h k)` autocorrelation closed forms.** The within-row
  autocorrelation profile (`algebra/WITHIN-ROW-PARITY.md`)
  factors as `A = Σ_{c1, c2} D(c1, c2) · V(c1) · V(c2)` where
  the **algebraic factor** `V(c) = q_value_by_class(shape, h+t,
  tau_sig)` is closed-form (exact `Fraction` via
  `algebra/predict_q.py`), and the **combinatorial factor**
  `D(c1, c2)` — the joint density of class pairs at lag `L` — is
  the open piece (a shifted-divisor-density problem in the
  Tenenbaum III §4 family). A formula sheet entry would document
  the V table per class and the structure of D, isolating the
  closed-form part from the open part.

A claim becomes a table entry once the workflow standard in
`README.md` is satisfied for it: stated, implemented, anchored,
cross-checked against the lattice if applicable, and documented.
