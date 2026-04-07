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

This repo is three things at once:

- **Math.** The construction, the proofs, the sawtooth, the
  epsilon function, the relationship between addition and
  multiplication. ([ACM-CHAMPERNOWNE.md](core/ACM-CHAMPERNOWNE.md),
  [BINARY.md](experiments/acm-champernowne/base2/BINARY.md),
  [EARLY-FINDINGS.md](sources/EARLY-FINDINGS.md))

- **Art.** Visualizations that make the algebra visible — digit
  fabrics, moire sieves, rolling shutters, epsilon landscapes.
  ([PITCH.md](experiments/acm-champernowne/base10/art/PITCH.md))

- **Cryptography.** A pseudorandom number generator (BIDDER) that
  achieves exact output uniformity by construction, built on
  Speck32/64 and the block-boundary guarantee. Not that kind of
  crypto. ([BIDDER.md](generator/BIDDER.md))

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
