# EXPENSIVE-BEEF-BOX-SIM

## Why this plan exists

Per `T1B-EVIDENCE-MAP.md`, T1b still has a small number of genuinely
load-bearing sim soft spots. Four deliberate pressure-tests would
either harden those results substantially or reveal where they are
softer than they look. All four were previously deferred on cost or
kernel-availability grounds. The ARM M1 they would have run on is
slow enough that the expensive ones among them (the long IC(b)
anchor extension and the full M4 completion) would have taken
days-to-weeks; the others were cheap but needed small kernel work.
A beefy x86 workstation changes the cost ceiling enough that these
become tractable.

The four runs below are ordered by paper priority:

1. finish the missing full-horizon √2 anchor (`M4` to `n = 20,000`);
2. stress-test the only direct `α ≈ 1/2` anchor (M3 IC (b));
3. stress-test the dependence of IC(b)'s clean algebraic signature
   on the specific `m = log10(√2)` choice;
4. stress-test B3's low-mode truncation.

Result 5 (dyadic dichotomy, 4.2×10¹⁰ walker-steps of zero-hit
evidence) is already decisive and is not re-probed here. The
BS(1,3) cross-group idea is interesting, but it is scope expansion,
not robustness hardening for the current paper, so it is moved out
of the core beef-box list.

## Coordination note

Not part of `ALGEBRAIC-SIM-MESS-PLAN.md`'s default schedule. This
is post-`T1B-EVIDENCE-MAP.md` robustness hardening. Runs are
independent; any can be skipped without blocking the others.

Hardware assumption: x86 workstation with ≳ 64 GB RAM and ≳ 16
cores at modern clock speeds. Expected per-walker-step throughput
is 3–25× the ARM M1's 4.75×10⁶ walker-steps/s benchmark,
depending on SIMD/BLAS. Wall-time estimates below use a
conservative 10× throughput assumption (≈ 5×10⁷ walker-steps/s);
scale accordingly for faster machines.

### Pre-flight cross-validation (Step 0)

**Before any expensive run.** NumPy's trig and log functions use
libm, which can differ in the last 1–2 bits across architectures.
PCG64 RNG is deterministic across platforms by design, and the
step kernel's integer arithmetic is bit-exact. The zero-hit
dichotomy (Result 5) is the one observable where last-bit
differences could in principle change an integer count.

Procedure:

1. Re-run `run_m1_b1_b2.py` at reduced scope (N = 10⁶, n = 100) on
   the x86 machine with the existing seed. Takes ~2 min.
2. Diff the resulting L₁ trajectory and ĥ(1) against the
   corresponding small-N reference generated on the M1. Do not
   start expensive runs until that reference artifact has been
   copied to the x86 box or checked into the repo. Expect either
   bit-exact agreement or agreement at the 10⁻¹² relative level.
3. Re-run R2 (rational-with-restart) at N = 10⁵, n = 50. Check
   that the numerical zero-hit count matches within ≲ 1% of the
   M1 result. At N = 10⁵, step 1 should give about 25,000 zero-hits
   (0.25 per walker), not the 10⁷-scale count from the full R2 run.
4. Re-run `run_m0.py` at N = 10⁸ with a fresh seed. This is cheap
   and directly stress-tests the null-floor baseline that M4's late
   √2 excess is compared against.

If pre-flight passes, proceed. If pre-flight shows divergence
larger than ~10⁻⁶ on L₁ or larger than ~2% on zero-hit counts,
investigate before committing to the long runs.

Time: ~10 min total for pre-flight including the fresh-seed M0 rerun.

---

## Run 1 — FULL-M4

**Purpose.** Close the most obvious remaining hole in
`T1B-EVIDENCE-MAP.md`: M4 currently stops at `n = 3000`, and
`m4_SUMMARY.md` says that is not enough to pin down `α = 1/2`
directly on the natural √2 IC. The original ALGEBRAIC plan wanted
`n = 20,000`; this run completes that missing anchor on the better
machine.

**Spec.**

    N = 10⁸ walkers
    Symmetric measure
    IC: x = +√2  (exactly the M4 setup)
    Time range: n = 0 to 20,000
    Sampling: same M4 / ALGEBRAIC schedule
        every 10 steps to 3000, then sparse tail checkpoints
        {5000, 7000, 10000, 14000, 20000}
    Output: L₁(n), ensemble ĥ(r, n), l2_norm(n)

**Checkpoint frequency.** Save partial results every 1000 sim
steps to `run1_full_m4_results.npz.partial`, same pattern as the
current M4.

**Analysis.**

- **A1a (late √2 α-local drift).** Recompute α-local on
  `(1000, 3000)`, `(3000, 7000)`, `(7000, 20000)`. The key question
  is whether the late-window α-local values continue drifting
  downward toward 0.5 or flatten elsewhere.
- **A1b (post-transient fit).** Fit the excess above `μ_null` on
  `[3000, 20000]` and `[7000, 20000]` to `B n^{-α}`. Do not
  oversell a point estimate for `B`; the real target is whether the
  late window stabilizes enough to support `α ≈ 1/2` directly.
- **A1c (null-floor robustness).** Compare the late-window excess to
  both the original M0 null and the fresh-seed M0 rerun from Step 0.

**Decision rule.**

- Late-window α estimates stabilize near 0.5 with no strong further
  drift ⇒ the √2 IC directly supports T1b's exponent claim.
- Late-window α keeps drifting materially across `[3000, 20000]` ⇒
  √2 still does not give a direct anchor, even on the longer horizon.
- Late-window signal above null depends sensitively on which M0 seed
  is used ⇒ revisit the null-floor story before leaning on √2's late
  excess.

**Cost.**

- N = 10⁸ × n = 20,000 = 2×10¹² walker-steps. At 5×10⁷ ws/s:
  ≈ 40,000 sec = 11 hrs. Plus sampling/Fourier overhead:
  **estimate 15–20 hrs.**

---

## Run 2 — LONG-ANCHOR

**Purpose.** Pressure-test Result 1 — M3 IC (b)'s α̂ = 0.525 on
[100, 600]. This is the single direct measurement of α for T1b.
Under the worry that the 500-step window's clean log-log fit is
itself a mid-range transient, extend the same IC to the n = 20,000
horizon used for M4. If α stays at 0.52 ± a few percent out to n =
20,000, the anchor is locked. If α drifts meaningfully — to 0.4,
0.6, or curves back to a stretched-exp shape — the anchor is not
what we thought and T1b's exponent claim needs reassessment.

**Spec.**

    N = 10⁸ walkers (baseline)
        or N = 10⁹ walkers (upgrade if RAM permits; gives ~3×
        better α̂ CI via √10 lower θ_N)
    Symmetric measure
    IC: m = log₁₀√2 (delta, sharp), E ~ Uniform{−5, …, 5},
        sign = +1  (exactly the M3 IC (b) setup)
    Time range: n = 0 to 20,000
    Sampling:
        every step from n = 1 to 500 (dense, for M3-overlap)
        every 10 steps from n = 500 to 5,000
        log-spaced {7500, 10000, 14000, 20000} beyond
    Exact-zero convention: restart (defensive; should not trigger
        on this IC but kept for safety)
    Output: L₁(n), ensemble ĥ(r, n) for r = 1..5, l2_norm(n),
        per-walker return-count histogram at checkpoints
        {500, 1000, 2000, 5000, 10000, 20000} for S0 at long n.

**Checkpoint frequency.** Save partial results every 1000 sim
steps to `run2_long_anchor_results.npz.partial` so that a crash
or interruption at hour N of the run does not lose everything.
Same pattern as M4.

**Analysis.**

- **A1a (α̂ stability).** Fit log L₁ = a − α log n on moving
  windows: [100, 1000], [500, 5000], [2000, 20000]. Report α̂ per
  window with uncertainty bands. The target is *stability near 1/2*,
  not blind acceptance of a narrow box.
- **A1b (late-window S0 extension).** Compute Laplace-transform
  residuals on the return-count histogram at the added checkpoints
  (5000, 10000, 20000) and confirm c_fit ≈ 0.19 remains stable
  at longer n. This simultaneously tests Result 3 (S0) at horizons
  we haven't previously reached.
- **A1c (pure vs mixture fit).** Fit L₁(n) = A exp(−c√n) + B
  n^{−α} + noise on the full horizon. If A ≈ 0 and α = 0.5 comes
  out cleanly, IC (b) is pure algebraic. If A > 0 and c is
  measurable, there's an IC (b) transient we missed because M3
  only went to n = 600.

**Decision rule.**

- α̂ is stable near 1/2 across the three windows, with overlapping
  CIs and no systematic late drift ⇒ Result 1 is confirmed as
  asymptotic, not transient. T1b's exponent claim is materially
  hardened.
- α̂ drifts meaningfully (e.g. 0.525 early, 0.45 late, or 0.525
  early and rising) ⇒ the 500-step fit was a local slope that
  happens to be near 1/2 at intermediate n. The anchor is softer
  than currently advertised.
- Fit quality (R²) degrades at long n even though the late-window
  raw L₁ is still well above the new N = 10⁸ or 10⁹ floor ⇒
  something structural changes past ~n = 5000 (e.g., a crossover
  to another regime). Investigate before any claim extension.

**Cost.**

- N = 10⁸ × n = 20,000 = 2×10¹² walker-steps. At 5×10⁷ ws/s:
  ≈ 40,000 sec = 11 hrs. Plus ~5 hrs of sampling/Fourier overhead.
  **Estimate 15–20 hrs at baseline.**
- N = 10⁹ × n = 20,000 = 2×10¹³ walker-steps. At 5×10⁷ ws/s:
  ≈ 400,000 sec = 110 hrs ≈ 5 days. Memory: ~15 GB state + ~10
  GB working = needs ≳ 32 GB RAM.

Recommended target: N = 10⁸ first. Treat N = 10⁹ as a pure
escalation path only if N = 10⁸ still leaves α̂ too loose to
separate "stable near 1/2" from meaningful drift.

---

## Run 3 — NON-SQRT2-DELTA

**Purpose.** Pressure-test Result 1 for a specific hidden
dependency. M3 IC (b) fixes m at log₁₀√2 = ½ · log₁₀ 2, which is
a *rational* multiple of the walk's rotation quantum log₁₀ 2.
This could in principle create arithmetic resonances that produce
the clean α̂ signal as an artifact of the specific rational-
multiple structure, rather than of sharp irrationality in general.

Swap m to log₁₀ of a transcendental, an algebraic irrational
unrelated to √2, and a non-dyadic rational. If α̂ stays near the
IC (b) anchor on all three substitutions, the signal is robustly
"sharp-m, spread-E" rather than "specifically log₁₀√2." If α̂
shifts, there is structure we have not accounted for.

**Three ICs.**

| label | m value          | x₀ analog      | class               |
|:------|:-----------------|:---------------|:--------------------|
| π     | log₁₀ π ≈ 0.4971  | π              | transcendental      |
| 7/5   | log₁₀(7/5) ≈ 0.1461 | 7/5         | non-dyadic rational |
| √3    | log₁₀√3 ≈ 0.2386  | √3             | algebraic (degree 2, unrelated to √2) |

**Spec per IC.**

    N = 10⁷ walkers
    Symmetric measure
    IC: m = (the label value, as a delta), E ~ Uniform{−5, …, 5},
        sign = +1
    Time range: n = 0 to 600 (match M3 IC (b) exactly)
    Sampling: M1 grid
    Exact-zero convention: restart (should not trigger)
    Output: L₁(n), ensemble ĥ(r, n), l2_norm(n)

**Analysis.**

- **A2a (α̂ comparison).** Fit log L₁ = a − α log n on [100, 600]
  for each IC. Compare to M3 IC (b)'s α̂ = 0.525.
- **A2b (initial-L₁ matching).** Confirm L₁(1), L₁(10) are in the
  same ballpark as M3 IC (b), ruling out gross IC-sensitivity.

**Decision rule.**

- All three new m-values give α̂ near the IC (b) anchor with
  similarly strong log-log fits ⇒ sharp-m-delta + E-spread is the
  relevant recipe for seeing algebraic decay; the specific
  `log10(√2)` choice is not special.
- At least one new IC shows α̂ meaningfully different from 0.525
  (e.g. outside [0.45, 0.60]) ⇒ the clean IC (b) signature has
  some √2-specific structure. Interesting finding; needs
  theoretical investigation. Paper would shift to "α̂ depends
  on m modulo log₁₀ p" or similar.

**Cost.** 3 × (10⁷ × 600) = 1.8×10¹⁰ walker-steps. ≈ 6 min at
5×10⁷ ws/s. Add overhead: **~15 min total.**

**Optional follow-up if Run 2 lands cleanly.** Pick the most
representative non-`√2` IC from this trio and extend it to
`n = 5000` or `20000` at `N = 10⁸`. That would give a second
long-horizon algebraic anchor without having to broaden the current
core plan up front.

---

## Run 4 — HIGH-MODE-B3

**Purpose.** Pressure-test Result 2 — ρ(K̂) = 0.924 from the
empirical mode-coupling matrix. That result used a 5×5 truncation
over modes r = 1..5. The BENTHIC framework cares about the
spectral radius of the *full* operator; if the truncation is
hiding a larger spectral radius in higher modes (e.g. ρ > 0.99 or
even > 1 in some high-mode subspace), the "injection-dominated
but still contractive" story changes.

Rerun B3 with modes r = 1..20, accumulating a 20×20 empirical
K̂. Analyze spectral radius and mode-band structure.

**Spec.**

    N = 10⁷ walkers  (same as B3)
    Symmetric measure
    IC: x = +√2  (same as B3)
    Time range: n = 0 to 600
    Modes: r = 1..20  (20×20 K̂ accumulator)
    Exact-zero convention: none (√2 IC algebraically excludes 0)
    Output: K̂ (20, 20), eigenvalues (20,), spectral_radius,
        per-mode per-excursion-length statistics,
        banded-ρ analysis (ρ on r ∈ [1..5], [6..10], [11..15],
        [16..20]).

**Analysis.**

- **A3a (full ρ).** Compute ρ(K̂_20) and compare to ρ(K̂_5) = 0.924.
  If agreement to within ~0.02, truncation is harmless; the
  5×5 was a faithful summary.
- **A3b (truncation ladder).** Compute ρ for the principal
  truncations K̂_5, K̂_10, K̂_15, K̂_20. If these stabilize, the
  5-mode regime reading is robust. If ρ drifts upward with truncation
  size, the low-mode picture was incomplete.
- **A3c (banded analysis).** Extract ρ for each 5×5 diagonal
  block. If all bands have ρ < 1 and there is no hidden slow
  high-mode band, injection-dominated classification is robust.
- **A3d (singular-value structure).** Report the top 5 singular
  values of K̂_20. If σ₁ / σ₂ pattern matches the K̂_5 truncation
  structure, again harmless truncation. If high modes contribute
  new singular values comparable to σ₁, the mode coupling is
  richer than the truncation suggested.

**Decision rule.**

- ρ(K̂_20) ∈ [0.90, 0.94] and all bands have ρ < 0.95 ⇒ Result 2
  is robust. Paper can cite B3's regime classification with
  confidence.
- ρ(K̂_20) > 0.97 ⇒ the truncation masked a slower-contracting
  mode structure. The "injection-dominated but ρ < 1" story
  weakens; the walk's T_R contracts much slower than previously
  thought, potentially to the point where ρ ≈ 1 in the limit.
  Paper's B3 citation becomes less load-bearing; α = 1/2 relies
  entirely on M3 IC (b) (and Run 1's extension of it).
- ρ(K̂_20) < 0.88 ⇒ higher modes contribute *more* contraction
  (fastest rotation + most injection compensation); the 5-mode
  truncation was pessimistic. Unlikely direction but possible.

**Cost.** Same kernel as B3 but with a 20×20 complex accumulator
instead of 5×5. K̂ update per excursion scales as 20² = 400 flops
(vs 25 in B3). B3 took ~3 min for 10⁷ × 600. Estimate **5–10 min
at x86 throughput.** A secondary N = 10⁸ run to tighten CI on the
high-mode entries would cost ~50 min and be worth doing if any
high-mode ρ value comes in at the decision boundary.

---

## Output files

- `run1_full_m4_results.npz` (+ `.partial` checkpoints)
- `run2_long_anchor_results.npz` (+ `.partial` checkpoints)
- `run3_non_sqrt2_delta/{pi,seven_fifths,sqrt3}_results.npz`
- `run4_high_mode_b3_results.npz`

Per-file schemas match their respective sibling runs (Run 1 like
M4, Run 2 like a long-horizon single-IC M3 extension, Run 3 like
M3 single-IC, Run 4 like B3 with mode extension).

## Total cost

Baseline (N = 10⁸ on Runs 1–2; single IC on Runs 3–4):
- Run 1: 15–20 hrs
- Run 2: 15–20 hrs
- Run 3: ~15 min
- Run 4: ~10 min

**Total: ~32–40 hrs of sim time**, plus light analysis work. This is
still a weekend-scale queue on the x86 box if Runs 1 and 2 are
allowed to overlap or if only one of them needs escalation.

Aspirational upgrade (N = 10⁹ on Run 2 only):
- Run 2 alone: ~5 days
- All other runs unchanged

**Total: ~5–6 days of sim time** for the upgrade path.

## What this plan does NOT do

- Does not re-probe Result 5 (dyadic dichotomy). Already decisive
  at 4.2×10¹⁰ walker-steps of zero-hit evidence.
- Does not test strong asymmetry (d ≳ 0.05). The E_THRESH = 20
  kernel confound is structural; a longer run doesn't fix it.
  Would need kernel redesign (larger E_THRESH, or floating-point
  exponent handling) outside this plan's scope.
- Does not include BS(1,3) / BS(1,p) cross-group work. That is
  interesting scope expansion, but it is not robustness hardening
  for the current BS(1,2) paper and should live in a separate plan.
- Does not extend ROOT-TWO-CHECKS's R2/R3 to resolve α for dyadic
  starts. R2/R3 hit floor before α is resolvable, and extending
  their horizons runs into the same at-floor issue unless we also
  raise N substantially. Deferred as lower priority than the four
  here.
- Does not test transcendental ICs in the non-IC(b) setting
  (i.e., sharp delta m with E = 0). Run 2 tests transcendentals
  in the IC (b) structure, which is the one that resolves α;
  testing at sharp-IC structure would only reproduce M1-style
  transients. Skipped.

## Success criteria for the full plan

If all four runs land cleanly — Run 1 showing the √2 IC's late
window settling toward `α ≈ 1/2`, Run 2 showing the IC(b) anchor
stays stable near `1/2` out to `n = 20,000`, Run 3's three
alternative delta-m choices all giving the same algebraic signal,
and Run 4's `ρ(K̂)` remaining stable under mode extension — the
paper's T1b becomes substantially harder to shake inside the
BS(1,2) setting: `α = 1/2` looks asymptotic rather than transient,
not tied to the specific `log10(√2)` choice, and not an artifact of
the 5-mode B3 truncation.

If any single run falsifies or softens its target result, the
corresponding clause of T1b needs to be revisited in the paper,
but the four runs fail independently — a failure in one does not
invalidate the others.
