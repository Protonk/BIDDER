# T1B-EVIDENCE-MAP verification report

Running log per the plan in
`T1B-EVIDENCE-MAP-VERIFY-PLAN.md` (v2). Each section is dated and
append-only until the final recommendation.

---

## Section 1: Chronology + inventory (Turn 1)

Date: 2026-04-19.

### Chronology

| file                                | mtime           | relative to map        |
|:------------------------------------|:----------------|:-----------------------|
| **T1B-EVIDENCE-MAP.md (base)**      | Apr 18 19:53    | —                      |
| Cited sources (from map's §"Sim inventory") |     |                        |
| m1_b1_b2_SUMMARY.md                 | Apr 17 19:24    | pre-map by ~24h        |
| s0_SUMMARY.md                       | Apr 17 19:30    | pre-map by ~24h        |
| b3_SUMMARY.md                       | Apr 17 19:46    | pre-map by ~24h        |
| m4_SUMMARY.md                       | Apr 18 04:59    | pre-map by ~15h        |
| t1b_unit_ball_SUMMARY.md            | Apr 18 09:37    | pre-map by ~10h        |
| root_two_checks_SUMMARY.md          | Apr 18 09:42    | pre-map by ~10h        |
| m3_SUMMARY.md                       | Apr 18 09:43    | pre-map by ~10h        |
| fp32_SUMMARY.md                     | Apr 18 18:13    | pre-map by ~1.5h       |
| fp16_SUMMARY.md                     | Apr 18 18:48    | pre-map by ~1h         |
| fp128_SUMMARY.md                    | Apr 18 19:42    | pre-map by 11 min      |
| Mess-era post-map sims              |                 |                        |
| laplace_diagnostic_SUMMARY.md       | Apr 19 14:12    | post-map by ~18h       |
| conditional_decay_SUMMARY.md        | Apr 19 17:36    | post-map by ~22h       |
| return_marginal_SUMMARY.md          | Apr 19 18:02    | post-map by ~22h       |
| tau_R_tail_SUMMARY.md               | Apr 19 18:40    | post-map by ~23h       |

**Not cited by the map but noted for context:**
- comparison_walks_SUMMARY.md (Apr 18 20:20) postdates the map
  by 27 min. Not in the map's "Sim inventory" table (§"what runs
  produced what"). Its post-dating is therefore not a drift
  concern for the internal faithfulness audit, though Turn 5 may
  still pick it up as paper-needs substrate.

### Branch determination

All cited M/S/B-run summaries predate the map. The closest
(fp128) predates by 11 minutes — trivially. All four Mess-era
sims postdate the map by 18–23 hours.

→ **Branch B: map predates Mess-era sims only.** Proceed to
Turn 2. Turn 6 is mandatory (not skippable).

### Inventory — clause-keyed claim list

Preface: Precision-robustness header (lines 7–14) states

- **p.1** [qual]: fp64 empirically sufficient for every T1b
  observable. Content overlaps with (iv). Cites: fp16, fp32,
  fp128.
- **p.2** [quant]: sub-fp64 events scale linearly with fp_eps;
  fp64 below detection. Overlaps with (iv). Cites: fp16, fp32.
- **p.3** [quant]: 128-bit MPFR bit-exactly identical L₁ and α̂
  to fp64 at matched seed on M3 IC (b). Overlaps with (iv).
  Cites: fp128.

#### Clause (i) Equidistribution — "consistent; two caveats"

- **i.1** [qual]: Every IC tested shows monotonically decreasing
  L₁ across observable horizon and reaches vicinity of null
  floor. Table at map lines 57–71 draws on: M1, M3 (a,b,c), M4,
  R1, R2, R3, Run 1 D1–D3, N1–N3, I1–I2, Run 2 sym/asym, Run 3
  S1–S2. Cites: m1_b1_b2, m3, m4, root_two_checks,
  t1b_unit_ball.
- **i.2** [quant]: M1 and M4 on √2 IC hover 1.27× above θ_N
  without crossing. M1 row: 3.44×10⁻³ at 1.27× θ_N. M4 row:
  2.72×10⁻³ at 1.0× θ_N with persistent ≈200σ excess in late
  window. Cites: m1_b1_b2, m4.
- **i.3** [quant]: M3 IC (b) still clearly decaying at n = 600,
  at 15× the N = 10⁷ floor (0.129 at n=600). Cites: m3.

#### Clause (ii) Asymptotic rate α = 1/2 — "one direct sighting + two consistency checks"

- **ii.1** [quant, DIRECT SIGHTING]: M3 IC (b), m = log₁₀ √2
  delta, E ~ Uniform{−5..5}, N = 10⁷:
  L₁(n) ≈ 3.16 · n^{−0.525} on [100, 600] with
  R²(log n) = 0.9986. 500-step log-log fit, essentially zero
  curvature. α̂ consistent with 1/2 within a few percent.
  Cites: m3 (IC (b)).
- **ii.2** [quant, consistency check 1]: S0 Laplace transform
  test passes. Conditional-on-excursion distribution N_n/√n
  matches ML(1/2): max |residual(log L̂)| shrinks
  ±0.018 (n=100) → ±0.006 (n=500); scale c_fit stable at
  0.179–0.195 across n ∈ {100, 200, 300, 500}. Cites: s0.
- **ii.3** [quant, acknowledged null]: S0 β̂ tail-slope test
  fails (β̂ ≈ 9 rather than ≈ 0.5), judged mis-specified per
  s0_SUMMARY.md (tested an expectation from geometric-stable/
  Linnik family; ML(1/2) has half-normal body). Failure does
  not indict α = 1/2. Cites: s0.
- **ii.4** [qual]: S0 validates the ML(1/2) assumption that
  MESSES's per-return Laplace-transform argument relies on;
  does not directly measure α on L₁.
  Cites: s0.
- **ii.5** [quant, consistency check 2]: B3 empirical
  mode-coupling matrix K̂ from 10⁷ walkers, 40M excursions:
  ρ(K̂) = 0.924. Injection-dominated criterion (ρ(M) > γ₁^{c'})
  met at ratio 2.70 vs balanced-regime boundary 1. Cites: b3.
- **ii.6** [qual]: B3's injection-dominated regime ⇒ algebraic
  (not stretched-exp). Combined with S0's ML(1/2), gives the
  ½ exponent. B3 alone does not pin exponent.
  Cites: b3, s0.
- **ii.7** [qual, self-correction]: "Three-way lock" framing
  is overclaim; correct description is "one measurement + two
  independent supports."
  Cites: m3, s0, b3.
- **ii.8** [quant, corroboration on √2]: M4 at N = 10⁸,
  n = 3000: 141 of 151 late-window (n ∈ [1500, 3000]) samples
  above null q99 (vs ≤ 1.5 expected under pure null). α_local
  drifts 1.43 (n=500) → 0.91 (n=1500–3000), consistent with
  transient fade + tail emergence but not yet at 0.5.
  Cites: m4.
- **ii.9** [quant, B-dependence]: Two empirically-grounded B
  values — M3 IC (b) ≈ 3 (direct fit, R²(log n) = 0.9986);
  M1/M4 (√2) ≈ 0.01 (order-of-magnitude from M4 late excess
  n ≈ 2000–3000). Cites: m3, m4.
- **ii.10** [qual, self-correction]: Initial M3 draft claimed
  B-universality; this has been corrected. B depends on IC's
  projection onto slow T_R modes. 300× ratio between M3 IC (b)
  and √2 is the only direct evidence — two-point comparison,
  not a panel.
  Cites: m3, m4.

#### Clause (iii) Pre-asymptotic stretched-exp transient — "IC-specific, not universal"

- **iii.1** [quant, M1 anchor]: M1 √2 IC: c ≈ 0.5, R² = 0.999
  on [20, 200]. Cites: m1_b1_b2.
- **iii.2** [quant, 13-IC panel]: c_hat across 13 ICs on
  [20, 150]:
    - dyadic rationals (D1=1, D2=3/2, D3=9/8): 0.335–0.347
    - non-dyadic rationals (N1=7/5, N2=17/12, N3=99/70):
      0.374–0.543 (wide)
    - irrational sharp (√2, φ): 0.466–0.498
    - spread-E mixtures (M3 IC (c), Run 3 S2): 0.356
    - E-uniform with delta-m (M3 IC (b)): 0.137 (transient
      effectively dead)
    - near-uniform ICs (M3 IC (a), Run 3 S1): < 0.05 (at floor)
  Cites: t1b_unit_ball, m3, root_two_checks.
- **iii.3** [qual]: c ≈ 0.5 from M1 is specific to
  (m = log₁₀√2, E = 0, sign = +1) joint delta. Not a load-
  bearing constant for T1b; transient descriptor for one IC.
  Cites: m1_b1_b2, m3, root_two_checks, t1b_unit_ball.

#### Clause (iv) Rational exception — "algebraic dichotomy respected up to fp_eps-scaling catastrophic cancellation, with fp64 sufficient in both directions"

- **iv.1** [qual]: Algebraic dichotomy: x₀ ∈ ℤ[1/2] (dyadic
  rationals) have orbits hitting 0; strict subset of ℚ.
  Cites: t1b_unit_ball, root_two_checks.
- **iv.2** [quant, precision ladder table]:
    - fp16: fp_eps = 4.9×10⁻⁴, rate ≈ 2×10⁻⁵ /walker-step
    - fp32: fp_eps = 6×10⁻⁸, rate ≈ 1.5×10⁻⁹ /walker-step
    - fp64: fp_eps = 1.1×10⁻¹⁶, rate < 3×10⁻¹¹ /walker-step
      (below detection at our volumes)
    - fp128: fp_eps = 6×10⁻³⁵, bit-exactly identical L₁, α̂ to
      fp64 at matched RNG seed on M3 IC (b)
  Three-point fp16/32/64 rate line scales linearly with fp_eps.
  Cites: fp16, fp32, fp128.
- **iv.3** [quant, zero-count]: 7 non-dyadic/irrational/smooth-
  Gaussian ICs (N1–N3, I1–I2, S1–S2) × 6×10⁹ walker-steps
  each = 4.2×10¹⁰ opportunities → **zero** numerical zero
  events. Dyadic ICs produced 0.019–0.791 events per walker
  depending on |x₀ − 1|. Cites: t1b_unit_ball (dyadic ladder
  Run 1).
- **iv.4** [quant, convention comparison]: R2 (restart at ±1)
  and R3 (absorb) agree on L₁ within ~7% over [50, 200]. Late-
  time ratio drifts to 0.77 at n = 600, dominated by floor
  fluctuations on independently-seeded runs. Cites:
  root_two_checks.
- **iv.5** [qual]: α for dyadic starts is not resolved by R2 or
  R3 — both hit the N = 10⁷ floor before α would be measurable.
  Cites: root_two_checks.

#### Clause (v) Symmetry clause — "weak asymmetry doesn't break T1b on envelope; strong asymmetry untested"

- **v.1** [quant]: T1B-UNIT-BALL Run 2: asymmetric
  (P(a) − P(a⁻¹) = 0.01) vs symmetric control, same IC, same
  N: L₁ ratios in [0.96, 1.06] throughout [1, 600]. Cites:
  t1b_unit_ball (Run 2).
- **v.2** [quant]: Stretched c_hat: 0.419 (asym) vs 0.416 (sym)
  on [20, 300], difference 0.7%. Cites: t1b_unit_ball.
- **v.3** [quant]: Frozen fraction stays < 3×10⁻⁴ through
  n = 600; E_THRESH envelope not active. Cites: t1b_unit_ball.
- **v.4** [qual]: Strong asymmetry (d ≳ 0.05) untested; would
  require modified kernel or longer horizon.
  Cites: t1b_unit_ball.
- **v.5** [qual, load-bearing]: "symmetric ⇒ null-recurrent E
  ⇒ ML(1/2) returns ⇒ α = 1/2" is an analytic statement that
  does depend on symmetry in principle; Run 2 confirms weak
  symmetry-breaking doesn't break observable-window behavior.
  Cites: t1b_unit_ball (empirical envelope check); map framing
  supplies the analytic implication.

---

### Inventory totals

- Precision header: 3 claims (all overlap with clause iv).
- Clause (i): 3 claims (1 qual, 2 quant).
- Clause (ii): 10 claims (6 quant, 4 qual).
- Clause (iii): 3 claims (2 quant, 1 qual).
- Clause (iv): 5 claims (3 quant, 2 qual).
- Clause (v): 5 claims (3 quant, 2 qual).

Total: **29 load-bearing claims** across 5 clauses + header.

### Stop-gate decision

Branch B confirmed. Proceed to Turn 2 (internal verification for
clauses (i), (iv), (v)). Turn 6 (Mess drift audit) is mandatory.

---

## Section 2: Internal verification — clauses (i), (iv), (v) (Turn 2)

Date: 2026-04-19.

Cross-checked each claim in clauses (i), (iv), (v) against its
cited sim summary. Classification: ✓ verified / ⚠ needs review /
✗ stale-or-wrong.

### Clause (i) Equidistribution

| id   | classification | note |
|:----:|:--------------:|:-----|
| i.1  | ⚠              | Map says "monotonically decreasing" but `m1_b1_b2_SUMMARY.md:21` explicitly notes 36 non-monotone upward moves in the null band (largest Δ = +2.69×10⁻⁴ at n=555→560). M4 similarly has L₁ going 2.76×10⁻³ → 2.70×10⁻³ → 2.72×10⁻³ at n∈{2000, 2500, 3000}. The jitter is null-band noise, not a real reversal; **the spirit (convergence to vicinity of floor) holds across all ICs**. Classify as ⚠ on wording only — the word "monotonically" is technically incorrect for M1/M4, but no downstream claim rests on literal monotonicity. |
| i.2  | ⚠              | M1 portion ✓: "3.44×10⁻³ at 1.27× θ_N" matches `m1_b1_b2_SUMMARY.md:33` exactly. M4 portion mostly ✓ (2.72×10⁻³ at n=3000, 1.0× θ_N — matches `m4_SUMMARY.md:50`). **Caveat: the map's "≈200σ excess" figure is not directly sourced.** The m4 summary reports (a) per-sample z-score ≈ 3.35 at n=3000, (b) 141/151 late-window samples above q99 vs ≤ 1.5 expected (which is ~114σ in a Bernoulli-z-score sense), (c) aggregate late-window mean excess z ≈ 51σ in standard-error terms. None of these three numbers is "200σ." The map's 200σ is plausibly a hand-computed combined significance statistic but its derivation is not made explicit anywhere I could find. Classify ⚠: the underlying signal is overwhelmingly real, but the specific "200σ" figure should be either sourced or replaced with "141/151 above q99, overwhelming significance." |
| i.3  | ✓              | "M3 IC (b) at 0.129, 15× floor" matches `m3_SUMMARY.md:42` exactly. |

### Clause (iv) Rational exception

| id   | classification | note |
|:----:|:--------------:|:-----|
| iv.1 | ✓              | Dichotomy (x₀ ∈ ℤ[1/2] hits 0; non-dyadic avoids) cleanly supported by `t1b_unit_ball_SUMMARY.md:43–67` (Run 1 zero-hit table: D1=0.791, D2=0.172, D3=0.019 dyadic; N1=N2=N3=I1=I2=0 non-dyadic/irrational). |
| iv.2 | ✓              | Precision-ladder table is supported as written by the **synthesized ladder** in `fp16_SUMMARY.md:135–153`: fp16 ≈ 2×10⁻⁵, fp32 ≈ 1.5×10⁻⁹, fp64 < 3×10⁻¹¹, fp128 bit-exact. `fp32_SUMMARY.md` carries a tighter standalone headline bound (< 2×10⁻¹¹) for one sub-run, but the map's row matches the cross-summary ladder the fp16 writeup explicitly assembles. This is not a faithfulness problem; at most it is a later wording-tightening opportunity if the map wants the sharpest fp64 bound. |
| iv.3 | ✓              | "7 ICs × 6×10⁹ walker-steps each = 4.2×10¹⁰ opportunities → zero numerical zeros" matches: 5 Run-1 non-dyadic/irrational + 2 Run-3 smooth-Gaussian = 7 ICs (`t1b_unit_ball_SUMMARY.md:52–56, 181–189`). Dyadic range 0.019–0.791 matches the zero-hit table exactly. |
| iv.4 | ✓              | "R2 vs R3 agree within ~7% over [50, 200]" matches `root_two_checks_SUMMARY.md:104` verbatim. Late ratio "0.77 at n=600" matches `root_two_checks_SUMMARY.md:102` (measured 0.765, rounded). |
| iv.5 | ✓              | "α not resolved by R2/R3 — hit floor before measurable" matches `root_two_checks_SUMMARY.md:222–225` ("the N = 10⁷ floor of ≈ 8.6×10⁻³ masks the late-time scaling of R1, R2, R3"). |

### Clause (v) Symmetry

| id  | classification | note |
|:---:|:--------------:|:-----|
| v.1 | ✓              | "L₁ ratios in [0.96, 1.06] throughout [1, 600]" matches `t1b_unit_ball_SUMMARY.md:28` verbatim. |
| v.2 | ✓              | "c_hat: 0.419 (asym) vs 0.416 (sym) on [20, 300], diff 0.7%" matches `t1b_unit_ball_SUMMARY.md:160, 164` exactly (computed diff 0.72%). |
| v.3 | ✓              | "Frozen fraction < 3×10⁻⁴ through n=600; E_THRESH envelope not active" matches `t1b_unit_ball_SUMMARY.md:128, 131` (max 2×10⁻⁴ at n=600, below 3×10⁻⁴). |
| v.4 | ✓              | "Strong asymmetry (d ≳ 0.05) untested" — qualitative, matches `t1b_unit_ball_SUMMARY.md:255–261` explicitly. |
| v.5 | ⚠              | The **empirical half** is supported: `t1b_unit_ball_SUMMARY.md:255–261` does support "weak asymmetry leaves observable-window behavior unchanged." But the stronger chain "symmetric ⇒ null-recurrent E ⇒ ML(1/2) returns ⇒ α = 1/2" is **map-level analytic framing**, not something the cited sim summary itself verifies. So this is not contradicted, but it is not source-verified in the same way as the purely empirical rows. Classify ⚠ on scope: the summary supports the envelope check, while the analytic implication belongs to proof framing rather than sim-summary fact. |

### Turn 2 summary

- **Total claims checked:** 13 (clause i: 3; iv: 5; v: 5).
- **✓ Verified:** 10.
- **⚠ Needs review:** 3 (i.1, i.2, v.5).
- **✗ Stale/wrong:** 0.

**No load-bearing ✗.** The three ⚠ items are about wording
precision or numeric averaging conventions, not about direction
or magnitude of findings:

- i.1 "monotonically decreasing" → should read "overall
  decreasing with small null-band jitter."
- i.2 "≈200σ excess in late window" → should be sourced or
  replaced with "141/151 above q99, overwhelming
  significance."
- v.5 should be split conceptually: the weak-asymmetry
  observable-window check is empirically supported, but the
  stronger analytic chain belongs to proof framing and is not
  source-verified by `t1b_unit_ball_SUMMARY.md`.

### Stop-gate decision

No load-bearing ✗ found. Proceed to Turn 3 (clause ii + clause ii
spot-checks). The three ⚠ items are recorded for inclusion in
final recommendation ("refresh then proceed" vs "proceed" gate).

---

## Section 3: Internal verification — clause (ii) + spot-checks (Turn 3)

Date: 2026-04-19.

Clause (ii) is the hardest: one direct sighting of α = 1/2 plus
consistency checks, spanning M3, S0, B3, M4. All clause (ii)
raw-data spot-checks live in this turn.

### Clause (ii) claim-by-claim

| id    | classification | note |
|:-----:|:--------------:|:-----|
| ii.1  | ⚠              | α̂ and R² verified exactly (see spot-check 1 below). **But the equation form "L₁(n) ≈ 3.16 · n^{−0.525}" is numerically self-inconsistent**: under the fitted α = 0.525 the coefficient is A = 3.807 (from regression intercept); the "3.16" appears in m4_SUMMARY.md as "0.129 · √600 = 3.16," which is A under an α = 0.5 _imposed_ constraint. The map's one-line equation mixes A from the α = 0.5 reading with the exponent from the α = 0.525 fit. Direct-sighting facts (α̂ = 0.525, R² = 0.9986, IC (b) configuration) are all verified; prefactor should read "A ≈ 3.8" if α = 0.525 is kept, or "L₁(n) ∼ 3 · n^{−1/2}" if the coefficient is quoted at assumed α = 0.5. |
| ii.2  | ✓              | Laplace-match numerics verified to 3 digits by spot-check 3. c_fit {0.179, 0.179, 0.183, 0.195} at n ∈ {100, 200, 300, 500} matches `s0_SUMMARY.md:27–30` exactly. Max |residual| shrinks 0.018 → 0.006 as claimed. |
| ii.3  | ✓              | β̂ ≈ 9 mis-specification properly documented in `s0_SUMMARY.md:34–40`. Failure correctly judged non-indicting. |
| ii.4  | ✓              | Qualitative framing ("S0 validates ML(1/2) assumption; does not directly measure α on L₁") is faithful to `s0_SUMMARY.md:57, 68–72`. |
| ii.5  | ✓              | ρ(K̂) = 0.924 verified exactly by spot-check 2 (measured 0.9243). Injection-dominated ratio 2.70 matches `b3_SUMMARY.md:117`. |
| ii.6  | ✓              | "Injection-dominated ⇒ algebraic, not stretched-exp" matches `b3_SUMMARY.md:16–19, 127`. Combination with S0's ML(1/2) to get ½ exponent is the map's synthesis of the two checks, logically consistent. |
| ii.7  | ✓              | Self-correction on "three-way lock" framing is the map's own epistemic-honesty adjustment; internally consistent with the measurement-vs-consistency-check distinction laid out in the sources. |
| ii.8  | ✓              | "141/151 above q99" matches `m4_SUMMARY.md:21–23` exactly. α_local 1.43 (n=500) → 0.91 (n=1500–3000) matches `m4_SUMMARY.md:64–71`, specifically windows (200, 500) → (1500, 3000). Minor framing note: "(n=500)" is shorthand for "window (200, 500)." |
| ii.9  | ⚠              | The **order of magnitude** is right, but the source attribution is mixed. `m4_SUMMARY.md:103–107, 122–123` supports **B ≈ 3** for IC (b) under the imposed-α=1/2 reading (`0.129·√600 = 3.16`), and `m4_SUMMARY.md:32` supports √2 **B ≈ 0.01**. But the map's anchor text says M3 IC (b) "≈ 3" comes from a **direct power-law fit on [100, 600]**, whereas spot-check 1 shows the free fit with α = 0.525 has intercept A = 3.807. So the value "≈ 3" is usable as an inferred B, but its stated anchor should be rewritten to match the actual convention rather than presented as the direct M3 fit coefficient. |
| ii.10 | ✓              | Self-correction retracting B-universality is explicitly documented in `m3_SUMMARY.md:142–145` and `m4_SUMMARY.md:130–131`. 300× ratio = 3 / 0.01 is direct. |

### Spot-checks (raw data)

**Spot-check 1: α̂ fit on M3 IC (b) against `m3_results.npz`.**

```
Fit log L₁ = a - α · log n on [100, 600], 181 points:
  α̂ = 0.5250
  R²(log n) = 0.99857
  A = exp(intercept) = 3.807
```

Map claim: α = 0.525, R² = 0.9986. **Exact match on both to
four digits.** A = 3.807 ≠ 3.16 (noted above in ii.1).

**Spot-check 2: ρ(K̂) against `b3_results.npz`.**

```
b3_results.npz → spectral_radius = 0.9243
```

Map claim: ρ(K̂) = 0.924. **Match to 3 digits.**

**Spot-check 3: ML(1/2) Laplace-match against `s0_results.npz`.**

```
cond_n100_c_fit = 0.1793   (map: 0.179)   ✓
cond_n200_c_fit = 0.1789   (map: 0.179)   ✓
cond_n300_c_fit = 0.1833   (map: 0.183)   ✓
cond_n500_c_fit = 0.1948   (map: 0.195)   ✓
cond_n100 residuals max |·| = 0.01790     (map: ±0.018)  ✓
cond_n500 residuals max |·| = 0.00558     (map: ±0.006)  ✓
```

**All six values match the map to three significant figures.**

### Direct-vs-derived status for "direct sighting" label

The map labels ii.1 as the "direct sighting" of α = 1/2.
Spot-check 1 confirms α̂ = 0.5250 on [100, 600] at N = 10⁷ is a
genuine 500-step log-log regression, not a derived quantity. The
label is accurate: this is the one place where α is measured by
fitting a power law to L₁ directly, rather than inferred from
auxiliary statistics (S0's ML-match and B3's regime classification
are labelled consistency checks, not direct measurements of α on
L₁).

### Turn 3 summary

- **Total claims checked:** 10 (clause ii: 10).
- **✓ Verified:** 8.
- **⚠ Needs review:** 2 (ii.1 equation-form prefactor inconsistent with fitted exponent; ii.9 B-anchor mixes fit conventions).
- **✗ Stale/wrong:** 0.
- **Spot-checks:** 3/3 pass at 3-digit precision.

**No load-bearing ✗.** The two ⚠ items are both convention/anchor
issues, not failures of the underlying evidence:

- ii.1: the one-line formula mixes the α = 0.525 fit with the
  α = 0.5-imposed prefactor convention.
- ii.9: the order-of-magnitude B comparison is supported, but the
  map's stated anchor "direct power-law fit" is not faithful to
  the source chain for the IC (b) coefficient.

### Stop-gate decision

No load-bearing ✗. Proceed to Turn 4 (clause iii + clause iii
spot-checks). Running total of ⚠ after Turns 2–3: **5** (i.1,
i.2, v.5, ii.1, ii.9).

---

## Section 4: Internal verification — clause (iii) + spot-checks (Turn 4)

Date: 2026-04-19.

Clause (iii) is the "pre-asymptotic stretched-exp transient —
IC-specific, not universal" clause: three claims (M1 anchor fit,
13-IC panel, IC-specificity framing). All clause (iii) raw-data
spot-checks live here; clause (ii) spot-checks are not revisited.

### Clause (iii) claim-by-claim

| id    | classification | note |
|:-----:|:--------------:|:-----|
| iii.1 | ⚠              | c_hat and R² are numerically correct by spot-check 1 below: M1 [20, 200] gives c_hat = 0.5058, R²(√n) = 0.9989, matching the map's "c ≈ 0.5, R² = 0.999." On [20, 150]: c_hat = 0.4980, matching the panel anchor 0.498. **But the source chain is not clean.** The assigned source `m1_b1_b2_SUMMARY.md` does not itself document the [20, 200] stretched-exp fit; it explicitly defers c-fitting to later analysis. The fit is documented in `m3_SUMMARY.md:72` and reproducible from the raw M1 `.npz`, so the claim is empirically right but citation hygiene needs tightening. |
| iii.2 | ✓              | Full 13-IC panel verified across four sources. Spot-check 2 confirms six panel entries at 3-digit precision: I1=0.491, I2=0.467, N1=0.543, D1=0.347, S1=0.039, S2=0.356. Two more verified directly by reading m3 data (M3 IC (b)=0.137, IC (a)=0.037). Remaining entries (N2=0.374, N3=0.488) cross-confirmed from `t1b_unit_ball_SUMMARY.md:89–96`. All class ranges in the panel are accurate. |
| iii.3 | ✓              | Qualitative framing (c ≈ 0.5 on M1 is IC-specific to the √2 sharp joint-delta; not a universal T1b constant) matches the narrative in `m3_SUMMARY.md:121–156` and `t1b_unit_ball_SUMMARY.md:20–25, 108–114`. |

### Spot-checks (raw data)

**Spot-check 1: M1 stretched-exp fit against `m1_b1_b2_results.npz`.**

```
M1 [20, 200] stretched-exp fit:
  c_hat = 0.5058, R²(√n) = 0.9989, 181 pts
M1 [20, 150] stretched-exp fit (panel anchor):
  c_hat = 0.4980, R²(√n) = 0.9985
```

Map claims: iii.1 "c ≈ 0.5, R² = 0.999 on [20, 200]" and iii.2
panel "irrational sharp: 0.466–0.498." **Both verified to 3
digits.** The 0.4980 matches the 0.498 endpoint in the
irrational-sharp panel range.

**Spot-check 2: 13-IC panel entries against
`t1b_unit_ball_results/` `.npz` files.**

```
[20, 150] stretched-exp fit:
  I1 (√2)   c = 0.491, R² = 0.9990    (map range: 0.466–0.498)  ✓
  I2 (φ)    c = 0.467, R² = 0.9990    (map range: 0.466–0.498)  ✓
  N1 (7/5)  c = 0.543, R² = 0.9986    (map range: 0.374–0.543)  ✓
  D1 (1)    c = 0.347, R² = 0.9922    (map range: 0.335–0.347)  ✓
  S1        c = 0.039, R² = 0.9181    (map: < 0.05)             ✓
  S2        c = 0.356, R² = 0.9924    (map: 0.356)              ✓
```

Plus from Turn 3's read of m3 data:
```
  M3 IC (b) c = 0.137  (map: 0.137)                              ✓
  M3 IC (a) c = 0.037  (map: < 0.05)                             ✓
```

**All eight spot-checked panel entries match map values at
three-digit precision.**

### Turn 4 summary

- **Total claims checked:** 3 (clause iii: 3).
- **✓ Verified:** 2.
- **⚠ Needs review:** 1 (iii.1 citation/source-chain issue).
- **✗ Stale/wrong:** 0.
- **Spot-checks:** 2/2 pass at 3-digit precision across 8 panel entries and the M1 anchor.

### Stop-gate decision

No load-bearing ✗. Clause (iii) remains very clean numerically:
all checked values match raw data, panel entries verify across
multiple sim summaries, and the only issue is iii.1's
citation/source-chain hygiene.

**Internal audit complete.** Turns 2–4 have answered the first
audit question ("is the map faithful to its own cited sources?"):
**yes, modulo six ⚠-level wording/citation refinements** (i.1,
i.2, v.5, ii.1, ii.9, iii.1). No load-bearing ✗ across 26 claims checked.

Proceeding to external audits: Turn 5 (PNAS-PLAN coverage) and
Turn 6 (mandatory per Branch B, Mess drift). These may be run in
either order.

---

## Section 5: PNAS-PLAN coverage audit (Turn 5)

Date: 2026-04-19.

External audit: does the map cover what the paper plans to say?
Scope: five specific PNAS-PLAN sections (per verify-plan §Turn 5).
Out of scope: the rest of PNAS-PLAN (§1 intro, §3 group setup,
§6 Hamming, §8 conclusion, rhetorical arc, audience, failure
modes, references). Any outdated numerics in PNAS-PLAN (e.g.
c = 0.55 stale) are judged against the _current_ sim-supported
value, not the stale one.

### Coverage table

| target | status | justification |
|:-------|:------:|:--------------|
| **T5.1** Theorem 1 wording + `### Theorem 1 variants — pre-committed wording` (T1a/T1b/T1c) | ✓ | Map explicitly commits to T1b throughout. The "T1b (current working statement)" section at map lines 16–44 gives the theorem in clauses (i)–(iv); "What the paper can safely say" (map lines 280–318) specifies variant-specific wording. The map's commitment answers which of the three pre-committed variants applies. |
| **T5.2** Theorem 2 block (empirical rate) | ↻ scope-shift | Map covers the empirical c ≈ 0.498 on the M1 √2 IC (clause iii.1, verified Turn 4) and explicitly marks it as an IC-specific transient descriptor, not a universal constant (clause iii.3, map line 322: "A universal c in exp(−c√n). T1a is dead."). **The coverage exists but the PNAS-PLAN Theorem 2 wording (lines 129–140) is stale** — it states c = 0.55 ± [error] as if for a single-regime theorem. Under T1b, Theorem 2 should become "IC-specific transient c for sharp IC; asymptotic α = 1/2 with IC-dependent B." **This is a PNAS-PLAN gap, not a map gap.** Recommend rewriting PNAS-PLAN §2's Theorem 2 block against the map's T1b framework. |
| **T5.3** `### 4. Mechanism / proof` — two empirical anchors | ✓ | PNAS-PLAN §4 names two anchors: "coordinate identity" (ψ, ε) and "visit rate" (E[L_n] ~ c_R√n). **Coordinate identity is BINADE-WHITECAPS territory, correctly not in map** (sim-scope exclusion). **√n visit rate ✓**: map clause ii.2/ii.4 covers S0's ML(1/2) Laplace-match which is the empirical realization of the null-recurrent √n return structure; clause ii.5/ii.6 covers B3's per-visit contraction ρ(K̂) = 0.924. Both empirical anchors §4 would need are in the map. |
| **T5.4** `### 5. Figures with captions` — Figure 1 three-walks substrate | ↻ not-in-map | Figure 1 shows add-only / alt / mixed three-walks on log-log axes. **The three-walks substrate lives in `comparison_walks_SUMMARY.md`, which is not in the map's Sim inventory.** Map's inventory covers BS(1,2) runs (m1, m3, m4, b3, s0, t1b_unit_ball, root_two_checks, fp ladder), but not the add/alt/mixed comparison. comparison_walks_SUMMARY.md postdates the map by 27 min (per Turn 1 chronology). **Gap for map; existing substrate exists elsewhere.** Promotion target: either extend the map, or write a separate paper-side figure-substrate doc (e.g. `paper/FIG1-SUBSTRATE.md`). |
| **T5.5** `### 7. Robustness and sensitivity` — biased / base-change / pure-add / precision | ↻ partial | **Precision ✓** in map clause (iv) (fp16/32/64/128 ladder). **Weak asymmetry ✓** in map clause (v) — tangential to "biased generators" as named in §7. **Gaps**: (a) Biased generators (phase 3 convergence to Benford under d > 0 asymmetry) — map's clause (v) only covers d = 0.01 on the observable window, not the phase-3 convergence claim; the broader biased-generators result may live in `SIM-REPORT.md` or a phase-3-specific summary not cited by the map. (b) Base change (L₁-to-Benford flat across b ∈ [2, 40]) — not in map, no obvious cited summary; **may be a genuine evidence gap** if it's claimed as empirically supported. (c) Pure-addition non-convergence — not in map, would live in `comparison_walks_SUMMARY.md`. |

### Summary of gaps

**Not in the map, evidence exists elsewhere in sim/**:
- Figure 1 three-walks substrate → `comparison_walks_SUMMARY.md`.
- Pure-addition non-convergence → `comparison_walks_SUMMARY.md`.

**Not in the map, evidence location unclear (possible true gap)**:
- Biased-generators phase-3 convergence (beyond the d = 0.01 weak-asymmetry check).
- Base change (b ∈ [2, 40] flat L₁-to-Benford).

**PNAS-PLAN gap (not map gap)**:
- Theorem 2 wording is stale against T1b. Map provides the correct foundation; PNAS-PLAN §2's Theorem 2 text needs rewriting.

### Implication for paper-side promotion

If the goal is `paper/T1B-EVIDENCE.md` = one consolidated
paper-side synthesis, the map needs extension or companion docs
for T5.4 (three-walks) and parts of T5.5 (biased, base-change,
pure-add). Candidates:

1. Extend the map's §Sim inventory to include
   `comparison_walks_SUMMARY.md` and add a clause on
   "Robustness envelope" covering the §7 bullets.
2. OR write separate paper-side docs:
   - `paper/FIG1-SUBSTRATE.md` for Figure 1.
   - `paper/ROBUSTNESS-ATLAS.md` for §7 bullets (as proposed
     earlier in the paper-promotion discussion).
3. OR rewrite PNAS-PLAN §2's Theorem 2 block and §7 against the
   map's T1b framework, accepting that some substrate lives in
   sim/ and is cited there rather than consolidated in one doc.

The verification does not choose among these — it identifies the
coverage gaps.

### Turn 5 summary

- **Targets checked:** 5.
- **✓ Covered by map:** 2 (T5.1, T5.3).
- **↻ Covered elsewhere (gap for map, evidence exists):** 2 (T5.4
  three-walks substrate; partial T5.5 precision).
- **Partial / mixed:** 1 (T5.5 — precision covered, others not).
- **Genuine gaps (evidence unclear)**: base change; broad biased
  generators beyond d = 0.01.
- **PNAS-PLAN gap (not map gap)**: Theorem 2 wording stale.

### Stop-gate decision

Turn 5 does not have internal-audit-style stop gates. The gaps
identified inform the final recommendation. Proceed to Turn 6
(mandatory per Branch B: Mess drift audit).

---

## Section 6: Mess drift audit (Turn 6, mandatory)

Date: 2026-04-19.

The map predates four post-map Mess-era sims (per Turn 1
chronology, Branch B). For each, check consistent / silent /
contradicted against the map. Use the scoped findings from each
summary, not a stronger reading.

### Per-sim assessment

**1. Laplace-diagnostic** (`sim/laplace_diagnostic_SUMMARY.md`).

Scoped findings:
- BS(1,2) E-process shows **positive mean drift ~0.16·√n** on
  the M1 IC (measured horizon).
- Local time L_n grows **linearly in calendar time n**, not as √n.
- "Zero-drift null-recurrent SRW" universality does not fit
  BS(1,2) verbatim.

Map's use of the null-recurrent chain: **v.5** (map lines
239–242) states "symmetric ⇒ null-recurrent E ⇒ ML(1/2) ⇒ α = 1/2"
as load-bearing analytic framing. Already flagged ⚠ in Turn 2
for being map-level framing beyond sim-verified.

**Status: ⚠ framing pressure.** Laplace-diagnostic adds concrete
empirical pressure on the v.5 analytic chain: the E-process has
observed positive mean drift and L_n has linear growth, neither
of which fits strict-null-recurrent martingale behavior. This
does **not** contradict the map's clauses (i)–(iv) content; it
sharpens the existing v.5 ⚠ into a more specific concern:
**the "null-recurrent E" bridge the map leans on for the
analytic derivation of α = 1/2 is not the literal regime the
walker is in**. The observed τ_R tail (next item) partially
rescues this: the walker's _return-time structure_ can still be
null-recurrent-like even when its _mean E_ has drift.

Recommendation: when using the map as a paper-side evidence
anchor, v.5's analytic chain needs softer framing. The
correct-under-T1b version is something like "the walker's
return-time distribution has 1/√n tail (consistent with
null-recurrent return-time statistics); the E-process as a
whole has additional structure that the paper does not claim
to fully characterize."

**2. Return-marginal** (`sim/return_marginal_SUMMARY.md`).

Scoped finding: pooled post-burn return-sample m-marginal σ̃ is
concentrated on the arc [1 − log₁₀ 2, 1) × {E = 10} at
R = {|E| ≤ 10}, under the map's kernel. This **pressures Route
1's identification step π_T ν_R = Leb_T** but does not by itself
identify the invariant law cleanly (stationarity not verified,
E₀-independence not tested — see return_marginal_SUMMARY.md
caveats).

Map's use of "invariant T-marginal" identification: **silent**.
The map is organized around φ(ν, n) = ‖π_T(νK^n) − Leb_T‖, the
full-walker m-marginal at step n, not the T_R-invariant's
T-marginal. The map's "Suggested paper structure" (map lines
340–346) proposes the per-return Laplace-transform rate
derivation but leaves ν_R's marginal implicit ("B IC-dependent;
do not claim closed form").

**Status: silent on the identification claim.** The map doesn't
make a π_T ν_R = Leb_T claim to be pressured. However, MESSES.md
Mess #2 (which is referenced by map's "§3 Algebraic rate
derivation" suggestion) does rest on this identification, and
**that identification is now under empirical pressure**.

Recommendation: when using the map as a paper-side anchor, note
that the map's implied proof route (MESSES per-return Laplace
with identification of π_T ν_R = Leb_T) now carries the
return-marginal finding as a distinct proof obstacle. This is a
proof-architecture concern, not a map content concern. MESSES.md
§Mess #2 update already carries this.

**3. τ_R tail** (`sim/tau_R_tail_SUMMARY.md`).

Scoped finding: first-excursion τ_R from the **M1 IC** has
empirical survival slope ≈ −0.495 on n ∈ [50, 10⁴]
(R² = 1.0000, 15 grid points). IC-specific, first-excursion,
n_max = 3 × 10⁴ — _not_ a uniform-in-x ∈ R theorem-level tail
bound.

Map's τ_R-related content: clause (ii.2)/(ii.4) uses S0's
conditional ML(1/2) Laplace-match (c_fit ≈ 0.19 stable) as
consistency check for α = 1/2. ML(1/2) has the 1/√n tail
structure.

**Status: ✓ consistent and reinforcing.** The τ_R tail's
first-excursion slope −0.495 is directly consistent with
ML(1/2)'s 1/√n tail shape that S0 validated. This is evidence
from a new angle (direct first-excursion survival vs S0's
Laplace-match) that converges on the same null-recurrent-like
return-time structure. **Useful addition, not drift.**

Recommendation: the paper-side doc could note that the map's
ML(1/2) anchor (S0) and the τ_R-tail sim's direct survival
measurement are two independent sightings of the same 1/√n
return-time structure, strengthening the α = 1/2 story.
(Caveat: both are IC-specific to M1; uniform-in-x not
established.)

**4. Conditional-decay** (`sim/conditional_decay_SUMMARY.md`).

Scoped finding: the analytic hypothesis H (b-steps passive on
m conditional on a-step count K; transient stretched-exp from
pure a-step Diophantine on T) was **rejected at Test A**.
Predicted TV shape: best-fit γ = 0.15 (not 0.5); at γ = 0.5
predicted c = 0.009 vs measured 0.498 (factor 55 off). **This
is narrower than "transient mechanism is not a-step":** it
rules out the clean a-only hypothesis, does not rule out a-step
involvement in a broader mechanism.

Map's transient-mechanism content: clause (iii.3) says the M1 c
≈ 0.5 is IC-specific, not a load-bearing constant. Map **does
not propose a mechanism** for the transient; it's purely a
descriptive observation that the sharp-IC trajectory looks
stretched-exp on the observable window.

**Status: silent / not in conflict.** The map doesn't propose H
or any other specific transient mechanism, so rejection of H
doesn't contradict the map. Conditional-decay's result tightens
what one _can't_ claim about the transient mechanism, but
doesn't change the map's factual content about transient c
values per IC.

Recommendation: no map refresh needed for this finding. The
conditional-decay result lives appropriately in MESSES #1
discussion.

### Turn 6 summary

| post-map sim           | status                 |
|:-----------------------|:-----------------------|
| Laplace-diagnostic     | ⚠ framing pressure on v.5 |
| Return-marginal        | silent (map doesn't claim); MESSES #2 concern |
| τ_R tail               | ✓ consistent, reinforcing |
| Conditional-decay      | silent (map doesn't claim mechanism) |

**Contradictions found: zero.**
**Silent items: two (not gaps — correctly out-of-scope for the
map).**
**Reinforcement found: one (τ_R tail strengthens S0's ML(1/2)
sighting).**
**Framing pressure: one (Laplace on v.5's analytic chain, which
Turn 2 already flagged ⚠).**

The map does not contain any claim that post-map sims directly
refute. One framing ⚠ (v.5) gets sharper empirical context from
Laplace; that was already flagged. Two items are appropriately
silent (proof-architecture territory).

### Stop-gate decision

No contradictions. Internal audit + external audits complete.
Proceed to final recommendation.

---

## Final recommendation

### Summary across six turns

- **26 internal claims checked** (Turns 2–4): 20 ✓ / 6 ⚠ / 0 ✗.
- **8 raw-data spot-checks** (Turns 3–4): 8/8 match to 3-digit
  precision.
- **5 PNAS-PLAN targets audited** (Turn 5): 2 ✓ / 2 ↻ / 1
  partial. Key gap: Figure 1 three-walks substrate not in map;
  §7 robustness partially in map.
- **4 post-map sim drift checks** (Turn 6): 0 contradictions;
  1 framing pressure (already flagged in Turn 2); 1 reinforcement.

### Verdict

**Outcome 2: Refresh then proceed.** The map is substantively
correct — no load-bearing ✗ found, and the post-map Mess-era
sims do not contradict its claims. The six ⚠ items are all
wording/citation/framing refinements that tighten the map's
language rather than change its content.

However, the map does not by itself cover everything the paper
needs (T5.4, T5.5 gaps). So a single paper-side doc
`paper/T1B-EVIDENCE.md` derived purely from the map would be
**incomplete relative to PNAS-PLAN's planned Figure 1 and §7**.

### Concrete recommendation

1. **Paper-side docs should not all descend from the map.** The
   map is the right source for Theorem 1 commitment (T5.1),
   Theorem 2 empirical c (T5.2's map portion), and §4 mechanism
   anchors (T5.3). But Figure 1 (T5.4) and most of §7 (T5.5)
   need their own paper-side substrates.
2. **The map itself is fine to reference as-is** with the six ⚠
   footnotes applied either as inline edits or as a "revisions
   needed" note appended to the map. The ⚠ items do not block
   reference.
3. **PNAS-PLAN's Theorem 2 block and §7 need rewrites** against
   T1b phenomenology (not a verification-scope action, but the
   audit identified it).
4. **Post-map Mess findings do not require map revision**; they
   require MESSES.md updates, which already exist per earlier
   work on Mess #1/#2/#3.

### The six ⚠ items (with suggested edits)

| id    | suggested revision |
|:-----:|:-------------------|
| i.1   | Replace "monotonically decreasing" with "overall decreasing with small null-band jitter." |
| i.2   | Replace "≈200σ excess" with "141/151 samples above null q99, overwhelming significance." |
| v.5   | Soften "symmetric ⇒ null-recurrent E ⇒ ML(1/2) ⇒ α = 1/2" from load-bearing analytic claim to "the walker's empirical return-time structure is consistent with ML(1/2), per S0 and τ_R-tail sims." |
| ii.1  | Fix the prefactor: either "L₁ ≈ 3.81 · n^{−0.525}" (at the fit's α) or "L₁ ∼ 3 · n^{−1/2}" (at imposed α = 0.5). |
| ii.9  | Rephrase anchor: "M3 IC (b) ≈ 3 (inferred B under α = 0.5, from L₁(600) · √600 = 3.16; direct fit at free α gives A = 3.807)." |
| iii.1 | Tighten citation: "fit in `m3_SUMMARY.md:72`; data in `m1_b1_b2_results.npz`." |

### What this clears and what remains

**Cleared for paper-side promotion based on the map:**
- Theorem 1 variant commitment (T1b).
- Theorem 2 empirical c ≈ 0.498 framing.
- §4 mechanism's √n-visit and per-visit-contraction anchors.

**Needs separate paper-side substrate** (not from the map):
- Figure 1 three-walks substrate (`comparison_walks_SUMMARY.md`
  is the source).
- §7 robustness atlas beyond precision.

**Needs new work (possibly):**
- Base-change sim evidence (b ∈ [2, 40] flat L₁) if the paper
  plans to cite this; location unclear from Turn 5.
- Biased-generators phase-3 convergence summary beyond
  t1b_unit_ball Run 2's d = 0.01.

---
