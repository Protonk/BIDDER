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

## Quick examples

Python:

```python
import bidder

list(bidder.sawtooth(n=3, count=10))
# [3, 6, 12, 15, 21, 24, 30, 33, 39, 42]

B = bidder.cipher(period=10, key=b'doc')
list(B)
# [0, 4, 8, 1, 7, 6, 9, 3, 2, 5]
```

## Construction, generator, gallery

This repo is now best read in three passes: the exact construction,
the keyed generator that sits on top of it, and the gallery of
coordinate experiments that turned the structure into pictures.

### Construction

> The construction is small but exact, and the consequences keep getting larger.

Leading base-`b` digits of an ACM-Champernowne real are uniform — not
approximately, *exactly* — over every full digit block in base `b`.
That exact count now supports a compact stable core:

- [ACM-CHAMPERNOWNE.md](core/ACM-CHAMPERNOWNE.md) — the construction and proofs
- [BLOCK-UNIFORMITY.md](core/BLOCK-UNIFORMITY.md) — exact leading-digit uniformity, integer and sieved
- [HARDY-SIDESTEP.md](core/HARDY-SIDESTEP.md) — closed form for the `K`-th n-prime
- [RIEMANN-SUM.md](core/RIEMANN-SUM.md) — permutation-invariance, quadrature rates, and the FPC benchmark

Around that core sit the block sawtooth, the epsilon function that
controls its phase, and the rolling-shutter relationship between
addition and multiplication that the sawtooth makes visible.

The base-2 side is the active frontier. Bit-balance of an n-prime
stream has a closed form that depends only on `v_2(n)`. The
Walsh-Hadamard spectrum carries 44 robust higher-order coefficients
that all collapse under entry-order shuffle and that the `v_2(n)` story
explains only a minority of. The current working conjecture is that no
finite automaton can generate or recognize a binary ACM stream at all.

- [BINARY.md](experiments/acm-champernowne/base2/BINARY.md) — what changes in base 2
- [HAMMING-BOOKKEEPING.md](experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md) — closed-form bit balance
- [WALSH.md](experiments/acm-champernowne/base2/forest/walsh/WALSH.md) — the Walsh signature
- [FINITE-RECURRENCE.md](experiments/acm-champernowne/base2/FINITE-RECURRENCE.md) — the finite-state boundary condition
- [MALLORN-SEED.md](experiments/acm-champernowne/base2/forest/MALLORN-SEED.md) — the binary expeditions in flight

### Generator

> Not that kind of crypto. A **block**-structured randomization tool that mates smoothly with a small, well-understood *block* cipher.

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
- [core/RIEMANN-SUM.md](core/RIEMANN-SUM.md) — the permutation-invariance theorem and finite-population correction
- [generator/BIDDER.md](generator/BIDDER.md) — cipher design doc, observed properties, known limitations, open questions
- [coupler.py](generator/coupler.py) / [bidder.c](generator/bidder.c) — alphabet-pinned Python and C implementations, byte-identical output
- [bidder.py](bidder.py) / [bidder_root.c](bidder_root.c) — root entry points in Python and C; same two-path surface, with one explicit range limit on the C side: sawtooth values that exceed `uint64_t` report overflow instead of returning Python-style bignums
- [speck.py](generator/speck.py) — full Speck family reference (all 10 variants, all Appendix C vectors)
- [experiments/bidder/unified/](experiments/bidder/unified/) — dither, period anatomy, MC diagnostics, Riemann proof, adversarial integrands
- [experiments/bidder/stratified/](experiments/bidder/stratified/) — the totalizing demonstration
- [experiments/bidder/reseed/](experiments/bidder/reseed/) — the rekeying experiment

### Art

> Uniform numbers, given too much room, make a star.

Art folders coordinate experiments on exact data. The next time someone says some of science is an art you should take it seriously. The below are a random set of examples.

- [`corona_attempt.png`](experiments/acm-champernowne/base2/art/rle/corona_attempt.png) — an instructive failure: binary run lengths on polar axes collapse toward the center because short runs dominate exponentially. The "sun" is a failure mode caused by structure of structure.
- [`rle_ridgeline.png`](experiments/acm-champernowne/base2/art/rle/rle_ridgeline.png) — the same residual histograms stacked as terrain. Warm seam tracks high `v_2(n)`.
- [`dense_bloom.png`](experiments/acm-champernowne/base10/art/sunflower/dense_bloom.png) — decimal block structure rendered as a bloom.

## Building

Python core tests (requires sage for numpy):

    sage -python tests/test_acm_core.py
    sage -python tests/test_sawtooth.py

Python generator and cipher tests (plain python3):

    python3 tests/test_bidder.py
    python3 tests/test_speck.py
    python3 tests/test_bidder_block.py
    python3 tests/test_api.py
    python3 tests/test_bidder_root.py

Theory red-team tests (plain python3):

    python3 tests/theory/test_riemann_property.py
    python3 tests/theory/test_quadrature_rates.py
    python3 tests/theory/test_fpc_shape.py

Doc verifier (plain python3):

    python3 core/api_doc_examples.py

C:

    gcc -O2 -o test_acm_core_c tests/test_acm_core_c.c core/acm_core.c -lm
    ./test_acm_core_c

    gcc -O2 -o test_bidder_c tests/test_bidder_c.c generator/bidder.c -lm
    ./test_bidder_c

    gcc -O2 -o test_bidder_root_c tests/test_bidder_root_c.c bidder_root.c generator/bidder.c core/acm_core.c -lm
    ./test_bidder_root_c
