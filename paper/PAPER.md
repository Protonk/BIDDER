# BIDDER: Exact Leading-Digit Sampling with Keyed Random Access

## §1. Abstract

We present a tool for exact leading-digit uniformity over arbitrary
digit-block parameters `(b, d)` — not asymptotic, not contingent
on power-of-two periods. The construction is two pieces: an
ACM-Champernowne substrate `M_n = {1} ∪ nZ_{>0}`, on which a
counting argument from positional notation gives exactly `b^(d-1)`
integers per leading digit on `[b^(d-1), b^d − 1]` (and exactly
`b^(d-1)·(n−1)/n²` n-prime atoms per leading digit when
`n² | b^(d-1)`); and a keyed cipher that is a stateless bijection
of `[0, P)` for any `P ∈ [2, 2³² − 1]`, implemented as Speck32/64
cycle-walking with an unbalanced Feistel fallback at small `P`. The
substrate is asked only to be exact; the cipher is asked only to
be a reproducible bijection. Their composition gives streaming
random-access to a deterministic anti-Benford reference, exact-
fold partitioning of arbitrary populations, format-preserving
permutation of small domains, and Monte Carlo with a known
endpoint and a measured FPC realisation gap, where the prefix-
mean variance at `N < P` follows the finite-population correction
`σ²/N · (P − N)/(P − 1)` up to a backend-dependent factor that M2
tabulates. The replication archive (~300 lines of C, two pinned
Python dependencies) reproduces every numerical claim from source.

## §2. What BIDDER is

BIDDER is two contracts plus a stable C surface.

**The substrate contract** (§4): the ACM monoid
`M_n = {1} ∪ nZ_{>0}` and its n-prime atoms (multiples of `n` not
divisible by `n²`) admit exact leading-digit counts on the
digit-class block `B_{b,d} = [b^(d-1), b^d − 1]`, plus an
`O(1)` random-access closed form for the `K`-th atom.

**The cipher contract** (§4): for any `period ∈ [2, 2³² − 1]` and
any key, `bidder_block_at(ctx, ·)` is a stateless bijection of
`[0, period)` — `at(i)` does not mutate `ctx` and does not require
`at(0), …, at(i−1)` to have been called first; identical key +
period produce identical permutations across runs and machines.

**The C surface** (five functions, `bidder_root.h`):

```c
int          bidder_cipher_init(bidder_block_ctx *ctx,
                                uint64_t period,
                                const uint8_t *key, size_t key_len);
int          bidder_block_at(const bidder_block_ctx *ctx,
                             uint64_t i, uint32_t *out);
const char  *bidder_block_backend(const bidder_block_ctx *ctx);
int          bidder_sawtooth_init(nprime_sequence_ctx *ctx,
                                  uint64_t n, uint64_t count);
int          bidder_sawtooth_at(const nprime_sequence_ctx *ctx,
                                uint64_t i, uint64_t *out);
```

The cipher path implements Speck32/64 cycle-walking with an
unbalanced 8-round Feistel fallback for `period < 2²⁶`. The
sawtooth path returns the `i`-th n-prime atom (0-indexed) in
ascending order via the closed form
`c_K = q·n + r + 1, (q, r) = divmod(K − 1, n − 1)`.

The two paths compose: open `bidder.cipher(P, key)` and
`bidder.sawtooth(n, P)` with `P` the smooth-block atom count from
clause 2 of the substrate contract, then iterate
`s.at(b.at(i))` for `i = 0, …, N − 1`. At `N = P`, this visits
the certified block exactly once and the leading-digit
distribution of the visited atoms is exact. For prefix exactness
at `N < P`, sample stratified by digit (the construction used in
the OUTLINE §7.1 worked example, deferred from this draft).

## §3. What the novelty is

BIDDER is not a new format-preserving encryption (FPE)
construction. Speck32/64 (Beaulieu et al. 2013), cycle-walking
(Black & Rogaway 2002), and Feistel networks are existing
building blocks. FF1 and FF3-1 with AES (NIST SP 800-38G) are the
reference FPE tools.

The novelty is the integrated finite-population substrate-and-
cipher contract with reproducible software. The substrate's
exact leading-digit counts on `B_{b,d}` are not invariants of
existing FPE work; the cipher's stateless random-access shape is
not a property of existing leading-digit-distribution work. The
combination — keyed, reproducible, streaming + random-access,
arbitrary `P ∈ [2, 2³² − 1]`, zero library dependencies, exact
leading-digit on arbitrary `(b, d)` — is what no existing tool
delivers simultaneously. The capability matrix in M3
(`paper/measurements/m3_results.md`) walks the comparator field;
BIDDER is the only row with all five axes.

**Where BIDDER sits.** Five lines of work are adjacent.
*PRNG-from-normal-numbers* (Bailey & Crandall 2002; Bailey 2004)
gives random access to the digits of a fixed Stoneham-class
constant via BBP-style extraction; BIDDER gives keyed random
access where the key selects among permutations rather than
indexing into a single fixed digit stream.
*Quasi-Monte Carlo* (Halton 1960; Sobol' 1967; Niederreiter 1992;
Owen 1995; Dick & Pillichshammer 2010) gives bounded star
discrepancy `O((log N)^d / N)` asymptotically; BIDDER gives
endpoint-exact at finite `N` with FPC-shaped interior at `N < P`.
*Exact ranged-integer generation* (Lemire 2019; Saad et al. 2020)
gives unbiased i.i.d. samplers over `[0, s)`; BIDDER is a
bijection that visits each value exactly once.
*Verifiable random functions* (Micali, Rabin & Vadhan 1999;
Gilad et al. 2017) give non-interactive proofs of correctness
from asymmetric keys; BIDDER's marginal is verifiable by
inspecting the algebra of §4.1, not by an asymmetric-key proof.
*Benford goodness-of-fit* (Lesperance et al. 2016; Cerioli &
Perrotta 2022) uses uniform `1/(b−1)` as the trivial null;
BIDDER provides a streaming addressable realisation of that
null at arbitrary block parameters. Each neighbour does one of
the things BIDDER does; none does all of them in the same object.

The substrate's exactness claims survive any keyed bijection
because they are statements about multisets and arithmetic
progressions. The cipher's job is bijection-hood; the substrate's
job is exactness; neither piece is asked to do the other's work.
The individual mathematical and cipher ingredients are elementary
or standard; the contribution is the finite-population contract
they make available as a tested tool.

## §4. What the proofs are

### §4.1. Theorem (Substrate contract)

Fix `(b, n, d)` with `b ≥ 2`, `d ≥ 1`, `n ≥ 2`. The following
hold simultaneously for the digit-class block
`B_{b,d} = [b^(d-1), b^d − 1]`:

1. **(Integer block-uniformity.)** The integers in `B_{b,d}` have
   leading-digit counts exactly `b^(d-1)` per digit
   `j ∈ {1, …, b−1}`.

2. **(Smooth-sieved uniformity.)** If `n² | b^(d-1)`, the n-prime
   atoms of `M_n` lying in `B_{b,d}` have leading-digit counts
   exactly `b^(d-1)·(n−1)/n²` per digit.

3. **(Family E.)** For `d ≥ 2` and `n ∈ [b^(d-1), ⌊(b^d−1)/(b−1)⌋]`,
   the n-prime atoms in `B_{b,d}` are exactly `{n, 2n, …, (b−1)n}`
   — one per leading digit. (Disjoint from clause 2 in this
   regime.)

4. **(Universal spread bound.)** For any `(b, n, d)`, per-leading-
   digit n-prime counts in `B_{b,d}` differ by at most 2.

5. **(Hardy random-access.)** For `K ≥ 1`, the `K`-th n-prime
   atom of `M_n` is `p_K = n · c_K` with `c_K = q·n + r + 1`
   where `(q, r) = divmod(K − 1, n − 1)`. Computing `p_K` from
   `K` is one divmod and arithmetic on
   `O(log K + log n)`-bit integers; no enumeration.

### §4.2. Proof sketches

*Clause 1.* A `d`-digit base-`b` integer is `d_1 d_2 … d_d` with
`d_1 ∈ {1, …, b−1}` and the remaining `d − 1` positions free over
`{0, …, b−1}`; each `d_1` accounts for `b^(d-1)` integers.

*Clause 2.* Under `n² | b^(d-1)`, each leading-digit strip of
length `b^(d-1)` starts at a multiple of `n²`; multiples of `n`
per strip are `b^(d-1)/n`, multiples of `n²` are `b^(d-1)/n²`;
subtracting gives the per-strip n-prime count, independent of
strip.

*Clause 3.* Three steps. *(In-block.)* For `k ∈ {1, …, b−1}`,
`k·n ≥ n ≥ b^(d-1)` and `k·n ≤ (b−1)·n ≤ b^d − 1` (the upper
bound follows from `n ≤ ⌊(b^d − 1)/(b − 1)⌋`); so each `k·n`
lies in `B_{b,d}`. Conversely, no other multiple of `n` does:
`b·n > b·b^(d-1) = b^d > b^d − 1`. *(Leading digit.)* For
`k ∈ {1, …, b−1}`, `k·b^(d-1) ≤ k·n < (k+1)·b^(d-1)` (the second
inequality from `n < b^(d-1) · b/(b−1) ≤ b^(d-1) · 2` for
`b ≥ 2`, refined by the upper bound on `n`), so `k·n` has
leading digit exactly `k`. *(Sieve removes nothing.)* For
`d ≥ 2`, `n² ≥ (b^(d-1))² = b^(2d-2) ≥ b^d` (the last step
holds for `d ≥ 2`), so `n² > b^d − 1` and no multiple of `n²`
lies in `B_{b,d}`. The atoms `{n, 2n, …, (b−1)n}` are therefore
n-primes (multiples of `n` not of `n²`) and exhaust the n-prime
atoms in the block.

*Clause 4.* The same divmod argument applied to a generic
interval bounds the count difference by 2.

*Clause 5.* The n-primes are an arithmetic progression with one
residue class deleted per period of `n`, so the inverse to
"the K-th term" is one divmod and constant arithmetic.

### §4.3. Cipher contract and endpoint-invariance corollary

BIDDER commits to: for any `period ∈ [2, 2³² − 1]` and any key,
`bidder_block_at(ctx, ·)` is a stateless keyed bijection of
`[0, period)`. *Bijection* — `{bidder_block_at(ctx, i) : 0 ≤ i <
period} = [0, period)` as a multiset; every output occurs
exactly once. *Stateless* — `at(i)` does not mutate `ctx` and
does not require `at(0), …, at(i−1)` to have been called first.
*Keyed* — identical key + period produce identical permutations
across runs and machines.

The cipher backend is Speck32/64 in cycle-walking mode for
`period ≥ 2²⁶` (Beaulieu et al. 2013; design follow-up notes
in Beaulieu et al. 2017; cycle-walking from Black & Rogaway
2002), with an unbalanced 8-round Feistel network for smaller
`period`. Speck32/64 has been the subject of public differential
cryptanalysis (Dinur 2014; Song, Huang & Yang 2016); the
unbalanced Feistel inherits the textbook PRF→PRP construction
(Luby & Rackoff 1988; Naor & Reingold 1999) with the standard
small-domain caveats (Durak & Vaudenay 2017). BIDDER's
correctness claim does not route through the fallback's PRP
advantage — the substrate's algebra in §4.1 gives the marginal
regardless.

*Corollary (endpoint invariance).* For any bijection
`π : [0, P) → [0, P)` and any `f`,

```
(1/P) Σ_{i=0}^{P-1} f(π(i)/P) = (1/P) Σ_{k=0}^{P-1} f(k/P) = R(f, P),
```

the left-endpoint Riemann sum, since `{π(0), …, π(P−1)}` is the
same multiset as `{0, …, P−1}`. The identity is bijection-trivial
— any keyed permutation has it. It is the reason BIDDER's
prefix-mean variance at `N = P` is machine-ε: no cipher-quality
argument is required at the endpoint.

### §4.4. FPC shape at `N < P`

For a uniformly-random permutation of `[0, P)`, the prefix-mean
variance for `N ≤ P` is

```
σ²/N · (P − N)/(P − 1).
```

BIDDER realises this shape with a backend-dependent gap. M2
(`paper/measurements/m2_results.md`) tabulates the ratio
(BIDDER / ideal) across a `(P, N)` grid. Best ratio in the
measured panel is ~1 at `P = 200`; worst is ~32× at
`(P, N) = (10000, 5000)`. The realisation gap is the empirical
price of the lightweight-cipher choice (Speck32 + 8-round minimal
Feistel, no library deps). FF1 with AES (D1) lands at ratio ~0.92
across the same two cells — sampling-consistent with the ideal —
at ~19–29× higher per-call cost.

The §3 substrate's exactness is unaffected by §4.4; §4.4 is a
statement about the cipher's PRP quality at sub-period prefixes,
not about leading-digit counts.

## §5. What it does

Two worked examples land the substrate contract and the cipher
contract in concrete statistical workflows. Three more cases
(§7.2 Benford-test null, §7.3 reproducible cross-validation,
§7.4 format-preserving permutation of small domains) are
implemented in `replication/use_case_*.py` and held in OUTLINE
for the expanded paper.

### §5.1. Stratified survey design with exact leading-digit strata

A survey designer drawing a sample of size `N_total` from a
finite population indexed by the digit-class block `B_{b,d}`
wants strata defined by leading digit. Standard practice draws
i.i.d. samples and post-stratifies, accepting binomial deviation
in realised stratum counts; the design weights then need post-
hoc adjustment for the realised sizes. §4.1 clause 1 partitions
`B_{b,d}` exactly into `b−1` leading-digit strata of size
`b^(d-1)` each, and the cipher's keyed bijection of
`[0, b^(d-1))` (one per stratum) gives a streaming reproducible
prefix sample of any size `N_j ≤ b^(d-1)` per stratum. The full
sample of size `Σ_j N_j` is the union of `b−1` keyed prefixes,
one per stratum, with each per-stratum count exactly `N_j`.

The comparator is proportional-allocation by post-stratify-after-
i.i.d.: realised stratum sizes are `Binomial(N_total, 1/(b−1))`
with standard deviation `√(N_total · (b−2)/(b−1)²)`. At
`(b, d) = (10, 4)` and `α_j = 0.1` across nine strata,
`replication/use_case_01_stratified_survey.py` reports the
BIDDER per-stratum count exactly `N_j = ⌊α · 1000⌋` at every
cell of the panel `α ∈ {0.1, 0.5, 1.0}` (100, 500, 1000 per
stratum); the 99th-percentile maximum stratum deviation under
i.i.d.-then-post-stratify across 1000 trials grows from 31
(`α = 0.1, N_total = 900`) to 97
(`α = 1.0, N_total = 9000`). Exact per-stratum counts mean
stratified-sample variance estimators apply the design weights
directly without post-hoc adjustment for realised sizes — the
`O(√N_total)` correction the i.i.d. approach otherwise carries.

### §5.2. Monte Carlo with known endpoint and measured FPC realisation gap

An analyst running prefix-mean Monte Carlo on a finite
population `[0, P)` wants the estimator's variance pinned at
the endpoint (exactly zero at `N = P`), the shape at `N < P`
known up to a measured gap from the ideal-permutation FPC,
reproducibility across runs (same key → same sequence), and
streaming (no materialised permutation of `[0, P)` in memory).
No single existing tool delivers all four.

§4.3's endpoint-invariance corollary gives the first: at
`N = P`, BIDDER's prefix-mean equals the left-endpoint Riemann
sum exactly, so variance across keys is machine-ε — no cipher-
quality argument is required at the endpoint. §4.4 gives the
second: at `N < P`, prefix-mean variance follows the FPC shape
`σ²/N · (P−N)/(P−1)` up to BIDDER's realisation gap (M2). At
`P = 2000`, `replication/use_case_06_variance_mc.py` reports
BIDDER variance at `N = P` of `6.15 × 10⁻³¹` (machine-ε; floating-
point round-off in the sum), ideal-FPC variance `0` exactly, and
i.i.d.-with-replacement variance `σ²/P ≈ 4.7 × 10⁻⁵` (never
zero). The realisation gap at `N < P` is U-shaped in `N/P`,
peaking at ratio `7.17` at `N = P/2 = 1000` and tapering to
ratio `1.00` at `N = P − 1` (sampling-consistent with the
ideal). Comparators each lack one property: i.i.d.-with-
replacement loses FPC (variance `σ²/N` at every `N`);
`numpy.random.permutation` gives ideal FPC but materialises
`[0, P)` in memory; FF1 / FF3 with AES is streaming and keyed
but heavyweight (~19–29× higher per-call cost than BIDDER per
D1); sort-by-i.i.d.-key needs `O(N log N)` extra memory and is
not deterministic across implementations. BIDDER provides the
four properties together at the cost of the measured FPC
realisation gap.

## §6. What the tests are

Eleven test files in three layers; `make test` runs all eleven on
a clean checkout (`paper/measurements/e4_smoke.md`).

**Layer 1 — unit and property tests** (six files in `tests/`):
`test_api.py`, `test_bidder.py`, `test_bidder_block.py`,
`test_bidder_root.py`, `test_sawtooth.py`, `test_speck.py`.
These exercise the Python wrappers against the C kernel and the
pure-Python oracle, plus property tests (bijection-hood at small
`P`, Speck round-trip equality, sawtooth monotonicity). The
implementation includes the published Beaulieu et al. Appendix
C test vectors as inline checks in `test_speck.py` and the
corresponding C test, so a reviewer can run those vectors against
the implementation independently of any of BIDDER's other code.

**Layer 2 — substrate verification** (`tests/test_acm_core.py`):
each clause of the §4.1 theorem has a verification test that
checks the implementation conforms to the proven statement over
a bounded range of `(b, n, d)`. The proofs live in §4.2; the
tests verify the implementation does not drift from them.

| §4.1 clause | proof | implementation | test function | range |
|---|---|---|---|---|
| 1. Integer block-uniformity | §4.2 | (fact about ℤ) | `test_block_boundary_*` | `b ≤ 12, d ≤ 5` |
| 2. Smooth-sieved | §4.2 | `bidder_sawtooth_at` | `test_block_uniformity_sieved_sufficient` | `b ≤ 12, d ≤ 5` |
| 3. Family E | §4.2 | `bidder_sawtooth_at` | `test_block_uniformity_sieved_family_e` | `b ≤ 12, d ≤ 5` |
| 4. Spread bound | §4.2 | `bidder_sawtooth_at` | `test_block_uniformity_sieved_spread_bound` | `b ≤ 12, d ≤ 5` |
| 5. Hardy random-access | §4.2 | `bidder_sawtooth_at` | `test_sawtooth.py` (oracle equality) | `n ≤ 20, K ≤ 10⁵` |

**Layer 3 — structural and statistical theory** (three files in
`tests/theory/`): `test_riemann_property.py` (the §4.3 endpoint
identity at `N = P`, exact equality, machine-ε),
`test_quadrature_rates.py` (Euler-Maclaurin convergence rates
for `f = x`, `sin(πx)`, `x²(1−x)²`, step), and
`test_fpc_shape.py` (the §4.4 FPC shape at `N < P`, the test
that gates M2's measurements).

The replication archive (`bidder-stat/`) runs end-to-end via
`make replicate` and reproduces every table referenced in this
paper from source: M1 (cycle-walking decision rule), M2 (FPC gap),
M3 (head-to-head comparison), M4 (wrapper throughput), D1
(FF1 / AES comparator), D4 (C-direct kernel), and five worked
use-case scripts (`replication/use_case_*.py`).

## §7. References

### Cipher provenance (§4)

- Beaulieu, R., Treatman-Clark, S., Shors, D., Weeks, B., Smith,
  J., & Wingers, L. (2013). *The SIMON and SPECK Families of
  Lightweight Block Ciphers.* IACR Cryptology ePrint Archive
  2013/404. The original specification; test vectors in
  Appendix C.
- Beaulieu, R., Shors, D., Smith, J., Treatman-Clark, S., Weeks,
  B., & Wingers, L. (2017). *Notes on the Design and Analysis of
  SIMON and SPECK.* IACR Cryptology ePrint Archive 2017/560.
  Post-publication design-and-analysis follow-up.
- Black, J., & Rogaway, P. (2002). *Ciphers with Arbitrary Finite
  Domains.* CT-RSA 2002, LNCS 2271, 114–130. The cycle-walking
  construction.
- Dinur, I. (2014). *Improved Differential Cryptanalysis of
  Round-Reduced Speck.* SAC 2014; IACR Cryptology ePrint Archive
  2014/320.
- Song, L., Huang, Z., & Yang, Q. (2016). *Automatic Differential
  Analysis of ARX Block Ciphers with Application to SPECK and
  LEA.* IACR Cryptology ePrint Archive 2016/209.
- Luby, M., & Rackoff, C. (1988). *How to Construct Pseudorandom
  Permutations from Pseudorandom Functions.* SIAM Journal on
  Computing, 17(2), 373–386.
- Naor, M., & Reingold, O. (1999). *On the Construction of
  Pseudorandom Permutations: Luby–Rackoff Revisited.* Journal of
  Cryptology, 12(1), 29–66.
- Durak, F. B., & Vaudenay, S. (2017). *Breaking the FF3 Format-
  Preserving Encryption Standard over Small Domains.* CRYPTO
  2017.

### Substrate and asymptotic background (§3, §4)

- Copeland, A. H., & Erdős, P. (1946). *Note on Normal Numbers.*
  Bulletin of the American Mathematical Society, 52, 857–860.
  The base-`b` normality of `C_b(n)`.
- Schiffer, J. (1986). Discrepancy of Champernowne-type
  concatenations. Cited from §3 (the asymptotic state of the
  art).

### Comparator framework (§3)

- NIST SP 800-38G (2016, errata 2019). *Recommendation for Block
  Cipher Modes of Operation: Methods for Format-Preserving
  Encryption (FF1/FF3-1).*

### Niche-against neighbours (§3 *Where BIDDER sits*)

- Bailey, D. H., & Crandall, R. E. (2002). *Random Generators
  and Normal Numbers.* Experimental Mathematics, 11(4), 527–546.
- Bailey, D. H. (2004). *A Pseudo-Random Number Generator Based
  on Normal Numbers.* LBNL-57489.
- Halton, J. H. (1960). *On the efficiency of certain quasi-random
  sequences of points in evaluating multi-dimensional integrals.*
  Numerische Mathematik, 2, 84–90.
- Sobol', I. M. (1967). *On the distribution of points in a cube
  and the approximate evaluation of integrals.* USSR
  Computational Mathematics and Mathematical Physics, 7(4),
  86–112.
- Niederreiter, H. (1992). *Random Number Generation and
  Quasi-Monte Carlo Methods.* SIAM CBMS-NSF Regional Conference
  Series in Applied Mathematics, vol. 63.
- Owen, A. B. (1995). *Randomly Permuted (t,m,s)-Nets and
  (t,s)-Sequences.* In Niederreiter, H. & Shiue, P. J.-S. (eds.),
  Monte Carlo and Quasi-Monte Carlo Methods in Scientific
  Computing. Springer Lecture Notes in Statistics, vol. 106,
  pp. 299–317.
- Dick, J., & Pillichshammer, F. (2010). *Digital Nets and
  Sequences: Discrepancy Theory and Quasi-Monte Carlo
  Integration.* Cambridge University Press.
- Lemire, D. (2019). *Fast Random Integer Generation in an
  Interval.* ACM Transactions on Modeling and Computer
  Simulation, 29(1), Article 3.
- Saad, F. A., Freer, C. E., Rinard, M. C., & Mansinghka, V. K.
  (2020). *Optimal Approximate Sampling from Discrete
  Probability Distributions.* Proceedings of the ACM on
  Programming Languages, 4(POPL), Article 36.
- Micali, S., Rabin, M., & Vadhan, S. (1999). *Verifiable Random
  Functions.* FOCS 1999, pp. 120–130.
- Gilad, Y., Hemo, R., Micali, S., Vlachos, G., & Zeldovich, N.
  (2017). *Algorand: Scaling Byzantine Agreements for
  Cryptocurrencies.* SOSP 2017, pp. 51–68.
- Cerioli, A., & Perrotta, D. (2022). *On Characterizations and
  Tests of Benford's Law.* Journal of the American Statistical
  Association, 117(540), 1887–1903.
- Lesperance, M., Reed, W. J., Stephens, M. A., Tsao, C., &
  Wilton, B. (2016). *Assessing Conformance with Benford's Law:
  Goodness-of-Fit Tests and Simultaneous Confidence Intervals.*
  PLoS ONE, 11(3), e0151235.
