# BIDDER Generator

A pseudorandom number generator that achieves exact output uniformity by construction.

Status: implemented in Python and C. Speck test vectors verified. Cross-language output parity confirmed.


## Motivation

Conventional PRNGs produce output that is statistically close to
uniform, verified empirically (TestU01, PractRand). No finite prefix
is exactly uniform — it converges.

BIDDER factors the problem differently: an algebraic substrate
provides exact uniformity, a keyed permutation provides disorder.
The substrate guarantees the distribution; the permutation provides
unpredictability. Neither depends on the other.


## Mathematical foundation

The construction rests on two facts from positional notation, both
documented and proven outside this file:

1. The irreducible elements of the monoid nZ+ are the multiples
   of n that are not multiples of n^2. See
   [ACM-CHAMPERNOWNE.md](../core/ACM-CHAMPERNOWNE.md).

2. In any base b, the integers in a complete digit class
   [b^(d-1), b^d - 1] have exactly uniform leading digits. See
   [BLOCK-UNIFORMITY.md](../core/BLOCK-UNIFORMITY.md).

The Champernowne encoding preserves leading digits, so over a
complete digit block the output distribution is exactly uniform.
The error is zero — not approximately zero, zero.


## Construction

### Operating block

Choose base b >= 2 and digit class d >= 1. The operating block is
B_d = {b^(d-1), ..., b^d - 1}, with size (b-1) * b^(d-1). Leading
base-b digits of its elements are exactly uniform over {1, ..., b-1}.

| Parameter | Controls                    | Example          |
|-----------|-----------------------------|------------------|
| b         | alphabet size (b-1 symbols) | 256 -> 255 syms  |
| d         | period = (b-1) * b^(d-1)   | d=2 -> 65280     |
| key       | which permutation           | arbitrary bytes  |

Block size must not exceed 2^32.

### Keyed permutation

Speck32/64 (Beaulieu et al., 2013): 22 rounds, 64-bit key, 32-bit
block. When the operating block is much smaller than 2^32
(cycle-walk ratio > 64), a balanced Feistel network with 8 rounds
of SHA-256-derived round keys is used instead. Mode selected
automatically at init.

Key derivation: SHA-256(raw_key) truncated to 8 bytes for
Speck32/64. For Feistel: SHA-256(raw_key) -> key_hash, then each
round key is SHA-256(key_hash || round_index) truncated to 8 bytes.

A reference implementation of the full Speck family (all 10
variants, all 9 Appendix C test vectors) is in `speck.py`.

### Output

Each call to `next()`:

    1. Permutes the counter through pi_K (with cycle-walking)
    2. Adds block_start to get an integer n in B_d
    3. Extracts the leading base-b digit of n
    4. Increments the counter (wraps at block_size)

Since pi_K is a bijection and B_d has exactly b^(d-1) elements
per leading digit, the output visits each symbol exactly b^(d-1)
times per period. Within a period, deviation follows a
deterministic sawtooth whose phase is scrambled by the permutation
([EARLY-FINDINGS.md](../sources/EARLY-FINDINGS.md), section 2).

### Constants

    SPECK32_ROUNDS = 22
    FEISTEL_ROUNDS = 8
    MAX_CYCLE_WALK_RATIO = 64


## Implementations

Both produce identical output for identical inputs.

| Lang   | Files                      | API                                    |
|--------|----------------------------|----------------------------------------|
| Python | `bidder.py`                | `Bidder(b, d, key)`, `next()`, `reset()`, iterator |
| C      | `bidder.h` + `bidder.c`    | `bidder_init()`, `bidder_next()`, `bidder_reset()` |
| Ref    | `speck.py`                 | Full Speck family, all test vectors    |

Tests: `tests/test_bidder.py`, `tests/test_speck.py`,
`tests/test_bidder_c.c`.


## Observed properties

### Exact uniformity

Full-period digit counts are exactly `period / (b-1)` for every
digit, every key, across bases 2, 7, 10, 16, 256 and digit classes
2-10. Deviation at block boundaries: zero.

### Multi-digit extraction

All d digit positions of each permuted index are independently
uniform — not just the leading digit. Position 0 over {1, ..., b-1};
positions 1..d-1 over {0, ..., b-1}. All pairwise joints exact.
Each evaluation yields d independent samples.
Experiment: `experiments/bidder/digits/other_digits.py`.

### Reseeding

Rekeying via SHA-256(old_key || period_counter) preserves exact
uniformity. No detectable seam for d >= 3. At d=2 (period 90 in
base 10) the seam is significant — a structural property of finite
permutations, not a cipher weakness, and irrelevant at intended
block sizes. Experiment: `experiments/bidder/reseed/reseed_test.py`.

### PractRand

Speck32/64 in counter mode passes clean through 16MB. Leading-digit
extraction fails at 8MB on FPF-14+6/16 — because the alphabet
excludes 0. This is the right result: BIDDER is a stratum-coverage
generator, not a byte-stream PRNG. Test code:
`tests/bidder_stream.c`, `tests/speck_stream.c`.

### Interferometry

Under random-draw sampling, BIDDER is indistinguishable from numpy.
Under consecutive-draw sampling, the raw ACM source shows phase
gradients that both numpy and the permuted BIDDER destroy. The
permutation mixes well.

### Arithmetic contamination

Using BIDDER as a known-uniform calibration source: multiplication
contaminates toward Benford irreversibly; addition cycles forever
(rolling shutter); a single multiplication in 20,000 additions
leaves a permanent scar. These characterize uniform distributions
generally, not BIDDER specifically. See
[EARLY-FINDINGS.md](../sources/EARLY-FINDINGS.md), sections 4-5.
Experiments: `experiments/acm-champernowne/base10/shutter/`, `experiments/bidder/art/contamination/`.

### Stratified sampling

At block boundaries, every stratum visited equally — integration
error drops to near machine epsilon for smooth functions. The
generator is totalizing.
Experiment: `experiments/bidder/stratified/`.

### Dithering (negative result)

Exact marginal uniformity does not help dithering. What dithering
needs is spatial uniformity (blue noise), which the generator does
not provide. Experiment: `experiments/bidder/dither/`.


## Known limitations

### Period-alphabet coupling

Period is (b-1) * b^(d-1), alphabet is b-1 — not independently
tunable. The 2^32 ceiling:

| base  | max d | max period      |
|-------|-------|-----------------|
| 10    | 9     | 900,000,000     |
| 256   | 4     | 4,278,190,080   |
| 65536 | 2     | 4,294,901,760   |

Multi-digit extraction and rekeying mitigate this. CRT-based
composition is the unexplored path to decoupling.

### Feistel fallback

8 rounds, simple round function, limited diffusion. Sufficient for
stratification and allocation. For strong PRP needs, use Speck32/64 mode.

## Open questions

1. **Composition.** CRT-based combination at different bases to
   decouple period from alphabet?

2. **Structure-aware permutation.** Exploit digit-block structure
   to reduce cost without sacrificing PRP quality?

3. **Spatial structure.** Extend to blue noise, or is
   post-processing required?
