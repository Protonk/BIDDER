# sim/ — BS(1,2) Benford simulation program

This directory holds the simulation code, plans, data, and summaries
for the paper's Theorem 1 convergence-to-Benford claim on the
symmetric BS(1,2) random walk.

**Status (2026-04-18).** The original three-way discrimination
(T1a stretched-exp vs T1b two-regime vs T1c mixture) has resolved:
**T1b is the surviving theorem shape** — asymptotic α = 1/2 with
IC-dependent coefficient B(ν), preceded by an IC-specific stretched-
exp transient for sharp ICs. Precision robustness closed in both
directions via a four-precision ladder (fp16/fp32/fp64/fp128).
See `T1B-EVIDENCE-MAP.md` for the paper-oriented synthesis;
individual run summaries for details.

---

## Where to start

| If you are… | Start here |
|:-----------|:-----------|
| Onboarding cold | `T1B-EVIDENCE-MAP.md` — paper-oriented synthesis of all evidence |
| Checking the current theorem statement | `T1B-EVIDENCE-MAP.md` §"T1b (current working statement)" |
| Reading individual findings | `*_SUMMARY.md` files (see Summaries section below) |
| Reviewing a run plan | `*-SIM.md` / `*-PLAN.md` / `*-LADDER.md` files (see Plans) |
| Re-running something | `run_*.py` (see Runners) |
| Looking for raw data | `*_results.npz` or subdirectory `runN_*` |
| Historical context (pre-T1b) | `SIM-REPORT.md` (phase 1 and phase 3, before the MESSES intervention) |

---

## File inventory

### Paper-oriented synthesis

- **`T1B-EVIDENCE-MAP.md`** — the single document mapping each
  clause of T1b to the sim evidence supporting it, plus paper-
  ready wording for each clause and a "safe to say / not safe to
  say" checklist. Primary reference for paper authoring.

### Summaries (per-run, in approximate order of execution)

| Summary                       | Run                                 | Status |
|:------------------------------|:------------------------------------|:-------|
| `m1_b1_b2_SUMMARY.md`         | M1 + B1 + B2 consolidated (√2 IC)   | done |
| `s0_SUMMARY.md`               | S0 Mittag-Leffler index test        | done |
| `b3_SUMMARY.md`               | B3 mode-coupling matrix             | done |
| `m3_SUMMARY.md`               | M3 three-IC robustness              | done |
| `m4_SUMMARY.md`               | M4 long-horizon √2 (n ≤ 3000)       | done |
| `root_two_checks_SUMMARY.md`  | ROOT-TWO: φ + rational conventions  | done |
| `t1b_unit_ball_SUMMARY.md`    | T1B-UNIT-BALL: dyadic / broken sym / smooth | done |
| `fp32_SUMMARY.md`             | FP32 precision-robustness           | done |
| `fp16_SUMMARY.md`             | FP16-MINI precision ladder          | done |
| `fp128_SUMMARY.md`            | FP128-CEILING (fp64 vs 128-bit MPFR) | done |

### Plans (authoritative run specs)

| Plan                          | Scope                               | Status |
|:------------------------------|:------------------------------------|:-------|
| `ALGEBRAIC-SIM-MESS-PLAN.md`  | Authoritative for M0, S0, M1–M4     | executed through M4 (n ≤ 3000); M4 extension pending (beef-box Run 1) |
| `BENTHIC-MINKOWSKI-SIM.md`    | B1, B2, B3 Fourier/mode-coupling    | B1/B2 folded into M1, B3 done; high-mode B3 pending (beef-box Run 3) |
| `TUKEYS-LADDER.md`            | Nonparametric shape identification  | not directly executed; findings aligned with IC (b) via M3 |
| `ROOT-TWO-CHECKS-SIM.md`      | φ + rational-IC conventions         | done |
| `T1B-UNIT-BALL-SIM.md`        | Dyadic ladder, broken sym, smooth   | done |
| `FP32-SIM.md`                 | fp32 precision-robustness           | done |
| `FP16-MINI-SIM.md`            | fp16 precision ladder               | done |
| `FP128-CEILING-SIM.md`        | fp64 vs 128-bit MPFR                | done |
| `EXPENSIVE-BEEF-BOX-SIM.md`   | Long-horizon M4, LONG-ANCHOR, HIGH-MODE-B3, NON-SQRT2-DELTA | pending on x86 beef-box |

### Runners (Python scripts)

Each runner is self-contained, takes no CLI args in normal use,
and writes its output alongside itself. All use `np.random.default_rng`
with fixed seeds for reproducibility.

| Runner                    | Produces                                    |
|:--------------------------|:---------------------------------------------|
| `run_m0.py`               | `m0_results.npz` (null-floor calibration)    |
| `run_m1_b1_b2.py`         | `m1_b1_b2_results.npz`                       |
| `run_s0.py`               | `s0_results.npz` (post-processes M1 data)    |
| `run_b3.py`               | `b3_results.npz`                             |
| `run_m3.py`               | `m3_results.npz` (three ICs in one file)     |
| `run_m4.py`               | `m4_results.npz` (+ `.partial.npz` checkpoints) |
| `run_root_two_checks.py`  | `r1_phi_results.npz`, `r2_rational_restart_results.npz`, `r3_rational_absorb_results.npz` |
| `run_t1b_unit_ball.py`    | `run1_dyadic_ladder/{D1..I2}_results.npz`, `run2_broken_symmetry/{asymmetric,symmetric}_results.npz`, `run3_smooth_ic/{S1,S2}_results.npz` |
| `run_fp32_checks.py`      | `fp32_results/ic_b_fp32_results.npz`, `fp32_results/dyadic_ladder/{D1..I2}_fp32_results.npz` |
| `run_fp16_checks.py`      | `fp16_results/{run1_fp16,run2_fp32_control,run3_fp64_control}/*.npz` |
| `run_fp128_check.py`      | `fp128_results/{ic_b_fp64_matched,ic_b_fp128}_results.npz` |

All runners use `sage -python run_*.py` (SageMath ships numpy +
scipy; CPython should work too, but that is not the tested path).

### Run logs

Paired `.log` files record stdout from each runner's most recent
full execution. Useful for confirming seeds, wall times, and any
warnings that didn't make it into the summaries.

### Historical / legacy

- **`SIM-REPORT.md`** — phase-1 and phase-3 experiments from
  before the MESSES intervention. Preserved for context; the T1b
  evidence comes from later runs, not these.
- **`data/`** — raw outputs from phase-1 and phase-3.
- **`fig/`** — figures from phase-1 and phase-3.

### Subdirectories with npz outputs

- `run1_dyadic_ladder/` — 8 ICs from T1B-UB Run 1
- `run2_broken_symmetry/` — 2 runs (asymmetric, symmetric control)
- `run3_smooth_ic/` — 2 ICs (S1, S2)
- `fp32_results/` — fp32 M3 IC (b) + fp32 dyadic ladder
- `fp16_results/` — fp16 + fp32-ctrl + fp64-ctrl precision ladder

---

## Timeline of the program

Rough chronological order of what was done and what was learned:

1. **M0** — null-floor calibration (θ_N at N = 10⁸).
2. **M1 + B1 + B2 consolidated** — the seed run on √2 IC. L₁
   trajectory, ensemble Fourier, per-walker return counts,
   in-R cohort Fourier.
3. **M1 fit on [20, 200]** gave a clean c ≈ 0.498 stretched-exp,
   initially interpreted as T1a. MESSES objected.
4. **S0** — Laplace-transform test on M1's return counts,
   validated ML(1/2) on the excursion sub-population. (The
   β̂ tail-slope sub-test was determined to be mis-specified.)
5. **B3** — mode-coupling matrix K̂ at r = 1..5. ρ(K̂) = 0.924,
   injection-dominated regime.
6. **M3** — three-IC robustness. **IC (b) produced a clean α̂
   = 0.525 on [100, 600], R²(log n) = 0.9986**, directly
   falsifying T1a and establishing T1b's algebraic exponent.
7. **M4** — long-horizon √2 IC (n ≤ 3000). Persistent signal
   above null at late times; corroborates α = 1/2 consistency,
   does not resolve it directly on √2.
8. **ROOT-TWO-CHECKS (R1/R2/R3)** — φ confirms √2 not one-off;
   rational-IC conventions (restart/absorb) give same late L₁.
9. **T1B-UNIT-BALL** — Run 1 dyadic ladder (established Z[1/2]
   as the exceptional set, not ℚ); Run 2 broken symmetry (weak
   asymmetry leaves envelope unchanged); Run 3 smooth-IC
   (Gaussian ν doesn't skip the transient the way IC (b) does).
10. **FP32-SIM** — fp32 rerun of M3 IC (b) and dyadic ladder.
    α̂ robust to precision loosening; the dyadic dichotomy has a
    detectable fp32 floor, refining Result 5's wording.
11. **FP16-MINI-SIM** — three-precision ladder with pristine-
    walker tracking. Precision-induced zero-hit rate scales
    linearly with fp_eps; fp64 below detection at our volumes.
12. **FP128-CEILING-SIM** — fp64 vs 128-bit MPFR on M3 IC (b)
    at matched seed. L₁ and α̂ **bit-exactly identical**.
    Precision-robustness closed in both directions.

**Pending (on x86 beef-box):**

- EXPENSIVE-BEEF-BOX Run 1 (FULL-M4 to n = 20,000 on √2)
- EXPENSIVE-BEEF-BOX Run 2 (LONG-ANCHOR, M3 IC (b) to n = 20,000)
- EXPENSIVE-BEEF-BOX Run 3 (HIGH-MODE-B3 with r = 1..20)
- EXPENSIVE-BEEF-BOX Run 4 (NON-SQRT2-DELTA, 3 m-values at IC (b) structure)

---

## Two purposes (retained from original README, updated)

**Scientific discrimination.** The question "does L₁ decay as
exp(−c√n) or 1/√n or a mixture?" has been answered: it's T1b —
asymptotically 1/√n with IC-specific transients, one of which
happens to look stretched-exp on the √2 IC at observable n. See
`T1B-EVIDENCE-MAP.md` for the full evidence thread.

**Proof triage.** B3's ρ(K̂) = 0.924 is the empirical answer
FIRST-PROOF gap 2 (R4) was asking for: the spectral radius is
genuinely < 1 but only by ~8%, so any analytical gap-2 proof
must deliver a tight bound to produce useful constants. See
`b3_SUMMARY.md` for the regime classification and implications.

---

## Conventions used across runners

- **Walker state** is `(m ∈ [0, 1), E ∈ ℤ, sign ∈ {−1, +1})`,
  representing `x = sign · 10^(E + m)`.
- **Symmetric measure** unless otherwise noted: `P(a) = P(a⁻¹) =
  P(b) = P(b⁻¹) = 1/4`.
- **Default IC** across the program is `x = +√2` (m = log₁₀√2,
  E = 0, sign = +1). Chosen because the orbit in Q(√2) avoids
  x = 0 algebraically, so no regularization convention is needed.
- **E_THRESH = 20** is the default "frozen" threshold; walkers at
  `|E| > E_THRESH` skip the active b-step. fp16 runs reduce this
  to 3 to avoid fp16 overflow on `10^(E+m)`.
- **Exact-zero convention**: R2-style restart at `(m=0, E=0,
  sign=sign(δ))`, matching the existing near-zero shortcut. R3 is
  the absorbing variant. Dyadic ICs trigger these; non-dyadic /
  irrational ICs do not (up to fp precision, see Result 5 in the
  evidence map).
- **Seeds** are deterministic per-runner and per-IC; see each
  runner's SEED_BASE at the top of the file. `np.random.default_rng`
  (PCG64) is used throughout for cross-platform reproducibility.
- **θ_N(N = 10⁸) = 2.72×10⁻³**, the 99.9% quantile of the
  multinomial null with N = 10⁸ walkers and B = 1000 bins (from
  M0). Rescale as `θ_N(N) ≈ θ_N(10⁸) · √(10⁸ / N)` for other N.

---

## Finding specific results by topic

| Topic                                    | Primary document |
|:-----------------------------------------|:-----------------|
| Why T1a died                             | `m3_SUMMARY.md`, "Headline" |
| Why α = 1/2 is the surviving exponent    | `T1B-EVIDENCE-MAP.md` clause (ii) |
| Why B(ν) is IC-dependent                 | `T1B-EVIDENCE-MAP.md` clause (ii), post-M4 block |
| Stretched-exp transient is IC-specific   | `T1B-EVIDENCE-MAP.md` clause (iii); `m3_SUMMARY.md` |
| Dyadic vs non-dyadic dichotomy           | `T1B-EVIDENCE-MAP.md` clause (iv); `t1b_unit_ball_SUMMARY.md` Run 1 |
| Precision-scaling of zero-hit events     | `fp16_SUMMARY.md`; `T1B-EVIDENCE-MAP.md` clause (iv) |
| fp64 is sufficient (precision closed)    | `fp128_SUMMARY.md`; `T1B-EVIDENCE-MAP.md` header + clause (iv) |
| Weak-asymmetry robustness                | `T1B-EVIDENCE-MAP.md` clause (v); `t1b_unit_ball_SUMMARY.md` Run 2 |
| Paper-ready wording recommendations      | `T1B-EVIDENCE-MAP.md` "What the paper can safely say" |
| Empirical K̂ / mode-coupling              | `b3_SUMMARY.md` |
| ML(1/2) return-count statistics          | `s0_SUMMARY.md` |
| Null-floor calibration                   | `m0_results.npz` via `run_m0.py` |

---

## Related paper-level documents (one level up)

- `../MESSES.md` — the forcing objection that motivated the
  discrimination program.
- `../PNAS-PLAN.md` — paper plan with Theorem 1 variants
  (T1a/T1b/T1c). As of 2026-04-18, T1b is the surviving variant.
- `../SECOND-PROOF.md` — live proof gap list. §3 (F3) is the
  spectral-gap sub-item triaged by B3.
- `../archive/FIRST-PROOF.md` — archived T1a-era proof draft.

---

## Disagreement is a deliverable

The original three-plan framing (TUKEYS gates family, ALGEBRAIC
estimates parameters, BENTHIC explains mechanism) was designed so
that structured disagreement would be legible and paper-usable.
In practice the three plans agreed: BENTHIC's injection-dominated
regime, S0's ML(1/2), and M3 IC (b)'s direct α̂ = 0.525 all point
at the same target, and TUKEYS-level shape identification was
largely preempted by IC (b)'s unambiguous log-log fit. The
agreement is a genuine result; the disagreement framing is
preserved here because the paper's Theorem 1 variant selection
(T1a→T1b) was made *because* the three plans jointly falsified
T1a. That's structured agreement operating as intended.
