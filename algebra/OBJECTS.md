# Objects

Definitions used by every other file in `algebra/`. Each object is
defined exactly once here, in three forms: natural language, math,
and BQN. Other files refer to objects by name and to this file by
path; they do not redefine.

## Monoid

The ACM monoid at parameter `n ≥ 2` is

    M_n = {1} ∪ n·Z_{>0}.

Its Dirichlet series is

    ζ_{M_n}(s) = Σ_{m ∈ M_n} m^{-s} = 1 + n^{-s} ζ(s).

`M_n` is not a unique-factorisation monoid: e.g. `36 = 6·6 = 2·18`
in `M_2`. There is no Euler product over the atoms of `M_n`.

```bqn
# Atoms of M_n. Canonical form per guidance/BQN-AGENT.md §"NPn2":
# generate 𝕩×𝕨 candidate cofactors, scale by n, keep those whose
# cofactor is not divisible by n.
NPn2 ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}
```

## Q_n: the local observable

For `m ∈ M_n` with `n^h | m` for some `h ≥ 1`,

    Q_n(m) := Λ_n(m) / log(m)
            = [m^{-s}] log ζ_{M_n}(s)
            = [m^{-s}] log(1 + n^{-s} ζ(s)).

The closed-form evaluation of this coefficient is `MASTER-EXPANSION.md`.

The classical analog is `Λ(n) / log n = [n^{-s}] log ζ(s)` for ordinary
primes; `Q_n` is the `M_n`-monoid version of the same construction.

## Height

The height of `m` at parameter `n` is the largest exponent of `n`
dividing `m`:

    h := ν_n(m) = max{e ≥ 0 : n^e | m}.

We use **height** and **monoid rank** for this same number.

```bqn
# h = ν_n(m), the n-adic height.
NuP ← {0=𝕨|𝕩 ? 1+𝕨 𝕊 ⌊𝕩÷𝕨 ; 0}
```

## Decomposition

Factor `n = p_1^{a_1} ⋯ p_r^{a_r}` and write

    m = n^h · k,    k = p_1^{t_1} ⋯ p_r^{t_r} · k',    gcd(k', n) = 1.

The exact-height condition `n ∤ k` is equivalent to: `t_i < a_i` for at
least one `i`. The *shape* of `n` is the sorted-descending tuple
`(a_1, …, a_r)`. The *τ-signature* of `k'` is the sorted-descending
tuple of its prime exponents.

```bqn
# Coprime cofactor: k' = k / p^{ν_p(k)} (single-prime case).
CoprimePart ← {𝕩 ÷ 𝕨 ⋆ 𝕨 NuP 𝕩}
```

Implementations: `predict_q.factor_tuple`, `shape_of`, `tau_sig_of`,
`decompose`, `n_adic_height`.

## τ_j: ordered j-fold divisor count

`τ_j(x)` counts ordered j-tuples `(d_1, …, d_j)` of positive integers
with `d_1 ⋯ d_j = x`.

    τ_1(x) = 1.
    τ_2(x) = d(x), the usual divisor count.
    τ_j  is multiplicative on coprime factors:
                  τ_j(uv) = τ_j(u) τ_j(v) when gcd(u,v) = 1.
    τ_j(p^e) = C(e + j - 1, j - 1).

```bqn
Divs ← {ks ← 1+↕𝕩 ⋄ (0=ks|𝕩)/ks}

Tau ← {
  j ← 𝕨
  j=1 ? 1 ;
  ds ← Divs 𝕩
  +´ (j-1) Tau¨ 𝕩÷ds
}
```

Implementation: `predict_q.tau`.

## Ω, ω

For `k ≥ 1` with `k = q_1^{e_1} ⋯ q_r^{e_r}`:

    Ω(k) = e_1 + e_2 + ⋯ + e_r       (prime factors with multiplicity)
    ω(k) = r                          (distinct primes)

Implementations: `predict_q.big_omega`, `predict_q.little_omega`.

## Notation table

| object | symbol | Python | BQN |
|---|---|---|---|
| ACM monoid | `M_n` | (literal sieve) | `NPn2` |
| Dirichlet series | `ζ_{M_n}(s)` | — | — |
| local observable | `Q_n(m)` | `q_general(n, h, k)` | `Qn` (see MASTER-EXPANSION.md) |
| height | `h = ν_n(m)` | `n_adic_height(n, m)` | `NuP` (single-prime case) |
| shape of `n` | `(a_1, …, a_r)` | `shape_of(n)` | — |
| τ-signature of `k'` | `(e_1, …, e_r)` | `tau_sig_of(k)` | — |
| ordered j-fold divisor count | `τ_j(x)` | `tau(j, x)` | `Tau` |
| big omega | `Ω(k)` | `big_omega(k)` | — |
| little omega | `ω(k)` | `little_omega(k)` | — |

## Scope

The objects defined here are local: each `Q_n(m)` is the
generating-function coefficient at a single `m`. Aggregate observables
(multiplication-table counts, continued-fraction expansions, digit
statistics) live in `experiments/`; they are not redefined here.

The right literature for analytic content beyond formal Mercator
manipulations is non-UF arithmetic semigroup theory (Beurling
generalised primes, Diamond–Zhang on arithmetic semigroups), not
classical multiplicative number theory.
