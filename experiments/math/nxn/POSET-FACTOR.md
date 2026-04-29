# POSET-FACTOR — Λ_n sign-table diagnostic

## ⚠️ STATUS UPDATE (Brief 4 has been re-executed)

This document was written as a **prerequisite gating diagnostic** for
Brief 4 (multiplication-table-on-M_n). That gating role is now
historical:

- **Brief 4 (h=2) has been executed empirically** in
  `experiments/acm-flow/mult-table/`. The "Λ_n stays nonneg ⇒ standard
  anatomy applies" / "Λ_n goes negative ⇒ structural direction" decision
  table below was written before the local algebra was understood. The
  finite-rank closed form `Q_n(m) = Σ_{j=1}^{ν_n(m)} (-1)^(j-1) τ_j(m/n^j)/j`
  (`core/Q-FORMULAS.md`) shows the sign locus is determined by ordered
  divisor counts on the payload `k = m/n^h`, not by anything
  flow-certified or UF-related at the level Brief 4's anatomy lives.
- **The h=2 empirical work** found `M_n(K) / M_Ford(K) → α_n = (n−1)/n`
  (asymptotic deficit exponent unchanged from Ford's `c`), with the
  finite-K convergence form unpinned. The "non-monotonicity ⇒ structural
  signal" reading in the coupling table below did not pan out as a
  diagnostic axis.
- **What's still useful here.** The M_n monoid setup (atoms, antichain
  framing, non-UF defect at `m=36`), the closed form for `Λ_{M_n}`
  derived via `Z_{M_n}(s) = 1 + n^{-s}ζ(s)` and Mercator, and the
  sanity check `Λ_{M_2}(36) = −log 6` are all still correct setup
  material for `Q_n`. Read this doc as a setup reference, not as a
  live gating decision for Brief 4.

For the current state of the local algebra see
`core/Q-FORMULAS.md` and `core/FINITE-RANK-EXPANSION.md`. For the h=2
multiplication-table empirics see `experiments/acm-flow/mult-table/`.

---

# POSET-FACTOR — Λ_n sign-table diagnostic

The Λ_n / antichain diagnostic. Prerequisite for Brief 4 of
`EXPERIMENTAL.md` (the multiplication-table-on-M_n question).
Decides whether the multiplication-table count on M_n factors
through a flow-certified poset, or whether residue restriction
introduces non-UF structure that standard anatomy machinery
doesn't see.


## The monoid M_n

    M_n  =  {1} ∪ nℤ⁺  =  {1, n, 2n, 3n, …}

closed under integer multiplication. Atoms (irreducibles) are

    A_n  =  P_n  =  { n·k  :  k ≥ 1, n ∤ k }

— the n-prime stream of `core/acm_core.py:88`.

**Antichain framing.** P_n is **primitive under M_n-divisibility**
even though not under ℤ-divisibility. In ℤ, `2 | 6`. In M_2,
`6 / 2 = 3 ∉ M_2`, so 6 is not divisible by 2 *as elements of M_2*
— the atoms of M_2 form a divisibility antichain. This is the
structural unlock: the right poset for analytic arguments on M_n
is M_n-divisibility, not ℤ-divisibility.

**Non-UF.** M_n is *not* a unique-factorisation monoid. The first
non-UF element of M_2 is `36 = 6·6 = 2·18` — two distinct length-2
atom factorisations. Higher-n analogues exist; their loci are part
of the diagnostic output.


## Λ_{M_n} — the monoid Mangoldt function

### Dirichlet-series definition

    Z_{M_n}(s)  =  Σ_{m ∈ M_n} m^{-s}  =  1 + n^{-s} ζ(s)

    -Z'_{M_n}(s) / Z_{M_n}(s)  =  Σ_{m ∈ M_n} Λ_{M_n}(m) · m^{-s}

For unique-factorisation monoids Λ_M ≥ 0 (it concentrates at atom
powers, value `log(atom)`). For non-UF monoids Λ_M can go negative;
the sign locus *is* the non-UF defect made quantitative.

### Closed form

Expanding `log Z_{M_n}(s) = Σ_{j ≥ 1} (-1)^(j-1)/j · (n^{-s}ζ(s))^j`
and differentiating gives, for `m ∈ M_n`,

    Λ_{M_n}(m)  =  log(m) · Σ_{j ≥ 1, n^j | m} (-1)^(j-1) · τ_j(m/n^j) / j

where `τ_j(k)` is the j-fold ordered divisor function (number of
ordered factorisations `k = k_1 · … · k_j` with each `k_i ≥ 1`).
`Λ_{M_n}(m) = 0` for `m ∉ M_n`.

**Sign of Λ_{M_n}(m)** is the sign of the rational
`Σ (-1)^(j-1) τ_j(m/n^j)/j` (since `log m > 0` for `m ≥ 2`). The
j=1 term is always `+1`; negativity arises when subsequent
alternating terms dominate.

### Sanity check at m = 36, n = 2

`n^j | 36` for `j = 1, 2`. So

    Λ_{M_2}(36) / log(36)  =  τ_1(18)/1  −  τ_2(9)/2
                            =  1  −  3/2
                            =  −1/2.

Hence `Λ_{M_2}(36) = −log(6) ≈ −1.79`.

This matches the direct convolution

    log(m) · 1[m ∈ M_n]  =  Σ_{d : d ∈ M_n, m/d ∈ M_n} Λ_{M_n}(d)

run on m=36 with M_2-divisors {1, 2, 6, 18, 36}, giving
`Λ(36) = log 36 − Λ(2) − Λ(6) − Λ(18) = log(6/(2·18)) = −log 6`.

The two formulations agree at the first non-UF element.


## The diagnostic

Implementation: `lambda_n.py` (this directory).

1. Pre-compute `τ_j(k)` for `k ≤ MMAX` and `j ≤ ⌈log₂ MMAX⌉` via
   `τ_{j+1} = τ_j ∗ 1` (Dirichlet convolution).
2. Sweep `n ∈ {2, 3, 4, 5, 6, 10}` and `m ∈ M_n ∩ [n, MMAX]`. For
   each, compute the rational
   `Q_n(m) = Σ (-1)^(j-1) τ_j(m/n^j) / j` exactly (Python
   `Fraction`), and `Λ_{M_n}(m) = log(m) · Q_n(m)`.
3. Record sign per (n, m). Identify first negative locus per n.

**MMAX = 10 000** — the previous-turn nudge. Bounded-integer
arithmetic; no precision tricks. Pure Python, single file. Runs in
seconds inside the Sage environment that the rest of the repo uses.


## Outputs (this directory)

| file | contents |
|---|---|
| `lambda_n.py` | implementation + sweep |
| `poset_factor.csv` | `(n, m, Λ_n rational, Λ_n value, sign)` |
| `lambda_n{n}.png` | per-n scatter of Λ_{M_n}(m) vs m, coloured by sign |
| `lambda_sign_strip.png` | combined negativity-locus strip across n |
| `sign_summary.txt` | per-n: total entries, count of negatives, first negative `m` |


## Coupling back to Brief 4

| Λ_n result | Brief-4 action |
|---|---|
| nonneg for all `(n, m)` tested | Run BPPW-MC unconditionally for all n. Expect Ford-shape with a residue prefactor — the "probably nothing" outcome from Brief 4. |
| Negative at `(n₀, m₀)` for some n₀ | Run BPPW-MC, **and watch for non-monotonicity** in `M_{n₀}(N)·Φ(N)/N` near the level corresponding to `m₀`. The non-monotonicity is the new signal. |
| Negative for all tested n at small m | Brief 4's "probably nothing" outcome is *out*; standard anatomy machinery doesn't apply; the structural / Lubell direction is the actual research move. |

A separate hypothesis worth recording: **the boundary between
n's where Λ_n stays nonnegative and n's where it goes negative**
(if such a boundary exists in the tested range) is itself a
structural fact about the monoids we have not seen written down.
The previous-turn pointer was that the asymmetry between `n`
prime, `n = p^k`, and `n` composite is exactly where this should
be visible.


## Status

- [x] Λ_n definition installed (monoid Mangoldt via −Z'/Z)
- [x] Sanity check Λ_{M_2}(36) = −log 6 verified two ways
- [ ] `lambda_n.py` implemented
- [ ] Sweep run for `n ∈ {2,3,4,5,6,10}`, `m ≤ 10⁴`
- [ ] Sign table rendered
- [ ] Sign summary written
- [ ] Result handed to Brief 4


## What this is not

- Not Brief 4 itself. Brief 4 is the BPPW Monte Carlo on `M_n(N)`.
- Not the CF spike work in `experiments/acm-flow/cf/`
  (that's Brief 2).
- Not the composite-lattice work in `experiments/acm/diagonal/`
  (that counts witness pairs per composite N — adjacent object,
  different question).
