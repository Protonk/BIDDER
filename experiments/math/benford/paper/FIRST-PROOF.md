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

**Status:** open. The load-bearing proof move. Route choice gated by
gap 3.

**The problem.** Produce a quantitative contraction bound on the
transfer operator (defined in gap 1) with the rate controlled by ε.
The claim gate has already retreated to λ ≥ f(ε, μ) > 0, so we need
ε > 0 on the interior to produce a contraction in some usable norm —
not exact identification. BINADE-WHITECAPS §§7–8 gives ‖ε‖²_{L²} via
Parseval, but that's the static defect under a coordinate change,
not a transfer-operator bound. The bridge from the static identity
to a dynamical contraction is what this gap asks for.

**What gap 1 supplies, and what remains external.** The operator
lives on L²(T × ℤ, μ) with μ = Leb ⊗ counting (σ-finite). The Markov
kernel K(x, A) is measurable (Tao Def 1.4.32) and acts by
(Kf)(x) = ∫ f(y) K(x, dy). Total-variation distance, minorization
inequalities, and Fourier decay on T are all well-typed in this
framework. The contraction *bound* is not — for that we go external
(Rosenthal, Meyn-Tweedie, or direct Fourier estimates on T).

**Route 1 (primary): Doeblin / minorization.** After k₀ steps, the
kernel satisfies a minorization on a small set R ⊂ X. This route
targets exactly the lower bound we need and admits a constructive
minorization constant from BINADE-WHITECAPS. Specifics from
Rosenthal, *Minorization Conditions and Convergence Rates for Markov
Chain Monte Carlo*, JASA 90 (1995), 558–566
(`sources/minor-markov.pdf`). (Rosenthal writes the minorization
constant as ε; we rename it **β** to avoid clash with the function
ε(m).)

- **Small-set minorization** (cond. (∗), §2, p. 4):
  K^{k₀}(x, ·) ≥ β · Q(·) for x ∈ R = {(m, E) : |E| ≤ E₀}. Whole-
  space Doeblin (Prop. 2, p. 5) would require uniform ergodicity,
  almost certainly false on T × ℤ.
- **TV bound** (Theorem 1, p. 4–5):
  ‖L(X^{(k)}) − L(Y^{(k)})‖_var ≤ (1−β)^{[j/k₀]} + P(N_{k−k₀+1} < j),
  with N_k counting joint returns of a coupled pair to R × R. Two
  terms: coupling probability once inside R, and the tail bound on
  how often the pair sits there jointly.
- **Constructive β** (Lemma 6(ii), p. 9): letting k^{k₀}(x, y) be
  the density of K^{k₀}(x, ·) with respect to the reference measure
  μ = Leb ⊗ counting (available once the b-step's smoothing on T
  gives absolute continuity), β = ∫_X (inf_{x∈R} k^{k₀}(x, y)) dμ(y).
  Directly computable from BINADE-WHITECAPS §§7–8.
- **No drift shortcut.** Theorem 12 (p. 15) uses
  E[V(X^{(1)})|x] ≤ λV(x) + b with λ < 1 to control return times;
  our exponent walk has no such drift (symmetric null-recurrent,
  biased transient-away). Return-time control must come from direct
  bounds — gap 3's simulation, or Cuno-Sava-Huss statistics.
- **σ-finite adaptation.** Rosenthal assumes a stationary
  probability π; we have σ-finite μ. The projection to the mantissa
  marginal is load-bearing here: because the b-step is E-dependent,
  the marginal kernel on T is time-dependent, obtained by averaging
  K against the coupled pair's current E-distribution. The small-set
  minorization survives this averaging — if K^{k₀}(x, ·) ≥ β · Q(·)
  holds for *all* x in R = {|E| ≤ E₀}, the E-averaged marginal bound
  inherits β regardless of how E-weight is distributed within R. The
  coupling's coin-flip cares about β, not full-space normalization.

**Route 2 (backup): Wrapped-Cauchy comparison.** Dominate the
averaged +1 kernel by a wrapped Cauchy of parameter γ = γ(ε) in some
operator norm. Convolution stability gives exp(−2πγn). Harder than
minorization — commits to choosing both the norm and the domination
inequality — but available if the minorization return-time bound
fails.

**Route 3 (unlikely): Wrapped-Cauchy identity.** The averaged +1
kernel actually *is* wrapped Cauchy with parameter γ = γ(ε). Noted
for completeness; wrapped Cauchy is too rigid a family for this to
hold generically.

**What closure looks like.** A lemma stating the contraction bound,
rate as a computable functional of ε (Doeblin constant, Fourier
tail, or Parseval). **Try route 1 first.** Gap 3's sim decides
whether to stay there: stretched exponential ⇒ Rosenthal-via-
coupling is the route; exponential ⇒ coupling can't reach the rate
and we fall back to route 2 or to direct Fourier decay on the
mantissa marginal. Either outcome keeps ε in control of the rate.

---

## 3. Visit-rate consistency with observed exponential rate

**Status:** open. The quietest crisis, and the one that decides what
gap 2 has to close.

**The problem.** Two predictions, same data, can't both be right.

- **Theory predicts stretched exponential.** The symmetric exponent
  walk is driftless ±1 on ℤ; its local time at zero grows as √n
  (P(S_n = 0) ∼ √(2/πn)). If contraction factors through visits to
  the low-depth zone {|E| ≤ E₀}, t steps give ∼√t contractions and
  TV mixing goes as exp(−c√t). Rosenthal 1995
  (`sources/minor-markov.pdf`), Theorem 1 (p. 4–5), makes this
  mechanical: the coupling bound (1−β)^{[j/k₀]} + P(N_{k−k₀+1} < j)
  with N_k counting joint returns of two independent copies to
  R × R (β the Rosenthal minorization constant, see gap 2) forces
  j ∼ √k and yields TV ≲ exp(−c√k). Every coupling-with-independent-
  partner argument in this framework gives stretched exponential.
- **Simulation shows exponential.** `bs12_rate.png` is a clean
  straight line on lin-log over t ∈ [20, 100] with R² = 0.99 and
  λ ≈ 0.035. No visible curvature.

Both functions are locally linear on short intervals, so a fit over
[20, 100] can't distinguish them.

**The action.** Extend the simulation to t ∈ [10³, 10⁵] with enough
walkers to resolve L₁ below 10⁻³ (≈10⁷ walkers for K = 9 digit bins,
whose empirical floor is √(K/N)). Produce two panels:

- log(L₁) vs. t — straight iff exp(−λt).
- log(L₁) vs. √t — straight iff exp(−c√t).

Whichever stays linear out to 10⁵ is the true asymptotic rate.

**What the answer decides.**

- **If log(L₁) vs. √t is straight.** Theorem 1's rate becomes
  stretched exponential. Gap 2 closes via Rosenthal (§2's
  minorization specifics).
- **If log(L₁) vs. t is straight.** Rosenthal-via-coupling cannot
  reproduce the rate. Gap 2 closes via a route that bypasses
  coupling with a partner chain — most likely direct Fourier decay
  on the single chain's mantissa marginal, using the BINADE-
  WHITECAPS §8 coefficients of ε.

Either outcome is actionable and unblocks drafting.

**Why this is first.** One night of simulation, and it tells us which
rate the theorem states and which route gap 2 takes.

---

## 4. Biased-walk convergence mechanism

**Status:** open. `PNAS-PLAN.md` lines 322–328 acknowledges but does
not settle.

**The problem.** For asymmetric measures (δ ≠ 0), the exponent walk
is transient. Cuno & Sava-Huss give sublinear speed but eventual
escape to the boundary. The walker visits any finite active zone
only finitely often — say N_active total visits almost surely.

If the contraction per visit is bounded below by some c_ε > 0 (via
gap 2), then after N_active visits the distribution is within
(1 − c_ε)^{N_active} of the contractive limit — a **finite** amount
of mixing, not exponential-to-uniform forever.

But the biased-walk simulation (weights 0.2/0.2/0.4/0.2, walkers at
10^1200) shows final L₁ = 0.091. Is that the floor, or still
decaying?

**What closure looks like.**

- Either: prove L₁ → 0 for any nondegenerate μ (even when exponent
  transient) via a mechanism that doesn't require infinite active-zone
  visits. E.g., the rotation by log₁₀ 2 under a-steps continues
  forever and is ergodic; the finite mixing from b-steps at low depth
  gets us close to uniform, and the ergodic rotation maintains it.
- Or: accept that biased walks converge only to a Benford-close
  distribution, and state Theorem 1 for symmetric measures, with
  robustness to bias as a quantitative corollary (L₁ ≤ ε_bias) rather
  than full convergence.

**Note.** The simulation at L₁ = 0.091 after 10^1200 steps is
suggestive of a floor, not continued decay. Confirm with a
longer-horizon or more-walkers run before committing Theorem 1
to cover biased μ.

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

## Pre-draft decision: Theorem 1's scope

Not a gap — a decision. The plan's Theorem 1 is stated "for any
nondegenerate probability measure μ." Gap 4 suggests biased walks may
converge to a Benford-*close* distribution with a positive L¹ floor
rather than to Benford exactly. The biased-walk sim at L₁ = 0.091
after 10^1200 steps is consistent with a floor.

Before drafting, we commit to one of:

- **Full scope.** Theorem 1 covers all nondegenerate μ. Requires
  proving L¹ → 0 in the biased case, which is what gap 4 asks for.
- **Symmetric scope.** Theorem 1 states convergence only for symmetric
  (driftless) μ. Biased case becomes a quantitative corollary
  (L¹ ≤ ε_bias). Cleaner, more honest, costs us the generality the
  plan currently claims.

This is independent of whether gaps 1–3 close. Resolve it after the
gap-3 simulation — the extended-horizon biased run will tell us
whether the floor is real.

---

## Triage

| Gap | Type | Cost to close | Blocks draft? |
|-----|------|---------------|---------------|
| 1. Operator definition | Bookkeeping | ~1 page | Yes |
| 2. Contraction step | Analytical | Varies by route | Yes |
| 3. Visit-rate vs. exponential | Simulation + analysis | 1 night sim + reconcile | Yes |
| 4. Biased-walk mechanism | Analytical + sim | ~1 page, or narrow theorem | Depends on scope decision above |
| 5. Group relation's role | Proof design | 1 proof step or rhetoric edit | No — can soften rhetoric |
| 6. Schatte bridge | Derivation or rewrite | 1–2 pages or cut the slogan | No — can cut |

**Minimum viable path to draft:** close 1, 2, 3. Make the scope
decision on Theorem 1. Dial 5 and 6 to match whatever route 2 takes.

**First concrete action:** run the extended-horizon simulation for
gap 3. Cheapest, most informative, and tells us whether gaps 1–2 are
targeting the right theorem statement — and, with a biased run
alongside, feeds directly into the Theorem 1 scope decision.
