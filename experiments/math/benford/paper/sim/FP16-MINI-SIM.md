# FP16-MINI-SIM

## Why this plan exists

After the fp32 run, Result 5's description needs rewording: the
dyadic/non-dyadic dichotomy is respected at fp64 but has a
detectable floor at fp32 (~1.5×10⁻⁹ per walker-step). A two-point
precision ladder — fp64 zero, fp32 nonzero — makes the dichotomy
sound like a knife-edge fp64 phenomenon that happens to land on
the algebraic answer.

A three-point ladder — fp64, fp32, fp16 — tells a better story IF
the events-per-walker-step rate scales monotonically with
precision. Then Result 5 can be restated:

> At precision fpN (k-bit significand), the sim respects the
> algebraic dichotomy up to catastrophic-cancellation events at a
> rate approximately 2^{−k} per active b-step. At fp64 (k=53) the
> rate is < 3×10⁻¹¹ per walker-step, below detection at our
> volumes.

That framing is empirical, quantitative, and turns the observation
into a feature rather than a caveat. It also gives the paper a
clean precision-scaling footnote.

## Coordination note

Runs locally on the M1 in parallel with x86 beef-box work. Total
compute ≈ 15–30 min. Independent of any other run; uses existing
fp64 baseline from T1B-UNIT-BALL Run 1 and fp32 baseline from
`run_fp32_checks.py`.

## Kernel changes for fp16

Several changes from fp32 port:

1. **Walker state dtype.** m: `float16`; E: `int32` (unchanged);
   sign: `int8` (unchanged).

2. **E_THRESH reduced from 20 to 4.** fp16 max finite ≈ 65504, so
   `10^(E+m)` overflows at E ≥ 5. E_THRESH = 4 keeps the active-
   branch reconstruction within fp16 range (10^4 ≈ 10000; 10^(4+m)
   for m ∈ [0, 1) up to ≈ 10^5 = 100000 which still overflows
   at m close to 1). Safer: E_THRESH = 3 — gives 10^(3+m) up to
   10^4, comfortably within fp16 range.

3. **Constants cast to fp16 at use site.** LOG10_2_F16 =
   `np.float16(log₁₀ 2)`, etc. Accumulated error per a-step is ~2⁻¹¹
   ≈ 5×10⁻⁴; over 100 steps, ~5×10⁻². Large enough to visibly
   distort the mantissa trajectory at late n.

4. **fp64 accumulators for statistics.** Fourier sums, L₁
   histograms stay at fp64. The per-walker m is fp16; everything
   else unchanged from fp32.

### Matched fp32 and fp64 controls

Because E_THRESH = 3 in the fp16 run is different from E_THRESH = 20
in the main fp32 run, matched controls are needed:

- **fp32 @ E_THRESH = 3** — tests fp16 vs fp32 at same envelope.
- **fp64 @ E_THRESH = 3** — measures the *mechanical snap-induced
  baseline* at this envelope. At E_THRESH = 3 walkers frequently
  reach |E| > 3 and trigger the snap branch, which re-emits them
  at x = ±1. The next b-step has probability 1/4 of producing
  x_new = 0 *exactly* via pure arithmetic (1 − 1 = 0, representable
  at any precision). So at E_THRESH = 3 all dtypes show nonzero
  zero-hit rates, dominated by this mechanical contribution. The
  fp64 control measures that baseline; subtracting it from fp32
  and fp16 isolates the precision-induced zero-hits.

Expected decomposition:

    rate(fp64_ctrl)  ≈ mechanical snap-induced baseline
    rate(fp32_ctrl)  ≈ baseline + fp32 precision signal
    rate(fp16)       ≈ baseline + fp16 precision signal

Differences `rate(fp32_ctrl) − rate(fp64_ctrl)` and
`rate(fp16) − rate(fp64_ctrl)` are the precision signals, expected
to scale with fp epsilon.

## Run 1 — FP16 mini

**Spec.**

    N = 10⁷ walkers
    n_max = 100 (mini)
    E_THRESH = 3
    Symmetric measure, R2-style exact-zero restart
    Dtype: m as float16 throughout
    ICs (5, representative subset):
        D1: x = 1             (dyadic)
        N1: x = 7/5           (non-dyadic)
        I1: x = √2            (irrational, E = 0)
        I2: x = φ             (irrational, E = 0)
        B-like: m = log₁₀√2 delta, E ~ Uniform{−3..3}
            (IC (b) analog adapted to fp16's tighter envelope)
    Output: L₁(n), zero_hits_per_step, mean_active_fraction(n)

**Analysis.**

- **R1a.** Zero-hit rates for each IC, computed per walker-step
  and per active walker-step (active = |E| ≤ E_THRESH, i.e. the
  subpopulation that actually runs the b-step reconstruction).
- **R1b.** L₁ trajectory shape. Does fp16 still give sensible
  decay even with the distorted rotation quantum? If fp16 breaks
  the mantissa dynamics entirely, the rate measurement is still
  valid for the precision question but the L₁ data shouldn't be
  taken as a trajectory measurement.

## Run 2 — FP32 E_THRESH=3 control

**Spec.** Identical to Run 1 but fp32 instead of fp16. Measures
the zero-hit rate under the same envelope as fp16 but with fp32
precision. Same 5 ICs, same N and n and seeds.

**Why this run matters.** Without it we can't distinguish
"precision reduction" from "lower E_THRESH increases restart
frequency." E_THRESH controls how often walkers are snapped to
(m=0, E=0, sign(delta)) = x = ±1, and b-steps from x = ±1 have a
25% chance of producing exact zero. So lowering E_THRESH raises
the zero-hit rate independently of precision.

## Precision-ladder analysis

Construct a 3-point table per IC and per class:

| IC   | fp64 rate (old, E_THRESH=20) | fp32-main rate (E_THRESH=20) | fp32-control rate (E_THRESH=3) | fp16 rate (E_THRESH=3) |
|:-----|:-----------------------------|:------------------------------|:-------------------------------|:------------------------|

The meaningful comparisons:

1. **fp32-control vs fp16** (E_THRESH matched, precision varies):
   the pure precision-sensitivity signal. Expected: fp16 rate >>
   fp32-control rate by roughly (fp32 eps / fp16 eps)² ≈ 10⁸, if
   the catastrophic-cancellation mechanism is the dominant source.
2. **fp32-main vs fp32-control** (precision matched, E_THRESH
   varies): the envelope-effect signal. Expected: fp32-control
   rate > fp32-main rate by some factor reflecting how much more
   often walkers get snapped.
3. **fp64 vs fp32-main** (our existing comparison): 0 vs
   1.5×10⁻⁹ per walker-step.

**Decision rule (soft).**

- fp16 rate ≫ fp32-control rate, both ≫ fp64 rate, with a
  scaling roughly consistent with fp-eps² or fp-eps ⇒ clean
  precision ladder. Paper can restate Result 5 as a precision-
  floor observation with quantitative scaling, instead of
  "exact at fp64." Nicer wording.
- Rates do not scale monotonically with precision ⇒ something
  else is going on besides catastrophic cancellation. Could be
  mode-mixing precision effects, or dominant-mode arithmetic
  sensitivity. Would need investigation before rewording.

## Expected cost

Run 1 (fp16, 5 ICs): ~5 ICs × 10⁷ walker × 100 steps = 5×10⁹
walker-steps. fp16 on CPU is typically 2–3× slower than fp64
(converted to fp32 internally on most platforms), so throughput
≈ 2×10⁶ ws/s on M1. Total: ≈ 2500 sec = 40 min.

Run 2 (fp32 control, 5 ICs): at fp32 throughput (roughly same as
fp64), ~2000 sec = 30 min.

**Total: ~70 min on M1.** Same order as fp32 main run.

## What this plan does NOT do

- Does not test fp16 at longer n (100 is adequate for rate
  measurement; longer would just accumulate the fp16 rotation-
  quantum drift without adding precision-comparison value).
- Does not claim fp16 gives physically-meaningful L₁ trajectory.
  The rotation quantum has ~10⁻⁴ error per step, so over 100
  steps the mantissa distribution is noticeably distorted
  compared to fp64. This plan uses fp16 only for the zero-hit-
  rate measurement; the L₁ is reported for diagnostic.
- Does not re-establish T1b. Results 1, 2, 3, 4 are not affected
  by fp16. Only Result 5's wording.
- Does not re-interpret Result 5's algebraic content. The
  algebraic orbit-avoids-0 fact is unchanged; what changes is
  how the paper describes the sim's empirical fidelity to it.

## Output

- `run_fp16_checks.py` — the runner
- `fp16_results/run1_fp16/{D1,N1,I1,I2,B-like}_fp16_results.npz`
- `fp16_results/run2_fp32_control/{D1,N1,I1,I2,B-like}_fp32_control_results.npz`
- `fp16_SUMMARY.md` — analysis with precision-ladder table

## Paper wording (anticipated)

If the precision ladder comes out clean:

> **Result 5.** The algebraic exceptional set under the walk's
> orbit action is {dyadic rationals}. Our symbolic sim respects
> this exceptional set up to floating-point catastrophic
> cancellation near ±1, at a rate ≤ r(p) per walker-step where
> p is the floating-point precision. Empirically r(fp64) <
> 3×10⁻¹¹, r(fp32) ≈ 1.5×10⁻⁹, r(fp16) ≈ 10⁻X. These are
> well-approximated by r(p) ~ 2^{-k(p)} with k the significand
> bit count, consistent with the catastrophic-cancellation
> mechanism. fp64 is therefore safely above the precision floor
> at our run volumes.

That sentence is cleaner than the previous "< 3×10⁻¹¹ at fp64 but
not zero." It says: "we understand the precision-scaling mechanism;
fp64 is below detection at our volumes; here are three data
points." Much more defensible.
