# BENTHIC-MINKOWSKI-SIM

## Why this plan exists

Two purposes, independent of each other:

**(1) Mechanism identification for the paper.** Decides whether an
observed `exp(−c√n)` shape is a genuine asymptotic rate (balanced
regime) or a transient before true exponential (rotation-dominated)
or before algebraic (injection-dominated). The other two sim plans
can't tell these apart; they only see the shape, not the mechanism.

**(2) Proof triage for FIRST-PROOF gap 2.** BENTHIC's B3 measures
`ρ(M)`, the spectral radius of the mode-coupling matrix for `T_R`,
empirically. This is exactly the object FIRST-PROOF gap 2 (R4)
wants to prove has value less than 1. If B3 returns `ρ(M) ≈ 1`,
(R4) is unprovable — the thing the proof would establish isn't
true. If B3 returns `ρ(M) < 1` with tight CI, (R4) has a numerical
target and empirical plausibility. Running B3 **before** committing
substantial analytical effort to gap 2 is proof triage, not just
paper support. See FIRST-PROOF §2 (R4) for the cross-reference.

Purpose (2) is why B3 is default always-on — the 4 hours it costs
buys information that could save weeks of analytical work, even in
cases where purpose (1) could be skipped on grounds of
TUKEYS+ALGEBRAIC concurrence.

## Coordination note

**Run specs and default execution schedule are authoritative in
`ALGEBRAIC-SIM-MESS-PLAN.md`.** See also
[sim/README.md](README.md) for the cross-document framing
(scientific discrimination + proof triage, the three-plan
triangle, and structured disagreement as deliverable). This
document specifies only BENTHIC-specific additions (B1's extended
output that folds into M1, and B3 as a separate ~4-hour run).
B1 + B2 are always-on by default (they're part of M1). B3 is
always-on by default too.

**Shared prerequisite: S0 (Mittag-Leffler index test).** BENTHIC's
balanced-regime prediction (that the effective rate is
stretched-exp with √n scaling) assumes N_n ~ ML(1/2). If S0's
measured β̂ is outside [0.45, 0.55], the balanced-regime rate
becomes exp(−c · n^{1 − β̂}), not exp(−c√n), and A3's regime-
determination comparisons (ρ(M) vs. γ₁^{c'}) must be reformulated
at the measured index. See `ALGEBRAIC-SIM-MESS-PLAN.md` Run S0
for the test spec and decision rule.

---

## Notation note (coordination with sibling plans)

This plan works primarily in L² and in the Fourier domain on
T = ℝ/ℤ. Three quantities appear and are not interchangeable:

- **h(m) := ρ(m) − 1**, the ensemble mantissa-density deviation
  from uniform. Function-valued.
- **‖h‖_{L²} = (Σ_{r≠0} |ĥ(r)|²)^{1/2}**, the L² norm of h,
  equivalently the Parseval sum over nonzero Fourier modes.
  This plan's primary diagnostic.
- **L₁(n) = ∫ |h(m)| dm** (up to the bin-count discretization
  the sim uses; equivalently (1/B)Σ|freq_j/N − 1/B|). This is
  the sibling plans' target statistic.

‖h‖_{L²} and L₁ are different norms of the same h. They satisfy
L₁ ≤ ‖h‖_{L²} (Cauchy-Schwarz) but their rates of decay can
differ. This plan's conclusions about ‖h‖_{L²} translate to
sibling-plan L₁ conclusions via that inequality; equality holds
roughly when h concentrates in a bounded number of Fourier modes.

---

## The problem in one paragraph

The symmetric BS(1,2) walk on T × ℤ has two mixing mechanisms
acting on the mantissa marginal simultaneously: rotation by
±log₁₀ 2 during excursions away from the low-depth zone
R = {|E| ≤ E₀}, and ε-perturbation during visits to R. Rotation
destroys non-uniformity at an exponential per-step rate.
ε-perturbation contracts non-uniformity per visit, but it also
*injects* new non-uniformity — the b-step map at E = 0 is a
genuine nonlinear deformation that creates Fourier content.
The measured ensemble TV decays as exp(−c√n), which is
intermediate between exponential (pure rotation prediction)
and algebraic (pure spectral-gap-on-returns prediction). The
hypothesis is that the exp(−c√n) rate arises from the
creation-destruction balance: exponential destruction between
visits, partially offset by creation at each visit, with √n
visits by time n.

---

## Minkowski decomposition

### Setup

Let p_k = P(N_n = k) be the probability of exactly k returns
to R by time n. Let ρ_k be the conditional mantissa density
given N_n = k. The ensemble deviation from uniform is

    h(m) = Σ_k p_k (ρ_k(m) − 1).

We want ‖h‖ in some norm. Work in L²(T) and pass to Fourier.

### Fourier decomposition

Write ĥ(r) = Σ_k p_k ĉ_r^{(k)} for each Fourier mode r ≠ 0,
where ĉ_r^{(k)} = ∫ ρ_k(m) e^{−2πirm} dm is the r-th Fourier
coefficient of the conditional density for return count k.
Parseval gives

    ‖h‖²_{L²} = Σ_{r≠0} |ĥ(r)|² = Σ_{r≠0} |Σ_k p_k ĉ_r^{(k)}|².

Minkowski in ℓ² over modes, applied to the k-sum:

    ‖h‖_{L²} ≤ Σ_k p_k (Σ_{r≠0} |ĉ_r^{(k)}|²)^{1/2}
             = Σ_k p_k ‖ρ_k − 1‖_{L²}.

This is the L² triangle inequality: norm of the mixture ≤
mixture of the norms. It discards inter-component phase
information.

### Where the phases live

Fix mode r. The coefficient ĉ_r^{(k)} for a walker with k
returns is the product of two factors:

1. A contraction factor from k visits to R: each visit
   multiplies |ĉ_r| by some factor ≤ q_r < 1 (the spectral
   gap of T_R acting on mode r). But each visit also
   *rotates* the phase of ĉ_r by a random amount determined
   by the ε-deformation, and can inject amplitude into mode r
   from other modes via the nonlinearity of the b-step.

2. A rotation factor from excursion time: during n − O(k)
   steps outside R, each step acts on ĉ_r as follows. With
   probability 1/4 each the step is a or a⁻¹, multiplying
   ĉ_r by e^{∓2πir log₁₀ 2}; with probability 1/2 the step is
   b or b⁻¹, which outside R is near-identity on the mantissa.
   The expected per-step multiplier on ĉ_r outside R is

       γ_r = (1/2) · (1 + cos(2πr log₁₀ 2)).

   For r = 1: γ₁ = (1/2)(1 + cos(2π · 0.30103)) ≈
   (1/2)(1 − 0.315) ≈ 0.342. For r = 2: γ₂ ≈ 0.10 (fastest
   rotation-based destruction). For r = 3: γ₃ ≈ 0.91 (slowest,
   near-resonance with log₁₀ 2). This is exponential destruction
   in the excursion time, mode-dependent.

The Minkowski bound uses |ĉ_r^{(k)}| ≤ q_r^k · γ_r^{n−O(k)}
for each component separately, then sums over k. Since
γ_r^{n−O(k)} is exponentially small in n for each k, the
Minkowski bound gives exponential decay of ‖h‖_{L²} — faster
than what the simulation shows. Something is wrong with the
bound.

### Why Minkowski is too optimistic

The bound |ĉ_r^{(k)}| ≤ q_r^k · γ_r^{n−O(k)} treats the
spectral-gap contraction factor q_r and the rotation factor
γ_r as independent multiplicative losses. But the b-step at
low E does not merely contract mode r — it is a nonlinear map
that couples modes. A b-step at E = 0 sends

    m ↦ frac(log₁₀(10^m + 1))

which is smooth but far from linear. In Fourier space, this map
scatters energy from mode r into modes r ± 1, r ± 2, etc. Some
of the energy that rotation destroyed in mode r gets recreated
by the b-step's nonlinear mixing from neighboring modes.

The per-visit "contraction" q_r is the net effect: true
contraction of mode r (ε pushes mantissa toward uniform) minus
injection into mode r (nonlinear coupling from other modes).
If q_r is close to 1, the injection nearly cancels the
contraction, and the net effect per visit is small. Between
visits, rotation destroys the injected energy exponentially.
But the next visit re-injects.

The creation-destruction balance is:

- Between visits: mode r decays as γ_r^{τ} per excursion
  of length τ.
- At each visit: mode r receives an injection of amplitude
  proportional to the energy in neighboring modes, offset
  by contraction of its own amplitude.

Minkowski ignores the injection because it bounds each
|ĉ_r^{(k)}| individually, treating the k-th visit as pure
contraction. The true |ĉ_r^{(k)}| can be *larger* after a
visit than the product q_r · |ĉ_r^{(k-1)}| because the visit
pumps energy in from other modes.

### The correct object

The right tool is not Minkowski on the component norms. It is
the Fourier-mode transfer matrix.

Define the column vector ĉ(k) = (ĉ_r^{(k)})_{r ≠ 0} after k
returns. The return operator T_R acts on this vector as

    ĉ(k+1) = M · ĉ(k)

where M is the mode-coupling matrix of T_R: M_{rs} is the
amplitude transferred from mode s to mode r by one return
cycle (visit to R plus subsequent excursion). The diagonal
entries M_{rr} contain the contraction (from ε) and the
rotation-averaged decay (from excursion). The off-diagonal
entries M_{rs} contain the injection from mode s into mode r
via the b-step nonlinearity.

The spectral gap of T_R in the Fourier-weighted L² norm is
the spectral radius of M. If M is diagonally dominant
(contraction exceeds injection for each mode), then
ρ(M) < 1 and T_R contracts. The effective per-return
contraction is q_eff = ρ(M), which folds in both the
diagonal loss and the off-diagonal injection.

After k returns, ‖ĉ(k)‖ ≤ q_eff^k · ‖ĉ(0)‖. Between
returns, rotation during excursions of length τ_j multiplies
each mode by γ_r^{τ_j}. But the excursion rotation is
*diagonal* in Fourier space (rotation couples no modes), so
it commutes with the norm and the bound is clean:

    |ĉ_r(n)| ≤ q_eff^k · Π_{j=1}^k γ_r^{τ_j} · γ_r^{τ_0}
              = q_eff^k · γ_r^{n − (time in R)}

The product q_eff^k · γ_r^{n−ck'} is the per-trajectory bound.
Taking expectations:

    E[q_eff^{N_n} · γ_r^{n − c'N_n}]
    = γ_r^n · E[(q_eff / γ_r^{c'})^{N_n}]

If q_eff < γ_r^{c'} (i.e., the per-return contraction is
larger than the rotation loss recovered by spending c' steps
in R instead of rotating), then q_eff / γ_r^{c'} < 1, and
the expectation E[(q_eff/γ_r^{c'})^{N_n}] is bounded by 1.
The dominant factor is γ_r^n, giving exponential decay.

If q_eff > γ_r^{c'} (the per-return injection is large
enough that the time spent in R is a net loss compared to
continued rotation), then q_eff / γ_r^{c'} > 1, and the
expectation E[(q_eff/γ_r^{c'})^{N_n}] grows. Its growth rate
depends on the distribution of N_n.

For N_n ~ Mittag-Leffler with index 1/2:

    E[λ^{N_n}] ~ exp(c_λ √n)    for λ > 1

(this is the Laplace transform of the Mittag-Leffler,
evaluated above 1; it grows stretched-exponentially). So:

    E[q_eff^{N_n} · γ_r^{n−c'N_n}]
    = γ_r^n · exp(c_λ √n)
    = exp(−n |log γ_r| + c_λ √n)
    = exp(−|log γ_r| · n + c_λ √n).

For large n, the −n term dominates and the bound is
exponential. But for moderate n — the regime the simulation
probes — the +c_λ √n term competes, and the effective rate
looks like exp(−c_eff √n) over a wide window.

This is a transient explanation: the true asymptotic rate is
exponential (set by rotation), but the approach to the
asymptote is slowed by √n-scaled injection events, producing
an apparent stretched-exponential over a simulation-accessible
window.

Alternatively, if the mode-coupling matrix M has spectral
radius close to 1 / γ_r^{c'}, the two terms in the exponent
nearly cancel, and the residual rate is controlled by the
next-order term — which could genuinely be exp(−c√n) as the
asymptotic rate, not a transient.

### Summary of the theoretical picture

Three regimes, depending on the balance:

| Condition | Ensemble TV rate | Mechanism |
|---|---|---|
| q_eff < γ^{c'} | exp(−α n), α > 0 | Rotation dominates; visits to R are a minor perturbation |
| q_eff ≈ γ^{c'} | exp(−c √n) | Balanced; injection nearly cancels rotation loss during visits |
| q_eff > γ^{c'} | O(1/√n) | Injection dominates; spectral-gap bound is tight |

The simulation says we are in the middle regime. The question
is whether the middle regime is a sharp balance that holds
asymptotically (giving true exp(−c√n)) or a crossover region
between the first and third (giving transient exp(−c√n) before
settling to one of the endpoints).

---

## Simulation plan

### What to measure

The Fourier coefficients of the ensemble mantissa distribution,
decomposed by return count. This is the direct empirical
counterpart of the Minkowski decomposition above.

### Run B1: Fourier mode tracking

    N = 10⁸ walkers
    Symmetric measure: P(a) = P(a⁻¹) = P(b) = P(b⁻¹) = 1/4
    Initial condition: m = 0, E = 0 for all walkers
    Time range: n = 0 to 600
    Sampling: every step from n = 1 to 200,
              every 5 steps from n = 200 to 600

At each sampled time n, record:

1. **Ensemble Fourier coefficients.** For r = 1, 2, 3, 4, 5:
   ĥ(r, n) = (1/N) Σ_{i=1}^N e^{−2πir m_i(n)}.
   Store both modulus and phase.

2. **Ensemble L₁** (same as existing sim infrastructure).

3. **Per-walker return count.** For each walker i, store
   N_n^{(i)} = number of times walker i has visited R by
   step n. Use E₀ = 3.

At a small number of checkpoint times (n = 25, 50, 100, 150,
200, 300, 500), additionally record:

4. **Conditional Fourier coefficients by return count.** Bin
   walkers by N_n^{(i)} = k. For each bin k with ≥ 1000
   walkers, compute ĉ_r^{(k)}(n) = (1/|bin_k|) Σ_{i ∈ bin_k}
   e^{−2πir m_i(n)} for r = 1, …, 5.

5. **Bin sizes.** P̂(N_n = k) = |bin_k| / N for each k.

Items 1–3 are cheap (one pass over walker array per sampled
step). Items 4–5 require binning at checkpoint times only.

### Run B2: Injection measurement

**Purpose:** directly measure how much Fourier amplitude the
b-step injects into each mode.

    N = 10⁸ walkers
    Same setup as B1
    Time range: n = 0 to 200
    Sampling: every step

At each step n, record for r = 1, …, 5:

    ĥ_before(r, n) = (1/N) Σ_i e^{−2πir m_i(n)}
    apply one generator step to all walkers
    ĥ_after(r, n+1) = (1/N) Σ_i e^{−2πir m_i(n+1)}

Also record, for walkers in R at step n only:

    ĉ_R_before(r, n) = (1/|R_n|) Σ_{i ∈ R_n} e^{−2πir m_i(n)}
    ĉ_R_after(r, n) = (1/|R_n|) Σ_{i ∈ R_n} e^{−2πir m_i(n+1)}

The ratio |ĉ_R_after(r)| / |ĉ_R_before(r)| is the empirical
per-step multiplier for mode r conditioned on the walker being
in R. If this ratio is < 1, the visit is a net contraction for
mode r. If > 1, the visit is a net injection. Tracking this
across steps as the mantissa distribution evolves reveals
whether the injection is constant, grows, or decays.

For walkers outside R, the same ratio gives the empirical
rotation multiplier. This should be approximately
cos(2πr log₁₀ 2) for each mode r, independent of n.

### Run B3: Excursion-resolved mode coupling

**Purpose:** measure the off-diagonal entries of the
mode-coupling matrix M directly.

    N = 10⁷ walkers
    Same setup
    Track individual excursions

For each walker, record a log of visits to R: the time of
each visit and the mantissa at entry. Between consecutive
visits (one complete excursion + one visit), compute the
Fourier transfer: if the walker entered excursion j with
mantissa m_enter and returned from excursion j with mantissa
m_return, accumulate the empirical kernel

    K̂_{rs} += e^{−2πir m_return} · e^{2πis m_enter}

over all walkers and all excursions. Normalize by excursion
count. The resulting matrix K̂ is the empirical version of M.

Its spectral radius is q_eff. Its diagonal elements give the
per-mode net contraction. Its off-diagonal elements give the
injection rates.

This run is more expensive in bookkeeping (per-walker
excursion logs) but uses fewer walkers. Wall time should be
comparable to B1.

**Mode-resolution sanity check.** With N = 10⁷ walkers and
~√600 ≈ 25 excursions per walker, B3 accumulates ~2.5 × 10⁸
excursion events. Per-event sampling noise on K̂_{rs} is
O(1/√events) ≈ 6 × 10⁻⁵. This gives matrix-entry precision
well below the ~10⁻² scale at which we need to distinguish
diagonal (q_eff ~ 0.3–0.9) from off-diagonal (injection)
structure, and below the ~3 × 10⁻² scale needed to
distinguish ρ(M) from γ₁^{c'} at 10% precision for the
balanced-regime test (see A3). N = 10⁷ is sufficient.

If the bin-k conditional analysis in B1 items 4–5 turns out
to need finer mode resolution at specific k, rerun B3 at
N = 10⁸ for that part alone.

---

## Analysis

### A1. Creation-destruction balance (from B1 + B2)

At each checkpoint time n, compute:

    Destruction rate: D(r, n) = −log|ĥ(r, n)| / n
    (effective per-step loss rate for mode r)

Plot D(r, n) vs n. Three possibilities:

- D(r, n) → constant > 0: exponential decay, rate set by
  rotation (first regime in the table above).
- D(r, n) → 0 but D(r, n) · √n → constant: stretched-exp
  decay (middle regime).
- D(r, n) → 0 and D(r, n) · √n → 0: algebraic or slower
  (third regime).

Also compute:

    Per-visit injection: I(r, n) from B2's ĉ_R_after/ĉ_R_before
    Per-step rotation loss: γ_r from B2's non-R walkers
    Implied balance: q_eff / γ_r^{c'} from B3's spectral radius

If q_eff / γ_r^{c'} ≈ 1 (within, say, 10%) for the dominant
mode r = 1, that confirms the balanced regime and supports
exp(−c√n) as the genuine rate, not a transient.

### A1b. L₁ vs. ‖h‖_{L²} rate cross-check

The sibling plans analyse L₁; this plan's regime classification
is about ‖h‖_{L²}. For BENTHIC's L² regime verdict to serve as a
coherence check on the sibling plans' L₁ shape claims, the two
norms must have the same exponent rate (prefactors may differ
via L₁ ≤ √B · ‖h‖_{L²}, but exponent rates should transfer under
a dominant-mode assumption).

At every sampled n from B1:

- **L₁(n)** from the same histogram used by ALGEBRAIC/TUKEYS.
- **‖h‖_{L²}(n)** = (Σ_{r=1…5} |ĥ(r, n)|²)^(1/2) from B1 item 1.

Plot log L₁ and log ‖h‖_{L²} vs. n on the same axes, and fit
slopes on [50, 200]:

- Parallel slopes (difference < 20%) ⇒ rate-family transfer
  is empirically valid. BENTHIC's L² conclusions apply to L₁.
- Divergent slopes ⇒ the mantissa deviation is spreading
  across modes at different rates, and the single-dominant-
  mode assumption fails. Interpret any authority-map
  disagreement between BENTHIC's regime and the L₁ shape as
  potentially norm-mismatch rather than mechanism
  contradiction, and flag accordingly in the final report.

Zero compute cost — both statistics derive from data already
recorded in B1.

### A2. Phase structure (from B1 items 4–5)

At each checkpoint, plot the conditional Fourier coefficients
ĉ_r^{(k)} in the complex plane, colored by k. Under the
Minkowski scenario (no inter-k cancellation), they should
cluster along a ray from the origin — all pointing the same
direction, different lengths. Under the cancellation scenario,
they should scatter in phase — different k values pointing
different directions.

If they scatter: the ensemble coefficient ĥ(r) = Σ_k p_k
ĉ_r^{(k)} benefits from phase cancellation, and Minkowski is
loose. The cancellation can be quantified:

    Cancellation ratio = |ĥ(r)| / Σ_k p_k |ĉ_r^{(k)}|

This ratio is 1 if all phases align (Minkowski tight) and
approaches 0 if phases are uniformly scattered. Plot vs n.

### A3. Mode-coupling matrix (from B3)

Compute the empirical M matrix (say 10 × 10, modes r = 1…10).
Report:

- Spectral radius ρ(M) = q_eff.
- Diagonal dominance: is |M_{rr}| > Σ_{s≠r} |M_{rs}| for
  each r?
- Energy flow: for the dominant mode (r = 1), what fraction
  of its post-visit amplitude came from injection (off-diagonal)
  vs. retention (diagonal)?
- Compare ρ(M) to γ₁^{c'} where c' is the empirical mean
  time spent in R per visit. The ratio ρ(M)/γ₁^{c'} determines
  which regime we are in.

**Uncertainty on ρ(M) via excursion bootstrap.** Bootstrap the
B3 excursion log 1000 times (resample excursions with
replacement), recompute M̂, compute ρ(M̂) for each resample,
and report the 95% CI on ρ(M). The regime determination

    ρ(M)  vs.  γ₁^{c'}

is meaningful only if the CI on ρ(M) is narrower than the
decision threshold (10% of γ₁^{c'}). If the CI is too wide,
escalate B3 to N = 10⁸ or increase excursion sampling.

A parallel bootstrap on c' (the mean time in R per visit)
is also needed — c' has Monte Carlo noise too. Report the CI
on γ₁^{c'} via bootstrap over visits. The regime determination
is consistent only when the two CIs (on ρ(M) and on γ₁^{c'})
either overlap at a common value (balanced regime) or are
cleanly separated (rotation-dominated or injection-dominated).

### A4. Stretched-exp diagnostic (combining A1–A3)

If A1 shows D(1, n)·√n → constant ≈ 0.55, and A3 shows
ρ(M) ≈ γ₁^{c'}, and A2 shows moderate but not extreme
cancellation, the conclusion is:

    The exp(−c√n) rate is the creation-destruction balance
    between exponential rotation-based mixing during excursions
    and √n-scaled ε-injection events during visits to R. The
    rate constant c is determined by the spectral radius of the
    mode-coupling matrix M relative to the per-step rotation
    multiplier γ, mediated by the null-recurrent visit
    statistics.

If instead A1 shows D(1, n) → constant and A3 shows
ρ(M) << γ₁^{c'}, the conclusion is that we are in the
exponential regime and the stretched-exp fit is a transient.

If A1 shows D(1, n) · n → constant and A3 shows
ρ(M) >> γ₁^{c'}, the conclusion is that we are in the
algebraic regime.

---

## Initial-condition assumption

All three runs (B1, B2, B3) use single initial condition
(m, E) = (0, 0). The mode-coupling matrix M, its spectral radius
ρ(M), and the regime determination are assumed IC-independent on
theoretical grounds: they describe the operator T_R itself, not a
walker trajectory from a particular starting point. The stretched-
exp amplitude A and crossover time n* are IC-dependent (as with
the sibling plans), but BENTHIC doesn't directly measure those.

If the theoretical IC-independence of M fails (e.g., different
starting distributions produce effectively different M because
the walk hasn't explored the state space enough at the moderate
n used by B3), the regime determination is single-IC only. The
empirical cross-check is `ALGEBRAIC-SIM-MESS-PLAN.md`'s optional
M4b run (IC (a) at N = 10⁸); if M4b's long-time L₁ agrees with
M4's, IC-independence holds downstream of B3's M as well.

---

## Cost

B1: 10⁸ walkers × 600 steps. Fourier coefficient computation
at each step is O(N) per mode (one complex exponential per
walker). Five modes: 5N per step. Total: 5 × 10⁸ × 600 =
3 × 10¹¹ flops. With vectorized NumPy: ~3 hours.

B2: same as B1 with additional per-step bookkeeping for R vs
non-R partition. Marginal cost over B1: ~20%. Can be folded
into the same run.

B3: 10⁷ walkers × 600 steps, plus per-walker excursion
logging. The logging is the bottleneck — storing entry/exit
mantissa pairs for ~10⁷ × O(√600) ≈ 2.5 × 10⁸ excursion
events. At 16 bytes per event (two float64): ~4 GB. Feasible
in RAM. Wall time: ~30 minutes for the walk, ~10 minutes for
the matrix computation.

Total: ~4 hours, no cluster.
