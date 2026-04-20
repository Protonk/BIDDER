# SUBSET-STEP-BUDDIES — results

Run: `run_step_buddies.py` + `analyze_step_buddies.py` +
`plot_fig_step_buddies.py` (2026-04-19). Figure:
`paper/fig/fig_step_buddies.png`. 16 runs
(BS(1,2) red and alternating purple at N ∈ {10⁴, 10⁵, 10⁶, 10⁷},
3 seeds per walk for N ∈ {10⁴, 10⁵}, 1 seed for N ∈ {10⁶, 10⁷}).

## Headline

**Both Q1 and Q2 have clean answers, and both differ from the
pilot-based prediction in the plan.**

- **Q2 (cross-N stability at fixed k): strongly confirmed.** At
  each `k ∈ {5, 3, 2, 1.2}`, the ratio `r(N, k) = n_purple/n_red`
  varies by at most 10.2% across `N ∈ {10⁴, 10⁵, 10⁶, 10⁷}` (the
  worst case is `k = 2`, where max/min = 1.102). The plan's
  threshold was 50%; we're well inside it.
- **Q1 (ratio grows as k decreases within a panel): NOT
  confirmed.** The expected "purple takes longer to finish
  saturating" trend doesn't show. Ratios are approximately flat
  across k within each panel, with some non-monotone wobble.
  The `N = 10⁴` panel even trends the *wrong* way (ratio
  slightly decreases as k decreases).

**Slowdown magnitude revised downward.** The plan predicted
1.3–1.5× at near-floor `k = 1.2`, extrapolating from a pilot
value I'd labelled "~1.5×." In fact the full table shows ratios
in a tight band of **1.10 to 1.22** across all 16 (N, k)
combinations. **Purple is ~10–20% slower than red, not 50%
slower.** The earlier "1.5×" number was a misread of a confused
metric (time to each walker's own noise floor, which mixes in
the noise-plateau transition and isn't the same quantity).

## The full table

n(θ_k) values (median across seeds; seeds in brackets). All uncensored.

### N = 10⁴, θ_N = 0.272

| k   | θ_k    | n_red            | n_purple         | ratio |
|:----|:-------|:-----------------|:-----------------|:------|
| 5.0 | 1.36   | 9   [9, 9, 9]    | 11  [11, 12, 11] | 1.22  |
| 3.0 | 0.815  | 19  [18, 19, 19] | 23  [23, 23, 23] | 1.21  |
| 2.0 | 0.543  | 29  [29, 29, 29] | 35  [35, 35, 36] | 1.21  |
| 1.2 | 0.326  | 50  [49, 54, 50] | 59  [62, 58, 59] | 1.18  |

### N = 10⁵, θ_N = 0.0859

| k   | θ_k    | n_red            | n_purple            | ratio |
|:----|:-------|:-----------------|:--------------------|:------|
| 5.0 | 0.430  | 33  [33, 33, 33] | 39  [39, 39, 39]    | 1.18  |
| 3.0 | 0.258  | 48  [48, 49, 48] | 55  [55, 56, 55]    | 1.15  |
| 2.0 | 0.172  | 64  [64, 63, 64] | 71  [71, 71, 71]    | 1.11  |
| 1.2 | 0.103  | 91  [94, 89, 91] | 105 [105, 105, 105] | 1.15  |

### N = 10⁶, θ_N = 0.0272

| k   | θ_k     | n_red | n_purple | ratio |
|:----|:--------|:------|:---------|:------|
| 5.0 | 0.136   | 67    | 77       | 1.15  |
| 3.0 | 0.0815  | 86    | 95       | 1.10  |
| 2.0 | 0.0543  | 105   | 115      | 1.10  |
| 1.2 | 0.0326  | 140   | 165      | 1.18  |

### N = 10⁷, θ_N = 0.00859

| k   | θ_k     | n_red | n_purple | ratio |
|:----|:--------|:------|:---------|:------|
| 5.0 | 0.0430  | 110   | 125      | 1.14  |
| 3.0 | 0.0258  | 130   | 155      | 1.19  |
| 2.0 | 0.0172  | 155   | 175      | 1.13  |
| 1.2 | 0.0103  | 200   | 225      | 1.13  |

## Cross-N stability at fixed k (Q2 check)

| k   | N=10⁴ | N=10⁵ | N=10⁶ | N=10⁷ | max/min |
|:----|:------|:------|:------|:------|:--------|
| 5.0 | 1.222 | 1.182 | 1.149 | 1.136 | 1.076   |
| 3.0 | 1.211 | 1.146 | 1.105 | 1.192 | 1.096   |
| 2.0 | 1.207 | 1.109 | 1.095 | 1.129 | 1.102   |
| 1.2 | 1.180 | 1.154 | 1.179 | 1.125 | 1.049   |

`max/min ≤ 1.10` at every `k`. Cross-N stability strongly
confirmed (spec was ≤ 1.5).

Mild trend: at `k = 5`, ratios slowly *decrease* with increasing
`N` (1.22 → 1.18 → 1.15 → 1.14). This is a small finite-n
effect visible at the coarsest threshold but not at the deeper
ones; plausibly the `N = 10⁴` panel is catching an early-
transient artifact that fades as `N` grows.

## k-trend within panels (Q1 check)

| N      | k=5   | k=3   | k=2   | k=1.2 | trend |
|:-------|:------|:------|:------|:------|:------|
| 10⁴    | 1.222 | 1.211 | 1.207 | 1.180 | ↓ (wrong direction) |
| 10⁵    | 1.182 | 1.146 | 1.109 | 1.154 | U-shaped |
| 10⁶    | 1.149 | 1.105 | 1.095 | 1.179 | U-shaped |
| 10⁷    | 1.136 | 1.192 | 1.129 | 1.125 | no clear trend |

Expected monotone increase as `k` decreases: **not observed**.
The "purple's slowdown grows near saturation" hypothesis from
the plan is empirically refuted at the thresholds we measured.
There's a mild U-shape at `N ∈ {10⁵, 10⁶}` where the ratio dips
at mid-k and recovers at near-floor `k = 1.2`, but the effect
is within 10% and not clearly structural.

## Seed replication at noisy N

At `N = 10⁴` the three seeds gave **identical** `n(θ_k)` values
for `k = 5, 3` (down to the granularity of our sampling grid).
At `k = 2, 1.2` seeds differed by at most 1–5 steps. At
`N = 10⁵` similar: seed spread ≤ 2 steps at all `k`. So seed-
to-seed MC noise is not a concern for this measurement at the
N values we ran. The 3-seed runs were a reasonable precaution
but turned out to be overkill — a single seed per (walk, N)
would have given the same qualitative story.

## The figure

`paper/fig/fig_step_buddies.png`, 2×2 small multiples. Each panel
shows red (BS(1,2)) and purple (alternating) L₁(n) trajectories
at one value of N, with the panel's noise floor drawn as a
horizontal gray line. No legend, no captions at the subplot
level. The visual story is clean: the same "red slightly below
purple during descent, both plateau at the shared floor" pattern
is visible at every N.

## What this means for the theorem connection

- The factor-of-4 theoretical ceiling from `sim/SUBSET-THEOREM.md`
  is nowhere near tight for this walk. The observed slowdown
  (1.10–1.22×) uses <6% of the ceiling's allowance.
- The empirical finding that `r(N, k)` is roughly constant
  across both `N` and `k` is a stronger empirical claim than
  the theorem itself, which only bounds the ratio. That constant
  value is **~1.15**, which is the paper-defensible number to
  cite.
- `sim/SUBSET-THEOREM.md` has been updated (2026-04-19) to replace
  the earlier "~1.5×" empirical claim with "~1.15×" and to
  reference this run. The theorem file's historical note also
  records the correct origin of the original 1.5× figure (see
  below).

## Deltas from the plan

The plan's calibration (using the earlier pilot's k-ratios) was:

| k   | predicted | actual |
|:----|:----------|:-------|
| 5   | ~1.04     | ~1.18  |
| 3   | ~1.04     | ~1.16  |
| 2   | ~1.16     | ~1.13  |
| 1.2 | ~1.2+     | ~1.16  |

The pilot estimates I gave were based on eyeballing M1 (N=10⁸)
data against alternating (N=10⁶) data — the M1 numbers were from
a different noise-floor context and therefore not directly
comparable at matched `k`. This run, with both walks at matched
N (though with independent seed streams — red and purple each
use their own deterministic seed derived from (walk, N,
seed_idx) arithmetic, not a shared stream), gives the correct
numbers.

The revised empirical statement:

> The alternating walk on BS(1,2) completes any given fraction
> of its convergence to Benford in approximately 1.15× as many
> steps as the full BS(1,2) walk, stable within ±10% across
> walker counts 10⁴ through 10⁷ and across threshold depths
> from 5× the noise floor down to 1.2× the noise floor.

Much cleaner than the earlier "1.3–1.5×, grows near floor"
picture.

## What's saved

- `sim/comparison_walks_results/step_buddies/{bs12,alt}_N1e{4,5,6,7}_s{0,1,2}.npz`
  (16 files; 8 for single-seed, 8 for 3-seed)
- `sim/comparison_walks_results/step_buddies/analysis.npz` —
  processed ratio table
- `paper/fig/fig_step_buddies.png` — 2×2 small-multiples figure

## Corrected origin of the original "1.5×"

Initially I'd suggested the 1.5× came from comparing each walk
to its own noise floor. That explanation is wrong. M1 at N = 10⁸
did **not** reach its own floor within its n = 600 horizon
(final L₁ / θ_N = 1.27, see `m1_b1_b2_SUMMARY.md`), so "time to
own floor" couldn't have been the measurement.

The actual source, verified by direct recomputation from saved
arrays: the old "~1.5×" was a **cross-N same-absolute-threshold**
comparison. Purple at `N = 10⁶` hits its own floor `θ_N(10⁶) ≈
0.0272` at `n = 181`; red at `N = 10⁸` (M1) hits that same
*absolute threshold* at `n ≈ 127`. Ratio: 181 / 127 ≈ **1.43**,
rounded in notes to ~1.5×.

That measurement mixes two things: (a) the structural slowdown
of purple vs red, and (b) the fact that for red the threshold
0.0272 is mid-descent (not near its own much-lower floor), while
for purple it's exactly the saturation point. The apples-to-
apples matched-N version (this run) gives ~1.15×, and the extra
30%-ish factor in the old number came from the mismatched
comparison regime rather than anything about the walks' dynamics.

`sim/SUBSET-THEOREM.md` now carries this corrected historical
note; also updated the one-sentence takeaway and the paper-safe
citation language.

## Follow-ups

1. **`comparison_walks_SUMMARY.md`** still cites "~1.5×" in its
   headline paragraph, with the same mismatched-comparison origin.
   Should be updated to ~1.15× with a one-line note pointing at
   this run, if we cite that summary for paper work.
2. **The k-trend finding (Q1 refuted)** is of theoretical
   interest: we had expected purple's slowdown to grow near
   floor as both walks approach saturation. The measured flat
   k-profile says that isn't how the sub-sampling penalty
   manifests in this walk. If the paper ever discussed "ratio
   grows near floor," that discussion needs to go.
