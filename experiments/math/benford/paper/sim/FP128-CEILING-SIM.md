# FP128-CEILING-SIM

## Why this plan exists

After the fp16-mini ladder, the precision-robustness story has
three data points from *below* fp64:

- fp16 pristine zero-hit rate ≈ 2×10⁻⁵
- fp32 rate ≈ 1.5×10⁻⁹
- fp64 rate < 3×10⁻¹¹ (below detection at our volumes)

All consistent with `rate ∝ fp_eps`, and all confirming that fp64
is above the precision floor. The remaining open question is
*from above*: is fp64 itself precise enough, or could a subtle
long-horizon accumulation of fp64 roundoff be biasing the T1b
results in a way that higher precision would correct? The
accumulated-error bound estimate says fp64 is fine (≤ 7×10⁻¹⁴
accumulated rounding on m over 600 steps, below any observable
L₁ scale), but that's a bound, not a measurement.

This plan closes the from-above direction by rerunning a single
IC (M3 IC (b)) at 128-bit arbitrary precision via gmpy2/MPFR and
comparing to a matched fp64 run. If α̂ and the L₁ trajectory
agree within sampling noise, fp64 is empirically confirmed as
sufficient. If they disagree, fp64 is empirically insufficient
and the paper needs to commit to higher precision.

**Coordination.** Runs locally on M1 in parallel with x86
beef-box. Expected total compute ≈ 15–20 min.

## Implementation notes

- **Precision target: 128-bit (≈ 38 decimal digits).** 75 bits
  more than fp64, so any accumulated fp64 roundoff of order
  2⁻⁵³ should be resolved.
- **Backend: gmpy2.mpfr** via `get_context().precision = 128`.
  MPFR is the fast C-backend arbitrary-precision library. On
  this machine `np.longdouble` aliases to fp64 (ARM M1), so
  numpy's extended precision is not available; gmpy2 is the
  practical route.
- **Architecture: numpy object arrays of mpfr scalars.** Stores
  m as `np.ndarray(dtype=object)` with each element an
  `mpfr(128-bit)`. E stays int32, sign stays int8. The b-step's
  active branch uses Python-level per-walker iteration (gmpy2
  ops don't broadcast); a-step uses numpy broadcasting on
  object arrays, which is faster.
- **Benchmark (measured, 2026-04-18):** ≈ 20 μs per active
  b-step per walker, ≈ 0.5 μs per a-step per walker. At average
  mix (1/4 each of a, a⁻¹, b, b⁻¹), ~10 μs per walker-step.
  At N = 10⁵ × n = 600: ~10 min wall time.

## Scope — minimal-sufficient test

**One IC, one horizon, one precision level, matched control.**

- **IC:** M3 IC (b) structure — m = log₁₀√2 (high-precision
  delta), E ~ Uniform{−5, …, 5}, sign = +1. This is our α̂
  anchor; if fp64 has a precision problem anywhere, it should
  show up here.
- **N:** 10⁵ walkers. Lower than M3's 10⁷ because mpmath/gmpy2
  is much slower than fp64; N = 10⁵ is the sweet spot where
  L₁ is resolvable above the (higher) N = 10⁵ null floor on
  [100, 600] and the run completes in ~10 min.
- **n:** 600 steps (match M3 original).
- **Precision levels tested:** 128-bit (gmpy2) + fp64 (control)
  at same N = 10⁵ and same seeds for matched comparison.

The null floor at N = 10⁵ is θ_N ≈ 2.72×10⁻³ × √(10⁸/10⁵) ≈
0.086. IC (b)'s L₁ trajectory: 0.335 at n = 100, 0.129 at n =
600 — comfortably above this higher floor throughout the [100,
600] fit window. Noise is 100× the N = 10⁷ run's but still fine
for a 2%-level α̂ measurement.

## Analysis

- **A1. L₁ trajectory agreement.** Fp64 vs fp128 at matched
  seed, same sample times. Expected: relative difference within
  sampling noise (O(1/√N) ≈ 3×10⁻³ at N = 10⁵). Any systematic
  beyond this indicates fp64 precision issue.
- **A2. α̂ agreement on [100, 600].** Primary observable. Fit
  `log L₁ = a − α log n` on both runs, compare α̂.
- **A3. Mantissa trajectory at individual-walker level.** Pick
  10 seeded walker indices, log (m, E, sign) at n = 100, 300,
  600 for both precisions. Check trajectory drift: at 128-bit,
  m should be accurate to < 10⁻³⁰, so comparing to fp64's m
  reveals the *actual* fp64 accumulated rounding. Expected
  magnitude: ≤ 7×10⁻¹⁴ per earlier bound estimate; if we see
  10⁻⁸ or worse, there's an accumulation issue.

## Decision rule

- **|Δα̂| < 0.01 and L₁ trajectories agree within sampling
  noise ⇒ fp64 sufficient.** Paper can cite the three-precision
  ladder (fp16 / fp32 / fp64) plus the fp64/fp128 agreement as
  a complete precision-robustness argument in both directions.
- **|Δα̂| ∈ [0.01, 0.05] ⇒ borderline.** fp64 introduces a
  small systematic; paper should note the magnitude and decide
  whether to upgrade some specific calculation to higher
  precision.
- **|Δα̂| > 0.05 ⇒ fp64 insufficient.** Primary results would
  need revisiting at higher precision. Unexpected but
  important if it happens.

The analysis also produces the "fp64 accumulated rounding
magnitude" as a direct empirical measurement (A3), which is
useful for paper footnoting regardless of the α̂ outcome.

## Output

- `run_fp128_check.py` — the runner
- `fp128_results/ic_b_fp128_results.npz` — 128-bit run
- `fp128_results/ic_b_fp64_matched_results.npz` — matched fp64 control
- `fp128_SUMMARY.md` — analysis with trajectory comparison

Schemas match `m3_results.npz`'s per-IC slice for cross-reference.

## Cost

- 128-bit gmpy2 run: ~10 min
- fp64 matched control: ~30 sec
- Analysis: ~5 min
- **Total ≈ 15 min**, local on M1 parallel with beef-box.

## What this plan does NOT do

- Does not test precision from below again (fp16 / fp32 already
  covered).
- Does not re-run the dyadic ladder or other ICs at 128-bit.
  The scope is specifically "is fp64 sufficient for the α̂
  measurement?" Expanding to other ICs would not add
  information unless fp64 fails here.
- Does not test mpmath itself or extended-precision float128.
  Both are available but gmpy2 is the fastest path to 128-bit;
  mpmath is reserved as a cross-check if gmpy2 gives a
  surprising result.
- Does not extend the horizon beyond n = 600. The long-horizon
  question (M4-style n = 20000) is the x86 beef-box's job; this
  plan addresses precision only at the M3 scale.

## Expected outcome (prediction)

Based on the accumulated-error bound estimate (~7×10⁻¹⁴ at n =
600), fp64 should agree with fp128 to within 13 decimal places
on per-walker m values. L₁ and α̂ should agree to within sampling
noise. So the expected result is "fp64 sufficient, confirmed from
above" — the null-ish outcome that closes the precision question.

If this prediction fails, it's interesting and directly paper-
relevant. If it holds, the paper can cite one sentence:

> fp64 precision was empirically verified from both directions.
> Below: the fp16 / fp32 ladder (rate ∝ fp_eps, fp64 below
> detection, see Result 5). Above: direct comparison against a
> 128-bit MPFR rerun of M3 IC (b), which agrees with the fp64
> α̂ to within sampling noise.

Closes the precision story cleanly, with empirical support in
both directions.
