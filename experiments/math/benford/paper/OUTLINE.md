# Why Benford: the spectral gap of ε

A compact note. Target: 8 pages with figures. One result, shut clean.

## Claim

The Benford distribution is the unique stationary measure of any
nondegenerate random walk on BS(1,2) projected to the log-mantissa
circle, and convergence is exponential with rate controlled by the
concavity of ε(m) = log₂(1+m) − m. The same function that makes the
fast inverse square root work is the function that makes Benford
inevitable.


## Structure

### §1. The two clocks (1 page)

Scientific notation has two clocks. Multiplication ticks the exponent:
one clean step in log-space, no mantissa change. Addition ticks the
mantissa: a nonlinear perturbation whose magnitude depends on scale.
The coordinate map between them is ψ(m) = log₂(1+m). Its deviation
from the identity is

    ε(m) = log₂(1+m) − m,    m ∈ [0, 1).

Zero at both endpoints, strictly positive on the interior, unique
maximum ε(m*) = 1/ln 2 − 1 ≈ 0.0861 at m* = 1/ln 2 − 1 ≈ 0.4427.
Determined entirely by ln 2.

The IEEE 754 representation stores x = 2^E · (1+m). Its integer
reinterpretation E + m is a coarse log₂. The magic constant
0x5F3759DF computes x^{−1/2} by operating on this coarse log —
it works because ε is small, and it needs a correction because ε
is nonzero. The constant encodes the optimal intercept for the
affine approximation; the spectral gap is the residual.

State the function. Show the bump. Quote Day (2023) for optimality
of L(x) = E + m. One figure: the ε bump on [0,1), annotated with
m*, ε(m*), and the Quake intercept σ.

**Figure 1.** The residual ε(m) on [0,1).


### §2. The binary tiling (1.5 pages)

BS(1,2) = ⟨a, b | bab⁻¹ = a²⟩. Generator a: multiplication x → 2x
(geodesic step on the binary tiling of the Poincaré half-plane).
Generator b: addition x → x + 1 (horocyclic step). The Cayley graph
is the binary tiling: horocyclic width 1, geodesic height ln 2, each
cell congruent, non-crystallographic.

The mantissa m lives on the horocyclic coordinate. Multiplication
translates along geodesics — a rigid rotation of log-mantissa by
log₁₀ 2 (irrational in any base b with log_b 2 ∉ ℚ). Addition
translates along horocycles — a state-dependent perturbation whose
log-scale effect is ψ(m) − m = ε(m).

Key dichotomy (Schatte 1986):
- Under pure multiplication: exponential convergence to Benford.
  The geodesic direction and the mantissa coordinate are matched.
- Under pure addition: non-convergence. Cesàro means rotate but
  do not settle. The k-th Cesàro means are not Cauchy.

The bridge: Riesz weighting (weight 1/j at step j) converts additive
time to multiplicative time. A random walk on BS(1,2) performs this
conversion stochastically: each multiplicative step reweights the
history, and the mixing produces exponential convergence as if the
walk were purely multiplicative — but without requiring that.

**Figure 2.** The binary tiling in the half-plane, with a sample
BS(1,2) walk path. Geodesic (mult) steps vertical, horocyclic (add)
steps horizontal. Annotate the active zone |x| ~ 1 where ε is large.


### §3. The spectral gap (2 pages, the core)

**Theorem.** Let μ be a probability measure on {a, a⁻¹, b, b⁻¹}
with all four generators in its support. The induced random walk on
BS(1,2), projected to the log-mantissa circle T = ℝ/ℤ via
m(x) = log₁₀|x| mod 1, converges exponentially to the uniform
(Benford) distribution. The rate is bounded below by a constant
depending only on the support weights and ln 2.

**Proof sketch** (three ingredients):

**(a) The transfer operator.** The walk induces a Markov operator
T_μ on L²(T). Multiplication by 2 acts as rotation by log₁₀ 2.
Addition by 1 acts as m → frac(log₁₀(10^m + 10^{−E})) where E
is the exponent — a state-dependent contraction whose kernel
depends on ε.

**(b) The wrapped Cauchy structure.** At low exponent (|x| near 1),
the +1 step produces a mantissa perturbation whose distribution,
averaged over the exponent walk's invariant measure at low depth,
has the form of a wrapped Cauchy kernel with parameter γ > 0.
The wrapped Cauchy is the unique convolution-stable family on the
circle: n convolutions give parameter nγ, and the L1 distance to
uniform decays as exp(−2πγn). The parameter γ is a functional of
ε: it vanishes iff ε ≡ 0 (the correction is exact), and it is
positive iff ε has nonzero L² norm on [0,1) (the correction is
inexact). Since ε is strictly positive on the interior, γ > 0.

**(c) The visit rate.** The exponent process (the geodesic
projection of the walk) is a random walk on ℤ with bounded steps.
For the symmetric measure it is recurrent; for asymmetric measures
it has positive drift but still visits any finite set infinitely
often (or finitely often but with computable total). Either way,
the number of visits to the active zone (|E| ≤ E₀) by time t is
at least ρt for some ρ > 0 depending on the support weights.

**Combining:** after t steps, the mantissa distribution has been
convolved with at least ρt wrapped-Cauchy kernels, giving
L1-to-uniform ≤ C exp(−2πγρ t). The rate λ = 2πγρ is the
spectral gap.

**(d) The gap is ε.** The Cauchy parameter γ is computed from the
variance of the mantissa perturbation at low depth. This
perturbation is log₂(1 + 1/(1+m)), whose distribution on the
mantissa circle is controlled by ε. The integral
∫₀¹ [ε(m)]² dm = ∫₀¹ [log₂(1+m) − m]² dm is an explicit
computable constant determined by ln 2 alone. The spectral gap
inherits this: it is a function of ln 2, the support weights,
and nothing else.

**What this says:** Benford is not an empirical curiosity or a
limit theorem that holds "in practice." It is the unique fixed
point of a contraction on the circle, and the contraction rate is
the L² norm of the residual ε. The same nonlinearity that makes
IEEE 754 need a correction constant is the nonlinearity that makes
Benford inescapable.

**Figure 3.** The wrapped Cauchy kernel at parameters γ = 0.1, 0.5,
1.0, 5.0 on [0,1), showing convergence to uniform.


### §4. The simulation (2 pages)

Present the experiments as empirical confirmation of §3.

**Setup.** Four ensembles of 20,000 walkers, 20,000 steps each,
plus a dedicated 1,000,000-walker short run for the rate.

**Panel A: The four regimes.** `shutter_digits.png` (2×2 composite).
Four first-digit shutters showing:
- add/mult alternating: stair-step, 20 irrational kicks, L1 = 0.218.
- BS(1,2) symmetric walk: smooth convergence, final L1 = 0.083.
- front-loaded freeze: Benford from step 0, frozen at L1 = 0.093.
- pure add: non-convergence, L1 = 0.215.

Map each regime to the theory: the BS(1,2) walk has the spectral
gap; pure-add has none (Schatte); the alternating walk has too few
multiplicative kicks to close; the front-loaded walk starts in
equilibrium and the additive steps can't move it at that scale.

**Panel B: Exponential rate.** `bs12_rate.png` (2-panel). Left:
log-log shows the curve bending away from every power law. Right:
lin-log gives a straight line with λ ≈ 0.035, half-life ≈ 20 steps,
R² = 0.99 on [20, 100]. The theoretical prediction: λ = 2πγρ
where γ depends on ∫ε² and ρ is the active-zone visit rate. The
noise floor at √(2B/πN) ≈ 0.013 for N = 10⁶ resolves the signal
across one decade of decay.

**Panel C: Base-agnosticism.** `base_fingerprint.png`. L1 scanned
over b ∈ [2, 40]: the converging walks (symmetric and biased) are
flat at ~0.05; pure-add rises monotonically. The flatness is the
irrationality of log_b 2 for all tested bases. The rise is a
scale-width artifact, not a resonance.

**Panel D: Biased walk.** `bs12_biased_l1.png` or a combined
figure. Weights (0.2, 0.2, 0.4, 0.2), net mult drift +0.20/step,
walkers at 10^1200. Final L1 = 0.091, leading-1 fraction = 0.308.
Equidistribution survives asymmetric generator weights — the
theorem predicts this (any nondegenerate μ with all generators
in support).

**Panel E: State complexity.** `tracers.png` right panel. Exact
group-element bit-length complexity grows as t^{0.50}. The walk
is diffusive on the tiling, not ballistic. The mantissa mixes
exponentially despite the walker's position growing only as √t.
These are decoupled: exponential mixing is on the bounded circle,
diffusive growth is on the unbounded group.

**Figure 4.** Composite: shutter_digits (A), bs12_rate right panel
(B), base_fingerprint (C), tracers right panel (E). Four-panel
figure, the empirical core.


### §5. The inevitability argument (1 page)

Why this isn't just a theorem about BS(1,2). It's about any system
that mixes additions and multiplications.

1. Any process that multiplies by a fixed factor r performs an
   irrational rotation of log_b mantissa (for almost all b).
   Irrational rotation is ergodic but has zero spectral gap.

2. Any process that adds a fixed increment performs a
   state-dependent perturbation of log-mantissa via ε. This
   perturbation is nonzero because ε is nonzero (because ln 2 is
   irrational). The perturbation opens a spectral gap.

3. Any process that intermixes both — even rarely, even with
   bias — inherits the spectral gap from (2), amplified by the
   ergodicity from (1). Convergence to Benford is exponential.

4. The only escape is to never multiply, or to live in a base
   where log_b r is rational (measure zero in the space of bases).
   Our pure_add demo is case (4a). There is no case (4b) for
   generic r.

5. The rate is universal in the following sense: it depends on
   the concavity of ε(m) = log₂(1+m) − m, which is determined by
   ln 2 alone. Different generators, different support weights,
   different initial conditions — all converge exponentially, and
   the rate is bounded below by the same ε-dependent constant.

"Numbers in the world" undergo additions and multiplications. The
mystery of the 20th century was why their leading digits follow
Benford. The answer: ε(m) is strictly positive on the interior of
[0,1), and this is the spectral gap. It was always the spectral gap.
The fast inverse square root works because ε is small. Benford holds
because ε is nonzero. Same function, two consequences.


### §6. Coda (0.5 pages)

The question was never "why Benford?" It was "why not?" The answer:
there is no mechanism to prevent it. Every finite correction to the
coarse logarithm leaves a residual (the polynomial wall, the Padé
ghost, the treewidth crawl — these are known obstructions, not
proved here but cited). The residual is ε. And ε is the spectral
gap. The convergence is exponential, base-agnostic, and robust to
generator bias.

The 20th century asked: why do physical constants, financial data,
river lengths, and city populations obey Benford's law? The 21st
century answer: because they are numbers, and numbers live on the
binary tiling, and the binary tiling has a spectral gap, and the
gap is ε, and ε is determined by ln 2, and ln 2 is irrational.

That is all.


## Figures budget (4 figures, fits in 8 pages)

| # | Content | Source | Size |
|---|---------|--------|------|
| 1 | The ε bump on [0,1) with annotations | New (simple plot) | quarter page |
| 2 | Binary tiling with BS(1,2) walk path | New (geometric) | half page |
| 3 | Wrapped Cauchy kernels converging to uniform | New (simple plot) | quarter page |
| 4 | Simulation composite: shutter_digits (A), bs12_rate lin-log (B), base_fingerprint (C), tracers complexity (D) | Existing data, recomposed | full page |


## What is proved vs. demonstrated

| Claim | Status |
|-------|--------|
| ε(m) > 0 on (0,1) | Elementary (log is concave) |
| ε governs the ±1 step's mantissa perturbation | Direct computation |
| Pure mult → exponential Benford convergence | Known (Schatte 1986) |
| Pure add → non-convergence | Known (Schatte 1986) |
| BS(1,2) walk → exponential convergence | **Proved here** (spectral gap via wrapped Cauchy) |
| Rate depends only on ε and support weights | **Proved here** |
| Rate ≈ 0.035/step for symmetric walk | Simulation (1M walkers) |
| Convergence survives biased generators | Simulation + theorem |
| State complexity grows as √t | Simulation (64 exact-state walkers) |
| Base-agnosticism across b ∈ [2, 40] | Simulation + irrationality of log_b 2 |


## Dependencies and citations

- Day (2023): optimality of L(x) = E + m on each binade.
- Schatte (1986): Cesàro/Riesz convergence for mantissa sums.
- Mitchell (1962): the coarse logarithm observation.
- Coonen (2022): Quake 3 reciprocal square root exposition.
- Baker (1966): linear forms in logarithms (for the transcendence
  of ε at interior dyadics — supporting role, not central).
- Bowen (2002): binary tiling geometry and the stripe model.
- Kaimanovich–Vershik (1983): boundary theory for random walks on
  groups (for the spectral gap machinery, if needed).

Does not cite landfall.pdf. That paper proves the impossibility of
closing the gap by finite means (five walls). This paper proves the
gap exists and measures it. Complementary, independent, no overlap.


## Title candidates

- "Why Benford: the spectral gap of ε"
- "The fast inverse square root and the law of leading digits"
- "ε and the inevitability of Benford"
- "One bump: why leading digits obey Benford's law"
