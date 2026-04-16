# FOURIER'S STAR

No finite order of Hölder summation makes the mantissa distributions
Cauchy. Riesz logarithmic means converge. The obstruction is a change
of basis, not a change of degree.


## §1. Fourier coefficients of mantissa distributions

Let X₁, X₂, ... be i.i.d. with EX₁ = a ≠ 0 and σ² = E(X₁ − a)² < ∞.
Set Zₙ = Σᵢ₌₁ⁿ Xᵢ. For Zₙ ≠ 0 write Zₙ = ±Y·eᴷ with 1 ≤ Y ≤ e,
K integer. The distribution function Mₙ(x) of Y is the mantissa
distribution of Zₙ. Its Fourier coefficients are

    hₙ(r) = E(|Zₙ|²ᵖⁱʳ ; Zₙ ≠ 0),     r ≠ 0 integer.

Schatte, Lemma 1:

    |hₙ(r) − (|a|n)²ᵖⁱʳ| ≤ A₁ r²σ² / (a²n)

where A₁ is absolute. The leading term (|a|n)²ᵖⁱʳ has unit modulus
and argument 2πr log(|a|n), which increases without bound.

Convergence of Mₙ in sup norm would force convergence of each hₙ(r),
since g(r) = ∫ |x|²ᵖⁱʳ dG(x) is a bounded continuous functional of G
in sup norm. But hₙ(r) does not converge: its leading term rotates
with unbounded argument and O(1/n) error. Therefore Mₙ does not
converge.

(Tsao 1974, Theorem 1, establishes the same for leading-digit
proportions of the positive integers via the same iterated-averaging
structure.)


## §2. Iterated averaging of rotating coefficients

Define k-fold Cesàro means: 𝔄₀(aₙ) = aₙ and

    𝔄ₖ₊₁(aₙ) = (1/n) Σₘ₌₁ⁿ 𝔄ₖ(aₘ) .

Schatte, Lemma 6 (equation 17):

    𝔄ₖ(hₙ(r)) = (|a|n)²ᵖⁱʳ / (2πir + 1)ᵏ + Eₖ(r, n)

where

    |Eₖ(r, n)| ≤ (1/n) Gₖᵣ Σⱼ₌₀ᵏ (log n)ʲ / j!

and Gₖᵣ does not depend on n. For fixed k and r, the error vanishes
as n → ∞.

The leading term has modulus |2πir + 1|⁻ᵏ and argument
2πr log(|a|n) + k · arg(2πir + 1)⁻¹. The additive constant
k · arg(2πir + 1)⁻¹ shifts the phase but does not stop the rotation.
The modulus does not depend on n.


## §3. Phase non-convergence

Set θₙ = 2πr log(|a|n) mod 2π (for any fixed r ≠ 0). Before reduction
mod 2π, the quantity 2πr log(|a|n) → ∞.

For all sufficiently large positive integers m, there exist n with
log(|a|n) ∈ (m, m + δ) and n′ with log(|a|n′) ∈ (m + 1/2 − δ,
m + 1/2 + δ), for any δ > 0. (Once m is large enough that the spacing
log(1 + 1/n) between consecutive values is less than δ, the sequence
log(|a|n) cannot cross an interval of length δ without landing in it.)
With r = 1, the corresponding phases θₙ and θ_{n′} are within 2πδ of
0 and π respectively.

Therefore {θₙ} does not converge, and there exists ε₀ > 0 and
infinitely many pairs (n₁, n₂), with both indices arbitrarily large,
satisfying

    |θ_{n₁} − θ_{n₂}| mod 2π ≥ ε₀ .

Take ε₀ = π/2.


## §4. Coefficient separation implies distribution separation

When P(Zₙ = 0) > 0, we have Mₙ(e) < 1. Following Schatte (p. 8),
define Mₙ*(x) = Mₙ(x) + (1 − Mₙ(e)) log x. Then Mₙ*(e) = 1 and the
Fourier coefficients of Mₙ* equal those of Mₙ. The correction has
sup norm at most P(Zₙ = 0) ≤ σ²/(na²).

Push forward by t = log x to [0, 1]. Let Fₙ*(t) be the pushed-forward
distribution. Then Fₙ*(0) = 0 and Fₙ*(1) = 1 exactly. Integration by
parts:

    cₙ(r) − cₘ(r) = ∫₀¹ e²ᵖⁱʳᵗ d(Fₙ* − Fₘ*)(t)

                   = [e²ᵖⁱʳᵗ (Fₙ*(t) − Fₘ*(t))]₀¹
                     − 2πir ∫₀¹ e²ᵖⁱʳᵗ (Fₙ*(t) − Fₘ*(t)) dt .

Boundary terms: at t = 0, Fₙ*(0) − Fₘ*(0) = 0. At t = 1,
Fₙ*(1) − Fₘ*(1) = 0. Therefore:

    |cₙ(r) − cₘ(r)| ≤ 2π|r| · ‖Fₙ* − Fₘ*‖_∞

    ‖Fₙ* − Fₘ*‖_∞ ≥ |cₙ(r) − cₘ(r)| / (2π|r|) .

Returning to original distributions:

    ‖Fₙ − Fₘ‖_∞ ≥ ‖Fₙ* − Fₘ*‖_∞ − ‖Fₙ* − Fₙ‖_∞ − ‖Fₘ* − Fₘ‖_∞
                  ≥ |cₙ(r) − cₘ(r)| / (2π|r|) − σ²/(na²) − σ²/(ma²) .


## §5. The Cauchy failure

The Fourier coefficient of the k-th Cesàro-averaged distribution at
frequency r equals the k-th Cesàro mean of the Fourier coefficients
at frequency r, by linearity of integration. So cₙ(r) in §4, applied
to the k-th averaged distributions, is 𝔄ₖ(hₙ(r)) from §2.

Fix r = 1 and Hölder order k. By §2, the leading term of 𝔄ₖ(hₙ(1))
traces a circle of radius |2πi + 1|⁻ᵏ with argument
θₙ = 2π log(|a|n) + k · arg(2πi + 1)⁻¹.

By §3, there exist infinitely many pairs (n₁, n₂), both arbitrarily
large, with |θ_{n₁} − θ_{n₂}| mod 2π ≥ π/2. Two points on a circle
of radius R separated by angle φ have distance 2R sin(φ/2). For
φ ≥ π/2, sin(φ/2) ≥ sin(π/4) = 1/√2. So the leading-term difference
has modulus at least

    2 · (1/√2) · |2πi + 1|⁻ᵏ = √2 · |2πi + 1|⁻ᵏ .

The error terms |Eₖ(1, nⱼ)| vanish as nⱼ → ∞. The correction terms
σ²/(nⱼa²) from §4 also vanish. Choose n₁, n₂ large enough that
all four quantities (two error terms, two correction terms) are
together less than half of √2 · |2πi + 1|⁻ᵏ / (2π). Then

    ‖F_{n₁} − F_{n₂}‖_∞ ≥ c · |2πi + 1|⁻ᵏ

for some absolute constant c > 0. (The constant absorbs the factor
1/(2π) from the reverse bridge, the sin(φ/2) bound, and the slack
from the vanishing terms. Its value depends on the choice of
threshold but not on k, n₁, or n₂.)

For every N, there exist n₁, n₂ > N achieving this bound. The
sequence {𝔄ₖ(Mₙ)} is not Cauchy in sup norm at tolerances below
c · |2πi + 1|⁻ᵏ. To be Cauchy at tolerance ε requires

    k > log(c/ε) / log |2πi + 1| .


## §6. Riesz convergence

Define Riesz logarithmic means:

    𝔏(aₙ) = (1/log n) Σⱼ₌₁ⁿ aⱼ / j .

Schatte, Theorem 5 (equation 32):

    |𝔏(Mₙ(x)) − log x| ≤ A₉(σ²/a² + 1) / ∛(log n)

for n > 1, uniformly in 1 ≤ x ≤ e.

This bound vanishes as n → ∞. The Riesz method converges to the
logarithmic distribution with no residual. Compare with §5: k-fold
Cesàro means are not Cauchy at any finite k.

The operative difference exposed by the Schatte asymptotics is the
weighting. Cesàro averaging weights each term uniformly (by 1/n).
Riesz weights the j-th term by 1/j. Under Cesàro, the rotating
Fourier mode (|a|n)²ᵖⁱʳ is damped by the factor (2πir + 1)⁻ᵏ but
continues to rotate. Under Riesz, the 1/j weighting produces
cancellation across the phases of the rotation, and the result
converges.

The non-Cauchy property of the Cesàro hierarchy (§5) combined with
the convergence of the Riesz means (this section) shows that the
obstruction is not a rate problem but a basis problem. Increasing
the Cesàro order k iterates the same operation (uniform averaging)
to higher power. The hierarchy does not converge because it indexes
the wrong family of summation methods. Convergence requires the
qualitative change from uniform to 1/j weighting — the coordinate
change ψ(m) = log₂(1+m) whose deviation from the identity is ε.
No finite k reaches it because the Cesàro family and the Riesz
method are separated by a change of basis, not a change of degree.


## §7. The result and the gap

**Theorem.** For every finite Hölder order k, the k-th Cesàro
means of the mantissa distributions are not Cauchy in sup norm.
The separation is at least c · |2πi + 1|⁻ᵏ for an absolute
constant c > 0. Riesz logarithmic means converge. The passage
from Cesàro to Riesz requires the coordinate change
ψ(m) = log₂(1+m), whose deviation from the identity is ε.

**Corollary (conditional).** If a finite machine with state
budget q is confined to Hölder summation at order k*(q), its
worst-case error is bounded below by c · |2πi + 1|^{−k*(q)}.

**Gap.** The confinement: proving k*(q) exists as a function of
machine capacity. The machine's operations are affine
(Aff⁺(ℝ): x ↦ ax + b, a > 0). The coordinate change
ψ(m) = log₂(1+m) is not affine. Affine maps compose to affine
maps, so no finite composition produces ψ. What remains is
connecting this to a bound k*(q) on the Hölder order achievable
with q states.


## References

- Schatte, P. (1986). On the Asymptotic Logarithmic Distribution of
  the Floating-Point Mantissas of Sums. Math. Nachr. 127, 7–20.

- Tsao, N.-K. (1974). On the Distributions of Significant Digits and
  Roundoff Errors. Comm. ACM 17(5), 269–271.

- Flehinger, B. J. (1966). On the Probability that a Random Integer
  Has Initial Digit A. Amer. Math. Monthly 73, 1056–1061.

- Fainleib, A. S. (1968). A generalization of Esseen's inequality and
  its application in probabilistic number theory. Izv. Akad. Nauk SSSR
  Ser. Mat. 32, 859–879.
