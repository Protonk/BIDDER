# BS12-FULLSTATE-SIM — WITHDRAWN 2026-04-19

**Status: withdrawn, never run.** Kept as a record of the
attempted design and why it doesn't work.

## Why withdrawn

The plan's central design choice — using uniform on `m × (E mod L)`
as the reference distribution — is not supported for BS(1,2).
Unlike ℤ² and H_3, BS(1,2) is non-compact; E diffuses to infinity
and the b-step couples m and E, so the joint projection onto
`(m, E mod L)` has no reason to converge to product-uniform. GPT5
verified empirically: at n = 2000 with the existing BS(1,2) kernel,
L₁(E mod 15, uniform) ≈ 0.30 and L₁(joint, product-uniform) ≈ 0.42,
with no sign of approaching the `k · θ_N ≈ 0.03–0.15` thresholds
this plan wanted to measure. The decision rule was asking for
data the sim cannot produce.

Additional issues that GPT5 flagged and that compound the above:

- **Sign is not negligible.** The plan omitted the sign coordinate
  on the grounds that "sign stays ≈ +1" for √2 IC. Empirically
  sign goes from +1 only 71% of walkers at n = 10 to ~52% by
  n = 2000. The "full-state" label with sign excluded is
  inaccurate.
- **Thresholds are unreachable.** Consequence of the reference
  problem above.
- **E_THRESH = 20 leakage.** At n = 2000 about 2.6% of walkers
  are in the frozen |E| > 20 regime, so the observable isn't
  purely measuring the underlying walk dynamics at that point.

The root issue (ad hoc reference with no stationary support) is
structural, not a detail that can be patched. Fixing the plan
properly would require either:

- building a natural finite quotient of BS(1,2) (matrix
  representation into an upper-triangular affine group over ℤ/p^k
  for some (p, k)), running the walk on that genuine finite group,
  and measuring L₁ to its uniform invariant. **Substantial
  additional machinery, ~days of setup, not a morning sim.**
- or abandoning "L₁ to uniform" entirely and using some other
  observable, which changes the question being asked.

## Decision

For the current paper-work scope, we're accepting that BS(1,2)'s
mantissa observable (r ≈ 1.15) and ℤ²/H_3's full-state observables
(r ≈ 2.0) are measured against **structurally different** reference
distributions, and that this difference is not decisively
resolvable without substantial additional work. The paper-level
takeaway remains what `h3_contrast_SUMMARY.md` concluded: the
sub-sampling slowdown depends on step-set and observable choice,
and is not a simple function of group structure.

Path B (the finite-quotient sim) is left as an open possibility
for future work if the question becomes paper-critical. It isn't
currently.

---

## [Original plan content preserved below for reference]

Sub-sampling slowdown on BS(1,2) measured with a **full-state**
observable (joint m × (E mod L) histogram) rather than the
mantissa-only projection. Tests whether the measured 1.15×
slowdown on BS(1,2) is specific to the mantissa projection, or
whether it survives on a state-space-level observable
comparable to what ℤ² and H_3 used in the previous contrast
runs.

## Why this plan exists

In the group-observable table (`h3_contrast_SUMMARY.md`):

| group / observable | r |
|:---|:---:|
| F_2 tree / drift | 0.5 |
| BS(1,2) / **mantissa L₁** | 1.15 |
| ℤ² torus / full-state L₁ | 2.0 |
| H_3(ℤ/15) / full-state L₁ | 2.0 |

BS(1,2)'s 1.15× is the odd one out. Two plausible explanations:

1. **Observable artifact.** BS(1,2)'s observable is a 1D
   projection (mantissa circle T = ℝ/ℤ) from a higher-dim
   state. Averaging over E and sign may be hiding a larger
   slowdown visible in the joint.
2. **Genuine group property.** BS(1,2) really does have a
   qualitatively different slowdown regime, maybe because of
   its solvable-but-non-nilpotent structure.

This plan runs BS(1,2) with a **full-state observable** (joint
m × E-mod-L histogram) and measures the slowdown ratio under
that observable. If it comes out at ~2×, explanation (1) wins
and we can retire "group-specific slowdown" language. If it
stays at ~1.15×, BS(1,2) is genuinely different and the paper
may want to explain why.

## Observable design

Walker state is (m, E, sign). The mantissa-only observable is

    L₁_m(P_n) = Σ_{bin j in m-axis} |freq_m_j − 1/B|

over B = 1000 bins. This marginalizes out (E, sign).

The **full-state observable** uses a joint histogram over
m × (E mod L) bins:

    L₁_{m,E}(P_n) = Σ_{(j, k)} |freq_{j,k} − 1/(B · L)|

with (j, k) ∈ {0, …, B−1} × {0, …, L−1}.

We ignore sign for cleanliness. For BS(1,2) starting from x =
+√2, sign stays ≈ +1 and rarely flips, so a sign coordinate
would mostly carry constant mass; adding it would dilute the
joint without adding information.

## Why E mod L (not a raw E cutoff)

Two reasons:

1. E diffuses to `|E| → ∞` under the walk; any fixed E cutoff
   `{|E| ≤ K}` loses walkers out the boundary. Modular
   wrap-around keeps all walkers in-range at all times.
2. `E mod L` equilibrates to uniform on ℤ/L under the walk as
   long as n is large enough that E's distribution spans many
   multiples of L (rule of thumb: n >> L²). This gives a
   well-defined uniform-reference distribution on the joint
   space.

L is a free parameter. Trade-offs:

- Small L (e.g., 7): E-mod-L equilibrates fast (n >> 49, easy
  at n_max = 1000). Fewer joint cells (B·L = 7000 at L = 7).
  Low noise floor at N = 10⁷. But less "resolution" in the E
  coordinate.
- Large L (e.g., 31): equilibrates slowly (n >> 961). More
  cells. Higher noise floor. But closer analog to the ℤ²
  torus's L = 31.

**Recommended: L = 15.** In the middle — L² = 225 is well below
n_max = 2000, so E-mod-L has plenty of time to equilibrate.
B · L = 15,000 cells. At N = 10⁷ the noise floor is
`√(2 · 15000 / (π · 10⁷))` ≈ 0.031, comparable to the ℤ² torus
floor at N = 10⁶ (0.025), giving ≥ 50× runway below the
initial `L₁ ≈ 2`.

## Run spec

### Walks

Both from IC `x = +√2` (m = log₁₀√2, E = 0, sign = +1).

- **Full:** step uniform on {a, a⁻¹, b, b⁻¹}.
- **Alternating:** odd step uniform on {a, a⁻¹}; even step
  uniform on {b, b⁻¹}. Stateless via step_index parity, same
  as step-buddies convention.

Step kernels are those in `run_m1_b1_b2.py` (via import, no
duplication), with the exact-zero restart convention preserved
(though it shouldn't fire on √2 IC).

### Parameters

    Observable: joint (m_bin, E mod 15) histogram
    B = 1000 mantissa bins, L = 15 exponent residues
        → 15,000 joint cells
    Walker counts: N ∈ {10⁶, 10⁷}
    One seed each (BS(1,2) sim has very low seed-to-seed
        spread at these N; no need for replicates)
    n_max = 2000
    Sampling: every 10 steps, so 200 samples per run

### Seeds

    SEED_BASE = 0xB51250AE  # distinct from step-buddies
    walk_idx = {'bs12_full': 0, 'bs12_alt': 1}
    log_N = int(round(math.log10(N)))
    seed = SEED_BASE + walk_idx * 10**6 + log_N * 10**4

### Cost estimate

- Per walker-step: unchanged from existing BS(1,2) runs (step
  kernel is the same; observable cost at sample times is the
  only added work). Joint histogram via np.bincount on
  flattened index = B·E_mod index. Cheap.
- N = 10⁷ × n = 2000 = 2×10¹⁰ walker-steps. Existing BS(1,2)
  throughput at N = 10⁸ is ~4.75×10⁶ ws/s; at N = 10⁷, similar
  or slightly higher per-walker. Estimate 5-10 min per run.
- Two runs at N = 10⁷ + two at N = 10⁶ = 4 runs. **Total ≈ 20
  min.**

## Analysis

Following the step-buddies / H_3-contrast pattern:

1. Compute `n(θ_k)` for both walks at thresholds `θ_k = k ·
   θ_N(N)` with `k ∈ {5, 3, 2, 1.2}` and
   `θ_N(N) = √(2 · B · L / (π · N))`.
2. Tabulate `r(N, k) = n_alt(θ_k) / n_full(θ_k)`.
3. Check:
   - **Q1 (k-trend):** is r flat across k, or does it vary?
   - **Q2 (N-stability):** at fixed k, how does r vary between
     N = 10⁶ and N = 10⁷?
4. Compare the measured r to the existing mantissa-only r
   ≈ 1.15 and to ℤ²/H_3's r ≈ 2.0.

## Decision rule

**Primary check:** does `r(N = 10⁷, k = 1.2)` (the deepest
measurement) sit closer to 1.15 or 2.0?

- r ∈ [1.0, 1.3] across all (N, k) on the full-state
  observable: **the mantissa projection was not hiding the
  slowdown.** BS(1,2) is genuinely different from ℤ²/H_3.
  Paper can keep whatever story it has about BS(1,2) being
  a special regime.
- r ∈ [1.8, 2.2] across all (N, k): **the 1.15× was an
  artifact of the mantissa projection.** On the "natural"
  full-state observable BS(1,2) behaves like ℤ²/H_3. Paper
  should retire group-specific slowdown language and frame
  the 2× as a step-set + full-state-observable property.
- r intermediate (say r ∈ [1.3, 1.8]): partial story. Both
  the group structure and the observable matter.

**Secondary check:** agreement between mantissa-only and
full-state observables in the N-stability behavior. If
full-state Q2 is also stable across N (max/min ≤ 1.5), then
the measurement is clean regardless of which outcome it
gives.

## Caveats and known limitations

1. **E-mod-L is not a natural BS(1,2) observable.** The walk
   doesn't have a natural invariant distribution on ℤ/L for
   the E coordinate. "Uniform on B·L cells" is a reference
   we construct to measure ensemble spread, not a stationary
   distribution the walk converges to in any group-theoretic
   sense. We measure deviation from this reference; the walk
   DOES converge to it asymptotically (because E diffusion
   equilibrates E-mod-L), but the convergence isn't special.
2. **L choice is arbitrary.** L = 15 is a chosen trade-off.
   If r differs dramatically between L = 7 and L = 31, the
   observable is poorly chosen. A sensitivity check at L ∈
   {7, 15, 31} would catch this. Deferred unless L = 15
   produces an ambiguous result.
3. **E mixing timescale vs m mixing timescale.** The m
   coordinate mixes to uniform on T in the stretched-exp
   regime measured by M1 (floor by n ≈ 200–400 on the √2
   IC). E-mod-15 mixes through diffusion, with characteristic
   scale n ~ L² = 225. These timescales overlap, but at
   short n the L₁ could be dominated by either. We should
   not over-interpret early-n behavior; look at late-n (k =
   1.2) for the asymptotic slowdown.
4. **No sign coordinate.** BS(1,2) from √2 IC has sign mostly
   +1; if alternating has a different sign-distribution from
   full walk at matched n, ignoring sign might hide a
   component of the slowdown. Checkable by adding a sign
   coordinate (B·L·2 = 30,000 cells at L = 15), at modest
   extra cost. Deferred unless the primary measurement is
   inconclusive.
5. **The "artifact of projection" framing may be
   oversimplified.** Even if full-state r ≈ 2.0, it's not
   a fully clean comparison to ℤ²/H_3 because BS(1,2)'s
   state space and dynamics are genuinely different. The
   best we can honestly say is "same order of magnitude"
   slowdown, not "identical mechanism."

## Output files

- `run_bs12_fullstate.py` — runner.
- `analyze_bs12_fullstate.py` — analysis (r table and checks).
- `bs12_fullstate_results/{full,alt}_N1e{6,7}.npz` — 4 npz
  files with (sample_times, l1, meta).
- `bs12_fullstate_SUMMARY.md` — write-up once results are in.

## What this plan does NOT do

- Does not propose a new natural finite quotient of BS(1,2).
  E-mod-L is an operational choice, not a principled
  quotient. A principled finite-quotient sim would require
  specifying a normal subgroup of BS(1,2) and working out
  the quotient's walk dynamics. Out of scope.
- Does not scan L values. L = 15 is the target; a sensitivity
  scan at L ∈ {7, 31} is listed as a follow-up only if the
  primary result is ambiguous.
- Does not include sign. Noted as a possible follow-up.
- Does not re-run mantissa-only; we already have M1 data at
  N = 10⁸ and step-buddies data at various N. Mantissa r ≈
  1.15 is taken as the reference number.
- Does not produce a figure. If the result is clean, a single
  entry in the group-observable table suffices; no need for a
  new figure.

## Paper-level implication

The outcome directly affects whether the paper should claim
BS(1,2) has a "special slowdown regime" distinct from
torus-like groups. Outcomes:

- **Full-state r ≈ 2.0:** paper says "the mantissa-projection
  observable hides part of the alternation penalty; on a
  full-state observable, BS(1,2) behaves like ℤ² and H_3 —
  ~2× slowdown." Cleaner story: slowdown is step-set and
  observable, not group-specific.
- **Full-state r ≈ 1.15:** paper keeps BS(1,2)-specific
  language. "On both observables BS(1,2)'s slowdown is
  markedly less than the torus groups'; this is a genuine
  property of the walk."
- **Intermediate:** "The slowdown depends on observable;
  BS(1,2)'s mantissa observable gives 1.15×, its full-state
  observable gives X, both smaller than ℤ²/H_3's 2×."

Any of these is a clean paper-compatible statement. Running
this plan removes the ambiguity.
