# TUKEYS-LADDER

Shape-first, nonparametric companion to `ALGEBRAIC-SIM-MESS-PLAN.md`.
Same data, same question, different approach: let the data's shape
reveal itself before committing to a parametric family.

---

## Premise

`ALGEBRAIC-SIM-MESS-PLAN.md` tests two named models (H_S: stretched-
exp; H_A: pure algebraic; later extended to an A·exp(−c√n) + B·n^(−α)
mixture) via parametric fits against pre-committed discriminants.
That plan answers a question of the form **"does the data fit model
X or model Y?"**

This document answers a different question: **"what shape is the
data?"** The distinction matters precisely when neither pre-specified
model is correct. The parametric plan's decision rule can reject
"neither" only as an "inconclusive" escape hatch. Here, neither is
the starting hypothesis; the data picks its own shape.

All three plans (this one, `ALGEBRAIC-SIM-MESS-PLAN.md`, and
`BENTHIC-MINKOWSKI-SIM.md`) use the same simulation runs (M0, S0,
M1–M4, M4b plus BENTHIC's B1–B3). **Run specs and the default
execution schedule are authoritative in `ALGEBRAIC-SIM-MESS-PLAN.md`**;
this document refers rather than re-specifies. If a run spec changes
there, update any downstream window definitions here.

See [`sim/README.md`](README.md) for the cross-document framing
(scientific discrimination + proof triage, the three-plan triangle,
structured disagreement as deliverable). This plan's authority map
at the end specifies the operational adjudication rules for
disagreements on *this plan's* shape diagnostics.

**Shared prerequisite: S0 (Mittag-Leffler index test).** Both this
plan's shape identification and BENTHIC's regime classification
implicitly assume the per-walker return count N_n follows ML(1/2).
If S0's measured tail exponent β̂ is outside [0.45, 0.55], the √n
framing of the sibling plans' diagnostics (s_log(n), L3, L4) may
be wrong in the exponent. Defer to `ALGEBRAIC-SIM-MESS-PLAN.md`
Run S0 for the prerequisite test and its decision rule.

The divergence between the plans is entirely in analysis:

- This plan identifies *what shape the data is*.
- ALGEBRAIC-SIM-MESS-PLAN estimates *what the parameters are*.
- BENTHIC-MINKOWSKI-SIM explains *why the shape is what it is*
  via the mode-coupling matrix for the walk.

They may agree; where they disagree is where the interesting
physics (or a bug) lives. See "Authority map" at the bottom of
this document for how conclusions combine.

---

## The ladder

Tukey's ladder of re-expressions: apply power transforms to each
axis and look for the one that straightens the curve.

    y → y^p_y,    x → x^p_x,    p ∈ {..., −1, −1/2, 0 (log), 1/2, 1, 2, ...}

For decay data L₁(n), we are asking: which (p_y, p_x) makes the plot
most linear? The winning pair *is* the shape. We don't fit a model
first and check — we find the shape first and name the model second.

**Grid to try:**

| # | y-transform | x-transform | linear ⇔ | priority |
|---|---|---|---|---|
| L1 | log L₁ | √n | L₁ = C exp(−c√n) — stretched-exp (H_S) | primary |
| L2 | log L₁ | log n | L₁ = C n^(−α) — power law (H_A) | primary |
| L3 | L₁·n^α (α-grid) | n | plateau at B for α = tail exponent | primary, α-grid |
| L4 | L₁·exp(c√n) | n | plateau at A if c is right (c from M1 [20, 200]) | primary, fixed c |
| L5 | log L₁ | n | L₁ = C exp(−k n) — pure exponential | sanity |
| L6 | log L₁ | n^(1/3) | L₁ = C exp(−c·n^(1/3)) — non-canonical stretched | sanity |

**Primary rows** (L1–L4) are the plots that directly answer the
question of shape. L1 and L2 distinguish stretched-exp from power-law
by which transform straightens the curve. L3 and L4 are direct
coefficient-reading plots (see "Direct plots" below). Each primary
row gets the full LOESS-bandwidth treatment (next section).

**Sanity rows** (L5, L6) check for non-canonical shapes — pure
exponential or stretched at a non-1/2 exponent. Generate once; skip
bandwidth sweeps unless primary rows are inconclusive.

**Primary diagnostic: visual linearity.** Plot each transform. The
one that is straightest — by eye, not by R² — tells you the shape.
R² is a secondary summary that compresses the picture.

**L3 uses an α-grid, not a single α.** L3 is the consolidated form
of what was previously "direct plot T1" (L₁·√n, which commits to
α = 1/2). Plot L₁·n^α for α ∈ {0.3, 0.4, 0.5, 0.6, 0.7} side-by-
side. The α that produces a visual plateau at large n *is* the tail
exponent. If no α in that range produces a plateau, the tail is
either exponent outside [0.3, 0.7] or not a power law at all.

**Cross-reference to BENTHIC.** The ladder's primary rows (L1–L4)
all decompose the mantissa deviation by mode at some level. L3 in
particular asks "which power-law exponent of n straightens the
tail," which is equivalent to asking about the asymptotic scaling
of ‖h‖_{L²} in the Fourier decomposition. BENTHIC's mode-coupling
matrix M is the operator whose spectral radius controls this
scaling at the dominant Fourier mode. If L3 and L4 converge on a
norm in which BS(1,2)'s transfer operator cleanly contracts,
that's exactly BENTHIC's Fourier-weighted L². Cross-check
BENTHIC's empirical ρ(M) and γ₁^{c'} against L3's inferred α and
L4's stability range of c; consistent answers raise confidence
in both plans.

**L4 uses a fixed c.** Use c from ALGEBRAIC-SIM-MESS-PLAN's M1 fit on
[20, 200]. A single scalar, not a grid. If L4 fails to be flat
throughout [20, 20000], that failure is itself diagnostic: either A
is changing (shouldn't under pure H_S), or c doesn't globally fit the
data (supporting mixture or "something else"). Cross-reference:
compare L4's failure pattern to the segmented-fit table's c_i values
(below). If c_i drifts across windows and L4 breaks in the same
windows, that's coherent evidence for shape change.

---

## The local power-law exponent s_log(n)

Define

    s_log(n) := d(log L₁) / d(log n).

This is the local power-law exponent at n. Computed nonparametrically
by LOESS (local linear regression) on the (log n, log L₁) data.

**Name note (coordination with ALGEBRAIC-SIM-MESS-PLAN A1).** The
sibling plan's A1 defines s_lin(n) := d(log L₁)/dn, the log-linear
slope. These are the same derivative, reparametrized via the chain
rule:

    s_log(n)  =  n · s_lin(n).

Different visual axes, same underlying quantity. Sibling A1 plots
s_lin vs. 1/√n (straight under H_S, slope −c/2) and vs. 1/n
(straight under H_A, slope −α). This plan's s_log plots vs. √n
(grows linearly under H_S) and vs. log n (flat under H_A). Neither
framing obsoletes the other — produce both or pick one consistently.
Here we adopt s_log because the "local power-law exponent" reading
is Tukey-native.

**LOESS bandwidth — concrete recipe.** "Modest" is useless without a
number. Produce three s_log plots side-by-side at bandwidths

- **Narrow: 5%** of the log-n data range — preserves features at
  the cost of noise.
- **Medium: 15%** — default.
- **Wide: 30%** — rejects noise, smooths features.

A mixture crossover that is real should be visible (same sign of
transition, similar transition location) at all three bandwidths. A
"feature" visible only at 30% is a smoothing artifact; one visible
only at 5% is noise. The running-median diagnostic (below) uses the
same three bandwidths on its neighborhood size so the two smoothers
are comparable.

**Expected patterns:**

| model | s_log(n) |
|---|---|
| Pure H_S: log L₁ = a − c√n | s_log(n) = −(c/2)·√n — grows in magnitude |
| Pure H_A: log L₁ = a − α log n | s_log(n) = −α — constant |
| Mixture: stretched + algebraic | starts growing in magnitude (H_S-like), plateaus at −α (H_A-like) |
| Something else | s_log(n) takes some other shape |

**What s_log(n) reveals that no single parametric fit does:**

- **Pure H_S** shows as a curve in −s_log(n) vs. √n that is straight
  through the origin with slope c/2.
- **Pure H_A** shows as −s_log(n) flat at α.
- **Mixture** shows as **a transition** in s_log(n): growing like
  √n in the pre-asymptotic window, then asymptoting to a
  constant. The transition point is the crossover; the asymptote
  is α.
- **Non-MESSES shapes** show as any other pattern — s_log(n) could
  oscillate, saturate at a value ≠ 1/2, grow super-linearly in
  √n, etc. All of these are visible in s_log(n) and invisible in
  a fitted c or α.

**Plot s_log(n) on log n.** Then plot s_log(n) on √n. Whichever plot
straightens the curve is your transform. If neither does, you're
looking at something that isn't H_S, H_A, or the mixture.

---

## Direct coefficient-reading plots

Two of the ladder's primary rows read mixture coefficients directly
without a fit. They deserve a separate look because the reading is
immediate.

### L3 (α-grid): tail coefficient B

L₁(n) · n^α vs. n, over α ∈ {0.3, 0.4, 0.5, 0.6, 0.7} side-by-side.

- The α that produces a **visual plateau at large n** *is* the
  tail exponent. The plateau's height *is* B.
- Pure H_S: L3 goes to zero for every α (because exp(−c√n) · n^α
  → 0 for any α). No plateau at any α.
- Pure H_A at exponent α_true: L3 at α = α_true is constant = B.
  At other α, L3 slopes up (α > α_true) or down (α < α_true).
- Mixture: L3 rises from 0 toward a plateau at B when α = α_true;
  at other α, rising to a drifting-up or drifting-down line.

If no α ∈ {0.3, ..., 0.7} produces a plateau, the tail is either
at an exponent outside this range or not a power law. Widen the
grid or fall back to s_log(n) for diagnosis.

### L4 (fixed c): stretched-exp coefficient A

L₁(n) · exp(c·√n) vs. n, at c from M1's [20, 200] fit (a single
scalar committed by the sibling plan, not a grid).

- Pure H_S: L4 is **constant = A**, the stretched-exp amplitude.
- Pure H_A: L4 grows as n^(−α) · exp(c√n) — super-exponentially
  in √n.
- Mixture: L4 ≈ A early, then grows as B · exp(c√n) · n^(−1/2)
  past the crossover.

**Flatness of L4 is a diagnostic in itself.** If L4 stays flat
throughout [20, 20000], pure H_S wins and A is L4's value. If L4
breaks from flat at some n*, that break is the crossover. If L4 is
not flat even at small n, c from the M1 fit doesn't globally fit
the data — which is independently telling (supports mixture or
something else). Cross-reference with the segmented-fit table
below: if c_i drifts across windows and L4 breaks at the same
transition, the two diagnostics agree on a shape change.

### Combined reading

- L3 flat at some α, L4 grows ⇒ mixture; B is L3's plateau, A is
  L4's small-n intercept, α_true is the plateau-producing α.
- L3 → 0 at every α, L4 flat ⇒ pure H_S; A is L4's value, no tail.
- L3 flat at some α, L4 grows from n = 0 ⇒ pure H_A; B is L3's
  plateau, A ≈ 0, α is L3's plateau-producing α.
- Anything else ⇒ neither pure nor mixture; the data says so
  visually.

These are cheap plots to generate and high-information.

---

## Segmented fits

Rather than one global fit, do many local fits and tabulate.

Split n ∈ [1, 20000] into disjoint log-spaced windows. Each window's
data comes from a specific run (per ALGEBRAIC-SIM-MESS-PLAN's specs):

    W1 = [20, 80]        ← M1 (dense sampling [20, 200])
    W2 = [80, 300]       ← M1 + M2 (M2 covers [0, 300])
    W3 = [300, 1000]     ← M4 (dense sampling [300, 2000])
    W4 = [1000, 3000]    ← M4
    W5 = [3000, 20000]   ← M4 (log-spaced past n = 2000)

If an analyst tries to fit W5 on M1 data, they'll find no samples
there — M1 stops at n = 600. Respect the run-to-window mapping.

In each window, fit both:

    (i)  log L₁ = a_i − c_i √n    (local stretched-exp fit)
    (ii) log L₁ = a_i − α_i log n  (local power-law fit)

Report a table:

| window | c_i | R²(i) | α_i | R²(ii) |
|---|---|---|---|---|
| W1 | | | | |
| W2 | | | | |
| W3 | | | | |
| W4 | | | | |
| W5 | | | | |

**Read the table, not a single number:**

- c_i stable across windows, α_i drifting down to ~1/2 from below ⇒
  pure H_S. α is just trying to fit a non-power-law shape and
  tilting with the window.
- α_i stable at ~1/2 across windows, c_i drifting up ⇒ pure H_A.
- c_i large in W1–W2, α_i close to 1/2 in W4–W5, both fits fighting
  in between ⇒ mixture with crossover in W3 or so.
- c_i and α_i both unstable ⇒ neither shape is right. Look at s(n).

The pattern across windows is the story. A single global fit hides
all of it.

---

## Robust / resampled estimation

Tukey was paranoid about outliers and distributional assumptions.
For this problem the paranoia is warranted: L₁ at small n has
discretization structure from the walker count, and at large n has
near-noise-floor behavior where the distribution of L₁ is asymmetric
(bounded below by 0).

### Running median of local slope

Instead of A1's finite difference, for each n_0 compute

    median{ (log L₁(n) − log L₁(n_0)) / (log n − log n_0) :
            n in a log-neighborhood of n_0 }

Plot vs. log n. The running median is robust to occasional outlier
L₁ values (from sampling noise or float quirks). Compare to the
LOESS-based s(n). Where they agree, trust the signal. Where they
disagree, the data has structure worth investigating.

### Jackknife by walker subset

Split the N = 10⁸ walkers into 20 groups of 5 × 10⁶. Compute L₁(n)
separately on each group. Report mean and interquartile spread of
L₁ at each n. If the IQR is tight, the parametric confidence
intervals are trustworthy. If it's wide (factor-of-3 or more at
moderate n), they're lying.

### L₁ vs. ‖h‖_{L²} rate cross-check

BENTHIC operates in L² on Fourier modes; this plan and ALGEBRAIC
work in L₁. The authority-map's BENTHIC-disagreement flag is
meaningful only if the two norms share the same exponent rate
— otherwise a "disagreement" could be benign norm-mismatch.

Compute from M1 + B1's shared data:

- L₁(n) — this plan's and ALGEBRAIC's primary statistic.
- ‖h‖_{L²}(n) ≈ (Σ_{r=1…5} |ĥ(r, n)|²)^(1/2) from B1's
  Fourier coefficients.

Plot log L₁(n) and log ‖h‖_{L²}(n) against the transform that
straightens L₁ (typically √n on [20, 200]). Parallel slopes
(within 20% of each other) confirm rate transfer and validate
using BENTHIC's L² regime as an L₁-consistency check.
Divergent slopes indicate h is spreading across modes at
different rates; interpret authority-map flags cautiously, and
see `ALGEBRAIC-SIM-MESS-PLAN.md` A4c for the detailed treatment.

Zero marginal cost: the Fourier coefficients needed for ‖h‖_{L²}
are already produced by the consolidated M1 + B1 run.

### Initial-condition robustness for the algebraic tail

M4 is single-IC at (0, 0); M3's three-IC coverage stops at n = 600
(the stretched-transient window). Neither plan's primary
diagnostics test IC-dependence of the algebraic tail directly.

**Assumed on theoretical grounds:** the algebraic-tail
coefficient B and exponent α are IC-independent, because they
derive from the lower tail of the return-time distribution for
a null-recurrent walk on ℤ, which depends on the walk's step
distribution, not on the initial state. A and the crossover time
n* are expected to be IC-dependent; M3 covers A-level
robustness via its early-regime analysis.

If this assumption fails — if B varies with IC for some reason
we haven't anticipated — neither plan's primary analysis would
catch it. The sibling plan's optional M4b (IC (a), N = 10⁸,
n = 0–5000) is the empirical cross-check. If M4b's L₁ at large
n agrees with M4's within 2 × θ_N, IC-independence of the tail
holds; if not, investigate before committing to the
shape-family classification from M4 alone.

State this assumption in any shape-identification report,
regardless of whether M4b is run.

### Jackknife by time window

Drop W_i from the data and refit globally. If c_global or α_global
changes by more than its stated SE when a window is dropped, the
fit is driven by that window rather than fitting a shape present
throughout.

### Null threshold: default and robust alternative

**Default: M0's θ_N** (99.9% quantile of L₁ under the multinomial
null), same threshold the sibling plan uses. Using the same null
threshold in both plans keeps comparisons apples-to-apples.

**Robust alternative: pointwise resampled threshold.** Resample a
walker-subset, compute L₁, repeat 500 times, take the 99th
percentile of resampled L₁ at each n. This gives a noise envelope
that accounts for the empirical distribution of L₁ on the actual
M4 data, not just the idealized multinomial null — useful as a
cross-check on θ_N, especially if M0's multinomial assumption
differs from the actual late-time walker distribution. If the
pointwise resampled 99th percentile is within 50% of θ_N at large
n, the null assumption is fine. If it's materially different, the
walkers aren't behaving like iid multinomial draws even after the
transient dies, and something about the walk's long-time behavior
deserves investigation.

---

## Residual diagnostics

After any parametric fit produced in the segmented analysis or
mixture fit, plot residuals

    r(n) = log L₁_obs(n) − log L₁_fit(n)

at **expanded vertical scale** — 10× the y-range of the original
plot, so residuals the size of 0.01 are visible at a glance.

**Things to look at, by eye, in each plot:**

- **Systematic sign pattern:** all-positive in one window and
  all-negative in another means the fit has missed a shape.
  Specifically, positive residuals in [2000, 20000] after a pure
  H_S fit are the signature of an algebraic tail.
- **Amplitude growth:** residuals larger at large n than at small
  n means the fit is accurate in early data and degrading.
- **Structure in residual(n):** if |r(n)| shows a bump, hump,
  or systematic variation, the model is missing that feature.
  Clean white noise is what "model fits" looks like.

Do not summarize residuals by a single number. Plot them.

---

## Pilot

Before committing to M4's 16-hour run at N = 10⁸: do a 5-minute
run at N = 10⁶ with the full horizon n ∈ [0, 20000]. The signal
will be swallowed by noise at large n (floor ~ 10⁻²), but:

- **Shape is visible.** s_log(n) on [20, 500] is clean enough to
  compare to phase 1 and catch implementation bugs.
- **Pilot catches pathology.** If L₁ does something unexpected
  (crosses zero, has discontinuities, decays at an unanticipated
  rate), better to find out in 5 minutes than 16 hours.
- **M0 pilot.** A 30-second M0 at N = 10⁶ establishes the
  pilot's own null floor; useful cross-check for the full-N M0.

**Pilot output:** s_log(n) plot with three bandwidths, L3 and L4
plots, segmented-fit table on the windows where signal is above the
pilot's noise floor.

**Concrete stop-trigger.** On [20, 300], fit s_log(n) using LOESS at
medium bandwidth. Under phase 1's stretched shape (c ≈ 0.548), the
expected s_log(n) is −(c/2)·√n. The pilot's LOESS s_log(n) should
lie within

    s_log(n) ∈ −(c/2)·√n · [0.9, 1.1]    for c ∈ [0.52, 0.58]

i.e., within 10% of phase 1's prediction across c's envelope. If
pilot s_log(n) lies materially outside this band (say, off by more
than 20% in magnitude, or trending toward a constant rather than
growing with √n), **stop and debug** before committing to the full
run. The tolerance here matches the sibling plan's mandatory check
on c — they should agree or something is wrong in both.

---

## What counts as an answer

No pre-committed decision rule. The goal is to characterize the
shape, not to reject a hypothesis. Final deliverables:

- **Shape description** from s(n) and the re-expression ladder:
  "data is stretched-exp with exponent c ≈ X on [20, 500],
  transitions to power law with α ≈ Y on [1000, 20000]" — or
  whatever the data actually shows.
- **Direct coefficient reads** from L3 (α-grid) and L4 (fixed c)
  where applicable.
- **Segmented-fit table** showing how parameters move across
  windows.
- **Robustness assessment** from walker and time-window jackknife.
- **Residual plots** at expanded scale after any global fit.

The output might be:

- *"Clean H_S throughout, A ≈ 5, c ≈ 0.55, L3 → 0 at every α,
  L4 flat, segmented-fit c_i stable, residuals white."* — same
  conclusion as the sibling, different route.
- *"Mixture detected: L3 plateaus at B ≈ 0.3 with α ≈ 0.5 past
  n ≈ 3000, L4 grows past n ≈ 2000, s_log(n) transitions from
  √n-growth to flat ≈ 0.5, segmented α_i drops to ~0.5 in
  W4–W5."* — same conclusion as the sibling's mixture branch,
  cross-validated.
- *"Shape changes at n ≈ 500 from stretched-looking to a power
  law with α ≈ 0.42, not 0.5. Neither H_S nor MESSES-exponent
  1/2 fits. Something else is going on."* — an answer this plan
  delivers naturally that the sibling plan can reach only via its
  "inconclusive" escape hatch and a follow-up.
- *"Data past n = 1000 is too noisy to distinguish; L3 and L4
  both floor-dominated; need higher N."* — honest call for
  escalation.

---

## What this plan does not do

- Does not commit to H_S or H_A as named hypotheses before looking.
- Does not produce a binary reject/accept decision.
- Does not set quantitative thresholds in advance.
- Does not formally test any model.

Everything in this plan is **diagnostic**, not **inferential**. The
inferential work — if any is needed — happens after the shape is
known, and is done by the sibling plan's machinery with the right
parametric family already chosen.

### Handoff rule to sibling A5

Explicit trigger for invoking the sibling's parameter-estimation
machinery: once this plan's shape identification concludes that the
data belongs to a family in {pure H_S, pure H_A, MESSES-mixture A·
exp(−c√n) + B·n^(−1/2)}, hand off to `ALGEBRAIC-SIM-MESS-PLAN.md`
A5 for tight numerical estimates of the parameters within that
family.

**A5 always runs the full four-parameter unconstrained fit**
(A, c, B, α) regardless of which family this plan identified. The
handoff is a *reporting and expectation* convention, not a
constraint on the fit itself. This preserves A5 as an independent
sanity check on the shape identification: if this plan says "pure
H_S" but the unconstrained A5 returns B̂ with CI excluding 0, the
two plans disagree and authority-map resolution fires.

Reporting and expectation by family:

- Shape is **pure H_S** ⇒ A5 runs unconstrained. Expect B̂ ≈ 0 with
  CI including 0 and |B̂| < 10⁻². Paper reports (A, c) prominently;
  (B, α) reported as consistency checks. If A5's unconstrained B̂
  disagrees (material nonzero), flag for escalation.
- Shape is **pure H_A** ⇒ A5 runs unconstrained. Expect Â ≈ 0 and
  well-defined (B, α) with α̂ ∈ [0.4, 0.6]. Paper reports (B, α).
- Shape is **MESSES-mixture** ⇒ A5 runs unconstrained. Expect both
  B̂ > 10⁻² with CI excluding 0 and α̂ ∈ [0.4, 0.6]. Paper reports
  all four parameters with bootstrap CIs.
- Shape is **outside the three families** (non-canonical stretched,
  non-0.5 power-law, two-regime without the MESSES form, etc.) ⇒
  **do not hand off to ALGEBRAIC A5.** ALGEBRAIC's A5 fits a form
  the data doesn't match; the "best fit" would be meaningless.
  Report this plan's shape characterization as the final output
  and flag that the paper's rate claim cannot be stated in the
  current framing.

**Parallel handoff to BENTHIC A3.** Regardless of which shape
family this plan identifies — including "outside the three
families" — also hand off to `BENTHIC-MINKOWSKI-SIM.md` A3 for
mode-coupling matrix analysis. BENTHIC doesn't need to know the
shape in advance; it reports regime (rotation, balanced,
injection) from B3's empirical M independent of shape
classification. Expected correspondence:

- Shape is pure H_S ⇒ BENTHIC should report balanced or
  rotation-dominated regime.
- Shape is pure H_A ⇒ BENTHIC should report injection-dominated.
- Shape is mixture ⇒ BENTHIC should report injection-dominated
  (the tail's presence is what "injection-dominated" means at
  the mechanism level).
- Shape is outside the three families ⇒ BENTHIC's regime is
  case-by-case; useful data for interpreting the anomaly but
  not a decisive handoff target.

Disagreement between this plan's shape and BENTHIC's regime is a
red flag and should be investigated before the paper commits to
any rate claim.

---

## Cost

Zero additional compute cost: same M0–M4 runs as `ALGEBRAIC-SIM-
MESS-PLAN.md`. All differences are in analysis — a few hours of
looking at plots carefully rather than minutes running fits.

Analysis time: ~half a day of focused plotting and table-building
per run batch, plus whatever time discrepancies with the sibling
plan trigger.

---

## Authority map (three plans)

The parametric plan (ALGEBRAIC) is efficient if the right model is
in its hypothesis class. This plan is efficient if the right model
is *not* in ALGEBRAIC's hypothesis class — it finds that out
faster, because it starts without presuming. BENTHIC is efficient
for explaining *why* the shape is what it is, not for deciding
shape or parameters.

**Authority split when the three plans' conclusions combine:**

1. **This plan identifies the shape family.** Output: which
   parametric family, if any, the data belongs to — pure H_S,
   pure H_A, MESSES-mixture, or something outside that set.
2. **ALGEBRAIC estimates parameters within the family.**
   Given a family that matches one of its decision-rule cases,
   its fits (c, α, A, B with bootstrap CIs) give the tight
   numerical estimates.
3. **BENTHIC explains the mechanism.** Reports a regime from
   the empirical mode-coupling matrix M:
   - rotation-dominated (ρ(M) < γ₁^{c'}) ⇒ true exp; finite-
     window shape may look stretched (transient);
   - balanced (ρ(M) ≈ γ₁^{c'}) ⇒ genuine stretched-exp
     asymptotic;
   - injection-dominated (ρ(M) > γ₁^{c'}) ⇒ algebraic.

   BENTHIC does not decide shape or parameters; it supplies
   theoretical narrative for the shape+parameters result.

**How disagreements resolve:**

- **This plan says family F; ALGEBRAIC's decision rule returns
  the matching case.** Agree. Paper's rate claim is set by
  ALGEBRAIC's fit within F. High confidence.
- **This plan says family F; ALGEBRAIC returns a different case
  in {H_S, H_A, mixture}.** Debug. Likely one of the plans
  mis-read marginal data; rerun with more N or check
  implementation.
- **This plan says the shape is outside {H_S, H_A, mixture};
  ALGEBRAIC forces a decision anyway (e.g., "reject H_A, accept
  H_S").** **This plan overrules.** ALGEBRAIC's "fit" is the
  least-bad inside its hypothesis class; the actual shape is
  outside. Paper's rate claim in its current framing cannot be
  made. Paper needs more work.
- **This plan says "too noisy to identify", ALGEBRAIC rules
  firmly.** Escalate N. Both plans agree the conservative move
  is more data.
- **BENTHIC's regime disagrees with shape+parameters.** Red
  flag. The concrete adjudication uses the crossover time n*
  implied by BENTHIC's ρ(M) and γ₁^{c'}:
  - **n* < sim horizon** ⇒ testable; if not seen, BENTHIC
    is wrong. Rerun.
  - **n* > sim horizon, < 10⁸** ⇒ untestable in current
    budget. Paper reports observable-window rate primary,
    theoretical caveat in a remark.
  - **n* >> 10⁸** ⇒ theoretical footnote; paper's rate is
    the observable-window rate.

  See `ALGEBRAIC-SIM-MESS-PLAN.md` authority-map rule 4 for
  the full adjudication with specific wording guidance.

**Summary.** This plan is gatekeeper for *which parametric family
applies*. ALGEBRAIC is estimator *once the family is fixed*.
BENTHIC is explainer *for why the family and parameters are what
they are*. The paper's rate claim is contingent on all three:
shape-family confirmation here, decision-rule outcome in
ALGEBRAIC, regime coherence from BENTHIC. Run all three.
Full agreement is high-confidence; any disagreement is
informative and triggers investigation.

In our specific case, the most consequential disagreement would
be this plan finding a non-canonical shape (e.g., power-law with
α ≠ 0.5, or a two-regime decay whose crossover doesn't match the
MESSES-predicted form). That is precisely what MESSES.md opened up,
and this plan is the mechanism for catching it. BENTHIC's regime
data then tells us which mechanism class we've landed in.
