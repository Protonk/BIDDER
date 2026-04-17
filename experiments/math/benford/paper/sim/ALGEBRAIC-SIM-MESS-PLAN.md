# ALGEBRAIC-SIM-MESS-PLAN

Simulation plan to reject the algebraic-rate hypothesis
(operationally: L₁(n) ~ C/√n) in favor of the
stretched-exponential (L₁(n) ~ C exp(−c√n), c ≈ 0.55)
observed in gap 3 phase 1.

Motivated by `MESSES.md` §1: the per-return spectral-gap
framework predicts algebraic decay because the relevant
Laplace-transform observable E[q^{N_n}] for null-recurrent
return counts is O(1/√n), not exp(−c√n). In this plan,
H_A is the operational proxy for that prediction at the level
of the measured mantissa statistic L₁(n). If the simulation
rejects algebraic, the framework is wrong about the rate
(not just unproven). If the simulation confirms algebraic,
the stretched-exp fit was a transient and the framework is
vindicated.

**Companions.** `TUKEYS-LADDER.md` analyses the same simulation
data with a nonparametric shape-first approach. `BENTHIC-
MINKOWSKI-SIM.md` analyses the walk at the mechanism level via
Fourier-mode decomposition and a mode-coupling matrix — it asks
*why* the shape is what it is, not what the shape is or what
the parameters are. Shared run specs (M0–M4) are authoritative
in *this* document.

See [`sim/README.md`](README.md) for the cross-document framing
(scientific discrimination + proof triage, the three-plan
triangle, structured disagreement as deliverable). This plan's
authority map section at the end specifies the operational
adjudication rules for disagreements on *this plan's* data.

**Notation.** The target statistic throughout is the empirical
L₁ distance of the mantissa histogram to uniform on T = [0, 1):

    L₁(n) := Σⱼ |freqⱼ(n)/N − 1/B|

over B bins, N walkers, at step n. The earlier sibling-style
notation φ(n) is dropped in favor of L₁(n) for consistency with
the run specs and analysis sections.

---

## The two models, stated precisely

**H_S (stretched-exponential):**

    log L₁(n) = a − c√n,    c ≈ 0.55

Predictions: slope d(log L₁)/dn = −c/(2√n). Signal vanishes
below any fixed noise floor in finite time. At n = 300 with
c = 0.55, L₁ ≈ exp(−9.5) ≈ 7 × 10⁻⁵.

**H_A (algebraic):**

    log L₁(n) = a − ½ log n

Predictions: slope d(log L₁)/dn = −1/(2n). Signal persists as
a power-law tail forever. At n = 300, L₁ ≈ C/√300 ≈ C/17.
At n = 5000, L₁ ≈ C/√5000 ≈ C/71.

The models agree qualitatively at small n (both are concave
on a log-linear plot). They diverge quantitatively by n ~ 50
and catastrophically by n ~ 200.

---

## Discriminants

Three independent tests, each sufficient alone. Running all
three makes the rejection watertight.

### D1. Slope ratio

Measure the local slope of log(L₁) vs n at two well-separated
points n₁, n₂. Compute the ratio slope(n₂)/slope(n₁).

    H_S predicts:  √(n₁/n₂)
    H_A predicts:  n₁/n₂

Example: n₁ = 25, n₂ = 100.

    H_S: √(25/100) = 0.50
    H_A: 25/100    = 0.25

These differ by a factor of 2. Gap 3 phase 1 already has the
data for this at (25, 130); the measured ratio was ~0.42,
matching H_S (predicted 0.44) and excluding H_A (predicted
0.19). But the existing data has limited time resolution and
was not designed for this test. A purpose-built run with dense
sampling in n ∈ [20, 200] and high walker count sharpens it.

### D2. Linearization

Plot log L₁(n) against √n. Under H_S, this is a straight line
with slope −c. Under H_A, it is concave (log(C/√n) =
log C − ½ log n, which is concave in √n because
log n = log(√n)² = 2 log(√n), so log L₁ = −2 log(√n) + const,
which bends downward).

Separately, plot log L₁(n) against log n. Under H_A, this is
a straight line with slope −½. Under H_S, it is convex
(−c√n = −c · n^{1/2}, so on a log-log plot it curves
downward faster than any power law).

One of the two plots will be straight. The other will curve.
This is a visual diagnostic that a referee can check by eye.

### D3. Signal death

The decisive test. Under H_S, L₁ drops below any fixed
threshold in finite time that grows as (log(1/threshold))².
Under H_A, L₁ stays above any threshold proportional to
1/√n — it never dies, just decays.

For the actual decision rule, do **not** use a bare 1/√N
heuristic as the threshold. The plotted statistic is

    L₁ = Σ |freq_j/N − 1/B|

with B = 1000 bins, so the null floor depends on N, B, and
the absolute-value aggregation. The threshold must therefore
be calibrated empirically for this exact statistic. Let
θ_N(B) be the 99.9% quantile of the null L₁ distribution under
multinomial counts with equal bin probabilities 1/B. This is
the detection floor used below. The 1/√N scaling remains a
sanity check only.

Noise floor table (M0 empirical at N = 10⁸, B = 1000; other
rows scaled as 1/√N from the measured anchor):

| N      | θ_N (null floor) | H_S: signal dies at n ≈ | H_A: signal at n = 5000 |
|--------|-----------------|-------------------------|-------------------------|
| 10⁷    | 8.6 × 10⁻³      | ~130                    | C/71 ≈ 0.005–0.01       |
| 10⁸    | 2.7 × 10⁻³      | ~185                    | C/71 ≈ 0.005–0.01       |
| 10⁹    | 8.6 × 10⁻⁴      | ~245                    | C/71 ≈ 0.005–0.01       |

M0 measurement (N = 10⁸, 2026-04-17): mean(L₁) = 2.521×10⁻³,
θ_N = 2.717×10⁻³, matches analytic √(2B/(πN)) = 2.523×10⁻³
within 0.1%. Sanity check passes.

Under H_A, the signal at n = 5000 is 2–4× above the noise
floor at N = 10⁸ — detectable but not overwhelming; worth
N = 10⁹ for a confident reading if M4 at N = 10⁸ is marginal.
Under H_S, the signal is below θ_N by n ≈ 185 at N = 10⁸.

D3's onset test is handled by M2 (n ∈ [0, 300], dense
sampling). Its tail test — whether L₁ stays at floor or
persists above it at large n — is handled by M4 (n up to
20000; see amendment). If L₁ hits θ_N by n ≈ 300 (M2) and
stays at/below it throughout M4's post-transient window,
pure H_A is rejected. If L₁ is measurably and persistently
above θ_N at large n in M4, pure H_S is rejected. The
mixture case is teased apart in A5.

---

## Run specification

### Run M0: empirical null-floor calibration

**Purpose:** calibrate the exact null distribution of the
plotted L₁ statistic for D3.

    N = 10⁸ walkers
    B = 1000 bins
    Replicates: 5000 null draws
    Null model: multinomial(N; 1/B, …, 1/B)
    Output: mean(L₁), sd(L₁), q_0.99(L₁), q_0.999(L₁)

Define

    θ_N := q_0.999(L₁ under the null).

Use θ_N, not 1/√N, as the signal-death threshold in A3 and in
the decision rule. Keep the 1/√N scale only as a rough
sanity check for order of magnitude.

**Sanity check.** Expected mean(L₁) under the multinomial null
is approximately √(2B/(πN)) ≈ √(2·1000/(π·10⁸)) ≈ 2.5 × 10⁻³.
θ_N should be ≈ 1.3–1.5× mean(L₁). If M0's empirical θ_N is
more than 50% off this expectation (either direction), the
null-draw implementation has a bug or the statistic definition
is subtly different from the multinomial model. **Freeze and
debug** before downstream use. Record actual θ_N for citation
in downstream run specs.

### Run S0: shared-prerequisite — Mittag-Leffler index test

**Purpose:** test the assumption that the per-walker return
count N_n follows Mittag-Leffler(1/2) statistics. Both the
MESSES-mixture prediction (α = 1/2 in the algebraic tail) and
BENTHIC's balanced-regime √n rate derive from this assumption.
If it fails, both frameworks' quantitative predictions are
wrong in the exponent.

**Data source.** Per-walker N_n records from Run M1 (which now
produces these as part of the consolidated M1 + B1 + B2 run).
S0 is a post-processing analysis on M1 output; no new sim
required.

**Analysis.** At each of n ∈ {100, 200, 500}:

1. Compute empirical distribution of N_n / √n across the 10⁸
   walkers.
2. Estimate tail exponent β from P(N_n ≥ k) ~ k^{−β} for k in
   the body of the distribution (say, k ∈ [√n/4, 2√n]). Use
   rank-based regression on log-log axes.
3. Equivalently, compute E[exp(−λ N_n / √n)] for λ ∈
   {0.1, 0.5, 1, 2, 5} and compare to the ML(1/2) Laplace
   transform's explicit form (Mittag-Leffler function
   E_{1/2}(−λ) up to normalization).

**Bootstrap β̂.** Resample walkers, refit β, produce 95% CI.

**Decision rule.**

- β̂ ∈ [0.45, 0.55] (within 10% of the theoretical 1/2) with
  tight CI ⇒ ML assumption holds empirically; ALGEBRAIC's
  α = 1/2 target and BENTHIC's √n-scaling prediction are
  well-grounded. **Proceed with the default schedule.**
- β̂ outside [0.45, 0.55] with tight CI ⇒ the walk's return
  count is not in the ML(1/2) basin. **Halt.** Reformulate:
  ALGEBRAIC's mixture becomes A·exp(−c·n^{1−β̂}) +
  B·n^{−β̂}; BENTHIC's balanced-regime rate becomes
  exp(−c·n^{1−β̂}). Downstream decision rules must be
  re-derived at the measured exponent.
- β̂ with loose CI (≥ 0.05 width) ⇒ insufficient data.
  Extend M1 or rerun at higher N until the CI tightens.

**Why this belongs in the prerequisites.** MESSES's algebraic
prediction and BENTHIC's balanced-regime derivation both have
√n baked in. If the underlying stable-law index isn't 1/2, the
√n is wrong in the exponent, and fitting "α ∈ [0.4, 0.6]" in
A5 is looking for a specific wrong number. S0 runs first;
everything downstream conditions on its output.

### Run M1: high-resolution slope run

**Purpose:** D1 and D2. Dense time sampling in the
discriminating window.

    N = 10⁸ walkers
    Symmetric measure: P(a) = P(a⁻¹) = P(b) = P(b⁻¹) = 1/4
    Initial condition: (m, E) = (0, 0) for all walkers
    Time range: n = 0 to 600
    Sampling: every step from n = 1 to 200,
              every 5 steps from n = 200 to 600
    Output: L₁(n) = Σ |freq_j/N − 1/B| where B = 1000
            bins on T = [0, 1)

Dense sampling in [1, 200] is the point. The slope ratio and
linearization tests need local derivatives, and numerical
differentiation on sparse data is noisy. Dense sampling makes
finite differences clean.

**M1 and BENTHIC's B1 can be the same run.** B1 specifies the
same N, same time range, same sampling pattern. Extend M1's
output to additionally record Fourier coefficients ĥ(r, n) for
r = 1, …, 5 at each sample time, plus per-walker return count
N_n^{(i)} and conditional Fourier coefficients at checkpoint
times (see BENTHIC B1 items 1–5). Marginal compute cost is
O(N) per mode per step, ~10% on top of M1's baseline. One
run, two plans' data.

**Bin count.** B = 1000 is finer than gap 3 phase 1 (which
used 9 or 10 bins for the digit-level L₁). The digit-level
binning is too coarse — it aliases the mantissa distribution
and could mask structure. 1000 bins on [0, 1) with N = 10⁸
walkers gives 10⁵ expected walkers per bin. The exact null
floor for this statistic is calibrated by M0; the 1/√N scale
is only a rough consistency check.

**Mandatory check.** The M1 stretched-fit log L₁ = a − c√n
on [20, 120] must recover:

- c within 0.05 of phase 1's 0.548 (i.e., c ∈ [0.50, 0.60]).
- R² ≥ 0.995 (phase 1 measured 0.9985).

The ±0.05 band is a rule-of-thumb envelope, not a formal 2σ
confidence region: phase 1's fit did not report a standard
error, and the ±0.05 here is chosen to be (a) tight enough to
catch a ~10% drift in the measured slope, which would signal
a real implementation difference, and (b) loose enough to
accommodate Monte Carlo variance between phase 1's N = 10⁷
and M1's N = 10⁸. If M1 ships with a proper bootstrap SE on
c, tighten this envelope to max(0.03, 2·SE) at that time.

If either criterion fails, the M1 implementation differs from
phase 1 in some way — different bin count, different L₁
convention, RNG seed pathology, or an actual bug. **Freeze and
debug** before any downstream analysis, including D1/D2/D3.
The rest of the plan assumes phase 1's stretched shape is
reproduced in the discriminating window; without that,
decision-rule outputs are meaningless.

### Run M2: signal-death onset run

**Purpose:** D3, onset portion. Determine where L₁ hits the
empirically calibrated null floor θ_N during the initial
stretched-exp decay. The extended-range [300, 20000] portion
is handled by M4 (see amendment below), which supersedes M2's
long-tail role.

    N = 10⁸ walkers
    Same measure, same initial condition
    Time range: n = 0 to 300
    Sampling: every step
    Output: same L₁ with B = 1000

Keep M2 focused on [0, 300] — dense sampling through the
stretched-exp death window. M4 picks up at n ≥ 300 and
extends to 20000 for the mixture/algebraic-tail question. This
consolidation saves ~20 hours of compute compared to running
M2 all the way to n = 5000 and having M4 repeat coverage
there.

**Precision.** Float64 (53-bit significand) gives ~15 decimal
digits; accumulated b-step error through n = 300 is negligible
(~3 × 10⁻¹⁴). Long-horizon precision concerns move to M4.

### Run M3: initial-condition robustness

**Purpose:** check that the rate classification is not an
artifact of the (0, 0) initial condition. This is mandatory:
the plan is testing an asymptotic rate law, not a single-IC
transient.

    N = 10⁸ walkers
    Same measure
    Initial conditions:
      (a) m uniform on T, E = 0  (Leb_T ⊗ δ₀ — the IC that
          killed GAP2-LEMMA's Claim (*))
      (b) m = 0, E uniform on {−5, …, 5}
      (c) m uniform on T, E uniform on {−5, …, 5}
    Time range: n = 0 to 600
    Sampling: same as M1

Under H_S, all initial conditions should show the same
asymptotic rate c ≈ 0.55 after a transient. Under H_A, the
prefactor C may change but the exponent −½ should be
universal. IC (a) is the interesting one — it starts near
equilibrium on T, so the initial transient is short and
the asymptotic regime is reached faster.

**"Same asymptotic classification" — operational definition.**
Run the M1 A1+A2 analysis separately on each M3 IC's data on
the window [20, 200]. An M3 IC *agrees* with M1's decision if:

- The winning linearization (√n vs. log n, per A2) is the
  same as M1's, i.e., max R² is achieved by the same model.
- The fitted exponent is within 2× the M1 standard error of
  M1's fitted exponent (c for H_S; α for H_A).
- The residual-autocorrelation sign (systematic vs. white,
  per A4) is the same.

An M3 IC *disagrees* if any of these three fails. Decision-rule
criterion 4 (either rejection direction) requires ≥ 1 of the
three M3 ICs to agree in this operational sense.

---

## Default execution schedule

This is the authoritative sequencing for all three plans (this
one, `TUKEYS-LADDER.md`, and `BENTHIC-MINKOWSKI-SIM.md`). It
holds unless a specific failure mode (e.g., phase-1 cross-check
fails) interrupts the flow.

**Step 0 (prerequisites, parallel):**
- **M0** — multinomial null calibration. ~1 min.
- **S0** — Mittag-Leffler index test (see below). Cheap; runs
  once M1 has produced the per-walker N_n record.

**Step 1: consolidated shape-and-mechanism run.**
- **M1 + B1 + B2 consolidated.** Single run producing L₁ for
  ALGEBRAIC/TUKEYS analyses and Fourier coefficients ĥ(r, n)
  plus per-walker N_n for BENTHIC. ~30 min at N = 10⁸.
- Phase-1 cross-check gates the rest of the schedule: must
  recover c ∈ [0.50, 0.60] and R² ≥ 0.995 on [20, 120], or
  freeze and debug.

**Step 2: IC robustness.**
- **M3** — three nontrivial ICs on early window. ~1.5 hrs.
  Mandatory.

**Step 3: mechanism detail.**
- **B3** — excursion-resolved mode coupling. ~4 hrs. This is
  separately resourced because of per-walker excursion logging,
  but it is **default always-on**. Skip only if TUKEYS and
  ALGEBRAIC converge with overwhelming clarity (H_S with R² >
  0.999 and B̂ CI excludes 0 by > 5σ) — and even then, running
  B3 is worth its 4 hours for reviewer defense. Treat the
  "always-on" default as binding.

**Step 4: long-horizon tail.**
- **M2 + M4** — signal-death onset and tail detection. ~16 hrs.
  Overnight.

**Step 5 (optional):**
- **M4b** — IC cross-check on algebraic tail at IC (a), n ≤ 5000.
  ~4 hrs. Run if the paper's rate claim is sensitive to IC-
  independence of B, α.

Total baseline: ~22 hrs with all mandatory steps + B3 always-on.
~26 hrs with M4b.

**Conditional skipping is discouraged.** The three plans are
designed to cross-validate each other; running all three is
cheap relative to the risk of a missed red flag.

---

## Analysis

### A1. Local slope

From M1 data, compute the local slope

    s(n) = (log L₁(n+1) − log L₁(n−1)) / 2

at each sampled n. (Use wider windows for smoothing if
single-step differences are noisy; a 5-point Savitzky-Golay
derivative is fine.)

Plot s(n) against:

    (a) 1/√n   — under H_S, this should be linear through
                  the origin with slope −c/2 ≈ −0.275
    (b) 1/n    — under H_A, this should be linear through
                  the origin with slope −1/2

One of these will be straight. The other will curve. Report
R² for both linear fits on the window [20, 200].

### A2. Linearization plots

From M1 data, two plots:

    (a) log L₁(n) vs √n — straight under H_S
    (b) log L₁(n) vs log n — straight under H_A

Fit lines to both on [20, 200]. Report slope, R², and
residual structure (systematic curvature vs. noise).

### A3. Signal death

From M2 (n ∈ [0, 300]) and M4 (n ∈ [300, 20000]) combined,
identify the time n* at which L₁ first drops below θ_N and
stays below for all subsequent measurements, where θ_N is the
empirically calibrated null threshold from M0.

    H_S predicts: n* ≈ 200–280
    H_A predicts: n* does not exist
                  (L₁ persists at 1/√n level past n = 5000)

If n* exists and is in the predicted H_S range, pure H_A is
rejected. If L₁ is measurably and persistently above θ_N at
large n in M4 (see decision rule for persistence criterion),
H_S is rejected — but the mixture case is only teased apart
in A5.

Plot L₁(n) on [300, 20000] with θ_N marked.
Under H_A, this should show a clean 1/√n decay. Under H_S,
it should be flat at the null floor throughout.

### A4. Fit comparison

From M1 data on [20, 200], fit both models:

    H_S: log L₁ = a_S − c√n       (2 parameters: a_S, c)
    H_A: log L₁ = a_A − α log n   (2 parameters: a_A, α)

Report for each: fitted parameters, R², residual σ,
and residual autocorrelation at lag 1 (a measure of
systematic misfit vs. white noise). Under the true model,
residuals should be white; under the false model, they
should show systematic curvature.

If α ≈ 0.5 under H_A, that is consistent with the algebraic
prediction. If α deviates significantly from 0.5 (e.g.,
α ≈ 0.8 or α ≈ 0.3), neither model is right as stated.

### A4b. Segmented-fit cross-check

Global fits on [20, 200] can hide shape changes. As a
sanity check, refit H_S and H_A in each of three disjoint
sub-windows and tabulate the fitted exponents:

| window | c_i (H_S) | R² | α_i (H_A) | R² |
|---|---|---|---|---|
| [20, 60]  |  |  |  |  |
| [60, 120] |  |  |  |  |
| [120, 200]|  |  |  |  |

**Flag if** c_i varies by more than 20% across windows, or α_i
varies by more than 20% across windows, or the sign of (R²(H_S)
− R²(H_A)) flips between windows.

A flag here means the global fit in A4 is averaging across a
shape change, and the "winning" model in A4 is the least-bad
approximation rather than the right shape. If flagged, trust
TUKEYS-LADDER's segmented analysis (see that plan's
segmented-fits section) over the global A4 conclusion, and
proceed to the three-way decision (post-M4) with the
knowledge that the early-window shape may differ from the
late-window shape.

### A4c. L₁ vs. ‖h‖_{L²} rate cross-check

BENTHIC's regime classification is a statement about ‖h‖_{L²}
(Fourier spectral radius). This plan and TUKEYS analyse L₁.
For BENTHIC's L² conclusions to serve as a coherence check on
L₁ shape claims, the two norms must have the same exponent
rate (they can differ in prefactor — L₁ ≤ √B · ‖h‖_{L²} by
Cauchy-Schwarz — but the exponent rate should transfer in the
single-dominant-mode regime).

From the consolidated M1 + B1 data, compute at every sampled
n both:

- L₁(n) — the primary statistic.
- ‖h‖_{L²}(n) ≈ (Σ_{r=1…5} |ĥ(r, n)|²)^(1/2) from B1's
  Fourier coefficients.

Plot log L₁(n) and log ‖h‖_{L²}(n) on the same axes vs. n.

- **Slopes parallel** (within sampling noise; say absolute
  slope-difference < 20% across [50, 200]) ⇒ rate-family
  transfer holds empirically. BENTHIC's L² conclusions can
  be read as statements about L₁'s exponent rate. The
  authority map's BENTHIC-disagreement flag is meaningful.
- **Slopes diverge** ⇒ h is spreading across modes at
  different rates and the single-dominant-mode picture
  fails. A "BENTHIC disagrees with shape" flag might be
  benign norm-mismatch rather than a mechanism contradiction.
  Report this as a separate diagnostic before interpreting
  any authority-map flag.

Zero marginal cost — ‖h‖_{L²}² is Σ|ĥ(r)|², which BENTHIC
already records.

---

## Amendment: mixture detection (M4 + A5)

### Why this is needed

Runs M1–M3 as specified will almost certainly reject *pure*
H_A (pure algebraic) because the data on [20, 200] is
stretched-dominated. But the MESSES.md prediction is not
pure algebraic — it is a mixture

    L₁(n)  ≈  A · exp(−c√n)  +  B · n^(−1/2),

where the stretched term dominates at small n (what M1 sees)
and the algebraic tail dominates asymptotically. Both terms
are predicted to be nonzero under the per-return Laplace-
transform framework.

Rejecting pure H_A does **not** reject the mixture. The
stretched transient dies by n ≈ 300; whether an algebraic
tail persists above θ_N past that point is a separate
question the M1–M3 runs were not designed to answer.

### Run M4: mixture-detection run

**Purpose:** detect or reject the algebraic tail coefficient
B. Secondary: measure the late-time exponent α if a tail is
present; if α ≠ 1/2, neither pure H_A nor the MESSES-mixture
form fits, and a different mechanism is indicated.

    N = 10⁸ walkers (baseline) or 10⁹ (properly resourced)
    Symmetric measure: P(a) = P(a⁻¹) = P(b) = P(b⁻¹) = 1/4
    Initial condition: (m, E) = (0, 0)
    Time range: n = 0 to 20 000
    Sampling:
      every step from n = 1 to 300
      every 10 steps from n = 300 to 2000
      log-spaced: {500, 700, 1000, 1500, 2000, 3000,
                   5000, 7000, 10000, 14000, 20000}
    Output: L₁(n) with B = 1000 bins, same statistic as M1/M2.

**Design constraints.**

- **Stretched transient must be completely below θ_N by the
  fit window.** At c = 0.55 and n = 20 000, exp(−c√n) ≈
  exp(−78) ≈ 10⁻³⁴ — fully dead. The fit window [max(n*, 2000),
  20000] is pure post-transient, so any persistent signal is
  the algebraic tail.
- **θ_N must sit below the predicted tail amplitude.** With
  N = 10⁸, θ_N ~ 10⁻³ (empirical, from M0 rerun at this N).
  At n = 20 000, B/√n for B = 0.5 is 3.5 × 10⁻³, i.e., ~3.5×
  above floor. For B = 0.1 it is 7 × 10⁻⁴, below floor. So
  N = 10⁸ detects mixture cleanly only if B ≳ 0.15; marginal
  below that. N = 10⁹ brings θ_N down to ~3 × 10⁻⁴ and
  improves the detection threshold by ~3×.
- **Precision check.** n = 20 000 is well within float64's
  accumulated-error envelope (~2 × 10⁻¹² at step 20 000). Fine.

**Memory / throughput.** N = 10⁸ walkers stored as (m: float64,
E: int64, sign: int8) is ~1.7 GB per state — fits in RAM.
N = 10⁹ is ~17 GB — requires streaming or chunked execution.
Runtime scaling from phase 3 (3.5 × 10⁷ ops/sec vectorized):
N = 10⁸ × 20 000 steps ≈ 16 hours; N = 10⁹ × 20 000 steps
≈ 6–7 days on a single machine (cluster recommended).

**Recommended execution order:** run M4 at N = 10⁸ first. If
the result is inconclusive (3-param fit CI for B straddles
zero with sizeable |B̂|), escalate to N = 10⁹.

**IC-independence of the algebraic tail — assumed.** M4 is
single-IC at (m, E) = (0, 0). The algebraic-tail coefficient B
and exponent α are assumed IC-independent on theoretical
grounds: they come from the lower tail of the return-time
distribution for a null-recurrent walk on ℤ, which depends on
the walk's step distribution, not on where the walk started.
The stretched-exp amplitude A and the crossover time n* are
expected to be IC-dependent (M3 tests A-level robustness on the
early regime). If the theoretical IC-independence of B, α
fails for some reason we haven't anticipated, neither M4 nor
M3 would catch it. The optional M4b (below) is the cross-check.

### Run M4b (optional): IC cross-check on the algebraic tail

**Purpose:** empirical confirmation of the assumed IC-
independence of B, α. Cheap cross-check; promote to mandatory
if the paper's rate claim is sensitive to this assumption.

    N = 10⁸ walkers
    Symmetric measure
    Initial condition: IC (a) — m uniform on T, E = 0
    Time range: n = 0 to 5000 (truncated — past stretched death,
                                before M4's log-spaced region)
    Sampling: every 10 steps from n = 300 to 1000,
              every 50 steps from n = 1000 to 5000
    Output: L₁(n) with B = 1000

At n ∈ {500, 1000, 2000, 3000, 5000}, compare L₁ values
between M4b and M4. Agreement within 2 × θ_N ⇒ the IC-
independence assumption holds empirically. Disagreement ⇒
investigate before committing to M4's single-IC tail
conclusion.

Cost: ~4 hours (5 × 10¹¹ walker-steps ÷ 3.5 × 10⁷ ops/sec).

### A5. Three-parameter mixture fit

Pool M1 + M2 + M4 data on n ∈ [20, 20 000]. Fit

    L̂₁(n)  =  A · exp(−c√n)  +  B · n^(−α)

by nonlinear least squares on log L₁ (or equivalently on L₁
with variance weights from the empirical M0 noise spectrum).
Initial guesses: A ≈ 5, c ≈ 0.55 (from phase 1); B and α
from a log-log linear fit on the pure late-time window
[max(n*, 2000), 20000] alone.

Four parameters. Watch for collinearity between A and c in
the early regime; use priors if needed (c constrained to
[0.5, 0.6], say).

**A5 always runs the full four-parameter unconstrained fit**
regardless of any shape identification handed over from
TUKEYS-LADDER. The unconstrained fit is authoritative. If
TUKEYS hands off "pure H_S" but the unconstrained A5 returns
B̂ with CI excluding 0, the two plans disagree and the
authority-map resolution (TUKEYS is gatekeeper for family;
sibling is estimator within family) fires: rerun, escalate N,
or accept that the shape characterization and parameter
estimation contradict each other and investigate before
committing to a rate claim.

**Sensitivity check.** Refit with c unconstrained (no prior)
and compare the unconstrained c ∈ [c_min, c_max] to the
constrained range [0.5, 0.6]. If c_unconstrained falls inside
[0.5, 0.6] with no pinning at the boundary, the constrained
fit is trustworthy. If c_unconstrained pins at 0.48 or 0.62,
the data disagrees with the phase-1 prior and the constrained
A, B, α estimates are biased — **report both fits in that
case**, and prefer the unconstrained c for interpretation.

**Primary test: bootstrap CI on B.**

Resample the M4 time points (block bootstrap with block size
~5 to preserve any residual autocorrelation) 1000 times,
refit each, produce a 95% CI on B.

- CI excludes 0 and B̂ > 10⁻² ⇒ **mixture detected.**
  MESSES is correct at the rate level: there is an algebraic
  tail. Paper's rate claim must change to a two-scale
  statement (stretched-exp on observable horizon, algebraic
  tail asymptotically).
- CI includes 0 with B̂ near zero (|B̂| < 10⁻²) ⇒
  **pure H_S supported.** MESSES is wrong at the rate level;
  some mechanism we have not identified suppresses the
  algebraic tail that the per-return framework predicts.
  Paper's rate claim stays as stretched-exp.
- CI includes 0 with |B̂| sizable but noisy ⇒ **inconclusive;
  escalate N**.

**Secondary test: late-time power-law fit.**

On the post-transient window [max(n*, 2000), 20 000],
fit log L₁ = b − α log n (two parameters: b, α). Report:

- α̂ and its standard error.
- R² and residual autocorrelation.

The MESSES prediction is α = 1/2. Interpretation:

- α̂ ∈ [0.4, 0.6] with R² > 0.95 ⇒ consistent with algebraic
  tail at the MESSES exponent.
- α̂ outside [0.4, 0.6] with R² > 0.95 ⇒ a different power-
  law tail exists; neither MESSES-mixture nor pure H_S is
  the right model. Something else is going on.
- R² < 0.95 ⇒ the late-time data is not a clean power law;
  possibly a non-power-law decay, possibly noise-dominated.

---

## Decision rule

One decision process, two stages. Stage 1 (initial filter) is
the pure-H_S-vs-pure-H_A test on M1–M3 data. Stage 2 (final
call) incorporates M4 and A5's mixture detection.

### Stage 1: initial filter on M1–M3

This stage decides between pure H_S and pure H_A on the early-
window data. It does *not* resolve mixture; that happens at
Stage 2.

**Reject pure H_A if** all four of:

1. Slope-ratio test at (n₁, n₂) = (25, 100) gives a ratio
   within 0.1 of √(n₁/n₂) and more than 0.1 from n₁/n₂.
2. Linearization: R²(log L₁ vs √n) > R²(log L₁ vs log n)
   on [20, 200], with the difference > 0.005.
3. Signal death: n* exists and n* < 500.
4. M3 agrees: at least one nontrivial initial condition
   ((a), (b), or (c)) shows the same asymptotic classification
   per M3's operational definition above.

**Reject pure H_S if** all four of:

1. Slope-ratio test gives a ratio within 0.1 of n₁/n₂
   and more than 0.1 from √(n₁/n₂).
2. Linearization: R²(log L₁ vs log n) > R²(log L₁ vs √n)
   on [20, 200].
3. L₁ > θ_N **persistently** across the M4 tail: at least 4 of
   the 5 M4 samples in {3000, 5000, 7000, 10000, 14000} lie
   above θ_N. M4's sampling past n = 2000 is log-spaced, so the
   "5 consecutive samples in [4800, 5200]" framing isn't
   meaningful here. This 4-of-5-log-spaced criterion has
   false-positive probability ≈ C(5,4)·(0.001)⁴·(0.999) ≈
   5 × 10⁻¹² under pure H_S, which is considerably stricter
   than a dense-sampling persistence criterion would have been.
4. M3 agrees: at least one nontrivial initial condition
   ((a), (b), or (c)) shows the same asymptotic classification.

**Inconclusive if** the tests split (e.g., linearization
favors H_S but signal death fails) or the effect sizes are
smaller than the stated thresholds. In this case, escalate
M1 to N = 10⁹ and re-run before proceeding to Stage 2.

### Stage 2: three-way final call after M4 and A5

After Stage 1's outcome and A5's mixture fit, the final
decision is one of three:

1. **Pure H_S** (rate is stretched-exp, algebraic tail is
   zero). Triggered by: Stage 1 rejects pure H_A AND bootstrap
   CI on B from A5 includes 0 with |B̂| < 10⁻². Paper's rate
   claim stands as
   ‖π_T(νK^n) − Leb_T‖_TV ≤ C exp(−c√n). Theoretical
   implication: MESSES's per-return Laplace-transform
   framework is wrong or incomplete for this walk — some
   mechanism suppresses the algebraic tail.

   **BENTHIC sub-case distinction.** BENTHIC A3 splits this
   branch in two:
   - ρ(M) ≈ γ₁^{c'} (balanced regime) ⇒ the stretched-exp is
     the *genuine asymptotic rate*, set by the creation-
     destruction balance between mode injection and
     rotation-based decay. The paper's theorem can claim
     exp(−c√n) without qualification.
   - ρ(M) < γ₁^{c'} (rotation-dominated) ⇒ the stretched-exp
     is a *transient* before true exponential emerges at
     horizons past our sim window. The paper's theorem must
     either claim the asymptotic (true exp, but then c is
     the wrong constant) or the observable-window rate
     (exp(−c√n), but as a finite-window statement). Honest
     reporting requires both and a note on the crossover.

2. **Mixture, MESSES-consistent** (stretched transient +
   algebraic tail at α = 1/2). Triggered by: Stage 1 rejects
   pure H_A AND A5 finds |B̂| > 10⁻² with CI excluding 0
   AND α̂ ∈ [0.4, 0.6]. Paper's rate claim becomes a
   two-scale statement. Theorem 1 needs rewriting to reflect
   both regimes; the "stretched-exp" headline becomes
   "stretched-exp on observable horizon, 1/√n asymptotically."

3. **Something else** (α ≠ 1/2, or pure H_A, or neither
   model fits). Neither pure H_S nor MESSES-mixture is the
   right model. Paper needs more work before submission.

**Note on c drift within branches 1 and 2.** The branch triggers
on rate *shape* (presence/absence of B, value of α), not on the
specific value of c. If A5's unconstrained c drifts outside phase
1's [0.50, 0.60] envelope, the branch classification is unchanged:
the paper reports the measured c with a caveat noting the drift.
Branch 3 is reserved for shape-level mismatch (α ∉ [0.4, 0.6],
non-canonical stretched, etc.), not c drift. Drifts larger than
20% from phase 1's 0.55 (i.e., c outside [0.44, 0.66]) should
prompt a second pilot run at independent seeds before the result
is committed to the paper; finite-sample fluctuation at N = 10⁸
shouldn't move c by that much, so material drift is suggestive of
something worth investigating.

---

## Authority map (three plans)

Three sibling plans analyse the same walk from different angles:

- **TUKEYS-LADDER identifies the shape family.** Gatekeeper
  for which parametric family, if any, the data belongs to
  (pure H_S, pure H_A, MESSES-mixture, or something outside
  that set).
- **This plan estimates parameters within the family.**
  Given a family in its decision-rule hypothesis class, the
  fits (c, α, A, B) with bootstrap CIs give the numbers.
- **BENTHIC-MINKOWSKI-SIM explains the mechanism.** Reports
  regime from the empirical mode-coupling matrix M:
  rotation-dominated (ρ(M) < γ₁^{c'}), balanced (ρ(M) ≈
  γ₁^{c'}, predicts genuine stretched-exp asymptotic), or
  injection-dominated (ρ(M) > γ₁^{c'}, predicts algebraic).
  Does not independently decide shape or parameters;
  supplies theoretical narrative for the shape+parameters
  result from the other two plans.

**Authority split.**

1. If TUKEYS-LADDER's shape identification falls inside this
   plan's hypothesis class (H_S, H_A, or MESSES-mixture),
   **this plan's decision rule governs** the paper's rate
   claim. TUKEYS confirms the family; this plan gives the
   numbers.
2. If TUKEYS-LADDER identifies a shape **outside** the
   hypothesis class (e.g., α ≈ 0.42 not 0.5, or a non-power-
   law tail, or an unanticipated decay), **TUKEYS-LADDER's
   verdict overrules** this plan's decision rule. This plan's
   "three-way" decision is only valid inside the three
   specified families; if the data is outside, the "best fit"
   inside the class is a misfit by construction, not a result.
   Paper needs more work.
3. If TUKEYS-LADDER says "too noisy to identify" and this plan
   rules firmly, escalate N — both plans agree escalation is
   the conservative move.
4. **BENTHIC's regime must be consistent with the shape and
   parameters.** Rules for coherence:
   - Shape pure H_S, branch 1 ⇒ expect BENTHIC regime
     "balanced" (genuine stretched-exp) or "rotation-
     dominated" (transient; true exp emerges at longer n).
   - Shape MESSES-mixture, branch 2 ⇒ expect BENTHIC regime
     "injection-dominated."
   - Shape outside class ⇒ BENTHIC regime may be any of the
     three or none; interpretation is case-by-case.

   **n*-based adjudication when BENTHIC disagrees with shape.**
   From BENTHIC's measured ρ(M) and γ₁^{c'}, derive an
   approximate crossover time n* where BENTHIC's predicted
   asymptotic regime should be visible:

       n* ≈ (log(ρ(M)) − log(γ₁^{c'}))^(−2) · scaling

   (exact formula depends on the regime; BENTHIC A3 reports
   n* directly).

   - **n* < max sim n** (inside our 20 000-step horizon) ⇒
     BENTHIC's prediction *should* have been visible in M4's
     tail data. If it isn't, either BENTHIC's M was measured
     incorrectly (rerun B3 at higher N) or the regime
     classification is wrong. **Do not commit to a paper
     claim until this is resolved.**
   - **n* > max sim n but within practical compute range**
     (n* ∈ [2 × 10⁴, 10⁸]) ⇒ BENTHIC's prediction is
     untestable in current budget. Paper reports the
     observable-window rate (e.g., stretched-exp with
     measured c) as primary; states the theoretical caveat
     in a remark: "BENTHIC analysis predicts a crossover to
     [true exp / algebraic / other] past n ≈ n*; this
     regime is outside our sim horizon and not empirically
     verified." Two-regime theorem wording.
   - **n* >> practical range** (n* > 10¹⁰ or formally
     infinite) ⇒ BENTHIC's prediction is of theoretical
     interest only; practical rate is the observable-window
     rate. Theoretical caveat becomes a footnote rather
     than a qualifying statement.

   In all three cases, the decision on paper wording depends
   on which case we're in — *specify this in the manuscript's
   Theorem 1 wording, not ex post*. Without the n*-based
   adjudication, "investigate" has no terminating condition.

A worked summary: TUKEYS-LADDER is gatekeeper for *which
parametric family applies*; this plan is estimator *once the
family is fixed*; BENTHIC is explainer *for why the family and
parameters are what they are*. The paper's rate claim is
contingent on all three: shape-family confirmation by TUKEYS,
decision-rule outcome here, and regime coherence from BENTHIC.

---

## Cost

Calibrated from phase 3's measured rate on the local machine:
3.5 × 10⁷ walker-steps per second with the (m, E, sign) state
representation and vectorized numpy operations.

M0: negligible (< 1 minute; multinomial null only).

S0: post-processing on M1's per-walker N_n output; < 10 minutes
analysis time. No new sim.

M1 (consolidated with BENTHIC B1 + B2): 10⁸ walkers × 600 steps
= 6 × 10¹⁰ walker-steps ÷ 3.5 × 10⁷ ≈ 30 minutes base, plus
~10% marginal for Fourier coefficient tracking; call it
~35 minutes.

M2 (consolidated to [0, 300]): 10⁸ × 300 = 3 × 10¹⁰ walker-
steps ÷ 3.5 × 10⁷ ≈ 15 minutes.

M3: 3 × M1 ≈ 1.75 hours. Mandatory.

B3 (BENTHIC excursion-resolved mode coupling): 10⁷ walkers ×
600 steps + per-walker excursion logging ≈ 4 hours.
Default always-on.

M4 (mixture detection): 10⁸ × 20 000 = 2 × 10¹² walker-
steps ÷ 3.5 × 10⁷ ≈ 16 hours on a single machine.
Conditional escalation to N = 10⁹ (≈ 6–7 days single-machine;
recommend cluster) if M4 at 10⁸ returns an inconclusive
bootstrap CI on B.

M4b (IC cross-check, optional): 10⁸ × 5000 = 5 × 10¹¹
walker-steps ÷ 3.5 × 10⁷ ≈ 4 hours. Recommended if the paper's
rate claim is sensitive to the IC-independence assumption on B,
α; skipped if budget-constrained and the theoretical argument
is accepted.

Analysis-only steps (A1b, A4b, A4c, BENTHIC A1b): post-processing
on existing sim data; a few hours of person-time, no new compute.

Total M0 + S0 + M1 + M2 + M3 + B3 + M4 baseline: ~22 hours,
overnight-plus-evening. Adding M4b: ~26 hours. M4 escalation to
10⁹ is separate and cluster-recommended.

(Earlier versions of this section estimated ~53 hours for the
baseline; that used a conservative 100 ns/walker-step scaling
that phase 3's 3.5 × 10⁷ ops/sec benchmark showed to be off by
~6×. Kept as a footnote in case the sim turns out slower than
phase 3 measured on different hardware.)
