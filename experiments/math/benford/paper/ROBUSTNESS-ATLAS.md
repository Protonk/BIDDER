# ROBUSTNESS-ATLAS

Paper-side summary for PNAS-PLAN §7 "Robustness and sensitivity."
Each bullet states what the current evidence actually supports
and what it does not. These points are not load-bearing for
Theorem 1.

## Scope

PNAS-PLAN §7 carries four strands: biased generators, base
change, pure addition, and precision. The evidence below is
uneven across them. Two strands rely partly on older material in
`experiments/math/benford/`, so this atlas is the paper-side
bridge to those sources.

## Bullet 1: Tested bias perturbations do not show a visible breakdown

**Claim.** The current runs do not show a visible failure of the
Benford phenomenon under two tested symmetry-breaking
perturbations: weak asymmetry on the T1b observable window, and
one strong positive-drift phase-3 run on a long horizon. This is
supportive robustness evidence, not a theorem-scale biased-case
result.

**Evidence.**

- **Weak asymmetry** (d = 0.01). T1B-UNIT-BALL Run 2: L₁ ratio
  asym/sym ∈ [0.96, 1.06] over [1, 600]; transient c_hat
  differs by 0.7%. Source: `sim/T1B-EVIDENCE-MAP.md` clause (v)
  and `sim/t1b_unit_ball_SUMMARY.md`. Addresses the
  "observable-window close to symmetric" end of the claim.

- **Strong asymmetry / phase-3 bias** (net multiplicative drift
  +0.20 per step, weights (0.2, 0.2, 0.4, 0.2) on
  {b, b⁻¹, a, a⁻¹}). In that run, L₁ reaches the N = 10⁶
  noise floor ≈ 0.013 by t ≈ 2000 and stays there through
  t = 50 000. The recorded shape is two-stage:
  active fraction collapses 100% → 0% in t ∈ [500, 1000] as
  walkers drift to |E| > 20; post-escape L₁-above-floor decays
  roughly as 1/t. Source: `sim/SIM-REPORT.md` §"Phase 3 —
  biased BS(1,2), convergence shape" (lines 54–112); script
  `experiments/math/benford/gap3_phase3.py`; data
  `experiments/math/benford/data/gap3_phase3.{csv,npz}`;
  figure `experiments/math/benford/fig/gap3_biased.png`.

**Caveats.** The phase-3 run is one bias vector, in the positive
drift direction, using the older `|E| > 20` freeze/snap
approximation. Its late-time rate fits are unreliable because the
curve is already at floor. So the safe paper-side statement is
only that this tested positive-drift run does not exhibit the old
claimed floor at 0.091 and does relax to the noise floor on the
recorded horizon. The negative-drift direction is untested.

## Bullet 2: Base-scan fingerprint is flat on the tested range

**Claim.** On the scanned range b ∈ [2, 40], the final-step
BS(1,2) ensemble fingerprint is visually flat as a function of
base. This supports a base-insensitivity claim for that finite
ensemble diagnostic. It is not a proof that the full walk has the
same asymptotic behavior for every base b > 1.

**Evidence.** `experiments/math/benford/base_fingerprint.py`
sweeps b ∈ [2, 40] continuously (381 values) on final-step
ensembles of `bs12_walk`, `bs12_biased`, and `pure_add`. The
`bs12_walk` and `bs12_biased` curves are visually flat across
the scan. Figure:
`experiments/math/benford/base_fingerprint.png`. Reuses data
from `data_bs12_walk.npz`, `data_bs12_biased.npz`,
`data_pure_add.npz`.

**Caveats.** This is a one-horizon ensemble diagnostic, not a
base-by-base convergence study. The theoretical sentence
"log_b 2 is irrational for every integer b > 1" would be false
(for example b = 2, 4, 8). So the atlas should stay with the
empirical scan itself. The `pure_add` rise in the same sweep is
best read as an ensemble-width artifact, not a resonance claim.

## Bullet 3: Pure addition — non-convergence

**Claim.** Removing multiplication entirely (pure additive walk
on ℤ) does not produce visible Benford convergence on the
observable horizon explored here.

**Evidence.** `sim/comparison_walks_SUMMARY.md` — pure-additive
run at N = 10⁶, n = 10⁴, same √2 IC as BS(1,2). L₁ stays at
≈ 1.88 at n = 600 and 1.57 at n = 10⁴; log-log slope −0.057.
Extrapolation to the N = 10⁸ noise floor gives n ≈ 10⁵¹.
Same substrate as `paper/FIG1-SUBSTRATE.md`'s pure-add curve.

**Caveats.** The paper-side claim here is only observable-horizon
non-convergence. This note is not the place to make a separate
asymptotic theorem claim about pure addition.

## Bullet 4: Precision robustness — fp64 sufficient

**Claim.** For the T1b ensemble observables actually used in the
paper, fp64 appears sufficient. Finer precision (fp128) matches
fp64 on the tested anchor, while coarser precisions show the
expected ε-scale roundoff events.

**Evidence.** `sim/T1B-EVIDENCE-MAP.md` clause (iv) + the
fp-ladder summaries (`sim/fp16_SUMMARY.md`,
`sim/fp32_SUMMARY.md`, `sim/fp128_SUMMARY.md`). Measured
precision-induced zero-hit rates (synthesized ladder in
`sim/fp16_SUMMARY.md`): fp16 ≈ 2×10⁻⁵, fp32 ≈ 1.5×10⁻⁹,
fp64 below detection (< few × 10⁻¹¹), fp128 bit-exactly
identical L₁ and α̂ to fp64 at matched RNG seed on M3 IC (b).
Three-point fp16/32/64 line is linear in fp_eps, consistent
with catastrophic-cancellation mechanism for the
orbit-reaches-0 algebraic event.

**Caveats.** Precision robustness is tested on the ensemble
observables the paper reports, not on exact per-walker dynamics.
It also does not cover every older robustness run; in particular,
the strong-asymmetry phase-3 run and much longer horizons lie
outside the direct fp-ladder evidence.

## What §7 can and cannot say

**Can safely state:**

- The tested biased perturbations do not show visible breakdown
  on the recorded horizons: weak asymmetry stays close to the
  symmetric window, and one strong positive-drift run shows a
  two-stage relaxation to the noise floor.
- The scanned base fingerprint is flat across b ∈ [2, 40] for
  the BS(1,2) final-step ensembles we checked.
- Pure addition alone does not converge on any empirically
  relevant horizon.
- fp64 is precision-sufficient for the ensemble observables
  the paper relies on.

**Should not overclaim:**

- Generic "biased generators converge" wording. What we have is a
  weak-asymmetry envelope check plus one strong positive-drift
  long-horizon run.
- The phase-3 run's precise post-escape rate. Qualitative
  two-stage shape only.
- Base-universality phrased as a theorem. The base-fingerprint
  result is "flat across the scan," not a proof for every b > 1.
- Pure-addition non-convergence as an asymptotic statement.
  Observable-horizon only.
- Cross-precision invariance beyond T1b observables. Per-walker
  dynamics drift at 10⁻¹⁵; ensemble observables don't.

## Evidence-location note

Two of the four robustness strands live in
`experiments/math/benford/` rather than `sim/`:

- Phase-3 biased-generator run:
  `experiments/math/benford/gap3_phase3.py`,
  `sim/SIM-REPORT.md` §Phase 3.
- Base-fingerprint sweep:
  `experiments/math/benford/base_fingerprint.py`.

These are not in `sim/T1B-EVIDENCE-MAP.md`'s inventory (which
covers only T1b-era BS(1,2) full-kernel runs). The paper-side
citation chain for §7 therefore has to go outside the map.
This atlas is the one place that collects those pointers.

## References

### Primary sources

- `sim/SIM-REPORT.md` — §Phase 3 biased-generator write-up.
- `sim/T1B-EVIDENCE-MAP.md` — clause (v) weak asymmetry,
  clause (iv) precision ladder.
- `sim/t1b_unit_ball_SUMMARY.md` — weak-asymmetry Run 2
  numerics.
- `sim/comparison_walks_SUMMARY.md` — pure-add curve.
- `sim/fp16_SUMMARY.md`, `sim/fp32_SUMMARY.md`,
  `sim/fp128_SUMMARY.md` — precision ladder.

### Scripts and data outside sim/

- `experiments/math/benford/gap3_phase3.py` — phase-3 biased
  run.
- `experiments/math/benford/data/gap3_phase3.{csv,npz}` —
  phase-3 data.
- `experiments/math/benford/fig/gap3_biased.png` — two-panel
  figure.
- `experiments/math/benford/base_fingerprint.py` — base sweep.
- `experiments/math/benford/base_fingerprint.png` — base-sweep
  figure.

### Paper-side companions

- `paper/T1B-EVIDENCE.md` — theorem-anchor evidence (Theorem 1,
  Theorem 2, §4 mechanism).
- `paper/FIG1-SUBSTRATE.md` — Figure 1 three-walks substrate
  (shares data with pure-addition bullet above).
- `paper/ALT-SLOWDOWN-MECHANISM.md` — §6 kicker footnote
  material.
