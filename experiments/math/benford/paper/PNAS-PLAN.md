# PNAS Plan

Target: PNAS Brief Report. ~1600 words, 2 figures, 15
references. This paper either closes in that space or not at all.


## What the paper is

A mechanism paper. Benford's law — leading digits of naturally
occurring numbers follow log_10(1 + 1/d) — has been documented
for 140 years and explained many times, never satisfactorily.
Hill (1995) characterizes the fixed point but regresses the
explanation one level (why scale-invariant?). CLT-for-logs
requires independence and identical distributions that real
data lack, and gives no rate. Spread-across-scales is necessary
but doesn't select Benford over other mantissa shapes.
Power-law mixing converges algebraically, too slowly to explain
strong Benford conformity in modest datasets. The question is
genuinely open: no existing account provides a mechanism with
minimal conditions and an exponential rate.

The paper provides the mechanism. Define

    epsilon(m) = log_2(1 + m) - m,    m in [0, 1).

This is the nonlinear part of the coordinate map between
linear and logarithmic representations of the mantissa. It is
strictly positive on the interior, zero at both endpoints,
with a unique maximum at m* = 1/ln 2 - 1, determined entirely
by ln 2. The paper's claim: **epsilon is the spectral gap of
the Markov operator induced by mixed arithmetic in the
BS(1,2) model on the mantissa circle.** Because epsilon > 0
on (0,1), the operator is a contraction, and the unique fixed
point is the Benford distribution. Convergence is exponential
with a rate controlled by the L^2 norm of epsilon. The
mechanism doesn't regress: it terminates at the concavity of
the binary logarithm, which is a fact about ln 2.


## What the paper is not

1. **Not forbidding.** Benford work is contaminated by the high power statistical tools needed for 
  the job of analysis. Consequently a lot of straightforward partial results are read as more total than they actually are because they look hard. Our job is to be inviting and specific. Any reader of PNAS should know someone who can explain the paper after one read through.

2. **Not a Benford survey.** There are good surveys (Berger and
   Hill 2015, Miller 2015). We cite them and move on. The paper's
   job is not to review what is known about Benford — it is to add
   one thing: the identification of epsilon as the spectral gap,
   with a rate.

3. **Not a cross-disciplinary connection paper.** Epsilon has a
   life in computer arithmetic (IEEE 754, the fast inverse square
   root). That connection is real and it's for the book. This
   paper is laser-focused on Benford. Epsilon is introduced as a
   mathematical object — the nonlinear part of the coordinate map
   psi(m) = log_2(1+m) — and its relevance is to the proof, not
   to any other domain. No CS hooks, no "two consequences"
   framing. Every word serves the Benford result.


## Why the paper exists: the field of failed explanations

Benford's law has been "explained" many times. Every existing
explanation fails in a specific, nameable way, and the failures
are different enough that no two accounts cover each other's
gaps. This is our leverage. The paper doesn't enter a crowded
field — it enters a field where everyone agrees the question is
open and each prior attempt demonstrates *which part* is hard.

**Hill (1995): scale-invariance.** Benford is the unique
distribution on significands invariant under multiplication by
any constant. This is a characterization theorem — it identifies
the fixed point. It does not explain why real data should be
scale-invariant in the first place. The explanatory burden
regresses one level: "Benford because scale-invariant" becomes
"why scale-invariant?" Hill's theorem is the *what*. The *why*
is still open. Our result gives the *why*: epsilon is a
contraction, and the Benford distribution is its unique fixed
point. Scale-invariance falls out as a *consequence* of the
contraction, not a *premise*.

**Central-limit-for-logs.** If you multiply many independent
random variables, the log of the product is a sum, and CLT
gives an approximately normal distribution of logs, which
projects to approximately Benford significands. This is the
textbook explanation and it has two problems. First, it
requires conditions: independence, common distribution (or at
least Lindeberg), and enough factors. Real data don't come with
those guarantees. Financial returns are correlated. Physical
measurements are not products of iid variables. The conditions
are assumptions about the data-generating process, and the
data-generating process is exactly what we don't know. Second,
CLT gives no usable rate of convergence for the significand
distribution specifically. Berry-Esseen controls the normal
approximation of the log, but the projection to the mantissa
circle can amplify or attenuate the error in ways CLT doesn't
track. Our result: no independence assumption, no identical-
distribution assumption, exponential rate.

**Spread-over-orders-of-magnitude.** Data that spans many orders
of magnitude tends toward Benford. True — and necessary, since
data confined to one order of magnitude has a constrained
leading-digit distribution. But it is not sufficient. *Why*
does spanning orders of magnitude give Benford rather than some
other distribution on the mantissa circle? A uniform
distribution on [1, 10^6] is not Benford. A log-uniform
distribution is. "Spread across scales" tells you the support
is wide enough; it does not tell you the shape. Our result:
the shape is determined by epsilon regardless of the initial
spread. Spanning orders of magnitude is what gives the
ergodicity (the irrational rotation from multiplication); the
*contraction* that selects Benford specifically is epsilon's
job.

**Power-law generators.** If data are drawn from a distribution
with a power-law tail (Pareto, Zipf), the significand
distribution converges to Benford as the exponent parameter
varies — or more precisely, as you sample from a mixture of
power laws. This is correct and gives genuine Benford
convergence. The problem is speed: the convergence is
algebraic (polynomial in the number of mixed components or the
tail range), not exponential. For small samples or narrow
parameter ranges, the approximation is poor, yet empirical
Benford conformity is often strong even in modest datasets.
Our result: exponential convergence. The half-life is ~20
operations in the symmetric BS(1,2) walk. Twenty steps, not
twenty thousand.

**What epsilon gives that none of them do:** a single,
identified mechanism (not a distributional assumption), minimal
conditions (any nondegenerate measure on the BS(1,2)
generators), an exponential rate (not algebraic, not
uncontrolled), and an explanation that doesn't regress (the
contraction exists because ln 2 is irrational, full stop).
Four failures, one function.

The paper must name these four failures in the main text. In
the Columbo structure, they come *after* the result (section
6, the Hamming diagnosis). The reader arrives at the diagnosis
already holding the answer — epsilon, with an exponential
rate — and checks each prior attempt against it. The four
deficits are specific: no mechanism, no rate, wrong
conditions, or explanatory regress. Sections 1-4 deliver the
mechanism, the rate, the conditions, and the terminus. Section
6 turns around and shows why no one else got there.


## The audience problem

PNAS readers who care about Benford's law:

- **Physicists.** Know it from first-digit tests on physical
  constants. Want a mechanism, not a characterization theorem.
  Hill's 1995 result tells them the stationary distribution; they
  want to know why the dynamics converge to it. Epsilon gives them
  the dynamics. The group-theoretic framing (geodesic =
  multiplicative, horocyclic = additive) maps onto how physicists
  already think about scale separation.

- **Statisticians.** Know Benford from fraud detection (Nigrini)
  and from the digit-testing literature. Interested in convergence
  rates — how many operations before the distribution is close
  enough to test against? The exponential rate with a computable
  bound is directly useful to them.

- **Number theorists / dynamicists.** Know about equidistribution
  mod 1, Weyl sums, Fourier coefficients on the circle. Will
  check whether the Schatte-style Fourier asymptotics and the
  BS(1,2) mechanism actually meet in the main text, and whether
  the spectral gap identification is stated at the strongest
  level we can prove. These are the referees.

The main text must serve the first two groups. A PNAS
Brief Report has 1600 words to make both the physicists and
the statisticians feel they got what they came for, while giving
the dynamicists enough actual proof, not deferred proof, to sign
off on the claim.


## The register: undergraduate-accessible, cite-precise

The paper should be readable by a strong undergraduate math
major — an upperclassman who has seen first-semester abstract
algebra and first-year calculus. This is not a concession to
a popular audience. It is the correct register for this
specific result, because the result's content is that the
mystery was never hiding behind advanced mathematics. It was
hiding behind the absence of one group-theoretic observation.

The material decomposes into pieces that are each
undergraduate-accessible:

- What a mantissa is, what the log-mantissa circle is.
  First-year calculus.
- What Benford's law says in the circle formulation. One
  line.
- Hamming's observation: multiplication gets you there,
  addition doesn't. Intuitive.
- Schatte's result, stated in words: no finite-order
  averaging rescues addition; a different kind of averaging
  does. No Fourier coefficients required to *understand*
  the claim.
- What a group is, generators and relations. First-semester
  abstract algebra.
- BS(1,2) as two generators a (double) and b (add one),
  with the relation bab⁻¹ = a². Concrete.
- Cayley graph as a picture of what the machine can do.
  Visual.
- Random walk on the Cayley graph, projected down to the
  mantissa circle. Picture plus one sentence.
- The Benford distribution as the stationary measure.
  Statement, not proof.
- Convergence rate. Named, not derived.

Each of those is a paragraph or less. None requires machinery
a good undergraduate hasn't seen. The paper that explains all
of them in sequence, with two figures carrying the setup, is
structurally identical to a Miller undergraduate chapter —
compressed and aimed at a peer audience rather than a student
audience.

**The implicit demonstration.** A reader who finishes the paper
and thinks "I could have understood that as a junior" has been
handed the actual content of the resolution: the mystery
wasn't hiding behind advanced mathematics, it was hiding
behind the absence of one group-theoretic observation. If the
paper reads as difficult, the reader will suspect the
difficulty is doing load-bearing work. If it reads as clear,
the reader will register that clarity as a claim — this was
always within reach, and the substrate is the reason it now
is. The register matches the thesis.

**The discipline this imposes.** Every time a sentence gets
technical, ask whether the technicality is carrying weight or
performing rigor. Schatte's Fourier machinery is the classic
trap — it's what makes his paper feel serious, and importing
even a little of it would make this paper feel like it needs
that machinery to work. It doesn't. Hamming's asymmetry plus
"Schatte proved no finite averaging suffices" is all the
diagnostic weight the paper needs to carry. The positive
result doesn't need machinery at all; the group relation does
the work.

**Paragraph heuristic.** If you showed it to a strong
undergraduate math major, could they read it once and explain
it back? If no, either the paragraph is doing more than it
needs to, or the concept needs one more sentence of
plain-prose onboarding. The Brief Report budget is tight, but
plain-prose onboarding is cheaper per word than technical
compression. Five words of "think of this as" often saves
fifteen words of careful qualification later.

**Three sentence-level disciplines:**

*Trust the picture to carry the setup.* The figures show what
equilibrium looks like and what the Cayley graph looks like.
Captions can define op-index and BS(1,2) operationally. Do
not spend an 80-word paragraph re-describing what the reader
is already looking at. If the figure is doing its job, the
prose points at it and moves on.

*Let single sentences carry the load, then stop.* "The
relation bab⁻¹ = a² is the interaction of addition and
multiplication as a group relation" is the paper's central
claim; it does not need a supporting paragraph beneath it.
Resist the academic reflex of restating the key sentence in
three successively more formal registers. One sentence, one
commit, move to the next thing.

*Name and move.* "Schatte (1986) proved no finite-order
Hölder summation suffices; the Riesz logarithmic mean does."
Two clauses, one citation, diagnostic closed — never return
to it. This avoids the trap where prior work keeps
reappearing because you didn't commit to one clean handoff
the first time. Each prior result gets one appearance, does
its job, and is done.

**The crank-adjacency risk.** Accessibility is the register
most likely to trip a reviewer's crank-adjacency alarm,
because most Benford cranks also write accessibly. The defense
is specificity. Cranks wave at the phenomenon; we name a
specific group, state a specific theorem, cite specific prior
work with specific characterizations of what it did and didn't
do. Accessibility plus specificity reads as confident
exposition. Accessibility without specificity reads as
evasion.

Every citation must do a specific job — naming what a prior
result did, what it didn't do, or what machinery the proof
rests on. No citation is there to signal familiarity. A
skeptical reader sees literature command not from density but
from precision: each name appears because the paper needs it,
and what the paper needs from it is stated. Much may be
needed. That is what separates this paper from the paper a
reviewer would reject on vibes.


## What must be true before we draft

These are in priority order.

1. **The proof must close.** Specifically: the wrapped-Cauchy
   comparison (or identity) in step (b), and the biased-walk
   treatment in step (c). If either is shaky, the theorem
   statement has to change, and the rhetoric changes with it.
   Do not draft around the gap. Bring the argument to the point
   where we know whether the spectral-gap identification is
   exact or only a lower bound, then write the paper in that
   register.

2. **The rate prediction must be quantitative.** The simulation
   gives lambda ~ 0.035. The theorem gives lambda = 2*pi*gamma*rho.
   We need gamma and rho as explicit numbers for the symmetric
   walk, and the predicted lambda needs to be in the same
   neighborhood as 0.035. If the bound is off by 10x, we state
   it as a bound and don't oversell the match. If it's within a
   factor of 2, we can say "the predicted rate agrees with
   simulation to within [factor]." This quantitative comparison is
   the difference between a paper that *says* "spectral gap" and a
   paper that *measures* one.

3. **Anything beyond BS(1,2) must arrive with status attached.**
   The theorem is stated for BS(1,2). Any broader sentence about
   "mixed arithmetic" must be either a corollary with an explicit
   embedding argument or a labeled conjecture. There is no
   ambient overclaiming prose.

4. **The existing simulations must be publication-grade.** The data
   exist. The figures are dark-background diagnostic plots. They
   need to be redrawn for PNAS column width, white background,
   correct fonts, and colorblind-safe palettes. The data don't
   change; the rendering does. This is the smallest item but it
   blocks submission.

5. **The related work must be positioned as a field of
   specific failures, not a background section.** The four
   prior explanations (Hill, CLT-for-logs, spread-across-scales,
   power-law mixing) are not "related work" in the usual sense
   — they are the *reason the paper exists*. Each one fails at
   a named point, and the paper's opening movement names those
   points. This is a stronger positioning than "complementary,
   not competing." It's: "here are the four things the field
   has tried, here is exactly where each one breaks, and here
   is the one function that fixes all four."

   The three closest ancestors get specific positioning:
   - **Hill (1995):** gives the fixed point. We give the
     dynamics that converge to it. Hill's theorem becomes a
     corollary: scale-invariance holds because the Benford
     distribution is the unique fixed point of the epsilon
     contraction, and a contraction's fixed point is invariant
     under the contraction's generators.
   - **Schatte (1986):** our direct ancestor. Proved exponential
     convergence under pure multiplication and non-convergence
     under pure addition. We close the gap: mixed arithmetic
     converges exponentially, and the rate is epsilon.
   - **Diaconis (1977):** "sufficiently many significant digits"
     implies approximate Benford. Our result gives the
     mechanism beneath his observation and replaces "sufficiently
     many" with an explicit exponential rate.

   At 1600 words, none of these gets a full paragraph. But
   the four-failure framing in movement 1 does the heavy
   positioning work — by the time a referee reaches the
   theorem, they already know where it sits relative to
   everything else.


## The proof problem

The earlier version of the proof story used three ingredients:
transfer operator, wrapped Cauchy structure, visit rate. That
framing was invented before the Schatte analysis was complete.
Now we have three sources that triangulate on a cleaner proof
story, and the mechanism section of the paper should reflect
this.

That isn't a problem. The problem is we need to get there in ~700 words, accessible to a mathematics undergrad. 

### The Schatte–FOURIER'S STAR backbone

Schatte (1986) proves the key dichotomy for iid sums Z_n with
nonzero mean:

- The mantissa distribution's Fourier coefficients h_n(r) have
  a leading term (|a|n)^{2πir} that rotates with unbounded
  argument and O(1/n) error (Lemma 1).
- k-fold Cesàro averaging damps the modulus by |2πir+1|^{-k}
  but does not stop the rotation (Lemma 6).
- Riesz logarithmic means (weight 1/j at step j) converge to
  the logarithmic (Benford) distribution at rate
  O(1/∛(log n)) (Theorem 5).

FOURIER'S STAR extracts the structural consequence:

- No finite Hölder order makes the Cesàro-averaged mantissa
  distributions Cauchy. The separation at order k is at least
  c · |2πi+1|^{-k}. The hierarchy never closes.
- The passage from Cesàro non-convergence to Riesz convergence
  is the coordinate change ψ(m) = log_2(1+m). Its deviation
  from the identity is ε.
- **The obstruction is a change of basis, not a change of
  degree.** Iterating uniform averaging (Cesàro) to higher
  order indexes the wrong family. Convergence requires the
  qualitative change to 1/j weighting — the coordinate change
  ε.

This gives us the proof's conceptual backbone: pure addition
performs Cesàro averaging on the mantissa Fourier coefficients
and does not converge. Multiplication performs the coordinate
change ψ = id + ε, converting Cesàro toward Riesz weighting.
Because ε > 0 on (0,1), each multiplicative step contributes
nonzero Riesz-type cancellation. The spectral gap opens.

### The Cuno & Sava-Huss machinery

Cuno & Sava-Huss (2015) provides the group-theoretic frame:

- The random walk Z_n on BS(1,2) decomposes into a vertical
  (level/geodesic) component λ(Z_n) and a horizontal
  (horocyclic) component B_{Z_n}.
- The vertical component is a random walk on ℤ with drift
  δ = E(λ(X_1)). The three cases (δ > 0, δ < 0, δ = 0)
  determine convergence to the boundary.
- For the symmetric measure on BS(1,2), δ = 0 (driftless).
  Lemma 2.3: the projections π_H(Z_n) have sublinear speed,
  d_H(π_H(Z_0), π_H(Z_n))/n → 0. Lemma 2.7: the projections
  converge a.s. to a random end in ∂T.
- The horizontal displacement B_{Z_n} = Σ C_k where
  C_k = A_{X_1} · ... · A_{X_{k-1}} · B_{X_k}. This is the
  mantissa accumulation.

This tells us that the "visit rate" ingredient from the
original outline already exists in the literature: the vertical
walk's recurrence (symmetric case) or transience with
computable return statistics (biased case) governs how often
the walker is at low depth where ε has maximal effect.

### The Marasa & Matula confirmation

Marasa & Matula (1973) provides independent empirical
confirmation — from 1973 — that the operator mix is the
determining factor:

- Multiply-only: log-linear error growth on a semilog plot
  (= exponential Benford convergence in mantissa terms).
- Add-only: linear error growth (= non-convergence).
- Mixed: dominated by the multiplicative component.
- "The determining characteristic of error growth is the
  operator mix." The specific finite-precision arithmetic
  (truncated, rounded, logarithmic) barely matters.

This maps directly onto our simulation results and the
theorem's prediction. It's also a natural citation for the
robustness section: the result is not sensitive to arithmetic
details, only to whether multiplication is present.


## Specific risks

- **The Fourier-coefficient route must connect to the L^2
  rate.** The Schatte asymptotics give pointwise (per-r)
  control. We need to lift this to an L^1 or sup-norm rate
  on the distribution. The integration-by-parts bridge in
  FOURIER'S STAR §4 is the tool, but it needs to be
  sharpened for the mixed-arithmetic case where the
  "rotating leading term" is replaced by the BS(1,2)
  walk's horizontal displacement.

- **The visit rate ρ.** For the symmetric walk (δ = 0),
  recurrence of the vertical component is standard (Cuno &
  Sava-Huss cite Pólya). For biased walks (δ ≠ 0), the
  vertical walk is transient — the total number of visits
  to the active zone is finite. The biased-walk simulation
  still shows convergence, so the theorem for the biased
  case must say: the finite total of Riesz-cancellation
  visits suffices. This is a weaker statement than the
  symmetric case but still gives convergence.

- **The quantitative rate.** Schatte's Riesz convergence is
  O(1/∛(log n)) — very slow. Our simulations show
  exponential convergence (λ ≈ 0.035/step). The gap between
  Schatte's rate and ours must be explained: Schatte studies
  iid sums (pure addition with growing mean), not mixed
  arithmetic. The mixed walk's multiplicative steps produce
  faster-than-Riesz convergence because the coordinate
  change is applied stochastically at every multiplicative
  step, not merely as a summation weight. The exponential
  rate is the spectral gap of the transfer operator on the
  circle, not the Riesz rate. The Riesz connection is
  conceptual (naming the obstruction), not quantitative
  (predicting the rate).

- **The gap identification.** Is the spectral gap "a functional
  of ε" or "bounded below by a functional of ε"? Both are
  publishable. The Fourier-coefficient route may give a
  cleaner path to the strong version: if the Cesàro-to-Riesz
  conversion rate is directly computable from ε, the
  identification is exact.

- **Operator-language precision.** The plan currently uses the
  strongest operator words — "ε is the spectral gap," "the
  operator is a contraction" — while the theorem section, as
  stated, only guarantees exponential convergence with a lower
  bound on the rate. Those are close but not identical claims.
  Before drafting, either the operator, function space, and norm
  have to be specified tightly enough to justify the stronger
  language, or the prose has to step down one notch and say
  exactly what is proved.


## The failure modes

What kills the paper at review:

- **"This is known."** A referee who works on random walks on
  solvable groups may feel that exponential mixing on BS(1,2) is
  folklore. Defense, and it's strong: (a) no one has identified
  the spectral gap of Benford convergence with a specific,
  named function and given a quantitative rate; (b) the existing
  "explanations" of Benford are all either characterization
  theorems without dynamics (Hill), distributional assumptions
  without rates (CLT-for-logs), necessary conditions that aren't
  sufficient (spread-across-scales), or convergence without speed
  (power-law mixing). If the result were known, one of those four
  would have settled the question. None has. The field's own
  track record is our evidence that the result is new. This
  defense works even if the *mixing* is expected, because the
  contribution is the *rate identification* plus the *unification
  of four failure modes under one function*.

- **"The proof isn't actually there."** In a 1600-word paper with
  no supplemental escape hatch, every sentence in the mechanism
  section has to carry proof weight. If the core implication
  relies on a deferred lemma, omitted estimate, or "see elsewhere"
  move, the paper will read like a claim in search of a proof.

- **"Why PNAS?"** This is a theorem about a specific solvable
  group and a specific function. What makes it PNAS-broad rather
  than Annals-of-Probability narrow? Answer: the Hamming
  diagnosis. The paper doesn't just prove a theorem — it
  positions the theorem against a field of failed explanations
  that PNAS readers already know about, and shows that the
  theorem resolves all four simultaneously. That framing is
  what makes it broad. If section 6 (the diagnosis) fails to
  land, the paper reads as a specialist result in a generalist
  venue.

- **"The generalization is hand-waving."** The theorem is for
  BS(1,2). Any sentence beyond that has to arrive as theorem,
  corollary, or conjecture. If the paper slides from "BS(1,2)
  models mixed arithmetic" to "therefore mixed arithmetic in
  general is settled" without an explicit embedding theorem, a
  careful referee will stop there.


## The rhetorical arc

Eight sections, Columbo structure: show the answer first,
then show why no one else found it.


### 1. Intro and statement of claim (200 words)

Open cold. Benford's law, one sentence. The question "why,"
one sentence — the existing explanations (name them, don't
review them) each fail at a specific point. Then the claim:
the mechanism is the function epsilon(m) = log_2(1+m) - m,
the nonlinear part of the coordinate map between linear and
logarithmic mantissa. It is the spectral gap of the BS(1,2)-
induced mixed-arithmetic Markov operator on the mantissa
circle.
Convergence is exponential. The rate is a functional of
epsilon. The mechanism terminates at the concavity of the
binary logarithm.

200 words. No history, no survey, no hedging, no
cross-references to other fields. The reader knows what the
paper claims by the bottom of the first column.


### 2. Theorems, compactly stated (150 words)

Two theorems, formally stated, with no orphaned display
equations and no deferred justification.

**Theorem 1 (spectral gap).** For any nondegenerate probability
measure mu on the generators of BS(1,2), the induced random
walk projected to T = R/Z via m(x) = log_10 |x| mod 1
converges exponentially to the uniform (Benford) distribution.
The rate is bounded below by lambda >= f(epsilon, mu) > 0.

**Theorem 2 (rate identification).** The constant f(epsilon, mu)
depends on the L^2 norm of epsilon on [0,1) and on the
active-zone visit rate of the exponent process. For the
symmetric measure, the predicted rate is [value]; the measured
rate is lambda = 0.035 +/- [error].


### 3. Group and Cayley-graph setup (250 words)

BS(1,2) = <a, b | bab^{-1} = a^2>. Generator a is
multiplication by 2: a geodesic step on the binary tiling of
the Poincare half-plane, a rigid rotation of log-mantissa by
log_10 2 (irrational). Generator b is addition of 1: a
horocyclic step, a state-dependent perturbation of
log-mantissa whose nonlinear part is epsilon.

The Cayley graph is the binary tiling (Bowen 2002):
horocyclic width 1, geodesic height ln 2, every cell congruent,
non-crystallographic. The mantissa lives on the horocyclic
coordinate. Multiplication translates geodesically — no
mantissa effect. Addition translates horocyclically — and the
mantissa perturbation factors through epsilon because the
coordinate map from linear to log scale is psi(m) = log_2(1+m)
= m + epsilon(m).

This is where the reader sees *why* epsilon enters. It's not a
coincidence or an analogy. It's the coordinate Jacobian. When
you add 1 to a number and ask what happened to its mantissa,
the answer passes through log_2(1+m), and the departure from
linearity is literally epsilon. The group structure of BS(1,2)
makes this departure accumulate coherently rather than canceling.

250 words. The reader leaves this section knowing: what the
group is, what the two generators do to the mantissa, why
epsilon is the nonlinear part and not a metaphor, and what the
geometry looks like. No extra geometric excursus: if the
figure and these 250 words cannot make the geometry legible,
the paper is not ready.

### 4. Mechanism / proof (300 words)

This section is the proof, not a teaser. It does not reproduce
every Fourier-coefficient estimate, but it must carry the
actual mechanism: pure addition gives the Cesàro obstruction,
multiplication inserts the coordinate change ψ = id + ε, the
BS(1,2) relation forces that reweighting into the walk, and
positivity of ε opens the spectral gap. The main text presents
the *substrate* and the argument in one motion.

**The substrate.** A random walk on BS(1,2) with any
nondegenerate measure μ, projected to the mantissa circle
T = ℝ/ℤ via m(x) = log₁₀|x| mod 1, converges exponentially
to the uniform (Benford) distribution. The group relation
bab⁻¹ = a² encodes the interaction of addition and
multiplication algebraically: it is not reconstructed by
summation methods applied after the fact, it is *present in
the generating relations* of the group. The Riesz weighting
that Schatte had to impose analytically is produced
automatically by the group's own structure — each
multiplicative step reweights the additive history through
the coordinate map ψ(m) = log₂(1+m), and this reweighting
is what drives convergence.

**The rate.** Convergence is exponential, controlled by the
concavity of ε(m) = log₂(1+m) − m itself. The rate depends on ε
and on the visit frequency of the walk's vertical
(exponent) component to the low-depth zone where the
coordinate map has its maximal nonlinearity. For the
symmetric measure, λ ≈ 0.035/step (simulation, 10⁶ walkers,
R² = 0.99 on the exponential fit).

300 words. The reader leaves this section knowing: the group
is BS(1,2), its random walk converges to Benford, the rate
is exponential and controlled by ε, and the proof mechanism is
on the page rather than deferred. They do *not* get every
auxiliary estimate, but they do get the argument's
load-bearing steps.


### 5. Figures with captions (150 words total)

Two figures, each carrying setup that the prose would
otherwise spend words describing.

**Figure 1** (the random walk converging): shows the walk's
mantissa distribution settling into Benford equilibrium.
Caption defines op-index and BS(1,2) operationally. The
reader *sees* convergence before the prose argues it.

**Figure 2** (the Cayley graph): shows the binary tiling with
generators labeled. Caption names the group relation
bab⁻¹ = a² and maps a/b to double/add-one. The reader
*sees* the geometry before the prose invokes it.

Trust the pictures. If a sentence is describing what a
figure shows, cut the sentence. The 150-word caption budget
is split across both figures — roughly 75 words each, enough
for operational definitions and one interpretive sentence.


### 6. Hamming-framed diagnosis of prior attempts (300 words)

Now — *after* the result — turn back and diagnose the field.
Two movements inside the 300 words.

**Movement A: The addition problem (~120 words).** One clean
paragraph, not a walkthrough. Hamming (1970) identified the
asymmetry — multiplication of independent random variables
produces mantissa distributions that converge to the
logarithmic distribution, while addition does not. Schatte
(1986) proved it: no finite-order Hölder summation makes
the mantissa distributions of sums Cauchy, and convergence
requires the Riesz logarithmic mean rather than any
finite-degree arithmetic averaging. Two sentences, both
names cited, Schatte's result stated in his terms. A reader
who wants the Fourier-coefficient proof goes to Math. Nachr.
127. A reader who doesn't sees that the problem was real,
had resisted the natural hierarchy of summation methods,
and was settled analytically forty years ago.

**Movement B: The field's four attempts (~180 words).**
Hamming-score the four prior explanations against the
substrate the paper has just presented:

- Hill: identifies the fixed point, not the dynamics.
  Regresses the explanation.
- CLT-for-logs: provides a mechanism but requires iid
  conditions and gives no rate.
- Spread-across-scales: necessary condition, not a
  convergence theorem.
- Power-law mixing: genuine convergence, but algebraic.

Then the kicker, which is now the pivot sentence restated
as diagnosis: Schatte's Riesz weighting was a coordinate
change imposed on the analysis after the fact. BS(1,2)
is the algebraic substrate that produces the same
coordinate change from the operations generating the data.
The asymmetry Hamming named disappears because the group
relation bab⁻¹ = a² contains the interaction rather than
leaving it to be reconstructed.

300 words. The Schatte paragraph is the anchor — it gives
the diagnostic its analytical weight. The four-way scoring
is brisk by comparison because the reader already holds
the answer. No Fourier details, no Cauchy recognition, no
basis-vs-degree framing. Name the obstruction, name the
mechanism, and move.


### 7. Robustness and sensitivity (150 words)

This section replaces what was previously "Why BS(1,2)
specifically." The question isn't "why this group" — BS(1,2)
is the minimal algebraic model of mixed addition and
multiplication, and that's stated in the setup. The question
is: what survives perturbation inside the model and at its
boundary?

- **Biased generators:** convergence survives asymmetric
  weights (simulation: weights 0.2/0.2/0.4/0.2, walkers at
  10^1200, final L1 = 0.091). The theorem predicts this: any
  nondegenerate mu.
- **Base change:** L1-to-Benford is flat across b in [2, 40]
  (simulation). The irrationality of log_b 2 for all integer
  b > 1 guarantees this.
- **Pure addition (the boundary):** non-convergence (Schatte
  1986, confirmed by simulation). This is the *only* escape:
  remove multiplication entirely.

150 words. Three bullet points, each naming the perturbation,
the outcome, and the reason. This section tells the reader
that the result isn't fragile — it degrades only at the one
boundary (pure addition) where the theory says it must.


### 8. Conclusion (100 words)

Short. Restate the result without the scaffolding:
Hamming's asymmetry — that multiplication converges to
Benford and addition does not — disappears when the
interaction of the two operations is present as a group
relation rather than reconstructed by summation methods.
The random walk on BS(1,2) converges exponentially to the
Benford distribution. The rate is controlled by ε. The
only escape is pure addition.

100 words. No future work, no hedging. End on the
substrate. The paper's one-sentence summary: "Random walks
on BS(1,2) converge exponentially to the Benford
distribution, and the rate is controlled by the concavity
of the binary logarithm."


## The word budget

Rough allocation, 1600 words:

| Section | Words | Job |
|---------|------:|-----|
| Intro and statement of claim | 200 | Problem, function, punchline |
| Theorems, compactly stated | 150 | Formal statements, immediately usable |
| Group and Cayley-graph setup | 250 | BS(1,2), binary tiling, two generators |
| Mechanism / proof | 300 | Cesàro obstruction, ε coordinate change, visit rate |
| Figures with captions | 150 | Two figures, captions carry definitions |
| Hamming-framed diagnosis of prior attempts | 300 | What each explanation gets wrong, in bits |
| Robustness and sensitivity | 150 | What survives bias, base change, etc. |
| Conclusion | 100 | The substrate resolves the asymmetry |


### Goal 1: The prior-work diagnosis comes after the result

The earlier plan opened with the four failed explanations as
motivation: "here's what's missing, and now here's epsilon."
This allocation reverses the order: state the claim, prove it,
*then* turn around and Hamming-diagnose the prior
attempts.

Why this is better for PNAS: the reader who opens a paper
titled "Why Benford" already knows the question is open. They
don't need to be convinced that prior explanations are
inadequate — they've read them. What earns their attention is
arriving at the answer fast (200 words), seeing the machinery
(250 + 300 words), and *then* getting the retrospective
satisfaction of understanding exactly which bit each prior
attempt was missing. The diagnosis is more powerful when the
reader already holds the correct answer and can check each
prior attempt against it. It's the difference between a
detective novel (withhold the answer, build suspense) and a
Columbo episode (show the answer first, then show why no one
else found it). For a 1600-word paper, Columbo is right.

The diagnosis is "Hamming-framed": treat the correct
explanation as a codeword with four features — identified
mechanism, exponential rate, minimal conditions,
non-regressive — and score each prior attempt by which bits
it has and which it's missing:

| Explanation | Mechanism | Exp. rate | Minimal cond. | Non-regressive |
|-------------|:---------:|:---------:|:-------------:|:--------------:|
| Hill / scale-inv. | -- | -- | yes | **no** |
| CLT-for-logs | yes | **no** | **no** | yes |
| Spread-across-scales | **no** | -- | yes | yes |
| Power-law mixing | yes | **no** (algebraic) | **no** | yes |
| **This paper (epsilon)** | **yes** | **yes** | **yes** | **yes** |

"--" means the feature doesn't apply (Hill doesn't give
dynamics, so "rate" is N/A; spread-across-scales isn't a
convergence theorem, so "rate" is N/A). The table might not
appear literally in the paper — 300 words of prose can carry
the same content — but the table is the *structure* the prose
follows. Each prior attempt gets two sentences: what it
provides, and which bit is flipped. No survey, no generosity,
no "complementary." Diagnosis.

This framing also protects against the "this is known" referee.
If the result were known, one of the four cells in the bottom
row would already be filled. The table shows they aren't.


### Goal 2: The group theory stays in the main text

The group *is* the argument. The paper's claim
isn't "epsilon is correlated with Benford convergence." It's
"epsilon is the spectral gap of a specific operator on a
specific group, and that group is the algebraic model of mixed
arithmetic." A reader who doesn't see the group doesn't see
*why* epsilon enters, only *that* it enters. 250 words is
enough for:

- BS(1,2) = <a, b | bab^{-1} = a^2>. One sentence.
- Generator a: x -> 2x (geodesic on the binary tiling,
  rigid rotation of log-mantissa by log_10 2). Two sentences.
- Generator b: x -> x+1 (horocyclic step, state-dependent
  perturbation whose log-scale effect is epsilon). Two
  sentences.
- The Cayley graph is the binary tiling of the Poincaré
  half-plane. One sentence, one citation (Bowen).
- The mantissa lives on the horocyclic coordinate;
  multiplication moves along geodesics, addition moves along
  horocycles. Two sentences.

That's ~120 words of definitions plus ~130 words of
orientation. The reader walks out of this section knowing where
epsilon sits in the geometry and why the two generators have
qualitatively different effects on the mantissa.

### Goal 3: Two figures, each carrying setup

Two separate figures: the random walk converging to Benford, and the Cayley graph of BS(1,2).

Why: the figures' job is no longer to show evidence — it's
to carry definitions that would otherwise cost prose words.
The random-walk figure defines op-index and shows what
convergence looks like. The Cayley graph defines the
generators and shows the geometry. Between them, they
replace ~160 words of descriptive prose in the group-setup
and mechanism sections, which is how the word budget
absorbs two figures without expanding.

#### The figures

Two figures. Each does a different job.

**Figure 1: The random walk converging to Benford.** A
visualization of the BS(1,2) walk's mantissa distribution
converging to equilibrium under mixed arithmetic. This is
the paper's thesis made visible: the walk mixes addition
and multiplication, and the mantissa settles into the
Benford distribution. The caption carries operational
definitions — what op-index means, what BS(1,2) is in
concrete terms (double and add-one). Trust the picture to
carry the setup: the reader sees equilibrium, the caption
names the parts, and the prose doesn't need to re-describe
what the reader is already looking at.

**Figure 2: The Cayley graph of BS(1,2).** The binary tiling,
with generators labeled. Geodesic (multiplication) vertical,
horocyclic (addition) horizontal. A sample walk path. The
caption defines the two generators operationally and names
the group relation bab⁻¹ = a². This figure replaces the
250-word group-setup section's heaviest lifting — the reader
sees the geometry, the caption names the algebra, and the
prose can be shorter because the picture is doing the work.

**The discipline:** these two figures together should let the
group-setup and mechanism sections shed ~80 words of
descriptive prose each. The figures define; the prose
argues. If a sentence is describing what a figure shows,
cut the sentence.

Both figures must be legible at PNAS column width (~8.7 cm).
White backgrounds, PNAS-compatible fonts, colorblind-safe
palette. The random-walk visualization exists as diagnostic
data; it needs to be recomposed for publication. The Cayley
graph is new — draw it clean from the start.

All other figures (the epsilon bump, the four-regime shutter,
the base-agnosticism scan, the biased-walk convergence, the
state-complexity growth, the wrapped Cauchy kernels) are cut
from this paper. If one of them turns out to be indispensable,
it has to replace Figure 1 or Figure 2; there is no overflow.


## The references

15 slots. Spend them carefully. Every reference must do a job
in the text. No "see also" padding. A human must verify these.

**Must cite** (the load-bearing walls):
1. Schatte (1986) — Cesàro/Riesz convergence for mantissa sums.
   Our direct ancestor. Provides the Fourier-coefficient
   asymptotics and the Cesàro non-convergence that the proof
   extends. The single most important citation.
2. Cuno & Sava-Huss (2015) — random walks on BS(p,q). Provides
   the group-theoretic decomposition (vertical/horizontal),
   the convergence-to-boundary results, and the sublinear-speed
   estimate for the driftless case. Cited in the group setup.
3. Hill (1995) — the scale-invariance characterization. Named
   in the Hamming diagnosis.
4. Benford (1938) — the law.
5. Berger & Hill (2015) — the modern survey.
6. Bowen (2002) — binary tiling geometry. Cited in the group
   setup.

**Should cite** (context and credit):
7. Hamming (1970) — named the addition/multiplication
   asymmetry. Cited in the diagnostic paragraph alongside
   Schatte.
8. Marasa & Matula (1973) — simulative study of error
   propagation in mixed arithmetic. Independent empirical
   confirmation (from 1973) that the operator mix is the
   determining factor. Cited in the robustness section.
9. Newcomb (1881) — priority over Benford.
10. Diaconis (1977) — "sufficiently many significant digits."
    Named in the Hamming diagnosis.
11. Nigrini (1996 or 2012) — Benford in fraud detection.
12. Miller (2015) — the second major survey.

**Proof infrastructure / reserve** (at most three of these earn
space in the final 15, and only if they do work in the main text):
- Élie (1982) — the ladder-time lemma used in Cuno &
  Sava-Huss's horizontal-displacement estimate.
- Kaimanovich & Vershik (1983) — boundary theory; spectral
  gap context.
- Kontorovich & Miller — Benford convergence rates via
  Fourier methods. Cited in Miller & Takloo-Bighash (2006),
  Ch. 11, as *the* application of CLT-rate Fourier analysis
  to Benford. This is the closest prior work from the analytic
  number theory side. If they establish an algebraic rate,
  they're in the power-law column of our Hamming table. If
  they get no quantitative rate, they're in the CLT column.
  Either way, our exponential rate via BS(1,2) supersedes —
  but we need to know exactly what they proved and position
  against it.
- Tsao (1974) — leading-digit proportions via iterated
  averaging. Parallel result to Schatte via different route.
  Cited in FOURIER'S STAR.


## The significance statement

PNAS requires a 120-word significance statement for all research
articles. Even if Brief Reports are technically exempt, writing
one is a forcing function for clarity. Draft:

> Benford's law — the observation that leading digits of natural
> data follow a logarithmic distribution — has been documented
> for over a century. Existing explanations each fail at a
> specific point: scale-invariance theorems identify the fixed
> point but not the dynamics; central-limit arguments require
> conditions real data rarely satisfy and give no convergence
> rate; power-law models converge, but slowly. We identify a
> single mechanism that resolves all three failures: the function
> epsilon(m) = log_2(1+m) - m, the nonlinear part of the
> coordinate map between linear and logarithmic mantissa. We
> prove that any nondegenerate random walk on BS(1,2), the
> algebraic model of mixed addition and multiplication,
> converges exponentially to the Benford distribution at a rate
> controlled by the concavity of epsilon, and confirm the
> predicted rate in simulation. The mechanism terminates at
> the irrationality of ln 2.

That's 121 words. The four failures are compressed to three
(spread-across-scales folds into the power-law line). Epsilon
is introduced as a mathematical object, not as a CS artifact.
The last sentence names the terminus.


## The title

The title should be bald, mechanism-first, and free of coyness.
Working direction: "Benford's law from mixed arithmetic" or
"Why mixed arithmetic is Benford."
