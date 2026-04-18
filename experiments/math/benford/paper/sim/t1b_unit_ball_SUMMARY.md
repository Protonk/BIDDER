# T1B-UNIT-BALL — summary (Run 1 + Run 2 + Run 3)

Run: `run_t1b_unit_ball.py` → outputs under
`run1_dyadic_ladder/`, `run2_broken_symmetry/`, `run3_smooth_ic/`
(2026-04-18). All 12 sub-runs at N = 10⁷, n_max = 600, M1 sample
grid. Total wall time ≈ 120 min.

**External comparison:** θ_N(N = 10⁸, M0) = 2.72×10⁻³.
θ_N(N = 10⁷) ≈ 8.59×10⁻³ (√N rescale).

## Headlines

1. **The algebraic dyadic/non-dyadic distinction is preserved in
   float64.** On the 8-IC ladder, dyadic ICs (D1, D2, D3) produce
   zero-hit rates per walker of 0.791, 0.172, 0.019 respectively —
   nonzero and ordered with how "close to 1" the IC is. All five
   non-dyadic rationals and irrationals (N1/N2/N3/I1/I2) produce
   **exactly zero** zero-hits over 6×10⁹ walker-steps each.

2. **Transient c_hat does not cleanly partition the 8 ICs by class.**
   Dyadic c_hat tightly clusters at ≈ 0.34 (R2/R3 signature
   reproduced). Irrational c_hat clusters at ≈ 0.48 (√2 signature
   reproduced). Non-dyadic c_hat scatters between 0.37 and 0.54 —
   overlapping both clusters. Zero-hit rate is the clean algebraic
   signature; transient c_hat is not.

3. **Weak asymmetry (d = 0.01) leaves L₁ on [20, 300] visibly
   unchanged.** Stretched-exp c_hat on asym = 0.419 vs sym = 0.416;
   ratio L₁(asym)/L₁(sym) ∈ [0.96, 1.06] across the horizon. Frozen
   fraction under asymmetric stays < 3×10⁻⁴ through n = 600, so the
   E_THRESH confound is not triggered. Scope limitation applies:
   this says the asymmetric walk looks the same as symmetric on the
   observable window, not that the true asymptotic is the same.

4. **Smooth-m Gaussian ν does not deliver a second clean α = 1/2
   sighting.** S2 (smooth m with E spread) behaves structurally
   like M3 IC (c), not M3 IC (b); α_hat on [100, 600] is 1.11, not
   ≈ 0.5. S1 (smooth m with E = 0) hits near-floor by n = 10
   because the initial ν is already too close to uniform. M3 IC (b)
   remains the only ν we have where α ≈ 0.5 emerges cleanly in the
   observable window.

## Run 1 — DYADIC-LADDER

### Zero-hit rates per IC

| IC | class      | x₀         | total zero-hits | per walker |
|:--:|:-----------|-----------:|----------------:|-----------:|
| D1 | dyadic     | 1.0        | 7,911,970       | 0.7912     |
| D2 | dyadic     | 1.5        | 1,724,486       | 0.1724     |
| D3 | dyadic     | 1.125      | 190,246         | 0.0190     |
| N1 | non-dyadic | 1.4 (7/5)  | 0               | 0.0000     |
| N2 | non-dyadic | 17/12      | 0               | 0.0000     |
| N3 | non-dyadic | 99/70      | 0               | 0.0000     |
| I1 | irrational | √2         | 0               | 0.0000     |
| I2 | irrational | φ          | 0               | 0.0000     |

**The dichotomy is sharp in the float64 sim.** No non-dyadic IC
produced a single numerical zero over the entire run (6×10⁹
walker-steps each). No sporadic float-roundoff-induced hits.

D1 matches R2 (0.792 vs R2's 0.7918) to 3 decimals — expected,
same IC, same kernel. D2's 0.172 and D3's 0.019 indicate that the
zero-hit rate drops sharply with |x₀ − 1| among dyadics. The walker
must navigate back to exactly ±1 via integer b-steps before a zero
becomes reachable; larger initial offsets require rarer trajectory
alignments.

### L₁(n) trajectories

| n   | D1      | D2      | D3      | N1      | N2      | N3      | I1       | I2       |
|----:|--------:|--------:|--------:|--------:|--------:|--------:|---------:|---------:|
|  10 | 1.77    | 1.67    | 1.44    | 1.42    | 1.42    | 1.23    | 1.23     | 1.25     |
|  50 | 0.778   | 0.709   | 0.514   | 0.279   | 0.477   | 0.231   | 0.225    | 0.199    |
| 100 | 2.76e-1 | 2.54e-1 | 1.91e-1 | 5.2e-2  | 1.58e-1 | 5.5e-2  | 5.3e-2   | 5.0e-2   |
| 200 | 5.0e-2  | 4.7e-2  | 3.9e-2  | 1.0e-2  | 2.7e-2  | 9.7e-3  | 1.0e-2   | 1.1e-2   |
| 300 | 1.5e-2  | 1.5e-2  | 1.3e-2  | 8.7e-3  | 1.1e-2  | 8.7e-3  | 8.6e-3   | 8.7e-3   |
| 600 | 8.3e-3  | 8.1e-3  | 8.3e-3  | 8.4e-3  | 8.7e-3  | 8.5e-3  | 8.1e-3   | 8.1e-3   |

All 8 ICs land at the N = 10⁷ floor (≈ 8.6×10⁻³) by n ≈ 300–400
and sit there through n = 600. The late-time L₁ values agree within
noise; this horizon cannot resolve the asymptotic B(ν) for any of
these ICs.

### c_hat on [20, 150]

| IC  | class      | c_hat | R²(√n)  | α_hat | R²(log n) |
|:----|:-----------|------:|--------:|------:|----------:|
| D1  | dyadic     | 0.347 | 0.9922  | 1.389 | 0.9536    |
| D2  | dyadic     | 0.345 | 0.9929  | 1.382 | 0.9553    |
| D3  | dyadic     | 0.335 | 0.9958  | 1.346 | 0.9630    |
| N1  | non-dyadic | 0.543 | 0.9986  | 2.195 | 0.9785    |
| N2  | non-dyadic | 0.374 | 0.9955  | 1.498 | 0.9620    |
| N3  | non-dyadic | 0.488 | 0.9988  | 1.966 | 0.9739    |
| I1  | irrational | 0.491 | 0.9990  | 1.979 | 0.9748    |
| I2  | irrational | 0.467 | 0.9990  | 1.897 | 0.9898    |

- Dyadic cluster: c ∈ [0.335, 0.347] — tight, matches R2/R3.
- Irrational: c ∈ [0.467, 0.491] — tight.
- Non-dyadic: c ∈ [0.374, 0.543] — **wide, overlapping both clusters**.

The non-dyadic transient c varies with the specific rational value
used. N1 (7/5) sits high at 0.543 (above irrational cluster); N2
(17/12) sits low at 0.374 (near dyadic cluster); N3 (99/70) sits at
0.488 (in the irrational cluster). No clean per-class pattern
beyond dyadic ≈ 0.34 vs "everything else" spanning a range.

**Reading:** zero-hit rate is the algebraic signature that cleanly
respects the Z[1/2] classification. Transient c_hat is an
observable-window summary that picks up additional IC-specific
structure (denominator, distance to exactly-representable float,
etc.). Both results are consistent with the theorem-level clause
"ν(Z[1/2]) = 0" being the right exceptional-set condition; the
transient c_hat does not support or refute it on its own.

## Run 2 — BROKEN-SYMMETRY

### E-statistics over time

| n   | mean(E) asym | std(E) asym | frozen asym | mean(E) sym | std(E) sym | frozen sym |
|----:|-------------:|------------:|------------:|------------:|-----------:|-----------:|
|  10 | −0.147       | 0.699       | 0.0000      | −0.166      | 0.696      | 0.0000     |
|  50 | +0.593       | 1.108       | 0.0000      | +0.511      | 1.082      | 0.0000     |
| 100 | +1.178       | 1.470       | 0.0000      | +1.017      | 1.413      | 0.0000     |
| 200 | +2.050       | 2.030       | 0.0000      | +1.728      | 1.908      | 0.0000     |
| 300 | +2.758       | 2.486       | 0.0000      | +2.272      | 2.299      | 0.0000     |
| 455 | +3.701       | 3.086       | 0.0000      | +2.956      | 2.798      | 0.0000     |
| 600 | +4.485       | 3.576       | 0.0002      | +3.496      | 3.197      | 0.0001     |

**The envelope holds throughout.** Frozen fraction stays at 0 until
n = 600 where it reaches 2×10⁻⁴ (asym) / 1×10⁻⁴ (sym) — well below
the 5% cap for trustworthy rate fits.

Interesting observation: both symmetric and asymmetric runs show
**positive mean(E)** by late times (+3.50 and +4.48 respectively).
Even the symmetric √2 IC accumulates positive E-drift. This is not
a drift in the measure but a feature of the √2 starting
distribution: b-step carry/borrow has structural asymmetry per
walker position on (10^E, 10^(E+1)), which integrates to a nonzero
mean under the √2 orbit. The asymmetric run sits ~1 unit above the
symmetric, consistent with d = 0.01 per a-step across 600 steps
modulo feedback from b-step corrections. Not load-bearing for the
rate-family question.

### L₁(n) — asymmetric vs symmetric

| n   | L₁(asym)  | L₁(sym)   | ratio | diff        |
|----:|----------:|----------:|------:|------------:|
|  10 | 1.230     | 1.229     | 1.001 | +1.29e-3    |
|  50 | 2.22e-1   | 2.25e-1   | 0.989 | −2.42e-3    |
| 100 | 5.17e-2   | 5.31e-2   | 0.973 | −1.45e-3    |
| 200 | 9.83e-3   | 9.92e-3   | 0.991 | −9.10e-5    |
| 300 | 8.34e-3   | 8.55e-3   | 0.975 | −2.14e-4    |
| 600 | 8.41e-3   | 7.95e-3   | 1.057 | +4.55e-4    |

### Rate-family fits on [20, 300]

| Model                  | asym  | R²     | sym   | R²     |
|:-----------------------|------:|-------:|------:|-------:|
| stretched: log L = a−c√n | c = 0.419 | 0.957 | c = 0.416 | 0.956 |
| pure exp: log L = a−γn   | γ = 1.87e-2 | 0.878 | γ = 1.86e-2 | 0.878 |
| algebraic: log L = a−α log n | α = 2.06 | 0.978 | α = 2.04 | 0.977 |

- asym vs sym c_hat: 0.419 vs 0.416, difference 0.7%.
- Best-fit family: algebraic (R² = 0.978) slightly better than
  stretched-exp (R² = 0.957), pure exp worst (R² = 0.878). This
  is characteristic of a sharp-IC transient on this window for
  the √2 IC — consistent with M1's √2 data.

**Reading:** weak asymmetry does not visibly change the L₁ rate
family on the [20, 300] observable window where the envelope
holds. This does NOT tell us what happens under strong asymmetry or
on longer horizons where the drift moves more walkers out of
envelope. It does rule out "d = 0.01 asymmetry instantly changes
the rate family from the symmetric baseline."

## Run 3 — SMOOTH-IC

### L₁(n) for S1, S2

| n   | L₁(S1)    | L₁(S2)    | zero-hits(S1) | zero-hits(S2) |
|----:|----------:|----------:|--------------:|--------------:|
|   1 | 0.682     | 0.796     | 0             | 0             |
|  10 | 1.78e-2   | 4.22e-1   | 0             | 0             |
|  50 | 1.14e-2   | 1.83e-1   | 0             | 0             |
| 100 | 9.87e-3   | 6.24e-2   | 0             | 0             |
| 200 | 9.07e-3   | 1.41e-2   | 0             | 0             |
| 300 | 8.44e-3   | 9.10e-3   | 0             | 0             |
| 600 | 8.35e-3   | 8.53e-3   | 0             | 0             |

Zero zero-hits on both S1 and S2. Smooth Gaussian-m ν is
numerically clean in the sim; the operational criterion for T1b's
"well-behaved ν" passes without exception.

### Rate fits

| IC | window       | c_hat | R²(√n) | α_hat | R²(log n) |
|:---|:-------------|------:|-------:|------:|----------:|
| S1 | [20, 150]    | 0.039 | 0.918  | 0.161 | 0.940     |
| S1 | [100, 600]   | 0.011 | 0.771  | 0.087 | 0.804     |
| S2 | [20, 150]    | 0.356 | 0.992  | 1.425 | 0.954     |
| S2 | [100, 600]   | 0.130 | 0.783  | 1.107 | 0.862     |

- **S1** hits near-floor by n = 10. The σ = 0.05 Gaussian on T
  started close enough to uniform that there was little transient
  to observe, and E = 0 anchors walkers in the single-decade zone
  where mixing is fast. The fits are uninformative (L₁ is at floor
  almost throughout).
- **S2** starts slightly higher (L₁(1) = 0.80 vs S1's 0.68, because
  the E-spread gives more structure to decorrelate), and decays
  through a visible transient. On [20, 150] S2's c_hat = 0.356
  **matches M3 IC (c)'s c = 0.356 exactly** — S2 is the smooth-m
  analog of M3 IC (c)'s uniform-m × uniform-E setup.
- **Neither S1 nor S2 shows α ≈ 0.5 on [100, 600].** S2's α = 1.11
  with R² = 0.862 is intermediate; S1 is dominated by floor noise.

### Comparison: S2 vs M3 IC (b)

| n   | L₁(S2)   | L₁(M3 IC (b)) | ratio |
|----:|---------:|--------------:|------:|
|  10 | 4.22e-1  | 1.07          | 0.395 |
|  50 | 1.83e-1  | 0.510         | 0.359 |
| 100 | 6.24e-2  | 0.335         | 0.186 |
| 200 | 1.41e-2  | 0.238         | 0.059 |
| 300 | 9.10e-3  | 0.194         | 0.047 |
| 600 | 8.53e-3  | 0.129         | 0.066 |

S2 reaches floor while IC (b) is still at 0.13 — the two ICs are
on fundamentally different trajectories. IC (b)'s delta-m-plus-
spread-E structure is what produces the clean algebraic decay;
replacing delta-m with a narrow Gaussian (S2) destroys it and puts
the IC back into the M3 IC (c)-like intermediate regime.

**Takeaway for α confirmation:** IC (b)'s specific (delta-m,
uniform-E) structure is load-bearing for the clean α ≈ 0.5
sighting. Smooth-m variants at the same N and horizon don't
deliver a second independent α measurement.

## What this run settles

1. **Float64 preserves the dyadic/non-dyadic algebraic
   classification exactly.** 5 non-dyadic ICs × 6×10⁹ walker-steps
   each = 3×10¹⁰ opportunities for float roundoff to produce an
   exact zero, and zero did. The Z[1/2] exceptional set is the
   right theorem-level condition, and the sim respects it in
   practice.
2. **Transient c_hat is not a reliable single-observable classifier
   of IC class.** It distinguishes dyadic (≈ 0.34) from irrational
   (≈ 0.48) on this ladder, but non-dyadic rationals scatter
   across the range. Reviewers should not be told "c = X implies
   class Y"; the class is determined by zero-hit rate (or the
   underlying algebra), not by c.
3. **Weak asymmetry (d = 0.01) leaves the observable-window rate
   family unchanged.** This is a check-passes, not a theorem-
   level certification.

## What this run does NOT settle

1. **Strong asymmetry.** Still untested with the current kernel;
   d ≳ 0.05 would push a significant fraction of walkers out of
   the E_THRESH envelope within the horizon.
2. **Longer-horizon α for these ICs.** M4-scale runs on D1–I2,
   S1, S2 would give direct α measurements but were not in this
   plan's scope.
3. **A second clean α ≈ 0.5 sighting.** Smooth-m Gaussian ν did
   not deliver. M3 IC (b) remains the primary empirical anchor,
   with M4's late √2 excess as corroboration.

## Plan document amendments implied

1. `ROOT-TWO-CHECKS-SIM.md` and `root_two_checks_SUMMARY.md` should
   update "ν(Q) = 0" references to "ν(Z[1/2]) = 0" consistent with
   the corrected exceptional set.
2. `m3_SUMMARY.md` already has a post-M4 correction on α vs B
   universality; should additionally note that M3 IC (b)'s
   (delta-m, uniform-E) structure is what produces the clean α̂
   signal, and smooth-m variants do not inherit it.
3. `ALGEBRAIC-SIM-MESS-PLAN.md` should optionally add a post-2026-
   04-18 note that the "IC robustness" M3 block has now been
   sanity-checked against 10 additional IC values (8 from Run 1,
   2 from Run 3) and the universality statement is empirically
   stable within the observable window, with the α-sighting
   dependence on the M3 IC (b) structure flagged.

## Data saved

- `run1_dyadic_ladder/{D1,D2,D3,N1,N2,N3,I1,I2}_results.npz`:
  sample_times, l1, h_full, l2_norm, modes, zero_hits_per_step,
  total_zero_hits, meta (N, steps, bins, x0, seed, ic_label)
- `run2_broken_symmetry/{asymmetric,symmetric}_results.npz`:
  same schema + mean_E, std_E, frozen_fraction, meta.probs,
  meta.drift
- `run3_smooth_ic/{S1,S2}_results.npz`: same schema + meta.mu,
  meta.sigma, meta.E_structure
