# Figure 1 substrate — three-walks comparison

Paper-side anchor for PNAS-PLAN §5 Figure 1 ("Convergence to
Benford requires mixing"). Compresses the sim evidence into the
content that will go into the caption, the figure itself, and
the §6 kicker that the three-walks comparison supports.

Underlying sim doc: `sim/comparison_walks_SUMMARY.md`.
Underlying data: `sim/comparison_walks_results/`,
`sim/m1_b1_b2_results.npz`.

## What the figure shows

Three random walks from the same initial condition (x₀ = +√2),
projected to the mantissa m = log₁₀|x| mod 1, with L₁(m_n, Leb_T)
plotted vs n on log-log axes.

| curve          | step set              | N    | n_max | visual |
|:---------------|:----------------------|:----:|:-----:|:-------|
| BS(1,2) mix    | {a, a⁻¹, b, b⁻¹}      | 10⁸  | 600   | red solid, concave-down, plunges to noise floor |
| pure add       | {b, b⁻¹} only         | 10⁶  | 10⁴   | blue/green, near-flat at L₁ ≈ 1.9 |
| pure mul       | {a, a⁻¹} only         | 10⁶  | 2000  | near-flat at L₁ ≈ 1.85 |

Figure files already exist at
`paper/fig/fig_three_walks_loglog.{png,pdf}`.

## The central quantitative facts

### Observable-horizon L₁

| walk       | L₁ at n = 600 | L₁ at n = 10⁴ |
|:-----------|:-------------:|:--------------:|
| BS(1,2)    | 3.4 × 10⁻³    | (below N = 10⁸ floor) |
| pure-add   | 1.88          | 1.57           |
| pure-mul   | 1.86          | 1.79 (at n = 2000) |

Pure-add and pure-mul are stuck at L₁ ≈ 1.5–2.0 over 10⁴ steps.
BS(1,2) hits its N = 10⁸ noise floor by n ≈ 300.

### Log-log slopes for the pure walks

- Pure multiplicative: slope −0.034 on log-log.
- Pure additive: slope −0.057 on log-log.

### Extrapolated steps-to-floor (for reviewer-response context)

Assuming log-log-linear decay continues (upper-bound
extrapolation):

- Pure multiplicative: n ≈ 10⁸⁵ to reach L₁ = 3 × 10⁻³.
- Pure additive: n ≈ 10⁵¹ to reach L₁ = 3 × 10⁻³.
- BS(1,2): n ≈ 300 (measured, not extrapolated).

## Mechanism sentences for the caption (one per curve)

- **Pure multiplicative** is irrational rotation on T by ±log₁₀ 2.
  From a delta IC, after n steps the support has at most n + 1
  points on T; with 1000 histogram bins, most bins stay empty
  until n ≳ 1000. Fourier coefficients do decay exponentially,
  but the 1000-bin L₁ statistic requires a continuous density.
- **Pure additive** is a simple random walk on ℤ. |x| grows like
  √n, so log|x| spans only (1/2) log₁₀ n decades at time n. At
  n = 10⁴, that is two decades of magnitude; the mantissa
  distribution never populates enough of T to look Benford on
  this statistic.
- **BS(1,2) mix** has the b-step nonlinearity at low |E|, which
  creates mantissa spread rather than shifting it. One b-step at
  E = 0 from x = √2 sends walkers to x = √2 + 1 or x = √2 − 1
  with mantissas log₁₀(2.414...) ≈ 0.383 and log₁₀(0.414...) ≈
  0.617 — two new mantissa values. After a few steps the
  walker's mantissa distribution is continuous, and the 1000-bin
  L₁ can converge.

## How the figure carries paper content

### Columbo lead (PNAS-PLAN §1 / §2 / §5)

The figure's title — "Convergence to Benford requires mixing" —
and the three curve shapes (two flat, one plunging) state the
paper's central empirical claim before any prose unpacks it. A
reader who sees the figure already holds:

- Pure addition alone does not converge (Hamming's asymmetry,
  visible).
- Pure multiplication alone does not converge on any practical
  horizon (Schatte's analytical finding, visible as the near-flat
  top curve).
- The mix converges, and does so at n ≈ 300 for the M1 IC.

### §6 Hamming kicker

The kicker (PNAS-PLAN §6 Movement B) contrasts the paper's
Markov-chain mechanism with Schatte's ex-post-facto Riesz
logarithmic weighting. The figure is the empirical half of that
contrast: the mix is a single Markov chain with no ex-post
re-weighting, and it converges; neither pure sub-walk does.

### §7 Robustness (pure-addition boundary)

The pure-add curve is also the empirical anchor for §7's "pure
addition (the boundary): non-convergence (Schatte 1986, confirmed
by simulation)." The figure _is_ the "confirmed by simulation"
part — the blue/green curve's flat shape at L₁ ≈ 1.9 across 10⁴
steps.

## Caption language (paper-ready, approximate)

> **Fig. 1. Convergence to Benford requires mixing.** L₁ distance
> of the mantissa marginal from the Benford (uniform on T)
> distribution versus step count n, same √2 initial condition,
> log-log axes. Red solid (BS(1,2) mix, N = 10⁸): symmetric
> ±1/4 probability over {a, a⁻¹, b, b⁻¹}; reaches noise floor by
> n ≈ 300. Blue (pure additive, N = 10⁶): {b, b⁻¹} only; stays
> at L₁ ≈ 1.9 through n = 10⁴. Green (pure multiplicative,
> N = 10⁶): {a, a⁻¹} only; stays at L₁ ≈ 1.85 through n = 2000.
> L₁ = Σ_j |count_j / N − 1/B| with B = 1000 bins on T; θ_N
> lines mark the multinomial null floor for each N.
> Extrapolations of the pure-walk log-log slopes give n ≈ 10⁵¹
> (additive) and n ≈ 10⁸⁵ (multiplicative) to reach the
> N = 10⁸ floor. The mix's nonlinearity at low |E|
> (b-step ε-perturbation) creates continuous mantissa spread;
> neither sub-walk does.

## Caveats (paper should not claim beyond these)

- Extrapolations assume log-log-linear continuation. Real decay
  may curve; the extrapolated n is an upper bound on when the
  sub-walks would hit the floor.
- The L₁ statistic is support-sensitive. Pure-mul's "slow
  convergence" on L₁ is partly a binning-statistic artifact
  (Fourier coefficients decay faster). The paper's Benford
  statement is about continuous densities, so the support-
  sensitivity is the right story for the figure.
- Pure-mul and pure-add both equidistribute on T asymptotically
  (Weyl / classical Benford on ℤ). The paper's claim is about
  _observable-horizon_ behavior relevant to real data, not about
  asymptotic equidistribution.

## Pointers

- Run script: `sim/run_comparison_walks.py`.
- Sim summary: `sim/comparison_walks_SUMMARY.md`.
- Figure: `paper/fig/fig_three_walks_loglog.{png,pdf}`.
- Relevant PNAS-PLAN sections: §1 intro, §2 Theorem 1, §5 Fig 1,
  §6 kicker, §7 robustness (pure-addition bullet).
