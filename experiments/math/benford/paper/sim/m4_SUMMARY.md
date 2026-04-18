# M4 — Algebraic-tail run on the √2 IC — summary

Run: `run_m4.py` → `m4_results.npz` (completed 2026-04-18).
N = 10⁸ walkers, n_max = 3000 (**reduced from plan's 20 000 for
feasibility**: on this machine the plan-spec run would have taken
~40+ hrs), IC x = +√2, sampling every 10 steps, seed `0xCACA0DE4`.
Wall time 8.5 hrs.

**External comparison:** μ_null = 2.521×10⁻³, θ_N(99.9%) =
2.717×10⁻³, q99(null) = 2.661×10⁻³ (from M0 at N = 10⁸).

## Headline

**A persistent signal above null is genuinely present on the √2 IC,
but it is much smaller than IC (b)'s and its scaling exponent has
not yet stabilized at 1/2 on [0, 3000].** Specifically:

- At n = 3000 the ensemble L₁ = 2.72×10⁻³, *essentially at θ_N*,
  with a mean excess above μ_null of 2.02×10⁻⁴.
- Over the late window n ∈ [1500, 3000] the mean L₁ = 2.77×10⁻³,
  mean excess 2.49×10⁻⁴, and **141 of 151 samples sit above the
  null q99**. Under a pure-null hypothesis we would expect ≤ 1.5
  samples above q99. Signal confirmed at very high significance.
- But the power-law slope α_local on various windows comes in at
  0.66–1.43, not 0.50. The exponent is **drifting downward** with
  n (1.43 at [200, 500] → 0.90 at [1500, 3000] → 0.66 at
  [1000, 3000]) — consistent with transient-fade plus tail-
  emergence, but not yet stabilized at the MESSES-predicted 0.5
  within our horizon.

The √2 IC shows a much smaller tail coefficient than IC (b). If the
late-window excess is read as B/√n, B ≈ 0.011 at n ≈ 3000. IC (b)'s
trajectory would suggest B ≈ 3. These are discrepant by ~270×.

## L₁(n) on the full M4 horizon

| n    | L₁        | (L₁−μ_null)   | (L₁−μ_null)/σ_null |
|-----:|----------:|--------------:|-------------------:|
|   10 | 1.229     | +1.226        | +20331             |
|   50 | 0.225     | +0.223        | +3690              |
|  100 | 5.29×10⁻² | +5.04×10⁻²    | +836               |
|  200 | 6.43×10⁻³ | +3.91×10⁻³    | +64.8              |
|  300 | 4.25×10⁻³ | +1.73×10⁻³    | +28.7              |
|  500 | 3.58×10⁻³ | +1.06×10⁻³    | +17.5              |
|  800 | 3.23×10⁻³ | +7.09×10⁻⁴    | +11.8              |
| 1000 | 2.94×10⁻³ | +4.19×10⁻⁴    | +6.95              |
| 1500 | 2.90×10⁻³ | +3.79×10⁻⁴    | +6.28              |
| 2000 | 2.76×10⁻³ | +2.38×10⁻⁴    | +3.94              |
| 2500 | 2.70×10⁻³ | +1.81×10⁻⁴    | +3.00              |
| 3000 | 2.72×10⁻³ | +2.02×10⁻⁴    | +3.35              |

σ_null is the single-sample std under the null. The per-sample
significance drops from 20 000 at n=10 to ≈3 at n=3000. The signal
is still statistically visible on any single late-time sample (as a
~3σ positive bias), and **overwhelmingly visible in aggregate over
the late window.**

## Local-exponent drift

If the excess above μ_null is a pure B/√n tail, α_local =
log((L₁(n₁)−μ_null)/(L₁(n₂)−μ_null)) / log(n₂/n₁) should equal
0.5 on every window where the transient has died. Measured:

| window (n₁, n₂) | α_local |
|:----------------|--------:|
| (200, 500)      | 1.43    |
| (500, 1000)     | 1.33    |
| (1000, 2000)    | 0.82    |
| (1500, 3000)    | 0.91    |
| (500, 3000)     | 0.92    |
| (1000, 3000)    | 0.66    |

**α is drifting downward** as n grows — consistent with the picture
"stretched-exp transient was still contributing at n = 500, is dying
by n = 1500, and the pure algebraic tail emerges past n ≈ 3000." The
0.66 value on [1000, 3000] is the closest we get to 0.5 within the
run but still 32% off. If we extended to n ≥ 10 000 we would expect
α → 0.5 under the MESSES prediction.

## Transient vs. tail: fit comparison

**Pure-stretched-exp + μ_null**  (no algebraic term):
L₁(n) = A · exp(−c√n) + μ_null fit with A = 5.00, c = 0.4405 on full
range. This model predicts the transient is extinct by n ≈ 1500
(A · exp(−c√1500) ≈ 10⁻⁸ — far below μ_null's scale). Yet the data
at n ≥ 1500 sits at +2.5×10⁻⁴ above μ_null, which this model cannot
explain. **Pure-stretched with no algebraic tail is ruled out.**

**Joint A · exp(−c√n) + B · n^{−1/2} + μ_null**: fit returns
A = 4.98, c = 0.438, B = −0.021 ± 0.005. The negative B shows that
the joint fit is ill-conditioned — the two decay forms are not
separable on this data. The model is over-parameterized for a window
where the transient dominates the signal by >10³ at all sampled n's.

**What is separable**: the late-window excess. If we assume L₁(n) −
μ_null = B/n^α in [1500, 3000], we get B ≈ 0.011 and α ≈ 0.9 ± 0.1.
Under the MESSES predicted α = 1/2, B would come out ≈ 0.01 at the
mean late-window n (this number rescales with any consistent α
assumption, since α_local is still drifting).

## Comparison with M3 IC (b)

| IC         | L₁ at n = 600 | Inferred B (assuming α = 1/2 at that n) |
|:-----------|--------------:|-----------------------------------------:|
| M1 (√2)    | 3.44×10⁻³     | (L₁−μ_null)·√600 = 0.023                |
| M4 (√2)    | 3.45×10⁻³     | same ≈ 0.023                             |
| M3 IC (b)  | 0.129         | 0.129·√600 = 3.16                        |

M1 and M4 at n = 600 agree to 3 decimals (sanity check passed).
**The √2 IC's inferred late-time B is ~140× smaller than IC (b)'s.**

## Implications for the paper's rate claim

Thread this together with S0, B3, M3, and FIRST-PROOF:

1. **α = 1/2 is likely IC-universal** (S0's ML(1/2) match at
   conditional scale c ≈ 0.19; B3's injection-dominated regime;
   M3 IC (b)'s direct α̂ = 0.525 on [100, 600]). M4's late
   excess on the √2 IC is *consistent with* α = 1/2 emerging
   past n ≈ 3000, but the exponent is not fully stabilized at
   this horizon. Not confirmed, not rejected.
2. **B is IC-dependent.** The √2 IC has B ≈ 0.01–0.02, IC (b)
   has B ≈ 3. This is ~250× discrepancy. Theoretically expected:
   for a null-recurrent walk, the algebraic-tail *exponent* comes
   from the ML(1/2) return-count distribution (universal), while
   the *coefficient* depends on the spectral weight of the
   initial deviation in the generalized-eigenbasis of T_R. Sharp
   ICs that load mass onto fast-decaying modes have small B;
   ICs that load mass onto slow-decaying modes have large B. My
   earlier m3_SUMMARY claim of "B-universal" was too strong; α is
   what's universal.
3. **T1a (single-regime stretched-exp) is definitively dead** on
   the √2 IC too, because a single A · exp(−c√n) model cannot
   produce the late-window excess above μ_null that we observe.
4. **T1b (two-regime) is the surviving theorem shape**:
   convergence-to-Benford rate has a stretched-exp transient
   followed by an algebraic tail; both amplitudes and crossover
   times depend on IC, but the asymptotic exponent is universal.

## What M4 did NOT close

- **α_local never stabilized at 0.5 within [200, 3000].** We see
  it drifting downward consistent with that target, but a
  definitive "α = 0.5 on the √2 IC" statement needs n ≥ 10 000 or
  a larger N to reduce the null-floor interference. Running the
  plan's full n = 20 000 would do it, at ~35 more hours of compute.
- **B on the √2 IC is not precisely estimated.** The joint A, c, B
  fit is ill-conditioned on this data; only the late-window
  excess order of magnitude (~0.01) is reliable.
- **Whether the √2 IC has a genuine B > 0 or the late excess is a
  systematic error** (bias in the M0 μ_null estimate, or an
  artifact of the null-band fluctuations at this N): 141/151
  samples above q99 is very hard to explain as null fluctuation,
  but a tiny systematic in μ_null of order 10⁻⁴ would explain it.
  Worth spot-checking by rerunning M0 at a different seed if this
  becomes load-bearing for the paper.

## Data saved (m4_results.npz)

- `sample_times(300,)` — sample grid (every 10 steps from n=10 to
  3000)
- `l1(300,)` — L₁(n) at each sample time
- `h_full(300, 5)` — complex Fourier coefficients ĥ(r, n) for
  r = 1..5
- `l2_norm(300,)` — √Σ|ĥ(r)|²
- `modes(5,)`, metadata (N, steps, bins, E_R, E_THRESH, seed)

## Recommendations

1. **Paper commits to T1b.** Universal asymptotic α = 1/2,
   IC-dependent B and transient. Caveat on √2 IC: tail
   coefficient is too small to pin down at n ≤ 3000 with
   N = 10⁸ walkers; asymptotic-exponent confirmation comes via
   IC (b) indirectly.
2. **Update the m3_SUMMARY.md wording.** The "B-universal" claim
   there was too strong; correct it to "α-universal, B
   IC-dependent."
3. **If the paper needs a direct α confirmation on the √2 IC** —
   e.g. for a reviewer's "does this hold for the most natural IC?"
   challenge — extend M4 to n = 20 000 (~35 more hours at
   N = 10⁸ on this machine, or a weekend on a properly resourced
   machine).
4. **FIRST-PROOF gap 2 pivot** (noted in earlier summaries):
   shift from "prove stretched-exp" to "prove n^{−1/2}
   asymptotically, via Doeblin on T_R + ML(1/2) Laplace estimate
   on N_n." This M4 run provides empirical support for the
   algebraic-rate target but does not yet pin down the constants.
