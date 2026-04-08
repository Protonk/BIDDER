# Hamming Bookkeeping

The bit-balance contribution of an n-prime in binary depends only on
`v_2` of that integer. This document derives the closed form for
`n = 2^m`, then describes the resolution at which `v_2` of the
*monoid* and `v_2` of an *entry* coincide and the resolution at
which they don't.

The closed form is verified by two experiments at different
resolutions: per-`(n, d)`-class in
[forest/hamming_strata/](forest/hamming_strata/) and per-entry in
[disparity/DETRENDED_RDS.md](disparity/DETRENDED_RDS.md). Both are
described in *Two experiments* below.

## Setup

For monoid `n`, n-primes are `n·k` where `n ∤ k`. When `n = 2^m`,
every n-prime has

- `m` trailing zeros (from multiplication by `2^m`)
- a constraint on the bottom `m` bits of `k`: not all zero

The leading bit is always 1 (it's the MSB of a positive integer).
Everything else is free.

We compare the expected fraction of 1-bits in a d-bit `2^m`-prime
to the universal baseline `(d+1)/(2d) = 1/2 + 1/(2d)`, which is the
expected 1-fraction over all positive d-bit integers.

## Two effects

Two structural changes distinguish a `2^m`-prime from a generic
positive d-bit integer.

**Effect A — trailing zero penalty.** Forcing `m` bits to 0 (instead
of leaving them free uniform) removes `m/2` expected 1-bits per
integer. This is *linear* in `m`.

**Effect B — bottom-bit constraint bonus.** The constraint
`k mod 2^m ≠ 0` excludes exactly one pattern (the all-zero pattern)
out of `2^m` possibilities for the bottom `m` bits of `k`. By
symmetry, each of those `m` bits then has

```
P(bit_i = 1 | bottom m bits not all zero) = 2^(m-1) / (2^m - 1)
```

instead of `1/2`. The bonus per constrained bit is the difference

```
bonus_per_bit = 2^(m-1)/(2^m - 1) - 1/2 = 1 / (2·(2^m - 1))
```

and the total bonus across all `m` constrained bits is

```
total_bonus = m / (2·(2^m - 1))
```

## The asymmetry

The penalty `m/2` is linear in `m`. The bonus `m/(2·(2^m − 1))`
decays exponentially. They cross at exactly `m = 1`.

| m | n  | penalty (m/2) | bonus       | net change in expected ones per integer |
|---|----|---------------|-------------|------------------------------------------|
| 1 | 2  | 1/2           | 1/2         | 0                                        |
| 2 | 4  | 1             | 1/3         | −2/3                                     |
| 3 | 8  | 3/2           | 3/14        | −9/7                                     |
| 4 | 16 | 2             | 4/30        | −28/15                                   |
| 5 | 32 | 5/2           | 5/62        | −75/31                                   |

The closed form is

```
deficit_per_integer  =  -m · (2^(m-1) - 1) / (2^m - 1)
```

which approaches `-m/2` as `m → ∞`. The same quantity, expressed as a
fraction of `d`, gives the bias from the asymptotic limit `1/2`:

```
bias(2^m, d)  =  1/2 + (1/(2d)) · [1 - 2m + m·2^m / (2^m - 1)]
```

valid in the regime `d > 2m`. (For `d ≤ 2m` the constraint
`k mod 2^m ≠ 0` is automatic and the formula simplifies to
`1/2 + (1−m)/(2d)`.)

## Why m = 1 is the balance point

At `m = 1`, the constraint `k mod 2 ≠ 0` reduces to "bit 0 of `k`
is 1" — a *tight* per-bit constraint that forces a specific bit to
be 1. This converts a free bit (E = 1/2) into a forced 1 (E = 1),
gaining exactly 1/2 of an expected one. That precisely cancels the
1/2 lost to the single forced trailing zero.

Read as bookkeeping:

```
n = 2  forces:  ... 1 0       one forced 1, one forced 0
universal:      ... 1 ?       one forced 1, one free ½
                ---------
                same expected count of ones, exactly
```

For `m ≥ 2`, the constraint loosens. Instead of forcing every bit
in the bottom group, it only excludes one joint pattern out of
`2^m`. The constraint applies to many bits but doesn't force any
single one of them. Per-bit, the bonus shrinks fast: `1/6` for
`m=2`, `1/14` for `m=3`, `1/30` for `m=4`. Meanwhile the trailing
zeros each cost a full `1/2`. The penalty wins decisively.

## The general intuition

A trailing zero is a *strong* per-bit constraint: it pins a specific
bit to a specific value. The "not all zero" constraint is a *weak*
joint constraint: it eliminates one combination out of many.
Strong per-bit constraints have linear weight; weak joint
constraints have exponentially diluting weight.

When the joint constraint applies to a single bit (`m = 1`), it
*becomes* a strong per-bit constraint, and the two effects balance
exactly. When it applies to many bits (`m ≥ 2`), it dilutes and can
no longer compensate.

## Per-entry, not per-monoid

The closed form `bias(2^m, d)` is a per-*integer* prediction. The
parameter `m` is the 2-adic valuation of the integer, not of the
monoid the integer belongs to. To predict any aggregate statistic
on a monoid's stream, the formula must be applied per-entry using
that entry's `v_2`, then summed.

The two coincide for exactly two families:

- `n = 1` (the ordinary primes): every entry is odd, every entry
  has `v_2(entry) = 0`.
- `n = 2`: every entry is `2 · k` with `k` odd, every entry has
  `v_2(entry) = 1` exactly.

For every other monoid in this repository the entries carry mixed
`v_2`. For pure `n = 2^m` with `m ≥ 2`, the n-primes are `2^m · k`
with `k mod 2^m ≠ 0`, so `k` ranges over `{1, 2, …}` minus the
multiples of `2^m`. Even values of `k` like `k = 2, 4, 6, …` are
allowed, and they give `v_2(entry) > m`. The conditional
distribution of `v_2(k)` on `k mod 2^m ≠ 0` is geometric (after
normalization), so

```
⟨v_2(entry) for n = 2^m⟩  =  m  +  Σ_{j=0}^{m−1}  j / (2^(j+1) · (1 − 1/2^m))
```

For `n = 2^1 = 2` the sum is empty and `⟨v_2(entry)⟩ = 1` exactly.
For `n = 2^2 = 4` it is `7/3 ≈ 2.33`. For `n = 2^8 = 256` it is
`≈ 8.97`. Even pure powers of two have entries whose `v_2` runs
over `{m, m+1, …, 2m − 1}` with a non-trivial mixture; only `n = 2`
is degenerate.

For composite `n = 2^a · q` with `q` odd, the same compounding
applies one level up. `v_2(entry) = a + v_2(k)` for the same
conditional `k`, and the empirical mean ranges from `1.80` for
`n = 6` through `2.82` for `n = 12` up to whatever the panel covers.

`v_2(n)` is therefore a useful coarse label for a monoid but it is
not the parameter that controls per-entry contribution. The
parameter is `v_2(entry)`.

## Two experiments

Two experiments in this repository measure the closed form, at
different resolutions.

### Experiment A — Hamming Strata, per-`(n, d)` class

[forest/hamming_strata/](forest/hamming_strata/) groups each
monoid's n-primes by bit-length class `d` and computes the
empirical mean 1-fraction within each `(n, d)` cell. The closed
form is evaluated at the same `(n = 2^m, d)` pairs and overlaid on
a bias-vs-`d` plot. The empirical and predicted curves for
`n = 2, 4, 8, 16, 32` overlap across the tested range
`d = 4..20`. A bias heatmap over `n = 2..32` shows the predicted
stratification by `v_2(n)`: rows with the same `v_2` lean the same
direction at the same depths, and the magnitudes track the
predicted ladder. A convergence plot of the running 1-fraction for
representative monoids shows `n = 2, 3, 5, 7` approaching `1/2`
from above and `n = 4, 8, 16, 32` approaching from below, with
rates set by `1/d`.

A confirms the closed form for the `n = 2^m` family at the
resolution of one cell per `(n, d)` pair, where each cell averages
over all valid `k` in its class. Within a cell, A is internally
consistent because the formula is itself an average over the same
set of valid `k`.

### Experiment B — Detrended RDS, per-entry

[disparity/DETRENDED_RDS.md](disparity/DETRENDED_RDS.md) computes
the running digital sum `RDS(t)` of each monoid's bit stream for a
panel spanning `v_2 = 0..8` and subtracts the closed-form expected
drift, parameterized in two ways: once using `v_2(n)` (the same
value for every entry of the monoid) and once using `v_2(entry)`
(different for each entry). The per-entry version matches `RDS` to
within a fair-walk envelope after detrending. The per-monoid
version does not.

For composite `n` the difference is large. The residual end of
`n = 12` against the per-monoid prediction is `−6264`; against the
per-entry prediction it is `+11`. For `n = 6` the same numbers are
`−7785` and `−934`. Even pure `n = 2^m` with `m ≥ 2` shows the
difference: `n = 4`'s residual end goes from `−2739` per-monoid to
`+158` per-entry. Only `n = 2` and the odd `n` give the same
residual under both parameterizations, because those are the
monoids where `v_2(entry)` is constant across entries.

B tests the closed form at per-entry resolution over the running
stream and surfaces the dependence on `v_2(entry)` directly.

### Where A and B agree

A and B agree on the closed form. Both use

```
bias(2^m, d)  =  1/2 + (1/(2d)) · [1 − 2m + m · 2^m / (2^m − 1)]
```

as the per-integer prediction. A applies it to the ensemble of
d-bit integers in each `(n = 2^m, d)` cell; B applies it to one
entry at a time. Where the two scales overlap — summed over a
complete `d`-class for `n = 2^m` — the per-entry sum equals the
per-class average times the cell count, and both equal the closed
form.

The empirical convergence directions in A are consistent with B:
integers with `v_2 ≤ 1` carry per-integer slope `≥ +1`, integers
with `v_2 ≥ 2` carry slope `< 0`. A sees this as the direction of
approach to `1/2` for representative monoids; B sees the same
thing as the sign of `slope_for_entry(v_2(entry), d)` summed over
each monoid's stream.

### Where A and B conflict

The conflict is at the level of the broader claim that monoids
sharing `v_2(n)` "track" each other — that `n = 6` behaves like
`n = 2`, `n = 12` behaves like `n = 4`, and so on. A's heatmap is
qualitatively consistent with this picture: rows visually
stratify by `v_2(n)`, with the same direction of bias at the same
depths. B contradicts the stronger reading at the level of running
statistics: composite `n` and pure `2^m` with `m ≥ 2` do not have
entry-level bit-balance summarized by `v_2(n)`, because the
distribution of `v_2(entry)` differs from monoid to monoid even
within a fixed `v_2(n)`.

We trust B on this point. B is at finer resolution and exhibits
the mechanism directly: switching the prediction from `v_2(n)` to
`v_2(entry)` collapses the composite-`n` residual end by a factor
of `~6×` for `n = 6` and over `~500×` for `n = 12`. A's heatmap
aggregates over many entries within each `(n, d)` cell and is
consistent with both readings — the right one (per-entry,
parameterized by `v_2(entry)`, with `v_2(monoid)` as an imprecise
coarse label) and the literal reading (per-monoid, parameterized by
`v_2(n)` exactly). B distinguishes the two and the per-entry
reading wins.

The right summary: bit-balance sees `v_2(entry)`. For `n = 1` and
`n = 2` every entry has the same `v_2`, and `v_2(monoid)` is a
fine label. For `n = 2^m` with `m ≥ 2` and for composite `n`,
`v_2(entry)` varies across entries, and the formula must be
applied per-entry.

## Where the convergence to 1/2 actually comes from

Both effects (penalty and bonus) scale with `m`, not with `d`. The
deficit `−m·(2^(m-1) − 1)/(2^m − 1)` is a *constant number of ones
per integer of `v_2 = m`* — independent of `d`. When you divide
that constant deficit across `d` bit positions, the per-bit bias
decays as `1/d`, which is why every stream of integers eventually
approaches `1/2`. The convergence is logarithmic in stream length
because `d ≈ log_2(N · n)`.

For integers with `v_2 ≤ 1`: the per-integer ones count matches or
exceeds the baseline. Streams of such integers approach `1/2` from
above.

For integers with `v_2 ≥ 2`: the per-integer ones count is short
of baseline by a `v_2`-dependent constant. Streams of such
integers approach `1/2` from below.

A monoid's stream is a mixture of integers with various `v_2`
values; the asymptotic direction of approach is set by the
*weighted* mean of these contributions. For `n = 1` (odd primes,
`v_2 = 0` always) and `n = 2` (`v_2 = 1` always) the mixture is
degenerate and the approach direction is unambiguous. For `n = 2^m`
with `m ≥ 2` and for composite `n`, the mixture contains a range
of `v_2` values; the dominant component is usually `v_2 = m` for
`n = 2^m` and `v_2 = a` for `n = 2^a · q`, but the next few
strata also contribute, and the running fraction is the running
weighted average across all of them.

## See also

- [forest/hamming_strata/](forest/hamming_strata/) — Experiment A.
  Per-`(n, d)`-class confirmation across `n = 2..32`.
- [forest/hamming_strata/PREDICTIONS.md](forest/hamming_strata/PREDICTIONS.md)
  — the closed-form predictions evaluated cell by cell.
- [disparity/DETRENDED_RDS.md](disparity/DETRENDED_RDS.md) —
  Experiment B. Per-entry test of the formula via running digital
  sum, with the `v_2(n)` vs `v_2(entry)` comparison.
- [BINARY.md](BINARY.md) §3 — the universal `+1/(2d)` baseline for
  arbitrary positive integer streams.
