# SIM-PLAN

Simulation plan for FIRST-PROOF gap 3 (and, as a side order, gap 4).
One evening for phase 1; phases 2–3 conditional on phase 1's result.

---

## What this decides

The symmetric BS(1,2) walk's L₁-to-Benford decay is either
exp(−λt) or exp(−c√t). These predictions come from different
mechanisms and commit gap 2 to different proof routes:

- **Exponential** ⇒ gap 2 closes via direct Fourier decay on the
  mantissa marginal. Paper's Theorem 1 keeps its exponential rate
  claim.
- **Stretched exponential** ⇒ gap 2 closes via Rosenthal coupling
  (FIRST-PROOF §2 Route 1). Theorem 1 becomes stretched.

The existing measurement (`bs12_rate.py`, fit over t ∈ [20, 100],
R² = 0.99, λ ≈ 0.035) cannot distinguish the two — both shapes are
locally linear on any short interval. We need a longer horizon and
enough walkers to hold L₁ above the noise floor while the two
shapes diverge.

---

## Discrimination window, honestly

Calibrate both models to the existing [20, 100] data before
designing new sampling:

- **Exponential.** λ ≈ 0.035 (reported fit).
- **Stretched.** Match the average slope of log(L₁) vs. t on
  [20, 100]. For log(L₁) = −c√t, d log(L₁)/dt = −c/(2√t). Setting
  this equal to −0.035 at the window's geometric mean t̄ ≈ 45 gives
  c ≈ 2·0.035·√45 ≈ 0.47.

Running each model to the N = 10⁶ noise floor (≈ 3×10⁻³):

- Exp reaches floor at t ≈ 150.
- Stretched (c ≈ 0.5) reaches floor at t ≈ 280.

The shapes separate most clearly in the **t ≈ 150 → 300 window**,
not out to 10⁴. Sample points at t = 1000, 5000, 10000 are floor
noise for both models.

Two design responses:

1. **Dense sampling between t = 50 and t = 300.** Fine log-grid or
   every-few-steps. Linear-fit residuals of log(L₁) vs. t will
   reveal stretched curvature if present — stretched exp has
   slope −c/(2√t) which runs from ≈ −0.056 at t = 20 to ≈ −0.025
   at t = 100, a factor of 2 across the window. An R² of 0.99
   linear fit over [20, 100] is already mild evidence against
   stretched, depending on noise.
2. **N = 10⁷ from the start.** Floor drops to ≈ 10⁻³, shifting
   exp-floor time to t ≈ 260 and stretched-floor time to t ≈ 600 —
   roughly doubling the usable window.

**Pre-sim check on existing data** (before writing any new code).
Refit the current `bs12_rate` output as log(L₁) = −c√t + const on
[20, 100] and report R². If it's materially worse than the reported
0.99 linear fit, the existing data already provides discrimination
and new sims become confirmatory rather than diagnostic.

---

## Representation

Per walker: (m, E) with m ∈ [0, 1) as float64 and E as int64. No
bignum.

- **a-step (×2).** m ← m + log₁₀ 2 mod 1; E ← E + carry(m).
  Constant time.
- **b-step (+1).** Three cases by sign/magnitude of E:
  - E large positive: mantissa barely changes; treat as identity on
    (m, E) up to a cutoff.
  - E near 0: full computation m_new = log₁₀(10^m + 10^{−E}) mod 1,
    E_new = E + carry.
  - E large negative: x + 1 ≈ 1; snap to (0, 0).
- **a⁻¹-step (÷2), b⁻¹-step (−1).** Analogous. Handle the sign
  flip in b⁻¹ when |x| < 1 by taking absolute value (the projection
  m(x) = log₁₀|x| ignores sign).

Vectorize across walkers using numpy under sage (per project
convention).

Noise floor for empirical L₁ over K = 9 digit bins with N walkers is
≈ √(K/N). N = 10⁶ ⇒ floor ≈ 3×10⁻³. N = 10⁷ ⇒ floor ≈ 10⁻³.

---

## Phase 1 — diagnostic

**Setup.** Symmetric measure (weights ¼ on each of a, a⁻¹, b, b⁻¹).
N = 10⁷ walkers (starting here, not 10⁶, per the discrimination
analysis above). t up to 600.

**Sampling.** Fine log-grid concentrated in [50, 300]:
t ∈ {20, 30, 50, 70, 100, 140, 180, 220, 260, 300, 400, 500, 600}.
Goal: enough points in [50, 300] to see curvature in the log(L₁)
vs. t residuals.

**Analysis.**

- Fit both log(L₁) = a − λt and log(L₁) = b − c√t on the
  pre-floor portion (L₁ > 10⁻³).
- Compare R² and residual structure. Stretched exp has systematic
  curvature in log-vs-t residuals (slope-of-slope changes by ~2
  across [20, 100]); exp does not.
- Plot log(L₁) vs. both t and √t. Whichever is linear with
  structureless residuals wins.

**Decision.**

- One model has clearly better R² and structureless residuals ⇒
  phase 1 is conclusive. Stop.
- Both fits degrade together near the floor ⇒ increase walker
  count further (phase 2).
- Residuals show a kink — exp early, stretched late ⇒ two-regime
  phenomenon; note it and treat both scales in the theorem.

---

## Phase 2 — confirmation (conditional on phase 1)

**Only if phase 1 is inconclusive.** N = 10⁸ walkers, same time
grid, extending to t ≈ 1000. Floor drops to ≈ 3×10⁻⁴, pushing the
discrimination window out further.

---

## Phase 3 — biased walk (parallel, feeds gap 4)

**Setup.** Weights (0.2, 0.2, 0.4, 0.2) — net multiplicative drift
+0.20/step, matching `bs12_biased.py`.

**Revised question.** The reported "L₁ = 0.091 at walkers of magnitude
10^1200" (~20k steps) is probably **not** a floor. For positive
multiplicative drift, walkers escape to E → +∞. Once |E| > 20 the
b-step becomes identity on the mantissa (per our representation),
leaving only a/a⁻¹ to act — irrational rotation by ±log₁₀ 2. Weyl
equidistribution is ergodic but at *algebraic* rate (~1/t), not
exponential. So plausibly the decay is two-regime: exponential while
walkers visit the active zone, then algebraic (power-law) once they
escape. The 0.091 value may just be the transition point.

**Plan.** Log-spaced sampling to at least t = 2×10⁵ steps. N = 10⁶
walkers is sufficient here since we're looking for power-law shape,
not resolving below 10⁻³. Plot on **both** log-linear and log-log
axes:

- Power-law decay ⇒ straight line on log-log.
- True floor ⇒ horizontal asymptote.
- Two-regime decay ⇒ log-linear early, log-log late, with a
  crossover near the escape time.

**Gap 4 implication.** If we see algebraic decay, biased walks *do*
converge to Benford — just via a mechanism that transitions from
exponential (active-zone visits) to algebraic (post-escape irrational
rotation). This is a more interesting claim than a floor, and
changes what the Theorem 1 corollary says: the theorem covers all
nondegenerate μ, but the rate is two-scale for biased μ, with the
second scale set by Weyl equidistribution.

**Snap-to-origin asymmetry.** The three-case b-step is physically
correct but creates an asymmetry: walkers at E ≪ 0 get recycled to
(0, 0), walkers at E ≫ 0 are frozen. For the symmetric walk this is
irrelevant (exponent visits both directions equally). For biased
walks, the drift direction determines which regime walkers escape
into — positive drift into frozen, negative drift into recycled. Our
weights give positive drift, so we land in the lost-active-contact
case where the power-law tail appears. A biased walk with *negative*
multiplicative drift would keep recycling walkers through the origin
and likely preserve exponential convergence. Worth a sentence in
gap 4's discussion; motivates an optional **phase 3b** with reversed
weights (0.2, 0.2, 0.2, 0.4) if time permits.

---

## Deliverables

- `sim/data/gap3_sym.csv` — columns (t, L₁) for the symmetric run.
- `sim/data/gap3_biased.csv` — (t, L₁) for the biased run.
- `sim/fig/gap3_diagnostic.png` — two-panel plot (log vs. t, log vs.
  √t), symmetric walk.
- `sim/fig/gap3_biased.png` — L₁ vs. t for the biased walk,
  log-linear, extended horizon.
- A one-paragraph summary written into FIRST-PROOF gap 3 "Status"
  line: which shape wins, at what t does the wrong-shape fit break,
  and what gap 2's route is now.

---

## Outcome → commitment table

**Phase 1 (symmetric walk):**

| Phase 1 result | Gap 2 route | Theorem 1 rate (symmetric) |
|---|---|---|
| Clean exp, residuals structureless | Direct Fourier decay on T | exp(−λt) |
| Clean √t, exp residuals show curvature | Rosenthal coupling (§2 Route 1) | exp(−c√t) |
| Kink (exp early, √t late) | Both routes, two regimes | Two-scale statement |

**Phase 3 (biased walk):**

| Phase 3 result | Gap 4 scope decision |
|---|---|
| Clean power-law on log-log | Theorem 1 covers all nondegenerate μ, with rate two-scale for biased (exp, then algebraic) |
| True floor at L₁ > 0 | Narrow Theorem 1 to symmetric μ; biased as quantitative corollary with L₁ ≤ ε_bias |
| Continued exp decay | Theorem 1 covers all nondegenerate μ with uniform rate; snap-to-origin handles escape |

---

## Open design choice: initial conditions

**Default.** All walkers start at (m = 0, E = 0). Cleanest rate
extraction — a single decay curve from a known state.

**Alternative.** Randomize initial m uniformly on [0, 1), or
sample from a smooth initial distribution on T × ℤ. Tests whether
the rate is initial-condition-dependent.

**Recommendation.** Start-at-origin for phase 1. If phase 1 gives a
clean answer, add a randomized-start run as a robustness check
before committing the Theorem 1 scope.

---

## Risks and guards

- **Numerical underflow for large |E|.** Mantissa perturbations
  under b-step when E > 15 are below float64 precision. Guard: treat
  |E| > 20 as the identity on m.
- **Correlated walkers.** Randomize each walker's generator sequence
  from an independent RNG stream. Sage's `RandomState` with distinct
  seeds per walker group, or a single well-behaved PRNG advanced by
  known offsets.
- **Fit bias near the floor.** Points within ~2× the noise floor
  are dominated by sampling error and bias the linear fit. Exclude
  them explicitly in the regression, not just by eye.
- **Short-horizon lock-in.** Don't repeat the [20, 100] fit's
  mistake. Fit the full pre-floor range, and look at residuals, not
  just R².
