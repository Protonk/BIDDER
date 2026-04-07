# BIDDER

> Numbers are weird and perfect uniformity is (almost uniformly) a trap. Do not use BIDDER to generate secrets.

Arithmetic Congruence Monoids encoded as Champernowne reals, and
the BIDDER block generator that falls out of them. Named for
George Bidder's logarithms, which everyone seems to forget about.

## What this is

For each positive integer n, the multiplicative monoid nZ+ has
irreducible elements (n-primes). Concatenating these into a decimal
real produces a signal whose leading-digit distribution is exactly
uniform — not approximately uniform, exactly uniform.

```bqn
NPn2         ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}       # n-primes for n >= 2
Digits10     ← {𝕩<10 ? ⟨𝕩⟩ ; (𝕊⌊𝕩÷10)∾⟨10|𝕩⟩}
ChamDigits10 ← {⥊ Digits10¨ 𝕩}               # exact digit concatenation
LeadingInt10 ← {⊑ Digits10 𝕩}                # leading digit of an integer

ChamDigits10 (5↑ 3 NPn2 5)   # ⟨3,6,1,2,1,5,2,1⟩ — digits of C(3)
LeadingInt10 3                # 3 — the leading digit of n is the
                              #     leading digit of C(n)
```

See `guidance/BQN-AGENT.md` for the full canonical vocabulary.

## Math, art, crypto

This repo is three things at once.

### Math

> The construction is small but exact, and the consequences keep getting larger.

Leading digits of an ACM-Champernowne real are uniform — not approximately, *exactly* — over every full digit block. From that one fact a small library of results falls out: the sawtooth that the cumulative digit count traces inside a block, the epsilon function that controls its phase, and the rolling-shutter relationship between addition and multiplication that the sawtooth makes visible. The base-2 side is the active frontier. Bit-balance of an n-prime stream has a closed form that depends only on `v_2(n)`. The Walsh-Hadamard spectrum carries 44 robust higher-order coefficients that all collapse under entry-order shuffle and that the `v_2(n)` story explains only a minority of. There is an open conjecture that no finite automaton can recognize a binary ACM stream at all.

- [ACM-CHAMPERNOWNE.md](core/ACM-CHAMPERNOWNE.md) — the construction and the proofs
- [BLOCK-UNIFORMITY.md](core/BLOCK-UNIFORMITY.md) — the exact-uniformity result
- [BINARY.md](experiments/acm-champernowne/base2/BINARY.md) — what changes in base 2
- [HAMMING-BOOKKEEPING.md](experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md) — closed-form bit balance
- [WALSH.md](experiments/acm-champernowne/base2/forest/walsh/WALSH.md) — the Walsh signature
- [MALLORN-SEED.md](experiments/acm-champernowne/base2/forest/MALLORN-SEED.md) — the binary expeditions in flight

### Art

> Uniform numbers, given too much room, make a star.

Open [`corona_attempt.png`](experiments/acm-champernowne/base2/art/rle/corona_attempt.png) and you see a sun: a luminous core in cream and yellow, banded outward through orange to a deep crimson edge, with thin rays escaping into black. The piece is built from one of the simplest things you can do to a binary ACM stream — count the lengths of its zero-runs and one-runs, then put them on a disk with monoid index as angle and run length as radius. The piece's own technical doc files it under "instructive failures": direct radius is too expensive a coordinate for a distribution that decays exponentially, almost all the visual mass collapses into the inner bins, and the bright core is, technically, the failure mode.

But the bright core is also the truth. Short runs really do dominate, exponentially, by counting alone. The flares around the rim really are the high-`v_2` monoids pushing extra mass outward. Every photon in that image is the binary ACM stream telling the truth about itself in a coordinate system that gives it nowhere to hide. The "wrong" geometry is what surfaces the star inside the data; the "right" geometry would have shown a clean histogram and missed the sun entirely. Art and technique want different things from the same numbers, and sometimes the more useful thing is the one the technique would throw away.

That tension runs through the rest of the folder. [`rle_spiral.png`](experiments/acm-champernowne/base2/art/rle/rle_spiral.png) braids the same RLE data into a single hypnotist's arm — cool blues for zero-runs, warm oranges for one-runs — and the result feels less like a chart than like a spinning thing you can look at for too long. [`rle_ridgeline.png`](experiments/acm-champernowne/base2/art/rle/rle_ridgeline.png) borrows the silhouette of *Unknown Pleasures*: one residual-zero-run histogram per monoid stacked as a ridge against the background's horizon, with a warm orange seam breaking out wherever `v_2(n)` is large. It is the same data as the corona rendered as a mountain range instead of a sun, and it teaches more about the algebra precisely because it gives the structure less room to dazzle. [`sunflower_attempt.png`](experiments/acm-champernowne/base2/art/rle/sunflower_attempt.png) places each monoid on a phyllotaxis lattice and colors it by mean zero-run length; the visible spirals are interference between the golden angle and the data, not theorems, and the eye does not care about the difference.

The base-10 side has its own beauties. [`dense_bloom.png`](experiments/acm-champernowne/base10/art/sunflower/dense_bloom.png) is a target or an iris or a tantric diagram, depending on the mood you bring to it: concentric rings of red, magenta, blue, gold, more blue, more gold, with a tiny patterned eye at the center. [`filament.png`](experiments/acm-champernowne/base10/art/collapse/filament.png) is the opposite kind of beauty — three thin neon curves drifting across black, almost nothing on the canvas. The fully curated set, with the negative results that did not survive the cut, lives in [PITCH.md](experiments/acm-champernowne/base10/art/PITCH.md): Rolling Shutter, Digit Fabric, Moire Sieves, Sieve Carpet, and Epsilon Landscape.

- [PITCH.md](experiments/acm-champernowne/base10/art/PITCH.md) — the base-10 curated set, and the pieces that didn't survive
- [RLE.md](experiments/acm-champernowne/base2/art/rle/RLE.md) — the binary RLE family in full
- [ARCS.md](experiments/math/arcs/ARCS.md) — epsilon landscape

### Crypto

> Not that kind of crypto. A **block**-structured randomization tool that mates smoothly with a small, well-understood **block** cipher.

BIDDER is not a stream cipher and is not designed to be one. It tries to keep two guarantees separable. An algebraic substrate — the ACM-Champernowne digit block `[b^(d-1), b^d - 1]` — gives exact leading-digit uniformity by a counting argument from positional notation: across the block there are exactly `b^(d-1)` integers with each leading digit, with no error term. A keyed permutation — Speck32/64 in cycle-walking mode for operating blocks well below `2^32`, with a Feistel fallback when the cycle-walking ratio gets bad — provides the disorder. Neither piece is asked to do the other's job. The substrate is a theorem, not a measurement; the cipher is a published primitive being used inside its strength.

Tested so far, at the parameters we have actually run: full-period digit counts are exactly `period / (b - 1)` for every digit, every key, across bases 2, 7, 10, 16, 256 and digit classes 2 through 10. All `d` digit positions of each permuted index are independently uniform, with pairwise joints exact. SHA-256 rekeying across period boundaries introduces no detectable seam for `d ≥ 3`. Stratified sampling at block boundaries is totalizing — integration error drops to near machine epsilon for smooth functions. PractRand passes the underlying Speck32/64 in counter mode cleanly through 16 MB. The leading-digit extraction fails PractRand at 8 MB on FPF-14+6/16 *by design*, because the alphabet excludes 0; that is the right answer for a stratum-coverage generator and the wrong answer for a byte-stream PRNG, and the difference is the whole point of the construction.

The honest gap. Our testing so far confirms the algebraic structure we expected — the substrate behaves as the theorem says it should at every `d` we have tried. But we have not proven all the cryptographically important results about that structure, and we have not even tested the substrate at every block size a user might want. The uniformity result extends naively to any `d`, but extrapolating from a clean theorem is not the same as verifying it where you intend to use it: we do not know that a `2^2048`-sized operating block is not subtly non-uniform in some way that a small-`d` run would never see. The right honest answer is "we would be astonished," and astonishment is not worth much when a secret leaks or an experiment fails. Beyond uniformity itself, the cryptographic properties anyone would want for adversarial use — PRP strength of Speck32/64 in this specific composition, key independence, side-channel behavior, robustness under chosen input — are mostly inherited from Speck and have not been independently verified for BIDDER. The epigraph at the top of this file is not rhetorical.

- [BIDDER.md](generator/BIDDER.md) — design doc, observed properties, known limitations, open questions
- [bidder.py](generator/bidder.py) / [bidder.c](generator/bidder.c) — Python and C implementations, byte-identical output
- [speck.py](generator/speck.py) — full Speck family reference (all 10 variants, all Appendix C vectors)
- [experiments/bidder/stratified/](experiments/bidder/stratified/) — the totalizing demonstration
- [experiments/bidder/reseed/](experiments/bidder/reseed/) — the rekeying experiment

## Structure

    core/
      acm_core.py              Core definitions (Python)
      acm_core.h, acm_core.c   Core definitions (C)
      ACM-CHAMPERNOWNE.md      Mathematical foundation
      BLOCK-UNIFORMITY.md      Exact block-boundary uniformity result

    generator/
      bidder.py              BIDDER generator (Python)
      bidder.h, bidder.c     BIDDER generator (C)
      speck.py               Speck cipher family (reference, all 10 variants)
      BIDDER.md              Design document and findings

    tests/
      test_acm_core.py       Core definition tests (Python)
      test_acm_core_c.c      Core definition tests (C)
      test_bidder.py         Generator tests (Python)
      test_speck.py          Speck cipher tests (Appendix C vectors)
      test_bidder_c.c        Generator tests (C)
      bidder_stream.c        Byte stream emitter for PractRand
      speck_stream.c         Raw Speck counter mode for PractRand

    experiments/
      README.md                Source-first classification rule
      acm-champernowne/        Experiments on the raw ACM-Champernowne construction
        base10/                  Decimal digit streams (sawtooth, shutter, stats, art)
        base2/                   Binary concatenations (forest, art, disparity) + theory
      bidder/                  Experiments on BIDDER generator output
                               (dither, reseed, stratified, digits, art)
      math/                    Base-generic theory (arcs/)
      future/                  Active ideas not yet in a stable home (wibblywobblies/)

    nasties/                 Known bugs and edge-case documentation
    sources/                 Reference papers and early findings
    guidance/                Agent guidance documents

## Building

Python core tests (requires sage for numpy):

    sage -python tests/test_acm_core.py

Python generator and cipher tests (plain python3):

    python3 tests/test_bidder.py
    python3 tests/test_speck.py

C:

    gcc -O2 -o test_acm_core_c tests/test_acm_core_c.c core/acm_core.c -lm
    ./test_acm_core_c

    gcc -O2 -o test_bidder_c tests/test_bidder_c.c generator/bidder.c -lm
    ./test_bidder_c

## Key findings

### ACM construction

- Leading digits of ACM-Champernowne reals are exactly uniform
  (1/9 each, by `LeadingInt10`; see `core/BLOCK-UNIFORMITY.md`)
- Bit-balance of n-prime streams has a closed form that depends
  only on `v_2(n)` (see
  `experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md`)
- Binary ACM streams carry a real coefficient-level Walsh signature:
  44 robust universal cells, all collapsing under entry-order shuffle;
  the brightest are uncorrelated with `v_2(n)` (see
  `experiments/acm-champernowne/base2/forest/walsh/WALSH.md`)
- Conjecture: no finite automaton recognizes binary ACM streams
  (see `experiments/acm-champernowne/base2/FINITE-RECURRENCE.md`)

### BIDDER generator

- The BIDDER generator achieves exact uniformity at block boundaries by construction
- All d digit positions of each permuted index are independently uniform
- Rekeying at period boundaries introduces no detectable seam
- Stratified sampling with BIDDER is totalizing at block boundaries
- PractRand: underlying Speck permutation passes clean; leading-digit
  extraction fails by design (alphabet excludes 0)
