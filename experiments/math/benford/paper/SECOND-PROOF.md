# SECOND-PROOF

Live gap list for the PNAS Brief Report, written against the T1b
theorem and the polynomial-tail induced-operator framework.
Successor to `paper/archive/FIRST-PROOF.md`, the T1a-era record.

This is a gap-list doc, not a proof. Each item is something that
has to close before draft text can be written. The damage-
assessment content that motivates the shift lives in
`paper/MESSES.md`; this doc names the work that remains under
the new commitments and stops there.

Priority: §3 (F1–F3) and §4 (identification) are load-bearing.
§1 is setup. §2 is a statement. §5 is description only. §6 and
§7 are bookkeeping against FIRST-PROOF.

---

## §0. Preamble

FIRST-PROOF was written against T1a (stretched-exp exp(−c√n) as
the asymptotic) and a Route 1' architecture with six sub-problems
(R1)–(R6). Two things changed: the target theorem moved to T1b
(asymptotic n^{−1/2}, stretched-exp survives only as an IC-
specific transient), and the rate-conversion step (R5) plus the
geometric-tail Feller argument (R2) are no longer appropriate
for the new target. The identification step (R6) also needs a
different handling because the natural return marginal at
R = {|E| ≤ 10} is not Leb_T.

SECOND-PROOF is a fork in the same family: same state space,
same induced operator T_R, same spectral-gap pressure, same
identification pressure. What changes is the rate mechanism
(polynomial-tail operator-renewal theory in place of a Laplace-
transform step) and the form of the identification argument
(walker-level π_T ν_n → Leb_T in place of a direct ν_R
identification). FIRST-PROOF is not edited in place because the
route shift and the target shift together reorganize too much
for line edits to remain legible.

---

## §1. State space and operator notation

Minimal setup, mostly reused from FIRST-PROOF §1.

**State space.** X = T × ℤ, where T = ℝ/ℤ is the log-mantissa
circle and ℤ is the exponent coordinate. σ-algebra B =
B(T) ⊗ 2^ℤ. The mantissa step under +1 depends on E, not just
m:

    m ↦ frac(log₁₀(10^m + 10^{−E})),

so the full state (m, E) is the right object; collapsing to T
alone loses information.

**Kernel.** The walk induces a Markov kernel K : X × B → [0, 1]
by averaging over the generator choice under the symmetric
measure. K(x, ·) is a 4-atom mixture (one atom per generator);
K(·, A) is B-measurable. Iterates K^n are kernel composition.

**TV distance.** For probability measures μ, ν on a common
measurable space (Y, G),

    ‖μ − ν‖_{TV} := sup_{A ∈ G} |μ(A) − ν(A)|
                  = ½ · ∫ |dμ − dν|,

equivalently ½ · ‖p − q‖_{L¹(λ)} when μ, ν both admit densities
p, q against a dominating measure λ. For T-marginals the
dominating measure is Leb_T.

**What the theorem targets.**

    φ(ν, n) := ‖π_T(ν K^n) − Leb_T‖_{TV},   ν a probability on X.

T1b asks for φ(ν, n) ∼ B(ν) · n^{−1/2} as n → ∞, for ν in the
hypothesis class stated in §2.

**The invariance question, deferred.** A full-space σ-finite
invariant measure on T × ℤ (most likely the pushforward of left
Haar on BS(1,2)) exists but need not be exhibited to prove the
asymptotic rate. Under Route 2 (§3), the load-bearing invariant
is a *probability* measure ν_R on compact R ⊂ X, supplied by
the spectral theory of the induced operator T_R.

**Caveat.** The σ-finite invariant is deferred, not necessarily
irrelevant. The walker-level identification argument sketched
in §4 may route through a harmonic / invariant-measure object
on T × ℤ. If it does, the deferred question re-enters.

---

## §2. The theorem to prove

SECOND-PROOF commits to the T1b shape:

**Asymptotic.** For any probability ν on X = T × ℤ satisfying
the hypotheses below,

    φ(ν, n) ∼ B(ν) · n^{−1/2}   as n → ∞,

with exponent α = 1/2 ν-universal and coefficient B(ν)
ν-dependent.

**Hypotheses.** Symmetric probability measure on the four
generators {a, a⁻¹, b, b⁻¹} of BS(1,2); ν absolutely continuous
with respect to the product Leb_T ⊗ (counting on ℤ) on a set of
full mass, or at minimum ν(T × {E}) ≪ Leb_T for each E;
ν(ℤ[1/2]) = 0 (the dyadic exceptional set); a logarithmic
moment on the E-marginal.

**Sharp-IC transient (not a proof target).** For ν concentrated
(sharp ICs), the observed pre-asymptotic L₁ trajectory includes
a stretched-exp transient A(ν) · exp(−c(ν)√n) that dominates
on n ≲ n*(ν) before crossing to the algebraic tail. This is
numerical description for the paper's Theorem 2 block, not a
proof obligation of SECOND-PROOF.

This statement replaces FIRST-PROOF's implicit T1a target
(φ(ν, n) ≤ C · exp(−c√n)).

---

## §3. Induced-return framework, read in the polynomial-tail regime

The induced-return object T_R on compact R is unchanged from
FIRST-PROOF §2 Route 1'. What changes is that the return-time
input P(τ_R > n) is heavy-tailed (polynomial, not geometric)
and should be fed into the operator-renewal framework for
induced operators with polynomial return-time tails rather than
into a standalone Laplace-transform step.

**Framework input/output.**

- *Input.* Induced operator T_R on compact R; spectral gap
  q < 1 on the zero-mean part in a suitable function space;
  return-time tail P(τ_R > n) ~ C/n^α with α ∈ (0, 1), under
  appropriate regularity conditions on the return-time density.
- *Output.* Correlation decay O(n^{−(1−α)}) for the full-
  process correlation function against the invariant measure,
  plus (via the correlation bound and standard TV ↔ correlation
  estimates) the TV-rate for marginals.

**Application to BS(1,2).** The measured τ_R tail on R =
{|E| ≤ 10} is consistent with α = 1/2 over two decades of n
(`sim/tau_R_tail_SUMMARY.md`). At α = 1/2 the framework
delivers O(n^{−1/2}), matching T1b's target.

**Walker excursion structure (three-sim consistency).** Three
measurements jointly pin the walker's excursion regime under
the paper kernel: `sim/tau_R_tail_SUMMARY.md` (τ_R tail at
slope −0.495, R² = 1.0000 on [50, 10⁴]);
`sim/laplace_diagnostic_SUMMARY.md` Part B (E-process mean ≈
0.16·√n, only 1.1% of walkers have E < 0 at n = 10⁴);
`sim/return_marginal_SUMMARY.md` (every one of 22.0M post-burn
returns at E = +10). These are mutually consistent: positive
E-drift coexists with a 1/√n return tail because the heavy
tail lets a small fraction of walkers sit far above R and drag
up the mean while the bulk still returns with the null-
recurrent 1/√n cadence; the "every return through E = +10"
pattern is what the drift asymmetry predicts (walker exits R
via 10 → 11 and re-enters via 11 → 10 through a⁻¹ with borrow,
which is also the single-step mechanism behind §4's arc
concentration). Jointly the three sims pin a specific
excursion regime that the polynomial-tail induced-operator
framework is written for.

**Framework choice at β = 1/2.** β = 1/2 is a boundary case in
the polynomial-tail literature. Of the three candidate papers
read:

- Young 1999 requires ∫R dm < ∞, which fails at β = 1/2 (tower
  mass diverges).
- Gouëzel 2004 requires β > 1 in Theorem 1.1.
- Melbourne–Terhesiu 2012 covers β ∈ (0, 1], with β = 1/2 at
  the boundary.

Melbourne–Terhesiu 2012 becomes the primary framework citation
for SECOND-PROOF; Young 1999, Gouëzel 2004, and Sarig 2002 stay
as supporting context. Instantiation detail lives in
`paper/F1-HYPO-PLAN.md` until that doc dissolves.

**Three-tier output at β = 1/2.** M–T's clean full-sequence
operator asymptotic (Theorem 2.1) is stated for β ∈ (1/2, 1].
At β = 1/2, M–T give:

1. *Default.* Theorem 2.2(a), an upper bound with a log
   correction: T_n ≪ n^{−1/2} log n under the natural reading
   of their slowly varying factor.
2. *Boundary fairness.* Theorem 2.3, a density-one subsequence
   limit and a positive-observable liminf at the clean n^{−1/2}
   scale.
3. *Clean extension.* M–T Remark 2.4 cites a private-
   communication result of Gouëzel that removes the log under
   the additional density-level condition μ(φ = n) =
   O(ℓ(n) · n^{−3/2}). One derivative stronger than the
   survival-function bound — see F2 for the empirical check.

Option 3 is the cleanest paper-grade statement; Option 1 is
the fallback if the density condition cannot be verified.

**Markov-to-deterministic translation.** M–T is phrased for
deterministic dynamics f : Y → Y with a Perron–Frobenius
operator. BS(1,2) is a Markov kernel. The primary plan
(Option A) constructs the Bernoulli skew product
F : Ω × (T × ℤ) → Ω × (T × ℤ), F(ω, x) = (σω, ω_0 · x), with
Ω = {a, a⁻¹, b, b⁻¹}^ℕ under the symmetric product measure.
F is deterministic and its walker-marginal transfer operator
reproduces K. The skew product *translates* the dynamics; it
does not by itself supply M–T's (H1)(H2). The fallback
(Option B) leaves Markov-chain language in place and uses
polynomial ergodicity for Markov chains à la Tuominen–Tweedie /
Meyn–Tweedie; different function-space output, different
citation family; flagged if the M–T route collapses at (GM-1).

Three sub-items carry the proof work.

### (F1) Regularity of T_R in the polynomial-tail framework

Melbourne–Terhesiu 2012 phrases its operator-renewal output
through two abstract hypotheses (M–T §2):

- **(H1)** A Banach space 𝓑 ⊂ L^∞(Y), containing constants,
  with |v|_∞ ≤ ‖v‖, such that the renewal operators R_n : 𝓑 →
  𝓑 satisfy ‖R_n‖ ≤ C · μ(φ = n) for all n ≥ 1.
- **(H2)** Spectral conditions on the generating renewal
  operator R(z): eigenvalue 1 simple and isolated at z = 1, and
  1 not in the spectrum of R(z) for z ∈ 𝔻̄ \ {1}.

M–T §11 gives two worked example classes for verifying
(H1)(H2):

- **§11.2 Gibbs–Markov first return.** Banach space Lip(Y, d_τ)
  under the dynamical metric d_τ(x, y) = τ^{s(x, y)}. Requires
  countable Markov partition of Y under F (GM-1), piecewise
  Lipschitz distortion (GM-3), and big images inf_a μ(Fa) > 0
  (GM-2). First-choice template for BS(1,2) because the
  excursion structure is naturally symbolic.
- **§11.3 AFN maps.** Banach space BV(Y). Non-Markovian
  interval maps with indifferent fixed points. Fallback if
  §11.2 fails on branch / carry discontinuities.

**Load-bearing risk.** (GM-1) is the upstream structural
question: under F on the skew product Y = Ω × R, does the
natural excursion-type partition (or a natural refinement)
satisfy the Markov property? On our current reading, F smears
excursion-type cells across a continuum of return states rather
than mapping onto unions of cells — see `paper/MESSES.md`
Mess #6. Mess #6 carries the falsification protocol (small-
example calculation on the minimal two-step excursion). Until
that check runs, this sub-item is aspirational: the paper has
no path to theorem if (GM-1) is confirmed and no refinement or
fallback repairs it.

If (GM-1) falsifies (Mess #6 wrong on the example, and the
behavior generalizes), (GM-3) becomes the next check — tight
enough for the Lasota–Yorke / Hennion argument under d_τ.
Candidate Banach spaces inherit from FIRST-PROOF's norm
discussion: Lip(Y, d_τ) primary by analogy with §11.2; BV
fallback under §11.3; Fourier-weighted L² on the mantissa as
an alternative in concert with F3.

**Open.** Main research item under SECOND-PROOF; structural
risk tracked in Mess #6.

### (F2) Uniform-in-x return-tail bound

The measured τ_R tail at 1/√n on n ∈ [50, 10⁴] is for a single
IC (x₀ = √2 at E₀ = 10). The framework needs this tail estimate
to hold uniformly over starting points in R:

    sup_{x ∈ R}  P_x(τ_R > n) ≤ C · n^{−1/2}   for n large.

The physical picture is that τ_R is the first re-entry time of
a zero-drift-with-bounded-increments walk on ℤ (the E-process),
started from a boundary state. The E-process is not autonomous
— b-step E-increments depend on m — but its increment
distribution is bounded uniformly in m under the symmetric
measure. The classical null-recurrent tail bound extends under
a coupling that controls the m-dependent part of the increments
as a perturbation.

**Secondary: density-level upper envelope (optional, removes
the log).** Under M–T Remark 2.4 + Gouëzel's private-
communication extension, the clean β = 1/2 renewal-operator
asymptotic (without the log correction in Theorem 2.2(a))
requires the extra density-level bound

    μ(φ = n) = O(ℓ(n) · n^{−3/2}).

This is an upper-envelope condition on the return-time point
mass, one derivative stronger than the survival-function bound
above. Empirically verifiable by a sim that measures the point
mass of τ_R at each n rather than the survival function. Not
load-bearing if the paper accepts n^{−1/2} log n at the
renewal-operator level; load-bearing if we want the clean
n^{−1/2} statement there.

**Open.** Primary tail bound: small lemma, not huge but not
free, Feller-style argument. Density-level upper envelope: sim
check first, then decide whether to make it load-bearing.

### (F3) Spectral gap for T_R on the zero-mean part

Same content as FIRST-PROOF R4. Target: q < 1 such that

    ‖T_R f − ν_R(f) · 𝟙‖_Z ≤ q · ‖f − ν_R(f) · 𝟙‖_Z

for f in the chosen function space Z. Function-space choice is
the same as in FIRST-PROOF: Fourier-weighted L² on the zero-
mean part (first choice), BV (fallback). The mantissa's
ε-coordinate identity from BINADE-WHITECAPS §§7–8 enters here
as the Fourier content of the b-step kernel; it underpins the
rate at which T_R damps non-constant modes on T.

**Empirical anchor.** `sim/b3_SUMMARY.md` measures the
spectral radius of T_R's mode-coupling matrix K̂ at ρ(K̂) =
0.924 from 40M excursions, classified as injection-dominated.
Numerical bound ρ < 1 with room; the analytic target must be
tight enough that the eventual q is strictly below 1 with an
explicit constant.

Uniqueness of ν_R is an output of this step (irreducibility
+ gap ⇒ unique invariant); existence comes from F1 via a
Krylov–Bogolyubov-style argument on compact R once the Feller
regularity is in place.

**Open.** Analytic statement outstanding. B3 supports but does
not substitute for the proof.

---

## §4. Target identification

The hardest item under SECOND-PROOF. At the natural
R = {|E| ≤ 10}, the pooled post-burn return marginal σ̃ is
concentrated on the arc [1 − log₁₀ 2, 1) × {E = +10}, with
L₁(σ̃, Leb_T) = 1.40 (260× the multinomial noise floor) and
order-unity low-r Fourier coefficients (`sim/return_marginal_SUMMARY.md`).
The arc concentration has a clean single-step arithmetic
mechanism: at E₀ = 10 the only channel from E = 11 back to
E = 10 is a⁻¹ with borrow, which requires m_pre < log₁₀ 2 and
deterministically maps m_pre → m_pre + (1 − log₁₀ 2). So the
identification step π_T ν_R = Leb_T that FIRST-PROOF R6
sketched does not close at this R by a rotation-invariance /
Weyl argument.

This is the old R6 pressure point and SECOND-PROOF's treatment
of it has to move off the rotation-invariance sketch.

### Main route: walker-level identification

The walker-level identification target is

    π_T(ν K^n) − Leb_T → 0   in TV as n → ∞.

This bypasses ν_R: it identifies the limit of the time-evolved
mantissa marginal directly, without asking the whole argument
to run through the invariant law of the induced operator.

The sim evidence is supportive: across the IC panel
(M1 √2, M3 IC (a) (b) (c), M4 on √2, t1b_unit_ball's 13 ICs,
Run 1/2/3), every IC tested reaches the vicinity of the
multinomial L₁ null floor for the run's N. This is direct
evidence that π_T ν_n approaches Leb_T at the observable
horizon, regardless of what ν_R is.

Candidate analytic routes:

- **Coupling.** Couple two walks with initial conditions
  ν and ν', arrange that their mantissa marginals merge on the
  same horizon the framework's correlation bound delivers. TV
  contraction under the full kernel K against a coupled partner
  is the natural object; rotation-isometry of TV on excursions
  (FIRST-PROOF's structural observation) is available as a
  factor.
- **Harmonic / invariant-density argument on T × ℤ.** A
  σ-finite invariant measure on T × ℤ whose T-marginal is Leb_T
  (the pushforward of left Haar on BS(1,2) is the obvious
  candidate), combined with a positive-recurrence-adjacent
  convergence theorem, identifies the limiting T-marginal of
  ν K^n. This is the route that pulls the deferred gap-1
  σ-finite invariant back in.
- **Fourier argument on the mantissa marginal.** Show that each
  nonzero T-Fourier mode of π_T ν_n is damped to zero. The
  b-step kernel's Fourier content (ε-coordinate identity from
  BINADE-WHITECAPS) damps low-depth modes explicitly; the
  a-step rotates by ±log₁₀ 2, an irrational rotation. A
  uniform Fourier bound on (πE composed with the kernel)
  against Leb_T would suffice. Overlaps with F3's norm choice;
  the two may share a single argument.

No one of these is clearly cheapest without more work. The plan
is to carry the route choice open until a candidate argument
can actually be written down.

### Backup note: vary R

The σ̃ arc mechanism at E₀ = 10 is specifically that the b⁻¹
channel has width O(10⁻¹¹) and is numerically irrelevant,
leaving a⁻¹-with-borrow as the sole return step. At smaller
E₀ the b⁻¹ channel widens and the return-state distribution
could, in principle, stop being arc-concentrated. Untested.

The trade-off is that smaller R makes F1 (Feller-type
regularity) and F3 (spectral gap) harder, because the
excursion structure gets shorter and less clean. If the
walker-level route in the main section does not close, an
E₀-sweep sim would be the first probe of whether varying R
rescues the ν_R-based identification.

**Open.** Main walker-level route is the primary plan; vary-R
is a backup note.

---

## §5. Transient description (not a theorem claim)

The IC-specific stretched-exp transient A(ν) · exp(−c(ν)√n)
is not a theorem obligation of SECOND-PROOF. It is a numerical
description for the paper's Theorem 2 block; values for c(ν)
across the IC panel are tabulated in
`sim/t1b_unit_ball_SUMMARY.md` and `paper/T1B-EVIDENCE.md`.

The transient mechanism is open. `sim/conditional_decay_SUMMARY.md`
rules out the cleanest single-mechanism candidate (pure a-step
Diophantine structure on log₁₀ 2) by a factor of 55× in the
rate constant; whatever produces the transient involves active
b-step m-mixing. Not load-bearing for T1b.

---

## §6. What's dropped from FIRST-PROOF

Explicit delta list so the fork is navigable.

- **R2 geometric-tail Feller argument.** Dropped. The
  polynomial-tail framework (§3) absorbs the operator-
  legitimacy question; Feller regularity becomes an instance of
  F1's framework-hypothesis check rather than an original
  lemma.
- **R5 Laplace-transform rate conversion.** Dropped. The T1b
  target is n^{−1/2}, which the framework delivers natively
  from the α = 1/2 tail exponent. No conversion step is needed.
- **R6 rotation-invariance sketch for π_T ν_R = Leb_T.**
  Dropped. §4's walker-level route replaces it as the main
  identification argument; the vary-R backup note retains a
  narrow path for a ν_R-based identification if the walker-
  level route doesn't close.
- **Biased-walk mechanism section (old gap 4).** Dropped from
  the proof gaps entirely. Robustness evidence, not theorem
  architecture; lives in `paper/ROBUSTNESS-ATLAS.md`.
- **Group-relation's role (old gap 5).** Archival; narrowed
  kicker wording in PNAS-PLAN §6 is stable.
- **Schatte bridge (old gap 6).** Archival; resolved as
  diagnostic only in PNAS-PLAN §6 movement A.

---

## §7. What's carried forward

- State space and operator setup (§1 here, FIRST-PROOF §1
  there), including the deferred-invariant caveat.
- Spectral-gap pressure on T_R (F3 here, R4 there). Function-
  space choice is the same; B3's empirical support carries
  over.
- The structural observation that rotation on T is TV-isometric
  against Leb_T on excursions. Still useful in §4's coupling
  route.
- Transient shape as numerical description. FIRST-PROOF gap 3
  claimed it as the asymptotic; under T1b it is a transient and
  lives in §5 here.

---

## §8. Triage

| Item | Status | Comment |
|------|--------|---------|
| §1 setup | Minimal setup only | Same as FIRST-PROOF |
| §2 theorem statement | T1b committed | Stated explicitly; hypotheses include ν(ℤ[1/2]) = 0 and symmetric measure |
| §3 (F1) framework regularity | Open, main technical work | Citation-bounded, but instantiating the hypotheses for BS(1,2) T_R is the main research step |
| §3 (F2) uniform τ_R tail | Open, small lemma | Sim is IC-specific; uniform-in-x extension needed |
| §3 (F3) spectral gap | Open, same as FIRST-PROOF R4 | B3 empirical support; analytic target tight |
| §4 identification | Open, heaviest pressure | Main walker-level route; vary-R backup note |
| §5 transient | Description only | Not a theorem-load-bearing gap |

**Minimum viable path to draft:** F3 → F2 → F1 → §4
walker-level identification. Any one of F1, F3, or §4 failing
breaks the theorem. F2 is small but on the critical path.

**Known empirical limits.** Caveats not load-bearing
individually but worth cataloguing for paper-writing honesty:

- **F3 tightness.** B3's ρ(K̂) = 0.924 is numerically plausible
  but wide — an analytic proof giving only ρ < 0.99 would not
  suffice for F3's target q. The bound has to beat 0.924 by a
  margin that survives the product bound inside the framework.
- **α = 1/2 on the √2 IC.** M4 at n = 3000 shows α_local
  drifting but not stabilized; T1b's asymptotic on √2 is an
  extrapolation, not a direct measurement. Direct resolution
  would need the longer-horizon beef-box Run 1.
- **Smooth-IC universality.** `sim/t1b_unit_ball_SUMMARY.md`
  Run 3 (smooth Gaussian ν) reaches the null floor too quickly
  to measure α; α_∞ = 1/2 under smooth ICs is inferred from
  the IC panel, not directly measured.
- **BS(1, p) for p ≠ 2.** All sims are on BS(1, 2). Nothing in
  the polynomial-tail framework or in §4's identification
  pressure depends on p = 2 specifically, but the sim corpus
  cannot certify the generalization either way.
- **F2 uniformity in x ∈ R.** `sim/tau_R_tail_SUMMARY.md`
  measures one IC (√2); the uniform-in-x tail estimate that the
  framework requires is not directly tested. Explicit in §3
  (F2); noted here for completeness.

---

## §9. Next concrete actions

1. **(F3) spectral gap.** Pick the function space (Fourier-
   weighted L² first), prove q < 1 on the zero-mean part,
   target q tight enough to survive the product bound inside
   the framework. B3 is the empirical calibration.
2. **(F2) uniform tail.** Show sup_{x ∈ R} P_x(τ_R > n) ≲
   C · n^{−1/2} by classical random-walk analysis with a
   coupling that handles the m-dependence of E-increments.
3. **(F1) framework regularity.** Instantiate the operator-
   renewal hypotheses (Doeblin / spectral / Lasota–Yorke /
   Banach-space regularity) for T_R on the chosen function
   space. Pick the framework paper after the match is clear.
4. **§4 walker-level identification.** Prove π_T ν_n → Leb_T
   directly. Try coupling first; Fourier and harmonic routes in
   reserve. The vary-R backup note carries only if the walker-
   level argument doesn't close.

Do not draft lemma text until F3 and the §4 route are both
settled on paper. The earlier GAP2-LEMMA withdrawal under
FIRST-PROOF came from drafting ahead of the framework; the
same caution applies here.

---

## References

### Paper-side

- `paper/archive/FIRST-PROOF.md` — T1a-era predecessor, archived.
- `paper/MESSES.md` — damage assessment for the R2/R5/R6
  pressure points and for the (GM-1) framework question under
  M–T §11.2 (Mess #6).
- `paper/F1-HYPO-PLAN.md` — live working doc for the F1
  instantiation under M–T 2012. Dissolves into §3 (F1) once
  Mess #6 (the Gibbs–Markov question) resolves.
- `paper/T1B-EVIDENCE.md` — paper-side synthesis of the T1b
  empirical case.
- `paper/PNAS-PLAN.md` — main-draft skeleton, T1b-synced.
- `paper/ROBUSTNESS-ATLAS.md` — robustness atlas (§7 of
  PNAS-PLAN); biased-walk and base-change evidence that was
  formerly FIRST-PROOF gap 4.

### Sim-side anchors

- `sim/tau_R_tail_SUMMARY.md` — 1/√n τ_R tail measurement
  (F2 empirical anchor).
- `sim/return_marginal_SUMMARY.md` — σ̃ arc concentration
  at E₀ = 10 (§4 empirical target).
- `sim/b3_SUMMARY.md` — ρ(K̂) = 0.924 (F3 empirical anchor).
- `sim/laplace_diagnostic_SUMMARY.md` — confirms Laplace
  obstruction on SRW; falsifies transportability to BS(1,2).
- `sim/T1B-EVIDENCE-MAP.md` — clause-by-clause evidence for
  T1b's asymptotic.

### Framework references (for §3)

- Melbourne & Terhesiu 2012, operator-renewal theory for
  infinite-measure dynamical systems. **Primary framework
  citation.** β = 1/2 is a boundary case within their range;
  Theorem 2.2(a) gives the default n^{−1/2} log n bound,
  Theorem 2.3 gives density-one-subsequence + liminf at clean
  n^{−1/2}, and Remark 2.4 cites a private-communication
  extension of Gouëzel that removes the log under the F2
  density condition.
- Gouëzel 2004, sharp polynomial bounds under polynomial
  return-time tail. Supporting context only; Theorem 1.1
  requires β > 1 and does not apply at β = 1/2.
- Sarig 2002, subexponential decay of correlations.
  Supporting context; predecessor whose results M–T and
  Gouëzel generalize.
- Young 1999, "Recurrence times and rates of mixing," Israel
  J. Math. 110. Supporting context only; requires ∫R dm < ∞,
  which fails at β = 1/2.
