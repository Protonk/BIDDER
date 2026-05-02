# Sport: The N=P Riemann-Sum Identity

**Date entered.** 2026-05-01

**Category.** Sport.

## Description

![Dark near-black background. A single panel with a logarithmic horizontal axis labelled "sample size N" running from about 5 to 2300, and a linear vertical axis labelled "MC estimate of ∫ sin(πx) dx". 25 thin trajectories in a viridis-palette colour scheme (deep purple through teal to bright yellow) wiggle across the plot, varying widely at low N and progressively narrowing toward a single point at the right at N=2000. A yellow circular marker sits at that convergence point. A yellow dashed horizontal line passes through the marker, labelled "R = 0.636620, true ∫ = 2/π (gap = 1.3e-07)". A faint dotted gray vertical line at N=2000 is labelled "N = P = 2000". The top-left has a dark inset box reading "25 keys → one point / spread at N = P: 2.66e-15 / (machine ε; functionally zero)". Title: "Sport: The N=P Riemann-Sum Identity — 25 keys, one destination".](../experiments/bidder/unified/sport_riemann_emblem.png)

`bidder.cipher(P, key)` is a keyed pseudorandom permutation of
`{0, 1, …, P − 1}`. Used as a Monte Carlo sampler over `[0, 1)` via
`f(π(i) / P)`, it produces a prefix mean

    E_N(key) = (1/N) Σ_{i=0}^{N-1} f(π(i) / P).

For `N < P` the prefix mean is a statistical estimate whose
fluctuation around the population mean depends on the cipher's PRP
quality and approximates the finite-population correction
`(P − N)/(P − 1)`. At `N = P`, all of that machinery vanishes:

    E_P(key) = (1/P) Σ_{k=0}^{P-1} f(k / P)  =  R(f, P)

— exactly, for any `f`, any `P`, any `key`. The proof is one line.
`π` is a bijection of `{0, 1, …, P − 1}`, so `{π(0), …, π(P−1)}` is
the same multiset as `{0, …, P−1}`, so the sum is the same.

The cipher's apparatus — Feistel network, key schedule, round
structure, the entire engineering effort that goes into making the
cipher pseudorandom — is irrelevant at `N = P`. Any bijection of
`[0, P)` has this property. The cipher is one specific bijection per
key, and the bijection's whole identity is consumed by the proof in
the act of being a bijection at all.

This is sport-shaped in the cabinet's sense. At `N < P` the cipher
behaves a-typically (it samples without replacement, the FPC sets the
ideal benchmark, the Feistel approximates the FPC at ~1.5–2× the
ideal RMSE). At `N > P` the question doesn't arise (no more grid
points). At exactly `N = P` the cipher's entire pseudorandom content
is in superposition with every other key's pseudorandom content, and
they all collapse to the Riemann sum. Alone in its neighbourhood.

## Evidence

- `generator/RIEMANN-SUM.md` — full statement, one-line proof, and the
  three-layer breakdown (structural / quadrature / statistical) that
  separates this identity from its surrounding statistical claims.
- `tests/theory/test_riemann_property.py` — structural-layer test:
  key-independence across favorable and adversarial integrands;
  direct-`R` match.
- `tests/theory/test_quadrature_rates.py` — quadrature layer:
  Euler-Maclaurin error rates as assertions. No cipher invoked.
- `tests/theory/test_fpc_shape.py` — statistical layer at `N < P`,
  where the cipher's PRP quality is what determines the gap from
  ideal.
- `experiments/bidder/unified/riemann_proof.py` — four-panel
  diagnostic: 10 keys converging to the same `N = P` value; 200-key
  histogram showing zero spread; Riemann error vs `P`.
- `experiments/bidder/unified/adversarial_integrands.py` — sin, x,
  √x, step. Quadrature bias varies by `f`; key-independence does not.
- `experiments/bidder/unified/sport_riemann_emblem.png` — emblem.
  Single panel, 25 keys producing running MC estimates of
  `∫₀¹ sin(πx) dx` over `N` on log-x linear-y. The 25 trajectories
  wiggle differently across `N < P` and all land on a single point
  at `N = P = 2000` — the Riemann sum `R = 0.636620`. Spread across
  the 25 keys at `N = P` is `2.66 × 10⁻¹⁵`, machine ε; functionally
  zero. The true integral `2/π` differs from `R` by `1.31 × 10⁻⁷`
  (the structural Riemann-sum bias the cipher does not address).
- `experiments/bidder/unified/sport_riemann_emblem.py` — render
  script.

## Status

Anchored. Structural claim has a one-line proof and a passing test.
Quadrature behaviour follows Euler-Maclaurin with rates verified at
`P = 50, 200, 1000, 2000, 20000` for `f = sin(πx)` (`P²·error → π/6 ≈ 0.5236`).
Statistical-layer behaviour is also measured; the gap from FPC ideal
is documented in `generator/RIEMANN-SUM.md` and is the only layer that
depends on the cipher's PRP quality.

## Aesthetic note

This is GOOFY. There's no reason that should work. The cipher was
built to be a careful keyed PRP — Feistel network, key schedule, the
entire apparatus of cryptographic indistinguishability. At `N = P`
all of that cancels and the Riemann sum falls out of the bare fact
that `π` is a bijection. The thing built for cryptographic
randomness produces an *exact* Monte Carlo result via none of its
cryptographic content. The whole engineering effort is, at this one
parameter setting, beside the point.

## Provocation

Three movements:

- **The transition.** The statistical layer at `N < P` and the
  structural layer at `N = P` meet at `N = P` itself: `Var → 0`,
  `FPC → 0`, the prefix mean lands exactly on `R`. The transition is
  smooth in `N` but discontinuous in *how* the result is obtained
  (statistical → structural). Is there a clean way to articulate the
  transition that respects both layers?
- **Other cancellations.** Are there other places in this project
  where elaborate machinery cancels and a structural identity falls
  out of bare bijection-hood? The `Q_n` master expansion has the
  rank lemma cancellation; the row-OGF cliff is a polynomial
  cancellation; the kernel-zero theorem is a finite-difference
  cancellation. Is the cipher's `N = P` identity in the same family,
  or genuinely sport-shaped?
- **The integrand-quality dimension.** The Riemann-sum bias `|R − I|`
  is a function of `f` and `P`, not of the cipher. Endpoint-matching
  integrands (`f(0) = f(1)`) get `O(1/P²)`; generic integrands get
  `O(1/P)`; analytic-periodic integrands get exponential rates. The
  cipher gives the Riemann sum exactly *whatever the rate is*. The
  cipher's role is to land on `R`; the rate of `R → I` is a separate
  question that the cipher does not enter.

## Cross-references

- `marvel-row-ogf-cliff.md` — both are exact-at-one-point identities
  with one-line-derivable proofs and no closed form for nearby values.
  The marvel framing puts the row-OGF in the "found-not-built"
  register; the sport framing puts the Riemann-sum identity in the
  "alone-in-its-neighbourhood" register.
- `prodigy-L1-cliff-n2-h8.md` — also a single-cell phenomenon, but
  the prodigy register (looked-wrong-then-wasn't) is different from
  the sport register (looks-too-clean-to-need-the-machinery).
- (forthcoming, my pending proposal: `marvel-mercator-bridge`) —
  the `M_n` zeta function's log-coefficient identity is the
  master-expansion analogue of "structural identity that the
  surrounding apparatus is over-specified for." Same family of
  observations.

## Discovery context

The cipher was built first, for cryptographic purposes (a keyed
permutation of `[0, P)` with an opaque-by-construction reordering).
The Monte Carlo application came as a use case; the realisation that
the cipher's MC behaviour at `N = P` is exact, key-free, and
independent of the cipher's careful design is what motivated
`generator/RIEMANN-SUM.md` as a separate document with its own
three-layer claim-types table. The companion experiments
(`riemann_proof.py`, `adversarial_integrands.py`,
`mc_diagnostic.py`) verify the property numerically across
integrands and key sets; the test suite (`tests/theory/`) gates
the three layers separately so that drift in any one of them
is named for what it is.

The user's note on entering this specimen: *"There's no reason that
should work."* The half-life of that affect is short — once the
one-line proof is read, the goofiness becomes mechanical. The entry
preserves the affect because the affect, not the proof, is what
makes this a wonder-cabinet specimen.
