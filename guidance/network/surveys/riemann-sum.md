# The Riemann-Sum Property

source: [`core/RIEMANN-SUM.md`](../../../core/RIEMANN-SUM.md)  
cited in: [`COLLECTION.md` — The Generator](../../../COLLECTION.md#chapter-2-the-generator)  
last reviewed: 2026-04-10

---

**Claim.** At `N = period`, the Monte Carlo estimate from
`bidder.cipher` equals the left-endpoint Riemann sum `R` exactly,
for any integrand and any key. Not approximately, not in
expectation — exactly. The key cancels in the sum. Every key
gives the same answer at `N = P`.

**Mechanism.** A sum over a permutation of a set equals the sum
over the set. Proof is one line: the multiset
`{π(0), …, π(P − 1)}` equals `{0, …, P − 1}` for any bijection
`π`, so `(1/P) Σ f(π(i)/P) = (1/P) Σ f(k/P)`. The gap between
`R` and the true integral `I` is a separate question, governed
by the Euler–Maclaurin expansion and depending on endpoint
cancellation for `f`. For `f(x) = sin(πx)` the gap decays as
`π / (6P²)`; for `f(x) = x` it stays stubbornly at `1/(2P)`
because `f(0) ≠ f(1)`.

**Depends on.** The integer block from
[`block-uniformity.md`](block-uniformity.md) (the set the
permutation acts on); the keyed permutation from
[`bidder-root.md`](bidder-root.md) (any permutation, any key —
the structural theorem does not care which).

**Supports.** The Monte Carlo utility claims in
[`bidder-generator.md`](bidder-generator.md); the four-layer
decomposition `E_N − I = (E_N − R) + (R − I)` in
[`red-team-theory.md`](red-team-theory.md); the theorem index
in [`tests-theory-readme.md`](tests-theory-readme.md) where
this is the most-tested theorem.

**Status.** Structural layer (`E_P = R`) proved, with the
one-line proof carrying the full weight. Quadrature layer
(the Euler–Maclaurin rate table) is deterministic analysis
from `f` and `P`. Statistical layer (finite-population
correction around `R`) is the ideal null benchmark. Coupling
layer (cipher vs shuffle null) is a measured quantity, not a
theorem — the current Feistel backend shows a ~1.5–2.5× variance
gap against the FPC prediction at intermediate `N`, recorded as
a measurement rather than fitted away.
