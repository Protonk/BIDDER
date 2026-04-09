# Complementary curves

`complementary_curves.png` is a 2-panel figure for the
"complementary row map" sweep at lattice scale `x = 10000`. The
left panel is a heatmap of joint coverage `|I_1 ∪ I_2|` for each
pair of 8 candidate row maps (28 unique pairs). The right panel is
a scatter of joint coverage vs disjoint rate, with the Pareto
frontier traced and the top 5 pairs labeled. `pairs.npz` is the
substrate with the full leaderboard data.

## The eight row maps

| symbol     | formula            | character                       |
|------------|--------------------|---------------------------------|
| `pronic`   | `n_k = k + 1`      | densest possible, hugs diagonal |
| `shift_2`  | `n_k = k + 2`      | shifted pronic                  |
| `shift_3`  | `n_k = k + 3`      | further shifted                 |
| `odd`      | `n_k = 2k + 1`     | linear, slope 2                 |
| `odd_3`    | `n_k = 2k + 3`     | shifted slope 2                 |
| `prime`    | `n_k = p_k`        | non-linear, the curve from plot 9 |
| `square`   | `n_k = k² + 1`     | quadratic                       |
| `prime_n`  | `n_k = p_{k+1}`    | shifted prime                   |

Each row map has its image computed up to `x = 10000`:

```
pronic    : |I| =  98
shift_2   : |I| =  98
shift_3   : |I| =  98
odd       : |I| =  69
odd_3     : |I| =  68
prime     : |I| =  46
square    : |I| =  20
prime_n   : |I| =  45
```

## The headline finding: the prediction failed

Going into plot 8, plot 9 had predicted that **`(pronic, prime)`**
would top the leaderboard, on the reasoning that the prime row map
picks up the 27% disagreement subset that the diagonal frontier
misses. The actual result puts `(pronic, prime)` at **rank 12 of
28**, well below the top.

The actual top 3 are tied at `union = 196`, all involving the three
densest row maps:

```
1.  pronic × shift_2   union=196  intersection=0  rate=1.000
2.  pronic × shift_3   union=196  intersection=0  rate=1.000
3.  shift_2 × shift_3  union=196  intersection=0  rate=1.000
```

For comparison:

```
12. pronic × prime     union=143  intersection=1  rate=0.993
```

## Why the prediction failed (the structural finding)

Two things came out of this that I want on the record, because they
matter for how we use the lattice in future work.

**1. Disjointness is essentially free at this scale.** The disjoint
rate range across all 28 pairs is `[0.974, 1.000]` — a variation of
under 3 percentage points. Every pair is "complementary" in the
trivial sense that any two ascending row maps are sparse enough to
not collide. Each row map catches `O(√x) ≈ 100` composites in a
lattice of `O(x) = 10000` cells; the probability of two random
row maps catching the same composite is `O(1/√x) ≈ 1%`, and the
empirical numbers match. **At this lattice scale, "complementary"
isn't a meaningful filter.**

The leaderboard is therefore dominated by *individual row map
size*, not by complementarity. `pronic`, `shift_2`, and `shift_3`
all hit the maximum of 98 catches (because their `k · R(k) = k² +
ck` grows fastest in `k`), and any pair among them maxes out at
`196 = 2 · 98` with no overlap. The next-best pairs add an
`odd`-flavored row map (which catches 68-69 composites because
`k · (2k+1) ≈ 2k²` saturates at `k ≈ √(x/2) ≈ 70`). And so on. The
leaderboard is just "rank by individual size."

**2. The prime row map catches a *narrower* class of composites
than plot 9 suggested.** Plot 9's `cost_prime` is a *witness
selector* — for each composite `N` it picks the witness `(k, n)`
closest to the prime curve `n = p_k`, even if `n` differs from
`p_k` by a few. The 27% disagreement subset there is composites
whose divisor structure has a witness *near* the prime curve.

The *prime row map itself* (`n_k = p_k`) is a much narrower object:
it catches exactly the composites `{k · p_k} = {2, 6, 15, 28, 55,
78, 119, 152, 207, 290, ...}` — a sparse arithmetic sequence with
46 elements below `x = 10000`. Most of the highly composite numbers
that plot 9 highlighted (`60, 72, 84, 96, 120`) are *not* of this
form. They're caught by `cost_prime` because they have *some*
witness near the prime curve, but they're not caught by the prime
row map because the prime row map only walks one specific witness
per `k`.

So plot 9's "the prime curve detects highly composite N" insight
does not transfer to "the prime row map covers highly composite
numbers." They are related but different. Plot 9 was about
selectors; plot 8 is about generators. Selectors can pick from a
2-D set of witnesses; generators are forced to walk a 1-D curve.

## What the picture shows

**Left panel (heatmap):** joint coverage `|I_1 ∪ I_2|` for each
pair, with cells labeled by the count. The gradient runs from
yellow (high coverage, ~196) to dark purple (low coverage, ~64).
The visible bands are:

- Yellow `3 × 3` block in the top-left (pronic / shift_2 / shift_3
  pairs)
- Teal mid-tier (the three dense row maps paired with `odd` or
  `odd_3`)
- Mid-purple (anything paired with `prime` or `prime_n`)
- Dark purple corner (`square` paired with `prime` or `prime_n`)

**Right panel (Pareto scatter):** each pair as a point in
`(|union|, disjoint_rate)` space. The y-axis is zoomed to
`[0.7, 1.03]` because all rates are above 0.97. The Pareto frontier
is the dashed line through the three top pairs in the upper-right
corner. The `(pronic, prime)` prediction is circled in red — it
sits in the middle of the cloud, clearly off the frontier.

The two panels carry different information. The heatmap shows
*which row maps catch a lot together*; the scatter shows *the
trade-off between coverage and disjointness*. At this scale, there
isn't much trade-off — disjointness is uniformly high — so the
useful axis is coverage, and the heatmap is the more informative
panel.

## What this means for the garden

The "complementary curves" question, as posed in `CANTORS-PLOT.md`,
is degenerate at lattice scale `x = 10000`. Every pair of ascending
row maps is essentially complementary because they're individually
too sparse to collide. The original `60–70% disjoint coverage`
threshold in the spec is met by every pair by a wide margin — the
lowest rate in the sweep is 97.4%, and most are above 99%.

**For the question to become interesting, we need either:**

- **More scale.** At `x = 10^6`, each row map catches `~1000`
  composites and collisions are far more likely. The disjoint rate
  would drop below 1 in interesting ways and the leaderboard would
  rank by complementarity rather than by raw size. This is the
  cheapest fix — bump `X` and rerun. Worth doing.

- **A different metric.** Instead of disjoint rate, score pairs by
  coverage of a *structured* subset (the highly-composite numbers,
  the disagreement subset from plot 9, the squarefree composites,
  etc.). This directly tests which row maps catch the *interesting*
  composites rather than just lots of composites. More work but
  more pointed.

- **Different candidates.** The 8 closed-form row maps in this
  sweep are all linear or near-linear. Adding row maps with
  *similar* growth rates (e.g., `(k+1, k+2)` already in the sweep,
  or new candidates that grow at exactly the same rate) would force
  more collisions and surface partition structure that the current
  candidates don't have.

The honest read of plot 8 at `x = 10000` is that the lossy sieve
problem at small lattice scale is dominated by individual row map
size, and the "complementary" question doesn't bite until the row
maps are dense enough to collide. Plot 9's `cost_prime` is doing a
different kind of work than what closed-form row maps can do, and
the two pictures of "natural row map" don't merge cleanly.

## What `pairs.npz` contains

```
bound:       [10000]
names:       array of 8 row map name strings
individual:  [98, 98, 98, 69, 68, 46, 20, 45]   per-row-map sizes
i, j:        index arrays (28 entries each)
union:       |I_i ∪ I_j| per pair (28 entries)
inter:       |I_i ∩ I_j| per pair
sym:         |I_i △ I_j| per pair
rate:        disjoint rate per pair
```

Pair `k` is `(NAMES[i[k]], NAMES[j[k]])` with statistics
`union[k]`, `inter[k]`, etc.

## Reproduce

```
sage complementary_curves.py
```

Computes images, runs sanity checks via inclusion-exclusion, prints
the leaderboard and prediction check, writes `pairs.npz` and
`complementary_curves.png`.
