# FP32-SIM

## Why this plan exists

Precision concerns about the sim come in two flavors:

1. **"fp64 might be insufficient"** — some subtle long-horizon
   calculation could be quietly bottoming out at fp64's ~10⁻¹⁶
   per-step roundoff. Cannot be tested from below; would need
   extended-precision (float128 / mpmath). Out of scope here.
2. **"fp64 might be overkill"** — results might depend on a
   knife-edge of precision that happens to land above fp64 but
   would collapse at lower precision. Testable from below by
   rerunning at fp32 and checking whether the answers move.

This plan addresses (2) directly. fp32's 24-bit significand gives
~10⁻⁷ per-operation roundoff — four orders of magnitude coarser
than fp64. Over 600 steps of a/a⁻¹/b/b⁻¹, accumulated error on
the mantissa coordinate is ~6×10⁻⁵: three orders of magnitude
below our smallest L₁ signal but comfortably above pure bit-noise.

If the T1b story survives a 10⁴× precision loosening, that is a
strong empirical robustness claim. If it doesn't, we've located
a precision floor and fp64 is empirically justified rather than
just bound-estimated.

**Two observables to test:**

- **Result 1 (M3 IC (b)'s α̂ = 0.525).** The primary direct-α
  anchor. Rerun at fp32 and check α̂ moves by < 2%.
- **Result 5 (dyadic zero-hit dichotomy).** fp64's demonstration
  was zero numerical zero-events across 7 non-dyadic/irrational
  ICs × 6×10⁹ walker-steps. At fp32, does the dichotomy survive?
  If yes, even stronger evidence. If some non-dyadic IC starts
  producing numerical zeros at fp32, we've located the float-
  precision boundary where algebra stops being exactly respected.

**Where this plan runs.** On the local ARM M1 machine, in parallel
with the x86 beef-box runs specified in `EXPENSIVE-BEEF-BOX-SIM.md`.
Total sim time ≈ 75 min, fits trivially alongside other work.

## Coordination note

Not part of `ALGEBRAIC-SIM-MESS-PLAN.md`'s default schedule.
Post-`T1B-EVIDENCE-MAP.md` precision-robustness hardening.

Independent of the x86 beef-box runs: no shared data, no shared
machine. Results are directly comparable to existing fp64 outputs
from `m3_results.npz` (for Run 1) and `run1_dyadic_ladder/*.npz`
(for Run 2).

## Kernel port

Changes to the standard M3/M1 step kernel to produce an fp32
variant:

1. **Walker state dtype.**
   - `m`: float64 → **float32**
   - `E`: int32 (unchanged; integer)
   - `sign`: int8 (unchanged)

2. **Constants cast to fp32 at use site.**
   - `LOG10_2_F32 = np.float32(math.log10(2.0))`
   - `LOG10_SQRT2_F32 = np.float32(0.5 * math.log10(2.0))`
   - IC m values (for the dyadic-ladder IC set) cast to fp32
     before passing to initializers.

3. **b-step reconstruction.** In the active branch,
   `x = sign * 10^(E+m)` becomes an fp32 operation. No overflow
   issues because E_THRESH = 20 keeps 10^(E+m) well within fp32's
   ~3.4×10³⁸ range.

4. **Accumulators kept at fp64.** Summing cos(arg) over 10⁷
   elements into an accumulator can lose fp32 precision via
   sum-of-small-residuals. Keep `cos_sum`, `sin_sum` at float64;
   the per-element inputs may be fp32. Histogram normalization
   similarly stays in float64 because the cost is trivial.

5. **Nothing else changes.** The RNG, the E_THRESH shortcut, the
   frozen/snap branches, the exact-zero restart convention, the
   sampling grid, the output schema — all identical to fp64.

### Port effort and validation

Expected engineering time: ~30 min careful type management.

Pre-run validation: smoke-test at N = 10⁵ × n = 50 on IC = √2,
confirm L₁ trajectory matches the fp64 reference within ~1%. This
catches accidental fp64 leaks (e.g. forgetting to cast a
constant) that would produce an inadvertently-fp64 run.

## Run 1 — M3 IC (b) at fp32

**Purpose.** Stress-test Result 1's α̂ = 0.525 at reduced
precision.

**Spec.**

    N = 10⁷ walkers
    Symmetric measure
    IC: m = log₁₀√2 (delta, fp32), E ~ Uniform{−5, …, 5},
        sign = +1   (exactly M3 IC (b) structure)
    Time range: n = 0 to 600
    Sampling: M1 grid
    Dtype: m as float32 throughout
    Output: L₁(n), ensemble ĥ(r, n), l2_norm(n), plus a
        zero-hit counter for diagnostic (expected 0 on this IC)

**Analysis.**

- **A1a.** Fit α̂ on [100, 600] under fp32 and compare to fp64's
  0.525. Decision threshold: if α̂_fp32 ∈ [0.50, 0.55], agreement
  with fp64 is clean.
- **A1b.** Diff L₁(n) vs fp64 `m3_results.npz['ic_b_l1']` at each
  sample time. Typical expected deviation: O(10⁻⁵) or smaller.
  Any deviation > 10⁻³ across most of the trajectory would
  indicate a kernel bug or a genuine precision-floor effect.

**Cost.** ~8 min on the M1.

## Run 2 — Dyadic-ladder at fp32

**Purpose.** Stress-test Result 5's algebraic zero-hit dichotomy.

**ICs (8 total, same as T1B-UNIT-BALL Run 1).**

| label | x₀         | class          |
|:------|:-----------|:---------------|
| D1    | 1          | dyadic         |
| D2    | 3/2        | dyadic         |
| D3    | 9/8        | dyadic         |
| N1    | 7/5        | non-dyadic     |
| N2    | 17/12      | non-dyadic     |
| N3    | 99/70      | non-dyadic     |
| I1    | √2         | irrational     |
| I2    | φ          | irrational     |

**Spec per IC.**

    N = 10⁷ walkers
    Symmetric measure
    IC: x = x₀, cast to fp32 at init; m = log₁₀(x₀) in fp32,
        E = 0, sign = +1
    Time range: n = 0 to 600
    Sampling: M1 grid
    Dtype: m as float32 throughout
    Exact-zero convention: restart (matches T1B-UNIT-BALL Run 1)
    Output: L₁(n), ensemble ĥ(r, n), l2_norm(n),
        zero_hits_per_step (critical for this run)

**Analysis.**

- **A2a (dyadic zero-hit rates at fp32).** For D1–D3, measure
  zero-hits/walker and compare to fp64 values (0.791, 0.172,
  0.019). Small differences expected from last-bit roundoff in
  step_b reconstruction; should be within ~5%.
- **A2b (non-dyadic + irrational zero-hit rates at fp32).** For
  N1–N3 and I1–I2, check whether any produce nonzero numerical
  zero events. The fp64 answer was exactly 0 across 4.2×10¹⁰
  walker-steps (7 ICs). The fp32 question: does the dichotomy
  survive, or does the coarser precision allow spurious zeros?

**Decision rule.**

- All 5 non-dyadic/irrational ICs still produce **exactly 0**
  zero-hits at fp32 ⇒ **algebraic dichotomy is robust to 10⁴×
  precision loss.** This is the strongest possible form of
  Result 5.
- Some non-dyadic/irrational IC produces nonzero zero-hits at
  fp32 ⇒ the dichotomy is an fp64 phenomenon, broken at fp32.
  Report the specific IC and count as a precision-floor
  observation. Does not weaken Result 5's fp64 finding but
  does bound the precision regime.
- Dyadic zero-hit rates diverge by > 10% from fp64 values ⇒
  investigate for kernel bug; fp32 port probably has a leak.

**Cost.** 8 ICs × 8 min = ~65 min on the M1.

## Total cost

- Kernel port + smoke test: ~30 min engineering
- Run 1 (M3 IC (b) fp32): ~8 min
- Run 2 (dyadic-ladder fp32): ~65 min
- Cross-analysis and summary: ~15 min

**Total ≈ 2 hours wall time**, mostly compute that runs in the
background while the x86 beef-box handles the expensive runs.

## Output files

- `run_fp32_checks.py` — the new runner
- `fp32_results/ic_b_fp32_results.npz` — Run 1 output
- `fp32_results/dyadic_ladder/{D1..I2}_fp32_results.npz` — Run 2 outputs
- `fp32_SUMMARY.md` — analysis document

Schemas match the fp64 siblings so existing analysis scripts work
without modification.

## What this plan does NOT do

- Does not test fp16 or lower. fp16 requires kernel restructuring
  (E_THRESH reduction, careful fp16 handling) outside this plan.
- Does not test fp128 / mpmath from above. "fp64 is insufficient"
  is a different concern and would need a separate effort.
- Does not extend any run to M4-style long horizons. Result 4's
  long-horizon question is the x86 beef-box's problem.
- Does not re-port B3 or M4 to fp32. B3's K̂ measurement is an
  ensemble average; fp64 vs fp32 on an averaged matrix is
  unlikely to move the spectral radius measurably, and rerunning
  would be a low-value precision check compared to the two above.

## Interpretation guidance

If fp32 agrees with fp64 on both runs, the precision-robustness
argument is **empirically** established, not just bound-estimated.
Any concerns about "is fp64 precise enough for this sim?" are
answered by: "a 10⁴× loosening doesn't move the answer, so
we're nowhere near a precision floor."

If fp32 diverges, we've located something interesting and can
report it honestly: "the algebraic dichotomy (or the α̂
measurement) holds at fp64 but breaks at fp32, indicating a
precision-sensitive regime that fp64 is above but fp32 is not."
Neither case is bad for the paper; both are clean empirical
statements about the precision behavior of the sim.
