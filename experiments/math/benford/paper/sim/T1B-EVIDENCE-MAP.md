# T1B-EVIDENCE-MAP

Consolidated status of all sim work, oriented around Theorem 1b
(the surviving form of the paper's convergence-to-Benford
theorem). As of 2026-04-18.

**Precision robustness: closed.** fp64 is empirically sufficient
for every T1b observable. The question was settled from both
directions: a four-precision ladder (fp16 / fp32 / fp64 / fp128)
shows (a) events below fp64 scale linearly with fp_eps, with fp64
below detection at our volumes, and (b) 128-bit MPFR produces
bit-exactly identical L₁(n) and α̂ to fp64 at matched seed on M3
IC (b). This is a direct empirical result — no precision-related
caveats attach to any T1b claim in this document.

## T1b (current working statement)

For the symmetric BS(1,2) random walk, let ν be a probability
measure on ℝ\{0} with a logarithmic moment and ν(Z[1/2]) = 0
(the walker's orbit does not reach 0; equivalently, ν is
supported away from dyadic rationals). Let P_n = π_T(μ^{*n} ∗ ν)
be the mantissa marginal of the n-step walk. Then:

**(i) Equidistribution.** ‖P_n − Leb_T‖ → 0 as n → ∞.

**(ii) Asymptotic rate.** L₁(P_n, Leb_T) ∼ B(ν) · n^{−1/2},
with α = 1/2 ν-universal and B(ν) ν-dependent. The coefficient
B(ν) reflects the spectral weight of the initial deviation from
Leb_T in the generalized-eigenbasis of the induced first-return
operator T_R.

**(iii) Pre-asymptotic transient.** For ν concentrated (sharp
ICs), a stretched-exp transient A(ν)·exp(−c(ν)√n) dominates L₁
on a horizon of size n ≲ n\*(ν), crossing to the algebraic tail
at n\* defined by A·exp(−c√n\*) ≍ B/√n\*. Both A and c depend on
ν; the sharpness of the IC determines whether the transient is
visible and how long it lasts.

**(iv) Rational exception.** x₀ dyadic (Z[1/2]) is handled either
by restart (return to ±1 on b-step hitting 0) or by absorption
(walker removed). Both conventions give the same late-time L₁
within noise on the observable window [1, 600]. The asymptotic α
for dyadic starts is *not* resolved by the runs we have — both
R2 and R3 hit the N = 10⁷ floor before α would be measurable.

## Status by clause

### (i) Equidistribution — **consistent; two caveats**

Every IC we ran shows overall decreasing L₁ across the
observable horizon (with small null-band jitter once L₁
approaches θ_N; not literally monotone, but the decay is
unambiguous) and reaches the vicinity of the null floor.
Two caveats: M1 and M4 on the √2 IC hover 1.27× above θ_N
without crossing; M3 IC (b) is still clearly decaying at n = 600
at 15× the N = 10⁷ floor. Neither contradicts clause (i) but
neither "at floor" is literally true.

| sim             | IC                      | L₁(horizon)         | distance to floor |
|:----------------|:------------------------|--------------------:|:------------------|
| M1              | √2, N=10⁸, n=600        | 3.44×10⁻³           | 1.27× θ_N; hovering |
| M3 (a)          | m~U, E=0, N=10⁷         | 8.0×10⁻³ at n=600   | at N=10⁷ floor by n≈150 |
| M3 (b)          | m=log₁₀√2, E~U, N=10⁷    | 0.129 at n=600      | 15× above floor; still decaying |
| M3 (c)          | m~U, E~U, N=10⁷          | 8.0×10⁻³ at n=600   | at floor by n≈330 |
| M4              | √2, N=10⁸, n=3000       | 2.72×10⁻³ at n=3000 | 1.0× θ_N; 141/151 late-window samples above null q99 (≤ 1.5 expected under null), overwhelming significance |
| R1 (φ)          | φ, N=10⁷                | 8.1×10⁻³ at n=600   | at N=10⁷ floor    |
| R2 (restart)    | 1, restart, N=10⁷       | 8.4×10⁻³ at n=600   | at floor          |
| R3 (absorb)     | 1, absorb, N=10⁷        | 1.1×10⁻² at n=600   | within ~1.3× floor |
| Run 1 D1–D3     | 1, 3/2, 9/8, N=10⁷      | 8.1–8.3×10⁻³ at n=600 | at floor         |
| Run 1 N1–N3     | 7/5, 17/12, 99/70       | 8.4–8.7×10⁻³ at n=600 | at floor         |
| Run 1 I1–I2     | √2, φ, N=10⁷             | ~8.1×10⁻³ at n=600  | at floor          |
| Run 2 sym/asym  | √2                       | 7.95 / 8.41 ×10⁻³   | at floor          |
| Run 3 S1, S2    | wN(0.5, 0.05)            | 8.35 / 8.53 ×10⁻³   | at floor          |

No IC tested fails to approach uniform. M3 IC (b) is the only one
where L₁ is still visibly declining at the end of the horizon —
that IC's slow algebraic decay is itself the anchor for clause (ii).

### (ii) Asymptotic rate α = 1/2 — **one direct sighting + two consistency checks**

The α = 1/2 reading rests on one direct measurement plus two
independent consistency checks. No single observable establishes
α = 1/2 on its own in the pure "three-way lock" sense.

1. **M3 IC (b) — primary direct sighting.** With
   m = log₁₀√2 (delta) and E ~ Uniform{−5..5} (spread), at
   N = 10⁷: free log-log fit gives L₁(n) ≈ 3.81 · n^{−0.525}
   on [100, 600] with R²(log n) = 0.9986. Under imposed
   α = 1/2 the prefactor reads off as L₁(600) · √600 = 3.16, so
   "L₁ ∼ 3 · n^{−1/2}" is the natural compressed statement.
   500-step log-log fit, essentially zero curvature. α̂
   consistent with 1/2 to within a few percent; α is actually
   resolvable here because IC (b)'s structure skips the
   sharp-IC transient.

2. **S0 — Laplace-match consistency check.** Two sub-tests on
   M1's hist_return_counts:
   - **Laplace transform test (passes):** the conditional-on-
     excursion distribution N_n/√n matches ML(1/2) with
     max |residual(log L̂)| shrinking ±0.018 (n=100) → ±0.006
     (n=500), scale c_fit stable at 0.179–0.195 across
     n ∈ {100, 200, 300, 500}.
   - **β̂ tail-slope test (fails as written, determined to be
     mis-specified):** β̂ ≈ 9 rather than near 0.5; per
     `s0_SUMMARY.md` this is because the test's β = 1/2
     expectation was drawn from a different family (geometric-
     stable / Linnik) than ML(1/2) itself (half-normal body).
     The failure does not indict α = 1/2; it does mean that S0
     as an "instrument suite" was half-passing, not
     fully-passing.
   The net read: S0 validates the ML(1/2) **assumption** that
   MESSES's per-return Laplace-transform argument relies on. It
   does not directly measure α on L₁.

3. **B3 — regime-classification consistency check.** Empirical
   mode-coupling matrix K̂ (10⁷ walkers, 40M excursions) has
   ρ(K̂) = 0.924. The injection-dominated criterion
   (ρ(M) > γ₁^{c'}) is met at ratio 2.70, far from the
   balanced-regime boundary of 1. Under BENTHIC's framework,
   injection-dominated ⇒ genuine asymptotic rate is **algebraic,
   not stretched-exp**. B3 alone does not pin the exponent; the
   n^{−1/2} reading comes from combining B3's "algebraic, not
   stretched" verdict with S0's ML(1/2) Laplace match (which
   gives the ½ exponent via the return-count tail).

So the honest architecture is: **M3 IC (b) measures α ≈ 0.525.
S0 + B3 make the MESSES-style derivation empirically self-
consistent, so α = 1/2 is the natural reading.** Calling this a
"three-way lock" was overclaim; the correct description is "one
measurement, two independent supports."

**M4 corroborates on √2.** Long-horizon run at N = 10⁸, n = 3000:
141 of 151 late-window (n ∈ [1500, 3000]) samples sit above the
null q99, which under a pure-null hypothesis would have ≤ 1.5
samples above q99. Significant persistent signal above floor.
α_local drifts 1.43 (n=500) → 0.91 (n=1500–3000), consistent
with transient fade + tail emergence but not yet at 0.5.

**B is IC-dependent, not universal.** Only two ICs in the sim
record have a B value with any empirical grounding:

| IC              | inferred B | anchor                               |
|:----------------|-----------:|:-------------------------------------|
| M3 IC (b)       | ≈ 3        | inferred B under α = 1/2 from L₁(600)·√600 = 3.16; the free log-log fit on [100, 600] gives A = 3.807 at α̂ = 0.525, R²(log n) = 0.9986 |
| M1/M4 (√2)      | ≈ 0.01     | order-of-magnitude from late-window excess above μ_null at n ≈ 2000–3000 (M4 summary explicitly flags this as not precisely pinned; α̂ has not stabilized at 0.5 yet) |

The M3 IC (b) number is a loose "inferred B" under the α = 1/2
reading; the clean direct-sighting content is the free-α log-log
fit itself (α̂ = 0.525, R² = 0.9986). The √2 number is a looser
inference only meaningful if we assume α = 0.5 and the late
excess is the tail. Other ICs (IC (a), IC (c), all Run 1 entries,
the S1/S2 ICs) reach near-floor too quickly for any B to be
extracted; an earlier draft of this doc reported B values for IC
(c) and the Run 1 N-series that were not actually measured, and
has been corrected.

The initial draft of the m3 summary claimed B-universality; this
has been corrected. Theoretically expected: B depends on how ν
projects onto the slow-decaying modes of T_R. The 300× ratio between
M3 IC (b)'s ≈ 3 and √2's ≈ 0.01 is the only direct evidence of this
dependence; it is a two-point comparison, not a panel.

### (iii) Pre-asymptotic stretched-exp transient — **IC-specific, not universal**

The stretched-exp shape we measured on M1 (c ≈ 0.5, R² = 0.999
on [20, 200] for the √2 IC; fit documented in the Run 2
cross-IC comparison table of `m3_SUMMARY.md`, data from
`m1_b1_b2_results.npz`) is not a property of the walk; it's
a property of the √2 IC's particular sharp initial structure.

Transient c_hat values observed across 13 ICs, all on [20, 150]:

| class                      | ICs                              | c_hat range          |
|:---------------------------|:---------------------------------|:---------------------|
| dyadic rationals           | D1 (1), D2 (3/2), D3 (9/8)       | 0.335–0.347          |
| non-dyadic rationals       | N1 (7/5), N2 (17/12), N3 (99/70) | 0.374–0.543 (wide)   |
| irrational sharp           | √2, φ                            | 0.466–0.498          |
| spread-E mixtures          | M3 IC (c), Run 3 S2              | 0.356                |
| E-uniform with delta-m     | M3 IC (b)                         | 0.137 (transient dead) |
| near-uniform ICs           | M3 IC (a), Run 3 S1               | < 0.05 (at floor)    |

The clean "c ≈ 0.5" value from M1 is specific to the (m = log₁₀√2,
E = 0, sign = +1) joint delta. It is **not** a load-bearing
constant for T1b; it's a transient descriptor for one particular
IC.

### (iv) Rational exception — **algebraic dichotomy respected up to fp_eps-scaling catastrophic cancellation, with fp64 sufficient in both directions**

The question "which ICs have orbits that hit 0?" has a clean
algebraic answer: x₀ ∈ Z[1/2] (dyadic rationals). This is a
strict subset of ℚ. The sim respects this algebraic fact up to
floating-point catastrophic-cancellation events `x + δ → 0`,
whose rate is approximately linear in machine epsilon. Measured
precision ladder (from fp16-mini, fp32, fp64 main runs, and the
fp128-ceiling check):

| precision | fp_eps      | behavior                                                   |
|:----------|------------:|:-----------------------------------------------------------|
| fp16      | 4.9×10⁻⁴    | precision-induced zero-hit rate ≈ 2×10⁻⁵ /walker-step      |
| fp32      | 6×10⁻⁸      | rate ≈ 1.5×10⁻⁹ /walker-step                               |
| fp64      | 1.1×10⁻¹⁶   | rate < 3×10⁻¹¹ /walker-step (below detection at our volumes) |
| fp128     | 6×10⁻³⁵     | bit-exactly identical L₁, α̂ to fp64 at matched RNG seed  |

Three direction-from-below data points show the rate scales
linearly with fp_eps, consistent with the catastrophic-cancellation
mechanism (`x + δ` rounds to 0 when `|x + δ| < fp_eps · |x|`).
The direction-from-above check at 128-bit on M3 IC (b) produces
bit-exactly identical L₁ trajectories and α̂ as the fp64 control,
demonstrating that fp64's per-walker roundoff (~10⁻¹⁵) is twelve
orders of magnitude below the L₁ histogram's bin width, so fp64
error is invisible in the ensemble observable. **fp64 is
sufficient in both directions.**

Empirically in the main fp64 sim, across 7 non-dyadic /
irrational / smooth-Gaussian ICs (N1–N3, I1–I2, S1–S2) × 6×10⁹
walker-steps each = 4.2×10¹⁰ opportunities for float roundoff
to produce 0, there were zero numerical zero events. Dyadic ICs
produced 0.019–0.791 events per walker depending on |x₀ − 1|
(algebraic path `b⁻¹(1) = 0` reaches 0 exactly at any precision
for IC x₀ = 1, and related paths for other dyadics).

**Conventions on dyadic ICs are empirically interchangeable within
noise on the observable window.** R2 (restart at ±1) and R3
(absorb) agree on L₁ within about 7% over [50, 200] and stay
within noise of each other throughout; the late-time ratio drifts
to 0.77 at n = 600, but both trajectories are at or near the
N = 10⁷ floor there, so the 23% gap is dominated by floor
fluctuations on independently-seeded runs rather than a systematic
separation. The observable consequence is: whichever convention
the theorem picks for the dyadic case, the late-time L₁ is the
same within noise. **α for dyadic starts is not resolved by either
R2 or R3** — both hit floor before α would be measurable.

### (v) Symmetry clause — **weak asymmetry doesn't break T1b on envelope; strong asymmetry untested**

From T1B-UNIT-BALL Run 2:

- Asymmetric (P(a) − P(a⁻¹) = 0.01) vs symmetric control, same IC,
  same N: L₁ ratios in [0.96, 1.06] throughout [1, 600].
- Stretched c_hat: 0.419 (asym) vs 0.416 (sym) on [20, 300],
  difference 0.7%.
- Frozen fraction stays < 3×10⁻⁴ through n = 600, so E_THRESH
  envelope is not active.

This is a check-passes, not a theorem-level certification. Strong
asymmetry (d ≳ 0.05) would push walkers out of the computational
envelope and requires either a modified kernel or a longer-
horizon run with explicit envelope analysis. Regarding the
analytic chain that would tie symmetry to the α = 1/2 rate via
null-recurrent returns and ML(1/2): the walker's empirical
return-time structure is consistent with ML(1/2) on the M1 IC
(S0's conditional Laplace-match, clause ii; τ_R first-excursion
survival slope ≈ −0.495 per `sim/tau_R_tail_SUMMARY.md`). The
stronger chain "symmetric ⇒ null-recurrent E ⇒ ML(1/2) ⇒
α = 1/2" is map-level analytic framing rather than a claim any
single sim verifies end-to-end; the Laplace-diagnostic sim
(`sim/laplace_diagnostic_SUMMARY.md`) also shows that the
E-process on M1 has positive mean drift and L_n growing
linearly, so the "null-recurrent E" bridge should not be stated
as strictly literal. Run 2 is a check that weak symmetry-
breaking (d = 0.01) doesn't break the observable-window
behavior; it is not a certification of the analytic chain.

## Sim inventory — what runs produced what

| sim (script)                     | purpose                       | key output |
|:---------------------------------|:------------------------------|:-----------|
| `run_m0.py`                      | null-floor calibration        | θ_N(N=10⁸) = 2.72×10⁻³ |
| `run_m1_b1_b2.py`                | M1 + B1 + B2 consolidated     | L₁(n) on √2 IC, ensemble Fourier, N_n histogram, in-R cohort Fourier |
| `run_s0.py`                      | ML-index test (postprocess)   | conditional Laplace residuals < 0.02, c_fit ≈ 0.19 stable |
| `run_b3.py`                      | mode-coupling matrix          | ρ(K̂) = 0.924, injection-dominated |
| `run_m3.py`                      | 3 IC robustness runs          | IC (b) shows α̂ = 0.525 on [100, 600] |
| `run_m4.py`                      | long-horizon √2 IC            | n=3000 late signal above null; α_local drifts toward 0.5 |
| `run_root_two_checks.py`         | φ + rational-with-conventions | R1 tracks √2, R2 ≈ R3 on rational start |
| `run_t1b_unit_ball.py`           | dyadic ladder + asym + smooth | zero-hit dichotomy confirmed; weak asym clean; smooth ν doesn't deliver α |
| `run_fp32_checks.py`             | fp32 precision-robustness     | α̂ robust under 10⁴× precision loosening; dichotomy has detectable fp32 floor |
| `run_fp16_checks.py`             | fp16 three-precision ladder   | rate ∝ fp_eps confirmed via pristine-walker tracking (fp16/fp32/fp64) |
| `run_fp128_check.py`             | fp64-vs-fp128 precision ceiling | L₁, α̂ bit-exactly identical on M3 IC (b); precision closed from above |

All summaries are at `sim/*_SUMMARY.md` next to each sim script's
output npz files.

## What is NOT yet pinned down

1. **α̂ = 1/2 on the √2 IC directly.** M4 at n = 3000 shows a
   persistent signal above null but α_local is still drifting
   (0.91 at n=1500–3000, not 0.5). A run at n = 20 000 would
   resolve this; costs ~40 hrs on the current machine.
2. **Coefficient B(ν) theory.** No closed-form prediction for B
   from MESSES exists. The T1B-UNIT-BALL appendix frames the
   question but a quantitative B predictor is genuine theoretical
   work.
3. **Transcendental ICs (π, e, etc.) not separately tested.** The
   orbit-avoidance-of-0 argument covers them, but no direct sim.
4. **Strong asymmetry.** Requires a modified kernel or long-
   horizon machinery that handles the E_THRESH confound.
5. **Cross-group universality.** Whether α = 1/2 holds for
   BS(1, p) with p ≠ 2. Would need a separate kernel.

## What the paper can safely say

Based on the evidence above, T1b's provable / empirically-
supported content is (with precision robustness closed in both
directions — see the top of this document):

- Convergence to Benford (clause i): universal across ν.
- Asymptotic exponent α = 1/2 (clause ii): the M3 IC (b) direct
  measurement is the primary anchor (α̂ = 0.525, R² = 0.9986 on a
  500-step log-log fit). S0's conditional Laplace match and B3's
  injection-dominated regime classification are independent
  consistency checks that make the α = 1/2 reading the natural
  one given MESSES's framework. M4 on √2 corroborates via
  persistent late-window signal above null floor, though α̂ has
  not stabilized at 0.5 on the √2 IC within the runs we have.
- Coefficient B(ν): IC-dependent, with two empirically-grounded
  values — M3 IC (b) ≈ 3 (direct fit) and √2 ≈ 0.01 (order-of-
  magnitude from M4's late excess). State as an IC-dependent
  constant in the theorem; do not tabulate it for ICs where it
  was not measured.
- Pre-asymptotic transient (clause iii): IC-specific; the
  paper should not promote any specific c to a universal
  constant, but may describe it for the √2 IC as an illustrative
  transient.
- Exceptional set (clause iv): ν(Z[1/2]) = 0 is the clean
  algebraic condition, respected by the sim up to floating-point
  catastrophic-cancellation events whose rate scales linearly
  with machine epsilon. fp16 gives ≈ 2×10⁻⁵ per pristine
  walker-step; fp32 gives ≈ 1.5×10⁻⁹; fp64 gives < 3×10⁻¹¹,
  below detection at our volumes; fp128 on M3 IC (b) gives
  bit-exactly identical L₁ and α̂ to the fp64 control, closing
  the precision-robustness question in both directions.
  Rational-IC conventions (restart vs absorb) give the same
  late-time L₁ within noise on the observable window; neither
  resolves α for dyadic starts.
- Symmetry (clause v): stated as an explicit hypothesis of the
  theorem. Weak asymmetry (d = 0.01) leaves the observable-
  window L₁ unchanged within the E_THRESH envelope; strong
  asymmetry untested.

## What the paper should not claim

- A universal c in exp(−c√n). T1a is dead.
- IC-invariance of B. Post-M4 correction.
- α = 1/2 directly measured on the √2 IC. M4 supports but does
  not pin this down within the horizons we've run.
- α = 1/2 directly measured on any dyadic IC. R2/R3 hit floor
  before α would be resolvable.
- "Three-way independent measurements of α = 1/2." The honest
  framing is one direct measurement (M3 IC (b)) plus two
  consistency checks (S0 Laplace match, B3 regime classification)
  that together make α = 1/2 the natural reading, not three
  independent measurements of the same quantity.
- Quantitative B(ν) values for ICs other than M3 IC (b) and √2.
- Anything about strong asymmetry or BS(1, p≠2).

## Suggested paper structure (implied by the evidence)

- **§1 Statement.** T1b as above, with the ν(Z[1/2]) = 0 clause
  and the symmetry hypothesis explicit.
- **§2 Equidistribution proof.** Whatever clean ergodic / mixing
  argument handles clause (i) under the standard group-walk
  hypotheses.
- **§3 Algebraic rate derivation.** Per-return Laplace-transform
  argument à la MESSES, using ML(1/2) return statistics (clause
  ii exponent). The coefficient B is left as an IC-dependent
  constant; do not claim closed form.
- **§4 Numerical illustration.** M3 IC (b) as the primary
  visualization of α = 1/2; M1/M4 on √2 as the "natural starting
  point with a pre-asymptotic transient"; the 13-IC robustness
  panel from T1B-UNIT-BALL as the anti-cherry-picking check.
  A one-paragraph *precision-robustness* footnote closes the
  "why fp64?" question in both directions:

  > Ensemble observables (L₁, Fourier coefficients, α̂) were
  > cross-validated across four floating-point precisions: fp16,
  > fp32, fp64, and 128-bit via MPFR. Below fp64, the dyadic-
  > exception-set zero-hit rate scales linearly with machine
  > epsilon, with fp64's rate below detection at our volumes.
  > Above fp64, running M3 IC (b) at 128-bit with matched RNG
  > seed produces bit-exactly identical L₁ trajectory and α̂ as
  > the fp64 control at the same N and horizon. fp64 is
  > therefore empirically sufficient for the observables this
  > paper relies on.

  This paragraph kills any "but what if fp64 is introducing
  systematic error" reviewer objection with empirical teeth,
  not bound estimates.

- **§5 Scope and non-results.** Explicit list: rational/dyadic
  exceptions and conventions; symmetric-measure requirement;
  what strong asymmetry would look like; open theoretical
  questions (B(ν), cross-group).
