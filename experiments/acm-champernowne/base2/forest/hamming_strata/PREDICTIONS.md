# Hamming Strata — Predictions

Section 7 of [MALLORN-SEED.md](../MALLORN-SEED.md). Slide a k-bit
window across the binary Champernowne stream, compute the Hamming
weight at each position, and plot the distribution. The naive
expectation is "approaches `Binomial(k, 0.5)` because positional
notation has a small persistent 1-bias of `1/(2d)` per d-bit integer
and that bias shrinks as d grows." This document predicts the
deviations from that naive picture before the experiment is run.

## The baseline

A d-bit positive integer has its MSB locked at 1 and `d−1` other bits
free. Expected 1-fraction is `(d+1)/(2d) = 1/2 + 1/(2d)`. So the
"universal" stream of all positive integers has a persistent 1-bias of
`1/(2d)` that shrinks as `d → ∞` but never vanishes.

This is the baseline. The Hamming Strata experiment asks what happens
when you replace "all positive integers" with "n-primes," which is a
sieve-restricted subset.

## Deriving the bias for n = 2^m

The repo's definition (`core/acm_core.py`) is that n-primes are
`n·k` where `n ∤ k`. For `n = 2^m`, that means `2^m · k` where the
bottom m bits of k are not all zero. In binary, `2^m · k` has m
forced trailing zeros and the bits of k stacked above them. There are
two regimes depending on whether the constraint actually excludes
anything.

### Regime A: small d (`d ≤ 2m`)

k is `(d−m)`-bit, so the largest k is `< 2^m` and `k mod 2^m = k > 0`
is automatic. Only the MSB of k is fixed; the other `d−m−1` bits are
free uniform. Then:

```
expected ones = 1 + (d − m − 1) / 2
fraction      = (d − m + 1) / (2d) = 1/2 + (1 − m) / (2d)
```

For m ≥ 2, this gives a strong negative bias near the lower edge of
the bit-length spectrum.

### Regime B: large d (`d > 2m`)

k is `(d−m)`-bit, the MSB is fixed at 1, the bottom m bits cannot all
be zero, and the middle `d−2m−1` bits are free. The bottom m bits
are uniform over the `2^m − 1` valid patterns; by symmetry each has
`E[bit] = 2^(m−1)/(2^m − 1)`. Working through:

```
fraction = 1/2 + (1/(2d)) · [1 − 2m + m · 2^m / (2^m − 1)]
```

Computing the bracket for m = 1..5:

| m | n  | bracket   | asymptotic bias  |
|---|----|-----------|------------------|
| 1 | 2  | 1         | +1/(2d)          |
| 2 | 4  | −1/3      | −1/(6d)          |
| 3 | 8  | −11/7     | −11/(14d)        |
| 4 | 16 | −41/15    | −41/(30d)        |
| 5 | 32 | −119/31   | −119/(62d)       |

For large m the bracket approaches `1 − m`, so the bias is roughly
`−m/(2d)`. The ladder is monotonic in m, but not linear in m for
small m.

## Three claims

### Claim 1 — n=2 matches the universal baseline exactly

For n=2, the constraint `k odd` is the only non-trivial constraint
and it's identical to "(d−1)-bit positive integer's LSB is fixed at
1." The forced bits balance out and the fraction is exactly
`1/2 + 1/(2d)`, identical to the universal baseline over all d-bit
positive integers. n=2 should be indistinguishable from "no sieve."

### Claim 2 — n=4 has a small but real *negative* bias

`fraction(n=4, d) = 1/2 − 1/(6d)` for `d > 4`, and `1/2 − 1/(2d)` at
`d = 4`. So the running mean for the n=4 stream approaches 0.5 *from
below*, slowly. This contradicts the naive "approaches from above"
intuition.

Spot check at d=6: 4-primes are 36, 40, 44, 52, 56, 60 with Hamming
weights 2, 2, 3, 3, 3, 4. Mean = 17/6 ones in 6 bits → fraction
17/36 ≈ 0.4722. Predicted `1/2 − 1/36 = 17/36`. ✓

### Claim 3 — n=8 has much bigger negative bias than n=2 has positive

Asymptotic biases: n=2 is `+1/(2d)`, n=8 is `−11/(14d)`. The ratio
of magnitudes is `11/7 ≈ 1.57`. So n=8 sits roughly 1.57× further
below 0.5 than n=2 sits above. They are *not* mirror images of each
other, even though the directions are opposite.

For higher powers of 2, the magnitude grows: n=16 is roughly 2.73×
the n=2 magnitude in the opposite direction; n=32 is roughly 3.84×.

The ladder of biases for n = 2, 4, 8, 16, 32 should appear on the
heatmap as a sequence of horizontal stripes that:

- alternate sign at exactly one place: between n=2 (positive) and
  n=4 (negative)
- grow monotonically in magnitude on the negative side as m
  increases
- have characteristic shape `(constant) / d`, so they fade toward
  zero as d grows

## Predictions for odd n

For odd n, no trailing zeros are forced and there is no cancellation
mechanism like in the `2^m` family. Naively the bias should remain
near the baseline `+1/(2d)`. Sieve effects exist (small d=6 spot
check for n=3 shows roughly −0.03 deviation from baseline) and may
or may not be predictable from a simple formula.

Two sub-predictions:

- **Odd n look like n=1 (the universal baseline) plus small noise.**
  The 2-adic structure is the only structure that bit balance can
  see; the rest of n's factorization is essentially invisible to
  Hamming weight.
- **n=6 (= 2·3) looks more like n=2 than like n=4.** v_2(6) = 1, so
  the trailing-zero structure is the same as n=2, just sieve-shifted
  by the factor of 3. The bit balance should be close to n=2's
  baseline, with small odd-sieve corrections.

## Heatmap appearance

Rows = n (1..N_MAX), columns = bit-length class d (4..20), color =
`(empirical_mean_fraction − 0.5)` with a diverging colormap centered
at 0.

Predicted appearance:

- **Row n=2**: red (above 0.5) gradient fading toward white as d
  grows.
- **Row n=4**: blue (below 0.5) gradient, weak — `−1/(6d)` is small.
- **Row n=8**: blue gradient, much stronger than n=4 — `−11/(14d)`.
- **Rows n=16, 32**: progressively stronger blue gradients early,
  fading to white as d grows.
- **Odd n (3, 5, 7, 9, ...)**: mostly red, similar to n=2.
- **n=6, 10, 14, ... (v_2 = 1)**: red, similar to n=2.
- **n=12, 20, 24, ... (v_2 = 2)**: faint blue, similar to n=4.
- **Most n**: tracks v_2(n).

If n=2 has any visible bias different from `+1/(2d)`, the baseline
formula is wrong. If n=4 has *zero* bias (white the entire row), the
asymmetric-constraint analysis is wrong. If n=8 looks like a perfect
mirror of n=2, the analysis is wrong in a different way.

## Convergence plot appearance

A second view: pick a few representative monoids (e.g., `n ∈ {2, 3,
4, 5, 7, 8, 16, 32}`) and plot the running 1-fraction as a function
of how many bits have been consumed, on a log x-axis.

- **n=2, n=3, n=5, n=7** (and most odd n): curves descend toward 0.5
  *from above*.
- **n=4**: curve descends toward 0.5 *from below*, slowly.
- **n=8**: curve ascends toward 0.5 *from below*, faster than n=4.
- **n=16, n=32**: ascend toward 0.5 *from below*, even faster.

The convergence rate is logarithmic in the number of n-primes
consumed because the bias decays as `1/d` and `d ≈ log_2(N · n)`.

The crossover between "above" and "below" is the most striking
visual feature: most n-streams are slightly 1-heavy, but the
high-`v_2(n)` streams are 0-heavy.

## What would falsify each claim

1. **Claim 1 falsified** if n=2's empirical bias differs from
   `+1/(2d)` at any d ≥ 4 by more than statistical noise.
2. **Claim 2 falsified** if n=4 sits at or above 0.5 at any d ≥ 5.
3. **Claim 3 falsified** if n=8's magnitude is not roughly 1.57×
   that of n=2 at large d, or if it's positive at any d ≥ 7.

## A note on revision

An earlier draft of this document claimed n=4 was "exactly fair" and
that the powers of 2 formed a linear ladder mirrored about 0.5. Both
were wrong: that derivation incorrectly assumed n-primes for n=2^m
are `2^m·(odd k)` rather than the broader `2^m·k` with `2^m ∤ k`.
The corrected math above admits k values like k=2, 6, 10 for n=4,
which break the perfect cancellation that produced the "exactly
fair" claim.
