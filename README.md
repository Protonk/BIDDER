# ACM-Champernowne

Arithmetic Congruence Monoids encoded as Champernowne reals, and
the HCH block generator that falls out of them.

## What this is

For each positive integer n, the multiplicative monoid nZ+ has
irreducible elements (n-primes). Concatenating these into a decimal
real produces a signal whose leading-digit distribution is exactly
uniform — not Benford, not approximately uniform, exactly uniform.

This repo explores that construction and builds a pseudorandom
number generator (HCH) on top of it.

## Structure

    acm_core.py             Core n-prime and Champernowne real definitions
    acm_sawtooth.py         Sawtooth structure and decomposition plots
    acm_benford.py          Benford convergence and rolling shutter analysis

    generator/
      hch.py                HCH generator (Python)
      hch.h, hch.c          HCH generator (C)
      speck.py              Speck cipher family (reference, all 10 variants)
      HCH-BLOCK-GEN.md      Design document and findings

    tests/
      test_hch.py            Python generator tests (18 tests)
      test_speck.py          Speck cipher tests (9 Appendix C vectors)
      test_hch_c.c           C generator tests
      hch_stream.c           Byte stream emitter for PractRand
      speck_stream.c         Raw Speck counter mode for PractRand

    experiments/
      sawtooth.py            5-decade sawtooth + running mean
      art/                   Visualizations (fabric, sunflower, PITCH.md)
      shutter/               Rolling shutter (addition vs multiplication)
      sieves/                Moire sieves and sieve carpet
      sunflower/             Phyllotaxis sunflower
      math/arcs/             Epsilon landscape
      stats/                 Uniformity demo, source comparison, interferometry
      stratified/            Stratified sampling comparison
      dither/                Dithering comparison
      others/                Multi-digit extraction analysis
      reseed/                Reseeding across period boundaries
      art/contamination/     How arithmetic contaminates uniform distributions

    sources/                 Reference papers (Speck)

## Building

Python (requires sage for plots, plain python3 for generator):

    python3 tests/test_hch.py
    python3 tests/test_speck.py

C:

    gcc -O2 -o test_hch_c tests/test_hch_c.c generator/hch.c -lm
    ./test_hch_c

## Key findings

- Leading digits of ACM-Champernowne reals are exactly uniform (1/9 each)
- Multiplication contaminates uniform distributions toward Benford irreversibly
- Addition cycles digit concentration forever (rolling shutter)
- The HCH generator achieves exact uniformity at block boundaries by construction
- All d digit positions of each permuted index are independently uniform
- Rekeying at period boundaries introduces no detectable seam
- Stratified sampling with HCH is totalizing at block boundaries
- PractRand: underlying Speck permutation passes clean; leading-digit
  extraction fails by design (alphabet excludes 0)
