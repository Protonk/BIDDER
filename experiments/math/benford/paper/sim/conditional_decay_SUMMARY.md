# Conditional decay — Test A rejects hypothesis, plan terminated

Ran Test A (analytic Fourier) of `CONDITIONAL-DECAY-PLAN.md` v3.
Decision gate at the end of Test A: if TV^H(n) under hypothesis H
does not match the measured paper transient shape (c ≈ 0.498 at
γ = 0.5), abort Tests B and C. Test A's result rejects H, so B
and C did not run.

Run: `run_conditional_a.py`.
Data: `conditional_decay_results/analytic_H.npz`.
Date: 2026-04-19.

## Recap of hypothesis H

Under H, b-steps in BS(1,2) do not move the mantissa conditional
on the a-step count K. Then:

    c_k^H(n) = e^{−2πi k m₀} · ((1 + cos(2π k α))/2)^n,
    |c_k^H(n)| = cos²(π k α)^n,

where α = log₁₀ 2, m₀ = log₁₀ √2.

TV^H(n) is computed by inverse-FFT from the first K_max = 500
Fourier coefficients to an m-grid of 10000 points, then
∫|ρ^H − 1|dm.

## Results

### Slow-mode hierarchy (top 12 by per-step magnitude)

| k   | per-step mag | decay rate/step | kα mod 1 (distance to integer) |
|:---:|:------------:|:---------------:|:------------------------------:|
| 485 | 0.9999980    | 2.0 × 10⁻⁶      | 0.000452                       |
| 196 | 0.9999651    | 3.5 × 10⁻⁵      | 0.001879                       |
| 289 | 0.9999464    | 5.4 × 10⁻⁵      | 0.002331                       |
| 392 | 0.9998606    | 1.4 × 10⁻⁴      | 0.003758                       |
| 93  | 0.9998250    | 1.8 × 10⁻⁴      | 0.004210                       |
| 10  | 0.9989533    | 1.0 × 10⁻³      | 0.010300                       |

These are the continued-fraction convergent denominators of
log₁₀ 2 (k = 10, 93, 196, 485 are consecutive convergents) and
their near-multiples. Each gives an extremely slow-decaying
Fourier mode under H.

### TV^H(n) shape

| n     | TV^H      | L²^H      |
|:-----:|:---------:|:---------:|
| 10    | 1.56      | 11.2      |
| 100   | 1.32      | 6.3       |
| 1000  | 1.05      | 3.5       |
| 10000 | 0.77      | 1.9       |

TV^H barely moves. At n = 10000 the hypothesis predicts the
mantissa is still at TV ≈ 0.77 from uniform — essentially
unmixed.

### Fit comparison

**Best-fit stretched-exp on TV^H (γ free):**
  γ = 0.150, c = 0.266, R² = 0.9993 on n ∈ [30, 3000].

**At fixed γ = 0.5 (paper's fit shape):**
  c = 0.0090, R² = 0.9509.

**Paper's measured M1 sharp-IC transient:**
  c ≈ 0.498 at γ = 0.5 (`T1B-EVIDENCE-MAP.md:157`).

The hypothesis predicts a c that is **55× smaller** than
measured, at the same γ = 0.5. The best-fit γ for H is 0.15,
not 0.5. In either view, H's shape is quantitatively
incompatible with the paper's observed transient.

## Why H fails

The a-step walk on T has step size ±α = ±log₁₀ 2. The walker's
m after k a-steps sits on a quasi-periodic lattice
{m₀ + j·α mod 1 : |j| ≤ k}. Mixing on T from this structure is
controlled by Diophantine properties of α. For log₁₀ 2, the
best rational approximations at scale k* ≈ √n put the dominant
surviving Fourier mode k = 10, 93, 196, 485 at very slow decay
rates. Result: the pure-a-rotation walk mixes VERY slowly — so
slowly that TV is still ≈ 0.77 at n = 10000.

The real BS(1,2) walker mixes orders of magnitude faster because
**b-steps shift m by non-α amounts when |x| is O(1)**. At the
M1 initial condition x = √2, the walker spends its early steps
near |x| ≈ 1 where b-steps contribute non-quasi-periodic m-shifts
that destroy the Diophantine bottleneck.

So the hypothesis was qualitatively wrong: the b-step is _not_
passive on m during the transient. It is the dominant mixer.
Once |x| grows large (E drifts up, per `laplace_diagnostic_SUMMARY.md`),
b-steps cease moving m, and the walker enters a different regime
whose dynamics this plan didn't address.

## Why this is a useful null result

Before Test A, the hypothesis had surface plausibility: the
measured transient shape (stretched-exp γ ≈ 0.5, c ≈ 0.5) and
the known Diophantine structure of log₁₀ 2 both seemed
compatible in order of magnitude. Test A shows they aren't. The
Diophantine/a-only mechanism gives a _dramatically_ slower
predicted transient (55× smaller c at γ = 0.5, or different γ
altogether). No amount of b-step correction would bridge that
gap by staying passive on m.

This rules out the cleanest mechanism-level story for the
transient. The actual transient must involve active b-step
mixing on m, which is harder to analyze in closed form.

## What this informs

- **Not load-bearing.** Under T1b the theorem's asymptotic is
  1/√n, and the transient is acknowledged as IC-specific. This
  null result tightens what we say about the transient but does
  not change T1b's status.
- **MESSES.md §1 unaffected.** Mess #1 addresses the asymptotic
  rate conversion, not the transient. This result doesn't
  change that diagnosis.
- **For the proof architecture:** the transient's mechanism
  requires active b-step contribution to m-mixing, not just
  a-step Diophantine structure. If the draft ever tries to
  explain the stretched-exp rate via a purely irrational-rotation
  argument, this sim shows that argument cannot recover the
  measured c. Revisiting the relevant section of `FIRST-PROOF.md`
  or `PNAS-PLAN.md` with this in mind would be appropriate.

## What was _not_ run

- **Test B** (per-K Fourier measurement on BS(1,2)). Skipped per
  plan's decision rule after A failed. Would have measured how
  b-step disrupts the a-only prediction — interesting but not
  necessary given A's magnitude of rejection.
- **Test C** (Binomial-weighted aggregation). Skipped; meaningless
  if H's conditional prediction doesn't even come close to
  matching the scale.

Both would become interesting again only if someone proposes a
refined hypothesis (e.g., "b-step contributes a state-independent
m-shift distribution θ_b, averaged over which gives the measured
c") that Test B could pin down. None on the table at present.

## What's saved

- `conditional_decay_results/analytic_H.npz` — TV^H, L¹^H, L²^H
  on dense n grid; per-step magnitudes; slow-mode table.

## Plan status

**CONDITIONAL-DECAY-PLAN.md terminated.** Tests B and C not run.
Hypothesis H (b-steps passive at Fourier-mode level) rejected at
the analytic gate.
