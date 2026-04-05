# HCH Block Generator

Hilbert-Champernowne-Hyland uniform block generator. A pseudorandom
number generator that achieves exact output uniformity by
construction, not by statistical convergence.

Status: implemented in Python and C. Speck test vectors verified
against the NSA specification. Cross-language output parity confirmed.


## Motivation

Conventional PRNGs (xoshiro, Mersenne Twister, counter-mode AES)
produce output distributions that are statistically close to
uniform. The quality is verified empirically (TestU01, PractRand).
No finite prefix of the output is exactly uniform — it converges.

HCH factors the problem in two. An algebraic substrate provides
exact uniformity. A keyed permutation provides disorder. The
substrate guarantees the distribution; the permutation guarantees
unpredictability. Neither depends on the other.


## Background

### The monoid

For a positive integer n >= 2, the set nZ+ = {n, 2n, 3n, ...} is
a multiplicative monoid. The element n*k is irreducible in nZ+ if
and only if n does not divide k. These irreducibles are the
**n-primes**: multiples of n that are not multiples of n^2.

### The encoding

Fix a base b >= 2 and a depth K >= 1. For each n, list its first
K n-primes and concatenate their base-b representations after a
radix point to form a real number C_b(n). The leading base-b digit
of C_b(n) is the leading base-b digit of n.

### The uniformity guarantee

In base b, the integers in a complete digit block
[b^(d-1), b^d - 1] have their leading base-b digits exactly
equidistributed over {1, ..., b-1}. Each digit appears exactly
b^(d-1) times. This is a consequence of positional notation.

The Champernowne encoding preserves this: the leading digit of
C_b(n) is the leading digit of n. Over a complete digit block,
the output is exactly uniform. The error is zero.


## Construction

### Operating block

Choose a base b >= 2 and a digit-class index d >= 1. The
**operating block** is B_d = {b^(d-1), ..., b^d - 1}. This
block has size (b-1) * b^(d-1). The leading base-b digits of
its elements are exactly uniform over {1, ..., b-1}.

The base b determines the output alphabet size (b-1 symbols).
The digit class d determines the block size and therefore the
generator's period before repetition.

### Keyed permutation

The implementation uses Speck32/64 (Beaulieu et al., 2013) as
the keyed bijection pi_K: 22 rounds, 64-bit key, 32-bit block.
Block sizes up to 2^32 are supported. When the operating block
is much smaller than 2^32 (cycle-walk ratio > 64), a balanced
Feistel network with 8 rounds of SHA-256-derived round keys is
used instead. The mode is selected automatically at init time.

Key derivation: SHA-256(raw_key) truncated to 8 bytes for
Speck32/64, or SHA-256(raw_key || round_index) for each of the
8 Feistel round keys.

A reference implementation of the full Speck family (all 10
variants from Table 4.1) is available in `speck.py` with all 9
Appendix C test vectors verified. The generator uses only
Speck32/64.

### Output

The generator maintains a counter from 0 to block_size - 1.
Each call to `next()`:

    1. Permutes the counter through pi_K (with cycle-walking)
    2. Adds block_start to get an integer n in B_d
    3. Extracts the leading base-b digit of n
    4. Increments the counter (wraps at block_size)

Since pi_K is a bijection on B_d, and B_d has exactly b^(d-1)
elements with each leading digit, the output stream visits each
symbol in {1, ..., b-1} exactly b^(d-1) times over a full
period. The marginal distribution is exactly uniform at the end
of each period.

Within a period, the distribution follows the same deterministic
sawtooth as the raw ACM source, but the permutation scrambles
the phase — the sawtooth's position is unpredictable without
knowledge of the key.

### Parameters

| Parameter | Controls                    | Example          |
|-----------|-----------------------------|------------------|
| b         | alphabet size (b-1 symbols) | 256 -> 255 syms  |
| d         | period = (b-1) * b^(d-1)   | d=2 -> 65280     |
| key       | which permutation           | arbitrary bytes  |

Block size (b-1) * b^(d-1) must not exceed 2^32.

### Constants

    SPECK32_ROUNDS = 22
    FEISTEL_ROUNDS = 8
    MAX_CYCLE_WALK_RATIO = 64


## Implementations

Both implementations have identical feature sets and produce
identical output for identical inputs.

**Python.** `generator/hch.py`. Speck32/64 and Feistel fallback.
SHA-256 via hashlib. Class `HCH` with `next()`, `reset()`, and
Python iterator protocol.

**C.** `generator/hch.h` + `generator/hch.c`. Speck32/64 and
Feistel. Bundled SHA-256. No external dependencies. Functions
`hch_init()`, `hch_next()`, `hch_reset()`.

**Reference.** `generator/speck.py`. Full Speck family (all 10
variants, all 9 Appendix C test vectors). Used for cipher
verification, not by the generator.

**Tests.** `tests/test_hch.py` (18 tests including cross-language
check against hardcoded C output), `tests/test_speck.py` (13
tests), `tests/test_hch_c.c` (10 tests including cross-language
print for manual comparison).


## Observed properties

### Exact uniformity

Verified across base 2, 7, 10, 16, 256 and digit classes 2-10.
Full-period digit counts are exactly `period / (b-1)` for every
digit, for every key tested. The deviation at the period boundary
is 0.0000000000 — not approximately zero, zero.

### Deviation sawtooth

Between block boundaries, the maximum deviation from exact
uniformity follows a deterministic sawtooth. Each new digit
class starts with digit 1 overrepresented (all d-digit numbers
begin with leading digit 1). The deviation peaks at ~4/9 ≈ 0.444
within each tooth, then returns to zero at the next boundary.
The peak height does not shrink with N — what shrinks is the
peak's duration relative to the total sample.

### Interferometry

Under random-draw sampling, the HCH generator is
indistinguishable from numpy: same power spectrum, same addition
heatmap, same rolling shutter structure. The Speck permutation
destroys the deterministic phase structure of the raw ACM source.

Under consecutive-draw (sliding-window) sampling, the raw ACM
source shows resolved phase gradients that numpy destroys. But
the HCH generator, having been permuted, looks like numpy here
too. The permutation is mixing well.

### Contamination under arithmetic

Outputs from the HCH generator start exactly uniform. Under
repeated operations:

- **Pure addition**: the rolling shutter. Digit concentration
  cycles 1→9→1 forever, never converging to Benford.

- **Pure multiplication**: instant Benford. ~10 operations lock
  the distribution to log_10(1 + 1/d).

- **Single multiplication in 20,000 additions**: the one mul
  leaves a permanent scar. 10,000 additions before and after
  cannot prevent or reverse the Benford shift.

- **Alternating add/mul**: multiplication dominates. Two muls
  per add is enough for Benford to win completely. Two adds
  per mul creates a stalemate.

Multiplication is a one-way contaminant of uniform distributions.

### Stratified sampling

When HCH output is used for Monte Carlo integration, each output
digit maps to a stratum. At block boundaries, every stratum has
been visited exactly equally — free stratification with no
overhead.

For smooth functions (x, x², sin(πx), e^x, 1/(1+25x²)), the
integration error at block boundaries drops to near machine
epsilon — orders of magnitude below random sampling and
comparable to systematic (deterministic grid) stratification.
Between boundaries, performance matches random sampling.

The generator is totalizing at the boundaries: every stratum
has been exhausted, so the integral estimate is not converging
toward the true value — it has computed it (up to within-stratum
discretization).

### Dithering

Tested as a noise source for 1-bit image dithering. Both HCH and
numpy produce comparable visual results. Exact marginal uniformity
does not help dithering — what dithering needs is spatial
uniformity (blue noise), which the generator does not provide.
This confirms that the generator's strength is distributional,
not spatial.


### PractRand

Tested with PractRand 0.95 (core test suite, standard folding).

**The underlying permutation passes.** Speck32/64 in counter mode
(raw encrypted indices, 4 bytes per output) passes PractRand clean
through 16MB with zero anomalies. The PRP is sound.

**The leading-digit extraction fails.** HCH output (leading base-b
digits, {1, ..., b-1}) fails PractRand at 8MB on the FPF-14+6/16
cross-correlation test. The cause: the output alphabet excludes 0.
PractRand expects byte-stream uniformity over {0, ..., 2^n - 1}.
HCH produces stratum-uniform output over {1, ..., b-1}. The
missing value is structural and detectable.

**This is the right result.** PractRand tests whether a byte stream
is indistinguishable from random. HCH is not a byte-stream PRNG —
it is a stratum-coverage generator. Its uniformity guarantee is
over a non-power-of-2 alphabet that excludes 0. Testing it with
PractRand is a category error, like testing a Sobol sequence with
a runs test. The correct test for HCH is whether the stratum
coverage is exact at block boundaries — which it is, by
construction.

Test code: `tests/hch_stream.c` (HCH byte emitter),
`tests/speck_stream.c` (raw Speck counter mode).


### Multi-digit extraction

All d digit positions of each permuted index are exactly uniform,
not just the leading digit. Verified across base 2, 7, 10, 16,
digit classes 2-4:

- Position 0 (leading): uniform over {1, ..., b-1}.
- Positions 1..d-1: uniform over {0, ..., b-1}.
- All (d choose 2) pairwise joints: exactly uniform.
  Max deviation: zero.

This means each Speck evaluation yields d independent uniform
samples, not 1. For base 10 d=4, throughput multiplies by 4x.
The deeper digits include 0, giving alphabet {0, ..., b-1} —
a full base-b digit set.

The uniformity follows from the same counting argument: the
operating block B_d contains every d-digit base-b number
exactly once. The permutation is a bijection, so the multiset
of d-tuples is preserved. Each digit position's marginal is
the projection of a uniform distribution over all d-tuples,
which is itself uniform.

Experiment: `experiments/others/other_digits.py`.


### Reseeding

Rekeying at each period boundary via `SHA-256(old_key || period_counter)`
works without issue. Tested over 100 consecutive rekeyed periods
(90,000 total outputs, base 10 d=3):

- **Per-period uniformity preserved.** Every rekeyed period has
  exactly uniform digit counts. The algebraic guarantee is
  independent of the key and survives rekeying.

- **No detectable seam.** Chi-squared test on boundary bigrams
  (last output of period N, first output of period N+1) vs
  interior bigrams: 107.45 with 81 df, below the 3-sigma
  threshold. The transition is statistically invisible.

- **Cross-period distribution exact.** 90,000 outputs across
  100 periods: each digit appears exactly 10,000 times. The
  per-period exactness compounds — 100 periods × 100 per digit
  = 10,000 per digit, no rounding, no drift.

- **Each period produces a different sequence.** The rekeyed
  permutation is distinct. No two periods share output order.

The running deviation drops to near zero within the first period
and stays there indefinitely. Rekey events are invisible in the
deviation curve.

Experiment: `experiments/reseed/reseed_test.py`.


## Open questions

1. **Structure-aware permutation.** Can a permutation exploit
   the digit-block structure to reduce cost without sacrificing
   PRP quality?

2. **Composition.** Can HCH blocks at different bases or digit
   classes be composed (e.g., via Chinese Remainder Theorem) to
   cover arbitrary domain sizes without cycle-walking?

3. **Spatial structure.** Can the generator be extended to produce
   spatially uniform (blue noise) output, or is a post-processing
   step needed?


## Lineage

- **Hilbert** (c. 1900): introduced the arithmetic congruence
  monoid M_{1,4} = {1, 5, 9, 13, ...} to demonstrate non-unique
  factorization.
- **Champernowne** (1933): constructed a normal number by
  concatenating consecutive integers. The encoding here adapts
  this idea to irreducible elements of ACMs.
- **Hyland** (2026): identified the exact uniformity of leading
  digits in the ACM-Champernowne construction and proposed its
  application to pseudorandom generation.
