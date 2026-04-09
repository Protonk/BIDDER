# Cheapest sieve per target

`cheapest_sieve.png` is a 3-panel figure showing, for each composite
`N` in the visible lattice (`k · n ≤ 100`, `k ≥ 2`), the witness pair
`(k, N/k)` that minimizes each of three cost functions on the
implied row map. `winners.npz` is the substrate, mapping each of 820
composites up to `k · n ≤ 1000` to its winner under each cost.

## The three costs

| name         | formula      | meaning                                  |
|--------------|--------------|------------------------------------------|
| `cost_k`     | `k`          | catch `N` at the earliest position       |
| `cost_diag`  | `n - k`      | most balanced factorization              |
| `cost_prime` | `|n - p_k|`  | closest to the prime row map `n = p_k`   |

`cost_diag` and `cost_prime` are both "balance-flavored" — they
prefer witnesses near the lower edge of the lattice — but
`cost_prime` is non-monotonic in `k` (because `p_k` is non-monotonic
in slope), so it can pick a *middle* witness when neither the
smallest nor the largest valid `k` lines up with the prime curve.

## The headline numbers

```
820 composites with witnesses (k * n ≤ 1000, k ≥ 2):
  all three agree:        35.98%   (295 / 820)
  cost_k    + cost_diag:  35.98%
  cost_k    + cost_prime: 35.98%
  cost_diag + cost_prime: 73.05%
```

These are not three independent agreement rates — they encode a
specific structural fact.

**`cost_k` has only one nontrivial agreement number, and it equals
the all-three rate.** Mechanically: `cost_k` agrees with `cost_diag`
exactly when the smallest-`k` witness is also the most-balanced
witness, which happens essentially only when there is one witness
to choose from. When there is one witness, all three costs trivially
agree. So 35.98% is "single-witness composites plus a small tail of
multi-witness coincidences," and it's the same number for any pair
involving `cost_k`.

**`cost_diag` and `cost_prime` agree on 73% of composites.** This
is the only genuinely informative agreement rate in the table. They
diverge on the remaining 27% — composites where the prime curve's
nonlinearity pushes the winner one or more columns away from the
most-balanced choice.

## What the eye is supposed to see

**Left panel (`cost_k`).** The winners form a vertical strip at
`k = 2`, with smaller strips at `k = 3, 5, 7`. This is essentially
"the smallest prime divisor of `N`" rendered geometrically. Even
composites have `k = 2` as their winner; odd composites with 3 as a
factor have `k = 3`; and so on up the prime ladder. The shape is
dictated by the prime factorization of each `N`, not by any
balance-flavored notion of cheap.

**Middle panel (`cost_diag`).** The winners cluster along a curved
frontier near the diagonal `n = k`. They are spread across all
visible columns and form a roughly hyperbolic pattern — for each
column `k`, the winners are the composites whose closest-to-`√N`
divisor lands at exactly that `k`.

**Right panel (`cost_prime`).** Looks similar to `cost_diag` at
first glance: the same general frontier, the same spread across
columns. The 27% disagreement with `cost_diag` is visible as
per-column shifts but does not dominate the overall shape.

## What this teaches

The cheapest-sieve costs do not converge to a single privileged
family of row maps. They split into at least two regimes:

- **`cost_k`-shaped**: the cheapest-by-`k` winner of `N` is the
  smallest prime factor of `N`. This is structural — no choice of
  cost based on "earliest catch" is going to wander far from the
  smallest-prime-factor map. The implied row map is degenerate
  (column 2 is overwhelming), and the winners do not lie on any
  smooth curve in the lattice.

- **Balance-shaped** (`cost_diag` and `cost_prime` together): the
  cheapest-by-balance winner of `N` is its largest divisor below
  `√N`, and the prime-curve correction shifts it occasionally. The
  winners form a curved frontier that traces the lower edge of the
  lattice, and they roughly follow the largest-small-divisor
  function `λ(N) = max{d : d | N, d ≤ √N}`.

There is no third regime here. The garden's "natural family"
framing — "are there a small number of canonical cheap sieves?" —
gets a partial yes: the balance-shaped family is one canonical
cheap sieve (with internal variation between `cost_diag` and
`cost_prime`). But `cost_k` is structurally separate, and any plot
8 partition that wants to use a single complementary pair will
have to choose between the two regimes rather than blending them.

## What it does not teach

It does not tell us *which* row map (which closed-form expression
for `n_k`) traces each winner family. The winner sets are clouds of
points, not curves; fitting a closed-form `n_k = f(k)` to those
clouds is the next step, and it's a separate question that plot 8
will have to address directly.

It also does not say anything about the abductive key's correctness
or the rank-1 substructure. This is a structural experiment on the
lattice, full stop.

## The interesting subset: 27% diag/prime disagreement

The 221 composites where `cost_diag` and `cost_prime` disagree are
the most informative subset in the substrate. The follow-up
analysis lives in `disagreements.py` and `disagreements.png`. The
findings are sharper than I expected before running it:

**The disagreements are essentially structural, not tie-breaking
artifacts.** 215 of 221 (97.3%) are *structural* — the prime winner
is the unique closest-to-prime witness. Only 6 are tie-affected,
where multiple witnesses tie at the same prime distance and the
order of evaluation picks one. The 27% headline rate is real, not
an artifact of how `min()` resolves ties.

**Every disagreement points the same direction in the lattice.**
All 215 structural disagreements have `diag_k > prime_k` (positive
k-gap, with the histogram peaking around `+6` to `+8`). Not one
single disagreement has `cost_prime` picking a *larger* `k`. This
is a strong directional fact: **`cost_prime` always shifts the
winner up-and-left**, toward smaller `k` and larger `n`.
Geometrically, the diag winner sits at `(k_max, √N)` which is below
the prime curve `p_{k_max} ≈ k_max · log k_max`, so to find a
witness closer to the prime curve you have to move to smaller `k`
where `N/k` has grown enough to meet `p_k`. The sweet spot is where
`k · p_k ≈ N` — composites with a divisor pair landing near the
prime row map.

**Disagreements concentrate on highly composite numbers, with a
sharper split than expected:**

```
                 mean witnesses    count(witnesses = 1)
Agreements:           1.96              295
Disagreements:        6.08                0
```

Zero disagreements have a single witness (tautological — you cannot
disagree with the only available option) but the *mean* gap is
3-fold: disagreements have on average 6 non-trivial witnesses,
agreements have 2. A composite with 6 witnesses has `d(N) ≈ 14`,
which is `N` like `72, 96, 120, 168, 192, 240, …` — the highly
composite numbers.

**The disagreement rate is not a constant. It grows with `N`:**

```
N in [   4,  100]:  15.7%
N in [ 101,  500]:  25.8%
N in [ 501, 1000]:  29.7%
```

The 27% headline number is specific to the substrate's `[4, 1000]`
range. Bumping `DATA_BOUND` to 10000 would push the rate higher,
because larger `N` have more divisors and more chances for a
witness to land near the prime curve.

**Examples that show the pattern.** The first few structural
disagreements all have the prime winner sitting essentially *on*
the prime row map:

```
N = 60:  diag (6, 10) → prime (5, 12),  prime_dist = |12 - 11| = 1
N = 72:  diag (8,  9) → prime (6, 12),  prime_dist = |12 - 13| = 1
N = 84:  diag (7, 12) → prime (6, 14),  prime_dist = |14 - 13| = 1
N = 90:  diag (9, 10) → prime (6, 15),  prime_dist = |15 - 13| = 2
N = 96:  diag (8, 12) → prime (6, 16),  prime_dist = |16 - 13| = 3
```

So `cost_prime` is not a "balance with a curvature correction." It
is a *prime-row-map detector* — it identifies composites whose
divisor pairs include a witness near `(k, p_k)` and prefers that
witness when one exists. When no such witness exists, it falls back
to balance-flavored behavior, which is why it agrees with
`cost_diag` on the other 73%.

## What this means for plot 8

The cheapest-sieve experiment, after the disagreement analysis,
identifies **two natural row maps** in the composite lattice:

- **The diagonal frontier** (`cost_diag` winners): roughly
  `n ≈ √N`. Catches every composite at its most-balanced witness.
- **The prime row map** (the disagreement subset of `cost_prime`
  winners): roughly `n ≈ p_k`. Catches the ~27% of composites whose
  divisor pairs land near `(k, p_k)`.

These are two genuinely different curves through the lattice. They
agree on 73% of composites (where the most-balanced witness is also
the closest-to-prime witness) and complement each other on the
remaining 27% (where the prime row map "sees" a witness the
diagonal frontier doesn't reach for).

For plot 8 (complementary curves), the right framing is therefore:
**the diagonal frontier and the prime row map are a candidate pair
whose images partially overlap and partially complement.** That's
not a clean partition — it's a fuzzier object than I had hoped —
but it is a structurally meaningful pair, and the 27% complement
subset is the place where the partition would have to do its work.

## What `winners.npz` contains

```
data_bound:          [1000]
min_k:               [2]
N:                   [4, 6, 8, 10, ..., 1000]               (820 entries)
cost_k_winners:      [[k, n], [k, n], ...]                  (820 x 2)
cost_diag_winners:   [[k, n], [k, n], ...]                  (820 x 2)
cost_prime_winners:  [[k, n], [k, n], ...]                  (820 x 2)
```

The composite at index `i` is `N[i]`, and its winner under cost
`X` is `X_winners[i]`. Plot 8 (complementary curves) and any
follow-up analysis on the 27% subset can consume this directly.

## Reproduce

```
sage cheapest_sieve.py
```

Reads `../witness_density/witnesses.npz`, writes `cheapest_sieve.png`
and `winners.npz` in this directory, prints the agreement rates to
the console. The script asserts each winner against the brute-force
argmin over its witness list, so a wrong cost implementation would
fail the assertion before the figure is rendered.
