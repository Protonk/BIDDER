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
