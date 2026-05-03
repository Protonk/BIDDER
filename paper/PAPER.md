# BIDDER: Exact Leading-Digit Sampling with Keyed Random Access

## §1. Abstract

*If we got rid of the odd numbers, what numbers would be odd?* The natural answer — the multiples of 2 that aren't multiples of 4 — generalises to the n-prime atoms of `M_n = {1} ∪ nℤ_{>0}` (multiples of `n` not divisible by `n²`). We present a tool around this construction: an exact counting theorem for n-prime atoms on arbitrary digit-class blocks `[b^(d-1), b^d − 1]` (`b^(d-1)·(n−1)/n²` per leading digit when `n² | b^(d-1)`; spread ≤ 2 universally), composed with a keyed cipher that is a stateless bijection of `[0, P)` for any `P ∈ [2, 2³² − 1]` (Speck32/64 cycle-walking with an unbalanced Feistel fallback at small `P`). The substrate is asked only to be exact; the cipher only to be a reproducible bijection. Their composition gives streaming random-access to a deterministic anti-Benford reference, exact-fold partitioning of arbitrary populations, format-preserving permutation of small domains, and Monte Carlo with a known endpoint and a measured FPC realisation gap. The replication archive (~300 lines of C, two pinned Python dependencies) reproduces every numerical claim from source.

## §2. Introduction

If we got rid of the odd numbers, what numbers would be odd?

The natural reading collapses on inspection. Remove the odd integers from `ℤ_{>0}` and you are left with `2ℤ_{>0} = {2, 4, 6, 8, 10, 12, …}`. Every element is divisible by 2 by construction, so nothing in this set is "odd" in the original sense. The question has to shift: not divisible by 2, but divisible *only* by 2 — not by 2². The new "odd" elements of `2ℤ_{>0}` are `{2, 6, 10, 14, 18, …} = 2ℤ \ 4ℤ`. These are the atoms of `2ℤ_{>0} ∪ {1}` as a multiplicative monoid — indecomposable elements that cannot be written as a product of two non-unit elements. Within the monoid, they play the role primes play in `ℤ`.

The generalisation is mechanical. For any `n ≥ 2`, the *n-prime atoms* of `M_n = {1} ∪ nℤ_{>0}` are `nℤ \ n²ℤ`: multiples of `n` not divisible by `n²`. The substantive question is how these atoms distribute across digit-class blocks `B_{b,d} = [b^(d-1), b^d − 1]`. The answer is a counting argument from positional notation. In the smooth regime where `n² | b^(d-1)`, each leading-digit strip of length `b^(d-1)` starts at a multiple of `n²`; subtracting multiples of `n²` from multiples of `n` per strip gives exactly `b^(d-1)·(n−1)/n²` atoms per leading digit, independent of strip. Outside the smooth regime, a universal spread bound of 2 holds, and a Family-E construction (`n ∈ [b^(d-1), ⌊(b^d−1)/(b−1)⌋]`) gives exact uniformity in a disjoint range. Hardy random-access — the closed form `c_K = q·n + r + 1` with `(q, r) = divmod(K − 1, n − 1)` — returns the `K`-th atom in `O(log K + log n)`-bit work, no enumeration. At `(b, n, d) = (10, 2, 4)`, for instance, the smooth condition holds (`4 | 1000`) and the count is exactly `250` atoms per leading digit on `[1000, 9999]`. The *substrate* of this paper is the bundle of these results into a single contract (§5.1).

The substrate is the answer to a small concrete question, with a counting argument. The novelty of this paper is the *contract* the substrate makes available, paired with a keyed cipher that delivers stateless random access on `[0, P)` for arbitrary `P`. The cipher is Speck32/64 (Beaulieu et al. 2013) in cycle-walking mode (Black & Rogaway 2002) for `P ≥ 2²⁶`, with an unbalanced 8-round Feistel network for smaller `P` (Luby & Rackoff 1988). Format-preserving encryption tooling — FF1 and FF3-1 with AES (NIST SP 800-38G) — supplies keyed bijections of arbitrary domains, but is sized for cryptographic-strength PRP, requires an AES library, and accepts AES-per-call cost. The contribution of this paper is the integrated finite-population substrate-and-cipher contract: a working tool of ~300 lines of C with no third-party dependencies, two structural contracts (substrate counting and cipher bijection), a measurement panel covering the cycle-walking decision rule, FPC realisation gap, comparator throughput, and wrapper / kernel performance, a stable C API (five functions in `bidder_root.h`), and use cases where exactness on arbitrary `(b, d)` or on arbitrary `P` is load-bearing. The replication archive (`bidder-stat/`) runs end-to-end via `make replicate` and reproduces every table referenced in this paper from source.

## §3. What BIDDER is

BIDDER is two contracts plus a stable C surface.

**The substrate contract.** The ACM monoid `M_n = {1} ∪ nZ_{>0}` and its n-prime atoms (multiples of `n` not divisible by `n²`) admit exact leading-digit counts on the digit-class block `B_{b,d} = [b^(d-1), b^d − 1]`, plus an `O(1)` random-access closed form for the `K`-th atom.

**The cipher contract.** For any `period ∈ [2, 2³² − 1]` and any key, `bidder_block_at(ctx, ·)` is a stateless bijection of `[0, period)` — `at(i)` does not mutate `ctx` and does not require `at(0), …, at(i−1)` to have been called first; identical key + period produce identical permutations across runs and machines.

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

The cipher path implements Speck32/64 cycle-walking with an unbalanced 8-round Feistel fallback for `period < 2²⁶`. The sawtooth path returns the `i`-th n-prime atom (0-indexed) in ascending order via the closed form `c_K = q·n + r + 1, (q, r) = divmod(K − 1, n − 1)`.

The two paths compose: open `bidder.cipher(P, key)` and `bidder.sawtooth(n, P)` with `P` the smooth-block atom count from clause 2 of the substrate contract, then iterate `s.at(b.at(i))` for `i = 0, …, N − 1`. At `N = P`, this visits the certified block exactly once and the leading-digit distribution of the visited atoms is exact. For prefix exactness at `N < P`, sample stratified by digit — one keyed prefix per leading-digit stratum (the worked construction is in §6.1).

## §4. What the novelty is

The substrate's exact leading-digit counts on `B_{b,d}` are not invariants of existing FPE work; the cipher's stateless random-access shape is not a property of existing leading-digit-distribution work. The combination is:

- **keyed** — same key produces the same permutation,
- **reproducible** — across runs and machines,
- **streaming + random-access** — no full-permutation materialisation,
- **arbitrary `P ∈ [2, 2³² − 1]`**,
- **zero library dependencies** in the C kernel,

plus the substrate's **exact leading-digit on arbitrary `(b, d)`** as a sixth property specific to BIDDER. The first five axes are walked across comparators below; BIDDER is the only row with all five, and the substrate axis is BIDDER's alone.

| comparator | keyed | reproducible | streaming | arbitrary `P` | extra deps |
|---|---|---|---|---|---|
| **BIDDER (cipher)** | yes | yes | yes (random-access) | yes (`P ≤ 2³² − 1`) | none |
| `numpy.random.permutation` | via seed | yes | no (in-memory) | yes | numpy |
| `random.shuffle` | via seed | yes | no (in-memory) | yes | stdlib only |
| sort-by-iid-key | via seed | yes | no (sort is global) | yes | numpy |
| i.i.d. (replacement) | via seed | yes | yes | yes | numpy / stdlib |
| FF1 / FF3-1 | yes | yes | yes (random-access) | yes | AES + FPE library |

The substrate's exactness claims survive any keyed bijection because they are statements about multisets and arithmetic progressions. The cipher's job is bijection-hood; the substrate's job is exactness; neither piece is asked to do the other's work. The individual mathematical and cipher ingredients are elementary or standard; the contribution is the finite-population contract they make available as a tested tool.

**Where BIDDER sits.** Three adjacent lines of work each do one of the things BIDDER does. *PRNG-from-normal-numbers* (Bailey & Crandall 2002; Bailey 2004) gives random access to the digits of a fixed Stoneham-class constant via BBP-style extraction; BIDDER gives keyed random access where the key selects among permutations rather than indexing into a single fixed digit stream. *Quasi-Monte Carlo* (Halton 1960; Sobol' 1967; Niederreiter 1992; Owen 1995; Dick & Pillichshammer 2010) gives bounded star discrepancy `O((log N)^d / N)` asymptotically; BIDDER gives endpoint-exact at finite `N` with FPC-shaped interior at `N < P`. *Exact ranged-integer generation* (Lemire 2019; Saad et al. 2020) gives unbiased i.i.d. samplers over `[0, s)`; BIDDER is a bijection that visits each value exactly once. None of the three delivers all of the BIDDER properties in the same object.

## §5. What the proofs are

### §5.1. Theorem (Substrate contract)

Fix `(b, n, d)` with `b ≥ 2`, `d ≥ 1`, `n ≥ 2`. The following hold simultaneously for the digit-class block `B_{b,d} = [b^(d-1), b^d − 1]`:

1. **(Integer block-uniformity.)** The integers in `B_{b,d}` have leading-digit counts exactly `b^(d-1)` per digit `j ∈ {1, …, b−1}`.

2. **(Smooth-sieved uniformity.)** If `n² | b^(d-1)`, the n-prime atoms of `M_n` lying in `B_{b,d}` have leading-digit counts exactly `b^(d-1)·(n−1)/n²` per digit.

3. **(Family E.)** For `d ≥ 2` and `n ∈ [b^(d-1), ⌊(b^d−1)/(b−1)⌋]`, the n-prime atoms in `B_{b,d}` are exactly `{n, 2n, …, (b−1)n}` — one per leading digit. (Disjoint from clause 2 in this regime.)

4. **(Universal spread bound.)** For any `(b, n, d)`, per-leading-digit n-prime counts in `B_{b,d}` differ by at most 2.

5. **(Hardy random-access.)** For `K ≥ 1`, the `K`-th n-prime atom of `M_n` is `p_K = n · c_K` with `c_K = q·n + r + 1` where `(q, r) = divmod(K − 1, n − 1)`. Computing `p_K` from `K` is one divmod and arithmetic on `O(log K + log n)`-bit integers; no enumeration.

### §5.2. Proof sketches

*Clause 1.* A `d`-digit base-`b` integer is `d_1 d_2 … d_d` with `d_1 ∈ {1, …, b−1}` and the remaining `d − 1` positions free over `{0, …, b−1}`; each `d_1` accounts for `b^(d-1)` integers.

*Clause 2.* Under `n² | b^(d-1)`, each leading-digit strip of length `b^(d-1)` starts at a multiple of `n²`; multiples of `n` per strip are `b^(d-1)/n`, multiples of `n²` are `b^(d-1)/n²`; subtracting gives the per-strip n-prime count, independent of strip.

*Clause 3.* Three steps. *(In-block.)* For `k ∈ {1, …, b−1}`, `k·n ≥ n ≥ b^(d-1)` and `k·n ≤ (b−1)·n ≤ b^d − 1` (the upper bound follows from `n ≤ ⌊(b^d − 1)/(b − 1)⌋`); so each `k·n` lies in `B_{b,d}`. Conversely, no other multiple of `n` does: `b·n > b·b^(d-1) = b^d > b^d − 1`. *(Leading digit.)* For `k ∈ {1, …, b−1}`, `k·b^(d-1) ≤ k·n < (k+1)·b^(d-1)` (the second inequality from `n < b^(d-1) · b/(b−1) ≤ b^(d-1) · 2` for `b ≥ 2`, refined by the upper bound on `n`), so `k·n` has leading digit exactly `k`. *(Sieve removes nothing.)* For `d ≥ 2`, `n² ≥ (b^(d-1))² = b^(2d-2) ≥ b^d` (the last step holds for `d ≥ 2`), so `n² > b^d − 1` and no multiple of `n²` lies in `B_{b,d}`. The atoms `{n, 2n, …, (b−1)n}` are therefore n-primes (multiples of `n` not of `n²`) and exhaust the n-prime atoms in the block.

*Clause 4.* The same divmod argument as clause 2 applied to a generic interval `[L, L + b^(d-1))` for `L` not necessarily a multiple of `n²`. The number of multiples of `n` in such an interval differs by at most 1 between adjacent strips, depending on where `L` falls modulo `n`; the analogous count for multiples of `n²` adds at most 1 more. Subtracting, per-strip n-prime counts differ from each other by at most 2.

*Clause 5.* The n-primes are an arithmetic progression with one residue class deleted per period of `n`, so the inverse to "the K-th term" is one divmod and constant arithmetic.

### §5.3. Cipher contract and endpoint-invariance corollary

BIDDER commits to: for any `period ∈ [2, 2³² − 1]` and any key, `bidder_block_at(ctx, ·)` is a stateless keyed bijection of `[0, period)`. *Bijection* — `{bidder_block_at(ctx, i) : 0 ≤ i < period} = [0, period)` as a multiset; every output occurs exactly once. *Stateless* — `at(i)` does not mutate `ctx` and does not require `at(0), …, at(i−1)` to have been called first. *Keyed* — identical key + period produce identical permutations across runs and machines.

The cipher backend is Speck32/64 in cycle-walking mode for `period ≥ 2²⁶` (Beaulieu et al. 2013; cycle-walking from Black & Rogaway 2002), with an unbalanced 8-round Feistel network for smaller `period` in the textbook PRF→PRP construction (Luby & Rackoff 1988). BIDDER's correctness claim does not route through the fallback's PRP advantage — the substrate's algebra in §5.1 gives the marginal regardless.

*Corollary (endpoint invariance).* For any bijection `π : [0, P) → [0, P)` and any `f`,

```
(1/P) Σ_{i=0}^{P-1} f(π(i)/P) = (1/P) Σ_{k=0}^{P-1} f(k/P) = R(f, P),
```

the left-endpoint Riemann sum, since `{π(0), …, π(P−1)}` is the same multiset as `{0, …, P−1}`. The identity is bijection-trivial — any keyed permutation has it. It is the reason BIDDER's prefix-mean variance at `N = P` is machine-ε: no cipher-quality argument is required at the endpoint.

### §5.4. FPC shape at `N < P`

For a uniformly-random permutation of `[0, P)`, the prefix-mean variance for `N ≤ P` is

```
σ²/N · (P − N)/(P − 1).
```

BIDDER realises this shape with a backend-dependent gap. The table below gives the measured ratio (BIDDER / ideal) across a `(P, N)` grid for `f = sin(πx)`, with each row a value of `P` and each column a fraction of `P`:

| `P` \ `N` | `0.10·P` | `0.25·P` | `0.50·P` | `0.75·P` | `0.90·P` |
|---|---|---|---|---|---|
| `200` | 1.022 | 1.170 | 1.336 | 1.212 | 1.133 |
| `500` | 1.257 | 1.839 | 2.242 | 1.884 | 1.407 |
| `1000` | 0.106 | 0.116 | 0.171 | 0.209 | 0.184 |
| `2000` | 3.260 | 5.452 | 6.754 | 5.617 | 3.353 |
| `5000` | 7.482 | 13.330 | 16.984 | 13.588 | 8.025 |
| `10000` | 13.982 | 25.274 | 31.995 | 25.773 | 14.677 |

Best ratio in the panel is `~1` at `P = 200`; worst is `~32` at `(P, N) = (10000, 5000)`. The gap is U-shaped in `N/P`, peaking near `N = P/2` and tapering toward both endpoints — applications that want tighter realisation should sample near `N = 0` or `N = P`. The `P = 1000` row reports ratios *below* 1 on the chosen integrand, an anomaly where the cipher's backend-specific symmetries happen to align with `sin(πx)` on a period-1000 grid; the effect does not persist across neighbouring `P` values. The realisation gap is the empirical price of the lightweight-cipher choice: the lightweight backends achieve only partial PRP-quality at sub-period prefixes, and FF1's higher AES round count is what drives its tighter realisation. FF1 with AES lands at ratio `~0.92` across the `(2000, 1000)` and `(10000, 5000)` cells — sampling-consistent with the ideal — at `~19–29×` higher per-call cost.

The substrate's exactness is unaffected by anything in this section: this is a statement about the cipher's PRP quality at sub-period prefixes, not about leading-digit counts.

## §6. What it does

The proofs above establish the contracts; the examples below show where those contracts change a statistical workflow. Two worked examples land the substrate contract and the cipher contract in concrete settings. Three further cases — a Benford-test null reference, reproducible cross-validation on non-power-of-two `n`, and format-preserving permutation of small domains — are implemented in `replication/use_case_*.py` and held for the expanded paper.

### §6.1. Stratified survey design with exact leading-digit strata

In audit sampling over account IDs, invoice magnitudes, or registry blocks, leading digit is sometimes a mandated reporting stratum: regulators ask for sample composition by leading digit, or the workflow downstream estimates a ratio per leading-digit class. A survey designer drawing a sample of size `N_total` from such a finite population indexed by the digit-class block `B_{b,d}` wants strata defined by leading digit. Standard practice draws i.i.d. samples and post-stratifies, accepting binomial deviation in realised stratum counts; the design weights then need post-hoc adjustment for the realised sizes. The substrate-contract clause for integer block-uniformity partitions `B_{b,d}` exactly into `b−1` leading-digit strata of size `b^(d-1)` each, and the cipher's keyed bijection of `[0, b^(d-1))` (one per stratum) gives a streaming reproducible prefix sample of any size `N_j ≤ b^(d-1)` per stratum. The full sample of size `Σ_j N_j` is the union of `b−1` keyed prefixes, one per stratum, with each per-stratum count exactly `N_j`.

The comparator is proportional-allocation by post-stratify-after-i.i.d.: realised stratum sizes are `Binomial(N_total, 1/(b−1))` with standard deviation `√(N_total · (b−2)/(b−1)²)`. At `(b, d) = (10, 4)` and `α_j = 0.1` across nine strata, `replication/use_case_01_stratified_survey.py` reports the BIDDER per-stratum count exactly `N_j = ⌊α · 1000⌋` at every cell of the panel `α ∈ {0.1, 0.5, 1.0}` (100, 500, 1000 per stratum); the 99th-percentile maximum stratum deviation under i.i.d.-then-post-stratify across 1000 trials grows from 31 (`α = 0.1, N_total = 900`) to 97 (`α = 1.0, N_total = 9000`). Exact per-stratum counts mean stratified-sample variance estimators apply the design weights directly without post-hoc adjustment for realised sizes — the `O(√N_total)` correction the i.i.d. approach otherwise carries.

### §6.2. Monte Carlo with known endpoint and measured FPC realisation gap

An analyst running prefix-mean Monte Carlo on a finite population `[0, P)` wants the estimator's variance pinned at the endpoint (exactly zero at `N = P`), the shape at `N < P` known up to a measured gap from the ideal-permutation FPC, reproducibility across runs (same key → same sequence), and streaming (no materialised permutation of `[0, P)` in memory). No single existing tool delivers all four.

The endpoint-invariance corollary gives the first: at `N = P`, BIDDER's prefix-mean equals the left-endpoint Riemann sum exactly, so variance across keys is machine-ε — no cipher-quality argument is required at the endpoint. The FPC-shape result gives the second: at `N < P`, prefix-mean variance follows `σ²/N · (P−N)/(P−1)` up to BIDDER's measured realisation gap. At `P = 2000`, `replication/use_case_06_variance_mc.py` reports BIDDER variance at `N = P` of `6.15 × 10⁻³¹` (machine-ε; floating-point round-off in the sum), ideal-FPC variance `0` exactly, and i.i.d.-with-replacement variance `σ²/P ≈ 4.7 × 10⁻⁵` (never zero). The realisation gap at `N < P` is U-shaped in `N/P`, peaking at ratio `7.17` at `N = P/2 = 1000` and tapering to ratio `1.00` at `N = P − 1` (sampling-consistent with the ideal). Comparators each lack one property: i.i.d.-with-replacement loses FPC (variance `σ²/N` at every `N`); `numpy.random.permutation` gives ideal FPC but materialises `[0, P)` in memory; FF1 / FF3 with AES is streaming and keyed but ~19–29× heavier per call than BIDDER on the same workload; sort-by-i.i.d.-key needs `O(N log N)` extra memory and is not deterministic across implementations. BIDDER provides the four properties together at the cost of the measured FPC realisation gap.

## §7. What the tests are

Eleven test files in three layers; `make test` runs all eleven on a clean checkout (`paper/measurements/e4_smoke.md`).

**Layer 1 — unit and property tests** (six files in `tests/`): `test_api.py`, `test_bidder.py`, `test_bidder_block.py`, `test_bidder_root.py`, `test_sawtooth.py`, `test_speck.py`. These exercise the Python wrappers against the C kernel and the pure-Python oracle, plus property tests (bijection-hood at small `P`, Speck round-trip equality, sawtooth monotonicity). The implementation includes the published Beaulieu et al. Appendix C test vectors as inline checks in `test_speck.py` and the corresponding C test, so a reviewer can run those vectors against the implementation independently of any of BIDDER's other code.

**Layer 2 — substrate verification** (`tests/test_acm_core.py`): each clause of the substrate-contract theorem has a verification test that checks the implementation conforms to the proven statement over a finite parameter sweep. The proof sketches cover all valid parameters; the tests below cover the listed sweep (every triple in the sweep is checked exhaustively).

| §5.1 clause | proof | implementation | test function | tested sweep |
|---|---|---|---|---|
| 1. Integer block-uniformity | §5.2 | (fact about ℤ) | `test_block_boundary_*` | base 10, `d ∈ {1, …, 9}` |
| 2. Smooth-sieved | §5.2 | `bidder_sawtooth_at` | `test_block_uniformity_sieved_sufficient` | `b, n ∈ {2, …, 10}`, `d ∈ {1, …, 5}` |
| 3. Family E | §5.2 | `bidder_sawtooth_at` | `test_block_uniformity_sieved_family_e` | `b ∈ {2, …, 10}`, `d ∈ {2, …, 5}` |
| 4. Spread bound | §5.2 | `bidder_sawtooth_at` | `test_block_uniformity_sieved_spread_bound` | `b, n ∈ {2, …, 10}`, `d ∈ {1, …, 5}` |
| 5. Hardy random-access | §5.2 | `bidder_sawtooth_at` | `test_at_matches_acm_n_primes` (oracle); `test_kth_prime_*` (closed-form vs enumeration) | sawtooth oracle: `n ∈ {2, …, 12}`; closed-form: `n ∈ {2, …, 9999}` |

**Layer 3 — structural and statistical theory** (three files in `tests/theory/`): `test_riemann_property.py` (the endpoint identity at `N = P`, exact equality, machine-ε), `test_quadrature_rates.py` (Euler-Maclaurin convergence rates for `f = x`, `sin(πx)`, `x²(1−x)²`, step), and `test_fpc_shape.py` (the FPC shape at `N < P`, the test that gates the realisation-gap measurement).

The replication archive (`bidder-stat/`) runs end-to-end via `make replicate` and reproduces every table and every numerical claim in this paper from source: the cycle-walking decision sweep, the FPC realisation-gap grid, the comparator throughput panel, the wrapper / kernel performance taxonomy, the FF1 / AES comparator measurement, and the five worked use-case scripts (`replication/use_case_*.py`).

## §8. References

- Bailey, D. H. (2004). *A Pseudo-Random Number Generator Based on Normal Numbers.* Lawrence Berkeley National Laboratory Technical Report LBNL-57489.
- Bailey, D. H., & Crandall, R. E. (2002). *Random Generators and Normal Numbers.* Experimental Mathematics, 11(4), 527–546.
- Beaulieu, R., Treatman-Clark, S., Shors, D., Weeks, B., Smith, J., & Wingers, L. (2013). *The SIMON and SPECK Families of Lightweight Block Ciphers.* IACR Cryptology ePrint Archive 2013/404. The original specification; test vectors in Appendix C.
- Black, J., & Rogaway, P. (2002). *Ciphers with Arbitrary Finite Domains.* CT-RSA 2002, LNCS 2271, 114–130. The cycle-walking construction.
- Copeland, A. H., & Erdős, P. (1946). *Note on Normal Numbers.* Bulletin of the American Mathematical Society, 52, 857–860.
- Dick, J., & Pillichshammer, F. (2010). *Digital Nets and Sequences: Discrepancy Theory and Quasi-Monte Carlo Integration.* Cambridge University Press.
- Halton, J. H. (1960). *On the efficiency of certain quasi-random sequences of points in evaluating multi-dimensional integrals.* Numerische Mathematik, 2, 84–90.
- Lemire, D. (2019). *Fast Random Integer Generation in an Interval.* ACM Transactions on Modeling and Computer Simulation, 29(1), Article 3.
- Luby, M., & Rackoff, C. (1988). *How to Construct Pseudorandom Permutations from Pseudorandom Functions.* SIAM Journal on Computing, 17(2), 373–386.
- Niederreiter, H. (1992). *Random Number Generation and Quasi-Monte Carlo Methods.* SIAM CBMS-NSF Regional Conference Series in Applied Mathematics, vol. 63.
- NIST SP 800-38G (2016, errata 2019). *Recommendation for Block Cipher Modes of Operation: Methods for Format-Preserving Encryption (FF1/FF3-1).*
- Owen, A. B. (1995). *Randomly Permuted (t,m,s)-Nets and (t,s)-Sequences.* In Niederreiter, H. & Shiue, P. J.-S. (eds.), Monte Carlo and Quasi-Monte Carlo Methods in Scientific Computing. Springer Lecture Notes in Statistics, vol. 106, pp. 299–317.
- Saad, F. A., Freer, C. E., Rinard, M. C., & Mansinghka, V. K. (2020). *Optimal Approximate Sampling from Discrete Probability Distributions.* Proceedings of the ACM on Programming Languages, 4(POPL), Article 36.
- Schiffer, J. (1986). Discrepancy of Champernowne-type concatenations.
- Sobol', I. M. (1967). *On the distribution of points in a cube and the approximate evaluation of integrals.* USSR Computational Mathematics and Mathematical Physics, 7(4), 86–112.
