# T1B-UNIT-BALL-SIM

## Why this plan exists

After the ROOT-TWO-CHECKS runs, T1b's surviving form —

> For every ν with a logarithmic moment and ν(Z[1/2]) = 0, L₁(P_n)
> ∼ B(ν) · n^{−1/2} with α = 1/2 universal, B IC-dependent.

— where Z[1/2] is the set of dyadic rationals (the orbit-reaches-0
points under exact arithmetic; this is the actual exceptional set, as
derived below; a naming note: "E" is reserved in these docs for the
exponent coordinate of walker state, so we use Z[1/2] for the
exceptional set). The theorem has been probed at four ICs (√2, φ, 1+restart,
1+absorb) plus M3's three. Every result is consistent. This plan
probes three further axes, plus an appendix on quantitative B(ν).

### Correction to the exceptional set

An earlier draft of this plan (and parts of the ROOT-TWO and m3
summaries) described the exceptional set as "ν supported on ℚ". That
is *wrong*. Under the affine action x ↦ 2^k · x + q with q ∈ Z[1/2]
(dyadic rationals) and k ∈ ℤ — which is the orbit of {a, a⁻¹, b, b⁻¹}
— x = 2^k · x₀ + q = 0 requires x₀ = −q/2^k, a **dyadic rational**,
not just any rational. So:

- x₀ dyadic (p/2^k form, k ≥ 0) ⇒ orbit reaches 0 under exact
  arithmetic. IC = 1, 3/2, 9/8, etc.
- x₀ rational but non-dyadic (p/q with q having odd prime factors,
  e.g. 7/5, 17/12, 99/70) ⇒ orbit **does not** hit 0. Same
  orbit-avoidance-of-0 status as irrationals.
- x₀ irrational ⇒ orbit avoids 0.

So the relevant algebraic clause is `ν(Z[1/2]) = 0`, not `ν(ℚ) = 0`.
This changes the design of Run 1 substantially. Whether the paper's
T1b quote should be updated to reflect this is a theorem-level
authoring decision; the transient-taxonomy runs below inform but do
not themselves make that edit.

### Float64 caveat

The kernels simulate in (m, E, sign) state with active-branch
reconstructions x = sign · 10^(E + m) followed by ± δ. This is
**not exact arithmetic**. Every active b-step introduces O(2⁻⁵³)
rounding. So algebraic statements like "non-dyadic rationals have
orbits that never equal 0 exactly" do not literally transfer to the
sim — float roundoff could in principle produce x_new == 0.0 from
a non-dyadic start. The sim's actual criterion is *numerical*
reachability of x_new == 0.0, which is measurable per run. Runs
below track this directly.

This plan probes three further axes of robustness:

1. **DYADIC-LADDER.** Map the trajectory taxonomy across dyadic,
   non-dyadic-rational, and irrational ICs, and directly measure
   the numerical zero-hit rate for each. Scope-limited to
   **transient taxonomy**, not to theorem-scale adjudication of
   the T1b clause.
2. **BROKEN-SYMMETRY.** Does T1b's α = 1/2 depend on the symmetry
   of the step measure? Weak-asymmetry variant, chosen so that
   drift does not push most walkers outside the kernel's
   computational envelope |E| ≤ 20 within the horizon.
3. **SMOOTH-IC.** Direct α̂ measurement on a ν that is absolutely
   continuous w.r.t. Lebesgue on T at the initial time.
4. **Appendix: MESSES-COEFFICIENT (investigation).** Open theory
   task to see whether MESSES's Laplace-transform framework can
   supply a closed-form prefactor B(ν). Not a decision-rule-level
   experiment; deliverable is a yes/no on whether this line of
   work is feasible with current theoretical inputs.

## Coordination note

Post-M4 follow-on, not part of `ALGEBRAIC-SIM-MESS-PLAN.md`'s default
schedule. Runs 1–3 are cheap (N = 10⁷, n_max = 600 each). Total
sim wall time estimate: ~75 min. Appendix is analysis-only.

Each run reuses kernels from `run_m3.py` and `run_root_two_checks.py`
with small modifications. The R2 exact-zero restart convention
handles dyadic ICs automatically; non-dyadic rationals and irrationals
shouldn't trigger it except via floating-point roundoff (Run 1 checks
this empirically).

**What these runs can and cannot conclude.** The late-window α̂ = 1/2
signature is only directly resolvable at our horizons for ν that
start with E already spread (M3 IC (b) does; the sharp-IC ICs in
Runs 1–3 may not). These runs map transient-sensitivity to IC
structure and rate-family fit on the observable window; they do
not pin down asymptotic α = 1/2 for each IC individually. M4-style
long horizons would be needed for that.

## Run 1 — DYADIC-LADDER

**Purpose.** Two questions:
- **Q1a (orbit structure)**: Do dyadic rationals, non-dyadic rationals,
  and irrationals populate distinct transient regimes in the
  observable window, consistent with the corrected exceptional-set
  story?
- **Q1b (float64 reality)**: Does the kernel's *numerical* zero-hit
  rate agree with the algebraic dichotomy? Specifically, non-dyadic
  rationals should produce ≈ 0 numerical zero hits; if they produce
  meaningful numbers, that is a sim-precision issue worth flagging.

**IC set (8 runs).**

| label | x₀         | class          | value (float64)        |
|:------|:-----------|:---------------|:-----------------------|
| D1    | 1          | dyadic         | 1.0                    |
| D2    | 3/2        | dyadic         | 1.5                    |
| D3    | 9/8        | dyadic         | 1.125                  |
| N1    | 7/5        | non-dyadic     | 1.4 (inexact in float) |
| N2    | 17/12      | non-dyadic     | 1.41666...             |
| N3    | 99/70      | non-dyadic     | 1.41428...             |
| I1    | √2         | irrational     | 1.41421356...          |
| I2    | φ          | irrational     | 1.61803399...          |

D1 matches R2's IC (useful as a sanity-check cross-reference).
I1 matches M1 (cross-reference). I2 matches R1. We rerun I1/I2 at the
same N and seed policy as the others so the side-by-side comparison
is like-for-like.

**Spec per IC.**

    N = 10⁷ walkers
    Symmetric measure
    IC: x = x₀ (8 values above)
        m = log₁₀(x₀) (float64), E = 0, sign = +1
    Time range: n = 0 to 600
    Sampling: M1 grid
    Exact-zero convention: R2-style restart at (m=0, E=0, sign=sign(delta))
    Output: L₁(n), ensemble ĥ(r, n), zero-hits-per-step

**Analysis.**

- **A1a (numerical zero-hit rate).** For each IC, report
  total_zero_hits / (N · n_max). Group by class. Expected:
  - D1, D2, D3: nonzero rate, O(10⁻⁴) – O(10⁻¹) per walker-step,
    dominated by the first few steps (as in R2).
  - N1, N2, N3, I1, I2: rate ≈ 0, possibly with sporadic
    float-roundoff-induced hits.
- **A1b (transient c_hat taxonomy).** Fit L₁(n) as `log L₁ = a − c·√n`
  on the window [20, 150]. Record c_hat per IC. Compare to the two
  reference transients from ROOT-TWO-CHECKS:
  - **R2/R3 signature** (c ≈ 0.35, dyadic-like)
  - **R1/√2 signature** (c ≈ 0.47, irrational-like)

**Decision rule (transient taxonomy only — explicitly not theorem-
scale).**

- Dyadic ICs cluster at c ≈ 0.35 AND have nonzero numerical
  zero-hit rate; non-dyadic + irrational ICs cluster at c ≈ 0.47
  AND have zero-hit rate ≈ 0 ⇒ **empirical evidence that
  non-dyadic rationals look numerically like irrationals on this
  horizon, and that the float64 kernel respects the algebraic
  dyadic/non-dyadic distinction.** This is transient-window
  evidence; it supports but does not on its own establish a
  theorem-level ν(Z[1/2]) = 0 clause (which is an algebraic
  statement about orbits, not a transient-rate statement).
- Non-dyadic ICs show nonzero zero-hit rate due to float roundoff
  ⇒ the algebraic dichotomy is not cleanly preserved at float
  precision. Report measured rate as a sim-precision caveat;
  does not imply a physical effect.
- Transient c_hat does not cluster cleanly by class ⇒ the
  dichotomy is finer than dyadic-vs-non-dyadic on this observable
  (e.g. it depends on denominator structure in some other way).
  Unexpected; would investigate.

In all three branches the theorem-level decision of what the T1b
clause should say is made by the paper's authors based on the
combined evidence (this run plus ROOT-TWO plus the orbit-algebra
argument), not by Run 1 alone.

**This run cannot show α → 1/2 on any individual IC.** The horizon
[1, 600] at N = 10⁷ sits below the late-time resolution threshold for
all sharp-IC-style starts, as ROOT-TWO-CHECKS established. Run 1 is
scoped to the transient-taxonomy question only.

Scope: 8 ICs × ~8 min = ~65 min.

## Run 2 — BROKEN-SYMMETRY (weak asymmetry)

**Purpose.** Locate T1b's dependence on step symmetry. Symmetric
measure gives E a null-recurrent walk on ℤ, which is what produces
ML(1/2) return counts (S0) and, via MESSES, α = 1/2. Strong asymmetry
gives E a linear drift, walker escapes to |E| → ∞, return-count
framework collapses.

**Caveat.** The kernel freezes b-steps for |E| > 20. Strong asymmetry
pushes many walkers into this frozen regime within the sim horizon,
so the observed L₁ would reflect (asymmetric walk) + (E_THRESH
approximation), not pure asymmetric walk. To keep the confound
bounded we use a weak asymmetry whose expected drift keeps most
walkers inside the envelope.

**Spec.**

    N = 10⁷ walkers
    Weakly asymmetric measure:
        P(a)   = 0.255     (drift d = P(a) − P(a⁻¹) = 0.01)
        P(a⁻¹) = 0.245
        P(b)   = 0.25
        P(b⁻¹) = 0.25
    Symmetric control run:
        P(a) = P(a⁻¹) = P(b) = P(b⁻¹) = 0.25  (re-running √2 at
            N = 10⁷ with the same seed policy for a like-for-like
            baseline; M1's √2 data is at N = 10⁸ and would give a
            misleading signal-to-noise advantage in direct comparison)
    IC: x = +√2
    Time range: n = 0 to 600
    Sampling: M1 grid
    Output: L₁(n), ensemble ĥ(r, n), mean(E)(n), std(E)(n),
            fraction of walkers with |E| > 20 at each sample time

**Expected drift envelope (heuristic).** Under d = 0.01 and a simple
±1-per-a-step model, E(n) is approximately Normal(d·n, c·√n) for
some c of order 1; b-steps also move E via carry/borrow, so any
closed-form estimate mixes a-step diffusion with a b-step contribution
and is heuristic rather than exact. Order-of-magnitude at n = 600:
mean |E| is small (≈ d·n = 6), the per-step E-variance is O(1), and
a non-trivial tail of walkers is expected at |E| > 20 by the horizon
end. The sim measures the actual frozen fraction at every sample time
(A2a below); fit windows are selected after that measurement, not
predicted in advance.

**Analysis.**

- **A2a (drift and envelope check).** Report mean(E)(n), std(E)(n),
  frozen_fraction(n) = Pr(|E| > 20) per sample time. Identify the
  largest n\_envelope such that frozen_fraction ≤ 5%. Fits in
  subsequent analysis are restricted to [20, n\_envelope]. The
  value of n\_envelope is set empirically by this measurement, not
  predicted in advance.
- **A2b (rate family fit).** Fit three families on [20, n\_envelope]
  for both the asymmetric and symmetric control runs:
  - stretched-exp: log L₁ = a − c√n
  - pure exp: log L₁ = a − γn
  - algebraic: log L₁ = a − α log n
  Report (c, γ, α, R²) for each.
- **A2c (difference test).** Compute L₁(asym, n) − L₁(sym, n)
  across the shared window. If weak asymmetry leaves α = 1/2 intact,
  the difference should be small and dominated by stretched-exp
  transient differences, not by a qualitatively different rate law.

**Decision rule.**

- Symmetric control: best-fit family matches M1 (stretched-exp
  transient with c ≈ 0.5). If this disagrees with M1 by more than
  noise, the N = 10⁷ downsampling is itself a problem — investigate.
- Asymmetric + symmetric agree on best-fit family within
  [20, n\_envelope] ⇒ **no qualitative change in the rate family
  is visible on this observable window, before the E_THRESH
  confound becomes large.** This does NOT say what the true
  asymptotic law is under asymmetry — only that within the
  envelope there is no visible change from the symmetric transient.
  Asymptotic behavior under asymmetry requires either a different
  kernel or a matched analytical argument.
- Asymmetric: pure-exp or algebraic fits significantly better than
  symmetric's stretched-exp on the same window ⇒ even weak
  asymmetry changes the rate family. Interesting; flag for
  theoretical analysis of how the drift interacts with the
  injection mechanism.

**Scope:** 2 runs (symmetric control + weak asymmetric) × ~8 min =
~16 min.

**What this run does NOT settle.** The strong-asymmetry case
(`d ≳ 0.1`) cannot be tested cleanly with the current kernel. Any
stronger-asymmetry conclusions would require either a modified
kernel (removing E_THRESH) or a longer-horizon run at strong
asymmetry with explicit analysis of the frozen fraction.

## Run 3 — SMOOTH-IC

**Purpose.** Direct α̂ measurement on a ν that is absolutely
continuous w.r.t. Lebesgue on T at the initial time. All our prior
sharp ICs (√2, φ, 1) have m-support at one point; M3's m-uniform
ICs (a, c) hit the noise floor fast. A narrow-but-smooth Gaussian on
T is the missing case.

**Two ICs.**

- **S1** (narrow wrapped Gaussian on T, E fixed):
  m ~ wrapped-Normal(μ = 0.5, σ = 0.05), E = 0, sign = +1
- **S2** (same m-distribution, E spread):
  m ~ wrapped-Normal(μ = 0.5, σ = 0.05), E ~ Uniform{−5, …, 5},
  sign = +1

**Sim-level zero-hit caveat.** The "x_new = 0 is numerically
unreachable from this IC" claim is an operational fact about the
sim, not a theorem about the Lebesgue measure. We monitor zero-hits
per step and expect none; if any occur, we report the rate as a
precision caveat.

**Spec per IC.**

    N = 10⁷ walkers
    Symmetric measure
    Time range: n = 0 to 600
    Sampling: M1 grid
    Exact-zero convention: R2-style restart (should fire ≈ 0 times;
        tracking confirms)
    Output: L₁(n), ensemble ĥ(r, n), l2_norm(n),
            zero_hits_per_step(601,)

**Initial L₁ estimate.** For a wrapped Gaussian(μ = 0.5, σ = 0.05) on
T = [0, 1), L₁(P_0, Leb) = ∫ |ρ_0(m) − 1| dm. For σ = 0.05, the
Gaussian is well-localized around 0.5, so L₁(0) ≈ 2·(1 − 2σ·√(2π))
≈ 2·(1 − 0.25) ≈ 1.5.

**Analysis.**

- **A3a (zero-hit sanity).** Confirm zero-hit rate ≈ 0 on both runs.
- **A3b (trajectory).** Record L₁(n) for both ICs. Compare to
  M3 IC (b) (another "E-spread" IC) and to √2 (sharp).
- **A3c (rate fits).** Fit both ICs on [20, 150] and [100, 600]
  against stretched-exp and algebraic. Emphasis on S2's late window
  where the E-spread feature should skip the stretched transient
  (as M3 IC (b) did).

**Decision rule.**

- S2 on [100, 600] shows α̂ ≈ 0.5 with R²(log n) > 0.99 ⇒ second
  clean sighting of α = 1/2, now at a smooth-m ν. Supports T1b's
  clause across the IC class we've now sampled.
- S1 shows sharp-IC transient (c ≈ 0.47 on [20, 150]) while S2
  shows algebraic decay ⇒ E-spread is the critical feature, not
  m-smoothness. Clarifies why M3 IC (b) is the cleanest test.
- Neither shows a clean α on the observable window ⇒ even smooth
  non-uniform ν's transient dominates the M1 horizon; α
  confirmation continues to depend on M3 IC (b) and M4 as before.

Scope: 2 runs × ~8 min = ~16 min.

## Appendix — MESSES-COEFFICIENT (open investigation)

**Scope.** Not a minutes-level postprocessing step. This is a
**theory-development task** that sits between MESSES.md and the
empirical data we have; it is listed here so that the question
doesn't drift, not as a run with a decision rule.

**Question.** Can MESSES's per-return Laplace-transform framework,
combined with B3's empirical K̂ and S0's ML(1/2) fit, supply a
closed-form prediction for the prefactor B(ν) in L₁(P_n) ∼ B(ν) ·
n^{−1/2}?

**What is available now.**

- The spectral radius ρ(K̂) = 0.924 (from `b3_results.npz`).
- The empirical 5×5 matrix K̂ itself (field `K_hat` in
  `b3_results.npz`) over modes r = 1..5, plus its eigenvalues
  (field `eigenvalues`). Eigenvectors are not saved but can be
  recomputed numerically from K̂ in one numpy call.
- The ML(1/2) scale constant c_fit ≈ 0.19 on the excursion
  subpopulation (from `s0_results.npz`).
- Measured B values: M3 IC (b) has B ≈ 3, M4 √2 has B ≈ 0.01 but
  (per `m4_SUMMARY.md`) the √2 estimate is not precisely pinned
  — the late excess above μ_null is real but α_local has not
  stabilized at 0.5 within [0, 3000].

**What is missing.**

- MESSES.md does not state a closed-form expression for the
  prefactor of the n^{−1/2} tail. The Laplace-transform argument
  gives the *order* of magnitude; reading off the constant requires
  either inverting a specific Laplace transform explicitly (non-
  trivial) or a rigorous matching step not currently written out.
- Whether the 5-mode truncation of K̂ captures enough of the
  operator spectrum to dominate B. At higher modes r ≥ 6 there
  could be non-negligible amplitude that changes the answer.
- An independent check at a third IC with well-measured B (beyond
  IC (b) and √2) — S1/S2 from Run 3 above could contribute if
  α̂ = 1/2 is resolvable there.

**Deliverable (if pursued).** A short note answering: (a) can
MESSES be extended to give B in closed form, or (b) is B
accessible only via numerical Laplace inversion on the empirical
K̂ data, or (c) is the current theoretical framework structurally
short a step. Output would go into MESSES.md, not into a
dedicated npz file.

**Why this matters to the paper.** If B is derivable, T1b gains a
quantitative claim (not just α, but the order of magnitude of B
for natural ν). If not, the paper can still state α = 1/2 and
note B as an IC-dependent constant to be estimated empirically.
Either outcome is publishable; the difference is how much the
theorem's decoration grows.

## Output files

- `run1_dyadic_ladder/{D1,D2,D3,N1,N2,N3,I1,I2}_results.npz`
  (8 files, one per IC)
- `run2_broken_symmetry_asymmetric_results.npz` and
  `run2_broken_symmetry_symmetric_results.npz` (2 files)
- `run3_smooth_ic/{S1,S2}_results.npz` (2 files)

Total: 12 sim outputs, ~1 GB combined.

## Total cost

- Run 1 (8 ICs): ~65 min
- Run 2 (2 runs): ~16 min
- Run 3 (2 ICs): ~16 min

Total sim time: ~97 min. All runs independent; any IC or run can
be skipped without blocking others.

## What this plan does NOT do

- Does not probe BS(1, p) for p ≠ 2. Separate kernel needed.
- Does not extend any IC to M4-style long horizons. Scope is
  perturbation-sensitivity of T1b's shape, not precision
  estimation of coefficients.
- Does not test strong asymmetry (d ≫ 0.01). The E_THRESH = 20
  kernel approximation confounds the interpretation once the
  frozen fraction exceeds ~10%.
- Does not test transcendental ICs (π, e) separately. The
  orbit-avoidance-of-0 argument applies to them equally; under
  the corrected dyadic/non-dyadic reading, transcendentals are in
  the same class as algebraic irrationals and non-dyadic
  rationals.
- Does not claim that the Appendix's MESSES-coefficient task is
  solvable. It frames the question and identifies the missing
  inputs; resolution is a separate theoretical effort.
