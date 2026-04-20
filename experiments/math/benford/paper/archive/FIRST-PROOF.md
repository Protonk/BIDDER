# FIRST-PROOF

**Superseded by `paper/SECOND-PROOF.md`** as of 2026-04-19.
FIRST-PROOF was written against T1a (stretched-exp asymptotic)
and Route 1'; SECOND-PROOF is the current gap list under T1b and
the polynomial-tail induced-operator framework. This doc stays
as the archival T1a-era record.

What must close before we draft the PNAS Brief Report. Each gap is a
load-bearing wall; the rhetoric in `PNAS-PLAN.md` assumes all six are
settled. BINADE-WHITECAPS §§7–8 contributes Parseval on ε but does not
by itself close any of these — that identity is static and
coordinate-theoretic; every gap below is dynamical or definitional.

Priority order: 1–3 are load-bearing. 4 is a numerical sanity check
that gates the rate claim in Theorem 2. 5–6 are rhetoric/proof
alignment — the paper can still ship if these soften, but the Columbo
structure loses force.

---

## 1. State space and operator notation

**Status:** minimal setup only. The substantive invariant-measure
question has migrated into gap 2 (which invariant to use depends
on the proof route chosen there).

**State space.** X = T × ℤ, where T = ℝ/ℤ is the log-mantissa
circle and ℤ is the exponent coordinate. σ-algebra
B = B(T) ⊗ 2^ℤ (Borel on T, discrete on ℤ). The mantissa step
under +1 depends on E, not just m:

    m ↦ frac(log₁₀(10^m + 10^{−E})),

so the full state (m, E) is the right object; collapsing to T
alone loses information.

**Kernel.** The walk induces a Markov kernel K : X × B → [0, 1]
by averaging over the generator choice under μ. K(x, ·) is a
probability measure for each x (a 4-atom mixture, one atom per
generator); K(·, A) is B-measurable for each A. Iterates K^n are
kernel composition, not repeated composition of a single
measurable map.

**Total variation distance.** For probability measures μ, ν on a
common measurable space (Y, G),

    ‖μ − ν‖_{TV} := sup_{A ∈ G} |μ(A) − ν(A)|
                  = ½ · ∫ |dμ − dν|,

and equivalently, when μ, ν are both absolutely continuous with
respect to a dominating measure λ with densities p, q, then
‖μ − ν‖_{TV} = ½ ‖p − q‖_{L¹(λ)}. In our setting: measures live
on (X, B) or on T; the dominating measure for T-marginals is
Leb_T. When we write "TV on measures," we mean this norm; when
we write "TV on densities," we mean the equivalent L¹(Leb_T)/2
reading of the same quantity.

**What the theorem targets.** The mantissa-marginal TV distance
to Leb_T:

    φ(ν, n) := ‖π_T(ν K^n) − Leb_T‖_{TV},   ν a probability on X.

Theorem 1 asks for φ(ν, n) ≤ C · exp(−c√n) as n → ∞, uniform over
ν with π_T ν ≪ Leb_T.

**The invariance question, deferred.** A full-space σ-finite
invariant measure on T × ℤ (most likely the pushforward of left
Haar on BS(1,2)) exists but need not be exhibited to prove
Theorem 1's decay rate. Under the current primary proof candidate
(gap 2 Route 1', induced-return operator on R), the load-bearing
invariant is a *probability* measure ν_R on a compact set R ⊂ X
(R is compact, not finite — T-coordinate is continuous), not a
σ-finite measure on all of X.

**Caveat:** the global σ-finite invariant is deferred, not
necessarily irrelevant. A natural way to prove gap 2's (R6)
(identifying the mantissa marginal of ν_R as Leb_T) may go
through a harmonic / invariant-measure object on T × ℤ. If (R6)
takes that route, gap 1's deferred question re-enters the proof.

**What closure looks like.** A half-page setup in the draft:
(X, B), the kernel K, the mantissa projection π_T, the TV
distance φ(·, ·). Invariant-measure details and function-space
choice are deferred to gap 2's proof section.

---

## 2. The contraction step

**Status:** open, primary candidate identified. Not yet drafted.
An earlier Rosenthal small-set minorization attempt is
[withdrawn](./GAP2-LEMMA.md) for the reasons documented at the
top of that file. The empirical target (stretched-exp rate,
c ≈ 0.55) stands.

**Why the earlier attempts failed.** TV-to-Leb_T on a single-walk
step isn't monotone for this kernel — uniform mantissa at E=0
becomes ≈0.09 away from uniform after one step (Monte Carlo
check). This kills any per-step contraction claim of the form
φ(νK) ≤ (1 − β·ν(R))·φ(ν). The underlying structural point is
that K does not preserve Leb ⊗ counting; Leb_T is not an
invariant marginal under a single step; and the kernel is atomic
for each x, so density-based minorizations on X directly don't
apply.

**TV is not the villain.** TV between two laws under the *same*
Markov kernel is always contractive. What failed was asking for
TV-to-Leb_T when Leb_T isn't invariant. The fix is to change the
*operator* (not the norm) to one that has a genuine invariant
probability.

### Route 1' (primary candidate): induced first-return operator on R

**Object.** Let R = {(m, E) ∈ X : |E| ≤ E₀}. For any probability
ν supported on R, define

    T_R ν := Law(X_{τ_R})     where  τ_R = min{n ≥ 1 : X_n ∈ R}.

T_R is a Markov operator on probability measures on R. Because
R is finite in the E direction and the walk is recurrent
(symmetric case), τ_R < ∞ almost surely, so T_R is well-defined.

Why this works where per-step didn't: T_R acts on a compact
state space R (T × finite E-range) and is expected to have a
genuine invariant probability ν_R. TV contraction under T_R to
ν_R is honest once ν_R exists.

**Sub-problems (R1)–(R6), plus a bookkeeping step (R1.5) and a
structural observation.**

- **(R1) Define T_R rigorously via excursion decomposition.** Two
  regimes, both a.s. finite but not literally bounded:
  - **Upward excursion** (walker leaves R via a-step to E > E₀).
    Once outside, a/a⁻¹ do rotation on T (no mantissa change
    otherwise) and diffuse E; b/b⁻¹ at large positive E are
    near-identity. Upward excursions are a.s. finite in length
    by null-recurrence of the symmetric exponent walk, but
    can be arbitrarily long — their length distribution has a
    heavy (√-scale) tail.
  - **Downward excursion** (walker leaves R via b⁻¹ to E < −E₀,
    more precisely: |x| becomes small). The next b or b⁻¹ step
    snaps |x| to near 1, re-entering R near (m=0, E=0). In
    practice short in duration; formally: bounded above by the
    first b/b⁻¹ arrival time conditional on being outside R,
    which is a.s. finite (a/a⁻¹ steps can intervene but each
    step is b or b⁻¹ with probability 1/2, so the first b-event
    is geometrically distributed).
- **(R1.5) Mid-excursion bookkeeping.** At a generic time n, the
  walker is usually *not* at a return time — it is partway
  through an excursion. The law-level bound on φ(ν, n) is the
  mixture of (walkers who have made k returns and are currently
  in R, handled by (R4)+(R5)) plus (walkers mid-excursion, not
  handled by any other item). Two contributions to bound:
  - **Upward mid-excursion.** The mantissa sees only a/a⁻¹
    rotations plus b/b⁻¹ perturbations of size O(10^{−E₀}) in
    TV. Rotation is TV-isometric against Leb_T, so the mantissa
    marginal is within O(10^{−E₀}) of whatever it was at the
    last return. Negligible for E₀ large.
  - **Downward mid-excursion.** Bounded by the geometric b-snap
    return time times the per-step TV perturbation. Absorbable
    into an O(1) adjustment to T_R's effective contraction
    constant.

  Not a research problem; needs to be stated and bounded
  explicitly so the final TV bound is complete.
- **(R2) Show T_R has an invariant probability on R.** R =
  T × {−E₀, …, E₀} is *compact* but not finite (continuous
  T-coordinate). The route is:
  - Show T_R is a weak-Feller / Feller Markov operator on
    compact R. The b-step map m ↦ frac(log₁₀(10^m + 10^{−E}))
    is continuous on T (carry/wrap discontinuity is resolved by
    working on the circle). For T_R's Feller property specifically,
    null-recurrence of τ_R's law means standard
    positive-recurrence inheritance doesn't apply off-the-shelf;
    a half-page argument suffices: truncated return operators
    are finite compositions of K and hence continuous, and
    uniform geometric tail bound on τ_R from any x ∈ R gives
    uniform convergence to T_R. Uniform limit of continuous is
    continuous.
  - Apply Krylov–Bogolyubov to get existence of at least one
    invariant probability ν_R.
  - **Defer uniqueness to (R4)** — uniqueness should fall out
    of the contraction/spectral-gap argument, not be claimed
    for free here.
- **(R3) Choose a norm on densities on R.** Priority order:
  - **Fourier-weighted L²** on the zero-mean part. Natural first
    try: BINADE-WHITECAPS §§7–8 gives the Fourier coefficients of
    ε, and the quantity that should control q is the Fourier
    decay of T_R's kernel — it should wire in directly.
  - **BV** fallback. If carry/wrap discontinuities make Fourier
    bookkeeping ugly, BV handles jumps more gracefully.
  - **H^s** least attractive. Branch/carry discontinuities are
    bad for Sobolev norms.
- **(R4) Prove T_R contracts zero-mean part in the chosen norm.**
  Target: spectral gap q < 1, i.e., ‖T_R f − ν_R(f)·𝟙‖ ≤ q·‖f −
  ν_R(f)·𝟙‖ for f in the chosen function space. The q should be
  a computable functional of ε; per-excursion contraction.
  Uniqueness of ν_R is an output of this step (irreducibility
  + gap ⇒ unique invariant).

  **Empirical cross-check.** `sim/BENTHIC-MINKOWSKI-SIM.md` B3
  measures the spectral radius ρ(M) of T_R's mode-coupling
  matrix empirically via excursion-resolved Fourier transfer.
  If B3 returns ρ(M) < 1 with tight CI, that is empirical
  support for (R4)'s gap claim even without a rigorous proof —
  and supplies a numerical target for the theoretical q. If
  B3 returns ρ(M) ≈ 1, proof of (R4) is unlikely to succeed.
  Run B3 before committing substantial effort to (R4)
  analytically.
- **(R5) Stochastic estimate on the return count.** Separate
  proof-grade step, not a trivial application of E[N_n] ∼ c_R√n.
  The law-level bound we need is

     E[q^{N_n}] ≤ C · exp(−c · √n),

  or equivalently a lower-tail estimate P(N_n ≤ a√n) ≤ exp(−rate
  in a), strong enough to convert (R4)'s per-return contraction
  into the claimed decay. N_n is random, with √n scaling but a
  nondegenerate Mittag-Leffler / arcsine-type limit; mean alone
  is insufficient.

  **Non-trivial subtlety:** the E-process is *not* autonomous.
  b/b⁻¹ steps produce E-increments that depend on m (and on E
  itself for large E-jumps — adding 1 to a number near a power
  of 10 can change the exponent by several levels). So N_n is a
  functional of the coupled (m, E) process, not of a simple
  ±1 walk. However, the E-process is a zero-drift martingale
  with bounded increments uniformly in m (under the symmetric
  measure). The Laplace-transform estimate follows by applying
  the classical exponential-martingale + optional-stopping
  argument to this generalized-increment walk, with constants
  adjusted by the comparison. Estimated length: 2–3 pages, not
  one. References: Feller *Probability*, Vol. II (Chung–Erdős
  return-time theory on simple walks, adapted).
- **(R6) Connect ν_R to Leb_T.** Spectral gap for T_R gives
  convergence to ν_R, *not* convergence to Leb_T. We need
  π_T ν_R = Leb_T. Two candidate routes.

  **Primary route (Fourier via R4).** If (R4)'s norm controls
  T-Fourier modes uniformly across E-levels, T_R's spectral gap
  forces each conditional density ρ_E(m) to be constant, making
  π_T ν_R uniform. The rotation-on-excursions fact enters here
  as the reason nonzero Fourier modes are damped by T_R's
  excursion part. Depends on (R3)/(R4) details; closing step is
  2–4 pages once R4 is in hand.

  **Secondary route (rotation-invariance, standalone).** During
  upward excursions, a-steps rotate the mantissa by ±log₁₀ 2 and
  b-steps are near-identity at depth E₀. The sketch: excursion
  length has positive probability on every n ∈ ℤ₊, n · log₁₀ 2
  mod 1 is dense in T by Weyl, so π_T ν_R must be rotation-
  invariant, hence Leb_T. This route is *not* self-contained: K
  does not commute with T-rotation inside R, dense support of
  the excursion-rotation distribution is weaker than σ-invariance
  under a specific irrational rotation, and the b-step
  perturbation at finite E₀ needs absorbing. See MESSES #2 for
  the mechanical specifics.

  The deferred σ-finite invariant from gap 1 is *not* needed for
  either route.

- **(Structural observation, stated once in the iteration step.)**
  Excursion-level rotation is independent of contraction-level
  dynamics because rotation on T is TV-isometric against Leb_T.
  This means the per-return contraction in (R4) and the return-
  count statistics in (R5) can be applied as independent factors.
  Immediate fact, but it's what makes the architecture
  (R4) × (R5) product bound legitimate.

### What closure looks like

A lemma combining three independent ingredients:
- (R4): T_R has spectral gap q < 1 on the chosen function space.
- (R5): N_n's Laplace transform satisfies E[q^{N_n}] ≤ C exp(−c√n).
- (R6): the mantissa marginal of ν_R equals Leb_T.
Conclusion: φ(ν, n) ≤ C' exp(−c√n) with c effectively determined
by q and the Laplace-transform-level rate constant from (R5). The
sim gives c ≈ 0.55; theoretical c should be in that neighborhood.

### Next action

Three-stage paper-first work:
1. **(R1)–(R2):** make T_R rigorous via the excursion
   decomposition (upward a-diffusion + return; downward b-snap +
   re-entry), prove T_R is weak-Feller on compact R, apply
   Krylov–Bogolyubov for an invariant probability ν_R (existence
   only; uniqueness later).
2. **(R3)–(R4):** pick a norm (Fourier-weighted L² first, BV
   fallback), prove spectral gap q < 1 on the zero-mean part,
   with q as a computable functional of ε. Uniqueness of ν_R
   follows.
3. **(R5) + (R6):** Laplace-transform analysis of the return
   count N_n to convert q-per-return into exp(−c√n) at the law
   level; and Benford identification of ν_R's mantissa marginal.

Do not write lemma text until (R4) and (R5) are both settled on
paper — the earlier GAP2-LEMMA withdrawal was caused by drafting
ahead of the framework; (R5) in particular is not a cosmetic step
and can derail the rate if handled carelessly.

---

## 3. Visit-rate consistency with observed rate

**Status:** **resolved.** Phase 1 sim (N = 10⁷, t ∈ [0, 600], see
`paper/sim/` and `gap3_phase1.py`) shows the true shape is
**stretched exponential exp(−c√t) with c ≈ 0.55**, not exponential.

**The finding.** Both models fit to a common pre-floor window:

| Window | exp fit (R², resid σ) | stretched fit (R², resid σ) |
|---|---|---|
| [20, 100] | 0.9963, 0.061 | **0.9983, 0.042** |
| [20, 120] | 0.9929, 0.094 | **0.9985, 0.043** |

The exp residuals are 2.2× larger than stretched on the extended
window, and they carry systematic curvature. The local slope of
log(L₁) vs. t drops from −0.048 at t = 25 to −0.020 at t = 130 —
a factor of 2.4× change — which tracks stretched's −c/(2√t)
prediction closely and is incompatible with constant-slope
exponential.

**Consequences.**

- **Shape fits the return-operator framework.** Gap 2 Route 1'
  (induced first-return operator on R) predicts exactly this
  shape: if T_R has spectral gap q < 1 and N_n ∼ c_R√n returns
  occur by step n, then q^{N_n} ≈ exp(−(−log q)·c_R·√n). Per-
  step contraction was the wrong object; per-return contraction
  lands the √n naturally.
- **Theorem 1 wording.** "Exponential convergence" in the plan's
  Theorem 1 must change to "stretched-exponential convergence" at
  rate exp(−c√n). See `PNAS-PLAN.md` (updated).
- **Phase 2 / phase 3 remaining.** Phase 2 (N = 10⁸, extend clean
  decay to t ≈ 200) is confirmatory, not decisive; optional. Phase
  3 (biased walk) done — see gap 4.

---

## 4. Biased-walk convergence mechanism

**Status:** **resolved.** Phase 3 simulation (N = 10⁶, t up to
50,000, weights (0.2, 0.2, 0.4, 0.2); see `gap3_phase3.py` and
`paper/sim/`) confirms biased walks converge to Benford via a
two-regime mechanism.

**The finding.** L₁ decays to the N = 10⁶ noise floor (0.0128) by
t ≈ 2000 and fluctuates there through t = 50,000.

**Two-regime mechanism, observed.**

| phase | t range | active fraction | L₁ at end |
|---|---|---|---|
| 1. Active (ε-minorization) | 0 → ~500 | 100% → 3% | 0.017 |
| 2. Transition | ~500 → ~1000 | 3% → 0% | 0.015 |
| 3. Post-escape (Weyl rotation) | > 1000 | 0% | floor |

In phase 1, walkers sit near the origin in E and the b-step produces
ε-controlled minorization — same mechanism as the symmetric case,
but with the exponent walk drifting through the active zone rather
than recurring to it. In phase 3, walkers are frozen in |E| > 20,
so b-steps are identity on mantissa and only a/a⁻¹ act. Irrational
rotation by ±log₁₀ 2 is ergodic on T at algebraic Weyl rate ~1/n;
residual deviation from uniform halves per doubling in t (0.017 at
t = 500 → 0.002 at t = 2000), consistent with 1/n.

**Consequences.**

- **Theorem 1 scope.** Remains the symmetric measure. Phase 3
  supports a **positive-drift biased corollary** with a two-regime
  rate statement, not a theorem broadened to all nondegenerate μ.
  PNAS-PLAN §7's biased-walk bullet is empirically confirmed in
  that narrower form.
- **Precise post-escape rate not measured.** The transition from
  stretched-exp to algebraic happens below the N = 10⁶ noise floor,
  so we cannot resolve a specific power-law exponent α from this
  run. A confirmatory N = 10⁸ run with focused t ∈ [500, 10⁴]
  sampling would pin α down if needed for publication.
- **Snap-asymmetry note (sim/SIM-REPORT phase 3).** Positive multiplicative
  drift sends walkers to the frozen zone; negative drift would
  recycle them through origin and plausibly preserve stretched-exp
  convergence. The current Theorem 1 corollary is for positive drift;
  negative drift is a separate conjecture.

---

## 5. Group-relation's role in the proof

**Status:** **resolved by option (B).** Route 1' proof uses only
generator *actions*:
- (i) rotation of mantissa by log₁₀ 2 under a-steps,
- (ii) ε-perturbation of mantissa under b-steps at bounded depth,
- (iii) null-recurrent return statistics of the exponent walk.

None uses the relation **bab⁻¹ = a²**. Web-agent review
(2026-04-17) confirmed the proof-rhetoric mismatch: a free group
on {a, b} with the same generator actions would give the same
proof.

**Resolution.** The §6 kicker has been narrowed to say "BS(1,2)
is the minimal algebraic setting in which both operations
appear — the relation bab⁻¹ = a² identifies the group, not the
mechanism." Option (A) (making the relation load-bearing via a
Cuno & Sava-Huss ladder-time argument) was considered but not
pursued — it would require adding proof machinery that the
symmetric-case Theorem 1 doesn't need.

---

## 6. Schatte → mixed-walk bridge

**Status: resolved.** Schatte is cited in PNAS-PLAN §6 movement A
as diagnostic of the pure-addition regime and engaged in the §6
kicker as a competing explanation for the mixed walk. The earlier
"Schatte's Riesz weighting is produced automatically by the
group's own structure" slogan was dropped; the mixed walk is a
Markov chain with intrinsic mixing, not an ex post facto
re-weighting.

---

## Triage

| Gap | Status | Cost to close | Blocks draft? |
|-----|--------|---------------|---------------|
| 1. State space + notation | Minimal setup only; σ-finite invariant deferred (may re-enter via gap 2 (R6)) | ~half page | No |
| 2. Contraction step | **Open, primary candidate identified.** Induced first-return operator T_R on compact R; six sub-problems (R1)–(R6), with (R5) Laplace-transform analysis of return count on critical path | Research, paper-first | Yes |
| 3. Visit-rate vs. rate shape | **Resolved** — stretched exp, c ≈ 0.55 | — | — |
| 4. Biased-walk mechanism | **Resolved** — 2-regime convergence | — | — |
| 5. Group relation's role | **Resolved** — §6 kicker narrowed; proof uses generator actions only, not the relation | — | — |
| 6. Schatte bridge | **Resolved** — diagnostic only (§6 movement A), not mechanism | — | — |

**Minimum viable path to draft:** gap 2 is the sole load-bearing
open problem. Three independent proof-grade steps must close:
(R4) spectral gap for T_R, (R5) Laplace-transform lower-tail
estimate for the return count, and (R6) Benford identification of
ν_R's mantissa marginal. Any one of these failing breaks the
theorem.

**Next concrete action:** work in this order on paper:

1. (R1)–(R2): define T_R rigorously; prove weak-Feller on
   compact R; apply Krylov–Bogolyubov for invariant-probability
   existence.
2. (R3)–(R4): pick norm, prove spectral gap q < 1 on zero-mean
   part. Uniqueness of ν_R follows from this.
3. (R5): Laplace transform of N_n. This is a classical
   random-walk calculation (Feller Vol. II style) but it is
   non-trivial and on the critical path — the √n scaling of
   E[N_n] is not sufficient.
4. (R6): show π_T ν_R = Leb_T. May require the deferred
   σ-finite invariant from gap 1.

Do not draft lemma text until (R4) and (R5) are both settled.
The earlier GAP2-LEMMA withdrawal was caused by drafting ahead of
the framework.
