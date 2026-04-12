# Bidderize: where the permutation matters

Three figures showing cases where BIDDER's keyed permutation
produces visibly different results from numpy's PRNG. The point
is not "BIDDER is better" in general — it's that the
without-replacement property has specific, observable consequences
that IID sampling doesn't have, and those consequences are
sharpest when the sampling ratio is low or the uniformity
constraint is load-bearing.


## Figure 1. Sampling aliasing at declining coverage

`aliasing.py` → `aliasing.png`

**Setup.** The escalating_mul experiment's inner loop draws
`n_trials` partner indices from a pool of `N = 9000` source
values. At `n_trials / N = 89%` the two generators look identical.
What happens as we reduce coverage?

Small multiples grid: 2 rows × 6 columns. Top row is BIDDER
cipher, bottom row is numpy PRNG. Columns are coverage ratios:
`n_trials / N` = 90%, 70%, 50%, 30%, 15%, 5%. Each panel is a
shutter heatmap (first digit × step) for the same schedule
(10k adds, 1 mul, 10k adds) — just the first two phases of
escalating_mul, enough to see the staircase and the first mul
kick.

**What to look for.** At high coverage, both rows are
indistinguishable. As coverage drops:

- **Numpy** develops speckle: some source values are sampled
  multiple times while others are skipped entirely, creating
  random hot/cold spots in the digit histogram. The staircase
  edges blur. The mul kick is diffuse.

- **BIDDER** stays clean: the permutation guarantees every source
  value appears at most once per step (when `n_trials ≤ N`), so
  there are no duplicates and no gaps. The staircase edges remain
  sharp. The mul kick is crisp.

The crossover — the coverage ratio where the two become visually
distinguishable — is the figure's punchline. Prediction: somewhere
around 30-50%, where numpy's duplicate rate exceeds ~10% of samples.

**Runtime.** 12 panels × ~10k steps × modest n_trials. Fast even
with pure Python bidder because the periods are small (N = 9000)
and only one cipher per step.


## Figure 2. Digit-count exactness over one period

`exactness.py` → `exactness.png`

**Setup.** BIDDER's Recipes section documents the uniform-symbols
construction: `period = k * m`, then `(B.at(i) % k) + 1` gives
each of the `k` symbols exactly `m` times. Numpy's `rng.integers`
gives each symbol *approximately* `m` times, with binomial
variance.

Single figure, two panels side by side. Both show a bar chart of
symbol counts for an alphabet of size `k = 9` over one full
period. Left panel: BIDDER cipher (`period = 9000`, fold mod 9).
Right panel: numpy (`rng.integers(1, 10, size=9000)`).

The BIDDER bars are all exactly 1000. The numpy bars jitter around
1000 with standard deviation ~√(9000 × 1/9 × 8/9) ≈ 29.8.

Then below: a second row showing the same comparison but over 10
independent periods (BIDDER with 10 different keys, numpy with 10
different seeds). 10 grouped bar charts per panel. BIDDER: every
group is exactly 1000. Numpy: each group jitters independently.

The visual: BIDDER's bars are a flat line. Numpy's bars are a
noisy picket fence. The flatness is the permutation property made
literal.

**Why this matters.** This is the property the calibration-notebook
consumer wanted ("each of digits 1..9 appears exactly 1000 times").
The figure shows it's not approximate — it's exact, and it's exact
on every key, not just in expectation.

**Runtime.** Trivial. Two ciphers, two numpy calls, bar charts.


## Figure 3. Collision heatmap under repeated sampling

`collisions.py` → `collisions.png`

**Setup.** Draw `n` samples from a pool of `N` items, repeatedly.
For each draw, count the number of *collisions* (items sampled
more than once). This is the birthday-problem regime.

Heatmap: x axis is `n / N` (sampling ratio, from 0.01 to 1.0),
y axis is the number of independent draws (1 to 100). Color is
the mean collision count across draws.

Two panels side by side. Left: numpy (`rng.integers(0, N, size=n)`
for each draw). Right: BIDDER (`B.at(i) for i in range(n)` with a
fresh key per draw — a permutation, so collisions are always 0
when `n ≤ N`).

**What to look for.** The numpy panel shows a smooth gradient:
collisions grow as `n² / (2N)` (the birthday bound), reaching
saturation near `n / N = 1`. The BIDDER panel is **solid black**
for all `n ≤ N` (zero collisions, always) and only lights up at
`n > N` when the permutation wraps.

The visual contrast is extreme: a smooth birthday-problem gradient
against a hard black/bright wall at `n = N`. The permutation
property shows up as a phase transition, not a gradual crossover.

Below the heatmap: a line plot of mean collisions vs `n / N` at
draw count = 50. Numpy traces the birthday curve. BIDDER is
identically zero until `n = N`, then jumps. Two lines, one
prediction.

**Why this matters.** Any application that samples a source and
needs distinct values (stratified sampling, coverage testing,
calibration) hits the birthday problem with IID draws. BIDDER
eliminates it by construction. The figure makes the elimination
visible.

**Runtime.** Moderate. For each `(n, draw)` cell: one cipher of
period N, iterate n elements. The grid is ~100 × 100 = 10k cells,
each with a small cipher. Fast even in pure Python.


## Execution order

1. `exactness.py` — trivial runtime, proves the concept.
2. `aliasing.py` — moderate runtime, the headline figure.
3. `collisions.py` — moderate runtime, the cleanest contrast.

All three use the `try: import bidder_c / except: import bidder`
convention.
