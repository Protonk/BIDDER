# Conditional decay sim — plan (v3)

Tests whether the **sharp-IC stretched-exp transient** observed
in BS(1,2) (c ≈ 0.498 on M1's irrational sharp IC per
`T1B-EVIDENCE-MAP.md:157`, `m1_b1_b2_SUMMARY.md:39`) is driven
by the a-step random rotation on T alone, with b-steps passive
at the Fourier-mode level.

## Scope discipline (up front)

- **T1b is the paper's theorem shape:** asymptotic α = 1/2
  (algebraic 1/√n), with IC-specific stretched-exp transient for
  sharp ICs (`sim/README.md`, `sim/T1B-EVIDENCE-MAP.md`).
- This plan addresses only the **transient**. It does not
  attempt to explain, predict, or constrain the asymptotic 1/√n.
- `MESSES.md` Mess #1's Laplace obstruction is a statement about
  the asymptotic. **This sim does not close Mess #1 and does not
  attempt to.** It can at most relocate where the transient
  stretched-exp comes from.
- Not load-bearing for the paper.

## The observable: Fourier modes

Earlier drafts tried to compare 1000-bin L₁ (or TV, or L²) across
differently-ICed walks. Those observables mix support-fill-in
effects with true mixing; worse, they do not have clean
closed-form predictions on sharp-IC pure-a walks. GPT5 flagged
this twice.

Switch to Fourier modes as the single common observable. For any
walker distribution at step n:

    c_k(n) := E[ e^{−2πi k m_n} ],   k ∈ ℤ

- Complex scalar per (k, n).
- Well-defined for any IC, sharp or smooth.
- Has exact closed-form under the hypothesis.
- Empirically measurable in sim as mean of e^{−2πi k m_n} over
  walkers, with noise O(1/√N).

Comparing c_k(n) across walks uses a single IC-independent
object. TV/L² can be reconstructed from truncated {c_k} by
Parseval or inverse FFT if needed — but the mode-level
comparison is the primary test.

## The hypothesis under this observable

Let α = log₁₀ 2.

**Pure a-walk on T.** Starting from sharp IC m₀, after K
deterministic a/a⁻¹ steps (each ±α with prob 1/2):

    c_k^a(K) = e^{−2πi k m₀} · cos(2π k α)^K.

Exact, closed form.

**BS(1,2) under the hypothesis "b-step does not move m
conditional on K" (H).** Starting from sharp IC m₀, after n
calendar steps with K ∼ Binomial(n, 1/2) a-steps:

    c_k^H(n) = E_K [ c_k^a(K) ]
             = e^{−2πi k m₀} · E_K [ cos(2π k α)^K ]
             = e^{−2πi k m₀} · ((1 + cos(2π k α)) / 2)^n.

Also exact and closed form, using
E[s^K] = ((1 + s)/2)^n for K ∼ Binomial(n, 1/2).

**Decay rate per mode k under H:**

    |c_k^H(n)| = ((1 + cos(2π k α)) / 2)^n = cos²(π k α)^n

    r_k := −log((1 + cos(2π k α))/2) = −2 log |cos(π k α)|.

Slowest mode is the k for which kα is closest to an integer — a
Diophantine statement about α. For α = log₁₀ 2: k = 10 gives
10α = 3.0103 (very close to 3), and r_{10} ≈ 0.00111; k = 93
gives 93α ≈ 27.996, r_{93} ≈ 0.00016; higher convergents give
slower modes.

## What this hypothesis does not predict

- **It does not give stretched-exp naturally.** Under H, the
  dominant mode at calendar step n is k* = argmin r_k subject to
  being reachable at scale n; this produces a complicated
  mode-selection curve, not a clean exp(−c√n). Stretched-exp can
  arise from a specific balance in the Fourier sum, but the
  analytic form under H is not inherently stretched-exp.
- **It does not explain the theorem-scale 1/√n.** That's T1b's
  asymptotic, outside this plan's scope.

Part of what this sim does: check whether the transient fit
shape matches H's analytic prediction, not whether H predicts
the specific fit of stretched-exp.

## Three tests (revised, mode-level)

### Test A: Analytic c_k^H(n) under hypothesis H

No sim. For α = log₁₀ 2, compute c_k^H(n) for k ∈ {1, 2, …, 500}
and n ∈ {10, 30, 100, 300, 1000, 3000, 10000} from the formula
above.

**Output A1:** table of |c_k^H(n)| for the slowest 20 modes.
Verify the mode hierarchy (k=10, k=93, k=196, ...) scales as
expected.

**Output A2:** reconstruct (approximate) density:
    ρ^H(n, m) = 1 + Σ_{|k|>0, |k|≤K_max} c_k^H(n) e^{2πi k m}
truncated at K_max = 500. Integrate |ρ^H − 1| over m on a fine
grid to get an approximate TV^H(n). Fit shape to C · exp(−c ·
n^γ) for n ∈ [30, 3000].

**Output A3:** same with L² norm, computed exactly via
Parseval: ‖ρ^H − 1‖_2² = Σ_{k ≠ 0} |c_k^H(n)|². Fit shape.

**Caveat:** TV and L² can have different decay shapes. Report
both. The paper's φ is TV; use TV^H as the primary comparison
target.

**Decision after A:** if TV^H(n) has a clean fit shape on
n ∈ [30, 3000], that is the shape predicted by the hypothesis
_for this observable on this IC_. Whatever it turns out to be
(stretched-exp, straight-exp, algebraic, mixture) is the shape
Test B/C should match if H is correct.

### Test B: per-K empirical Fourier modes on BS(1,2)

**Kernel:** paper's default step_b with the |E| < −20 snap
(match comparison_walks). Sharp IC m₀ = log₁₀ √2 to match M1.

**Instrumentation:** add a per-walker integer counter K that
increments on each a/a⁻¹ step, doesn't change on b/b⁻¹. Run
N = 10⁷ walkers up to n = 3000.

**Snapshots:** at n ∈ {100, 300, 1000, 3000}, save for each
walker the (m_n, K_n) pair. Storage: 10⁷ × 2 × 4 bytes × 4
snapshots = 320 MB. OK.

**Aggregation rule (consistent with Test C below):** use **unit
K-bins**, with no binning beyond "integer K value." For each
(n, K) pair, compute empirical Fourier coefficients:

    ĉ_k(n, K) = (1/N_{n,K}) · Σ_{walkers in bin (n, K)}
                 e^{−2πi k m_n}

for k ∈ {1, 2, 5, 10, 20, 50, 93} (slow modes of interest).

**Output B1:** table of ĉ_k(n, K) / c_k^a(K) for each (k, n, K)
with N_{n,K} ≥ 1000. Ratio should be 1 if H holds exactly, at
any (n, K). Deviations from 1 quantify b-step contribution at
the mode level.

**Output B2:** ĉ_k(n, K) plotted vs K for each k, at each n.
Under H, this should collapse to the pure-a curve cos(2πkα)^K
for that k, independent of n.

### Test C: aggregated Fourier modes, mix first then evaluate

Addressing GPT5 objection 2: don't average TVs; mix densities.
At the Fourier level this means: aggregate Fourier coefficients
with Binomial weights, then compute norms.

**Aggregation:**

    ĉ_k^{agg}(n) = Σ_K P(K = K_val | Binomial(n, 1/2)) · ĉ_k(n, K_val)

where P is the exact Binomial density on K ∈ {0, 1, …, n}. Since
we store per-unit-K data in Test B, this sum is exact (no
binning error).

**Comparison:**

(1) Compare ĉ_k^{agg}(n) to the _predicted_ c_k^H(n) from Test
    A. Gap measures b-step's aggregated contribution to mode k.

(2) Compare ĉ_k^{agg}(n) to the _measured unconditional_
    ĉ_k^{BS}(n) = (1/N) Σ_walkers e^{−2πi k m_n}. These should
    agree by construction — this is a sanity check on the
    aggregation.

**Output C1:** |ĉ_k^{agg}(n) − c_k^H(n)| / |c_k^H(n)| per
(k, n). If ≤ 10% for all slow modes, H is strongly supported at
the mode level.

**Output C2:** TV reconstructed from {ĉ_k^{agg}}_k via inverse
FFT, compared to paper's measured φ_BS(n). If H predicts the
paper's φ_BS shape within a factor of 2 over n ∈ [30, 3000],
the transient mechanism is located.

## Decision rules

After Test A alone:
- If TV^H(n) fits stretched-exp with c ≈ 0.498 on the M1
  irrational-sharp IC: H is a priori plausible. Proceed to Tests
  B, C.
- If TV^H(n) is stretched-exp but with very different c
  (say > 2× gap): H has qualitative shape right but
  quantitatively off; proceed with caveats.
- If TV^H(n) is not stretched-exp at all (e.g., exponential or
  algebraic): H's hypothesis is incompatible with the measured
  transient. Abort B and C; the transient is not from the
  a-step-alone mechanism, full stop.

After Tests B, C:
- ĉ_k^{agg}(n) matches c_k^H(n) per mode within 10%: H confirmed
  at the mode level. b-step does not move Fourier content.
- Agreement within factor 2 but not 10%: H partially correct,
  b-step adds a measurable but small correction. Further work
  could identify where.
- Large divergence: H rejected. The b-step contribution is not
  small at the mode level, and the transient mechanism is more
  complicated than just Binomial-weighted a-step rotation.

## What this would inform

**If H confirmed:** the sharp-IC transient has a clean analytic
explanation that doesn't involve the per-return contraction
framework. `MESSES.md` Mess #1's framing — per-return Laplace
delivers the rate — targets the asymptotic, not this transient;
the two mechanisms live at different scales. This clarifies what
Mess #1 is actually about but does not close it.

**If H rejected:** the transient has some other source. Not a
paper-load-bearing finding either way under T1b.

## What this does not do

- Does not close `MESSES.md` §1, §2, or §3.
- Does not predict or constrain the asymptotic 1/√n.
- Does not speak to the Benford-identification gap (§2).
- Does not tighten operator legitimacy (§3).

## Cost estimate

- Test A: seconds (analytic, numerical over ~500 modes × 10
  sample n's).
- Test B: ~60 min at N = 10⁷, n = 3000 (kernel is paper's
  default, which has some overhead from the snap logic).
- Test C: seconds (arithmetic on Test B outputs and Test A
  outputs).

Total: ~1 hour compute + ~2 hours writeup.

## What's saved

- `conditional_decay_results/analytic_H.npz` — c_k^H(n) grid,
  TV^H(n), L²^H(n).
- `conditional_decay_results/bs12_mk_snapshots.npz` — (m, K)
  pairs per walker at each snapshot n.
- `conditional_decay_results/aggregated_modes.npz` — ĉ_k^{agg}(n)
  and comparison metrics.

## Priority ranking

**Medium** if the paper or its supporting documentation wants a
mechanism-level explanation of the stretched-exp transient
beyond "it is an IC-specific transient that eventually rolls
off." **Low** if the T1b phenomenology is sufficient.

## Changes from v2 (addressing GPT5 round 2)

1. **Observable now Fourier modes throughout.** Test A and Test
   B use the same observable on the same IC. No smooth-vs-sharp
   mismatch.
2. **Fourier formulas are now exact.** Test A computes
   |c_k^H(n)| exactly; TV^H comes from inverse-FFT to density,
   L²^H comes from Parseval. Σ |f̂_k| · |cos|^n is no longer
   used as if it were an exact norm.
3. **No unsupported claim about T1b crossover.** Test A no
   longer claims it "shows" the algebraic asymptotic. The
   plan is explicit that the analytic model under H does not
   predict the T1b asymptotic and is not designed to.
4. **K-binning is consistent.** Unit-K storage from sim
   (per-walker K values), exact Binomial aggregation in
   Test C, no bin/strata switchover.
5. **c value updated.** 0.498 from M1's current sharp-IC fit,
   not 0.55.

## Open design questions

- **IC choice in A/B/C.** m₀ = log₁₀ √2 (M1's canonical IC)
  throughout, matching existing φ_BS data for Test C's TV
  comparison.
- **K_max for Fourier truncation.** 500 is generous for smooth
  reconstructions; reducing to 200 would still capture modes
  k=10, 93, 196 with their harmonics.
- **N for Test B.** 10⁷ gives per-K bin populations of
  ≥ 10⁴ in the Binomial bulk (|K − n/2| ≤ 2σ_K), enough for
  ĉ_k(n, K) with O(1%) noise. Scaling up would tighten the
  per-mode comparisons but isn't necessary for the decision
  gates as stated.
