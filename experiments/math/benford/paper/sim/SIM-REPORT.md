# SIM-REPORT

Minimal record of simulations run for FIRST-PROOF gap 3 (symmetric
walk rate shape) and gap 4 (biased walk convergence). Preserved so
a data appendix can be assembled without re-running.

---

## Phase 1 — symmetric BS(1,2), rate-shape discrimination

**Question.** Is the L₁-to-Benford decay exp(−λt) or exp(−c√t)?
The existing `bs12_rate.py` fit over [20, 100] gave R² = 0.99 for
exp but couldn't distinguish from stretched on that window.

**Setup.**
- Script: `experiments/math/benford/gap3_phase1.py`
- Symmetric walk: weights (¼, ¼, ¼, ¼) on {a, a⁻¹, b, b⁻¹}.
- N = 10⁷ walkers, t ∈ [0, 600], log-spaced checkpoints.
- State representation: x as float64, direct (not (m, E)) since
  600 symmetric steps stays within float64 range.
- Seed: 0xDECADE.
- Runtime: 2:44 on local machine.

**Result.** Stretched exponential wins decisively.

| Window | exp fit: (λ, R², resid σ) | stretched fit: (c, R², resid σ) |
|---|---|---|
| [20, 100] | 0.0374, 0.9963, 0.061 | **0.543, 0.9983, 0.042** |
| [20, 120] | 0.0357, 0.9929, 0.094 | **0.548, 0.9985, 0.043** |

Exp residuals are 2.2× stretched's on [20, 120] and carry
systematic curvature. Local slope of log(L₁) changes by factor
2.4 across the window, tracking stretched's −c/(2√t) prediction.

**Artifacts.**
- `data/gap3_phase1.csv` — (t, L₁), 31 checkpoints.
- `data/gap3_phase1.npz` — same data in numpy format with `floor`.
- `fig/gap3_diagnostic.png` — two-panel: log(L₁) vs. t and vs. √t.
- `fig/gap3_residuals.png` — residuals of both fits.

**Noise floor.** N = 10⁷, 256 bins: √(2·256/(π·10⁷)) ≈ 0.00404.
Data bottoms at the floor around t = 140; fits restricted to
pre-floor points.

---

## Phase 2 — deferred, not run

Plan was N = 10⁸ at longer t for confirmation. Phase 1 was
decisive enough that phase 2 wasn't needed. Easy to execute if a
referee requests higher resolution: bump N_WALKERS to 1e8 in
`gap3_phase1.py`, expect runtime ~25 min.

---

## Phase 3 — biased BS(1,2), convergence shape

**Question.** Does the biased walk floor at L₁ > 0 (earlier
reported as 0.091), or converge to Benford via a two-regime
mechanism (active ε-minorization → post-escape Weyl rotation)?

**Setup.**
- Script: `experiments/math/benford/gap3_phase3.py`
- Biased walk: weights (0.2, 0.2, 0.4, 0.2) on {b, b⁻¹, a, a⁻¹}.
  Net multiplicative drift +0.20/step.
- N = 10⁶ walkers, t ∈ [0, 50 000], log-spaced checkpoints.
- State representation: (m, E, sign) with m float64, E int64,
  sign int8. Three-case b-step (|E| > 20 frozen; E < −20 snap to
  origin; |E| ≤ 20 direct computation). Required because |E|
  grows linearly with positive drift and would exceed float64
  range at t = 50 000.
- Seed: 0xB1A5.
- Runtime: 24:33 on local machine.

**Result.** Converges to Benford — no floor at 0.091. L₁ reaches
the N = 10⁶ noise floor (0.0128) by t ≈ 2000 and fluctuates
there through t = 50 000.

| t | L₁ | ⟨E⟩ | active fraction |
|---|---|---|---|
| 0 | 1.9922 | 0.00 | 100% |
| 50 | 0.0316 | 2.77 | 100% |
| 500 | 0.0169 | 29.9 | 3.1% |
| 1000 | 0.0146 | 60.0 | 0% |
| 2000 | 0.0135 | 120 | 0% |
| 10 000 | 0.0134 | 602 | 0% |
| 50 000 | 0.0138 | 3010 | 0% |

Two-regime decay visible:
- t < 500: active phase, walkers near E=0, fast contraction.
- t ∈ [500, 1000]: escape transition, active fraction
  collapses 100% → 0% as walkers drift to |E| > 20.
- t > 1000: post-escape, walkers frozen; residual above-floor
  decays roughly as 1/t (consistent with Weyl equidistribution
  from a/a⁻¹ rotation). L₁ above floor: 0.004 at t=500 → ~0 at
  t=2000 (below resolution).

**Power-law / stretched late-time fits reported but unreliable:**
both R² ≈ 0.3–0.5 because the post-escape data is at the noise
floor. The two-regime *shape* is unambiguous; the precise
post-escape rate would need N ≈ 10⁸ and focused sampling on
t ∈ [500, 10⁴].

**Previously reported "L₁ = 0.091 at walkers of magnitude 10^1200"
superseded.** Likely a digit-level (9-bin) L₁ snapshot or an
earlier run with fewer walkers.

**Artifacts.**
- `data/gap3_phase3.csv` — (t, L1, mean_E, active_frac).
- `data/gap3_phase3.npz` — numpy format including `floor`.
- `fig/gap3_biased.png` — two-panel: log-log and log-linear.

---

## Reproducibility

Both phase scripts are standalone, run with `sage -python -u`.
Dependencies are in `experiments/math/benford/common.py`
(matplotlib, numpy; sage ships both). Seeds are hard-coded, so
re-running produces identical data. Machine: macOS on M-series
Apple silicon, Python 3 / numpy 2.3.2, SageMath 10.8.

---

## What these runs do and don't establish

**Do:**
- Symmetric BS(1,2) walk L₁ decays as exp(−c√t), c ≈ 0.55.
- Biased BS(1,2) walk (positive multiplicative drift) converges
  to Benford to within sampling noise by t ≈ 2000.
- Two-regime decay for biased case (fast active → algebraic
  post-escape) is qualitatively confirmed.

**Do not:**
- Prove anything (no theoretical proof of either finding).
- Quantify the post-escape algebraic rate precisely.
- Address negative-drift biased walks (recycled-through-origin
  regime). Motivated "phase 3b" in original plan, not run.
- Establish initial-condition independence. All runs start at
  x = √2 (phase 1) or m = log₁₀ √2, E = 0 (phase 3).
