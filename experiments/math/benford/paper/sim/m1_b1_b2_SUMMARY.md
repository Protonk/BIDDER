# M1 + B1 + B2 consolidated run — summary

Run: `run_m1_b1_b2.py`, output `m1_b1_b2_results.npz` (2026-04-17).
N = 10⁸ walkers, 600 steps, B = 1000 bins, modes r = 1..5,
E_R = 3, E_THRESH = 20, seed 0xBADC0DE1, IC x = +√2.
Walk time 210.6 min (3.5 h), throughput 4.75×10⁶ walker-steps/s.

**External comparison (not from this run):** null floor from M0 is θ_N = 2.717×10⁻³ (mean 2.521×10⁻³, ratio 1.08). All L₁/θ_N entries below use that M0-derived threshold; it is pulled in for cross-reference, not established by this run.

## Data inventory (all present in npz)

- `l1(280)` — L₁(n) on the sample grid
- `h_full(280, 5)` — ensemble ĥ(r, n) for r = 1..5
- `h_R(280, 5)`, `h_R_after(280, 5)`, `n_R(280)` — in-R cohort Fourier before a step and after that same step over the same walkers; `n_R` is the cohort size. **No direct out-of-R series is saved**; the out-of-R contribution is reconstructed as `h_full · N − h_R_after · n_R`.
- `l2_norm(280)` — √Σ|ĥ(r,n)|² over modes 1..5 (verified to match recomputation at 0 error)
- `hist_return_counts(7, 43)` and `hist_time_in_R(7, 501)` at checkpoints {25, 50, 100, 150, 200, 300, 500}
- `cond_fourier(98, 5)` — conditional Fourier binned by return count (98 bins meeting ≥1000 walker threshold)

## L₁ trajectory and D3

L₁(n) is overall downward but not monotone — inside the null band (roughly n ≳ 400) the trajectory has 36 small upward moves on the 280-point sample grid, the largest Δ = +2.69×10⁻⁴ from n = 555 to n = 560. The minimum L₁ = 3.21×10⁻³ at n = 565, after which L₁ rises again to 3.44×10⁻³ at n = 600. These reversals are null-band noise (θ_N scale), not a collapse of the decay. L₁/θ_N at canonical times:

| n   | L₁        | L₁/θ_N |
|----:|----------:|-------:|
|   1 | 1.992e+00 | 733   |
|  25 | 5.746e-01 | 211   |
|  50 | 2.251e-01 |  83   |
| 100 | 5.273e-02 |  19   |
| 150 | 1.562e-02 | 5.75  |
| 200 | 6.554e-03 | 2.41  |
| 300 | 4.231e-03 | 1.56  |
| 500 | 3.591e-03 | 1.32  |
| 600 | 3.444e-03 | 1.27  |

**n\* is not reached on [0, 600].** Min L₁ = 3.21×10⁻³ at n = 565; final L₁/θ_N = 1.27. D3 (signal death) cannot be scored from M1 alone; M4's [300, 20000] horizon is required as planned.

## D1/D2 rate signature — preliminary

Local slopes d(log L₁)/dn by central differences on the dense single-step grid, with c_implicit = −(d log L₁/dn)·2√n (constant c_implicit ⇔ pure H_S stretched-exp). Rows at n ∈ {10, 25, 50, 100, 150} use t−1, t, t+1 centered on t. The n = 200 row is shown separately because the sample grid transitions from every-step to every-5-step at n = 200, so no genuine central diff exists there on the saved grid:

| n   | d(log L₁)/dn | c_implicit |
|----:|-------------:|-----------:|
|  10 | −6.00e-02    | 0.380      |
|  25 | −4.41e-02    | 0.441      |
|  50 | −3.27e-02    | 0.462      |
| 100 | −2.66e-02    | 0.531      |
| 150 | −2.85e-02    | 0.699      |

At n = 200 the one-sided estimates disagree sharply — backward diff (199→200) = +3.65×10⁻³, forward diff (200→205) = −9.72×10⁻³, (asymmetric) central over (199, 205) = −7.49×10⁻³. This disagreement itself is the diagnostic: once L₁ approaches θ_N the local slope is dominated by null-band noise, not the decay signal.

**Findings to flag, not smooth over:**
- c_implicit **drifts upward** over [10, 150] rather than stabilizing. Under pure H_S this should tend to a constant. Possible readings: (a) we're still in the pre-asymptotic regime; (b) the form is mixed; (c) the L₁ constant A > 1 means the global fit bends and c_implicit from finite differences does not approach c until much later. A5 nonlinear fit is the proper discriminant.
- Past n ≈ 150 finite differences are no longer informative: the backward/forward/centered estimates at n = 200 disagree in sign and magnitude, reflecting the null-band noise rather than the underlying rate.
- Global −log L₁ ratio (n₁=50, n₂=200) is 3.37, between H_S (2.00) and H_A (4.00) but closer to H_A. The (25, 100) pair gives 5.31, *above* both predictions. These are crude two-point estimates contaminated by the log-prefactor; not a D1 verdict, only a cross-check. Treat as a caution: the clean D1/D2 discrimination the plan expects will have to come from the A5 fit with proper windows.

## Fourier spectrum (h_full)

|ĥ(r)| at key times:

|  n  |    |h1|   |   |h2|   |   |h3|   |   |h4|   |   |h5|   |
|----:|---------:|---------:|---------:|---------:|---------:|
|   1 | 4.80e-01 | 4.19e-01 | 1.54e-01 | 6.10e-01 | 6.53e-01 |
|  25 | 9.07e-03 | 3.77e-04 | 1.27e-02 | 1.76e-03 | 7.67e-04 |
|  50 | 5.90e-03 | 5.94e-04 | 3.31e-03 | 7.54e-04 | 1.09e-04 |
| 100 | 4.01e-03 | 4.45e-04 | 1.11e-03 | 4.30e-04 | 6.41e-05 |
| 200 | 2.76e-03 | 2.02e-04 | 8.48e-04 | 3.66e-04 | 1.84e-04 |
| 600 | 1.55e-03 | 1.27e-04 | 4.61e-04 | 1.83e-04 | 5.46e-05 |

n = 1 values are large because all walkers emerge from a 4-atom distribution (post first step from x = +√2). By n = 25 mode-3 dominates mode-1, but from n = 50 onward mode 1 is the biggest, with mode 3 the next largest. Decay is not a clean single exponential in any mode.

## B2 in-R Fourier step-contraction

|ĉ_R_before(1)| vs |ĉ_R_after(1)| on the same walker cohort:

| n   |  n_R         | |c_R,before[1]| | |c_R,after[1]| | ratio after/before |
|----:|-------------:|----------------:|---------------:|-------------------:|
|  25 | 99,985,540   | 9.32e-03        | 9.06e-03       | 0.972              |
|  50 | 99,321,111   | 4.71e-03        | 5.42e-03       | **1.152**          |
| 100 | 94,628,218   | 6.38e-03        | 2.26e-03       | 0.354              |
| 200 | 82,969,068   | 1.69e-02        | 4.26e-03       | 0.252              |
| 500 | 61,592,398   | 2.70e-02        | 7.63e-03       | 0.283              |
| 600 | 57,333,352   | 2.84e-02        | 8.21e-03       | 0.288              |

- Per-step contraction factor stabilizes near 0.25–0.30 for n ≥ 200 — a strong single-step effect that BENTHIC's mode-coupling matrix has to explain.
- **n = 50 ratio exceeds 1 (|c_R,after| > |c_R,before|).** Single-step can increase mode-1 amplitude on the in-R cohort at early times. Noted for BENTHIC's analysis; likely a transient sign effect, not a bug.

## Return counts and time-in-R

Return-count histograms (entries into R, 0→1 edges):

| n   | P(N_n = 0) | E[N_n] | sd(N_n) | max N_n | E[N_n ∣ N_n ≥ 1] | E[N_n]/√n |
|----:|-----------:|-------:|--------:|--------:|------------------:|----------:|
|  25 | 0.9998     | 0.000  | 0.017   |  6      | 1.19             | 0.0000    |
|  50 | 0.9933     | 0.009  | 0.121   |  9      | 1.34             | 0.0013    |
| 100 | 0.9303     | 0.128  | 0.556   | 15      | 1.84             | 0.0128    |
| 150 | 0.8336     | 0.382  | 1.064   | 18      | 2.30             | 0.0312    |
| 200 | 0.7350     | 0.719  | 1.552   | 23      | 2.71             | 0.0509    |
| 300 | 0.5642     | 1.510  | 2.403   | 28      | 3.47             | 0.0872    |
| 500 | 0.3333     | 3.202  | 3.698   | 42      | 4.80             | 0.1432    |

**Finding to flag, not smooth over:** E[N_n] is **not yet on a √n scaling**. Raw E[N_n]/√n grows monotonically over [25, 500] from 0 to 0.14 — if the Mittag-Leffler(1/2) asymptotic held on this window, this would already be near-constant. Regressing E[N_n] on n over [300, 500] gives E[N_n] ∝ n^{≈1.47}. Conditional E[N_n ∣ N_n ≥ 1] regresses as n^{≈0.60} over [100, 500] — closer to the ½ target but not yet there.

Interpretation: at n = 500, **33% of walkers have never entered R at all.** The ensemble is a mixture of "still-at-origin" walkers and "excursioners," and the √n scaling applies only to the latter. S0's job is to unpack this — MESSES's prediction is about the excursion subpopulation's tail, not the unconditional mean on the pre-asymptotic window we sampled.

Time-in-R `mean(time_in_R)/n`: 1.00 (n=25) → 0.88 (n=300) → 0.80 (n=500). Fraction of walkers with time_in_R = n (never left R): 0.90 (n=100) → 0.50 (n=300) → 0.27 (n=500).

## Conditional Fourier (cond_fourier)

98 records total, one per (checkpoint n, return-count k) bin with size ≥ 1000. Bin sizes at n = 500 range from 33 M walkers (k = 0) down to 1020 (k = 28); we have conditional Fourier all the way up to k ≈ 20 at n = 300 and k = 28 at n = 500. This is the primary dataset for BENTHIC's per-return decomposition and for TUKEYS's L3/L4 coefficient plots.

Striking feature to flag: at n = 300, `|ĉ(1, k=1)| = 2.05×10⁻⁴`, an order of magnitude smaller than both its k = 0 (6.76×10⁻³) and k = 2+ (≥ 1.5×10⁻³) neighbors. The one-excursion subpopulation is nearly uniform in mode 1. Needs BENTHIC analysis to assess whether this is a selection/phase effect or a genuine structure in the first-return distribution.

## What this run settles and what it leaves open

**Settled:**
- Data collection for M1 (all D1/D2/A4 inputs), B1 (ensemble ĥ, conditional ĥ by return count, per-walker N_n) and B2 (in-R cohort Fourier before and after a single step on the same walkers, plus cohort size n_R) — all present and self-consistent. A direct out-of-R Fourier time series is not saved; when needed it is derived from `h_full` and `h_R_after` using `h_out = (h_full · N − h_R_after · n_R) / (N − n_R)`.
- L₂-norm saved and recomputes exactly.
- θ_N from M0 (external) is at 1.08× the analytic multinomial null mean (sanity OK in that run, reported here only for context).

**Open / deferred:**
- **D3 (signal death at n\*) cannot be scored** without M4 — observed horizon insufficient.
- **D1/D2 rate discrimination is not yet clean** from this data alone. c_implicit drifts 0.38 → 0.70 before hitting noise at n ≈ 200; global −log-ratio estimates are noisy and not decisive. A5's three-parameter fit on [max(n\*, 2000), 20 000] (from M4) is the decisive instrument; M1 on its own is pre-asymptotic.
- **Mittag-Leffler(1/2) scaling of N_n is not visible yet** on [25, 500]. S0 must run on the conditional (N_n ≥ 1) subpopulation, not the unconditional mean, or wait for later times where the "at-origin" population shrinks further.
- **Step-contraction factor (≈ 0.25–0.30 for n ≥ 200)** needs B3 to contextualize — is this the balanced regime's ρ(M), or injection-dominated?

## Next per default schedule

1. S0 (ML-index): run analysis on `hist_return_counts` at the later checkpoints with conditioning on N_n ≥ 1; cross-check scaling hypothesis before A5 uses it.
2. B3 (excursion-resolved mode coupling) and M3 (IC robustness) can run in parallel since they read different data.
3. M2 / M4 for D3 and the tail.
