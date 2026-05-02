# EXP02 — δ continued fraction is generic

The continued-fraction expansion of `δ = C_Bundle − C_Surv` at the
Two Tongues panel parameters (`[2, 10], k = 400`) **looks like a
typical rational of its denominator size by every CF metric tested**.
This is a clean null: the construction's structure does not
propagate through the CF lens.

## Setup

`δ = p/q` with `p` a 12,873-digit integer and `q = 2^11,879 · 5^4,894`
(a 12,874-digit power-of-10 divisor — 4894 fives matching `C_Surv`'s
length, the rest twos). The Euclidean algorithm gives a finite CF
of length `N = 24,923`.

Reference baselines for a random rational `p/q`:
- Worst-case CF length (Fibonacci-tight): `log_φ(q) ≈ 61,594`.
- Average CF length: `(12 ln 2 / π²) · ln(q) ≈ 24,975` (Heilbronn 1969).
- Asymptotic partial-quotient distribution: Gauss–Kuzmin
  `P(a_i = k) = log₂((k+1)² / k(k+2))`.
- Asymptotic geometric mean: Khinchin's constant `K₀ ≈ 2.6854520`.

## The numbers

```
CF length:               24,923   (Heilbronn average:  ~24,975)
ratio N / log_φ(q):       0.405   (theoretical mean:    ~0.405)
final Khinchin K_N:       2.6948  (Khinchin constant:    2.6854)
deviation from K₀:       +0.0093

partial-quotient distribution (vs Gauss–Kuzmin):
   k    empirical    GK        deviation
   1     0.4115      0.4150    −0.0035
   2     0.1747      0.1699    +0.0048
   3     0.0933      0.0931    +0.0002
   4     0.0574      0.0589    −0.0015
   5     0.0401      0.0406    −0.0005
   6     0.0284      0.0297    −0.0013
   7     0.0230      0.0227    +0.0003
   8     0.0179      0.0179     0.0000
   9     0.0133      0.0145    −0.0012
  10     0.0136      0.0120    +0.0016
  ≥11    0.1267      0.1241    +0.0026
```

Maximum deviation across the visible spectrum: 0.005. With 24,923
samples, the expected sampling error at `p ≈ 0.4` is
`√(p(1−p)/n) ≈ 0.003`, so the deviations are within sampling noise
across all `k`.

## Reading

Three observables independently confirm "generic rational":

1. **CF length** lands within 0.2% of the Heilbronn average for a
   random rational of denominator `≈ 10^12,874`. The ratio
   `N / log_φ(q) ≈ 0.405` is the theoretical mean exactly.

2. **Partial-quotient distribution** matches Gauss–Kuzmin to within
   sampling noise at every `k ∈ [1, 10]` and in the tail `k ≥ 11`.
   `P(a_i = 1) = 0.4115` (predicted 0.4150). No anomalous spike or
   suppression at any partial-quotient value.

3. **Khinchin geometric mean** converges to `K_N = 2.6948`, within
   `+0.0093` of Khinchin's constant. This is consistent with the
   variance for `n = 24,923`.

The largest partial quotients (96,733 at position 4,989; 31,802 at
6,870; etc.) are big-but-not-extraordinary for a random rational of
this size. Their positions do not correlate with structurally-
meaningful indices: bundle digit count (12,874), survivor digit
count (4,894), atom count (3,600), survivor count (1,338).

The convergent denominators `q_k` grow nearly linearly in `log_10`
across the CF, slope set by the running Khinchin geometric mean —
also as predicted for a typical rational.

## What this combines with EXP01

EXP01 found the apparent digit-frequency bias of full δ to be largely
inherited from bundle's tail; the substantive overlap region was
mostly a subtraction-with-borrows signature, with the underlying
content roughly uniform on digits 1-8.

EXP02 adds: the CF view independently confirms that δ has no detectable
structure beyond "rational of size ~10^12,874." Two orthogonal lenses
(decimal-position frequency, rational-approximation hierarchy) both
return null content above the L1-tracking layer.

The combined reading: **the bundle/survivor relation, on this single
panel, is captured by the L1-tracking observable**. The "rich and
persistent" character that motivated `differences/` doesn't show in
either of the two natural perpendicular observables — at least at
this one panel.

## What it does *not* close

The result is for *one* panel (`[2, 10], k = 400`). It doesn't address:

- **Parameter sweep.** Does `δ` at other `(n_0, n_1, k)` parameters
  also look generic? If yes, the null is robust. If at some
  parameters δ's CF *deviates* (anomalous Khinchin mean,
  partial-quotient skew), those parameters are the address.

- **Length-matched δ.** Truncating `C_Bundle` to `C_Surv`'s length
  removes the tail-leak completely. δ over equal-length reals might
  carry more localised structure than the full δ does.

- **Cross-base.** δ in base 10 might be generic; δ read in base 7
  might not be. The construction is base-10-specific; cross-base
  CF analysis is a separate axis.

- **Comparison to random control.** A random rational with the same
  denominator structure (`p' uniform in [0, q)`, `q = 2^11,879 ·
  5^4,894`) is the natural null. EXP02 hasn't directly measured the
  control; the CF metrics agree with theoretical predictions for
  random rationals, but a Monte Carlo control would tighten the
  comparison.

## Files

- `exp02_delta_cf.py` — script.
- `exp02_delta_cf.png` — four-panel figure: distribution, convergent
  denominators, running Khinchin mean, top largest partial quotients.
