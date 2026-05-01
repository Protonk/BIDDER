# Prime-row ordinary generating function

For prime `p` and `k' ≥ 1` coprime to `p`, the column
`h ↦ Q_p(p^h · k')` of the Q-lattice is a single polynomial or a
single transcendental function in one variable.

## Statement

Define

    F(x; p, k') := Σ_{h ≥ 1} Q_p(p^h · k') · x^h.

(i) **k' = 1.** `F(x; p, 1) = -log(1 - x)`. Coefficient extraction
gives `[x^h] F = 1/h`.

(ii) **k' ≥ 2 coprime to p.** `F(x; p, k')` is a polynomial in `x` of
degree exactly `Ω(k')`. Its leading coefficient is

    [x^{Ω(k')}] F = (-1)^{Ω(k') - 1} (Ω(k') - 1)! / ∏_i e_i!,

where `k' = ∏_i q_i^{e_i}`. For `h > Ω(k')`, `[x^h] F = 0`.

(iii) **Single-prime-power closed form.** For any prime `q ≠ p` and
`e ≥ 1`,

    F(x; p, q^e) = (1 - (1 - x)^e) / e,
    [x^h] F      = (-1)^{h - 1} C(e, h) / e   for  h = 1, …, e.

(iv) **Row sum.** For `k' ≥ 2` coprime to `p`,

    F(1; p, k') = 1/e   if k' = q^e   (single prime cofactor, ω = 1)
                = 0     if ω(k') ≥ 2.

For `k' = 1`, `F(1; p, 1)` is the harmonic series and diverges.

## Proof

Substitute the prime-`n` specialisation (`MASTER-EXPANSION.md` C3)
into the OGF and swap sums:

    F(x; p, k') = Σ_{j ≥ 1} (-1)^{j-1} τ_j(k')/j · Σ_{h ≥ j} C(h-1, j-1) x^h
                = Σ_{j ≥ 1} (-1)^{j-1} τ_j(k')/j · (x / (1 - x))^j.

Set `y = x / (1 - x)` so `1 + y = 1/(1 - x)`.

(i) `k' = 1`: `τ_j(1) = 1`, so `F = Σ_{j ≥ 1} (-1)^{j-1} y^j / j =
log(1 + y) = log(1/(1 - x)) = -log(1 - x)`.

(ii) `k' ≥ 2`: `τ_j(k') = ∏_i C(j + e_i - 1, e_i)` is a polynomial in
`j` of degree `Ω(k')` and vanishes at `j = 0` (each factor does, since
`C(e_i - 1, e_i) = 0` for `e_i ≥ 1`). So `R(j) := τ_j(k')/j` is a
polynomial in `j` of degree `Ω(k') - 1`. The alternating sum
`Σ_{j ≥ 1} (-1)^{j-1} R(j) y^j` is a rational function of `y` with
denominator dividing `(1 + y)^{Ω(k')}`; substituting `1 + y = 1/(1 -
x)` clears the denominator against `(1 - x)^{Ω(k')}`, leaving a
polynomial of degree `Ω(k')` in `x`. The leading coefficient is the
boundary value from `KERNEL-ZEROS.md` (ii).

(iii) For `k' = q^e`, `τ_j(q^e) = C(j + e - 1, e)` and
`τ_j(q^e)/j = C(j + e - 1, e)/j`. The derivative

    dF/dy = Σ_{j ≥ 1} (-1)^{j-1} τ_j(q^e) y^{j-1}
          = Σ_{i ≥ 0} (-1)^i C(e + i, e) y^i
          = (1 + y)^{-(e+1)}

integrates to `F(y) = (1 - (1 + y)^{-e}) / e`, equivalently
`F(x) = (1 - (1 - x)^e) / e`. Coefficient extraction gives
`[x^h] F = (-1)^{h-1} C(e, h) / e`.

(iv) Setting `x = 1`: by the hockey-stick identity
`Σ_{h=j}^{Ω} C(h-1, j-1) = C(Ω, j)`,

    F(1; p, k') = Σ_{j=1}^{Ω} (-1)^{j-1} C(Ω, j) τ_j(k')/j.

The standard finite-difference identity
`Σ_{j=0}^{Ω} (-1)^j C(Ω, j) p(j) = 0` for any polynomial `p` of
degree `≤ Ω - 1` reduces the right-hand side to `R(0) = lim_{j → 0}
τ_j(k') / j`. Factor `τ_j(k') = j^{ω(k')} · g(j)` with `g` a
polynomial:

- `ω(k') = 1`, `k' = q^e`: `τ_j(q^e)/j = (j+1)(j+2) ⋯ (j+e-1)/e!`,
  evaluating to `(e-1)!/e! = 1/e` at `j = 0`.
- `ω(k') ≥ 2`: `τ_j(k')/j = j^{ω - 1} · (...)`, which vanishes at
  `j = 0`. ∎

## Anchor

A10 in `test_anchors.py`: degree, leading coefficient, and row sum
checked simultaneously over six primes `p ∈ {2, 3, 5, 7, 11, 13}` and
all coprime `k' ≤ 200` with `Ω ≤ 5` (901 cases), with 180 independent
cross-checks against the single-prime-power closed form
`row_polynomial_qe_closed`.

## Implementation

- `predict_q.row_polynomial(p, k_prime)` returns the coefficient list
  `[c_1, …, c_{Ω}]`.
- `predict_q.row_polynomial_qe_closed(e)` returns the
  single-prime-power coefficients from the closed form (independent
  of the master expansion; cross-check).
- `predict_q.row_sum(p, k_prime)` returns `F(1; p, k')`.
