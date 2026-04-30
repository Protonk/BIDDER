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

The conjectured limit `ψ/x → 1` is independent of `n` (a meta-fact
from the residue calculation; see "Why the candidate rate is +1"
below), despite `Q_n` being signed and `M_n` not having unique
factorisation.

## Why the candidate rate is `+1`

`ζ_{M_n}(s) = 1 + n^{-s} ζ(s)` has a simple pole at `s = 1` with
residue `1/n`. Its Laurent expansion gives

    log ζ_{M_n}(s) = -log(s - 1) - log n + O(s - 1),

so

    -ζ'_{M_n}(s) / ζ_{M_n}(s) = 1/(s - 1) + (log n - n - γ) + O(s - 1).

Coefficient of `1/(s - 1)` is `+1`, independent of `n`.

What this establishes: the *candidate* main term of any
asymptotic of the form `ψ_{M_n}(x) ~ rx` is `r = 1`. **It does not
establish that an asymptotic exists.** For positive Beurling
Chebyshev measures, residue plus boundary regularity gives the
asymptotic via Wiener–Ikehara — the proof routes through
non-negativity of the underlying measure. Here `Λ_{M_n}` is
signed, so the standard Tauberian closure does not apply
directly. What replaces it is part of O1 below.

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

E1. **Finite-range approach toward 1.** `ψ/x` is monotonically
    increasing (after small-x oscillations) for every `n` tested
    in `{2, 3, 5, 6, 10}`. No plateau apparent through
    `x = 5 × 10⁶`. The conjecture is that the limit is `1`;
    a finite-range monotonic approach is consistent with that but
    does not establish it.

E2. **Convergence rate is `n`-dependent.** At `x = 5 × 10⁶` the
    diagnostic `|ψ - x| · log x / x` takes the values

        n =  2:  0.010    n =  3:  0.063    n =  5:  0.368
        n =  6:  0.704    n = 10:  2.612

    For `n ∈ {2, 3, 5, 6}` the residual at this `x` is **below**
    `x / log x`; only `n = 10` exceeds it (by a factor of `~2.6`).
    The diagnostic is monotonically decreasing in `x` for every
    `n` tested. **The asymptotic limit is not determined by this
    data**: it could go to `0` (residual `o(x / log x)`), to a
    non-zero constant (`Θ(x / log x)`), or away from `0`. The
    classical zero-free-region PNT gives residual
    `O(x exp(-c √log x))` — faster than any inverse polylog;
    RH-conditional bounds give `O(x^{1/2} (log x)^2)`. Whether
    `M_n` reaches either regime is not established here.

E3. **Zeros of `ζ_{M_n}` found in the scanned window of the
    critical strip; none found on `Re s = 1`.** Search in
    `σ ∈ [0.4, 1.05], t ∈ [0.1, 50]` (30 × 200 grid plus
    refinement) finds zeros at `σ ≈ 0.42–0.60` for
    `n in {2, 3, 5, 6, 10}`. For `n = 6, 10` some zeros lie at
    `σ < 1/2`, so no Riemann-hypothesis analog holds *within
    this window*. **No claim is made about zeros at `t > 50`,
    about the rest of the critical strip, or about
    `Re s = 1` outside the scanned `t` range.**

E4. **The lowest discrete zero does not predict the residual.**
    For `n = 10`, the lowest found zero `ρ ≈ 0.437 + 28.4i`
    predicts `|x^ρ / ρ| ≈ 29` at `x = 5 × 10⁶`; empirical
    `|ψ - x| ≈ 8.5×10⁵`. Four orders of magnitude apart.
    Possible explanations include: (a) many higher-`t` zeros
    summing coherently; (b) the Perron-formula decomposition for
    non-UF `ζ_{M_n}` differing from the classical case; (c) a
    continuous boundary-distribution contribution we have not
    isolated; (d) a finite-range transient masking the eventual
    asymptotic; or (e) the missing signed Tauberian condition
    (O1) admitting a regime where no clean zero/residue
    decomposition applies. Discriminating among these requires
    denser zero data and longer ψ runs.

## What is open

O1. **A signed Tauberian theorem for `ψ_{M_n}`.** Standard
    Wiener–Ikehara/Debruyne closure of "residue ⇒ asymptotic"
    needs both:
    *(i) Analytic-side input.* `-ζ'_{M_n}(s)/ζ_{M_n}(s) - 1/(s - 1)`
    has local pseudofunction boundary behaviour on `Re s = 1`.
    Necessary for this is global absence of zeros and other bad
    boundary singularities of `ζ_{M_n}` on the entire line
    `Re s = 1`. The E3 finite-window scan is *weak evidence*
    consistent with this but does not establish it.
    *(ii) Arithmetic-side input.* `ψ_{M_n}` satisfies a one-sided
    Tauberian condition — slow decrease, bounded decrease, bounded
    variation in a transformed variable, or a replacement
    theorem. For positive Mangoldt this is automatic from
    `Λ ≥ 0`; for signed `Λ_{M_n}` it is not. The standard
    Beurling proofs of `ψ ~ ρx` route through positivity to
    bypass this; here we do not have that route.
    Without both, the residue calculation identifies a candidate
    main term but does not yield a proven asymptotic.

O2. **The exact rate of `ψ_{M_n}(x) - x`.** Empirically
    `n`-dependent and at finite `x` larger than `x / log x` (E2);
    asymptotic behaviour undetermined. A closed-form rate function
    `R_n(x)` consistent with the data is unknown.

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
   (say `x = 10⁸`). The conjecture predicts the values
   eventually approach `1`; **it does not predict monotonicity**.
   A finite plateau or reversal is consistent with the conjecture
   (the limit could still be `1`). Falsification requires
   stronger evidence: `lim sup ψ / x < 1`, or a stable approach
   to a value `c ≠ 1` over a much larger range with the
   diagnostic `(ψ/x - c)` going to zero.

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

The residue calculation **identifies the candidate main term**
(`+1`, independent of `n`); the asymptotic `ψ_{M_n}(x) ~ x`
itself remains a **conjecture**, supported empirically for
`n ∈ {2, 3, 5, 6, 10}` to `x = 5 × 10⁶`. Closure requires a
signed-Tauberian argument (O1) that we have not supplied. The
finite-`x` rate of convergence is `n`-dependent and unexplained.

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
