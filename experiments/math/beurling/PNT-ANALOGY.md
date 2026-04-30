# A PNT analog for `M_n`

## Statement

For the non-UF arithmetic congruence monoid
`M_n = {1} ∪ nZ_{>0}`, define a signed Mangoldt-style weight
on positive integers:

    Λ_{M_n}(m) := Q_n(m) · log m,

where `Q_n(m) = [m^{-s}] log ζ_{M_n}(s)` is the master-expansion
coefficient of `log ζ_{M_n}` (`algebra/Q-FORMULAS.md`). `Q_n` is
zero outside `nZ_{>0}` and signed inside it.

The Chebyshev-style cumulant is

    ψ_{M_n}(x) := Σ_{m ∈ M_n, m ≤ x} Λ_{M_n}(m).

**Conjecture (BIDDER PNT analog).**

    ψ_{M_n}(x) ~ x       as x → ∞,    for every n ≥ 2.

The asymptotic rate is `+1` independent of `n`, despite `Q_n`
being signed and `M_n` not having unique factorisation.

## Why the leading rate is `+1`

`ζ_{M_n}(s) = 1 + n^{-s} ζ(s)` has a simple pole at `s = 1` with
residue `1/n`. Its Laurent expansion gives

    log ζ_{M_n}(s) = -log(s - 1) - log n + O(s - 1),

so

    -ζ'_{M_n}(s) / ζ_{M_n}(s) = 1/(s - 1) + (log n - n - γ) + O(s - 1).

Coefficient of `1/(s - 1)` is `+1`, independent of `n`. Under
Wiener–Ikehara-style hypotheses, the corresponding cumulant
inherits leading rate `+1`: `ψ_{M_n}(x) ~ x`.

The Wiener–Ikehara hypothesis itself is not established for
`M_n`. See "What is open" below.

## BQN annotation

Building on `Qn` from `algebra/FINITE-RANK-EXPANSION.md`. This is
exact-math annotation; the implementation lives in
`experiments/math/beurling/zeta_mn.py:psi_mn` (which uses
`predict_q.q_general` for `Q_n` and accumulates as floats).

```bqn
# Λ_{M_n}(m) = Q_n(m) · log m  (uses Qn from FINITE-RANK-EXPANSION.md)
LambdaMn ← {(𝕨 Qn 𝕩) × ⋆⁼ 𝕩}

# ψ_{M_n}(x) = Σ_{m in nZ_{>0}, m <= x} Λ_{M_n}(m)
PsiMn ← {+´ {𝕨 LambdaMn 𝕩}¨ 𝕨×1+↕⌊𝕩÷𝕨}
```

Reference values, against `psi_mn` in
`experiments/math/beurling/zeta_mn.py`:

- `2 PsiMn 8 ≈ 3.871`  (Σ over m ∈ {2, 4, 6, 8})
- `3 PsiMn 12 ≈ 6.474` (Σ over m ∈ {3, 6, 9, 12})

## What is proved

P1. **Residue.** `Res_{s=1}[-ζ'_{M_n}/ζ_{M_n}] = +1`.
    Direct from the Laurent expansion above. Independent of `n`.

P2. **No pole at `s = 0`.** `ζ_{M_n}(0) = 1 + ζ(0) = 1/2`.
    Regular, so the Olofsson `Re s = 0` rigidity template
    (BEURLING.md) gives no constraint on `M_n`.

P3. **Pole structure.** `ζ_{M_n}` has only one pole, at `s = 1`,
    simple, residue `1/n`. Inherited from `ζ`.

## What is empirical

Numerical evidence from `exp01_olofsson_transplant.py` and
`exp02_zeros_and_residual.py`. All values at `x = 5 × 10⁶` unless
noted:

| `n`  | `ψ_{M_n}(x) / x` | residual `ψ - x` |
|------|------------------|-------------------|
| 2    | 0.99934          | -3290             |
| 3    | 0.99592          | -20392            |
| 5    | 0.97616          | -119200           |
| 6    | 0.95433          | -228362           |
| 10   | 0.83063          | -846825           |

E1. **Convergence to 1.** `ψ/x` is monotonically increasing
    (after small-x oscillations) for every `n` tested in
    `{2, 3, 5, 6, 10}`. No plateau apparent through `x = 5 × 10⁶`.

E2. **Convergence rate is `n`-dependent and slower than
    classical PNT.** The classical residual is `O(x · exp(-c√log x))`,
    faster than any inverse polylog. The `M_n` residual is slower
    than `x / log x` for every `n` tested:
    `|ψ - x| · log x / x` is non-constant and far from zero at
    `x = 5 × 10⁶` for larger `n` (`n = 10`: 2.61).

E3. **Zeros of `ζ_{M_n}` in the critical strip, none on
    `Re s = 1`.** Search in `σ ∈ [0.4, 1.05], t ∈ [0.1, 50]`
    finds zeros at `σ ≈ 0.42–0.60` for `n in {2, 3, 5, 6, 10}`.
    For `n = 6, 10` some zeros lie at `σ < 1/2`, so no
    Riemann-hypothesis analog for `ζ_{M_n}` holds.

E4. **The lowest discrete zero does not predict the residual.**
    For `n = 10`, the lowest zero `ρ ≈ 0.437 + 28.4i` predicts
    `|x^ρ / ρ| ≈ 29` at `x = 5 × 10⁶`; empirical `|ψ - x| ≈ 8.5×10⁵`.
    Four orders of magnitude apart. Either many higher-`t` zeros
    sum coherently, or the Perron-formula decomposition for non-UF
    `ζ_{M_n}` differs from the classical case.

## What is open

O1. **Wiener–Ikehara hypothesis for `ζ_{M_n}`.** Need:
    `-ζ'_{M_n}(s)/ζ_{M_n}(s) - 1/(s - 1)` has local pseudofunction
    boundary behaviour on `Re s = 1`. No `Re s = 1` zeros (E3) is
    necessary; sufficient is not yet checked. Without this, the
    rate-`+1` is a residue calculation, not a proven asymptotic.

O2. **The exact rate of `ψ_{M_n}(x) - x`.** Empirically slower
    than `x / log x` and `n`-dependent (E2). A closed-form rate
    function `R_n(x)` consistent with the data is unknown.

O3. **The full zero distribution of `ζ_{M_n}`.** E3 found a
    handful of zeros in a finite scan window. The density
    `N_{M_n}(T) := #{ρ : 0 < γ < T}` as a function of `T` is not
    measured. For classical `ζ`, `N(T) ~ T log T / 2π`. For
    `ζ_{M_n}` it could differ.

O4. **σ < 1/2 zeros for composite `n`.** E3 finds zeros below
    the line `σ = 1/2` for `n = 6, 10`. Whether this is a finite
    list (and which `n` admit them) or extends to higher `t` is
    unmeasured.

## How to test

A reader who wants to falsify or sharpen the conjecture should:

1. Recompute `ψ_{M_n}(x) / x` at larger `x` for `n ∈ {6, 10}`
   (say `x = 10⁸`). The conjecture predicts continued
   monotonic approach to `1`. A plateau or reversal at any `n`
   falsifies it.

2. Verify the rate `+1` claim algebraically by an independent
   path: the residue argument is one line, but reproducing it
   from a different decomposition of `log ζ_{M_n}(s)` checks
   for arithmetic error.

3. Independently confirm the Λ definition by comparing
   `Σ Q_n(m) m^{-s}` evaluated as a finite Dirichlet series at
   small `s = σ + it` against a numerical evaluation of
   `log ζ_{M_n}(s)`. Disagreement would invalidate the
   construction.

4. Run a denser zero search (E3 was a 30 × 200 grid;
   `mpmath.findroot` from a 200 × 1000 grid in
   `σ ∈ [0, 1.1], t ∈ [0, 200]` is feasible).

## Status, in one line

The leading rate is established by residue calculation; the
asymptotic itself is empirical for `n ∈ {2, 3, 5, 6, 10}` to
`x = 5 × 10⁶`; the rate of convergence is unexplained.

## References

- `experiments/math/beurling/BEURLING.md` — the Beurling theory
  background and why `M_n` doesn't fit the standard framework.
- `experiments/math/beurling/EXP01-FINDINGS.md` — null Olofsson
  transplant; pivot to `ψ_{M_n}`; first convergence evidence.
- `experiments/math/beurling/EXP02-FINDINGS.md` — zero search,
  long ψ extension, residual rate analysis.
- `experiments/math/beurling/zeta_mn.py` — numerical library
  (`psi_mn`, `zeta_mn`, log-derivative).
- `algebra/Q-FORMULAS.md` and `algebra/FINITE-RANK-EXPANSION.md` —
  algebraic core for `Q_n`.
- `algebra/predict_q.py` — exact-rational `Q_n` implementation.
