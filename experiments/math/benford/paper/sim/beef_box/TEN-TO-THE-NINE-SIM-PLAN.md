# TEN-TO-THE-NINE-SIM-PLAN

One run. One goal.

## Goal

Resolve the L₁ α-local drift on IC (b) from `BEEF-BOX-SUMMARY.md`
Run 2. At N = 10⁸, L₁ α-local drifts from 0.52 on [100, 500]
(matching M3) to 0.70 on [5000, 20 000], while L₂ on modes
r = 1..5 and |ĥ₁| individually stay near 0.52. Three readings
to distinguish:

- **(a) High-Fourier-mode contribution.** Modes r > 5 contribute
  materially to L₁ and decay *faster* than modes r ≤ 5 at the
  available horizon. Because L₁'s late-window α (≈ 0.70)
  exceeds the dominant-low-mode α (≈ 0.52), whatever high-mode
  contribution drives the L₁ drift must itself decay at α > 0.5
  — a slower-decaying tail would pull L₁'s apparent α *down*,
  not up. Reading (a) preserves T1b cleanly: modes 1..5 carry
  the long-run n^{−1/2}, high modes fall out by n much greater
  than 20 000.
- **(b) L₁ pre-asymptotic slowdown.** L₁'s approach to its own
  n^{−1/2} asymptotic is slower than modes r = 1..5 in Fourier
  norm. α-local on L₁ is still in pre-asymptotic on [5000,
  20 000] and will roll back to 1/2 at n ≫ 20 000.
- **(c) Different L₁ asymptotic.** The true L₁ asymptotic
  exponent is not 1/2. The M3 window's α ≈ 0.525 was an
  intermediate-n local slope; the asymptotic is some α > 1/2.
  Melbourne–Terhesiu's Theorem 2.2(a) *upper* bound
  T_n ≪ n^{−1/2} log n does not rule this out; upper bounds
  constrain from above, not below. What α > 1/2 on L₁ would
  conflict with is M–T Theorem 2.3's positive-observable liminf
  at the n^{−1/2} scale and Gouëzel's sharpened asymptotic,
  *if* those transport cleanly from the renewal-operator T_n
  to L₁(P_n, Leb_T). That transport is SECOND-PROOF §4's open
  identification question.

Reading (a) preserves T1b. Reading (b) preserves T1b but
softens its empirical anchor. Reading (c) motivates a
framework-level investigation.

## What went wrong with the aborted N = 10⁹ attempt

`logs/run2_N1e9_aborted.log` shows the straight-port of Run 2
to N = 10⁹ with r = 1..5 and the same 954-sample cadence
projected 767–856 hours (≈ 32–36 days) wall time. The dominant
cost was the per-sample Fourier pass (`run2_long_anchor.py`
`compute_fourier` at lines 184–200): trig evaluations scale as
R × N per sample, and at R = 5, N = 10⁹, 954 samples this is
~5×10¹² trig calls — larger than the walker-step cost itself.

Going to R = 20 as originally planned here would have made it
worse by 4×. That framing was the critique's main structural
objection and is now discarded.

## The run (revised)

**Single run** targeting IC (b)'s long-horizon behavior with
full 1000-bin histogram saved at each sample time; all Fourier
analysis happens post-hoc from the saved histograms.

    N           = 1,000,000,000
    IC          = M3 IC (b): sharp m = log₁₀√2,
                  E ~ Uniform{−5..5}, sign = +1
    Time range  = n = 0 to 20,000
    Bins        = 1000
    Seed        = 0xee1c3a73  (the Run 2 seed, unchanged)
    Exact-zero  = restart (defensive; should not trigger)
    Symmetric measure on {a, a⁻¹, b, b⁻¹}

**Per-sample output** — changed from Run 2:

- `histogram_full[s, b]` — int32 or int64, shape
  (n_samples, 1000). Full 1000-bin histogram at each sample
  time. Allows post-hoc DFT to extract all 500 discrete Fourier
  modes of the binned observable.
- `l1[s]` — float64, L₁(P_n, Leb_T) computed during the run
  from the histogram (cheap; avoids any redo later).
- `sample_times[s]` — int32.
- Run metadata (N, seed, steps, bins, IC).

**Dropped vs Run 2:**

- No per-sample `compute_fourier` call. Fourier is done post-
  hoc on the saved histogram at negligible cost. **This is what
  makes N = 10⁹ feasible.**
- No return-count histograms (`rc_checkpoints`,
  `rc_histograms`). Not load-bearing for this run's goal.
- No per-step `zero_hits_per_step` accumulator. Keep a single
  cumulative counter only.

**Sample schedule** — cut from Run 2's 954 to ~50 log-spaced
points:

- Dense enough in [100, 600] for the M3-window cross-check.
- Enough points across [500, 20 000] for moving-window α-local
  (±1.6× window → need ~12 points per decade).
- Concretely: a log-spaced grid of ~50 points over
  [10, 20 000] with explicit anchors at
  {100, 200, 400, 500, 600, 1000, 2000, 5000, 10 000, 20 000}
  for direct comparison to Run 2's key-times table.

## Cost (evidence-based)

- **Walker-step work.** Run 2 at N = 10⁸ with 954-sample
  Fourier was 20.6 hrs; subtracting the Fourier pass (the
  dominant cost) gives walker-steps alone at ~30–40% of that.
  Scaling to N = 10⁹ linearly (and accounting for memory-
  bandwidth effects visible at 13 GB state): walker-steps at
  N = 10⁹ without Fourier should be 3–5 days. **Budget 4 days,
  ceiling 6 days.**
- **Storage.** 50 samples × 1000 bins × 8 B = 400 kB for the
  histogram grid. Trivial.
- **Sample-pass cost.** Per sample: histogram accumulation (one
  pass over the walker array) ~ 40 GB memory traffic at N = 10⁹,
  ≲ 1 s at modern DRAM bandwidth. 50 samples × 1 s = 50 s
  total. Negligible.
- **RAM.** Walker state is 13 GB at N = 10⁹. The per-step
  `step_b_restart` temporaries (`run2_long_anchor.py:116–162`)
  — `log_mag`, `x`, `x_new`, `log_abs`, `new_E`, `new_m`
  arrays at the active-branch fraction of N, plus the `choice`
  and mask arrays from `step_walkers` at lines 165–171 —
  are what drove Run 2's peak to ~30–35 GB (recorded in
  `launch.sh:98`). Dropping the 5 GB return-count bookkeeping
  helps but does not remove the step-level temporaries.
  **Needs ≥ 32 GB free RAM**, and no other heavy process on
  the box while the run is live. The 64 GB beef box can
  co-run a Run-1-sized 3 GB workload but not much else.

The 35-day aborted projection does not reapply because it was
dominated by a component (per-sample Fourier) that this run
removes.

## Preflight

- **Benchmark (required, gating).** Before committing the 4-day
  budget, run the revised histogram-only kernel at a real
  scale:

      N = 10⁸, n = 2000, bins = 1000
      sample schedule = the full 50-point log-spaced grid

  Measure sustained walker-steps/sec, peak resident-set-size,
  total wall time. Extrapolate to the N = 10⁹ × n = 20 000
  target linearly in N × n, with a margin factor for memory-
  bandwidth effects that kick in above the 13 GB walker-state
  threshold.

  **Launch gate:** proceed to the long run only if

  1. extrapolated wall time ≤ 6 days;
  2. extrapolated peak RSS ≤ 40 GB (under the 64 GB ceiling
     with margin for OS and monitoring);
  3. L₁(n) trajectory at N = 10⁸, n = 2000 matches Run 2's at
     matching n to within the N = 10⁸-vs-10⁸ multinomial
     spread (sanity-check correctness of the revised kernel).

  Expected benchmark wall time: 10–30 min. The 4-day budget in
  this document is *extrapolated*, not measured — the aborted
  10⁹ log gives a negative constraint (what not to do) and
  removing per-sample Fourier gives a direction of improvement,
  but there is no measured steps/sec for the revised kernel at
  N = 10⁹. Skipping this benchmark means launching a 4-day run
  on an untested cost estimate. Don't.

- **Cross-architecture diff (optional, not gating).** The
  existing x86 references `preflight_{m1_b1_b2,r2}_ref_x86_64.npz`
  can still be checked against an ARM-side M1 run if one is
  available. This is not gating for the N = 10⁹ run because
  the run itself executes on the same x86 box. The cross-arch
  diff is for paper-level numerical reproducibility claims —
  separate concern.

## Post-hoc analysis

All analyses operate on the single output
`run1e9_histogram_anchor_results.npz`. No per-sample Fourier
was stored; all Fourier quantities are computed by DFT of the
saved histograms.

**A1 — DFT the histograms.** Compute |ĥ(r, n)| for r = 1..500
at each sample n. Identify signal-dominated modes (those with
|ĥ(r, n)| persistently above the N = 10⁹ shot-noise floor
1/√N ≈ 3.16×10⁻⁵). At lower amplitudes, per-mode α is
noise-dominated and uninformative.

**A2 — Per-mode α-local.** For each signal-dominated mode r,
compute α-local on [100, 500], [500, 5000], [5000, 20 000],
[2000, 20 000]. Tabulate.

**A3 — L₂ with extended truncation.** Compute
L₂(k, n) := √(Σ_{r=1..k} |ĥ(r, n)|²) for
k ∈ {5, 10, 20, 50, 100, 499}. Fit α-local on the same windows.
(L₂ is fine to k = 500 as a sum of squared magnitudes, but
capping at 499 keeps A3 and A4 on the same truncation grid.)

**A4 — L₁ of truncated reconstruction.** For each k, reconstruct
p̂_k(m, n) = 1 + 2·Σ_{r=1..k} Re(ĥ(r, n)·e^{2πi r m}) on a 1000-
point m-grid (the histogram bin centers), and compute
L₁(p̂_k, 1)(n) := (1/1000)·Σ_{bin b} |p̂_k(m_b, n) − 1|. Use
k ∈ {5, 10, 20, 50, 100, 499} and fit α-local as a function of
k.

For a 1000-bin real histogram, r = 500 is the Nyquist mode and
appears once in the DFT rather than as part of a conjugate
pair. The `1 + 2·Σ Re(...)` reconstruction formula with factor
2 is valid for r ≤ 499 only; cap k at 499 to avoid the special
case. The discarded r = 500 contribution is a real-valued mode
at the finest scale the binning resolves and does not change
the diagnostic.

L₁ is not additive across Fourier bands, and partial Fourier
sums are not monotone in k either — L₁(p̂_k, 1) can rise or
fall as k grows depending on which modes get added. What the
diagnostic tests is the *trend* in α-local of L₁(p̂_k) across a
span of k values, not a monotone ordering. The reconstruction
does converge to the full binned L₁ as k → 499.

**A5 — Mixture re-fit.** Refit `L₁ = A·exp(−c√n) + B·n^{−α}` on
[100, 20 000]. The Run 2 baseline is A = 0.214, c = 0.067,
B = 2.434, α = 0.518, R² = 0.99990, with a 23.6% overshoot at
n = 20 000 (see BEEF-BOX-SUMMARY.md). The N = 10⁹ tail is
~3× better resolved relative to floor than Run 2's; the refit
either tightens around α = 1/2 with a smaller overshoot
(readings (a) and (b)) or forces α well above 1/2 with no
plausible transient (reading (c)).

**A6 — M3 window cross-check.** α-local on [100, 600]. Should
reproduce Run 2's 0.534 (which reproduced M3's 0.525) if the
walk and IC are unchanged. Sanity check, not a main
discriminant.

## Decision rules (corrected sign logic)

**Reading (a) — HIGH-MODE CONTRIBUTION**, signature:

- L₁(p̂_k) α-local shows a clear upward *trend* with k on the
  late window [5000, 20 000] — materially larger at k ∈
  {100, 499} than at k = 5 (say, ≥ 0.10 above the k = 5 value).
  Strict monotonicity in k is not required.
- L₂(k) α-local shows the same upward trend on the late window:
  L₂(5) ≈ 0.52, L₂(100) or L₂(499) closer to L₁'s value.
- The per-mode signal-dominated modes with r > 5 have α_r
  *higher* than α_r for r ∈ 1..5. (A slower-decaying tail
  would push the combined observable toward *smaller* α, not
  larger.)
- Mixture refit of L₁ lands near α = 0.5 with a smaller
  residual overshoot than Run 2's 23.6%, because the high-mode
  contribution that L₁ integrates is better resolved.

**T1b survives as stated.** Paper either commits to Fourier
norm on modes 1..R (for small fixed R) as the observable for
the asymptotic claim, or sticks with L₁/TV and treats the late-
window α > 1/2 as a finite-horizon mixed-mode effect.

**Reading (b) — L₁ SLOW APPROACH**, signature:

- L₁(p̂_k) α-local is flat in k across the late window: every
  truncation shows the same ≈ 0.70 late slope.
- L₂(k) α-local is flat in k (≈ 0.52) because modes 1..5 carry
  most of L₂ at every truncation anyway.
- Per-mode α for every signal-dominated mode is ≈ 0.5.
- Mixture fit on L₁ recovers α = 0.5 with a smaller overshoot
  and shorter implied transient horizon.

**T1b survives.** The late-window L₁ drift is a pre-asymptotic
feature without a clean mode-level explanation. Paper wording
sticks with the mixture-fit evidence and acknowledges the
pre-asymptotic.

**Reading (c) — ASYMPTOTIC ≠ 1/2**, signature:

- Per-mode α-local for all signal-dominated modes bunches around
  0.7, not 0.5.
- L₁(p̂_k) α-local is ≈ 0.70 for all k including small k.
- L₂(k) α-local is ≈ 0.70 even at k = 5 (i.e., what looked like
  0.52 at N = 10⁸ was itself a pre-asymptotic artifact).
- Mixture fit cannot recover α = 0.5 without unphysical
  transient parameters.

**T1b as stated is wrong.** Paper claim gate rewrites, SECOND-
PROOF §2 theorem statement revises to report the observed α,
and the mismatch with M–T Theorem 2.3 / Gouëzel's sharpened
asymptotic becomes a framework-level investigation question
under SECOND-PROOF §3 + §4.

## Checkpointing

Save partial results to
`run1e9_histogram_anchor_results.npz.partial` every 1000 sim
steps (histograms accumulated-so-far + L₁ trajectory). A crash
at hour 40 of a 4-day run must not lose the early trajectory.
The partial file at n ≥ 5000 (≈ 25 hrs in) already covers the
M3 window and early late-window and distinguishes reading (c)
from the others even if the run doesn't complete.

## Scope

- **Does not** re-probe Run 1 (√2 IC α direct measurement). The
  √2 null-floor-sensitivity question is separate.
- **Does not** test non-IC (b) deltas at the long horizon.
  Run 3 was positive at n = 600 for π, 7/5, √3; whether they
  drift like IC (b) is a cheap ~1-hour follow-up at N = 10⁷.
- **Does not** extend B3. Run 4 already gave ρ(K̂₂₀) = 0.752.
- **Does not** test BS(1, p) for p ≠ 2, biased measure, or
  alternative R windows.

## Success criterion

The run succeeds if the signature among (a), (b), (c) is
unambiguous — i.e., the L₁(p̂_k) α-vs-k trajectory and the
per-mode α table make one of the three branches obviously
right and the other two obviously wrong.

The run is not claimed to prove α = 1/2; it is claimed to
identify the L₁ drift's source. Each of the three outcomes is
a definitive update to the paper's evidence map.
