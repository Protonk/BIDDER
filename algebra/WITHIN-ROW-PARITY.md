# Within-Row Parity Profile

First closed-form deliverable for `algebra/`. Translates the
substrate-side observation that the (n, k) Q-lattice has structured
autocorrelation along its k-axis into an exact decomposition that
rides on top of the master expansion (`Q-FORMULAS.md`) and the rank
lemma (`FINITE-RANK-EXPANSION.md`).

## Object

For prime `n` and fixed height `h`, the row of the Q-lattice is the
function

    k -> Q_n(n^h k),  k = 1, 2, ..., K.

Its lag-`L` autocorrelation is

    A(n, h, L; K) := (1 / (K - L))
                     sum_{k=1}^{K - L} Q_n(n^h k) * Q_n(n^h (k + L)).

This matches `q_lattice_4000_h{5,6,7,8}.npy` row-by-row at the cells
`lattice[n - 2, k - 1] = Q_n(n^h k)` (verified: see "Validation" below).

## Class signature

Every `k >= 1` factors uniquely (relative to a prime `n = p`) as

    k = p^t * k',     gcd(k', p) = 1.

Define `cls(k) := (t, tau_sig(k'))`, where `tau_sig(x)` is the
sorted-descending tuple of `x`'s prime exponents. The master expansion
implies

    Q_p(p^h k) = q_value_by_class((1,), h + t, tau_sig(k')).

So `Q_p(p^h k)` is determined by `cls(k)` together with `h` — nothing
about the specific primes of `k'` enters, only their exponent profile.

For non-prime `n`, the analog is `cls(k) = (overlap_tuple, tau_sig(k'))`
where `overlap_tuple` is aligned with `n`'s prime list.

## Decomposition

    A(n, h, L; K) = sum_{c1, c2} D(c1, c2; n, L, K) * V(c1; h) * V(c2; h)

with

    D(c1, c2) := #{k in [1, K - L] : cls(k) = c1, cls(k + L) = c2} / (K - L)
    V(c; h)   := q_value_by_class(shape(n), h + t, tau_sig)        [exact rational]

The sum has finitely many nonzero terms for any finite `K`. The
algebraic factor `V` is rigorous (`predict_q.q_value_by_class`
returns a `Fraction`); the combinatorial factor `D` is computed by
direct enumeration over `k = 1..K - L` (`predict_correlation.class_decomposition`).
Their product reconstructs `A(n, h, L; K)` exactly (verified to
machine precision in `predict_correlation._self_check`).

The decomposition does not give a closed form for `D` in itself —
that is the shifted-divisor-density problem of analytic number
theory and is not attempted here. What it gives is a clean
factorisation: every `Q`-related contribution is exact, and the
remaining ambiguity lives entirely in the class-pair density.

## Mechanism for the L-parity gap

For prime `n = p`, the residue class of `L` modulo `p` controls the
coupling between `cls(k)` and `cls(k + L)`:

- **`p | L`**: `(k mod p) = ((k + L) mod p)`. So `t > 0` iff both `k`
  and `k + L` are divisible by `p`. The pair stays on the `t`-diagonal:
  either both are coprime (`t1 = t2 = 0`) or both are in some higher
  `t`-stratum. Cross-stratum pairs (`t1 != t2`) have density 0.

- **`p` does not divide `L`**: at least one of `(k mod p, (k + L) mod p)`
  is nonzero, but the two are paired by `(k + L) - k = L mod p`,
  shifting the residue by a fixed amount. Pairs with `t1 = t2 = 0`
  have density `(p - 2)/p`. Pairs with `t1 = 0, t2 > 0` and
  `t1 > 0, t2 = 0` each have density `1/p`. Pairs with `t1 > 0, t2 > 0`
  have density 0 (modulo refinement at `t >= 2`).

Specialise to `n = 2`:

- **`L` even**: 50% of pairs have both `k, k + L` odd; 50% have both
  even. Cross-parity pairs have density 0.
- **`L` odd**: 0% of pairs have both odd or both even; 100% are
  cross-parity.

The Q-values on each kind of pair are:

- (odd, odd): `Q_2(2^h * k) * Q_2(2^h * (k + L))`, both at strip `h`.
- (even, even): both shifted to strip `h + t` (`t >= 1`); Q values
  taken at higher rows of the prime-row coefficient table.
- (odd, even): one at strip `h`, the other at strip `h + t`; the
  product mixes coefficients at two different heights.

At `h = 5` the prime row has the kernel-zero set
`tau_sig in {const, p, p^2, pq, p^3, pqr}` from the alternating-binomial
identity `sum_{j} (-1)^(j-1) C(4, j-1) j^d = 0` for `0 <= d <= 3`.
At higher `h = 6, 7, 8` the kernel set expands, but the
`(t, t)`-diagonal pairs still mix Q values of the same kernel structure,
while `(0, t)`-off-diagonal pairs mix Q values from different rows. The
row mismatch is the algebraic origin of the L-parity gap.

## Empirical readout

`test_within_row_lattice.py` enumerates `(h, n) in {5, 6, 7, 8} x {2, 3, 5, 7, 11, 13}`
at `K = 4000` and reports the lag-`L` autocorrelation profile for
`L = 1..20`. Aggregated parity statistics:

```
h = 5
    n   odd-L mean    even-L mean   gap          ratio (e/o)
    2   +3.12e-06     +1.76e-03     +1.75e-03    563
    3   +6.33e-04     +1.21e+00     +1.21e+00    1913
    5   +2.44e-01     +1.11e+01     +1.09e+01    46
    7   +4.95e-01     +2.18e+01     +2.13e+01    44
   11   +1.12e+00     +3.78e+01     +3.66e+01    34
   13   +1.46e+00     +4.11e+01     +3.96e+01    28

h = 6
    n   odd-L mean    even-L mean   gap          ratio
    2   +2.00e-06     +2.37e-06     +3.71e-07    1.19
    3   -7.26e-05     +2.06e-01     +2.06e-01    -2835
    5   +1.74e-02     +1.92e+00     +1.90e+00    110
    7   +2.80e-02     +3.54e+00     +3.51e+00    127
   11   +8.84e-02     +8.44e+00     +8.35e+00    96
   13   +1.15e-01     +9.09e+00     +8.98e+00    79

h = 7
    n   odd-L mean    even-L mean   gap          ratio
    2   +1.53e-06     +1.89e-06     +3.67e-07    1.24
    3   +1.46e-05     +1.10e-02     +1.10e-02    755
    5   +7.14e-05     +1.10e-01     +1.09e-01    1534
    7   +1.37e-03     +1.68e-01     +1.67e-01    123
   11   +1.21e-03     +9.33e-01     +9.32e-01    772
   13   +1.12e-03     +1.02e+00     +1.02e+00    914

h = 8
    n   odd-L mean    even-L mean   gap          ratio
    2   +1.21e-06     +1.55e-06     +3.44e-07    1.29
    3   -1.91e-06     +1.17e-06     +3.08e-06    -0.61
    5   -6.75e-06     +6.27e-07     +7.38e-06    -0.09
    7   -4.38e-05     +2.49e-03     +2.53e-03    -57
   11   -1.60e-05     +5.01e-02     +5.01e-02    -3137
   13    0.00e+00     +5.01e-02     +5.01e-02    inf
```

## Reading the table

1. **Gap exists at every `(h, n)` with `n >= 3`**. The even-L mean is
   either much larger in magnitude or of opposite sign from the odd-L
   mean. The L-parity gap is robust across heights.

2. **`n = 2` is special**. The gap at `n = 2` is much weaker —
   ratio 1.19 to 1.29 across `h = 6, 7, 8` — because the prime-row
   kernel zeros are densest at `n = 2`'s lattice row (its column
   index just runs over all positive integers without filtering),
   so most pair products are zero on both sides. The signal at
   `h = 5, n = 2` (ratio 563) comes from sparse high-Ω payload
   alignments at specific even lags (`L = 12, 18, 20` carry the
   bulk of the even-L mass at `h = 5, n = 2`).

3. **Sign flips at `h = 8`**. For `h = 8` the odd-L mean turns
   negative for `n = 3, 5, 7, 11`, and the even-L mean stays
   positive but small. The ratio sign flip indicates that the
   even-L diagonal Q-products and the odd-L cross-stratum
   Q-products carry opposite signs at this height. This is a
   quantitative parity-of-h × parity-of-L coupling — the substrate
   side observed parity-of-h (in 2D spatial correlation); the
   within-row analog is parity-of-h modulating the parity-of-L gap
   sign.

## Validation

`test_within_row_lattice.py` (`PASS`):

- 24 spot-checks confirm `q_general(n, h, k) == lattice[n - 2, k - 1]`
  (within float precision) for `(h, n) in {5,6,7,8} x {2,3,5,7,11,13}`
  at 11 sample `k` values per slice.
- 24 autocorrelation profiles computed independently from `predict_q`
  and from the lattice file agree to `< 1e-7` at every lag in
  `L = 1..20`.

`test_anchors.py` (`PASS`):

- `Q_p(p^h * 1) = 1/h` for `h = 1..12` (A1).
- The 8x6 (shape, tau-signature) matrix at `h = 5` matches at every
  cell, including all kernel zeros (A2).
- `Q_n(n^2 k) = 1 - d(k)/2` across 347 (n, k) pairs at `h = 2` (A3).
- `q_general` and `q_value_by_class` agree on 4120 coprime cases (A5).
- `predict_q.q_general` matches `payload_q_scan.csv` on all 24,203
  rows (A4) — every previous Phase-2.2 verification at zero
  Fraction-equality mismatches.

## What this predicts

- The lag-L autocorrelation profile of any prime row of the Q-lattice
  at any `h`, with the algebraic factor exact.
- The location of even-L vs odd-L bias: a residue-class shift in
  `L mod n`, with the diagonal-vs-off-diagonal Q-product asymmetry
  controlling the magnitude.
- The kernel-zero structure at `h = 5` extends through `h = 6, 7, 8`
  with progressively wider kernel sets, which the table reflects in
  decreasing odd-L magnitudes and the eventual sign flip at `h = 8`.

## What this does not predict

- The class-pair joint density `D(c1, c2; n, L, K)`. That is a
  shifted-divisor-density problem in the style of Tenenbaum III §4.
  The decomposition isolates this quantity but does not solve it.
- The 2D spatial autocorrelation observed in
  `arguments/ATTRACTOR-AND-MIRAGE.md` ("parity-of-h structure" at
  `h = 5, 6, 7, 8`). The within-row lag-L profile is a 1D slice; the
  full 2D structure requires both row-axis and column-axis joint
  classes, and is a separate decomposition.
- Any analytic asymptotic. The profile is computed at `K = 4000`;
  the K -> infinity limit (assuming it exists) requires Tauberian
  input.

## What's next

In rough order of cost:

1. **Refine the decomposition for `n = 2, h = 5`** by enumerating the
   high-Ω payload pairs that carry the even-L mass at `L = 12, 18, 20`.
   The conjecture is that the even-L tail at `n = 2, h = 5` comes
   from a finite list of resonant `(k, k + L)` pairs with both sides
   carrying high `tau_5` weight; predict_q gives the exact `Q` at
   each such pair, and we can isolate the resonances.

2. **Try the column-axis analog** (varying `n` at fixed `k`). The
   substrate-side observation in ATTRACTOR-AND-MIRAGE was 2D — both
   axes carry structure. The column-axis correlation has a different
   class structure (`n`'s shape varies, not just `k`'s `tau_sig`),
   so the decomposition reorganises.

3. **Fold the n=2 "h-strip mixing" into a cleaner formula** by
   summing the geometric series over `t >= 0` of `Q_2(2^{h+t} * k')`
   at fixed `k'`. The series telescopes (rank lemma kills high `t`),
   so the strip-mixed Q at any specific even `k = 2^t * k'` is
   computable from a finite sum of higher-row prime-Q values.
