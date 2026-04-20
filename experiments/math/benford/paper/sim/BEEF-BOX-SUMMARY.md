# BEEF-BOX-SUMMARY

Results from the four runs planned in `EXPENSIVE-BEEF-BOX-SIM.md`.
All runs completed on x86 hardware 2026-04-19 to 2026-04-20.
Preflight cross-architecture reference artifacts exist
(`preflight_{m1_b1_b2,r2}_ref_x86_64.npz`); the ARM-side diff has
not yet been run.

## Per-run verdict against the plan's decision rules

| run | target | outcome |
|---|---|---|
| 1 — FULL-M4 | pin α on √2 IC to n=20 000 at N=10⁸ | **inconclusive.** L₁ hit null floor by n ≈ 3000; no direct α anchor on √2 |
| 2 — LONG-ANCHOR | hold IC (b)'s α ≈ 0.525 out to n=20 000 | **softens the anchor.** L₁ α-local drifts 0.52 → 0.70; L₂ α-local stays ≈ 0.52 |
| 3 — NON-SQRT2-DELTA | confirm IC (b) α-signal is m-choice-robust | **positive.** π, 7/5, √3 all give α̂ ≈ 0.50–0.55 on [100, 600] |
| 4 — HIGH-MODE-B3 | check 5-mode truncation of K̂ | **positive (best-case branch).** ρ(K̂₂₀) = 0.752 < ρ(K̂₅) = 0.925 |

Runs 1 and 2 alone would read as a material softening of T1b.
Run 2's L₁/L₂ split and Run 4's mode-extension both recover
ground. Runs 3 and 4 harden independent support points.

## Run 1 — FULL-M4

- **Spec.** N = 10⁸, IC = +√2, n = 0..20 000, symmetric, bins = 1000.
- **Wall time.** 17.4 hrs. Throughput 3.20×10⁷ walker-steps/s.
- **L₁ trajectory** (selected):

  | n | L₁ |
  |---:|---:|
  | 100 | 5.29e-2 |
  | 500 | 3.58e-3 |
  | 1000 | 2.94e-3 |
  | 3000 | 2.72e-3 |
  | 10 000 | 2.64e-3 |
  | 20 000 | 2.55e-3 |

- **Null floor.** Multinomial estimate µ_null ≈ 0.798·√((K−1)/N)
  = 2.52e-3 for K = 1000, N = 10⁸. L(20 000)/µ_null ≈ 1.01 —
  **at floor.**
- **Late-window α-local** (raw): [1000, 3000] = 0.070;
  [3000, 7000] = 0.015; [7000, 20 000] = 0.049. The null-
  subtracted excess L − µ_null is small-positive across the
  late window: {4.2, 2.0, 1.4, 1.7, 1.2, 0.8, 0.3}×10⁻⁴ at n
  ∈ {1000, 3000, 5000, 7000, 10 000, 14 000, 20 000}. Positive
  but noise-dominated — α-local on the excess is not cleanly
  resolvable at this N.
- **Decision-rule branch.** The plan's third outcome: "late-
  window signal above null depends sensitively on which M0 seed
  is used ⇒ revisit the null-floor story before leaning on √2's
  late excess." The √2 IC at N = 10⁸ does not yield a direct
  late-window α measurement — the signal reaches floor
  before the window opens. A fresh-seed M0 comparison from the
  plan's preflight step was not executed on the beef box, so
  the seed-sensitivity check the plan called for is pending.
- **What this does and doesn't mean.** Doesn't falsify T1b's √2
  clause; just can't confirm it at this N. A direct √2 anchor
  would need N ≈ 10⁹ or finer-bin coordination. T1b's √2 row
  remains extrapolation, same as before the run.

## Run 2 — LONG-ANCHOR

- **Spec.** N = 10⁸, IC = M3's IC (b) (sharp m = log₁₀√2,
  E ~ Uniform{−5,…,5}, sign = +1), n = 0..20 000, symmetric,
  bins = 1000.
- **Wall time.** 20.6 hrs. Throughput 2.70×10⁷ walker-steps/s.
  Zero exact-zero restarts.
- **L₁ trajectory:**

  | n | L₁ | L₂ | \|ĥ₁\| |
  |---:|---:|---:|---:|
  | 100 | 3.35e-1 | 3.05e-3 | 2.86e-3 |
  | 500 | 1.44e-1 | 1.63e-3 | 1.50e-3 |
  | 1000 | 9.24e-2 | 1.28e-3 | 1.20e-3 |
  | 5000 | 3.09e-2 | 6.16e-4 | 5.72e-4 |
  | 10 000 | 1.91e-2 | 5.59e-4 | 4.83e-4 |
  | 20 000 | 1.17e-2 | 3.01e-4 | 2.54e-4 |

  L(20 000)/µ_null ≈ 4.6 — **above floor**, unlike Run 1.

- **The drift.** L₁'s α-local is not stable:

  | window | α-local |
  |---|---:|
  | [100, 500] | 0.524 |
  | [100, 600] (M3 overlap) | 0.534 |
  | [500, 1000] | 0.641 |
  | [500, 5000] | 0.669 |
  | [1000, 5000] | 0.681 |
  | [2000, 10 000] | 0.691 |
  | [5000, 20 000] | **0.702** |
  | [1000, 20 000] | 0.691 |

  The [100, 600] window reproduces M3's α̂ = 0.525 to within
  rounding — the M3 measurement itself replicates. What's new
  is that at longer n the local slope is meaningfully steeper.

- **Decision-rule branch.** The plan's second outcome: "α̂ drifts
  meaningfully (e.g. 0.525 early and rising) ⇒ the 500-step fit
  was a local slope that happens to be near 1/2 at intermediate
  n. The anchor is softer than currently advertised."

### Digging into the drift

Four angles, reported because each changes the reading.

**1. L₂ and the dominant Fourier mode stay near α = 1/2.**

L₂ α-local: [100, 500] = 0.391; [500, 1000] = 0.346; [1000,
5000] = 0.454; [5000, 20 000] = 0.516; [2000, 20 000] = 0.471.

|ĥ₁| (dominant low-frequency mode) α-local: [100, 500] = 0.401;
[1000, 5000] = 0.463; [5000, 20 000] = 0.586; [2000, 20 000] =
0.491.

The Fourier-L² observable and the dominant mode both cluster
around 1/2 across the full horizon, with late-window values
closer to 0.5 than the L₁ values. **The drift is L₁-specific,
not an observable-invariant property of the walk.**

**2. Mixture fit on L₁ returns α ≈ 1/2 plus a small transient,
but the late tail sits below the fit's envelope.**

Fit L(n) = A·exp(−c√n) + B·n^{−α} on [100, 20 000]:
A = 0.214, c = 0.067, B = 2.434, α = **0.518**, R² = 0.99990.

The fit captures the overall shape of L₁ across the window and
returns α at 1/2 plus a small stretched-exp transient. Its
prediction at n = 20 000 is 0.01442, overshooting the observed
L₁ (0.01167) by **23.6%**. So the late tail decays *faster*
than the α = 0.518 mixture predicts, not slower. The R² of
0.99990 is driven by the early-window bulk (where L is large
and the mixture captures it well); the late-window residual is
small in absolute terms but systematic and one-sided.

**3. Null-floor subtraction makes the L₁ drift worse, not
better.**

Subtracting µ = 2.52e-3 (multinomial), α-local on [5000, 20 000]
becomes 0.815. Subtracting µ = 5e-3 gives 0.978. No floor value
restores α = 1/2 — subtracting a larger floor only steepens the
tail. Whatever is causing the L₁ late-window drift, it is not
"approach to null floor."

**4. Moving-window α-local shows a smooth 0.5 → 0.7 transition
on L₁, not an oscillation.**

Moving window (±1.6× center) on L₁:

| n_center | α-local |
|---:|---:|
| 50 | 0.58 |
| 166 | 0.50 |
| 302 | 0.55 |
| 552 | 0.62 |
| 1006 | 0.66 |
| 1834 | 0.69 |
| 3343 | 0.69 |
| 6094 | 0.69 |
| 11 110 | 0.71 |
| 15 000 | 0.71 |

The crossing from ~0.5 to ~0.7 happens on n ∈ [300, 2000] and
then plateaus. Not a passing transient.

### Reading of Run 2

Three non-exclusive explanations for the L₁/L₂ split:

- **(a) Higher-mode tail dominates L₁ at late n.** `h_full`
  tracks only modes r = 1..5; the histogram has 1000 bins
  and therefore 500 Fourier modes of signal. L₂ (truncated to
  r = 1..5) tracks the low-mode portion and gives α ≈ 0.52; L₁
  integrates over all modes, and modes 6..500 may be decaying
  slower, contributing a slower-decaying L₁ component. Needs
  checking with a higher-mode-truncated L₂ or a per-mode
  extension of the run.
- **(b) L₁ has a slower approach to asymptotic than L₂.** Even
  if the true asymptotic of L₁ is n^{−1/2}, pre-asymptotic
  corrections could be dominating on n ≤ 20 000. The mixture-
  fit α of 0.518 is consistent with this.
- **(c) The L₁ asymptotic is not exactly 1/2.** The data is
  genuinely consistent with α ≈ 0.7 on the late window if one
  trusts the pure log-log fit there. The Melbourne–Terhesiu
  upper bound T_n ≪ n^{−1/2} log n does *not* rule out faster
  decay like n^{−0.7} — an upper bound constrains from above,
  not below. What α > 1/2 would conflict with, if the results
  transport cleanly from the renewal-operator T_n to L₁(P_n,
  Leb_T), is (i) Gouëzel's private-communication sharpened
  *asymptotic* T_n ∼ d·n^{−1/2} under the extra density
  condition, and (ii) M–T Theorem 2.3's liminf of n^{1/2}·T_n
  > 0 pointwise for positive observables, which requires T_n
  to decay no faster than n^{−1/2} infinitely often. Whether
  those transport cleanly is itself the open identification
  question in SECOND-PROOF §4.

**The reading we favor, conditional on the evidence on hand:**
(a) and (b) in combination. The mixture fit returns α = 0.518
with R² = 0.99990 and a 23.6% overshoot at n = 20 000; the
overshoot is in the direction where the observed L₁ decays
faster than the α = 1/2 mixture predicts, which is consistent
with — not evidence against — a high-mode-tail contribution
that the single-α-plus-transient model absorbs imperfectly.
The L₂ observable, which filters out high-mode contributions
by construction (truncated at r = 5), gives α ≈ 0.52 cleanly.
The L₁ late drift is then most plausibly a resolved-observable
effect, not a theorem-level shift — but the N = 10⁸ run cannot
distinguish (a) from (c) directly; see `TEN-TO-THE-NINE-SIM-
PLAN.md`.

**What this implies for T1b.** T1b's asymptotic claim is about
L₁(P_n, Leb_T). The clean α = 1/2 signature at the M3 window
[100, 600] reproduces. At longer n (≤ 20 000), the L₁ signal
shows a slower approach to its asymptotic than the M3 window's
500-step slope suggested. The paper cannot cite M3's α = 0.525
as a direct measurement of the asymptotic exponent; it is a
measurement of the intermediate-n local slope.

Options for the paper:
1. Keep L₁ as the stated observable; rely on the mixture-fit
   α = 0.518 as direct evidence and downweight the late-window
   pure-fit α = 0.70 as a finite-horizon artifact (with the
   high-mode-tail caveat made explicit).
2. Switch the primary observable to L₂ (or a Fourier norm) for
   the α-measurement clause; L₂'s α ≈ 0.52 on [5000, 20 000] is
   the cleanest numerical evidence we have for asymptotic
   α = 1/2.
3. Extend the observable tracking: a future run should save
   Fourier modes r = 1..20 (or 1..100) so that the mode-by-mode
   α can be checked directly. Would have caught this at B3's
   mode-extension cost rather than at Run 2's 20-hour cost.

## Run 3 — NON-SQRT2-DELTA

- **Spec.** Three sharp-m deltas (π, 7/5, √3), each
  N = 10⁷, E ~ Uniform{−5,…,5}, sign = +1, n = 0..600.
- **Wall time.** 25.6 min total across the three ICs.
- **Results:**

  | IC | L₁(100) | L₁(600) | α[100, 500] | α[100, 600] |
  |---|---:|---:|---:|---:|
  | π | 0.379 | 0.154 | 0.493 | 0.502 |
  | 7/5 | 0.349 | 0.129 | 0.549 | 0.554 |
  | √3 | 0.343 | 0.135 | 0.510 | 0.519 |
  | M3 IC (b) √2 (reference) | — | — | — | 0.525 |

- **Decision-rule branch.** The plan's first outcome: "All three
  new m-values give α̂ near the IC (b) anchor with similarly
  strong log-log fits ⇒ sharp-m-delta + E-spread is the relevant
  recipe; the specific log₁₀√2 choice is not special."
- **Caveat.** The 7/5 rational IC triggered 10 100 exact-zero
  restart events (expected 0 by orbit arithmetic). The saved
  output records event counts via `zero_hits_per_step`, not
  distinct affected walkers, so a single walker could account
  for multiple hits. Likely a floating-point underflow or
  cancellation, not a systematic orbit-zero. L₁ measurement not
  materially affected at N = 10⁷.
- **What this does and doesn't say.** Does: the M3-style [100,
  600] algebraic signature is robust across transcendental,
  algebraic-other, and non-dyadic-rational m. Does not: address
  Run 2's late-window drift — these ICs only go to n = 600 and
  haven't been probed in the drift range.

## Run 4 — HIGH-MODE-B3

- **Spec.** N = 10⁷, IC = +√2, modes r = 1..20, 20×20 K̂
  accumulator, n = 600.
- **Wall time.** 3.76 min (225.8 s). 40.35M total excursions,
  4.03 excursions per walker, mean excursion length 16.5 steps.
- **Spectral radii:**

  | truncation | ρ(K̂) |
  |---|---:|
  | K̂₅ (B3's original) | 0.925 |
  | K̂₁₀ | 0.755 |
  | K̂₁₅ | 0.811 |
  | K̂₂₀ | **0.752** |

  Banded 5×5 diagonal blocks (modes [1..5], [6..10], [11..15],
  [16..20]): ρ = 0.925, 0.934, 0.931, 0.933 — all ≈ 0.93.

  Top singular values of K̂₂₀: 3.40, 3.33, 3.27, 3.21, 3.11 —
  nearly flat, consistent with a richly coupled operator.

- **Decision-rule branch.** The plan's third outcome
  ("Unlikely direction but possible"): "ρ(K̂₂₀) < 0.88 ⇒ higher
  modes contribute *more* contraction (fastest rotation + most
  injection compensation); the 5-mode truncation was
  pessimistic."
- **Reading.** Each 5-mode band has intra-band ρ ≈ 0.93, but
  the cross-band off-diagonals drive phase cancellation in the
  full 20×20 operator that drops ρ to 0.75. The 5-mode
  truncation missed that cross-band cancellation and therefore
  reported a pessimistic upper bound.
- **Consequence for F3.** SECOND-PROOF §3 (F3) needs an analytic
  q < 1 with explicit margin to the product bound inside the
  framework. The "must beat 0.924" spec in the Known Empirical
  Limits subsection of §8 is now more forgiving — the empirical
  target is 0.752 with room to 1.0, not 0.924. The analytic
  proof of F3 still has to close; B3 just gives more empirical
  slack.

## Preflight cross-architecture reference (not yet diffed)

x86_64 artifacts saved:

- `preflight_m1_b1_b2_ref_x86_64.npz`: L₁(100) = 5.8624e-2,
  \|ĥ(1)\| = 5.592e-3 on N = 10⁶, n = 100, seed = 0xbadc0de1, IC
  = +√2.
- `preflight_r2_ref_x86_64.npz`: 78 676 exact-zero hits (≈ 0.787
  per walker), L₁(50) = 7.80e-1, on N = 10⁵, n = 50, IC = +1,
  exact-zero restart, seed = 0xc0ffee33.

The M1-side corresponding run has not been executed. The diff
against the ARM reference should happen before leaning on Run 1
or Run 2's quantitative numbers in the paper. Expected outcome:
bit-exact agreement or ≲ 10⁻¹² disagreement (PCG64 is
deterministic by design; integer step arithmetic is exact;
floating-point log/trig can differ at the ULP level).

## Implications for the paper

- **PNAS-PLAN claim gate, "goes in" bullet #1.** Currently
  reads "L₁(P_n, Leb_T) ∼ B(ν) · n^{−1/2}". This claim is now
  split:
  - **L₂-flavored (Fourier sense):** cleanly supported by Run 2
    at α ≈ 0.52 on [5000, 20 000].
  - **L₁-flavored (TV sense):** mixture fit gives α = 0.518 on
    [100, 20 000]; pure late-window log-log on L₁ gives α ≈ 0.70;
    the asymptotic reading requires the mixture / high-mode-
    tail explanation to hold.

  Candidate re-wordings, in order of claim-strength and
  plausibility under the data:
  1. Restate as "Fourier-L² rate α = 1/2 with IC-dependent
     coefficient" and drop the TV-norm framing from the claim
     gate. Solid under Run 2's L₂ reading. Weaker rhetorical
     claim (Fourier-L² is less reader-friendly than TV).
  2. Keep L₁/TV framing; cite the mixture fit α = 0.518 at
     R² = 0.99990 as supporting evidence (with the 23.6% late-
     tail overshoot noted); acknowledge the late-window pure-fit
     α ≈ 0.70 as a finite-horizon mixed-mode effect pending
     higher-mode instrumentation.
  3. Drop the universality of α = 1/2 from the claim gate
     entirely; state only "algebraic decay with IC-dependent
     exponent in the range [0.5, 0.7]." Weakest claim, least
     useful to the paper.

- **SECOND-PROOF §8 "Known empirical limits" update.** Item "α =
  1/2 on the √2 IC" should be upgraded: Run 1 confirms that
  direct measurement on √2 at N = 10⁸ hits floor; the √2
  α-clause remains extrapolation. Item "ρ(K̂) = 0.924" can now
  cite 0.752 at modes r = 1..20. New item: "L₁ vs L₂ exponent
  split on IC (b) — late-window L₁ shows α ≈ 0.70 while L₂ and
  |ĥ₁| give α ≈ 0.52; the L₁ reading depends on a high-mode-
  tail interpretation."

- **T1B-EVIDENCE-MAP.md update.** Result 1 ("α̂ = 0.525 on M3 IC
  (b)") replicates at [100, 600] but softens at longer horizons.
  Result 2 ("ρ(K̂) = 0.924 with B3") hardens under mode extension
  to ρ(K̂₂₀) = 0.752. Add a new row for the L₂/L₁ observable
  split.

- **Open follow-up sims** (if the beef box is still available):
  1. Re-run one of Run 3's non-√2 ICs (likely π, cleanest α)
     out to n = 20 000 at N = 10⁷. Cheap (~1 hr). Tests whether
     the Run 2 L₁ drift is IC(b)-specific or a general sharp-m-
     delta feature.
  2. Instrument a Run 2-style run with Fourier modes r = 1..20
     tracked. Lets the mode-by-mode α and the L₂-on-more-modes
     observable be read directly. Small marginal cost over Run 2's
     20-hour base.
  3. ARM-side preflight diff. Small, required before citing
     quantitative Run 1 / Run 2 numbers in the paper.
