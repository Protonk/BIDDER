# (α′) Pre-Write — Doubling Heuristic and Empirical c_1(n) Fit

Per the cross-thread agent's recommendation: pre-commit to the form
`ρ_K(n) = α_n + c_1(n)/log K + …` before doing the inclusion-exclusion
calculation. This document is the pre-write.

## What K=10⁸ established

`h2_ratio_n1e8.py` confirmed:

- All six panel values fell within ±0.001 of the geometric-extrapolation
  predictions. **Drift is slowing as expected.**
- The `(α_n + α_n²)/2` midpoint match at K=10⁷ for n=2 and n=3 is a
  *coincidence on the way up* — at K=10⁸ both ratios drifted *past*
  the midpoint by ~0.003. So the midpoint is NOT the asymptote (the
  cross-thread agent's "numerology" critique stands).
- Drift slowdown ratios (drift K7→8 / drift K6→7): 0.76, 0.78, 0.61,
  0.86, 1.05, 1.09 for n = 2, 3, 5, 7, 11, 13. Slowing for n ≤ 7;
  approximately stable for n = 11, 13. The convergence rate may
  itself depend on n.

The remaining gap to α_n at K=10⁸ is large (0.04 to 0.12 across the
panel), and at current drift rates would take ~16-44 more decades of
K to close. So we're genuinely pre-asymptotic.

The framing `ρ_K(n) = α_n + c_1(n)/log K + …` with α_n the asymptote is
**consistent with the data direction** but unsubstantiated rigorously
without analytic derivation.

## Empirical c_1(n) values

Defining `c_1(n) := (ρ_K(n) − α_n) · log K`, the K=10⁸ values:

| n | ρ_K(10⁸) | α_n | (ρ−α_n) | log K | empirical c_1(n) |
|---|---|---|---|---|---|
| 2 | 0.3777 | 0.5000 | −0.1223 | 18.42 | **−2.25** |
| 3 | 0.5578 | 0.6667 | −0.1089 | 18.42 | **−2.01** |
| 5 | 0.7181 | 0.8000 | −0.0819 | 18.42 | **−1.51** |
| 7 | 0.7922 | 0.8571 | −0.0650 | 18.42 | **−1.20** |
| 11 | 0.8625 | 0.9091 | −0.0466 | 18.42 | **−0.86** |
| 13 | 0.8820 | 0.9231 | −0.0411 | 18.42 | **−0.76** |

For c_1(n) to be a stable leading-order coefficient, it should be
approximately constant in K for fixed n. Cross-checking with K=10⁷:

| n | c_1 @ K=10⁷ | c_1 @ K=10⁸ | ratio |
|---|---|---|---|
| 2 | −2.02 | −2.25 | 1.11 |
| 3 | −1.83 | −2.01 | 1.10 |
| 5 | −1.37 | −1.51 | 1.10 |
| 7 | −1.10 | −1.20 | 1.09 |
| 11 | −0.79 | −0.86 | 1.09 |
| 13 | −0.70 | −0.76 | 1.09 |

The "c_1" estimates are growing in magnitude by ~10% per decade. So
the simple `α_n + c_1/log K` form is **not** the exact leading-order
expansion. Either:

- (i) The expansion has higher-order corrections of order `1/(log K)`
  ratio that aren't yet sub-dominant.
- (ii) The leading correction is `(log log K)/(log K)` instead of
  `1/log K`.
- (iii) The leading correction has form `α_n − ρ_K(n) ∝ (log K)^{−γ}`
  for some `0 < γ < 1`.

To distinguish, fit (`α_n − ρ_K`) vs `log K` on a log-log plot:

| n | log(α_n − ρ_K @ K=10⁴) | @ 10⁵ | @ 10⁶ | @ 10⁷ | @ 10⁸ |
|---|---|---|---|---|---|
| 2 | log(0.142) = −1.95 | log(0.135) = −2.00 | log(0.129) = −2.05 | log(0.125) = −2.08 | log(0.122) = −2.10 |

log K = 9.21, 11.51, 13.82, 16.12, 18.42.

Slope log(α_n − ρ_K)/log(log K)? Hmm let me try log K instead:

For n=2: slope of log(α_n − ρ_K) vs log K:
- (−2.10 − (−1.95))/(18.42 − 9.21) = −0.15/9.21 = −0.0163.

So `α_n − ρ_K ∝ K^{−0.016}` for n=2 at our range. Very small power — not really a power law in K, more like a slowly-shrinking constant.

A `1/log K` form predicts slope on log-log of (log α_n − ρ_K) vs log K
should be -log(log K) corrections... too noisy at our K range to pin
the exact shape.

## The doubling heuristic — refined

For prime n, write k = n^a · m with `gcd(m, n) = 1`, a ≥ 0. Cases:

- **a = 0**: k coprime to n. Counts in M_n(K).
- **a = 1**: k = n·m, m ≤ K/n. Dominant contribution to multiples of n.
- **a ≥ 2**: k = n²·m', m' ≤ K/n². Sub-leading for large n.

For a = 1, divisors of k = n·m (with gcd(n,m)=1) are
`{d : d | m} ∪ {n·d : d | m}`.

For Ford-image-at-K (k has divisor in [k/√K, √K] = [n·m/√K, √K]):

- **Type-A (small divisor of m)**: d | m, d ∈ [n·m/√K, √K].
  Equivalent: m has divisor d such that m/d ≤ √K/n AND d ≤ √K.
- **Type-B (n·d divisor with d | m)**: n·d ∈ [n·m/√K, √K], i.e.,
  d ∈ [m/√K, √K/n].

For m ≤ K/n²: Type-A range and Type-B range OVERLAP (combined =
[m/√K, √K]). For K/n² < m ≤ K/n: ranges are DISJOINT, combined =
[m/√K, √K/n] ∪ [n·m/√K, √K].

So for `m ≤ K/n²`: condition is "m has any divisor in [m/√K, √K]" —
which is m's Ford-image at scale K (NOT K/n²). For most m ≤ K/n² ≤
√K · √K/n² ~ K^{1−2/log n}... actually let me just think about it:
m ≤ K/n² ≤ K. m's Ford-image at scale K is m has divisor in
[m/√K, √K]. For m ≤ K/n², we have m/√K ≤ √K/n². And √K/n² ≤ √K.
The range is [small, √K]. For m ≤ √K (always true for m ≤ K/n²
when n ≥ 2 and K small), most m have divisor 1 in the range.

Hmm wait, divisor 1 is in [m/√K, √K] iff m/√K ≤ 1 iff m ≤ √K. So for
m ≤ √K, divisor 1 always works. For √K < m ≤ K/n², need a larger
divisor.

For m ≤ √K: roughly all m are in image. Count ≈ √K.

For √K < m ≤ K/n²: roughly Ford-image-at-K count restricted to this
range. ~ M_Ford(K) · (K/n² − √K)/K ≈ M_Ford(K)/n².

So the m ≤ K/n² regime contributes ≈ √K + M_Ford(K)/n² to the
multiples-of-n count.

For K/n² < m ≤ K/n: union of Type-A and Type-B ranges. Each range
shrinks as m grows. Estimating this count needs more work.

Empirically at K=10⁸ for n=2: |{multiples of 2 in Ford image}| =
M_Ford(K) − M_n(K) = 22504348 − 8500546 = 14003802.

M_Ford(K)/n² = 22504348/4 = 5626087. √K = 10000. Sum = 5636087.

The empirical 14003802 is **2.5×** the leading-order prediction
M_Ford(K)/n² + √K. So the m ∈ (K/n², K/n] regime contributes the
remaining ~8.4M (60% of the total). My earlier hypothesis that this
regime contributes nontrivially is confirmed.

So the doubling heuristic from the agent's note ("≈ M_Ford(K/n²)")
undercounts by a factor of ~2.5x for n=2. The correction comes from
the m > K/n² regime.

## A second heuristic — splitting by a in k = n^a · m

P(k coprime to n | k ∈ Ford image) measures distinct k that are
coprime to n.

Alternative model: rather than splitting by Type-A/Type-B factorization
structure, split by:
- P(k ≡ 0 mod n | k ∈ Ford image, k ≡ 0 mod n^j for some specific j)

The empirical bias for n=2 at K=10⁸: P(k even | Ford-image) = 0.622.
If this approached 1/n = 0.5 (independence), we'd be at α_n
asymptote. Empirically still way above.

For 2-adic decomposition: P(k = 2^a · k', k' odd | Ford-image) ≈ ?.

If P(k even | Ford-image) > 1/n, the "excess" comes from over-
representation of multiples of n among integers with many divisors.

Quantitatively: integers with v_2 = 1 contribute (1/2)(1) + (1/2)(d_2)
to typical d(k), where d_2 is the divisor function on the 2-adic part.
The over-representation factor is approximately the ratio of average
d on multiples-of-n vs non-multiples. For n=2, average d(2k)/d(k) ≈
ln(log K) / log(log K) - some specific factor.

This is sketchy. The proper calculation needs Ford's machinery (his
§6 multiplicative-weight extension, per the cross-thread agent).

## Predicted form for ρ_K(n) — best current guess

Based on the empirical fit and the heuristic:

    ρ_K(n) = α_n + c_1(n)/log K + c_2(n)·(log log K)/(log K)² + …

with leading c_1(n) approximately:

    c_1(n) ≈ −α_n · F(n) · log K_*

for some K-dependent F(n). Empirical fit suggests c_1(n) ≈ −α_n/(2n) ·
log K_* with K_* close to current K, but the K-dependence is non-trivial.

A "pure leading-order" without K-dependence would have c_1 stable in K.
Empirically c_1 grows ~10% per decade of K, suggesting either
sub-leading corrections or different functional form.

## Why the analytic derivation is harder than the agent's heuristic suggested

The cross-thread agent's heuristic relied on |multiples-of-n in Ford
image| ≈ M_Ford(K/n²). Empirically this captures only ~40% of the
correct count for n=2. The remainder (60%) comes from `m ∈ (K/n², K/n]`
regime where Type-A and Type-B divisor ranges fragment.

Estimating this fragmented regime requires Ford-style anatomy estimates
on truncated balanced ranges — which is a Tenenbaum/Koukoulopoulos
calculation.

Specifically: count of m ∈ (Y, Y'] with divisor in [a₁, b₁] ∪ [a₂, b₂]
(disjoint), as a fraction of m ∈ (Y, Y']. Each of [a_i, b_i] gives a
Ford-style count; the union via inclusion-exclusion.

Effort estimate: this is 1-2 days of careful Ford anatomy work. The
literature (Ford 2008 §6, Koukoulopoulos 2010 §4-5) provides the tools
but the calculation is bespoke.

## Where this leaves us

Three statements stand:

1. **Empirically: ρ_K(n) → α_n is the most likely asymptote**, with
   slow `1/log K`-style convergence and non-trivial sub-leading
   corrections.

2. **The leading correction c_1(n) has the qualitative shape
   c_1(n) ∝ −α_n/n · log K_*** at current K, but the K-dependence
   suggests we're not at the leading-order regime yet.

3. **Rigorous derivation** of c_1(n) requires Ford-style anatomy on
   truncated balanced divisor ranges. Available in Ford 2008 §6 and
   Koukoulopoulos 2010 §4-5 (downloaded). Effort: 1-2 days of careful
   analytic work.

## What survives for `core/FINITE-RANK-EXPANSION.md`

The cell-resolved + ratio test investigations have established:

- **At fixed K, ⟨d(k)⟩ on the Ford image is monotone in n.** (Real,
  controlled, reflects residue restriction shifting d-distribution.)
- **M_n(K)/M_Ford(K) → α_n likely**, with finite-K bias from
  multiples-of-n over-representation in Ford image.
- **The c-shift in M_n · Φ(N)/N is a finite-K transient.** Asymptotically
  the deficit exponent is Ford's c, and the ratio prefactor is α_n
  (or at least very close to α_n). The "c(n) > c" reading was
  finite-K bias, not real asymptotic c-shift.

This LAST is a substantive correction to `H2-RESULT-N1E8.md`'s
"c-shift confirmed." The cross-thread agent's framing was right: drift
slowing, asymptote α_n.

## What I'd do next

Given budget, **defer the rigorous Ford-anatomy calculation** and:

1. **Cross-check by extending K**: K=10⁹ is feasible via numpy bytearray
   (1GB memory, ~10 min compute). Confirms drift continues toward α_n.
2. **Compute c_1(n) at higher precision** by fitting `(α_n − ρ_K)` to
   `1/log K` and `(log log K)/(log K)²` simultaneously. Multi-K fit
   with 5+ data points.
3. **Pursue the analytic path only if (1) and (2) raise new questions**.

If the K=10⁹ data doesn't show convergence problem, the qualitative
picture (asymptote α_n, finite-K bias) is closed empirically. The
exact c_1(n) form is a number-theory exercise that doesn't change the
Phase 4 framing.

For `FINITE-RANK-EXPANSION.md`: the rank-2 multiplication-table
"shadow" turns out to be a **prefactor effect** (asymptote α_n²-coefficient
or α_n² in pair-count framing) with finite-K transient. The c-shift
isn't real. So the speculation that "rank-h Q_n cell structure causes
the deficit-exponent shift" is REFUTED at h=2 — there is no
deficit-exponent shift to cause. This is itself a substantive
correction.

## Files

- `h2_ratio_n1e8.py` — K=10⁸ ratio test.
- `h2_ratio_n1e8.csv` — per-(n) data at K=10⁸.
- `sources/koukoulopoulos_2010_kfold_mult_table.pdf` — downloaded
  literature (gitignored, in sources).
- This document — the pre-write.
