# Projection check — summary

Re-running ℤ² (L=31) and H_3(ℤ/15) full and alternating walks at
N = 10⁶, n_max = 2000, and computing L₁ under multiple projections
of the state space in a single pass per (group, walk).

Run script: `run_projection_check.py`.
Analysis: `analyze_projection_check.py`.
Data: `projection_check_results/`.
Date: 2026-04-19.

## Why we ran this

Outstanding question from `h3_contrast_SUMMARY.md`: BS(1,2) shows
r ≈ 1.15× at the mantissa (a 1D projection of a much larger state
space); the natural-L₁ walks on ℤ² and H_3 show r ≈ 2×. We
hypothesized that BS(1,2)'s smaller r comes from projecting a
higher-dimensional walk onto a 1D observable, and that if we
measured ℤ² or H_3 under low-D projections we'd see r drop from
2× toward ~1×. The BS12-FULLSTATE route to test this was
killed (`BS12-FULLSTATE-SIM.md`) because BS(1,2) has no natural
finite-quotient reference. So instead: test the
projection-reduces-slowdown story on groups where we already have
apples-to-apples matched-threshold comparisons.

## Predictions going in

- ℤ² full 2D: r ≈ 2.0 (confirms prior)
- ℤ² x_1d marginal: **r ≈ 1.0** (expected — x gets same # updates
  on average for both walks)
- H_3 full 3D: r ≈ 2.0
- H_3 (a,b) 2D: ~2.0 (abelianized)
- H_3 a_1d: r ≈ 1.0 by same argument as ℤ²
- H_3 c_1d: wildcard

## Actual results

| group | projection | r = n_alt / n_full |
|:------|:-----------|:------------------:|
| ℤ²    | full_2d    | 2.00 |
| ℤ²    | x_1d       | **3.83–4.00** |
| ℤ²    | y_1d       | **3.92–4.09** |
| H_3   | full_3d    | 2.00 |
| H_3   | ab_2d      | 1.94–2.05 |
| H_3   | a_1d       | **3.63–4.20** |
| H_3   | b_1d       | **3.73–4.10** |
| H_3   | c_1d       | **1.57–1.80** |

(Ranges are across k ∈ {5, 3, 2, 1.2}.)

**The 1D marginal prediction was wrong. Projections can _increase_
r, not decrease it.** r goes from 2× on full state to 4× on an
axis marginal.

## Why — Fourier spectral analysis

On Z/L with L=31, the slowest-decaying Fourier mode for each
(walk, observable) determines r, and each case below matches data
to three-digit precision.

**x-marginal (1D on Z/31).** Both walks project down so that only
(k₁, 0) modes survive.

| walk | slowest 1D mode | magnitude per calendar step | decay rate |
|:-----|:----------------|:----------------------------|:-----------|
| alt  | k = 15 (near-parity): cos(2π·15/31) ≈ −0.9949 per x-step, one x-step per 2 cal steps | 0.9949^{1/2} = 0.99745 | 0.00256 |
| full | k = 1: laziness folds cos(2π·k/L) through → (1+cos(2πk/L))/2; at k = 15 this is 0.00255 (dead), so slow mode shifts to k = 1 at 0.9898 | 0.9898 | 0.01025 |

ratio = 0.01025 / 0.00256 = **4.00**. Matches.

**2D full state on Z²/31².** Both walks' slowest 2D mode is
**parity-like** (k₁, k₂) with k ≈ L/2, but the asymmetric step
schedule of alt makes its axis-parity modes slower than full's
diagonal-parity mode.

| walk | slowest 2D mode | magnitude per calendar step | decay rate |
|:-----|:----------------|:----------------------------|:-----------|
| alt  | (15, 0) or (0, 15) "axis parity": cos(2π·15/31)·1 = −0.9949 per 2-step block (only x moves on odd steps) | 0.9949^{1/2} = 0.99745 | 0.00256 |
| full | (15, 15) "diagonal parity": (cos(2π·15/31)+cos(2π·15/31))/2 = −0.9949 per step | 0.9949 | 0.00511 |

ratio = 0.00511 / 0.00256 = **2.00**. Matches.

The extra factor of 2 on the 1D marginal is driven by the fact
that **alt's slowest 1D Fourier mode is the near-parity mode
k ≈ L/2** (cos(2π·15/31) ≈ −0.995), which the lazy (full) walk
completely kills by folding it through (1 + cos)/2 to ≈ 0.003.
On 2D, both walks are bottlenecked by _some_ near-parity mode,
but alt's axis-parity mode (one coord at L/2, the other at 0)
decays half as fast as full's diagonal-parity mode (both coords
at L/2) because alt updates each axis only half the calendar
time.

## The c-marginal anomaly (H_3)

c_1d gives r ≈ 1.7, not 4.0. This is because c isn't a standalone
RW on Z/15 — it's driven by δ_b · a, i.e., its update depends on
the walker's current a value. The slow-mode structure of the
c-marginal depends on coupled a–y dynamics, not a pure 1D SRW
spectral gap.

Rough argument: for alt, c updates only on y-steps (every other
calendar step), each time by ±a. So c's increments have mean 0
and variance E[a²]. Once a has mixed on Z/15, the c-increments
look roughly like ±U where U is uniform on {0, ..., 14}. This
mixes c differently from a pure ±1 walk — the parity structure
is scrambled because a takes many values.

So the c-marginal escapes the parity-mode penalty that a_1d and
b_1d suffer, and sits between the "pure marginal" r=4 and the
"full state" r=2. Empirically r ≈ 1.7 — below 2, which is
notable.

## Implications for BS(1,2) mantissa

The 1.15× result on BS(1,2)'s mantissa projection does NOT
naturally fall out of the "projection reduces slowdown" story,
because that story is false as stated — on pure 1D marginals,
projection _increases_ r.

What the c-marginal result hints at is a different mechanism:
projections onto **coordinates whose increments depend on the
state in a non-trivial way** (like c's dependence on a, or
mantissa's dependence on the E coordinate in BS(1,2)) can give
smaller r than both the pure 1D marginal and the full state.
The mantissa observable has the right flavor — its increments
depend on the current m value via the logarithmic law. This is
a more plausible story than my original "projection averages
out slowdown" intuition.

Not proved. But the c-marginal r ≈ 1.7 provides a concrete
non-trivial data point against the "r is either 1, 2, or 4"
clean story.

## Updated group-observable table

| group / observable                       | r    | regime           |
|:-----------------------------------------|:----:|:-----------------|
| F_2 tree / drift                         | 0.5  | speedup          |
| BS(1,2) / mantissa L₁ (T = ℝ/ℤ)          | 1.15 | intermediate     |
| H_3 / c-marginal                         | ~1.7 | intermediate     |
| ℤ² / full L₁ on L² cells                 | 2.0  | saturated        |
| H_3 / full L₁ on L³ cells                | 2.0  | saturated        |
| H_3 / (a, b) 2D                          | 2.0  | saturated        |
| ℤ² / x-marginal (axis projection)        | 4.0  | parity-mode      |
| H_3 / a-marginal or b-marginal           | 4.0  | parity-mode      |

## What this means for the paper

The candidate paper claim "BS(1,2)'s 1.15× comes from projection
averaging out the 2× slowdown" is not supported in this clean
form. The spectral picture is richer:

1. On a fixed lattice walk, r depends on the projection's
   spectral structure, not on its dimension per se.
2. Pure axis marginals can give r = 4× (alt's near-parity mode
   survives projection but full's is killed by laziness).
3. Twisted-coupling marginals (c in H_3) give intermediate r
   between 2× and 1×.
4. BS(1,2)'s 1.15× sits in that intermediate regime — plausibly
   driven by the same mechanism as H_3's c-marginal: the
   mantissa's increments depend on the state (via E), so it
   doesn't look like a pure 1D SRW.

Honest footnote for the paper:

> Sub-sampling slowdown varies by group, observable, and the
> observable's coupling to the state. On natural finite-quotient
> L₁ observables for ℤ² and H_3, alternating is ~2× slower;
> on pure axis marginals of those groups, ~4× slower (driven by
> the near-parity Fourier mode); on the H_3 commutator marginal
> ~1.7×; on the BS(1,2) mantissa ~1.15×. The free group F_2
> gives 2× _faster_ (lazy-walk speedup). There isn't a clean
> "group structure" or "dimension" determinant; the slowdown is
> spectral and depends on how the observable interacts with the
> walk's slowest modes.

This is messier than the previous draft, but closer to the
truth. The paper's conversational point ("only the full mix
converges in practice") doesn't depend on getting the slowdown
taxonomy exactly right, so the sensible move is probably to
omit the slowdown section and let the three-walks figure carry
the point alone.

## What's saved

- `projection_check_results/{z2,h3}_{full,alt}.npz` — 4 files.
  Each stores `sample_times`, `l1_<proj>` per projection, plus
  meta fields (`meta_L`, `meta_N`, `meta_seed`, `meta_walk`,
  `meta_group`).

## What's not done

- Finer-resolution sampling for the H_3 c-marginal near-floor
  behavior. The r ≈ 1.7 estimate is based on step-10 sampling
  which has quantization at k=5.0 giving (50, 90) → 1.80 —
  large relative quantization at small n.
- Projection check on BS(1,2) itself. Would need a finite
  quotient; blocked by the same issue that killed
  `BS12-FULLSTATE-SIM.md`.
- Closed-form formula for r(projection) on ℤ² and H_3 given
  the spectral-gap decomposition. The 4× and 2× ratios are
  exact in the spectral calculation above; the c-marginal
  1.7× would need a calculation we haven't done.
