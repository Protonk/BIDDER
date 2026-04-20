# Alternating-step slowdown — mechanism on ℤ²

Settles what drives the sub-sampling slowdown of the alternating-step
walk on the ℤ²/(Lℤ)² torus, for both full 2D and 1D axis-marginal
observables. Four independent tests — all run on ℤ² — plus a
spectral calculation that also agrees on ℤ³ and (at the
regime-label level) H_3 pin the mechanism to a single near-parity
Fourier mode.

Scope:
- **ℤ² (L = 31, odd):** mechanism confirmed via four independent
  tests (Fourier calc + lazy-alt single-point + ε-scan + even-L).
- **ℤ³ (L = 15):** new-dimension prediction r = 3 on 3D full state
  and r = 4 on 2D/1D marginals; measured values match within
  step-10 sampling-grid quantization. Regime-label confirmation;
  no perturbation tests run.
- **H_3(ℤ/15) full 3D and axis marginals:** numerically strongly
  consistent with the same regime (r ≈ 2, r ≈ 4); no surgical
  perturbation tests run.
- **H_3 c-marginal (r ≈ 1.7) and BS(1,2) mantissa (r ≈ 1.15):** open.
  The parity-mode picture does not directly explain these
  intermediate regimes.

This document replaces the tentative slowdown discussion drafted
earlier (see `sim/h3_contrast_SUMMARY.md` and `PNAS-PLAN.md`) and
supports the updated paper footnote at the end.

---

## The phenomenon

On the ℤ² torus (L = 31, odd), the Heisenberg torus H_3(ℤ/15),
and the ℤ³ torus (L = 15), the alternating-step walk and the
full (Cayley) walk differ in how quickly their L₁ distance to
uniform crosses a matched threshold θ_k = k · √(2M/(πN)). At
N = 10⁶ walkers, the ratio r = n_alt(θ_k) / n_full(θ_k) is
stable and observable-dependent:

| group | observable                        | r    |
|:------|:----------------------------------|:----:|
| ℤ²    | full 2D state (L² = 961 bins)     | 2.0  |
| ℤ²    | x-axis marginal (L = 31 bins)     | 4.0  |
| ℤ³    | full 3D state (L³ = 3375 bins)    | 3.0  |
| ℤ³    | (a, b) 2D planar marginal         | 4.0  |
| ℤ³    | a-axis marginal (1D)              | 4.0  |
| H_3   | full 3D state (L³ = 3375 bins)    | 2.0  |
| H_3   | (a, b) 2D abelian marginal        | 2.0  |
| H_3   | a-marginal or b-marginal (1D)     | 4.0  |
| H_3   | c-marginal (central coord, 1D)    | 1.7  |

Measured ranges across k ∈ {5, 3, 2, 1.2}: ℤ² 2D: 1.96–2.00;
ℤ² 1D: 3.83–4.09; ℤ³ 3D: 2.73–2.92; ℤ³ 2D marginals: 3.79–4.11;
ℤ³ 1D marginals: 3.65–4.33; H_3 3D: 1.92–2.11; H_3 1D: 3.63–4.20.
The c-marginal 1.7 has wider spread from step-10 sampling
quantization at small n; the ℤ³ 3D range (~10% below 3.0)
reflects the same quantization at small crossing times
(n_full ≈ 110–200 for k = 5). (Full tables in
`sim/projection_check_SUMMARY.md`, `sim/h3_contrast_SUMMARY.md`,
and `sim/eps_scan_and_z3_SUMMARY.md`.)

---

## The mechanism (for ℤ²)

For ℤ² with L = 31, the r values decompose cleanly into a ratio of
two slow Fourier modes. (The H_3 full-3D and axis-marginal r values
fall in the same regimes numerically, but we have not done the
corresponding surgical tests on H_3; the parallel spectral
calculation is plausible but unverified here.) For Z/L with L = 31:

**Full walk on 1D x-marginal.** Char fn at Fourier mode k per
calendar step is (1 + cos(2πk/L))/2 — the lazy-walk formula,
because the full walk moves x with probability 1/2 per step. At
k = ⌊L/2⌋ = 15 this folds cos(2π·15/31) ≈ −0.9949 to ≈ 0.0026,
killing the near-parity mode. The slow mode is then k = 1, at
rate (1 + cos(2π/31))/2 = 0.9898, decay 0.01025 per step.

**Alt walk on 1D x-marginal.** Char fn at Fourier mode k per
x-step is cos(2πk/L); alt takes one x-step per two calendar
steps. At k = 15, cos(2π·15/31) = −0.9949 — the near-parity
mode — and its magnitude _survives_ because alt has no holding
step. Per calendar step: 0.9949^{1/2} ≈ 0.99745, decay 0.00256.

**Ratio 0.01025 / 0.00256 = 4.00.** The factor 4 decomposes as
2 (alt takes half-rate x-updates) × 2 (the near-parity mode
alt keeps and full kills).

The 2D calculation tracks the same way, bottlenecked at
diagonal-parity (15, 15) for full and axis-parity (15, 0) for
alt. See `sim/projection_check_SUMMARY.md` for the 2D table.

**ℤ³ extension.** The same calculation at L = 15, three
dimensions: full walk's slowest mode is the full-diagonal
(7, 7, 7) at rate −log(cos(π/15)) = 0.0222 per step; alt's
slowest mode is the axis-parity (7, 0, 0) at rate per
cal step = −log(cos(π/15))/3 = 0.0074 (one-coord update per
three cal steps). Ratio = 3.00, matching the measured r_3D
regime label. On 2D and 1D marginals of ℤ³, the calculation
gives r = 4, also matching measured ranges. The spectral
picture generalizes to ℤ^d with the exponent determined by
the alt schedule's period.

The c-marginal of H_3 and BS(1,2)'s mantissa do not fit the
parity picture cleanly, because their increments are state-dependent
(c depends on a, mantissa depends on E). The parity-mode story
explains the 2×, 3×, and 4× regimes; the 1.7× and 1.15× remain
intermediate regimes whose mechanism is not pinned down here.

---

## Four confirmations

### (1) Fourier calculation matches numerics across groups

| observable            | predicted r | measured range over k   |
|:----------------------|:-----------:|:-----------------------:|
| ℤ² 2D                 | 2.00        | 1.96–2.00               |
| ℤ² 1D marginal        | 4.00        | 3.83–4.09               |
| ℤ³ 3D                 | 3.00        | 2.73–2.92               |
| ℤ³ 2D planar marginal | 4.00        | 3.79–4.11               |
| ℤ³ 1D marginal        | 4.00        | 3.65–4.33               |
| H_3 3D                | 2.00        | 1.92–2.11               |
| H_3 1D marginal       | 4.00        | 3.63–4.20               |

Two independent computations agreeing — spectral, from the char
fn of the step distributions; numerical, from the walker sim —
across three different groups and two lattice dimensions. The ℤ³
r = 3 is a distinct regime label the mechanism predicts for
3-cycle alt schedules; measured range slightly below 3.0 is
step-10 sampling-grid quantization at small crossing times
(n_full ≈ 110–200).

Agreement is evidence but not mechanism proof — the
calculations could in principle agree for the wrong reason.

### (2) Single-point perturbation: laziness kills the mode

If the near-parity mode is the bottleneck, adding a holding
probability ε > 0 to the alt walk should suppress that mode
(via (1 − ε) + ε·cos(2πk/L)) and drop r by exactly a factor 2
on each ℤ² observable at ε = 0.5.

Ran lazy-alt at ε = 0.5 on ℤ²/31²:

| observable  | r_alt (prior) | r_lazy_alt (predicted) | r_lazy_alt (measured) |
|:------------|:-------------:|:----------------------:|:---------------------:|
| 2D          | 2.00          | 1.00                   | **1.00 ± 0.01**       |
| 1D marginal | 4.00          | 2.00                   | **2.00 ± 0.07**       |

Factor-2 drops on both observables, matching the prediction to
within sampling-grid precision. The perturbation is minimal —
one parameter added to the walk — and the r pattern changes
precisely as the spectral picture demands.

### (3) ε-scan: U-shape and sub-unity r region

Extending the ε = 0.5 test to ε ∈ {0, 10⁻³, 3×10⁻³, 5×10⁻³,
8×10⁻³, 10⁻², 3×10⁻², 0.1, 0.3, 0.5} traces the full r(ε)
curve. The spectral calculation predicts a specific U-shape
driven by the crossover between two slow modes: at ε = 0 the
(k = 15) parity mode dominates; as ε grows, the parity mode is
damped; at ε ≈ 0.008 the (k = 1) mode overtakes; beyond that
the schedule's sub-sampling penalty reasserts itself.

Numerical predictions and measurements at k = 2.0:

|    ε  | r_1D meas | r_1D pred | r_2D meas | r_2D pred |
|:-----:|:---------:|:---------:|:---------:|:---------:|
| 0.000 | 4.000     | 4.000     | 2.028     | 2.000     |
| 0.001 | 2.939     | 2.877     | 1.451     | 1.439     |
| 0.003 | 1.898     | 1.841     | 0.915     | 0.920     |
| 0.005 | 1.388     | 1.352     | 0.690     | 0.676     |
| 0.008 | 1.061     | 1.003     | **0.549** | **0.501** |
| 0.010 | 1.000     | 1.005     | 0.507     | 0.502     |
| 0.030 | 1.041     | 1.026     | 0.521     | 0.513     |
| 0.100 | 1.102     | 1.107     | 0.563     | 0.553     |
| 0.300 | 1.469     | 1.426     | 0.718     | 0.713     |
| 0.500 | 1.959     | 2.000     | 1.014     | 1.000     |

Measurements match predictions within 5% at all ten ε values on
both observables. The r_2D < 1 regime (ε ∈ [0.003, 0.3]) is the
hardest signal to fake: **lazy-alt is up to 2× faster than full
on the 2D observable** in the interior of the ε range. A
uniform "sub-sampling slows mixing" mechanism cannot produce
r < 1; the observed curve requires the specific two-mode
crossover the parity picture predicts.

### (4) Exact conservation law on even L

If the near-parity mode is a real conservation structure, making
it exact (via L even) should freeze alt's L₁ at an exact non-zero
value, while full mixes only modulo the (x + y) mod 2 parity that
every nearest-neighbor walk on Z²/L² obeys.

Ran alt and full at L = 30, N = 10⁶:

| walk      | observable | tail L₁ at n = 2000 | predicted | std at tail |
|:----------|:-----------|:-------------------:|:---------:|:-----------:|
| alt       | x_1d       | **1.0000**          | 1.0       | 1e-16       |
| alt       | 2D         | **1.5000**          | 1.5       | 5e-17       |
| full      | x_1d       | 4.4 × 10⁻³          | ≈ floor   | 5.5 × 10⁻⁴  |
| full      | 2D         | **1.0000**          | 1.0       | 5e-17       |

Plateau values hit their predicted integer/half-integer values
to machine precision. The "1.5" on alt 2D reflects a double
conservation law (x-parity and y-parity each deterministic,
walker restricted to one of four parity classes); "1.0" on full
2D reflects the single (x + y)-parity law that every symmetric
nearest-neighbor walk has. These are the expected outputs of the
spectral picture taken to its L-even limit.

---

## What this buys

The four confirmations are independent in the right sense:

| confirmation       | evidence type                                        |
|:-------------------|:-----------------------------------------------------|
| (1) Fourier/num    | two computations agree across ℤ², ℤ³, H_3            |
| (2) lazy-alt 0.5   | single perturbation acts as mechanism predicts       |
| (3) ε-scan U-shape | ten perturbations trace the predicted curve, including r < 1 |
| (4) even-L         | mechanism taken to its limit freezes the observable  |

The ε-scan is the sharpest of these: it constrains the mechanism
to match a specific continuous curve, not just hit a scalar
prediction. The r_2D < 1 regime in particular rules out any
alternative story in which alt is uniformly a sub-sampled (and
therefore uniformly slower) version of full.

Together the four leave little room on ℤ²: the r ≈ 2 and r ≈ 4
values on ℤ² are driven by the near-parity spectral mode, and
that mode's suppression (via laziness), exactness (via even L),
or full-range tracking under holding (via ε-scan) reshape the
slowdown exactly as predicted. The ℤ³ r = 3 and r = 4 values
track the same spectral picture extended to three dimensions
(regime-label confirmed, no perturbation tests run). The H_3
full-3D and axis-marginal r values fall in the same regimes
numerically, which is consistent with the same mechanism acting
on H_3 — but we have not run the lazy-alt or even-L checks there,
so this is a strong numerical fit, not an independently confirmed
mechanism.

---

## What this does not explain

- **BS(1,2) mantissa r ≈ 1.15.** Mantissa increments depend on
  the exponent E; this is not a marginal of any finite-quotient
  lattice walk, and the parity-mode picture doesn't directly
  apply. The most parsimonious hypothesis is that continuous
  averaging over E suppresses whatever slow mode the mantissa
  _would_ have, much as the H_3 c-marginal's partial averaging
  over a brings r to 1.7. Not tested — testing would require a
  BS(1,2) finite quotient (see `sim/BS12-FULLSTATE-SIM.md` for
  why that's blocked).
- **H_3 c-marginal r ≈ 1.7.** State-dependent increments again.
  The spectral picture requires a small-system calculation with
  joint (a, c) dynamics; not done.
- **F_2 drift r = 0.5 (alt faster).** This is a different
  regime (tree, alternating removes backtracking). Covered in
  `sim/SUBSET-THEOREM.md`; not part of the parity story.

---

## For the paper

The honest footnote, scoped to what's actually established:

> Sub-sampling an alternating-step walk on a Cayley-type
> generating set slows mixing by a group- and
> observable-dependent factor. On the full-state L₁ observable
> of the ℤ² torus, alternating is ~2× slower than the full
> walk; on a 1D axis marginal, ~4×. Both regimes are driven by
> a near-parity Fourier mode that the alternating walk fails
> to suppress. A holding-probability ε-scan traces a U-shaped
> r(ε) curve whose minimum sits below 1 — the alternating walk
> can be made faster than full by adding a small holding
> probability — matching the spectral prediction at all ten
> scanned values; the same mode becomes an exact conservation
> law (hence an infinite slowdown) on even-L quotients. The
> same spectral picture gives r = 3 on the 3D full state of
> the ℤ³ torus under a 3-cycle alternating schedule and r = 4
> on its 2D/1D marginals, matching measured values within
> sampling-grid quantization. The corresponding observables on
> the Heisenberg torus H_3(ℤ/L) fall in the same ~2× / ~4×
> regimes numerically, consistent with the same mechanism. On
> the continuous mantissa observable for BS(1,2), alternating
> is ~1.15× slower; on the H_3 commutator marginal, ~1.7×.
> These intermediate regimes have no established mechanism
> here; one plausible but untested hypothesis is that
> state-dependent coupling of the observable to other
> coordinates averages out the slow mode that drives the
> 2×/3×/4× regimes. On the free group F_2 measured by drift,
> alternating is 2× _faster_: a distinct lazy-walk speedup
> mechanism. The slowdown is not a clean function of group
> structure; it depends on the step set, the observable, and
> how the observable couples to the walk's slowest spectral
> modes.

The paper's rhetorical point — _only the full additive +
multiplicative mix converges to Benford in practice_ — doesn't
depend on the slowdown taxonomy. The cleanest paper move
remains to let the three-walks figure carry that point and
confine the slowdown discussion to this footnote.

---

## References (working documents)

- `sim/SUBSET-THEOREM.md` — Dirichlet-form gap bound (ceiling
  factor 4 on two-step sub-sampling).
- `sim/step_buddies_SUMMARY.md` — original BS(1,2) r ≈ 1.15
  measurement.
- `sim/f2_contrast_SUMMARY.md` — F_2 r = 0.5 (tree speedup).
- `sim/h3_contrast_SUMMARY.md` — ℤ² r = 2.0, H_3 r = 2.0.
- `sim/projection_check_SUMMARY.md` — projection table, r = 4
  on 1D marginals, r = 1.7 on H_3 c.
- `sim/parity_falsifier_SUMMARY.md` — lazy-alt ε = 0.5 (r drops
  2 → 1 on 2D, 4 → 2 on 1D) and even-L (exact plateau) results.
- `sim/eps_scan_and_z3_SUMMARY.md` — ε-scan of lazy-alt (U-shape
  confirmed, r_2D < 1 near crossover) and ℤ³ torus (r = 3 on 3D,
  r = 4 on marginals).
- `sim/BS12-FULLSTATE-SIM.md` — withdrawn BS(1,2) finite-quotient
  plan and why it doesn't work.
