# Brief 4 / Phase 4 — h = 2 predictor

The first step in pushing `algebra/FINITE-RANK-EXPANSION.md` rank-by-rank
through the multiplication-table coupling. We derive the rank-2
contribution to `M_n(N)·Φ(N)/N` for prime `n` from Ford's anatomy +
coprime-to-n density, then state where (and where not) `Q_n`'s rank-2
formula enters.

## Setup

For prime `n` with `gcd(n, b) = 1`, the n-prime atoms are

    A_n = { n · c : gcd(c, n) = 1, c ≥ 1 }.

The (balanced) restricted multiplication-table count from
`EXPERIMENTAL.md` Brief 4:

    M_n(N) := |{ a · b : a, b ∈ A_n, a, b ≤ √N }|.

Each pair (a, b) with a = n·c_1, b = n·c_2, c_i coprime to n, c_i ≤ √N/n,
contributes a product

    a · b = n² · c_1 · c_2

with `gcd(c_1·c_2, n) = 1` (since each factor is coprime to n; product
is coprime to n). So **every product has rank exactly 2** for prime n
under binary multiplication. The count is

    M_n(N) = | { c_1 · c_2 : c_1, c_2 coprime to n, c_i ≤ √N/n } |
           = | { k coprime to n : k ≤ N/n², k = c_1·c_2 with c_i ≤ √N/n, c_i ⊥ n } |.

Setting `K = N/n²`, this is the **multiplication-table count on
coprime-to-n integers up to K, with both factors ≤ √K**.

## Ford's theorem applied to coprime-to-n integers

Ford (`Ann. of Math. 168 (2008)`) showed for ordinary integers:

    M(K) = | { k ≤ K : k = ab for some 1 ≤ a, b ≤ √K } |
         ~ K · κ_F · (log K)^{−c} · (log log K)^{−3/2}

with deficit exponent

    c = 1 − (1 + log log 2)/log 2 ≈ 0.0860713320…

and `κ_F` an absolute constant.

For coprime-to-n integers (a multiplicative subset of density
`α_n := (n−1)/n` in the integers), Ford's theorem extends. The deficit
exponent `c` is **invariant** under residue restriction (Ford's `c` is
a universal anatomy-of-integers constant tracking the typical number
of distinct prime factors near `√K`; restricting to a residue class
coprime to `n` doesn't change the local anatomy). The prefactor
acquires `α_n²` from the density of pairs in the multiplication table:

    M_n^{coprime}(K) ~ α_n² · K · κ_F · (log K)^{−c} · (log log K)^{−3/2}.

(Heuristic: number of pairs (c_1, c_2) coprime to n with c_1·c_2 ≤ K is
`α_n² · K · log K` by inclusion-exclusion + hyperbola; Ford's deficit
is the fraction with a balanced factorization; same fraction applies
to the coprime subset because anatomy is multiplicatively invariant.)

## h = 2 closed-form prediction

Combining the two pieces:

    M_n(N) ~ M_n^{coprime}(N/n²)
          ~ ((n−1)/n)² · (N/n²) · κ_F · (log(N/n²))^{−c} · (log log (N/n²))^{−3/2}.

For large N, `log(N/n²) ~ log N` and `log log(N/n²) ~ log log N`.
Defining `Φ(N) := (log N)^c · (log log N)^{3/2}`:

    M_n(N) · Φ(N) / N  ~  κ_F · (n−1)² / n⁴.

That's the **h = 2 prime-n predicted constant**:

    C(n)  :=  (n−1)² / n⁴       (up to Ford's universal constant κ_F).

Panel values:

| n | C(n) = (n−1)²/n⁴ | C(n)/C(2) |
|---|---|---|
| 2 |  1/16 = 0.0625 | 1.000 |
| 3 |  4/81 ≈ 0.0494 | 0.790 |
| 5 | 16/625 = 0.0256 | 0.410 |
| 7 | 36/2401 ≈ 0.0150 | 0.240 |

The **Ford-flat with prefactor `(n−1)²/n⁴`** outcome, in `EXPERIMENTAL.md`
Brief 4's parlance — the "probably nothing" outcome.

## Where Q_n enters (and where it doesn't)

This is the **honest reading**. Q_n at h = 2 is

    Q_n(n²k) = 1 − τ_2(k)/2 = 1 − d(k)/2,    gcd(k, n) = 1.

The h=2 prediction `(n−1)²/n⁴` derives from coprime density × Ford's
universal `κ_F`. It does **not** explicitly use the value of `Q_n`.
Q_n's role is implicit, via the multiplicative-anatomy that drives
Ford's deficit:

- `1 − d(k)/2` says the local Λ_n at rank 2 has sign determined by
  the divisor count of the cofactor product `k`. When `d(k) ≥ 3`,
  Q_n < 0 — exactly when `k` has multiple "balanced" factorizations.
- These same `k` are the ones that contribute to the multi-counting
  in Ford's pair-count → distinct-product reduction.
- So Q_n's negative sign locus is precisely the UF-defect region that
  *causes* the Ford deficit, but the COUNT statement aggregates this
  effect into a universal `κ_F` and doesn't expose Q_n directly.

The connection between Q_n and the count is **implicit through Ford's
universal constant**, not explicit in the prediction's leading term.

## When Q_n becomes explicit

A few candidate observables that *would* make Q_n's structure
explicit at rank 2:

1. **Λ_n-weighted multiplication-table sum:**
   ```
   S_n(N) := Σ_{m ∈ M_n^{(2)}, m ≤ N} Λ_n(m)
           = Σ Q_n(m) · log(m).
   ```
   For prime n at rank 2, this is `Σ_{k coprime n, k ≤ N/n²} (1 − d(k)/2) · log(n²k)`.
   The `1` term gives a `log` integral (PNT-like). The `−d(k)/2` term
   gives a Dirichlet-like sum. **Q_n's sign explicitly drives the
   asymptotic of S_n(N).**

2. **Q_n-cell-resolved distinct-product count:**
   bin distinct products by their payload divisor count `d(k)`.
   Predict each bin's count from Q_n at that bin × Ford anatomy.
   Test predicted vs measured per bin.

3. **Negative-Q_n-region density:**
   `M_n^{−}(N) := |{m ∈ M_n^{(2)}, m ≤ N : Q_n(m) < 0}|`. Predict from
   Q_n at h=2: condition is `d(k) ≥ 3`, equivalent to `k` not prime
   and not 1. Density of such k in coprime-to-n is computable.

These are richer than the bare M_n(N) prediction and would directly
exercise Q_n's local algebra.

## Composite n preview (deferred)

For composite n (n=4, 6, 10), products of atoms can have rank ≥ 3
when cofactors share primes with n:

- n=4: pair `(c_1, c_2)` with both `c_i ≡ 2 (mod 4)` gives
  `n² · c_1·c_2` with extra `2²` in the factorisation, lifting rank
  from 2 to 3. Rank-3 "extra" cell is a fraction of all pairs.
- n=6 = 2·3: pair with one `c_i` even and another `c_j` divisible by 3
  similarly lifts rank.
- n=10 = 2·5: similar.

The composite-n M_n(N) decomposes as

    M_n(N) = M_n^{(rank 2)}(N) + M_n^{(rank 3)}(N) + ...,

each term governed by the corresponding Q_n cell formula. Rank-2 for
composite n is restricted to "no extra height" cofactor pairs.
Walking up rank by rank for composite n is a natural next step *after*
prime n is settled.

## What the predictor returns

For prime n at h=2, the asymptotic prediction is

    M_n(N) · Φ(N) / N → κ_F · (n−1)²/n⁴

where `κ_F ≈ 0.4815…` is Ford's universal constant (numerical value
extractable from the literature; see Ford 2008 §1).

At finite N there are correction terms in `(log log N)^{-1}` etc.
The cleanest empirical test is to plot `M_n(N)·Φ(N)/N` vs N for
several N and observe convergence to the predicted constant per n.

The **ratio test** `M_n / M_2 → (n−1)²/n⁴ · 16` (= `16·(n−1)²/n⁴`) is
sharper because Ford's universal `κ_F` cancels — purely a
density-prediction on the coprime-to-n subsets.

## Empirical first-pass result

`h2_predictor.py` direct-enumerates `M_n(N)` for `n ∈ {2, 3, 5, 7}`
and `N ∈ {10^4, 10^5, 10^6, 10^7}` and tests the ratio prediction
`M_n / M_2 → 16(n−1)²/n⁴` (Ford-flat with residue prefactor):

| n | predicted | observed (N=10⁴) | (10⁵) | (10⁶) | (10⁷) | drift direction |
|---|---|---|---|---|---|---|
| 3 | 0.7901 | 0.6868 | 0.6785 | 0.6706 | 0.6695 | drifting **away** from prediction |
| 5 | 0.4096 | 0.3665 | 0.3412 | 0.3279 | 0.3191 | drifting away |
| 7 | 0.2399 | 0.2100 | 0.2007 | 0.1866 | 0.1831 | drifting away |

At every N the observed ratio is **lower** than the simple Ford-flat
prediction. The discrepancy at N = 10⁷:

- n = 3: −15.3 %
- n = 5: −22.1 %
- n = 7: −23.7 %

For n = 3 the drift has plateaued by N = 10⁶ (−15.1 → −15.3 %) —
suggesting either a constant prefactor different from `(n−1)²/n⁴`, or
a c-shift that's small. For n = 5, 7 the drift is still growing
(albeit slowly) at N = 10⁷.

**This is the "drifts logarithmically/polynomially in log N" outcome
from `EXPERIMENTAL.md` Brief 4** — the residue restriction is *not*
Ford-flat-invisible. Either (or both):

1. **Prefactor correction:** the asymptotic constant isn't
   `κ_F · (n−1)²/n⁴`. Restricting to coprime-to-n changes the
   anatomy in a way that needs more than the squared-density `α²`
   factor.
2. **Deficit exponent shift:** `c(n) > c` for n > 2. The exponent
   would shift the ratio by `(log N)^{−(c(n) − c)}`, which is
   small but non-zero and explains continued drift at N = 10⁷.

Distinguishing (1) from (2) requires N ≥ 10⁸ to see whether the
ratio plateaus or keeps decaying logarithmically. Direct enumeration
at N = 10⁸ is doable (~25M pairs); BPPW Monte Carlo gets to N = 10⁹
cheaply.

### Where this leaves Q_n

The rank-2 Q_n formula (`1 − d(k)/2`) does **not** enter the
prediction `(n−1)²/n⁴` directly — that prediction is purely
density × Ford. The empirical mismatch suggests Q_n *might* matter
in ways I didn't account for. Two specific possibilities:

- The "anatomy" of coprime-to-n integers depends on the local
  divisor count distribution. Ford's c is computed from `d(k)`
  asymptotics on ordinary integers; for coprime-to-n integers, the
  d-distribution is shifted (since `k` coprime to n has restricted
  prime support). Q_n at h=2 uses exactly `d(k)`; this is the same
  distribution that drives the deficit. **The c-shift, if real,
  may be derivable from Q_n's local structure.**
- A signed Q_n-weighted sum
  `Σ_{m ∈ M_n^{(2)}, m ≤ N} Q_n(m) · log(m)` is a different
  observable that *would* directly use Q_n's value. This is closer
  to the original Λ_n / Mangoldt sum and probably has a cleaner
  asymptotic.

So the simple "predict M_n(N)" path missed Q_n; the next-pass
predictors should incorporate Q_n's local d-distribution structure
explicitly.

## What's next

Three branches, in order of cost:

**(A) Push to larger N to distinguish prefactor-correction vs
c-shift.** Direct enumeration to N = 10⁸ is feasible (slow but
single-script). BPPW Monte Carlo to N = 10⁹ or 10¹⁰. The plateau-vs-
continued-drift question is the one to answer.

**(B) Cell-resolved h = 2 prediction.** Bin distinct products by
payload divisor count `d(k)` and predict each bin's count from Q_n
at that cell. Test predicted vs measured per bin. This DIRECTLY uses
Q_n's value at h=2.

**(C) Λ_n-weighted sum predictor.** Compute and predict
`Σ Q_n(m) log(m)` for rank-2 elements in M_n. This is a different
observable but closer to the original Mangoldt/Q machinery. Cleaner
asymptotic likely.

(A) confirms the qualitative finding. (B) tests Q_n's structure
explicitly. (C) gives a Q-flavored observable to compare. All three
are appropriate; my lean is (A) first to nail down the plateau
question, then (B) to bring Q_n into the prediction.

## Files

- This document: derivation + h=2 prediction + first empirical pass.
- `h2_predictor.py`: numerical predictor + direct-enumeration
  empirical test at N up to 10⁷.
- `h2_predictor.csv`: per-(n, N) table.
