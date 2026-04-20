# MESSES

Problems that threaten the proof architecture. Current live
target is SECOND-PROOF §3 + §4 under T1b; the historical framing
below originates against the archived FIRST-PROOF §2 Route 1'
sub-problems (R1)–(R6), with per-mess "T1b reconciliation"
updates absorbing the shift where relevant.

Not repair proposals — damage assessments.

---

## Mess #1: Laplace's revenge

### The claim

FIRST-PROOF §2 (R5) asks for

    E[q^{N_n}] ≤ C · exp(−c√n)

where q < 1 is the spectral gap from (R4) and N_n counts returns
to R by time n. This is the step that converts per-return
contraction into law-level stretched-exponential decay. Without
it, (R4) gives a spectral gap that never reaches the theorem.

### The computation

For simple symmetric random walk on ℤ, the local time at 0 has
generating function

    G(z) = Σ_{n≥0} E[q^{L_n}] z^n
         = q√(1 − z²) / ((1 − z)(1 − q + q√(1 − z²))).

Near z = 1, set δ = 1 − z. Then √(1 − z²) ≈ √(2δ), and

    G(z) ≈ q√2 / ((1 − q) · √δ).

By transfer lemma, [z^n](1 − z)^{−1/2} ~ 1/√(πn). Therefore

    E[q^{L_n}] ~ q√2 / ((1 − q)√(πn)).

This is **algebraic**: O(1/√n), not exp(−c√n).

The BS(1,2) walk's E-process is not simple SRW, but it is a
zero-drift martingale with bounded increments, so its local-time
statistics at {|E| ≤ E₀} are in the same universality class.
The 1/√n rate is structural and survives the coupling.

### Why the expectation and the typical value disagree

The typical value of L_n is ~ c√n (local CLT). So the typical
value of q^{L_n} is q^{c√n} = exp(−|log q| · c · √n), which is
stretched-exponential. But E[q^{L_n}] is not controlled by the
typical value — it is controlled by the lower tail.

The return count N_n for a null-recurrent walk has a
Mittag-Leffler / arcsine-type limit distribution. In particular,

    P(N_n ≤ a) ~ C · a / √n

for bounded a. On the event N_n ≤ 1, we have q^{N_n} ≈ q, a
constant. So

    E[q^{N_n}] ≥ P(N_n ≤ 1) · q ≈ Cq / √n.

The rare trajectories where the walker barely returns to R
contribute O(1/√n) to the expectation, and this dominates the
stretched-exponential contribution from typical trajectories.
No tightening of constants changes this — the lower bound
matches the upper bound in order.

### What this breaks

The proof architecture in FIRST-PROOF §2 Route 1' is:

    (R4) T_R has spectral gap q < 1
    (R5) E[q^{N_n}] ≤ C exp(−c√n)
    ∴    φ(ν, n) ≤ C′ exp(−c√n)

(R5) is false. Therefore the route, as framed, does not produce
stretched-exponential decay. It produces an honest upper bound,
but that bound is O(1/√n) — algebraic.

This is not a matter of strengthening the estimate. The Laplace
transform E[q^{N_n}] for any fixed q < 1 decays as 1/√n when the
return-time distribution is in the domain of attraction of a
stable law with index 1/2. This is a theorem, not an artifact.

### What this does not break

The simulation is fine. The measured stretched-exponential
c ≈ 0.55 at N = 10⁷ stands on its own empirical merits. The
issue is with the proof framework, not the phenomenon.

The per-return spectral gap (R4) is not itself wrong — if it
can be proved, T_R does contract. What fails is the mechanism
for converting per-return contraction into a law-level rate.
The Laplace-transform route was supposed to be that mechanism,
and it gives 1/√n, not exp(−c√n).

### The structural point

The per-return framework treats the walk as a renewal process:
wait for a return to R, apply a contraction, repeat. The rate
is then q^{N_n}, a product of N_n identical factors. But N_n is
random with a heavy-tailed distribution (Mittag-Leffler), and
the expectation of a geometric function of a heavy-tailed
random variable is controlled by the tail, not the bulk.

Compare with the (withdrawn) per-step framework in GAP2-LEMMA,
which used

    φ(ν_n) ≤ ∏_{k=0}^{n-1} (1 − β · ν_k(R)) · φ(ν)
           ≤ exp(−β · E[L_n])
           ≤ exp(−β c_R √n).

This gives stretched-exponential because the contraction factors
enter *additively* in the exponent (via log(1−x) ≤ −x), and the
sum Σ ν_k(R) = E[L_n] is the *mean* local time, which is c√n.
The mean is insensitive to the lower tail of N_n because it
aggregates linearly.

The per-return framework converts the sum into a product
(q^{N_n} = exp(N_n log q)), then takes the expectation of the
product. The per-step framework takes the log first
(−β Σ ν_k(R)), then exponentiates the expectation. These give
different answers whenever N_n has large variance, which it does.

GAP2-LEMMA's per-step Claim (*) is false for other reasons
(TV-to-Leb_T is not monotone step-to-step). But its *iterative
structure* — sum in the exponent, not product under the
expectation — is the one that produces stretched-exponential.
Route 1' adopted the induced-return operator to fix Claim (*)'s
norm problem, and in doing so moved to the per-return framework,
which introduced the Laplace-transform problem.

### The depth of the problem

The standard literature on mixing rates for infinite-measure
dynamical systems (Melbourne & Terhesiu 2012, Gouëzel 2004,
Sarig 2002) gives polynomial correlation decay for systems
where the return time to a finite-measure set has tail
P(τ > n) ~ C/n^α. For α = 1/2 (our case: null-recurrent walk
on ℤ), the predicted mixing rate is O(1/n^{1/2}).

If these results apply to our system — and they appear to,
since the induced return operator on compact R with a spectral
gap and a return-time tail ~ C/n^{3/2} (so P(τ > n) ~ C/n^{1/2})
is exactly the setup they treat — then the correct rate is
algebraic, and the simulated stretched-exponential is either:

(a) a finite-time transient that has not yet relaxed to the
    asymptotic algebraic regime, or

(b) produced by a mechanism not captured by the per-return
    spectral-gap framework.

Option (a) requires explaining why exp(−0.55√n) fits the data
so well over three decades (n ∈ [20, 120]) with R² = 0.9985
while 1/√n does not (the residuals carry systematic curvature —
this is what gap 3's phase 1 tested). Option (b) requires a
different proof architecture.

### Status

Open. This is a framing-level problem, not a gap inside a
working framework. The six sub-problems (R1)–(R6) were designed
under the assumption that (R5) would deliver the rate, and that
assumption is false.

### Update (2026-04-19): empirical evidence + T1b reconciliation

Three relevant sims; the last two significantly soften this
Mess's diagnosis once T1b is the target.

**SRW baseline validation** (`sim/laplace_diagnostic_SUMMARY.md`).
Measured E[q^{L_n}] on simple ±1 walk on ℤ matches the
closed-form prediction q√2 / ((1 − q)√(πn)) to within 0.2% at
n = 10⁴, for q ∈ {0.3, 0.5, 0.7}. Slope of log E[q^{L_n}] vs
log n is −0.500 ± 0.005. The Laplace-transform obstruction —
that null-recurrent Laplace averages decay as 1/√n — is
quantitatively verified on the textbook case. The computation
in this Mess is correct for SRW.

**BS(1,2) does not match the same universality class**
(`sim/laplace_diagnostic_SUMMARY.md`). The E-process has mean
growing as ~0.16 · √n (positive drift, _not_ zero-drift
martingale). The local time L_n grows as ~n, not √n — walkers
spend a macroscopic fraction of calendar time in R. E[q^{L_n}]
on BS(1,2) does not follow 1/√n: for small q it decays fast
initially then plateaus. The claim "the 1/√n rate is structural
and survives the coupling" from this Mess's original text is
not empirically supported for BS(1,2).

**Transient stretched-exp is not a-step-alone Diophantine**
(`sim/conditional_decay_SUMMARY.md`). A direct analytic test of
the "pure a-walk irrational-rotation" hypothesis for the
measured transient gave best-fit γ = 0.15 (not 0.5) and, at
fixed γ = 0.5, c = 0.009 vs the paper's measured c ≈ 0.498
(current M1 value; the "0.55" in the original text of this
Mess is stale). The transient mechanism involves b-step's
active contribution to m-mixing at small |x|, not a-step
rotation structure alone. The transient mechanism remains
unidentified at the analytic level — but see the T1b point
below for why this doesn't block the paper.

### T1b reconciliation

This Mess was framed assuming the theorem target is stretched-exp
(T1a). The paper has since moved to **T1b: asymptotic 1/√n with
IC-specific stretched-exp transient** (see `sim/README.md`,
`sim/T1B-EVIDENCE-MAP.md`). Under T1b, the per-return Laplace
route's 1/√n prediction is no longer an obstruction; **it is the
correct rate**.

Combining T1b with Mess #3's empirical finding (τ_R tail ~ 1/√n),
the correct proof route is polynomial-tail induced-operator
theory — Melbourne & Terhesiu 2012, Gouëzel 2004, Sarig 2002,
Young's towers. That framework takes tail exponent α = 1/2 and
delivers correlation decay O(n^{−(1−α)}) = O(1/√n) natively,
matching T1b's asymptotic.

So Mess #1's original negative diagnosis — "the per-return
framework gives 1/√n, which is the wrong rate" — inverts under
T1b into a positive diagnosis: the per-return framework gives
1/√n, which **is** the right rate. The framework was aimed at
the wrong target (stretched-exp) rather than being wrong.

### Revised status

Under T1a: open, framing-level obstruction. Under T1b:
**substantially softened**. The per-return framework is
structurally correct for T1b's 1/√n asymptotic. The remaining
tasks are technical:

1. **Rigorous polynomial-tail induced-operator writeup for
   BS(1,2).** The machinery exists in the Melbourne-Terhesiu
   literature; instantiating it for the specific BS(1,2) walk
   is technical work but not a framing question.
2. **Uniformity of τ_R's 1/√n tail in x ∈ R.** The sim tested
   one IC; Feller-continuity-like arguments in the induced-
   operator theorems need uniform bounds. Not established here.
3. **Identification of the transient mechanism.** Not
   load-bearing for T1b but of independent interest.
4. **Mess #2's WHERE issue remains untouched by any of this.**
   The identification π_T ν_R = Leb_T is a separate problem
   (see Mess #2 update for the WHERE vs WHEN framing). Solving
   Mess #1's rate question does not solve Mess #2's target
   question.

The "Option (a) vs Option (b)" dichotomy in the original Mess
text ("transient that has not relaxed to algebraic" vs
"different mechanism not captured by the framework") is
superseded by T1b: the observed behavior is a 1/√n asymptotic
with a stretched-exp transient, both of which fit the
polynomial-tail framework's predictions (asymptotic
O(1/n^{1−α}) = O(1/√n)) plus finite-n corrections (the
stretched-exp transient has some specific mechanism, not
resolved here).

---

## Mess #2: Convergence to what?

### The claim

FIRST-PROOF §2 (R6) asks for

    π_T ν_R = Leb_T

where ν_R is the invariant probability for the induced
first-return operator T_R on the compact return set R.

This is the step that converts "the mantissa marginal converges
to the invariant law of T_R" into "the mantissa marginal
converges to Benford." Without it, the route gives a
stretched-exponential convergence theorem to some probability
ν* on T, but not a Benford theorem.

### The problem

The return-operator framework naturally produces an invariant
probability ν_R on R, then convergence to ν_R under T_R. That
much is internal to the operator. Benford does not come for
free. It requires identifying the T-marginal of ν_R.

The current recommended route is an irrational-rotation sketch:
upward excursions rotate the mantissa by random multiples of
log₁₀ 2, the excursion lengths hit every n with positive
probability, n·log₁₀ 2 mod 1 is equidistributed, therefore the
T-marginal of ν_R must be rotation-invariant, therefore uniform.

This is plausible, but it is still a sketch. Dense irrational
rotations along some part of the dynamics do not automatically
force the invariant law of the whole induced operator to have
uniform T-marginal. The walk also includes low-depth b-dynamics,
return-time weighting, and conditioning on re-entry to R. All of
that is folded into T_R. The identification step has to show that
this whole operator leaves no room for a non-Lebesgue marginal.

### What this breaks

The proof architecture in FIRST-PROOF §2 Route 1' is:

    (R4) T_R has spectral gap q < 1
    (R5) return statistics supply the law-level rate
    (R6) π_T ν_R = Leb_T
    ∴    φ(ν, n) ≤ C′ exp(−c√n) toward Benford

If (R6) fails, the theorem degrades to:

    φ(ν, n) ≤ C′ exp(−c√n)

for convergence toward an unidentified limit ν* on T.

That is still a convergence theorem. It is not the theorem the
paper claims.

### What this does not break

The simulation is fine. The observed limiting distribution can
still look Benford to numerical precision. The issue is not that
Benford is false in the experiment; the issue is that the current
route has not yet shown the operator's invariant marginal is
forced to be Benford.

Likewise, the contraction side of the route can still be right.
One can imagine proving that T_R contracts to a unique invariant
ν_R and still failing to identify π_T ν_R explicitly.

### The structural point

This is a different failure mode from Mess #1.

- Mess #1 is about **rate conversion**: does per-return
  contraction produce stretched-exponential decay or only an
  algebraic law?
- Mess #2 is about **target identification**: even if the route
  proves convergence at some rate, does it converge to Leb_T?

The two are logically independent. A route can get the rate right
and the limit wrong, or get the limit right and the rate wrong.
The paper needs both.

### Why this is deeper than bookkeeping

FIRST-PROOF gap 1 explicitly says the global invariant-measure
question was deferred, not settled. If identifying π_T ν_R as
Leb_T ends up requiring a harmonic or invariant-measure object on
T × ℤ after all, then the "deferred" global measure problem
re-enters through the back door. In that case, (R6) is not a
one-page Weyl argument but a second invariant-measure problem.

PNAS-PLAN's claim gate already contains the contingency:
if (R4)+(R5) close but (R6) does not, the result is a
stretched-exponential convergence theorem to an unidentified ν*,
and the title, theorem statement, significance statement, and
mechanism section all have to drop the Benford-identification
claim.

### Mechanical obstructions in the rotation-only sketch

FIRST-PROOF §2 (R6)'s rotation-invariance sketch — excursions
rotate the mantissa by n · log₁₀ 2, Weyl gives density, so
π_T ν_R is rotation-invariant — papers over five specific
issues:

1. **Rotation-equivariance fails inside R.** The walk kernel K
   does not commute with T-rotation for |E| ≤ E₀: the b-step map
   f(m, E) = frac(log₁₀(10^m + 10^{−E})) depends on m nonlinearly
   when |E| is small. Rotation-equivariance is only approximately
   recovered during excursions (|E| > E₀, where b-steps are
   near-identity). T_R as a whole is not rotation-equivariant.

2. **Dense support ≠ invariance under a specific rotation.**
   Weyl gives that {n · log₁₀ 2 mod 1 : n ∈ ℤ} is dense in T.
   That is a fact about the *support* of the excursion-rotation
   random variable θ. Concluding σ := π_T ν_R equals Leb_T needs
   either σ invariant under a specific irrational rotation or a
   Fourier/spectral argument that θ's distribution damps every
   nonzero mode of σ — neither follows from "dense support"
   alone.

3. **The real closing move is probably Fourier.** If σ has Fourier
   coefficient σ̂(r) ≠ 0 for r ≠ 0, T_R's excursion part damps
   σ̂(r) by E[e^{2πi r θ}] (modulus < 1 when θ has nontrivial
   spread). Invariance then forces σ̂(r) = 0 for r ≠ 0, giving
   σ = Leb_T. Clean, but overlaps with R4's norm choice — so R6
   is not really standalone.

4. **The b-step ε at finite E₀.** For any finite E₀, b-steps during
   excursions add O(10^{−E₀}) to the mantissa. The "rotation by
   n · log₁₀ 2" is really "rotation by n · log₁₀ 2 + O(10^{−E₀})."
   Either E₀ becomes a free parameter of the main theorem or the
   argument absorbs the O(10^{−E₀}) as a perturbation bound.

5. **Net-a-count distribution, not excursion length.** The
   rotation per excursion is (net a-count during excursion) ·
   log₁₀ 2, where net a-count is a bridge of a ±1 walk
   conditioned to start at E₀+1 and return to E₀. That bridge
   distribution is the Weyl input, not τ_R's law directly.

Any one is tractable; all five in one page is aspirational.
Expect R6 to be 2–4 pages via the Fourier route, not standalone.

### Status

Open. This is a theorem-identity problem, not a rate problem.
Until (R6) is genuinely closed, the current route proves at most
"convergence to the invariant marginal of T_R" in aspiration,
not "convergence to Benford."

### Update (2026-04-19): empirical evidence — WHERE

The `sim/return_marginal_SUMMARY.md` sim measured the pooled
post-burn distribution σ̃ of walker states at return events.
Setup: BS(1,2) paper kernel, N = 10⁶ walkers, n_max = 10⁴,
R = {|E| ≤ 10}, K_burn = 5, IC x = √2.

Findings:

- σ̃ is supported on the arc [1 − log₁₀ 2, 1) × {E = 10}, i.e.
  m ∈ [0.699, 1.000), E = +10. Every return event is on that arc.
- On the arc, σ̃ is uniform at density 1/log₁₀ 2 ≈ 3.32.
- L₁(σ̃, Leb_T) = 1.40, 260× above multinomial noise floor.
- Low-r Fourier coefficients of σ̃ are order unity:
  |σ̂(1)| ≈ 0.86, |σ̂(2)| ≈ 0.50, |σ̂(5)| ≈ 0.21.

Proposed mechanism (not directly measured): the only channel
returning a walker from E = 11 to E = 10 is a⁻¹ with borrow,
which requires m_pre < log₁₀ 2 and deterministically maps
m_pre → m_pre + (1 − log₁₀ 2). The arc support is therefore
arithmetic, not Diophantine.

**Pressure on the identification step.** If σ̃ is a reasonable
proxy for π_T ν_R (plausible, not certified — the sim pools
post-burn returns without verifying stationarity), the
identification π_T ν_R = Leb_T fails at the obvious R by a
specific and explicable mechanism. See `return_marginal_SUMMARY.md`
for the caveat list: stationarity check not performed,
E₀-sweep not done, pre-return-state not instrumented.

### WHERE vs WHEN: Mess #2 and Mess #3 are independent problems

Mess #2 and Mess #3 are sometimes grouped because both concern
the return operator T_R. In fact they probe **orthogonal
marginals** of the same return event.

Each return event has two components:

- **WHERE** — the walker's state at the return moment. Its
  distribution is the T-marginal of ν_R. **This is Mess #2.**
- **WHEN** — the duration τ_R of the excursion from exit to
  return. Its distribution is P(τ_R > n). **This is Mess #3.**

The two marginals are set by different mechanisms:

- **WHERE is set by single-step carry arithmetic.** The return
  step must be a⁻¹ with borrow at E = 11; that step deterministically
  sends m_pre → m_pre + (1 − log₁₀ 2), placing m_return in
  [1 − log₁₀ 2, 1) regardless of how long the excursion was.
- **WHEN is set by walker-level dynamics above R.** The E-process
  does an approximately symmetric random walk above R, and τ_R is
  its first re-entry time. That gives P(τ_R > n) ~ 1/√n (see
  Mess #3 update below). This tail depends on the b-step's effect
  on E and on the E-generator structure, not on the m-arithmetic.

Varying one does not force the other:

- Swap log₁₀ 2 for log₁₀ 3 (or any other irrational rotation
  amount): the arc for σ̃ becomes [1 − log₁₀ 3, 1) but τ_R's tail
  still ≈ 1/√n (still SRW-like in E).
- Swap b's action on E from ±1 to ±2: τ_R's tail constant
  changes but the arc doesn't.

**Consequence for the proof architecture.** Route 1' as sketched
treats Mess #2 and Mess #3 as if both were part of one operator-
legitimacy story that a single rewrite might resolve. They aren't.
Each needs its own fix:

- A fix for Mess #2 (different R, different framework for
  identifying the invariant T-marginal, or a walker-level
  argument for π_T ν_n → Leb_T that bypasses ν_R) says nothing
  about τ_R's tail.
- A fix for Mess #3 (polynomial-tail induced-operator theory,
  Young's towers, or a Markov-chain framework that tolerates
  heavy tails) says nothing about whether the invariant
  T-marginal is Leb_T.

A single fix that addresses both simultaneously is possible —
for instance, a walker-level argument that bypasses T_R entirely
would sidestep both — but it is not forced, and treating them
as "one coupled problem" has hidden their independence.

---

## Mess #3: The geometric tail that isn't

### The claim

FIRST-PROOF §2 (R2) wants the induced first-return operator

    T_R ν := Law(X_{τ_R})

on the compact return set R to be a weak-Feller / Feller Markov
operator, so that Krylov-Bogolyubov gives an invariant
probability ν_R.

The sketch there says truncated return operators are continuous
and converge uniformly to T_R because of a **uniform geometric
tail bound on τ_R** from x ∈ R.

### The problem

FIRST-PROOF §2 (R1) says the opposite thing about the hard part of
τ_R: upward excursions are null-recurrent, a.s. finite, but can
be arbitrarily long, with a heavy √-scale tail. That is the same
null-recurrent excursion structure that drives the rest of the
paper.

So the current R2 sketch appeals to the wrong kind of tail
control at the exact point where T_R is supposed to become a
legitimate operator. If the true return time has only polynomial
tail decay, then the usual "truncate and pass to the limit"
argument is no longer routine. Slow tails are exactly what make
uniform convergence delicate.

This is not just a loose bound. It is a mismatch of mechanism:
the route invokes fast-return regularity for an operator built
from a process whose defining feature is slow null-recurrent
return.

### What this breaks

The Route 1' architecture begins:

    define T_R
    show T_R is Feller on compact R
    obtain invariant probability ν_R
    prove spectral gap / identify marginal / get theorem

If the Feller step is not actually justified, the invariant
probability ν_R is not yet licensed. Then (R4) has no fixed
operator target, and (R6) has no invariant measure to identify.

Mess #3 is therefore upstream of both Mess #1 and Mess #2. It is
not about the rate once T_R exists, and not about the identity of
the limit once ν_R exists. It is about whether the operator at the
heart of the route has been put on solid ground in the first
place.

### What this does not break

It does not show that the return-operator route is impossible.
There may be a correct heavy-tail argument that still proves
weak-Feller continuity, or a different operator-theoretic route
to existence of ν_R, or a reformulation of T_R that avoids the
bad step entirely.

But none of those is what the current sketch says. The point of
this mess is not that the route cannot be repaired; it is that the
repair is not yet in hand, and the present draft is not entitled
to proceed as if it were.

### The structural point

Mess #1 and Mess #2 attack two downstream claims:

- Mess #1: does per-return contraction convert to the claimed
  stretched-exponential **rate**?
- Mess #2: even if there is convergence, is the **limit** actually
  Benford?

Mess #3 attacks the operator layer beneath both:

- Mess #3: is the induced return operator `T_R` actually
  well-behaved enough to support the invariant-measure /
  spectral-gap story at all?

That is why it is a peer. The issue is not a missing constant or
a nicer proof of a true claim. It is that the current legitimacy
argument for the central object uses the wrong qualitative tail.

### Why this is deeper than an afternoon patch

If the return time really had a geometric tail, truncated-return
operators would converge fast and uniformly, and the Feller
argument would be routine. With polynomial tails, uniform control
must be proved by some more delicate argument, and the walk is
coupled: E-increments depend on the mantissa, so one cannot simply
drop in the textbook simple-random-walk return analysis unchanged.

This is exactly the kind of point that can be resolvable by
investigation, modification, or research, and still be a mess now.
Until the actual heavy-tail continuity argument exists on paper,
the route is resting on a false heuristic.

### Status

Open. This is an operator-legitimacy problem, not a rate or
identity problem. The current Route 1' sketch treats `T_R` as if
its return-time regularity were exponentially tame; the walk
described in the same document is not. Until that mismatch is
resolved, the return operator is still partly aspirational.

### Update (2026-04-19): empirical evidence — WHEN

The `sim/tau_R_tail_SUMMARY.md` sim measured the first-excursion
τ_R survival function directly. Setup: BS(1,2) paper kernel,
N = 10⁶ walkers, n_max = 3 × 10⁴, R = {|E| ≤ 10}, IC x = √2.

Findings:

- P(τ_R > n | had first exit) ~ C · n^{-0.495} on n ∈ [50, 10⁴],
  R² = 1.0000 across 15 log-spaced grid points.
- Slope matches the textbook SRW null-recurrent return exponent
  −1/2 to two decimals.
- S(3 × 10⁴) = 7.0 × 10⁻³, still declining as 1/√n; no plateau
  visible at the horizon.
- 99.30% of walkers had at least one return; 0.70% had not
  returned by n = 3 × 10⁴.

**This empirically confirms the qualitative concern in Mess #3.**
The tail is polynomial, not geometric. More specifically, it is
1/√n — the best-behaved case of polynomial tails.

**Implication for the proof architecture.** FIRST-PROOF §2 R2's
appeal to uniform geometric convergence of truncated-return
operators is framework-incompatible with a walk whose return
tail is 1/√n. The correct framework for this regime is the
literature on induced operators with polynomial return tail:

- Melbourne & Terhesiu 2012 (operator-renewal theory for
  infinite-measure dynamical systems).
- Gouëzel 2004 (sharp polynomial bounds for mixing under
  polynomial return-time tail).
- Sarig 2002 (subexponential decay of correlations).
- Young's tower construction (Ann. Math. 1998).

These theorems take tail exponent α ∈ (0, 1) for P(τ > n) ~
C/n^α and give correlation decay O(n^{-(1-α)}). With α = 1/2
(our empirical finding), the delivered decay is O(1/√n) —
natively the 1/√n shape claimed in T1b.

**Encouraging alignment with T1b.** The polynomial-tail
framework gives T1b's asymptotic natively. The measured tail
exponent and the claimed theorem asymptotic match. A proof of
T1b through this framework would not need a separate mechanism
for the rate; the tail exponent and the asymptotic are the
same object.

**Caveats.** IC-conditional (the 1/√n slope is for first
excursions from x = √2; subsequent excursions pool differently).
Finite horizon (n_max = 3 × 10⁴). Single R shape (E₀ = 10).
The uniform-in-x ∈ R claim that Feller-continuity would need is
not tested. See `tau_R_tail_SUMMARY.md` for the full caveat list.

### Independence from Mess #2

Mess #3's empirical content (polynomial tail on τ_R) is
orthogonal to Mess #2's empirical content (arc-concentrated σ̃
on m_return). Each marginal of the return event has its own
mechanism. For the full independence argument and its
consequences for proof strategy, see the "WHERE vs WHEN"
subsection under Mess #2's update above.

The short version: a rewrite of Route 1' that uses polynomial-
tail induced-operator theory would address Mess #3 but leave
Mess #2's identification step untouched. A rewrite that fixes
the identification (via a different R, or by bypassing ν_R)
would address Mess #2 but leave Mess #3's polynomial-tail
framework question untouched. The two fixes are logically
independent, even if a single restructuring of the proof
architecture might end up addressing both.

---

## Mess #5: Relation vs. actions under Route 1'

**Status:** Resolved for Route 1' (2026-04-17). **Reopen trigger:**
any future proof route that tries to make `bab⁻¹ = a²` load-bearing
(e.g., ladder-time, horocyclic/geodesic, or Cuno–Sava-Huss style).
Canonical wording lives in PNAS-PLAN §6 kicker and
FIRST-PROOF §5; this entry is the archival record.

### Original claim

The paper wanted BS(1,2) to matter as an algebraic object, with the
relation `bab⁻¹ = a²` doing explanatory work — not decoration.

### Why Route 1' didn't deliver

Route 1' uses only generator *actions*: irrational rotation under
a-steps, low-depth ε-perturbation under b-steps, and null-recurrent
return statistics of the exponent walk. None invokes the relation.
A free group on {a, b} with the same generator actions would give
the same proof skeleton. That threatens theorem-story match, not
theorem truth.

### Resolution

Narrow the claim. BS(1,2) is the *minimal algebraic setting* in
which the two operations (double, add-one) appear together; the
relation identifies the group, not the mechanism. The convergence
comes from the generator actions plus null-recurrent returns. The
§6 kicker in PNAS-PLAN and §5 of FIRST-PROOF now carry this
wording. Option (A) — making the relation load-bearing via a
Cuno–Sava-Huss ladder-time argument — was considered and not
pursued, on the grounds that Theorem 1 doesn't need the extra
machinery.

---

## Mess #6: Is the induced map Gibbs–Markov?

### The claim

SECOND-PROOF §3 (F1) currently leans on Melbourne–Terhesiu 2012
as the primary framework citation, with the verification
template of M–T §11.2 (Gibbs–Markov first-return map). On our
current reading, that template requires, on the
Bernoulli-shift skew product Ω × (T × ℤ), that the induced
first-return map F on Y = Ω × R satisfies:

- **(GM-1) Countable Markov partition.** A partition α of Y
  such that F maps each partition element bijectively onto a
  union of partition elements.
- **(GM-2) Big images.** inf_{a ∈ α} μ(Fa) > 0.
- **(GM-3) Uniformly piecewise Lipschitz distortion.**
  log(dμ/dμ ∘ F) Lipschitz on each a ∈ α with uniform constant,
  under the dynamical metric d_τ.

These hypotheses are the standard route to M–T's (H1)(H2) via
Hennion's theorem. If they really hold, they give the
renewal-operator input to T1b's n^{−1/2} scale (with a log
correction at β = 1/2; see `paper/F1-HYPO-PLAN.md`). They do
not by themselves finish the theorem: the return-to-full-walk
and mantissa-identification steps still have to close.

### The problem

(GM-1) is the load-bearing hypothesis at risk. The natural
first guess for a partition is by *excursion type*: two points
(ω, x) and (ω', x') are in the same cell if their generator
sequences from first exit to first return are identical. That
partition is countable and adapted to the dynamics.

But F maps each excursion-type cell to a set of return states
that depends *continuously* on the entry mantissa. Two walkers
in the same cell (identical generator sequence) arrive at
different return mantissas because the a-step rotates by
log₁₀ 2 and the b-step action on T is continuous in m. So
F(cell) is a continuous range of return states, not a union of
excursion-type cells.

On our current reading, that means the naive excursion-type
partition is not Markov under F: F does not map its cells onto
unions of cells, but smears them across a continuum. What has
not been shown is that no finer partition could repair this.

### What this breaks

If this reading is right and no refinement exists, M–T §11.2
does not apply directly. F1's current verification falls
through at the (H1) step. The paper's theorem statement
("BS(1,2) mantissa converges at rate n^{−1/2}") then loses its
clean M–T backing.

The skew-product translation (Option A in F1-HYPO-PLAN) is not
itself the issue. The issue is that the natural partition on
the skew product isn't Markov under the induced map.

### What this does not break

The sim evidence is unaffected. T1b's empirical content
(α̂ = 0.525 on M3 IC (b), c(ν) transient values on the IC
panel, etc.) stands regardless of whether M–T applies at the
proof level.

(GM-2) is not the present obstruction, and Mess #2 may help its
eventual verification heuristically: return mass concentrates on
a specific arc. But that is not the same thing as proving
inf_{a ∈ α} μ(Fa) > 0 for partition-element images, so the
big-images hypothesis should not be counted as closed here.

(GM-3) depends on b-step regularity parametrized by ε
(`sources/BINADE-WHITECAPS.md`). If (GM-1) fails, (GM-3)
doesn't matter; if (GM-1) holds, (GM-3) is probably the
easier check.

### The structural point

Messes #1 and #3 asked whether per-return contraction × return
count gives the right asymptotic shape. Mess #2 asks whether
ν_R's T-marginal is Leb_T. Mess #6 is more upstream: does the
framework that would give us (H1)(H2) actually apply to the
object we built, or are we still using the wrong symbolic model
for the induced map?

If the naive partition really fails and no refinement repairs
it, the next lines of defense are:

- **(a) Different framework.** Option B in F1-HYPO-PLAN:
  direct Markov-chain polynomial ergodicity (Tuominen–Tweedie
  1994, Jarner–Roberts, Meyn–Tweedie-adjacent). Different
  function spaces, different citations. Currently tagged
  fallback.
- **(b) Different partition.** Some partition of Ω × R that is
  genuinely Markov under F even if the excursion-type partition
  isn't. Unclear what that would be.
- **(c) Different M–T example class.** AFN template
  (M–T §11.3, BV norm), which is more forgiving of branch
  discontinuities but needs a different structural match —
  an AFN-style non-Markovian interval map with indifferent
  fixed points, which BS(1,2) isn't directly.

None of these is free. Each is real technical work.

### Why this is different from "just run more sims"

The paper's value-add is the *theorem*: BS(1,2) mantissa
converges to Benford with identified rate, proved via an
identified mechanism. Empirical Benford-ish behavior on
various processes is common in the literature; a proved-rate
theorem for this walk isn't. If this reading is right and none
of (a)(b)(c) nor a softer M–T interpretation works, the paper
has no theorem — at which point
the work is a numerical study, not a theorem paper.

So Mess #6 is the mess that tests whether the current proof
plan has a path to theorem at all.

### Status

Open. Transitional form. The older objection was "M–T may not
apply at all." The current, narrower objection is: on our
present reading, the naive §11.2 verification route looks wrong
because the excursion-word partition is probably not Markov.
That may still collapse to a partition-refinement issue or a
looser reading of M–T, but it is not resolved yet. The
investigation that produced this Mess is in
`paper/F1-HYPO-PLAN.md`.

### Falsification protocol

**Claim to falsify.** On our present reading, F with the natural
excursion-type partition is not Markov, so the M–T §11.2 route
doesn't apply. What would falsify it: exhibit a partition (the
naive one or a natural refinement) under which F maps cells to
unions of cells, confirmed on a small concrete example.

**First test.** The minimal two-step excursion type: one a-step
exits R (at some boundary E = E₀), one a⁻¹ with borrow at
E = E₀ + 1 returns to R. For this excursion type, compute by
hand:

1. The subset of entry mantissas m ∈ T *compatible* with this
   generator word — i.e., the entry m for which the return step
   a⁻¹ at E = E₀ + 1 is admissible (its pre-mantissa < log₁₀ 2).
2. F restricted to the compatible subset: the entry-to-return
   mantissa map. Is it piecewise monotone and smooth, or does
   it smear continuously?
3. F(compatible subset): is the image a union of intervals that
   matches the compatible subsets of *other* excursion-word
   cells in R, or is it an arbitrary continuous range that
   doesn't align with any natural partition?
4. If F is monotone on the compatible subset, check whether
   log(dμ/dμ ∘ F) is Lipschitz under d_τ.

**Outcomes.**

- **Mess #6 falsified on this example.** F(compatible subset)
  matches a union of partition-element images cleanly. Next
  check: does this behavior generalize to longer excursion
  words, or is it a lucky short case? If it generalizes,
  Mess #6 downgrades and F1-HYPO-PLAN Option A proceeds;
  (GM-3) becomes the next check and F1-HYPO-PLAN can dissolve
  as planned.
- **Mess #6 confirmed on this example.** F(compatible subset)
  smears across a continuum not aligned with any natural
  partition. M–T §11.2 route stays blocked; promote
  F1-HYPO-PLAN Option B (Meyn–Tweedie polynomial ergodicity)
  to primary and reopen the framework question.

This is paper-side calculation, not a sim. 1–2 pages of work.
See `paper/F1-HYPO-PLAN.md` §4–§5 for the broader verification
context that this protocol feeds.
