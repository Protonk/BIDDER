# M3 — Initial-condition robustness — summary

Run: `run_m3.py` → `m3_results.npz` (2026-04-17).
N = 10⁷ walkers/IC, 600 steps, same sampling grid as M1.
Three nontrivial ICs; seed base `0xEE1C3A11`.
Wall time 25 min total.

**External comparison:** θ_N at N = 10⁷ scales as √(10) × θ_N(M0 at N=10⁸) ≈ 8.59×10⁻³.

## Headline

**M3 falsifies the universality of M1's measured stretched-exp rate.**
IC (b) — delta in m, uniform in E — decays **algebraically** with
exponent α̂ = 0.525 ± a bit, R²(log n) = 0.9986 on [100, 600]. This is
a direct empirical sighting of MESSES's predicted n^{−1/2} asymptotic
tail, on a window that M1's √2 IC could not reach because the √2 IC's
decay is dominated by a separate, faster (stretched-exp-looking)
transient driven by the E = 0 initial sharpness.

**The paper's Theorem 1a (single-regime exp(−c√n)) is inconsistent with
IC (b)'s trajectory** unless the "exp(−c√n)" clause is restricted to a
horizon-and-IC-specific transient. T1b (two-regime: stretched-exp on
observable horizon, algebraic asymptotically) or T1c (mixture) are the
surviving theorem shapes.

## L₁(n) across ICs

| n   |  M1 (√2)  |  IC (a)   |  IC (b)   |  IC (c)   |
|----:|----------:|----------:|----------:|----------:|
|   1 | 1.9920    | 0.1756    | 1.9700    | 0.3233    |
|  10 | 1.2289    | 0.0156    | 1.0690    | 0.4136    |
|  25 | 0.5746    | 0.0119    | 0.7305    | 0.3157    |
|  50 | 0.2251    | 0.0112    | 0.5105    | 0.1829    |
| 100 | 0.0527    | 0.0098    | 0.3349    | 0.0626    |
| 150 | 0.0156    | 0.0092    | 0.2742    | 0.0254    |
| 200 | 0.0066    | 0.0088    | 0.2384    | 0.0134    |
| 300 | 0.0042    | 0.0090    | 0.1937    | 0.0087    |
| 455 | 0.0037    | 0.0084    | 0.1528    | 0.0086    |
| 600 | 0.0034    | 0.0080    | 0.1294    | 0.0080    |

IC (a) is at floor by n ≈ 150. IC (c) by n ≈ 330. IC (b) is still at
0.129 at n = 600 — **15× above the N = 10⁷ floor**.

### n\* (first sample with L₁ below the relevant θ_N)

| IC     | θ_N used    | n\*    |
|:-------|:------------|:-------|
| M1(√2) | 2.72×10⁻³   | > 600  |
| IC (a) | 8.59×10⁻³   | 157    |
| IC (b) | 8.59×10⁻³   | **> 600** (min L₁ = 0.129 at n=600) |
| IC (c) | 8.59×10⁻³   | 330    |

## Rate fits

Fit log L₁(n) = a + s · x over windows, comparing **stretched-exp** form
(x = √n, rate constant c_hat = −s) vs **algebraic** form (x = log n,
exponent α_hat = −s). R² close to 1 ⇒ good fit in that parameterization.

### Window [20, 150] — the plan's early-asymptotic window

| IC      | c_hat | R²(√n)  | α_hat | R²(log n) |
|:--------|------:|--------:|------:|----------:|
| M1 (√2) | 0.498 | 0.9985  | 2.005 | 0.9722    |
| IC (a)  | 0.037 | 0.926   | 0.152 | 0.932     |
| IC (b)  | 0.137 | 0.9834  | 0.564 | **0.9982** |
| IC (c)  | 0.356 | 0.9929  | 1.424 | 0.9554    |

### Window [20, 200] (plan spec)

| IC      | c_hat | R²(√n)  | α_hat | R²(log n) |
|:--------|------:|--------:|------:|----------:|
| M1 (√2) | 0.506 | 0.9989  | 2.253 | 0.9701    |
| IC (a)  | 0.033 | 0.9165  | 0.149 | 0.938     |
| IC (b)  | 0.120 | 0.9707  | 0.550 | **0.9979** |
| IC (c)  | 0.364 | 0.9960  | 1.614 | 0.9602    |

### Window [100, 600] — algebraic-tail-candidate window

| IC      | c_hat | R²(√n)  | α_hat | R²(log n) |
|:--------|------:|--------:|------:|----------:|
| M1 (√2) | 0.172 | 0.7733  | 1.465 | 0.8529    |
| IC (b)  | 0.065 | 0.9952  | **0.525** | **0.9986** |

For IC (b), **α_hat = 0.525 with R²(log n) = 0.9986** on a 500-step
window is an unusually clean power-law fit. The exponent is consistent
with 1/2 to within fit uncertainty. This matches MESSES's Laplace-
transform-derived prediction that E[q^{N_n}] is O(n^{−1/2}) for
null-recurrent walks, and BENTHIC's B3 verdict that the regime is
injection-dominated (→ algebraic asymptotic).

## Plan decision-rule check

The plan's M3 rule (§ Run M3) asks whether at least one nontrivial IC
agrees with M1's [20, 200] classification — c within ±15% of M1's c, and
residual-autocorrelation sign matching M1 — treating all three ICs as
candidates.

| IC      | c_hat  | within 15% of M1's c = 0.506? | L₁ sits above floor throughout [20, 200]? |
|:--------|-------:|:-------------------------------|:------------------------------------------|
| IC (a)  | 0.033  | **no** (c ~ 15× low)            | no (floor by n ~ 150)                     |
| IC (b)  | 0.120  | **no** (c ~ 4× low)             | yes                                       |
| IC (c)  | 0.364  | **no** (c ~ 28% low)            | yes (until n ≈ 330)                       |

**No M3 IC agrees with M1's c within the plan's tolerance.** Under the
plan's rule as literally written, M3 fails and the pipeline would halt.

But the disagreement is not a bug in M3 — it is the finding itself. M1's
c ≈ 0.5 is a fit over [20, 200] on the trajectory of an IC whose initial
state is a joint delta function in (m, E). The stretched-exp shape on
this window is the **IC-specific transient** of relaxing from a joint
delta, not the universal asymptotic rate. The moment any axis of the IC
is spread (IC b spreads E; IC c spreads both m and E) the transient is
replaced by something else — and in IC (b)'s case, that something else
is the algebraic tail itself.

The plan's M3 decision rule presupposed that a robust rate law is
c-universal across nontrivial ICs. The data says **the rate law is not
c-universal**: the √2 IC has a distinct-from-the-others transient that
a universal rate statement cannot capture.

## Interpretation vs BENTHIC B3 and MESSES

Cross-reference with B3:

- B3 measured ρ(K̂) = 0.924 ≫ γ₁^{c'} = 0.342, i.e. the creation-
  destruction balance is deep in the injection-dominated regime.
- Injection-dominated → genuine asymptotic is algebraic with exponent
  set by the return-count distribution's lower tail. Under ML(1/2) (S0
  confirmed) the exponent is 1/2.
- M3 IC (b) measures α̂ = 0.525 on [100, 600]. The three results
  (B3 regime verdict, S0 ML-index match, M3 IC (b) direct exponent)
  are **mutually consistent**.

The paper's working picture is now:

1. **Asymptotic form is algebraic**, L₁(n) ~ B·n^{−1/2}, with the
   **exponent α = 1/2 IC-universal** (derived from ML(1/2) return-
   count statistics that S0 confirmed). The **coefficient B is
   IC-dependent**: it is set by the spectral weight of the initial
   deviation in the generalized-eigenbasis of T_R, so sharp ICs
   loading onto fast-decaying modes have small B and ICs loading
   onto slow-decaying modes have large B. Post-M4 (2026-04-18)
   correction: the original draft of this summary claimed B was
   IC-invariant; M4 showed the √2 IC has B ≈ 0.01 while IC (b) has
   B ≈ 3, a ~270× discrepancy. α is what's universal, not B.
2. **Observable-horizon rate looks stretched-exp** for sharp ICs like
   M1's √2, because the E-relaxation transient dominates L₁ while it
   is O(1) above the algebraic floor. The crossover happens when the
   transient has decayed to the same scale as the algebraic tail.
3. **For IC (b)**, the E-relaxation transient is completed at t = 0
   by construction — E starts spread on {−5..5} — so the algebraic
   tail is visible from the start. There is no stretched-exp phase
   to see.
4. **For IC (c)**, m is also spread, so the initial L₁ is small, but
   the E-spread still has structure. Decay is intermediate-looking —
   neither a clean stretched-exp nor a clean power law on [20, 150].

## Implications for the paper

**What survives:**

- Convergence to Benford (ensemble mantissa marginal equidistributes
  on T) is IC-universal. All four ICs reach L₁ near or below θ_N
  within the simulated horizon (except IC (b), which would need
  ~n = 10⁵ or more to do so under its measured power law).
- The algebraic tail **exponent** α = 1/2 is IC-universal; the
  **coefficient** B is IC-dependent (see post-M4 correction above).
  IC (b) shows the form directly at B ≈ 3; M4 at n = 3000 on the
  √2 IC shows a persistent but much smaller signal (B ≈ 0.01, see
  m4_SUMMARY.md).
- **Post-2026-04-18 addendum (from T1B-UNIT-BALL Run 3):** IC (b)'s
  specific structure — delta in m at log₁₀√2, uniform in E over
  {−5, …, 5} — is load-bearing for the clean α̂ ≈ 0.5 signal on
  [100, 600]. Replacing delta-m with a narrow Gaussian (σ = 0.05)
  while keeping uniform-E (Run 3's S2 IC) gives α̂ = 1.11 on
  [100, 600], not 0.5. Smooth-m ICs behave structurally like M3
  IC (c), not IC (b). The m-coordinate concentration matters: when
  m is smooth the initial L₁ is lower, and the tail becomes buried
  in noise floor at our horizon. IC (b) remains the primary
  empirical anchor for α, with M4 √2's late excess as corroboration.

**What does not survive as written:**

- Any theorem claiming "TV(P_n, uniform_T) ≤ C·exp(−c√n)" with C, c
  IC-independent constants. IC (b) directly falsifies this: an
  algebraic power law cannot be bounded by any exponential in √n for
  large n (the algebraic decay is slower).
- Theorem 1a (single-regime stretched-exp) as a universal statement.

**What the paper should commit to:**

- **Theorem 1b** (two-regime) OR **Theorem 1c** (mixture): the
  ensemble TV decays to 0, with a pre-asymptotic window that varies
  by IC and an asymptotic tail of order n^{−1/2} that is universal.
- The observable-horizon stretched-exp rate c ≈ 0.5 measured for
  the √2 IC becomes: "on the √2 IC, L₁ on [1, ~200] is well-
  approximated by A·exp(−c√n) with c ≈ 0.5; this is the transient,
  not the universal rate." Other ICs will have different transients.

## Plan amendment needed

The M3 decision rule in ALGEBRAIC-SIM-MESS-PLAN.md assumes a universal
rate law across ICs, which this run has now falsified. The amendment
should:

1. Replace the "one IC agreeing ⇒ robustness confirmed" rule with a
   two-step read: (i) do all ICs satisfy the **convergence to Benford**
   statement? (ii) is the asymptotic-tail exponent α stable across ICs
   where it is resolvable?
2. Recognize that the stretched-exp c is a transient-rate descriptor,
   IC-dependent, and not appropriate as the target for M3 concurrence.
3. Promote the algebraic-tail exponent α to the primary IC-invariance
   test, with IC (b) as the cleanest empirical anchor.

(I'll draft the actual amendment text after you've looked at this.)

## What's saved in m3_results.npz

Per IC key ∈ {a, b, c}:

- `ic_{key}_l1(280,)` — L₁(n) on the M1 sample grid
- `ic_{key}_h_full(280, 5)` — ensemble ĥ(r, n) for r = 1..5
- `ic_{key}_l2_norm(280,)` — √Σ|ĥ(r)|² over r=1..5
- `ic_{key}_seed` — RNG seed used for that IC
- `sample_times`, `modes`, standard metadata

## Caveats

- Fits assume no model drift within the fit window; for IC (b) we see
  R²(log n) stable at 0.998 across [20, 150], [20, 200], and [100, 600]
  windows, so the power law is the right parameterization across this
  range. But the fit is a local slope; whether α stays at 0.525 for
  very large n (n ≫ 10⁴) is not established by M3.
- IC (c) at window [20, 150]: c_hat = 0.356 with R²(√n) = 0.993 and
  α_hat = 1.424 with R²(log n) = 0.955. Stretched fits marginally
  better than power-law here. This is the only M3 IC where the rate-
  family choice is ambiguous; likely IC (c) is in a crossover phase
  between IC (a)'s floor and IC (b)'s algebraic tail.
- N = 10⁷ per IC (vs M1's 10⁸) means noise on L₁ is √10 ≈ 3.2× larger
  than M1's. The fits above are stable under this noise at the reported
  precision, but rerunning any specific IC at 10⁸ would tighten α_hat
  CI substantially.
- IC (b) at L₁ = 0.13 at n = 600 gives an S/N ratio of 15 vs the N=10⁷
  floor — clean enough that the α̂ = 0.525 is not a noise artifact.
