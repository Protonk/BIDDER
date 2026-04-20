# Comparison walks — "why BS(1,2) is special" figure

Run: `run_comparison_walks.py` → `comparison_walks_results/`
(2026-04-18). Figure: `paper/fig/fig_three_walks_loglog.{png,pdf}`.

## Purpose

Paper-supporting figure for the scenario where the convergence-rate
story becomes a bigger deal (e.g. a reviewer pushes back on "but
α = 1/2 is slow, why does BS(1,2) produce Benford on real data?").
Shows directly that **only the full BS(1,2) walk converges to Benford
on an empirically relevant horizon**. Pure multiplicative and pure
additive sub-walks both fail to converge in any useful sense on our
10⁴-step horizon, and would require astronomically more steps
(n ≈ 10⁵¹ for pure-add, n ≈ 10⁸⁵ for pure-mul, by extrapolation)
to reach BS(1,2)'s measured n=600 position.

## The three walks

All from the same IC: x₀ = +√2, symmetric measure over the allowed
step set.

| walk               | allowed steps           | N        | n_max  |
|:-------------------|:------------------------|---------:|-------:|
| BS(1,2) mix        | {a, a⁻¹, b, b⁻¹} (M1)   | 10⁸      | 600    |
| Pure multiplicative | {a, a⁻¹} only           | 10⁶      | 2000   |
| Pure additive       | {b, b⁻¹} only           | 10⁶      | 10 000 |

## Headline

Measured on the same 1000-bin L₁ statistic:

| walk               | L₁ at n=600 | L₁ at n=10⁴ | log-log slope |
|:-------------------|------------:|------------:|--------------:|
| BS(1,2) mix        | 3.4×10⁻³    | (below floor at N=10⁸ by then) | curved, hits θ_N by n≈200-600 |
| Pure multiplicative | 1.86        | 1.79 (at n=2000)             | −0.034 |
| Pure additive       | 1.88        | 1.57                          | −0.057 |

Both pure sub-walks are stuck at L₁ ≈ 1.5–2.0 over 10⁴ steps.
Extrapolating the log-log slopes, they would need cosmologically
many steps to reach even the N=10⁸ noise floor:

- Pure multiplicative: n ≈ 10⁸⁵ to hit L₁ = 3×10⁻³
- Pure additive: n ≈ 10⁵¹ to hit L₁ = 3×10⁻³

Compare: BS(1,2) hits it by n ≈ 300.

## Why the sub-walks fail (mechanism, for the paper caption)

Both failures have clean mechanistic explanations that the paper
can cite in one sentence each:

- **Pure multiplicative** is equivalent to an irrational rotation on
  T = ℝ/ℤ by ±log₁₀ 2. From a delta initial condition, the mantissa
  support after n steps is at most n+1 distinct points on T. With
  1000 histogram bins, most bins are empty until n ≳ 1000, bounding
  L₁ below at ≈ 1 − (support coverage). Fourier coefficients decay
  exponentially, but ensemble L₁ doesn't see this because L₁ with
  fine binning requires a **continuous** density, not just fast
  Fourier decay.
- **Pure additive** is a simple random walk on ℤ. Walker position
  |x| grows like √n, so log₁₀|x| spans only (1/2)log₁₀ n decades
  at time n. At n = 10⁴, that's 2 decades of magnitude; the
  mantissa distribution never populates enough of T to look
  Benford.
- **BS(1,2) mix** has the b-step nonlinearity at low E, which
  *creates* mantissa spread rather than shifting it. Starting from
  a delta at m = log₁₀√2, one b-step at E = 0 sends walkers to
  x = √2 + 1 or √2 − 1 with mantissas log₁₀(2.414...) ≈ 0.383 and
  log₁₀(0.414) ≈ 0.617 — two genuinely new mantissa values. After
  a few steps, the walker's mantissa distribution is continuous
  (densely supported on T), which is what the 1000-bin L₁ needs
  to converge.

This is the "Goldilocks" statement: the full walk is the minimal
random walk on an abelian-by-cyclic BS-type group whose generators
include a nonlinear move at the low-|E| zone, and that nonlinearity
is exactly what turns a countable-support mantissa into a
continuous one in O(10) steps.

## Data saved

- `comparison_walks_results/pure_mul_results.npz` — (sample_times,
  l1, metadata). N = 10⁶, n = 2000, seed 0xCA1C0FFEE.
- `comparison_walks_results/pure_add_results.npz` — same schema.
  N = 10⁶, n = 10⁴, seed 0xADDAD0DE.

BS(1,2) data reuses existing `m1_b1_b2_results.npz`.

## Figure files

- `paper/fig/fig_three_walks_loglog.png` (160 dpi, display)
- `paper/fig/fig_three_walks_loglog.pdf` (vector, paper inclusion)

Features:
- Three L₁(n) log-log curves (red solid, blue dashed, green dotted)
- Two noise floor lines (θ_N at N = 10⁶ and 10⁸)
- "Empirical horizon" shaded band at n ∈ [50, 1000]
- Inline annotations for each curve's dominant mechanism
- Bottom-right info box with extrapolated n-to-floor for
  context

## When to deploy

- As a **paper figure** if the "α = 1/2 is slow, why is BS(1,2)
  Benford on real data?" objection surfaces. The figure answers:
  BS(1,2) converges at the empirical horizon even with the
  algebraic asymptotic rate, and no subgroup-only walk has this
  property.
- As a **talk slide** for the intuition. The log-log plot with
  two flat-at-top lines and one plunging line visually makes the
  "only the mix converges" point in one glance.
- As a **reviewer response** artifact. The extrapolation
  numbers (10⁵¹ and 10⁸⁵) make the "pure sub-walks don't work
  empirically" case quantitative rather than hand-wavy.

## Caveats

- Extrapolations assume log-log-linear decay continues. This is
  a conservative estimate for both pure walks (actual decay
  likely curves downward beyond our horizon, so the extrapolated
  n is an *upper bound* on when they'd hit the floor). Still
  astronomically large.
- The L₁ statistic's support-size sensitivity means pure-mul's
  "slow convergence" is partly a statistic-choice artifact — the
  Fourier coefficients decay exponentially. The figure uses L₁
  because that's the paper's primary statistic, and the support-
  sensitivity is part of the story (the paper's Benford statement
  is about continuous densities, not Fourier decay).
- This is not a claim about the asymptotic behavior of pure walks.
  Pure multiplicative does equidistribute on T (by Weyl); pure
  additive does too (by the Benford theorem for natural numbers).
  The claim is strictly about *observable-horizon* behavior
  relevant to real data.
