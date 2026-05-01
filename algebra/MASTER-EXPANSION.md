# Master expansion

Closed-form evaluation of `Q_n(m)` for every `m ∈ M_n`. Definitions in
`OBJECTS.md`.

## Statement

Let `m ∈ M_n` with height `h = ν_n(m) ≥ 1`. Write `n = p_1^{a_1} ⋯
p_r^{a_r}` and `k = m / n^h = p_1^{t_1} ⋯ p_r^{t_r} · k'` with
`gcd(k', n) = 1` and at least one `t_i < a_i`. Then

    Q_n(m) = Σ_{j=1}^{h} (-1)^{j-1}
               [ ∏_{i=1}^{r} C(a_i (h - j) + t_i + j - 1, j - 1) ]
             · τ_j(k') / j.

## BQN

```bqn
Qn ← {
  h ← 𝕨 NuP 𝕩
  js ← 1+↕h
  sign ← ¯1⋆js-1
  terms ← js Tau¨ ⌊𝕩÷𝕨⋆js
  +´ sign × terms ÷ js
}
```

`NuP`, `Tau`, `Divs` are defined in `OBJECTS.md`.

## Proof

Apply the Mercator series `log(1 + x) = Σ_{j ≥ 1} (-1)^{j-1} x^j / j`
to `log ζ_{M_n}(s)` with `x = n^{-s} ζ(s)` (definition in
`OBJECTS.md`). The `j`-th term is `(-1)^{j-1} n^{-js} ζ(s)^j / j`.
The Dirichlet coefficient of `ζ(s)^j` at `m / n^j` is `τ_j(m / n^j)`
when `n^j | m` and `0` otherwise. Multiplicativity of `τ_j` on
coprime factors and the prime-power formula
`τ_j(p^e) = C(e + j - 1, j - 1)` give

    τ_j(m / n^j) = τ_j(k') · ∏_{i=1}^{r} C(a_i(h - j) + t_i + j - 1, j - 1),

since `m / n^j = p_1^{a_1(h-j) + t_1} ⋯ p_r^{a_r(h-j) + t_r} · k'`.
Substituting gives the statement. ∎

## Corollaries

(C1) **Rank truncation.** The `j`-sum runs from `j = 1` to
`j = ν_n(m)`; for `j > ν_n(m)`, `n^j ∤ m` and the Dirichlet
coefficient `τ_j(m / n^j)` is zero. See `RANK-LEMMA.md`.

(C2) **Prime-row identity.** For prime `p` and any `h ≥ 1`,
`Q_p(p^h · 1) = 1/h`. Proof: shape `(1,)`, `tau_sig = ()`, `t = 0`,
so the binomial factor is `C(h-1, j-1)` and `τ_j(1) = 1`; the sum
is the classical `Σ_{j=1}^{h} (-1)^{j-1} C(h-1, j-1) / j = 1/h`.
Anchored as A1 in `test_anchors.py`.

(C3) **Prime-n specialisation.** For prime `p` and `gcd(p, k) = 1`,

    Q_p(p^h k) = Σ_{j=1}^{h} (-1)^{j-1} C(h-1, j-1) τ_j(k) / j.

Proof: shape `(1,)`, `tau_sig` arbitrary, `t = 0`; the binomial
product collapses to `C(h-1, j-1)` and the master expansion reduces
as displayed.

(C4) **Integer-language reading.** `Q_n(m) = Σ_{j=1}^{ν_n(m)}
(-1)^{j-1} N_j(m) / j`, where `N_j(m) = #{ordered factorisations of
m into j multiples of n}` equals `τ_j(m / n^j)` when `n^j | m` and
`0` otherwise.

## Anchor

A4 in `test_anchors.py`: `q_general(n, h, k)` matches all 24,203 rows
of `payload_q_scan.csv` over `n ∈ {2, 3, 4, 5, 6, 10}`. A5: agreement
between `q_general` and `q_value_by_class` on coprime `(n, k)`.

## Implementation

`predict_q.q_value_by_class(shape, h, tau_sig)` computes the master
expansion in the `gcd(k, n) = 1` case (`t = 0`). `predict_q.q_general(
n, h, k)` handles arbitrary `k`, including `k` carrying extra powers
of `n`'s primes; it computes the effective height
`h_eff = h + min_i ⌊t_i / a_i⌋` and runs the sum to `j = h_eff`.
