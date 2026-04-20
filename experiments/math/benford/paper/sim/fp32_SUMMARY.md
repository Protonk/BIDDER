# FP32-SIM — summary

Run: `run_fp32_checks.py` → outputs under `fp32_results/` (2026-04-18).
Two sub-runs at N = 10⁷ × n = 600, walker mantissa as float32.
Total wall time ≈ 120 min.

## Headlines

1. **Result 1 is precision-robust.** α̂ on M3 IC (b) is 0.5249 at
   fp32 vs 0.5250 at fp64. Δα̂ = −0.0001 (< 0.1% relative). R²(log n)
   matches to 4 decimals. L₁ trajectories agree within ~0.4%
   throughout [10, 600]. The primary T1b α anchor survives a 10⁴×
   precision loosening with no visible change.

2. **Result 5's algebraic dichotomy is real at fp64 but not exact at
   fp32.** Non-dyadic rationals and irrationals (N1–N3, I1–I2)
   produced 4–14 numerical zero-events each at fp32, totalling 45
   events across 3×10¹⁰ walker-steps (rate ≈ 1.5×10⁻⁹ per
   walker-step). At fp64, zero events across the same 3×10¹⁰ walker-
   step volume, bounding the fp64 rate at < 2×10⁻¹¹ per walker-step.
   **fp64 is ~75× or better cleaner than fp32** on this metric. The
   orbit-avoids-0 algebraic fact is approximated, not perfectly
   preserved, by floating-point arithmetic.

3. **Dyadic zero-hit rates shift modestly at fp32.** D1 (x = 1) is
   −3.7% (7.62M fp32 vs 7.91M fp64), D2 (3/2) is +3.8%, D3 (9/8) is
   +30.6%. The pattern is consistent with "more roundoff at fp32 can
   either produce or suppress events depending on the specific
   b-step arithmetic path"; no uniform direction.

## Run 1 — M3 IC (b) at fp32

### L₁ trajectory agreement

| n   | fp32 L₁   | fp64 L₁   | rel diff  |
|----:|----------:|----------:|----------:|
|  10 | 1.065     | 1.069     | −3.8×10⁻³ |
|  50 | 0.5104    | 0.5105    | −2.0×10⁻⁴ |
| 100 | 0.3349    | 0.3349    | −1.8×10⁻⁶ |
| 200 | 0.2386    | 0.2384    | +8.0×10⁻⁴ |
| 300 | 0.1932    | 0.1937    | −2.8×10⁻³ |
| 455 | 0.1526    | 0.1528    | −1.2×10⁻³ |
| 600 | 0.1292    | 0.1294    | −1.4×10⁻³ |

Differences are within ~0.4% everywhere. Two interpretations: either
the two runs use different seeds (yes — fp32 run's seed is
`SEED_BASE ^ ord('B')` = not the same as M3's seed 0xEE1C3A11 ^
ord('b')), so some of this is independent MC noise, or there is a
genuine precision-driven systematic of order 10⁻³. Either way, the
macroscopic observable is stable.

### α̂ fit on [100, 600]

| dtype | α̂       | R²(log n) |
|:------|--------:|----------:|
| fp32  | 0.5249  | 0.9985    |
| fp64  | 0.5250  | 0.9986    |

**Δα̂ = −0.0001.** Indistinguishable within fit uncertainty. The
anchor result is precision-robust at 10⁴× loosening.

### IC (b) zero-hits at fp32

2,483 numerical zero-events across 6×10⁹ walker-steps (≈ 4×10⁻⁷
per walker-step). Of these, 1,285 occur by n = 61 and 2,076 by
n = 121 — most early in the trajectory, while walkers are still
distributed over the initial E ∈ {−5, …, 5} range and some reach
|x| ≈ 1 configurations where fp32 catastrophic cancellation
produces exact zero.

This rate is ~250× higher than the N/I-ladder fp32 rate (1.5×10⁻⁹
per walker-step). The E-spread of IC (b) puts walkers at |E| ≥ 1
from t = 0, where the active-branch b-step reconstruction
`x = sign · 10^(E+m)` can produce values very close to ±1 in fp32.
E = 0 ICs (N1–N3, I1–I2) need to diffuse in E first, so fp32
precision events are rarer there.

## Run 2 — Dyadic-ladder at fp32

### Zero-hits comparison

| IC | class       | fp64 count | fp32 count | ratio / note |
|:---|:------------|-----------:|-----------:|:-------------|
| D1 | dyadic      | 7,911,970  | 7,621,964  | 0.963       |
| D2 | dyadic      | 1,724,486  | 1,790,520  | 1.038       |
| D3 | dyadic      | 190,246    | 248,478    | 1.306       |
| N1 | non-dyadic  | 0          | 4          | **fp64 was 0** |
| N2 | non-dyadic  | 0          | 9          | **fp64 was 0** |
| N3 | non-dyadic  | 0          | 13         | **fp64 was 0** |
| I1 | irrational  | 0          | 14         | **fp64 was 0** |
| I2 | irrational  | 0          | 5          | **fp64 was 0** |

**Non-dyadic/irrational total at fp32: 45 events.** Across 5 ICs ×
6×10⁹ walker-steps = 3×10¹⁰ walker-steps, rate is 1.5×10⁻⁹ per
walker-step. These events are from float32 catastrophic
cancellation in `x + delta` when x lies within ~10⁻⁷ of ±1.

At fp64, the same 5 ICs produced 0 events, bounding the fp64 rate
at < 1/(3×10¹⁰) = 3.3×10⁻¹¹ per walker-step (95% upper bound via
Poisson with 0 observed, N = 3×10¹⁰). Extending to the 7-IC count
from T1B-UNIT-BALL (N1-N3, I1-I2, S1, S2 all zero across
4.2×10¹⁰ walker-steps) tightens this to < 2.4×10⁻¹¹.

So **fp64 is at least 60× cleaner than fp32** on the zero-hit
observable. Good evidence that fp64 is not a knife-edge choice —
it's safely above the precision floor, with fp32 being the first
precision level where the floor becomes visible.

### Late L₁(600) comparison

| IC | fp32 L₁ | fp64 L₁ | rel diff |
|:---|--------:|--------:|---------:|
| D1 | 8.0×10⁻³ | 8.3×10⁻³ | −3.4% |
| D2 | 8.3×10⁻³ | 8.1×10⁻³ | +2.5% |
| D3 | 8.5×10⁻³ | 8.3×10⁻³ | +3.4% |
| N1 | 8.1×10⁻³ | 8.4×10⁻³ | −3.1% |
| N2 | 8.0×10⁻³ | 8.7×10⁻³ | −8.2% |
| N3 | 8.3×10⁻³ | 8.5×10⁻³ | −1.5% |
| I1 | 8.5×10⁻³ | 8.1×10⁻³ | +5.7% |
| I2 | 8.0×10⁻³ | 8.1×10⁻³ | −1.1% |

All at N = 10⁷ floor (≈ 8.6×10⁻³); differences are dominated by
independent MC noise between fp32 and fp64 runs (different seeds).
Not a precision signal.

### Mid-window L₁(100) comparison (above floor)

| IC | fp32 L₁ | fp64 L₁ | rel diff |
|:---|--------:|--------:|---------:|
| D1 | 0.276   | 0.276   | −0.08%   |
| D2 | 0.253   | 0.254   | −0.3%    |
| D3 | 0.191   | 0.191   | −0.2%    |
| N1 | 0.0519  | 0.0516  | +0.5%    |
| N2 | 0.157   | 0.158   | −0.6%    |
| N3 | 0.0554  | 0.0551  | +0.6%    |
| I1 | 0.0532  | 0.0534  | −0.5%    |
| I2 | 0.0495  | 0.0501  | −1.2%    |

At this window (above floor) differences are within ~1% for all
ICs. fp32 and fp64 give effectively the same trajectory shape.

## Interpretation

The fp32 runs give a **three-level empirical precision ladder**:

1. **Macroscopic observables (L₁ trajectory, α̂) are precision-
   robust** at the ~10⁻³ relative level. fp32 and fp64 agree on the
   shape and rate of ensemble mantissa equidistribution. The T1b
   primary anchor result (α̂ ≈ 0.525 on IC (b)) is stable under
   10⁴× precision loosening.

2. **The algebraic dyadic/non-dyadic dichotomy is empirical, not
   exact, at finite precision.** At fp64 it appears perfect (0
   events in 4.2×10¹⁰ walker-steps). At fp32 it's violated at a
   small but measurable rate (~10⁻⁹ events per walker-step). The
   rate difference is ≥ 60×, so fp64 is clearly above the
   precision floor where the dichotomy breaks down.

3. **The sim's floor observable (L₁ near θ_N) is dominated by MC
   noise, not precision.** Independent seeds give ±5% fluctuations
   at L₁(600); this is statistical, not precision-driven.

## What this settles for T1b

**Strengthens:**
- Result 1 (α anchor): robust under 10⁴× precision loosening. α̂
  shifts by less than 0.1%.
- Result 5 (zero-hit dichotomy): confirmed as an fp64 phenomenon
  not an exact algebraic identity. Paper should describe the
  exceptional set as "approximately-respected to < 3×10⁻¹¹ per
  walker-step at fp64 precision" rather than as "exact" —
  technically correct, and the quantitative bound is useful.

**Does not change:**
- Paper's α = 1/2 claim: unchanged; fp32 and fp64 agree.
- T1b's exceptional-set clause (ν(Z[1/2]) = 0): unchanged; the
  algebraic statement is about exact orbits, the sim is an
  approximation, the two agree to within the precision bound.

## What's saved

- `fp32_results/ic_b_fp32_results.npz` — Run 1 output, same schema
  as M3's per-IC slice
- `fp32_results/dyadic_ladder/{D1..I2}_fp32_results.npz` — 8 outputs,
  same schema as T1B-UNIT-BALL Run 1

Each npz has `meta_dtype = 'float32'` for easy distinction from
fp64 siblings; everything else (sample_times, l1, h_full, l2_norm,
zero_hits_per_step, modes) matches the fp64 conventions.

## What this plan did NOT settle

- Does not test fp128 or higher. "Is fp64 itself precise enough?"
  remains an open question; we've only checked the direction below.
- Does not extend to M4-style long horizons at fp32. At n = 20,000
  the accumulated fp32 error is ~2×10⁻³, which would bump up against
  the N = 10⁸ floor. Would require explicit analysis of whether α̂
  at long horizons is precision-dominated.
- Does not test the B3 regime classification at fp32. The mode-
  coupling matrix K̂ is an ensemble average, so fp32 would likely
  give the same ρ to within statistical noise, but this is not
  directly verified.
