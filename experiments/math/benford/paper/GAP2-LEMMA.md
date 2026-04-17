# GAP2-LEMMA — WITHDRAWN

> **This draft is withdrawn.** A review identified five problems,
> two of them fatal to the framework:
>
> - **Atomic kernel.** K(x, ·) is a 4-atom mixture for each x (one
>   atom per generator choice), so K^{k₀}(x, ·) has no density
>   against Leb ⊗ counting; Rosenthal Lemma 6(ii) is inapplicable
>   because there is no density to take the pointwise infimum of.
> - **Claim (*) is false.** Starting from (Leb_T, E=0) gives
>   φ(ν) = 0 but φ(νK) ≈ 0.09 (Monte Carlo), so no bound of the
>   form φ(νK) ≤ (1 − β·ν(R))·φ(ν) can hold. Corollary:
>   Leb ⊗ counting is not invariant for K — the b-step has
>   Jacobian 10^m/(10^m + 10^{−E}) ≠ 1.
> - Plus three medium/low issues (local-time concentration
>   overstated, L² of ε is wrong kind of control for minorization,
>   β_* constant inconsistency).
>
> The **Rosenthal small-set minorization route is not salvageable
> in the TV-on-measures formulation** used below. A rebuild should
> work with the transfer operator K\* acting on absolutely
> continuous mantissa densities in a translation-invariant norm
> (BV, Sobolev H^s, or weighted Fourier), with per-visit contraction
> proved at the level of the density action rather than via kernel
> density-bounds.
>
> Left in place (not deleted) as the historical record of the wrong
> route. See FIRST-PROOF §2 for the open-gap status.

---

## (Below: withdrawn draft)

Working draft of the contraction lemma. Status: **sketch with
marked gaps** — the per-step TV contraction (*) and the small-set
minorization on R are the two technical load-bearers and need
proofs written out. The local-time estimate is classical.

A correction from earlier working notes: the mechanism is
**single-walker** ε-minorization per active-zone visit, not
two-copy Rosenthal coupling. The single-chain local time at R
scales as √n (null-recurrent 1D walk), which gives exp(−c√n).
Two independent null-recurrent copies have joint local time ~log n,
which would give *algebraic* TV decay — that's why straight
Rosenthal-with-independent-partner doesn't reproduce the sim.

---

## Preliminaries

**State space.** X = T × ℤ, where T = ℝ/ℤ is the log-mantissa
circle and ℤ is the exponent.

**σ-algebra.** B = B(T) ⊗ 2^ℤ (Borel on T, discrete on ℤ).

**Reference measure.** μ = Leb_T ⊗ counting_ℤ, σ-finite.

**Walk.** Symmetric measure on BS(1,2) generators:
P(a) = P(a^{−1}) = P(b) = P(b^{−1}) = 1/4. Induces a Markov kernel
K : X × B → [0, 1] on (X, B).

**Projection.** π_T : X → T, (m, E) ↦ m.

**Small set.** For E₀ ∈ ℕ, R_{E₀} = {(m, E) : |E| ≤ E₀}.

**Pseudo-log residual.** ε(m) = log₂(1 + m) − m on [0, 1), strictly
positive on the interior, ε(0) = ε(1) = 0,
max ε = ε(1/ln 2 − 1) ≈ 0.0861 (cf. BINADE-WHITECAPS §6).

**Notation.** For a probability ν on X, write
φ(ν) := ‖π_T ν − Leb_T‖_TV. Iterating K: ν_n = ν K^n.

---

## Main Lemma

**Lemma (stretched-exponential mantissa-marginal mixing).** There
exist constants E₀ ∈ ℕ, β_* = β_*(ε, E₀) > 0, C_* < ∞, and
n_0 ∈ ℕ such that for every probability measure ν on X with
π_T ν absolutely continuous with respect to Leb_T,

    φ(ν K^n) ≤ C_* · exp( −β_* · √n ),     n ≥ n_0.

Equivalently, the mantissa marginal of ν K^n converges to Leb_T in
total variation at stretched-exponential rate, with explicit
constant c := β_* determined by ε and by the local-time statistics
of the symmetric exponent walk on ℤ.

---

## Proof outline

The proof has three steps. Step 1 is classical; Steps 2 and 3 are
where the technical work lives.

### Step 1 (classical): local time at R scales as √n

Let (X_n)_{n ≥ 0} be the walk on X. Let L_n := #{k ≤ n : X_k ∈ R}
be the local time at R. For the symmetric BS(1,2) walk, the
exponent marginal E_n is a null-recurrent random walk on ℤ with
step distribution dominated by the a/a^{−1} increments
(±1 with probability 1/4 each, and bounded b/b^{−1} carries). By the
local central limit theorem / local time of simple random walk on ℤ,

    P(E_n = 0)  ~  c₁ / √n,      c₁ > 0 explicit.

Summing over the box |E| ≤ E₀,

    P(X_n ∈ R)  ~  (2E₀ + 1) · c₁ / √n,     n → ∞.

Therefore

    E[L_n]  =  ∑_{k=0}^{n-1} P(X_k ∈ R)  ~  c_R · √n,

with c_R = 2 (2E₀ + 1) c₁ (up to constants from the Abel sum). By
concentration of local times (classical, Borodin-Salminen or
Révész), L_n / √n converges in probability to its mean, and for
any δ > 0,

    P( L_n ≥ (1 − δ) c_R √n )  →  1     as n → ∞.

**No gap here.** This is standard random-walk theory.

### Step 2 (technical): per-step TV contraction when the walker is in R

**Claim (*).** There exists β_* = β_*(ε, E₀) > 0 such that for
every probability ν on X,

    φ(ν K) ≤ (1 − β_* · ν(R)) · φ(ν).

**Proof sketch.** Decompose ν = ν_R + ν_{R^c}, where ν_R is the
restriction of ν to R (a sub-probability with mass p := ν(R)) and
ν_{R^c} is the restriction to X \ R (mass 1 − p). Then

    ν K = ν_R K + ν_{R^c} K.

Take π_T:

    π_T(ν K) = π_T(ν_R K) + π_T(ν_{R^c} K).

**The R^c contribution.** Outside R, the walker has |E| > E₀. For
E₀ large enough (to be fixed), the b/b^{−1} steps are
approximately identity on the mantissa (E >> 0) or snap the
walker to (0, 0) (E << 0 — but this re-enters R, accounted for
via p). The a/a^{−1} steps act on the mantissa by rotation by
±log₁₀ 2. Rotation is an isometry of TV on T:

    ‖π_T(ν_{R^c} K) · (1/(1−p)) − Leb_T‖_TV
      =  ‖π_T ν_{R^c} · (1/(1−p)) − Leb_T‖_TV          (rotation isometry)
      =: φ_{R^c}.

**The R contribution.** For the walker in R (|E| ≤ E₀), the b-step
at low depth produces a mantissa perturbation controlled by ε.
Specifically: if the walker is at (m, E), one b-step gives
mantissa m' = frac(log₁₀(10^m + 10^{−E})). The density of this
kernel, as a function of m with E fixed and |E| ≤ E₀, is bounded
below on a non-trivial subset of T by a quantity proportional to
ε' (i.e., the derivative of ψ(m) = log₂(1+m) deviated from
identity). Over a bounded number k₀ of b and a steps, we obtain
a small-set minorization

    K^{k₀}(x, ·) ≥ β · Q(·)        for all x ∈ R,

where Q is a probability on X with a density on T bounded below
by a positive constant on an interval of positive length, and

    β = β(ε, E₀, k₀) = ∫_X inf_{x ∈ R} k^{k₀}(x, y) dμ(y)

(Rosenthal Lemma 6(ii); density k^{k₀} exists because the b-step
smooths on T). By the standard argument (Meyn-Tweedie Thm 5.2.4,
or direct), this yields the pointwise contraction

    ‖π_T(δ_x K^{k₀}) − Leb_T‖_TV ≤ (1 − β) · ‖π_T δ_x − Leb_T‖_TV
                                 + β · ‖π_T Q − Leb_T‖_TV'

where the last term is bounded by a constant depending on how
close Q already is to Leb_T. Averaging over ν_R/p gives, for the
per-step (k₀ = 1 after appropriate reduction or replacing n by
n/k₀),

    ‖π_T(ν_R K / p) − Leb_T‖_TV ≤ (1 − β_*) · ‖π_T ν_R / p − Leb_T‖_TV
      =: (1 − β_*) · φ_R.

**GAP.** Writing this out rigorously — constructing Q, computing β
as an explicit functional of ε's L² norm via Parseval from
BINADE-WHITECAPS §§7–8, and verifying the minorization holds
uniformly on R for k₀ = 1 or a finite k₀ — is the technical load
this step carries. The shape of the computation is standard
(Meyn-Tweedie Ch. 5); the content specific to our setting is
(a) ε > 0 on (0,1) giving β > 0 and (b) an explicit lower bound
β_* ≥ β_*(ε) that we can state as a functional of ‖ε‖²_{L²}.

**Combining R and R^c contributions.** By triangle inequality,

    φ(ν K) ≤ p · (1 − β_*) · φ_R + (1 − p) · φ_{R^c}.

Because φ_R and φ_{R^c} are both bounded by φ(ν) · (some const),
after routine work one gets

    φ(ν K) ≤ (1 − β_* · p) · φ(ν)

which is Claim (*). The routine work here is bounding the
cross-terms in the triangle inequality using boundedness of
π_T Q near Leb_T. **GAP** is making this precise.

### Step 3 (iteration): stretched-exp bound

From (*),

    φ(ν_n) = φ(ν K^n) ≤ ∏_{k=0}^{n-1} (1 − β_* · ν_k(R)) · φ(ν).

Taking logs and using log(1 − x) ≤ −x for x ∈ [0, 1),

    log φ(ν_n) / φ(ν)  ≤  −β_* ∑_{k=0}^{n-1} ν_k(R)  =  −β_* · E[L_n]

where we used ∑_k P_ν(X_k ∈ R) = E[L_n]. By Step 1, E[L_n] ~ c_R √n, so

    log φ(ν_n) / φ(ν)  ≤  −β_* · c_R · √n · (1 − o(1)),

i.e.,

    φ(ν_n) ≤ C_* · exp( −β_* · c_R · √n )     for n ≥ n_0.

Set c := β_* · c_R. □ (modulo the two gaps in Step 2).

---

## Discussion

**Where the √n comes from.** Not from two-copy joint local time
(log n scaling), but from single-chain local time at R (√n
scaling). The mechanism is: each step spent in R contracts the
mantissa TV by factor (1 − β_*); steps outside R do not contract
it (rotation is isometric); total contraction is geometric in the
time spent in R, which scales as √n. Hence exp(−c√n).

**What c is.** c = β_* · c_R where β_* is the small-set
minorization constant (function of ε, E₀, k₀) and c_R is a
random-walk constant (function of E₀ and the step distribution,
classical). For the sim parameters: measured c ≈ 0.55 at
N = 10⁷ (gap 3 phase 1). Theoretical c should match this
neighborhood.

**What's not proven yet.**

- **(G1)** Explicit construction of Q and β in Step 2. This is
  the heart of the technical work. The BINADE-WHITECAPS §§7–8
  Fourier coefficients of ε give us ‖ε‖²_{L²} in closed form; the
  challenge is wiring that into a minorization density bound.
- **(G2)** Rigorous handling of cross-terms in the per-step TV
  contraction, specifically when the walker's mantissa
  distribution is concentrated near Leb_T and the rotation of
  R^c mass matters.
- **(G3)** The upper bound constant C_* and the starting
  threshold n_0 should be explicit. Routine but needs care.

**What's optional for PNAS.** The paper's claim gate asks for
"λ ≥ f(ε, μ) > 0" as a lower bound, not exact identification. The
lemma as stated gives that — a lower bound c ≥ c(ε, μ) > 0. We do
NOT need to identify c exactly to submit.

**What's outside this lemma.** (i) Biased-walk case — needs a
separate lemma with the two-regime structure documented in
FIRST-PROOF §4. (ii) The base-agnosticism claim (L1 flat across
b ∈ [2, 40]) — this is a corollary of the fact that log_b 2 is
irrational for all b > 1 and plays no role in the symmetric-case
theorem.

---

## Next steps

1. Write out (G1) rigorously. BINADE-WHITECAPS §8 gives the
   Fourier coefficients of ε; need to convert these into a
   density lower bound for K^{k₀}(x, ·) on R. Pick E₀ = 2 or 3 as
   a clean test case.
2. Write out (G2) — the cross-term bookkeeping in Step 2. This
   is grunt work, not research.
3. Verify the measured c ≈ 0.55 is in the ballpark of the
   theoretical c = β_* · c_R. If not, revisit β_*.
4. Consider whether to state the lemma for measurable ν (not
   just absolutely continuous) — this matters for initial
   conditions with singular mantissa marginal (e.g., point
   masses). For the PNAS statement, absolutely continuous is
   sufficient since we're talking about "data from the wild."
