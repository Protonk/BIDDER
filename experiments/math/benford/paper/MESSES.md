# MESSES

Problems that threaten the proof architecture in FIRST-PROOF §2.
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

### Status

Open. This is a theorem-identity problem, not a rate problem.
Until (R6) is genuinely closed, the current route proves at most
"convergence to the invariant marginal of T_R" in aspiration,
not "convergence to Benford."

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
