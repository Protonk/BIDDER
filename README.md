# BIDDER

> Numbers are weird and perfect uniformity is (almost uniformly) a trap. Do not use BIDDER to generate secrets.

Arithmetic Congruence Monoids encoded as Champernowne reals, and
the BIDDER block generator that falls out of them. Named for
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

## Math, art, crypto

This repo is three things at once.

### Math

> The construction is small but exact, and the consequences keep getting larger.

Leading base-`b` digits of an ACM-Champernowne real are uniform — not
approximately, *exactly* — over every full digit block in base `b`.
From that one fact a small library of results falls out: the sawtooth
that the cumulative digit count traces inside a block, the epsilon
function that controls its phase, and the rolling-shutter relationship
between addition and multiplication that the sawtooth makes visible.

The base-2 side is the active frontier. Bit-balance of an n-prime
stream has a closed form that depends only on `v_2(n)`. The
Walsh-Hadamard spectrum carries 44 robust higher-order coefficients
that all collapse under entry-order shuffle and that the `v_2(n)` story
explains only a minority of. The current working conjecture is that no
finite automaton can generate or recognize a binary ACM stream at all.

- [ACM-CHAMPERNOWNE.md](core/ACM-CHAMPERNOWNE.md) — the construction and the proofs
- [BLOCK-UNIFORMITY.md](core/BLOCK-UNIFORMITY.md) — the exact-uniformity result
- [BINARY.md](experiments/acm-champernowne/base2/BINARY.md) — what changes in base 2
- [HAMMING-BOOKKEEPING.md](experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md) — closed-form bit balance
- [WALSH.md](experiments/acm-champernowne/base2/forest/walsh/WALSH.md) — the Walsh signature
- [FINITE-RECURRENCE.md](experiments/acm-champernowne/base2/FINITE-RECURRENCE.md) — the finite-state boundary condition
- [MALLORN-SEED.md](experiments/acm-champernowne/base2/forest/MALLORN-SEED.md) — the binary expeditions in flight

### Art

> Uniform numbers, given too much room, make a star.

Open [`corona_attempt.png`](experiments/acm-champernowne/base2/art/rle/corona_attempt.png) and you see a sun: a luminous core in cream and yellow, banded outward through orange to a deep crimson edge, with thin rays escaping into black. The piece is built from one of the simplest things you can do to a binary ACM stream — count the lengths of its zero-runs and one-runs, then put them on a disk with monoid index as angle and run length as radius. The piece's own technical doc files it under "instructive failures": direct radius is too expensive a coordinate for a distribution that decays exponentially, almost all the visual mass collapses into the inner bins, and the bright core is, technically, the failure mode.

But the bright core is also the truth. Short runs really do dominate, exponentially, by counting alone. The flares around the rim really are the high-`v_2` monoids pushing extra mass outward. Every photon in that image is the binary ACM stream telling the truth about itself in a coordinate system that gives it nowhere to hide. The "wrong" geometry is what surfaces the star inside the data; the "right" geometry would have shown a clean histogram and missed the sun entirely. 

That tension runs through the rest of the folder. [`rle_spiral.png`](experiments/acm-champernowne/base2/art/rle/rle_spiral.png) braids the same RLE data into a single hypnotist's arm — cool blues for zero-runs, warm oranges for one-runs — and the result feels less like a chart than like a spinning thing you can look at for too long. [`rle_ridgeline.png`](experiments/acm-champernowne/base2/art/rle/rle_ridgeline.png) borrows the silhouette of *Unknown Pleasures*: one residual-zero-run histogram per monoid stacked as a ridge against the background's horizon, with a warm orange seam breaking out wherever `v_2(n)` is large. It is the same data as the corona rendered as a mountain range instead of a sun, and it teaches more about the algebra precisely because it gives the structure less room to dazzle. [`sunflower_attempt.png`](experiments/acm-champernowne/base2/art/rle/sunflower_attempt.png) places each monoid on a phyllotaxis lattice and colors it by mean zero-run length; the visible spirals are interference between the golden angle and the data, not theorems, and the eye does not care about the difference.

The base-10 side has its own beauties. [`dense_bloom.png`](experiments/acm-champernowne/base10/art/sunflower/dense_bloom.png) is a target or an iris or a tantric diagram, depending on the mood you bring to it: concentric rings of red, magenta, blue, gold, more blue, more gold, with a tiny patterned eye at the center. [`filament.png`](experiments/acm-champernowne/base10/art/collapse/filament.png) is the opposite kind of beauty — three thin neon curves drifting across black, almost nothing on the canvas. The fully curated set, with the negative results that did not survive the cut, lives in [PITCH.md](experiments/acm-champernowne/base10/art/PITCH.md): Rolling Shutter, Digit Fabric, Moire Sieves, Sieve Carpet, and Epsilon Landscape.

- [PITCH.md](experiments/acm-champernowne/base10/art/PITCH.md) — the base-10 curated set, and the pieces that didn't survive
- [RLE.md](experiments/acm-champernowne/base2/art/rle/RLE.md) — the binary RLE family in full
- [ARCS.md](experiments/math/arcs/ARCS.md) — epsilon landscape

### Crypto

> Not that kind of crypto. A **block**-structured randomization tool that mates smoothly with a small, well-understood block cipher.

BIDDER exists to keep two guarantees separable. An algebraic substrate — the ACM-Champernowne digit block `[b^(d-1), b^d - 1]` — gives exact leading-digit uniformity by a counting argument from positional notation: across the block there are exactly `b^(d-1)` integers with each leading digit, with no error term. A keyed permutation — Speck32/64 in cycle-walking mode for operating blocks well below `2^32`, with a Feistel fallback when the cycle-walking ratio gets bad — provides the disorder. Neither piece is asked to do the other's job. 

Tested so far, at the parameters we have actually run: full-period digit counts are exactly `period / (b - 1)` for every digit, every key, across bases 2, 7, 10, 16, 256 and digit classes 2 through 10. All `d` digit positions of each permuted index are independently uniform, with pairwise joints exact. SHA-256 rekeying across period boundaries introduces no detectable seam for `d ≥ 3`. Stratified sampling at block boundaries is totalizing — integration error drops to near machine epsilon for smooth functions. PractRand passes the underlying Speck32/64 in counter mode cleanly through 16 MB. The leading-digit extraction fails PractRand at 8 MB on FPF-14+6/16 *by design*, because the alphabet excludes 0; that is the right answer for a stratum-coverage generator and the wrong answer for a byte-stream PRNG, and the difference is the whole point of the construction.

The algebraic substrate is proved, not merely tested. The integer block lemma (`core/BLOCK-UNIFORMITY.md`) is a counting argument from positional notation that holds for every `b ≥ 2` and every `d ≥ 1` — there is no untested block size and no `d`-dependent failure mode. The permutation-invariance theorem (`core/RIEMANN-SUM.md`) shows that at `N = period`, the MC estimate equals the Riemann sum `R` for any key and any integrand; this is structural (it follows from the definition of "permutation") and also does not depend on `d` or on the cipher backend.

What is *not* proved is the cipher side. The PRP properties anyone would want for adversarial use — distinguishing advantage of Speck32/64 in this specific composition, key independence beyond the structural `E_P = R` result, side-channel behavior, robustness under chosen input — are inherited from Speck and have not been independently verified for BIDDER. The Feistel fallback at small block sizes introduces a measurable variance gap at intermediate `N`: the `random.shuffle` null matches the finite-population correction formula, but the Feistel-keyed permutations run ~2× worse (see the coupling measurement in `core/RIEMANN-SUM.md §What the cipher actually achieves` and the theory tests in `tests/theory/test_fpc_shape.py`). This gap is a property of the PRP backend, not of the algebra, and it does not affect the structural guarantees. The epigraph at the top of this file is not rhetorical — it applies to the cipher layer, where BIDDER inherits Speck's strengths and has not independently demonstrated more.

- [BIDDER.md](BIDDER.md) — root API reference: `bidder.cipher` and `bidder.sawtooth` in three layers (natural language, Python, BQN)
- [core/API.md](core/API.md) — detailed cipher-path reference
- [core/RIEMANN-SUM.md](core/RIEMANN-SUM.md) — the permutation-invariance theorem and finite-population correction
- [generator/BIDDER.md](generator/BIDDER.md) — cipher design doc, observed properties, known limitations, open questions
- [coupler.py](generator/coupler.py) / [bidder.c](generator/bidder.c) — alphabet-pinned Python and C implementations, byte-identical output
- [speck.py](generator/speck.py) — full Speck family reference (all 10 variants, all Appendix C vectors)
- [experiments/bidder/unified/](experiments/bidder/unified/) — dither, period anatomy, MC diagnostics, Riemann proof, adversarial integrands
- [experiments/bidder/stratified/](experiments/bidder/stratified/) — the totalizing demonstration
- [experiments/bidder/reseed/](experiments/bidder/reseed/) — the rekeying experiment

## Structure

    bidder.py                Root entry point: bidder.cipher() and bidder.sawtooth()
    BIDDER.md                Root API reference (three-layer: prose, Python, BQN)

    core/
      acm_core.py              Core definitions (Python)
      acm_core.h, acm_core.c   Core definitions (C)
      ACM-CHAMPERNOWNE.md      Mathematical foundation
      BLOCK-UNIFORMITY.md      Exact block-boundary uniformity (integer + sieved lemmas)
      HARDY-SIDESTEP.md        Closed-form K-th n-prime for n >= 2
      RIEMANN-SUM.md           Permutation-invariance theorem + FPC
      API.md                   Detailed cipher-path API reference
      api.py                   fulfill(period, key) orchestrator
      sawtooth.py              NPrimeSequence (Hardy closed form)
      hardy_sidestep.py        Companion verification script
      api_doc_examples.py      Doc verifier for API.md, RIEMANN-SUM.md, BIDDER.md

    generator/
      coupler.py             Alphabet-pinned BIDDER generator (Python, renamed from bidder.py)
      bidder.h, bidder.c     BIDDER generator (C, parity with coupler.py)
      bidder_block.py        Period-only adapter (BidderBlock)
      speck.py               Speck cipher family (reference, all 10 variants)
      BIDDER.md              Cipher design document and findings
      AGENTS.md              Parity rules and conventions

    tests/
      test_acm_core.py       Core definition tests + sieved block uniformity (sage)
      test_acm_core_c.c      Core definition tests (C)
      test_bidder.py         Cipher parity tests including at(i) (Python)
      test_bidder_c.c        Cipher parity tests including bidder_at (C)
      test_bidder_block.py   BidderBlock contract tests
      test_api.py            fulfill() tests
      test_sawtooth.py       NPrimeSequence tests (sage)
      test_bidder_root.py    Root entry point smoke tests
      test_speck.py          Speck cipher tests (Appendix C vectors)
      bidder_stream.c        Byte stream emitter for PractRand
      speck_stream.c         Raw Speck counter mode for PractRand
      theory/                Theory red-team tests (see theory/README.md)
        test_riemann_property.py   Permutation-invariance (structural layer)
        test_quadrature_rates.py   Euler-Maclaurin rates (quadrature layer)
        test_fpc_shape.py          Finite-population correction (statistical + coupling)

    experiments/
      README.md                Source-first classification rule
      acm-champernowne/        Experiments on the raw ACM-Champernowne construction
        base10/                  Decimal digit streams (sawtooth, shutter, stats, art)
        base2/                   Binary concatenations (forest, art, disparity) + theory
      bidder/                  Experiments on BIDDER generator output
        unified/                 Dither, period anatomy, MC, Riemann, adversarial integrands
        dither/                  Legacy dither comparison
        reseed/                  Rekeying experiment
        stratified/              Stratified sampling comparison
        digits/, art/            Digit experiments and contamination art
      math/                    Base-generic theory (arcs/)
      future/                  Active ideas not yet in a stable home (wibblywobblies/)

    nasties/                 Known bugs and edge-case documentation
    sources/                 Reference papers and early findings
    guidance/                Agent guidance documents

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

## Key findings

### ACM construction

- Leading base-`b` digits are exactly uniform on every complete digit
  block (see `core/BLOCK-UNIFORMITY.md`)
- Bit-balance of n-prime streams has a closed form that depends
  only on `v_2(n)` (see
  `experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md`)
- Binary ACM streams carry a real coefficient-level Walsh signature:
  44 robust universal cells, all collapsing under entry-order shuffle;
  the brightest are uncorrelated with `v_2(n)` (see
  `experiments/acm-champernowne/base2/forest/walsh/WALSH.md`)
- Working conjecture / boundary condition: no finite automaton
  generates or recognizes binary ACM streams (see
  `experiments/acm-champernowne/base2/FINITE-RECURRENCE.md`)

### BIDDER generator

- The BIDDER generator achieves exact uniformity at block boundaries by construction
- All d digit positions of each permuted index are independently uniform
- Rekeying at period boundaries introduces no detectable seam
- Stratified sampling with BIDDER is totalizing at block boundaries
- PractRand: underlying Speck permutation passes clean; leading-digit
  extraction fails by design (alphabet excludes 0)
- **Riemann-sum property**: at `N = period`, the MC estimate from
  `bidder.cipher` equals the left-endpoint Riemann sum `R` of the
  integrand — for any key, any integrand. The key cancels out.
  (`core/RIEMANN-SUM.md`)
- **Hardy sidestep**: the K-th n-prime for `n ≥ 2` has a closed form
  that costs one `divmod` and one multiply on bignums. Locating the
  `2^4096`-th 2-prime takes microseconds. (`core/HARDY-SIDESTEP.md`)
- **Sieved block uniformity**: two sufficient families (smooth and
  Family E) certify exact leading-digit uniformity for n-prime blocks.
  The spread is ≤ 2 when neither family applies.
  (`core/BLOCK-UNIFORMITY.md`)
- **Unified API**: `bidder.cipher(period, key)` for keyed permutations,
  `bidder.sawtooth(n, count)` for deterministic n-prime sequences.
  (`BIDDER.md`, `core/API.md`)
