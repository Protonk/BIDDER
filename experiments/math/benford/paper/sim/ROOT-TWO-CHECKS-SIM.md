# ROOT-TWO-CHECKS-SIM

## Why this plan exists

T1b (the surviving theorem after M3 + M4) wants an IC-universality
clause for α = 1/2. The existing draft says "for every ν with a
logarithmic moment," but that overreaches: rational ICs can reach
x = 0 in finite time (from x₀ = 1, a single b⁻¹ step lands at 0),
where the mantissa projection m = log₁₀|x| is singular.

The current `run_m1_b1_b2.py` kernel does **not** regularize that
exact-zero event. Its only snap branch is the approximate near-zero
shortcut for `E < -20`, which sends `x ≈ 0 ± 1` to `±1` according to
the step direction. Exact `x_new = 0` in the active branch would
currently hit `log10(0)` and produce invalid state. So any rational-IC
follow-on requires an explicit exact-zero branch; it cannot literally
reuse the √2 runner unchanged.

So the √2 IC is not a cosmetic choice. It's the canonical
**regularization-free** IC: its orbit stays in
`{2^k · √2 + q : k ∈ Z, q ∈ Z[1/2]}`, which never contains 0 because
`√2 ∉ Q`. So the walk's dynamics are well-defined along every
trajectory without any convention.

This plan tests the empirical equivalence classes:

1. **Generic-irrational check.** A second irrational IC should not
   force a different asymptotic exponent just because √2 has a special
   sharp transient. Test: run φ = (1+√5)/2.
2. **Rational IC with explicit exact-zero restart.** Starting from
   `x = 1`, insert a dedicated `x_new = 0` branch that immediately
   restarts the walker at `±1` according to the step direction. Test
   whether this restart convention changes late-time L₁ materially.
3. **Rational IC with absorbing zero.** Starting from `x = 1`, treat
   exact zero as absorption and compute L₁ on surviving walkers only.
   This isolates the rational-start pathology from any restart rule.

If all three hold, T1b's revised IC clause is at least empirically
supported:

> For every ν with a logarithmic moment and ν(Q) = 0, L₁(P_n)
> ∼ B(ν) · n^{−1/2} with α = 1/2 universal, B IC-dependent.

The rational case would still need separate wording. These runs can
only tell us whether the rational pathology looks like a removable
artifact, a distinct conditional process, or a genuine exception.

## Coordination note

This is a **post-M4 follow-on**, not part of the default schedule in
`ALGEBRAIC-SIM-MESS-PLAN.md`. Runs are cheap (N = 10⁷, n = 600 each,
est. ~8 min per IC on this machine). All three below can run
sequentially in well under an hour.

R1 can reuse the same kernel as `run_m1_b1_b2.py` and `run_m3.py`
with only the initial condition changed. R2 and R3 need a dedicated
rational-IC runner that adds an explicit `x_new = 0` branch before
`log10`, with restart or absorb policy selected by flag. Output is
single-IC L₁(n) and ensemble Fourier, plus per-walker zero-hit
statistics for R2 and a survival trajectory for R3.

## Run specification

### R1: IC = φ (golden ratio)

**Purpose:** second generic-irrational check. φ is algebraic of
degree 2 over Q, like √2, but with a different minimal polynomial
`x² − x − 1`. Its orbit stays in `{2^k · φ + q : k ∈ Z, q ∈ Z[1/2]}`
and therefore also avoids 0.

    N = 10⁷ walkers
    Symmetric measure
    Initial condition: x = +φ
        (m = log₁₀ φ ≈ 0.2090, E = 0, sign = +1)
    Time range: n = 0 to 600
    Sampling: M1 grid (every step [1, 200], every 5 [205, 600])
    Output: L₁(n), ensemble ĥ(r, n) for r = 1..5

**Decision rule.** Fit α̂ on the latest contiguous sample window that
still sits comfortably above the `N = 10⁷` floor (`θ_N ≈ 8.6×10⁻³`).
If `[100, 600]` is usable, prefer it; otherwise use the longest
floor-clear late window available. Compare primarily to M3 IC (b)'s
`α̂ ≈ 0.525`; use √2 only as a transient reference:

- α̂ on R1 matches IC (b) (i.e. α̂ ∈ [0.45, 0.55]) ⇒ irrational-
  class support for a universal exponent. The coefficient B may differ.
- R1's late-window fit still prefers the same √2-style transient
  `A·exp(−c√n)` with `c ≈ 0.5` ⇒ R1 is in the same "sharp-IC transient"
  regime as √2; the asymptotic algebraic tail is not yet visible on the
  sampled horizon. Run R1 at longer n to distinguish.
- α̂ outside both patterns ⇒ non-universal; investigate before
  restating T1b.

### R2: IC = 1, exact-zero restart on

**Purpose:** test whether a concrete exact-zero restart rule changes
the late-time asymptotic materially.

    N = 10⁷ walkers
    Initial condition: x = +1 (m = 0, E = 0, sign = +1)
    Time range: n = 0 to 600
    Sampling: M1 grid
    Exact-zero branch: if an active b/b⁻¹ step produces x_new = 0,
        immediately restart at (m=0, E=0, sign=sign(delta)),
        matching the existing E < −20 near-zero shortcut
    Output: L₁(n), ensemble ĥ(r, n), plus:
        - total_zero_hits: cumulative count of exact-zero events
        - zero_hits_per_step(600,): exact-zero events per sim step
        - first_zero_hit_hist: distribution of first-hit time
          across walkers

**Expected zero-hit rate.** Walker at x = 1 takes b⁻¹ with probability
1/4, landing at x = 0. So the first-step zero-hit probability is 1/4.
Under the restart rule above, that walker is re-emitted at x = −1; from
x = ±1 the opposite b/b⁻¹ move again hits 0 with probability 1/4.
Away from the ±1 states the zero-hit rate should drop quickly.

**Decision rule.** Measure L₁(n) at n = 200, 400, 600. Compare to
M1 (√2) at the same n:

- L₁(R2, n) ≈ L₁(√2, n) within N=10⁷ noise across all three
  times ⇒ this particular restart rule looks empirically benign on
  the sampled horizon.
- L₁(R2, n) differs systematically from √2 at late n ⇒ the restart rule
  is **not** benign; it changes the dynamics
  in a way the theorem must not hide. In this case R3 becomes the
  decisive test.

### R3: IC = 1, absorbing boundary at x = 0

**Purpose:** measure the walk minus the artifact. Walkers that hit
x = 0 are **removed** from the ensemble instead of restarted.

    N = 10⁷ walkers (initial)
    Initial condition: x = +1
    Time range: n = 0 to 600
    Sampling: M1 grid
    Exact-zero branch: walkers entering x = 0 on an active b-step are
        marked absorbed and excluded from L₁ and Fourier computations
        from that step onward.
    Output: L₁(n) computed on surviving walkers only,
        N_survivors(n), ensemble ĥ(r, n) on survivors.

**Expected survival.** First-step survival is exactly 3/4. Beyond that
I do not want to hard-code a plateau guess; the point of R3 is to
measure the survival trajectory rather than smuggle one in.

**Decision rule.** Compare conditional L₁ on survivors to √2 and
to R2:

- Conditional L₁(R3, n) matches L₁(√2, n) at late n ⇒ the restart
  convention is not needed to recover the generic-irrational behavior.
  This supports stating T1b for `ν(Q) = 0` and, if desired, discussing
  rational starts separately via a conditional-on-survival process.
- Conditional L₁(R3, n) matches R2's L₁ at late n but not √2 ⇒
  the walk-minus-artifact itself differs from the generic-IC
  walk. This would be unexpected and worth investigating; it
  would argue for stating T1b strictly in the generic-ν case and
  treating rational ICs as genuinely distinct.

## Analysis

### A1. α̂ on R1

Same fit as M3: `log L₁(n) = a − α · log n` on a window clear of the
floor. No hard precision promise here; report the fit window and R²
honestly rather than pretending `N = 10⁷` makes uncertainty vanish.

### A2. L₁(R2, n) / L₁(√2, n) ratio at n = 200, 400, 600

If the restart rule is benign, this ratio should be ≈ 1 at all three times
once past the burn-in (say n > 50). Departures at late n flag
non-trivial restart contribution.

### A3. N_survivors(R3, 600) and conditional L₁

Report the survival fraction at the horizon, and the conditional
L₁ on survivors. If survival is < 1% by n = 600, the conditional-
L₁ statistics will be noisy — extend N to 10⁸ for that specific
run.

## Decision matrix for T1b's IC clause

| R1 α̂ vs IC(b) | R2 late L₁ vs √2 | R3 cond. L₁ vs √2 | Paper wording supported by data |
|:-------------------|:------------------|:-------------------|:------------|
| matches            | matches           | matches            | generic-irrational clause looks good; this restart rule also looks benign |
| matches            | matches           | doesn't match      | do not generalize rational starts; restart rule may be masking distinct rational behavior |
| matches            | doesn't match     | matches            | "for generic ν (`ν(Q) = 0`)" remains the clean statement; restart rule is an artifact |
| doesn't match      | —                 | —                  | no generic-irrational universality claim; stop and rethink |

The central case — "matches, doesn't match, matches" — is still the
cleanest outcome and is what this plan expects.

## Scope / cost

All three runs: N = 10⁷, n_max = 600. Approx wall time per run on
this machine, based on M3's benchmark (~8.5 min per 10⁷ × 600):
- R1: ~8 min
- R2: ~8 min + minimal overhead for zero-hit tracking
- R3: ~8 min + minimal overhead for survival tracking

Total: ~25–30 min sequential. Runs are independent; any can be
skipped without blocking the others.

## Output files

- `r1_phi_results.npz` — R1 data (L₁, h_full, sample_times, seed, metadata)
- `r2_rational_restart_results.npz` — R2 data plus zero-hit statistics
- `r3_rational_absorb_results.npz` — R3 data plus survival trajectory

## What this plan does NOT do

- Does not extend M4-style long-horizon for R1, R2, R3. The purpose
  is equivalence-class verification, not precise B estimation.
- Does not test transcendental ICs (π, e) separately. A successful φ
  run would show that √2 is not a one-off; it would not by itself prove
  "all irrationals behave the same." A reviewer-driven π/e spot-check
  would still be easy if needed.
- Does not test extremely small-magnitude ICs (e.g. `10^{-30}`). Those
  start immediately in the `E < −20` approximate near-zero regime and
  therefore probe a different regularization question.
