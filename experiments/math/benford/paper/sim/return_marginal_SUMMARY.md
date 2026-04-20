# Return-marginal — pooled post-burn sample is far from Lebesgue

Mess #2 asks whether π_T ν_R = Leb_T, where ν_R is the invariant
probability of the induced return operator T_R on R = {|E| ≤ E₀}.
The identification step is load-bearing for the paper's
Benford-conclusion claim.

This sim measured the pooled distribution of walker states at
return events for BS(1,2), N = 10⁶ walkers, n_max = 10⁴, E₀ = 10,
K_burn = 5, paper's default kernel. Result: **the pooled
post-burn return-sample m-marginal is concentrated on the arc
[1 − log₁₀ 2, 1) ≈ [0.699, 1.000) and is flat on that arc**.

Call this pooled marginal σ̃. σ̃ is a proxy for π_T ν_R but not
the same object: it pools all post-burn returns across walkers
and return indices without checking that they are drawn from
the invariant distribution. See Caveats below for what would
tighten the identification.

Run: `run_return_marginal.py`.
Analysis: `analyze_return_marginal.py`.
Data: `return_marginal_results/return_marginal.npz`.
Date: 2026-04-19.

## Measured distribution

22.0 million post-burn return samples from 876,022 contributing
walkers (87.6% of 10⁶).

**E at return.** All 22.0M returns had **E = +10**. Zero returns
at E = -10, -9, …, 0, …, +9. Every return entered R from above.
This matches the Laplace-diagnostic finding that BS(1,2) walkers
drift strongly positive in E.

**m at return.** Support on the arc [0.699, 1.000), density
≈ 3.33 (= 1 / log₁₀ 2). Coarse-binned to 20 buckets of width
0.05:

| bucket        | empirical density |
|:--------------|:-----------------:|
| [0.00, 0.65)  | 0.0000            |
| [0.65, 0.70)  | 0.069             |
| [0.70, 0.75)  | 3.357             |
| [0.75, 0.80)  | 3.339             |
| [0.80, 0.85)  | 3.333             |
| [0.85, 0.90)  | 3.319             |
| [0.90, 0.95)  | 3.303             |
| [0.95, 1.00)  | 3.281             |

L₁(m_density, 1) = 1.398, vs multinomial noise floor 5.4 × 10⁻³;
ratio **260×**. Structural, not sampling.

**Fourier coefficients |σ̂(r)| (noise ~ 2 × 10⁻⁴):**

| r   | \|σ̂(r)\|    | ratio / noise |
|:---:|:------------:|:-------------:|
| 1   | 0.858        | 4021          |
| 2   | 0.502        | 2353          |
| 3   | 0.106        | 497           |
| 5   | 0.211        | 991           |
| 10  | 0.0025       | 11.7          |
| 20  | 0.0036       | 16.9          |
| 50  | 0.0047       | 22.0          |

Low-r modes are order unity, not zero. The distribution is
nowhere near Leb_T.

## Proposed mechanism (not directly measured)

The following is a back-of-envelope derivation of the observed
arc support and density level. It is _consistent_ with the
measurement but is not independently tested by this sim; the
runner does not record pre-return states at E = 11.

For R = {|E| ≤ 10} at E₀ = 10, a walker at E = 11 can
return to E = 10 primarily via a⁻¹ with borrow. That step
requires m_pre < log₁₀ 2 ≈ 0.301 and maps m_pre → m_pre +
(1 − log₁₀ 2) ∈ [0.699, 1).

- a-step from E = 11 requires m ≥ 1 − log₁₀ 2 for a carry, which
  sends E → 12 (away from R).
- a-step without carry keeps E = 11.
- b, b⁻¹ at |x| ≈ 10¹¹ change log|x| by O(10⁻¹¹). In particular,
  b⁻¹ acting on an x with m near 0 and sign = +1 gives
  log|x − 1| ≈ log|x| − 10⁻¹¹; E normally stays at 11 but for m
  sufficiently small the floor can drop to 10. At E₀ = 10 this
  strip has width O(10⁻¹¹) and is numerically irrelevant; at
  smaller E₀ the strip widens and this channel matters.
- a⁻¹ without borrow keeps E = 11.
- **At E₀ = 10, a⁻¹ with m < log₁₀ 2 is essentially the only
  channel returning the walker to R, giving m_new ∈ [0.699, 1).**

If m_pre is approximately uniform on [0, log₁₀ 2) at the
return step (which would follow from a-step rotation
equidistribution during the excursion above R, but which is _not_
directly measured here), m_new is approximately uniform on
[0.699, 1). Density there is 1/log₁₀ 2 ≈ 3.322, matching the
measured 3.33.

**What would verify this:** instrument the sim to record m at
the step immediately before each return event (the m_pre
distribution) and compare to uniform on [0, log₁₀ 2). Not done
here.

## What this means for Mess #2

Mess #2's five-issue list (`MESSES.md` §Mess #2, mechanical
obstructions) warned that the rotation-invariance sketch was
aspirational. This sim sharpens the challenge: for R = {|E| ≤ 10}
and the paper's canonical walker, the pooled post-burn
return-sample T-marginal σ̃ is empirically far from Leb_T. That
is the cleanest statement the data supports.

The proposed mechanism (previous section) — walker drifts upward,
exits via E₀ + 1, returns via a⁻¹ with borrow, landing with
m ∈ [1 − log₁₀ 2, 1) — is consistent with both the arc support
and the 1/log₁₀ 2 density. If that mechanism is the full story
and ν_R's T-marginal is exactly that uniform arc, then Route 1's
identification step π_T ν_R = Leb_T would be false for this R.

We have not shown the stronger claim. In particular:

- **Not shown: σ̃ = ν_R.** The sim discards first 5 returns per
  walker but does not verify stationarity; marginals by return
  index are not computed. What we have is σ̃, the pooled
  post-burn sample, not a certified estimate of ν_R itself.
- **Not shown: the mechanism extends to all E₀.** At E₀ = 10
  the b⁻¹ channel has width O(10⁻¹¹) and is irrelevant. At
  smaller E₀ (say E₀ = 3) the b⁻¹ contribution is non-negligible
  and the return-mode support picks up mass outside [1 − log₁₀ 2,
  1). How that changes σ̃ at small E₀ is not tested here.
- **Not shown: ν_R is well-defined.** 12.4% of walkers did not
  contribute a post-burn sample in n_max = 10⁴. The walker has
  positive drift in E, and a positive fraction may never return.
  If so, T_R is not a probability kernel and ν_R is a measure on
  R that may be substochastic or require a different framework.
  This is Mess #3's concern in a different form.

## What this does _not_ directly refute

- **T1b phenomenology.** The paper's φ(ν, n) on the M1 walker is
  the _unconditional_ m-marginal at time n, not the return-time
  marginal. Empirically φ → 0 (the mantissa marginal does
  converge to uniform). So the walker's overall m-marginal
  equidistributes, even though the return-time marginal doesn't.
- **The truth of Theorem 1b.** That is an asymptotic statement
  about the walker's m-marginal, empirically supported by
  multiple sims in `T1B-EVIDENCE-MAP.md`. This sim doesn't touch
  that.
- **The existence of _some_ operator-theoretic route** to the
  theorem. This refutes a specific identification step in Route
  1' as currently sketched, not every possible route.

## What this puts pressure on

- **Route 1' as currently sketched in FIRST-PROOF §2.** The
  identification step "π_T ν_R = Leb_T" is under significant
  empirical pressure at R = {|E| ≤ 10}: σ̃ is concentrated on
  an arc of length log₁₀ 2, far from Leb_T. A rotation-
  equidistribution argument inside R would have to overcome the
  concentration of entry states onto that arc, which appears
  difficult.
- **The rhetorical frame that Route 1' needs only to "identify
  the invariant T-marginal."** Even before identifying it with
  Leb_T, this sim suggests the pooled return marginal has a
  specific structure (arc support, uniform density on the arc)
  that the current sketch doesn't anticipate. The gap between
  the return-time marginal and the unconditional time-n marginal
  is now plausibly the load-bearing question, not just the
  identification.

## For FIRST-PROOF / PNAS-PLAN

The Mess #2 footnote in FIRST-PROOF §2 should be expanded with
this empirical pressure noted. Specifically:

- The current FIRST-PROOF Route 1' architecture uses T_R's ν_R
  as the intermediate object and needs π_T ν_R = Leb_T. Under
  R = {|E| ≤ 10}, the pooled return-sample marginal is
  empirically far from Leb_T and sits on a specific arc. If
  that pooled marginal is a good estimate of π_T ν_R (plausible
  but not independently verified here), the identification step
  fails at the natural R.
- Options for adapting: (a) use a different R with a different
  return mechanism, (b) decouple the return-time marginal from
  the final theorem and argue for the unconditional marginal
  directly, or (c) find a bridge — an operator that sees both
  the return-time distribution and the time-averaged
  distribution — that can close the gap.
- Option (b) — walker-level argument for π_T ν_n → Leb_T not
  mediated by T_R — looks most promising given that the walker's
  full-time mantissa does equidistribute (from M1's φ → 0) while
  the return-time marginal doesn't.

## Caveats

Three gaps between "pooled post-burn return marginal σ̃ is far
from Leb_T" (established) and "π_T ν_R is not Leb_T" (stronger,
not established here):

- **Stationarity check not performed.** The sim pools all
  post-burn returns across return indices. It does not compute
  the return-index-conditioned marginals σ̃_k for k = 6, 7, 8,
  … and check that they stabilize. If σ̃_k still has index-
  dependence, σ̃ is not yet a certified estimate of ν_R.
  Tightening this would instrument the runner to save per-return
  index sums and compare marginals across indices.
- **Burn-in sensitivity not measured.** K_burn = 5 is ad hoc.
  A tighter claim would repeat at K_burn ∈ {5, 20, 50} and
  verify σ̃ is the same.
- **Mechanism's all-E₀ claim not verified.** The summary's
  derivation assumed only the a⁻¹ channel returns walkers from
  E₀ + 1 to E₀. At E₀ = 10 the b⁻¹ channel has width
  O(10⁻¹¹) and is numerically irrelevant. At smaller E₀ the
  b⁻¹ channel widens and the argument no longer applies
  verbatim. We do not here show that σ̃'s arc-concentration
  is robust under R-choice; only that it holds for E₀ = 10.

Other caveats:

- **R definition.** The sim uses R = {|E| ≤ 10}. If the paper
  intended a different R (e.g., a function-space cutoff on
  densities rather than a set of states), the interpretation
  could shift.
- **Transience.** 12.4% of walkers never contributed a post-burn
  sample in 10⁴ steps — they drifted too far upward to return 6
  times. The existence of walkers that never return is itself
  problematic for treating T_R as a probability kernel; this is
  Mess #3's concern.
- **Sign coordinate.** The sim runs with sign = +1 initially.
  From the M1 IC (x = √2 > 0), sign flips are rare; the
  concentration on the +10 boundary is consistent with this.

## What's saved

- `return_marginal_results/return_marginal.npz` — m-histogram,
  E-histogram, Fourier coefficients, sample count.

## Not done

- **Stationarity-by-index check.** Compute σ̃_k per return index
  k post-burn. Verify k → ν_R. Required to upgrade from σ̃ to
  π_T ν_R.
- **Burn-in sweep.** K_burn ∈ {5, 20, 50} with stability check.
- **Pre-return-state instrumentation.** Save m_pre at the step
  before each return. Verify the proposed equidistribution on
  [0, log₁₀ 2) (the mechanism's key premise).
- **E₀ sweep.** E₀ ∈ {3, 5, 10, 15} to test whether the arc
  support is stable under R-shape or whether the b⁻¹ channel at
  small E₀ reshapes σ̃.
- **Different R shapes.** Test R = T × {0} (single slice) or
  R = {m ∈ [a, b]} × ℤ (mantissa-bounded). Each would have a
  different return operator and potentially different ν_R.
- **Theoretical calculation of ν_R.** The proposed mechanism is
  clean enough that ν_R should be derivable in closed form at
  E₀ = 10 where the b⁻¹ channel is negligible. An exercise, not
  a sim.
