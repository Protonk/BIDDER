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

This repo is three things at once:

- **Math.** The construction, the proofs, the sawtooth, the
  epsilon function, the relationship between addition and
  multiplication. ([ACM-CHAMPERNOWNE.md](ACM-CHAMPERNOWNE.md),
  [EARLY-FINDINGS.md](EARLY-FINDINGS.md))

- **Art.** Visualizations that make the algebra visible — digit
  fabrics, moire sieves, rolling shutters, epsilon landscapes.
  ([PITCH.md](experiments/art/PITCH.md))

- **Cryptography.** A pseudorandom number generator (BIDDER) that
  achieves exact output uniformity by construction, built on
  Speck32/64 and the block-boundary guarantee. Not that kind of
  crypto. ([BIDDER.md](generator/BIDDER.md))

## Structure

    acm_core.py             Core definitions (Python)
    acm_core.h, acm_core.c  Core definitions (C)

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
      sawtooth/              Sawtooth and residual analysis
      shutter/               Rolling shutter (addition vs multiplication)
      sieves/                Moire sieves and sieve carpet
      art/                   Visualizations (fabric, contamination, collapse)
      math/arcs/             Epsilon landscape
      stats/                 Uniformity demo, source comparison, interferometry
      stratified/            Stratified sampling at block boundaries
      dither/                Dithering comparison
      others/                Multi-digit extraction analysis
      reseed/                Reseeding across period boundaries
      wibblywobblies/        Wibble-wobble conservation law

    nasties/                 Known bugs and edge-case documentation
    sources/                 Reference papers (Speck)

## Building

Python core tests (requires sage for numpy):

    sage -python tests/test_acm_core.py

Python generator and cipher tests (plain python3):

    python3 tests/test_bidder.py
    python3 tests/test_speck.py

C:

    gcc -O2 -o test_acm_core_c tests/test_acm_core_c.c acm_core.c -lm
    ./test_acm_core_c

    gcc -O2 -o test_bidder_c tests/test_bidder_c.c generator/bidder.c -lm
    ./test_bidder_c

## Key findings

- Leading digits of ACM-Champernowne reals are exactly uniform (1/9 each)
- Multiplication contaminates uniform distributions toward Benford irreversibly
- Addition cycles digit concentration forever (rolling shutter)
- The BIDDER generator achieves exact uniformity at block boundaries by construction
- All d digit positions of each permuted index are independently uniform
- Rekeying at period boundaries introduces no detectable seam
- Stratified sampling with BIDDER is totalizing at block boundaries
- PractRand: underlying Speck permutation passes clean; leading-digit
  extraction fails by design (alphabet excludes 0)
