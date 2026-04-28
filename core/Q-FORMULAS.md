# Q-Formulas

This is the algebraic core behind `core/FINITE-RANK-EXPANSION.md`.
It records exact formulas for

    Q_n(m) = Λ_n(m) / log(m)

inside the ACM monoid `M_n = {1} ∪ nZ_{>0}`. The formulas are local
and base-agnostic. They do not see digit concatenation, cutoff effects,
or continued-fraction geometry.


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

Thus the split is no longer merely empirical. The experiment found the
visible shadow of the binomial-product coefficients.


## Scope

The master expansion covers all heights and all factorizations of `n`.
The displayed tables cover the current panel: primes, `n = 4`, and
squarefree two-prime rows through `h = 4`. Height `h = 5` and mixed
exponent multi-prime examples such as `n = 12` require no new formula,
but they are not tabulated here.

A useful implementation check is exact Fraction equality between the
master expansion and `experiments/acm-flow/payload_q_scan.csv`, followed
by table checks for the displayed specialisations. Any mismatch should
be a coefficient transcription error or a missing overlap sub-case.

This document is not a sign-classification theorem and not a statement
about normality. It is the local algebraic formula sheet for `Q_n`.
