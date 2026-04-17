# FIRST-PROOF

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

## 1. Define the operator

**Status:** scope decided (σ-finite, on T × ℤ). Three technical items
still open inside that scope; enumerated below.

**Why T alone won't do.** The mantissa step under +1 depends on the
exponent E, not just m:

    m ↦ frac(log₁₀(10^m + 10^{−E})).

So the state space is T × ℤ (mantissa × exponent), not T. Insisting
on a probability measure forces an averaging move — and for both
symmetric μ (null-recurrent exponent walk) and biased μ (transient)
no stationary probability measure exists on ℤ. The σ-finite register
removes the forcing: invariance of a σ-finite measure, not
normalization, is what the proof needs.

**The commitment.** Following Tao (*Introduction to Measure Theory*,
§1.4):

- **State space.** X = T × ℤ.
- **σ-algebra.** B = B(T) ⊗ 2^ℤ — Borel on the mantissa circle (Def
  1.4.16), discrete on the exponent (Def 1.4.12).
- **Kernel.** The walk is a Markov kernel K : X × B → [0, 1],
  averaging over the generator choice under μ. K(x, ·) is a
  probability measure for each x ∈ X; K(·, A) is B-measurable for
  each A ∈ B (Def 1.4.32). This is the object the proof acts on —
  not the per-realization measurable morphism, which is only one
  sample from K(x, ·).
- **Reference measure.** μ_ref = Leb_T ⊗ counting_ℤ — σ-finite but
  not finite (Def 1.4.27, Example 1.4.26, Remark 1.4.13). Provides
  the L² scaffolding.

**Three items to close before gap 2 can build on this.**

1. **Find the invariant σ-finite measure.** μ_ref K = μ_ref is *not
   obvious* and probably not true. The a-step (mult by 2) is a
   measure-preserving bijection of (T × ℤ, Leb ⊗ counting) — m ↦ m +
   log₁₀ 2 mod 1, E ↦ E + carry(m), and carry is Lebesgue-Bernoulli
   independent of E. The b-step (add 1) is not: for E ≪ 0 it
   collapses all of T × {E} onto a thin slice near (m = 0, E = 0),
   destroying counting-measure mass on negative-E strata. The
   combined kernel inherits the obstruction. The honest fix is to
   identify the invariant σ-finite measure by construction — most
   likely the pushforward of left Haar measure on BS(1,2) through
   the projection |x| ↦ (m, E). BS(1,2) is solvable, hence amenable,
   hence has a well-defined left Haar; its pushforward is σ-finite
   on T × ℤ and walk-invariant by construction. Whether it equals
   Leb ⊗ counting is a separate computation; if not, the invariant
   μ is a weighted version and the L² scaffolding shifts
   accordingly.

2. **Call K a Markov kernel, not a morphism.** (Already corrected
   above.) The iterate K^n is kernel composition, not self-
   composition of a fixed map. Remark 1.4.33's ergodic-theory
   framing is still the right register, but the object is the
   kernel, not its realizations.

3. **Say what λ refers to.** In the σ-finite infinite-measure
   setting, constants are not in L²(X, μ), so "gap from eigenvalue
   1" has no direct meaning (1 is typically in the spectrum but not
   the point spectrum of K). The theorems want convergence of the
   *mantissa marginal* to the uniform (Benford) law on T, so define:

       λ := the contraction rate of the mantissa marginal,
       i.e. the largest λ > 0 such that
       ‖π_T (ν K^n) − Leb_T‖_{TV} ≤ C_ν · e^{−λ n}
       for every initial law ν on X with π_T ν ≪ Leb_T.

   This is what Theorem 1 actually needs. Any spectral-radius or
   L²-gap statement is a means to this end; it is not the λ the
   paper claims.

**What closure looks like.** Roughly one page in the draft: X, B,
the Markov kernel K, the invariant σ-finite μ (by construction from
Haar on BS(1,2)), and the definition of λ as a mantissa-marginal
contraction rate. Gap 2 then bounds λ from below via a functional of
ε.

---

## 2. The contraction step

**Status:** **open — no working route yet.** The Rosenthal small-
set minorization direction drafted in
[`GAP2-LEMMA.md`](./GAP2-LEMMA.md) is withdrawn; see the note at
the top of that file for the diagnosis. The theorem target
(stretched-exp rate, c ≈ 0.55) stands; the proof mechanism does
not.

**Why the withdrawn route fails.** Two structural problems, not
bookkeeping gaps:
- The kernel K(x, ·) for fixed x is a 4-atom mixture, so
  K^{k₀}(x, ·) has no density with respect to Leb ⊗ counting.
  Rosenthal Lemma 6(ii)'s β = ∫_X inf_{x∈R} k^{k₀}(x, y) dμ(y) is
  inapplicable because there is no k^{k₀}(x, y) to take the inf of.
- A proposed per-step TV contraction
  φ(νK) ≤ (1 − β·ν(R))·φ(ν) is false: a MC check from
  ν = Leb_T ⊗ δ_{E=0} (so φ(ν) = 0) gives φ(νK) ≈ 0.09. Corollary:
  Leb ⊗ counting is not invariant for K — the b-step has Jacobian
  10^m / (10^m + 10^{−E}) ≠ 1.

Gap 1's claim "μ = Leb ⊗ counting is the natural invariant
σ-finite measure" was also overstated — it holds for a-steps,
fails for b-steps. The invariant σ-finite measure, if it exists,
is most likely the pushforward of left Haar on BS(1,2), which
isn't Leb ⊗ counting.

**Live routes, in rough priority order:**

- **Route 1' (primary candidate): transfer operator K\* on
  absolutely continuous mantissa densities.** Work in the space
  of probability measures ν with π_T ν ≪ Leb_T. The action of K
  on such densities is AC-preserving (b-step is a diffeomorphism
  of T for each fixed E). Pick a translation-invariant norm on T
  (BV, Sobolev H^s, or weighted Fourier ℓ²) in which a-step
  rotation is an isometry and b-step at low depth is a strict
  contraction controlled by ε. The atomic-kernel obstruction goes
  away at the density-action level. Four sub-problems: (R1)
  choose the norm; (R2) prove per-visit contraction on densities
  in that norm; (R3) verify a-step is isometric in that norm;
  (R4) iterate using E[L_n] ~ c_R √n. **The whole route needs to
  be worked out on paper before we write a lemma.**
- **Route 2 (backup): wrapped-Cauchy comparison.** Dominate the
  averaged +1 kernel by a wrapped Cauchy in an operator norm on
  densities. Available if Route 1' doesn't yield a clean norm.
- **Route 3 (unlikely): wrapped-Cauchy identity.** The averaged
  +1 kernel *is* wrapped Cauchy. Noted for completeness.
- **Route 4 (alternative): direct Fourier analysis on the
  mantissa-marginal Fourier coefficients.** Show each Fourier
  coefficient of the mantissa marginal decays at stretched-exp
  rate. Closer to Schatte's machinery, bypasses kernel/density
  structure entirely. The Fourier coefficients of ε from BINADE-
  WHITECAPS §§7–8 plug in naturally if this works.

**What closure looks like.** A lemma that produces the stretched-
exp mantissa-marginal TV bound via one of the routes above. Not
yet drafted; we are specifically *not* drafting until the
function-space / norm choice is settled on paper first (the
withdrawn GAP2-LEMMA is a cautionary record of drafting on an
unsettled framework).

**Next action:** work out Route 1' on paper. Pick a candidate
norm (most likely H^{1/2}(T) or BV(T) — both translation-
invariant, both give b-step's Jacobian natural room to appear),
verify rotation-isometry, attempt the per-visit contraction. If
no norm works cleanly, fall back to Route 4.

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

The previously reported λ ≈ 0.035 on `bs12_rate.png` (fit window
[20, 100]) was a local-linear artifact: on a short window, both
models look straight, and the average slope of stretched is
numerically close to what exp would give.

**Consequences.**

- **Gap 2 route.** Rosenthal coupling (§2 Route 1) is the right
  route. The coupling framework's stretched-exp prediction (from
  null-recurrent joint visits ∼1/k forcing j ∼ √k in Theorem 1's
  TV bound) matches reality; no fall-back to direct Fourier is
  needed.
- **Theorem 1 wording.** "Exponential convergence" in the plan's
  Theorem 1 must change to "stretched-exponential convergence" at
  rate exp(−c√n). See `PNAS-PLAN.md` (updated).
- **Phase 2 / phase 3 remaining.** Phase 2 (N = 10⁸, extend clean
  decay to t ≈ 200) is confirmatory, not decisive; optional. Phase
  3 (biased walk) still needed for gap 4 scope.

---

## 4. Biased-walk convergence mechanism

**Status:** **resolved.** Phase 3 simulation (N = 10⁶, t up to
50,000, weights (0.2, 0.2, 0.4, 0.2); see `gap3_phase3.py` and
`paper/sim/`) confirms biased walks converge to Benford via a
two-regime mechanism.

**The finding.** L₁ decays to the N = 10⁶ noise floor (0.0128) by
t ≈ 2000 and fluctuates there through t = 50,000. There is **no
floor at 0.091** — the previously reported value was either a
digit-level (9-bin) L₁ snapshot or an earlier-run artifact.

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

- **Theorem 1 scope.** Can cover all nondegenerate μ. Biased case is
  a corollary with a two-regime rate statement, not a quantitative
  floor. PNAS-PLAN §7's biased-walk bullet is empirically
  confirmed.
- **Precise post-escape rate not measured.** The transition from
  stretched-exp to algebraic happens below the N = 10⁶ noise floor,
  so we cannot resolve a specific power-law exponent α from this
  run. A confirmatory N = 10⁸ run with focused t ∈ [500, 10⁴]
  sampling would pin α down if needed for publication.
- **Snap-asymmetry note (SIM-PLAN phase 3).** Positive multiplicative
  drift sends walkers to the frozen zone; negative drift would
  recycle them through origin and plausibly preserve stretched-exp
  convergence. The current Theorem 1 corollary is for positive drift;
  negative drift is a separate conjecture.

---

## 5. Group-relation's role in the proof

**Status:** rhetorical/proof misalignment.

**The problem.** The proof as sketched uses:
- (i) rotation of mantissa by log₁₀ 2 under a-steps,
- (ii) ε-perturbation of mantissa under b-steps,
- (iii) visit rate of the exponent walk to the active zone.

None of these uses the relation **bab⁻¹ = a²**. A free group on
{a, b} with the same generator actions would give the same proof.

But `PNAS-PLAN.md` §6 (lines 536–542) pivots on:

> "the asymmetry Hamming named disappears because the group relation
> bab⁻¹ = a² contains the interaction rather than leaving it to be
> reconstructed."

This is the rhetorical kicker of the paper. If the proof doesn't
use the relation, the kicker is overclaim.

**What closure looks like.** Two options.

- **(A) Make the relation load-bearing.** Identify a proof step that
  uses bab⁻¹ = a² — most likely in the visit-rate argument (the
  relation constrains the word length / geodesic depth of typical
  walk paths, giving a tighter ρ). Cuno & Sava-Huss's ladder-time
  machinery might be the vehicle.
- **(B) Soften the rhetoric.** Replace "group relation contains the
  interaction" with "BS(1,2) is the minimal algebraic model with
  both operations present, and the ε mechanism applies to any
  finitely-generated group whose action on the mantissa circle
  decomposes into rotation + ε-perturbation." Less dramatic, but
  honest.

**Recommendation.** Try (A) first via the visit-rate channel. If it
doesn't work within a week, fall back to (B) and rewrite the §6
kicker.

---

## 6. Schatte → mixed-walk bridge

**Status:** rhetorical pivot, unsupported.

**The problem.** `PNAS-PLAN.md` §4 (lines 444–462) claims:

> "pure addition performs Cesàro averaging on the mantissa Fourier
> coefficients and does not converge. Multiplication performs the
> coordinate change ψ = id + ε, converting Cesàro toward Riesz
> weighting. The Riesz weighting that Schatte had to impose
> analytically is produced automatically by the group's own
> structure."

This is a slogan. Schatte's weighting is an **index on summation
methods**: the j-th partial sum weighted by 1/j. The BS(1,2) walk
doesn't explicitly weight past contributions — it just applies
generators stochastically. Claiming the walk "performs" Riesz
weighting requires:

1. Writing the mantissa distribution after n steps as a weighted
   sum over histories.
2. Identifying the induced weights on the *additive* sub-histories
   as 1/j (or as something with the same damping on rotating Fourier
   modes).
3. Connecting this to the ε coordinate change.

**What closure looks like.** Either (a) a derivation executing steps
1–3 above, giving a clean operational statement of the pivot; or
(b) a rewrite of §4/§6 that proves exponential mixing by a different
route (e.g., the wrapped-Cauchy route of gap 2) and cites Schatte
only as diagnostic context — "pure addition fails for the Fourier
reasons Schatte identified; mixing fixes it for a different reason."

**Recommendation.** Route (b) is more honest if the proof actually
closes via wrapped Cauchy. The Schatte-as-Riesz rhetoric is elegant
but only worth carrying if the derivation works. If the wrapped-
Cauchy proof is what closes, say so and cite Schatte as the
diagnostic, not the mechanism.

---

## Pre-draft decision: Theorem 1's scope — resolved

Phase 3 biased-walk sim confirms L₁ → 0 for weights
(0.2, 0.2, 0.4, 0.2): no floor at 0.091, walkers reach the N = 10⁶
sampling-noise floor by t ≈ 2000 and stay there. **Theorem 1 can
cover all nondegenerate μ.**

The biased case is a corollary with a two-regime rate — fast
(ε-minorization) while walkers are in the active zone, algebraic
(Weyl rotation) after they escape. The symmetric case is a single-
regime stretched-exponential. Both convergences are to Leb_T.

Caveat: positive multiplicative drift is what phase 3 tested.
Negative drift (walkers recycle through origin, maintaining active-
zone contact) is not covered by the corollary and remains a
separate conjecture.

---

## Triage

| Gap | Status | Cost to close | Blocks draft? |
|-----|--------|---------------|---------------|
| 1. Operator definition | Open — invariant σ-finite measure not yet identified (Leb ⊗ counting is not it) | Research | Yes |
| 2. Contraction step | **Open — no working route.** Rosenthal small-set minorization withdrawn; transfer operator on AC densities is current candidate (Route 1') | Research | Yes |
| 3. Visit-rate vs. rate shape | **Resolved** — stretched exp, c ≈ 0.55 | — | — |
| 4. Biased-walk mechanism | **Resolved** — 2-regime convergence | — | — |
| 5. Group relation's role | Proof design | 1 proof step or rhetoric edit | No — can soften rhetoric |
| 6. Schatte bridge | Derivation or rewrite | 1–2 pages or cut the slogan | No — can cut |

**Minimum viable path to draft:** gaps 1 and 2 are both open and
interlinked — identifying the invariant σ-finite measure (gap 1)
is likely part of choosing the right function space for the
transfer operator (gap 2 Route 1'). No point dialing 5 or 6
until gap 2's framework is settled.

**Next concrete action:** work out Route 1' on paper. Choose a
function space / norm; check rotation-isometry; attempt per-visit
contraction. Do not draft more lemma text until this is settled
on paper. Drafting on an unsettled framework is how we got
GAP2-LEMMA withdrawn.
