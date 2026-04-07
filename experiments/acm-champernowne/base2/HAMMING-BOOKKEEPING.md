# Hamming Bookkeeping

The bit-balance of binary n-prime streams depends only on `v_2(n)`,
the 2-adic valuation. This document explains why, in the simplest
form. The empirical confirmation lives in
[forest/hamming_strata/](forest/hamming_strata/).

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

## Why bit-balance only sees `v_2(n)`

The trailing-zero structure of a multiple of `n` in binary is
determined entirely by `v_2(n)`. The other prime factors of `n`
sieve the monoid `nZ+` in ways that don't constrain bit positions
in any specific way visible to a bit-balance statistic. So:

- `n = 2, 6, 10, 14, ...` (`v_2 = 1`) all behave like `n = 2`:
  matches the universal baseline.
- `n = 4, 12, 20, 28, ...` (`v_2 = 2`) all behave like `n = 4`:
  small negative bias `−1/(6d)`.
- `n = 8, 24, 40, 56, ...` (`v_2 = 3`) all behave like `n = 8`:
  larger negative bias `−11/(14d)`.

The 2-adic valuation is the *only* feature of `n` that the bit-
balance statistic can see. The empirical heatmap in
[forest/hamming_strata/](forest/hamming_strata/) shows this
stratification across all `n` from 2 to 32.

## Where the convergence to 1/2 actually comes from

Both effects (penalty and bonus) scale with `m`, not with `d`. The
deficit `−m·(2^(m-1) − 1)/(2^m − 1)` is a *constant number of ones
per integer* — independent of `d`. When you divide that constant
deficit across `d` bit positions, the per-bit bias decays as `1/d`,
which is why every monoid eventually approaches `1/2`. The
convergence is logarithmic in stream length because `d ≈ log_2(N·n)`.

For `v_2(n) ≤ 1`: the per-integer ones count matches or exceeds
the baseline, so the running fraction approaches `1/2` from above.

For `v_2(n) ≥ 2`: the per-integer ones count is short of baseline
by a `v_2(n)`-dependent constant, so the running fraction approaches
`1/2` from below.

The direction of approach is set by the bookkeeping above. The rate
of approach is set by `1/d`.

## See also

- [forest/hamming_strata/](forest/hamming_strata/) — the experiment
  that confirms this empirically across `n = 2..32`
- [forest/hamming_strata/PREDICTIONS.md](forest/hamming_strata/PREDICTIONS.md)
  — the per-monoid predictions derived from the same formula
- [BINARY.md](BINARY.md) §3 — the universal `+1/(2d)` baseline for
  arbitrary positive integer streams
