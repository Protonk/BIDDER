# BIDDER

> Numbers are weird and perfect uniformity is (almost uniformly) a trap. Do not use BIDDER to generate secrets.

![Every generator is uniform. BIDDER is exact, algebraically. 20 keys, 9000 outputs each, digits 1-9. BIDDER produces exactly 1000 of each digit on every key (blue squares on the reference line). numpy produces approximately 1000 with up to 77 counts of deviation (yellow circles scattered above and below).](exact.png)

Arithmetic Congruence Monoids encoded as Champernowne reals, and
the [BIDDER](BIDDER.md) block generator that falls out of them. Named for
George Bidder's logarithms, which everyone seems to forget about.

## What this is

For each positive integer n, the multiplicative monoid nZ+ has irreducible elements, which we call n-primes (numbers which would be prime were (n-1) factorization not available). Concatenating these into a decimal real produces a signal whose leading-digit distribution is exactly uniform — not approximately uniform, exactly uniform.

The first few n-primes for small `n`:

| n | first n-primes |
|---|---|
| 2  | 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, … |
| 3  | 3, 6, 12, 15, 21, 24, 30, 33, 39, 42, … |
| 4  | 4, 8, 12, 20, 24, 28, 36, 40, 44, 52, … |
| 5  | 5, 10, 15, 20, 30, 35, 40, 45, 55, 60, … |
| 10 | 10, 20, 30, 40, 50, 60, 70, 80, 90, 110, … |

Concatenating those digits [as a sequence in order](https://en.wikipedia.org/wiki/Champernowne_constant) gives the Champernowne real `C(n)`:

| n | `C(n)` |
|---|---|
| 2  | `0.2610141822263034…` |
| 3  | `0.3612152124303339…` |
| 4  | `0.4812202428364044…` |
| 5  | `0.5101520303540455…` |
| 10 | `0.1020304050607080…` |

The mathematical definitions shown in this README and the core theory
docs are written in [BQN](https://mlochbaum.github.io/BQN/), used here
as executable mathematical notation: dense enough to fit a construction
on one line, unambiguous enough to actually run, and structurally
close to the array-and-index style the math itself uses. The full
vocabulary lives in [guidance/BQN-AGENT.md](guidance/BQN-AGENT.md).
Reading BQN is not required to follow this README — the prose carries
the meaning, the tables above show the result, and the block below is
the precise form for anyone who wants to run it.

```bqn
NPn2         ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}       # n-primes for n >= 2
Digits10     ← {𝕩<10 ? ⟨𝕩⟩ ; (𝕊⌊𝕩÷10)∾⟨10|𝕩⟩}
ChamDigits10 ← {⥊ Digits10¨ 𝕩}               # exact digit concatenation
LeadingInt10 ← {⊑ Digits10 𝕩}                # leading digit of an integer

ChamDigits10 (5↑ 3 NPn2 5)   # ⟨3,6,1,2,1,5,2,1⟩ — digits of C(3)
LeadingInt10 3                # 3 — the leading digit of n is the
                              #     leading digit of C(n)
```

Leading base-`b` digits of an ACM-Champernowne real are uniform — not
approximately, *exactly* — over every full digit block in base `b`.

- [ACM-CHAMPERNOWNE.md](core/ACM-CHAMPERNOWNE.md) — the construction and proofs
- [BLOCK-UNIFORMITY.md](core/BLOCK-UNIFORMITY.md) — exact leading-digit uniformity, integer and sieved

## Consequences

The construction is the deletion rule. The consequences are larger
than the construction. Below: a bilingual algebra that organises
the substrate's residuals (the open heart, potentially the most
important feature); a keyed permutation that mates with the
substrate as a block-structured generator; and the art that falls
out when exact data has room to move.

### Algebra (the open heart)

> Our constructive normals leave algebra in their residue.

![A circular disk filling most of a square frame on a black background. The disk's interior is rendered in deep magenta and purple tones overlaid with a network of bright orange-yellow lines. Two prominent perpendicular bright bars cross through the disk's centre forming an orange cross — one horizontal diameter, one vertical diameter. Beyond the central cross, the disk is filled with a curvilinear orthogonal grid: arcs that bend along the disk's curvature, growing denser and finer toward the disk's circumference. The grid is regular near the centre and compresses tightly at the rim, where the structure thickens into a fine textured band along the disk's boundary.](experiments/acm-champernowne/base10/art/q_distillery/q_lattice_4000_fft_poincare.png)

The single deletion rule `M_n = {1} ∪ nZ_{>0}` does three things at
once: it discards unique factorisation, exposes the arithmetic
progression Hardy inverts, and supplies the generating function
`ζ_{M_n}(s) = 1 + n^{-s} ζ(s)` whose Mercator log is a bilingual
program. *Bilingual* because the `K`-index it runs on positions an
atom in the substrate lattice and a position in the base-`b` digit
stream of `C_b(n)` simultaneously, polylog-bignum work to convert
in either direction.

What that buys: the substrate organises its own residuals as
algebra. `offset(n)` indexed by `ord(b, n)`, `β(n)` for the
`O(b^{-k})` tails, the off-spike denominator process between
consecutive boundary spikes, the `(n−1)/n²` smooth-block density,
the `α_n = (n−1)/n` mult-table asymptote, the lucky-cancellation
locus — distinct objects, all referring back to the same deletion
rule. Other constructive normals — classical Champernowne (1933),
Stoneham (1973), Becher–Figueira — have residues. None of them
expose those residues as algebra in the way this substrate does.

The open commitment is *absolute* normality of every `C_b(n)`
across every base, not just the base of concatenation that
Copeland–Erdős (1946) settles. We submit it will remain open. The
algebra of residuals is what would close it, or what would record
exactly where closing fails. That distinction is the project's
potentially most important contribution — independent of whether
absolute normality itself ever falls.

- [THE-OPEN-HEART.md](THE-OPEN-HEART.md) — the manifesto: closure refused, log identity recovered at higher altitude, UFD traded for K-indexed access
- [algebra/THE-WHOLE-MACHINE.md](algebra/THE-WHOLE-MACHINE.md) — the eleven parts of the BIDDER UTM, named once each
- [algebra/Q-FORMULAS.md](algebra/Q-FORMULAS.md) — the master expansion `Q_n(m) = Σ_{j=1}^{ν_n(m)} (−1)^{j−1} τ_j(m/n^j) / j` and its row specialisations
- [algebra/FINITE-RANK-EXPANSION.md](algebra/FINITE-RANK-EXPANSION.md) — the rank lemma: Mercator truncates at `j = ν_n(m)` by integer divisibility
- [algebra/WITHIN-ROW-PARITY.md](algebra/WITHIN-ROW-PARITY.md) — first closed-form deliverable: autocorrelation factored as algebraic `V` × combinatorial `D`
- [experiments/acm-flow/cf/DENOMINATOR-PROCESS.md](experiments/acm-flow/cf/DENOMINATOR-PROCESS.md) — the CF coordinate of the cost ledger; three-population decomposition

### Generator

> Not that kind of crypto. A **block**-structured randomization tool that mates smoothly with a small, well-understood *block* cipher.

![Side-by-side anatomy of bidder.cipher (left, yellow) and bidder.sawtooth (right, blue). Four rows: output scatter, output histogram, first differences, and autocorrelation. The cipher path is flat, noisy, and uncorrelated — a keyed permutation. The sawtooth path is structured, deterministic, and strongly correlated — exact n-primes in order. Two paths, one interface, opposite guarantees.](experiments/bidder/unified/period_anatomy.png)

BIDDER exists to keep two guarantees separable. An algebraic substrate — the ACM-Champernowne digit block `[b^(d-1), b^d - 1]` — gives exact leading-digit uniformity by a counting argument from positional notation: across the block there are exactly `b^(d-1)` integers with each leading digit, with no error term. A keyed permutation — Speck32/64 in cycle-walking mode for operating blocks well below `2^32`, with a Feistel fallback when the cycle-walking ratio gets bad — provides the disorder. Neither piece is asked to do the other's job. 

Proved:

- The algebraic substrate is exact, not merely tested. The integer
  block lemma in [core/BLOCK-UNIFORMITY.md](core/BLOCK-UNIFORMITY.md)
  is a counting argument from positional notation; there is no hidden
  block size where it stops working.
- At `N = period`, the MC estimate equals the left-endpoint Riemann
  sum `R` for any key and any integrand. This is the structural
  permutation-invariance theorem in
  [core/RIEMANN-SUM.md](core/RIEMANN-SUM.md).
- The root entry points are stable:
  [BIDDER.md](BIDDER.md) documents `bidder.cipher(period, key)` and
  `bidder.sawtooth(n, count)`, with
  [core/API.md](core/API.md) as the detailed cipher-path reference.

Measured:

- Full-period digit counts are exactly `period / (b - 1)` for every
  digit, every key, across the tested bases and digit classes.
- All `d` digit positions of each permuted index are independently
  uniform, with pairwise joints exact on the tested ranges.
- SHA-256 rekeying across period boundaries shows no detectable seam
  for `d ≥ 3`.
- Stratified sampling at block boundaries is totalizing for smooth
  functions.
- The theory front is now executable. Three red-team test files
  under `tests/theory/` attack the structural, quadrature, and
  statistical layers independently. The organizing document is
  [RED-TEAM-THEORY.md](tests/theory/RED-TEAM-THEORY.md) — it
  decomposes the total error `E_N − I = (E_N − R) + (R − I)` into
  four layers, names what would falsify each claim, and tracks the
  measured coupling gap between the cipher backend and the ideal
  without-replacement null.

Not claimed:

- The PRP properties anyone would want for adversarial use —
  distinguishing advantage in this exact composition, key
  independence beyond the structural `E_P = R` result, side-channel
  behavior, robustness under chosen input — are inherited from Speck
  and have not been independently verified for BIDDER.
- The Feistel fallback at small block sizes shows a measurable
  variance gap at intermediate `N`: the `random.shuffle` null matches
  the finite-population correction formula, but the Feistel-keyed
  permutations run roughly `1.5×` to `2.5×` worse. This is a backend
  property, not an algebra failure.
- The warning at the top of this file is literal: BIDDER is not a
  secret-generation tool.

- [BIDDER.md](BIDDER.md) — root API reference: `bidder.cipher` and `bidder.sawtooth` in three layers (natural language, Python, BQN)
- [core/API.md](core/API.md) — detailed cipher-path reference
- [generator/BIDDER.md](generator/BIDDER.md) — cipher design doc, observed properties, known limitations, open questions

### Art

> Uniform numbers, given too much room, make a star.

![Binary run lengths of n-prime streams plotted on polar axes. Short runs dominate exponentially, collapsing the plot toward the center and producing concentric rings of light. The result looks like a sun — bright core, banded corona, radial spikes at long rare runs. An instructive failure: the visualization was meant to show structure in the runs, but the structure of the structure made a star instead.](experiments/acm-champernowne/base2/art/rle/corona_attempt.png)

Art folders coordinate experiments on exact data. The next time someone says some of science is an art you should take it seriously. The below are a random set of examples.

- [`corona_attempt.png`](experiments/acm-champernowne/base2/art/rle/corona_attempt.png) — the sun above. An instructive failure: binary run lengths on polar axes collapse toward the center because short runs dominate exponentially. The "sun" is a failure mode caused by structure of structure.
- [`dense_bloom.png`](experiments/acm-champernowne/base10/art/sunflower/dense_bloom.png) — decimal block structure rendered as a bloom.
- [`escalating_bidder_mul.png`](experiments/bidder/art/contamination/escalating_bidder_mul.png) — 1, then 5, then 10 multiplications in a sea of additions. Each burst deepens the Benford scar. The additive staircase is the Champernowne sawtooth; the multiplicative kick is ε doing its work.
- [`art_groove.png`](experiments/math/benford/art_groove.png) — four Benford demos rendered as vinyl records. Groove eccentricity is mantissa non-uniformity; a perfect circle is Benford equilibrium. The BS(1,2) walk's record has one bright scratch (the initial delta) and then a machined surface.
- [`butterfly.png`](experiments/bidder/bidderize/butterfly.png) — a keyed permutation of 20,000 integers, rotated 45 degrees and cropped to an oval. Colored by output mod 9 on a CMB scale. The density variations are the Feistel round function's fingerprint, almost but not quite uniform.
