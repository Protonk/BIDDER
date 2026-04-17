# PNAS Plan

Target: PNAS Brief Report. ~1600 words, 2 figures, 15
references. This paper either closes in that space or not at all.

## Core drafting discipline

Columbo. Show the answer first, then show why no one else
found it. 

![meirl.jpg](./meirl.jpg)


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


## Why the paper exists

Benford's law has been "explained" many times. Every existing
explanation fails in a specific, nameable way, and the failures
are different enough that no two accounts cover each other's
gaps. This is our leverage. The paper doesn't enter a crowded
field — it enters a field where everyone agrees the question is
open and each prior attempt demonstrates *which part* is hard.

The four failures (Hill, CLT-for-logs, spread-across-scales,
power-law mixing) are diagnosed in detail in Section 6 of
the rhetorical arc. In the Columbo structure, they come
*after* the result: the reader arrives at the diagnosis
already holding the answer and checks each prior attempt
against it.


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

The main text must serve the first two groups. To do that, it
has to satisfy the third: the referees.

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

Every citation must do a specific job — naming what a prior
result did, what it didn't do, or what machinery the proof
rests on. No citation is there to signal familiarity. A
skeptical reader sees literature command not from density but
from precision: each name appears because the paper needs it,
and what the paper needs from it is stated. Much may be
needed. 


## The proof problem

We have three sources that triangulate on a cleaner proof story, and the mechanism section of the paper should reflect this. That isn't a problem. The problem is we need to get there in ~700 words, accessible to a mathematics undergrad. 

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

- No finite Hölder order damps the rotating leading term. The
  residual at order k is bounded below by c · |2πi+1|^{-k}.
  The hierarchy never closes.
- The passage from Cesàro non-convergence to Riesz convergence
  is the coordinate change ψ(m) = log_2(1+m). Its deviation
  from the identity is ε.
- **The obstruction is a change of basis, not a change of
  degree.** Iterating uniform averaging (Cesàro) to higher
  order indexes the wrong family. Convergence requires the
  qualitative change to 1/j weighting — the coordinate change
  ε.

BINADE-WHITECAPS §7 sharpens the backbone to an identity:
the accumulated density defect E(t) = φ(t) − t equals −ε(m)
after the coordinate change. The departure from Benford *is*
ε, not merely controlled by it. The Fourier coefficients of
ε are exactly computable (§8), so the lift to L^2 is Parseval,
not an estimate.

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

### What must be true before we draft

These are in priority order.

1. **The proof must close.** Specifically: the wrapped-Cauchy
   comparison (or identity) in step (b), and the biased-walk
   treatment in step (c). If either is shaky, the theorem
   statement has to change, and the rhetoric changes with it.
   Do not draft around the gap. 

2. **The rate prediction must be quantitative.** The simulation
   gives lambda ~ 0.035. The theorem gives lambda = 2*pi*gamma*rho.
   We need gamma and rho as explicit numbers for the symmetric
   walk, and the predicted lambda needs to be in the same
   neighborhood as 0.035. 

## Specific risks

- **~~The Fourier-coefficient route must connect to the L^2
  rate.~~** Resolved. BINADE-WHITECAPS §7 gives the identity
  E(t) = φ(t) − t = −ε(m): the accumulated density defect
  *is* ε (up to sign and coordinate change). The lift from
  per-frequency to L^2 is this identity plus Parseval — no
  integration-by-parts bridge to sharpen. The Fourier
  coefficients of δ(t) = 2^t ln 2 − 1 are exactly computable,
  so the L^2 norm of ε is available in closed form. This
  justifies Theorem 2's "f(ε, μ) depends on the L^2 norm of
  ε" — the L^2 norm is, via Parseval, the ℓ^2 norm of the
  Fourier coefficients of the density defect. Not arbitrary;
  forced by the coordinate change.
  **Measure change (resolved in principle).** §§7–8 are
  formulated against Lebesgue measure on the circle. The PNAS
  setting uses the walk's stationary measure μ with density ρ
  against dt. The identity E = −ε∘φ is coordinate-theoretic
  and survives. The Parseval-based norm changes: ‖E‖²_{L²(μ)}
  = ∫|E(t)|² ρ(t) dt instead of ‖E‖²_{L²(dt)}. But ρ is
  bounded above and below — the stationary distribution is
  Benford, which is bounded on the log-mantissa circle — so
  the two L² norms are equivalent with constants ρ_min and
  ρ_max (Radon–Nikodym). The bound carries over with exactly
  a constant change. This is bookkeeping, not a gap.

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
  exponential convergence (λ ≈ 0.035/step). Schatte studies
  iid sums (pure addition), not mixed arithmetic. The mixed
  walk's multiplicative steps apply the coordinate change
  stochastically at every step, not as a summation weight.
  The exponential rate is the spectral gap of the transfer
  operator, not the Riesz rate. BINADE-WHITECAPS §§7–8 now
  give exact Fourier coefficients of ε, so the L^2 norm
  controlling the rate is computable — the gap between
  Schatte's rate and ours should be quantitatively
  accountable, not just conceptually explained.

- **The gap identification.** Is the spectral gap "a functional
  of ε" or "bounded below by a functional of ε"? Both are
  publishable. BINADE-WHITECAPS §8 strengthens the lower-bound
  path: ε controls the entire Fourier tail of the defect,
  giving λ ≥ f(ε, μ) > 0 rigorously without needing the exact
  gap. The stronger identification (exact) may follow if the
  Cesàro-to-Riesz conversion rate is directly computable from
  ε, but the lower bound is now available without it.

- **Operator-language precision.** See the claim gate below.


## The failure modes

What kills the paper:

- **"This is known."** A referee who works on random walks on
  solvable groups may feel that exponential mixing on BS(1,2) is
  folklore. Defense: the four-failure diagnosis in Section 6 is
  the evidence. If the result were known, one of those four
  attempts would have settled the question. None has. The
  contribution is the rate identification plus the unification
  of four failure modes under one function.

- **"The proof isn't actually there."** In a 1600-word paper with
  no supplemental escape hatch, every sentence in the mechanism
  section has to carry proof weight. If the core implication
  relies on a deferred lemma, omitted estimate, or "see elsewhere"
  move, the paper will read like a claim in search of a proof.

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
one sentence — the existing explanations each fail at a
specific point. Then the claim: the mechanism is the function
epsilon(m) = log_2(1+m) - m, the nonlinear part of the
coordinate map between linear and logarithmic mantissa. It is
the spectral gap of the BS(1,2)-induced mixed-arithmetic
Markov operator on the mantissa circle. Convergence is
exponential. The rate is a functional of
epsilon. The mechanism terminates at the concavity of the
binary logarithm.

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

This is where the reader sees *why* epsilon enters. It's the coordinate Jacobian. When
you add 1 to a number and ask what happened to its mantissa,
the answer passes through log_2(1+m), and the departure from
linearity is literally epsilon. The group structure of BS(1,2)
makes this departure accumulate coherently rather than canceling.

### 4. Mechanism / proof (300 words)

This section must carry the actual mechanism: pure addition gives the Cesàro obstruction,
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

### 5. Figures with captions (150 words total)

Two figures, each carrying setup that the prose would
otherwise spend words describing.

**Figure 1** (convergence rates, log-log): titled
"Convergence to Benford requires mixing." Single panel,
log-log axes, three curves: addition only (flat — no
convergence), alternating add/mult (straight line —
algebraic decay), mixed BS(1,2) (concave down — exponential
convergence). Direct curve labels, no legend box. A dotted
line marks the finite-sample L₁ floor. The log-log format
is the argument: the three regimes have three qualitatively
different *shapes*, not just three speeds. A reader who
sees the figure already holds the theorem's content — mixing
is the condition, and the rate is exponential. Caption
defines L₁ distance to Benford, names the three regimes
operationally (±1, sequenced add-then-mult, simultaneous
¼-probability each), and states N = 50,000 walkers.

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
(1986) proved it: finite-order Hölder summation damps the mantissa Fourier
coefficients' modulus but leaves the rotating leading term
intact, and convergence requires the Riesz logarithmic mean
rather than any finite-degree arithmetic averaging. Two sentences, both
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
substrate.


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


### Design rationale: two figures, each carrying setup

Two separate figures: the L₁ convergence plot and the
Cayley graph of BS(1,2).

Why: the figures' job is no longer to show evidence — it's
to carry definitions and claims that would otherwise cost
prose words. The convergence figure (log-log, three curves)
carries the theorem's content visually: three regimes, three
qualitatively different curve shapes, the title itself
stating the claim. The alternating-add/mult curve does
double duty — it appears in both the figure and the
robustness section, showing that having both operations is
necessary but not sufficient, and that the figure already
demonstrates the sensitivity boundary. The Cayley graph
defines the generators and shows the geometry. Between them,
they replace ~160 words of descriptive prose in the
group-setup and mechanism sections, which is how the word
budget absorbs two figures without expanding.

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
- Kontorovich & Miller — asymptotic Benford behavior in
  special analytic settings via Gaussian limit laws for
  logarithms, Poisson summation, and equidistribution.
  Cited in Miller & Takloo-Bighash (2006), Ch. 11, as a
  Fourier-analysis route to Benford. This is the closest prior
  work from the analytic number theory side, but it belongs
  with the CLT/Fourier line of the Hamming diagnosis, not the
  power-law line: their method is system-specific and
  asymptotic, and does not identify the mixed-arithmetic
  mechanism or furnish the exponential rate proved here.
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


## The claim gate

Two bins only. The title, intro, theorem statement,
significance statement, conclusion, and figure captions may
use only language from the first bin.

**Goes in the paper**
- The BS(1,2) mixed-arithmetic walk converges exponentially to
  Benford.
- The rate satisfies lambda >= f(epsilon, mu) > 0.
- Epsilon is the nonlinear coordinate term that controls the
  rate.
- The theorem is for BS(1,2), not for "mixed arithmetic in
  general."

**Stays out of the paper**
- Epsilon is the spectral gap.
- The operator is a contraction.
- Exact gap identification.
- Any statement broader than the BS(1,2) theorem unless it is
  explicitly marked as conjecture or remark.

**Promotion test.** A claim moves from "stays out" to "goes in"
only if the paper can answer immediately and precisely: which
operator, on what function space, in what norm, and whether the
statement is exact or only a lower bound.


## The title

The title should be bald, mechanism-first, and free of coyness.
Working direction: "Benford's law from mixed arithmetic" or
"Why mixed arithmetic is Benford."
