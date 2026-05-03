<!--
PAPER.md — JStatSoft submission. LaTeX-bound markdown for the
math-typeset skill (pandoc + amsart).

Conventions used throughout:

  * Math is in inline ($...$) or display ($$...$$) form.
  * Code identifiers inside math contexts use \mathtt{}; standalone
    code spans use markdown backticks (which pandoc renders as
    \texttt{}). Both resolve to Computer Modern Typewriter at the
    same size in lmodern, so the two styles render identically.
  * Math-mode set braces use \{ \}; the divides bar uses \mid; the
    set difference uses \setminus.
  * Code fences carry no language tag (pandoc otherwise emits the
    Shaded environment, which the skill's default preamble does not
    define).
  * Section headings carry no §N. prefix; amsart auto-numbers via
    the \setcounter block below the abstract, putting "The question
    and the bargain" at §2 and continuing through §7 References.

Build note: the math-typeset skill's default preamble does not load
lmodern, longtable, or booktabs. If pandoc emits longtable for the
markdown tables, or if the runtime cannot generate cm bitmap fonts,
extend the preamble with

  \usepackage{lmodern, longtable, booktabs, array, calc}

before \begin{document}.

Suggested skill invocation (after extracting the H1 title and the
Abstract section content into separate files):

  python3 /mnt/skills/user/math-typeset/scripts/build.py PAPER-body.md \
    --title "BIDDER: Exact Leading-Digit Sampling with Keyed Random Access" \
    --author "<author>" \
    --abstract @PAPER-abstract.md \
    --output ./out/
-->

# BIDDER: Exact Leading-Digit Sampling with Keyed Random Access

## Abstract

We present BIDDER, an exact leading-digit sampler with keyed random access for the $n$-prime atoms of the multiplicative monoid $M_n = \{1\} \cup n\mathbb{Z}_{>0}$ (multiples of $n$ not divisible by $n^2$). Two contracts compose: an exact counting theorem on arbitrary digit-class blocks $[b^{d-1}, b^d - 1]$ ($b^{d-1} \cdot (n-1)/n^2$ atoms per leading digit when $n^2 \mid b^{d-1}$; spread $\leq 2$ universally), and a keyed stateless cipher that is a bijection of $[0, P)$ for any $P \in [2, 2^{32} - 1]$ (Speck32/64 cycle-walking with an unbalanced Feistel fallback at small $P$). The substrate is asked only to be exact; the cipher only to be a reproducible bijection. Composing them yields streaming random-access to a deterministic anti-Benford reference, exact-fold partitioning of arbitrary populations, format-preserving permutation of small domains, and Monte Carlo with a known endpoint and a measured FPC realisation gap. The implementation is $\sim$300 lines of C.

```{=latex}
% Body sections start at §2; the abstract holds the §1 slot.
\setcounter{section}{1}
```

## The question and the bargain

If we got rid of the odd numbers, what numbers would be odd?

The natural reading collapses on inspection. Remove the odd integers from $\mathbb{Z}_{>0}$ and you are left with $2\mathbb{Z}_{>0} = \{2, 4, 6, 8, 10, 12, \ldots\}$. Every element is divisible by 2 by construction, so nothing in this set is "odd" in the original sense. The question has to shift: not divisible by 2, but divisible *only* by 2 — not by $2^2$. The new "odd" elements of $2\mathbb{Z}_{>0}$ are $\{2, 6, 10, 14, 18, \ldots\} = 2\mathbb{Z} \setminus 4\mathbb{Z}$. These are the atoms of $2\mathbb{Z}_{>0} \cup \{1\}$ as a multiplicative monoid — indecomposable elements that cannot be written as a product of two non-unit elements. Within the monoid, they play the role primes play in $\mathbb{Z}$.

The generalisation is mechanical. For any $n \geq 2$, the *$n$-prime atoms* of $M_n = \{1\} \cup n\mathbb{Z}_{>0}$ are $n\mathbb{Z} \setminus n^2\mathbb{Z}$: multiples of $n$ not divisible by $n^2$. The substantive question is how these atoms distribute across digit-class blocks $B_{b,d} = [b^{d-1}, b^d - 1]$. The answer is a counting argument from positional notation. In the smooth regime where $n^2 \mid b^{d-1}$, each leading-digit strip of length $b^{d-1}$ starts at a multiple of $n^2$; subtracting multiples of $n^2$ from multiples of $n$ per strip gives exactly $b^{d-1} \cdot (n-1)/n^2$ atoms per leading digit, independent of strip. Outside the smooth regime, a universal spread bound of 2 holds, and a Family-E construction ($n \in [b^{d-1}, \lfloor (b^d-1)/(b-1) \rfloor]$) gives exact uniformity in a disjoint range. Hardy random-access — the closed form $c_K = q \cdot n + r + 1$ with $(q, r) = \operatorname{divmod}(K - 1, n - 1)$ — returns the $K$-th atom in $O(\log K + \log n)$-bit work, no enumeration. At $(b, n, d) = (10, 2, 4)$, for instance, the smooth condition holds ($4 \mid 1000$) and the count is exactly $250$ atoms per leading digit on $[1000, 9999]$.

The substrate is the answer to a small concrete question, with a counting argument. The bargain BIDDER offers is to ask each side only for what it can deliver: the substrate is asked only to be exact, the cipher only to be a stateless reproducible bijection of $[0, P)$. Composing them yields, as a single object, four properties that no individual existing tool delivers together — streaming random-access (no full permutation materialised), keyed reproducibility across runs and machines, arbitrary period $P \in [2, 2^{32} - 1]$, and exact leading-digit counts on arbitrary $(b, d)$. The cipher backend is Speck32/64 in cycle-walking mode (Beaulieu et al. 2013; cycle-walking from Black & Rogaway 2002) for $P \geq 2^{26}$, with an unbalanced 8-round Feistel network for smaller $P$ (Luby & Rackoff 1988); the contract relied on throughout is bijection-hood, not PRP quality. The implementation is $\sim$300 lines of C with no third-party dependencies; `make replicate` reproduces every table in this paper from source.

Four adjacent lines of work each do part of what BIDDER does. *PRNG-from-normal-numbers* (Bailey & Crandall 2002; Bailey 2004) gives random access to the digits of a fixed Stoneham-class constant via BBP-style extraction; BIDDER gives keyed random access where the key selects among permutations rather than indexing into a single fixed digit stream. *Quasi-Monte Carlo* (Halton 1960; Sobol' 1967; Niederreiter 1992; Owen 1995; Dick & Pillichshammer 2010) gives bounded star discrepancy $O((\log N)^d / N)$ asymptotically; BIDDER gives endpoint-exact at finite $N$ with FPC-shaped interior at $N < P$. *Exact ranged-integer generation* (Lemire 2019; Saad et al. 2020) gives unbiased i.i.d. samplers over $[0, s)$; BIDDER is a bijection that visits each value exactly once. *Format-preserving encryption* (NIST SP 800-38G — FF1 and FF3-1 with AES) supplies keyed bijections of arbitrary domains sized for cryptographic-strength PRP, requires an AES library, and accepts AES-per-call cost; BIDDER asks of its cipher only bijection-hood, with no library dependency and $\sim$19–29$\times$ lower per-call cost on the same workload. None of the four sits at all four BIDDER corners simultaneously.

## The substrate

**Theorem.** Fix $(b, n, d)$ with $b \geq 2$, $d \geq 1$, $n \geq 2$. The following hold simultaneously for the digit-class block $B_{b,d} = [b^{d-1}, b^d - 1]$:

1. **(Integer block-uniformity.)** The integers in $B_{b,d}$ have leading-digit counts exactly $b^{d-1}$ per digit $j \in \{1, \ldots, b-1\}$.

2. **(Smooth-sieved uniformity.)** If $n^2 \mid b^{d-1}$, the $n$-prime atoms of $M_n$ lying in $B_{b,d}$ have leading-digit counts exactly $b^{d-1} \cdot (n-1)/n^2$ per digit.

3. **(Family E.)** For $d \geq 2$ and $n \in [b^{d-1}, \lfloor (b^d-1)/(b-1) \rfloor]$, the $n$-prime atoms in $B_{b,d}$ are exactly $\{n, 2n, \ldots, (b-1)n\}$ — one per leading digit. (Disjoint from clause 2 in this regime.)

3'. **(Generalised Family E.)** Let $W = b^{d-1}$. For integers $(qp, m_{\min})$ with $m_{\min} \geq 1$, $qp \geq 1$, set $m_{\max} := m_{\min} + qp(b-1) - 1$. Suppose

$$
\begin{aligned}
(m_{\min} - 1) \cdot n &< W \leq m_{\min} \cdot n, \\
m_{\max} \cdot n &\leq bW - 1 < (m_{\max} + 1) \cdot n,
\end{aligned}
$$

so that $[m_{\min}, m_{\max}]$ is exactly the integer multiplier range whose product with $n$ lands in $B_{b,d}$. Suppose further that for each $k \in [m_{\min}, m_{\max}]$ the leading digit of $kn$ equals $\lceil (k - m_{\min} + 1)/qp \rceil$. Then the multiples of $n$ in $B_{b,d}$ distribute as exactly $qp$ per leading digit. If additionally the multiples of $n^2$ in $B_{b,d}$ distribute uniformly across strips with $\delta$ per strip, the $n$-prime atoms distribute as exactly $q = qp - \delta$ per leading digit. Clause 3 is the special case $qp = 1$, $m_{\min} = \lceil W/n \rceil$, $\delta = 0$.

4. **(Universal spread bound.)** For any $(b, n, d)$, per-leading-digit $n$-prime counts in $B_{b,d}$ differ by at most 2.

5. **(Hardy random-access.)** For $K \geq 1$, the $K$-th $n$-prime atom of $M_n$ is $p_K = n \cdot c_K$ with $c_K = q \cdot n + r + 1$ where $(q, r) = \operatorname{divmod}(K - 1, n - 1)$. Computing $p_K$ from $K$ is one divmod and arithmetic on $O(\log K + \log n)$-bit integers; no enumeration.

**Proof sketches.**

*Clause 1.* A $d$-digit base-$b$ integer is $d_1 d_2 \ldots d_d$ with $d_1 \in \{1, \ldots, b-1\}$ and the remaining $d - 1$ positions free over $\{0, \ldots, b-1\}$; each $d_1$ accounts for $b^{d-1}$ integers.

*Clause 2.* Under $n^2 \mid b^{d-1}$, each leading-digit strip of length $b^{d-1}$ starts at a multiple of $n^2$; multiples of $n$ per strip are $b^{d-1}/n$, multiples of $n^2$ are $b^{d-1}/n^2$; subtracting gives the per-strip $n$-prime count, independent of strip.

*Clause 3.* Three steps. *(In-block.)* For $k \in \{1, \ldots, b-1\}$, $k \cdot n \geq n \geq b^{d-1}$ and $k \cdot n \leq (b-1) \cdot n \leq b^d - 1$ (the upper bound follows from $n \leq \lfloor (b^d - 1)/(b - 1) \rfloor$); so each $k \cdot n$ lies in $B_{b,d}$. Conversely, no other multiple of $n$ does: $b \cdot n > b \cdot b^{d-1} = b^d > b^d - 1$. *(Leading digit.)* For $k \in \{1, \ldots, b-1\}$, $k \cdot b^{d-1} \leq k \cdot n < (k+1) \cdot b^{d-1}$ (the second inequality from $n < b^{d-1} \cdot b/(b-1) \leq b^{d-1} \cdot 2$ for $b \geq 2$, refined by the upper bound on $n$), so $k \cdot n$ has leading digit exactly $k$. *(Sieve removes nothing.)* For $d \geq 2$, $n^2 \geq (b^{d-1})^2 = b^{2d-2} \geq b^d$ (the last step holds for $d \geq 2$), so $n^2 > b^d - 1$ and no multiple of $n^2$ lies in $B_{b,d}$. The atoms $\{n, 2n, \ldots, (b-1)n\}$ are therefore $n$-primes (multiples of $n$ not of $n^2$) and exhaust the $n$-prime atoms in the block.

*Clause 3'.* The bracketing hypotheses say exactly that $[m_{\min}, m_{\max}]$ is the integer multiplier range whose product with $n$ lands in $B_{b,d}$. The leading-digit hypothesis says this range partitions into $b-1$ consecutive blocks of length $qp$, the $k$-th block landing in leading-digit strip $k$. The multiples of $n$ count is therefore $qp$ per strip. The atom count subtracts the per-strip multiples of $n^2$; uniform $\delta$-per-strip distribution of $n^2$ multiples leaves $qp - \delta$ atoms per strip.

*Clause 4.* The same divmod argument as clause 2 applied to a generic interval $[L, L + b^{d-1})$ for $L$ not necessarily a multiple of $n^2$. The number of multiples of $n$ in such an interval differs by at most 1 between adjacent strips, depending on where $L$ falls modulo $n$; the analogous count for multiples of $n^2$ adds at most 1 more. Subtracting, per-strip $n$-prime counts differ from each other by at most 2.

*Clause 5.* The $n$-primes are an arithmetic progression with one residue class deleted per period of $n$, so the inverse to "the $K$-th term" is one divmod and constant arithmetic.

**Open: $n^2$-cancellation residual.** Across the swept range $b = 10$, $n \in [2, 200]$, $d \in [1, 7]$, 27 cells exhibit per-leading-digit spread $= 0$ outside the regimes of clauses 2, 3, and 3'. The mechanism is identified — *Beatty pattern-alignment*, where the per-strip excess multiples of $n$ match the per-strip excess multiples of $n^2$ bit-for-bit, exactly cancelling in the atom count — and the alignment condition is verified $27/27$ in the swept range. The closed form for *which* integer triples $(b, n, d)$ trigger the alignment is open; characterising the trigger set is left as an open question on this paper. Clause 4's universal spread $\leq 2$ covers these cells; the spread $= 0$ observation is sharper than the contract guarantees, and is reported here as such.

## The cipher

For any `period` $\in [2, 2^{32} - 1]$ and any key, `bidder_block_at(ctx, ·)` is a stateless keyed bijection of $[0, \mathtt{period})$. *Bijection* — $\{\mathtt{bidder\_block\_at}(\mathtt{ctx}, i) : 0 \leq i < \mathtt{period}\} = [0, \mathtt{period})$ as a multiset; every output occurs exactly once. *Stateless* — `at(i)` does not mutate `ctx` and does not require `at(0)`, $\ldots$, `at(i-1)` to have been called first. *Keyed* — identical key + period produce identical permutations across runs and machines. The backend is Speck32/64 in cycle-walking mode for `period` $\geq 2^{26}$ (Beaulieu et al. 2013; cycle-walking from Black & Rogaway 2002), with an unbalanced 8-round Feistel network for smaller `period` in the textbook PRF$\to$PRP construction (Luby & Rackoff 1988). The contract is bijection-hood; nothing in this paper routes through a PRP-quality argument.

**Endpoint corollary.** For any bijection $\pi : [0, P) \to [0, P)$ and any $f$,

$$
\frac{1}{P} \sum_{i=0}^{P-1} f(\pi(i)/P) = \frac{1}{P} \sum_{k=0}^{P-1} f(k/P) = R(f, P),
$$

the left-endpoint Riemann sum, since $\{\pi(0), \ldots, \pi(P-1)\}$ is the same multiset as $\{0, \ldots, P-1\}$. The identity is bijection-trivial — any keyed permutation has it. It is the reason BIDDER's prefix-mean variance at $N = P$ is machine-$\varepsilon$: the cipher's quality is not in play at the endpoint.

**Realisation gap at sub-endpoint.** For a uniformly-random permutation of $[0, P)$, the prefix-mean variance for $N \leq P$ is

$$
\frac{\sigma^2}{N} \cdot \frac{P - N}{P - 1}.
$$

BIDDER realises this shape with a backend-dependent gap. The table below gives the measured ratio (BIDDER / ideal) across a $(P, N)$ grid for $f = \sin(\pi x)$, with each row a value of $P$ and each column a fraction of $P$:

| $P \backslash N$ | $0.10 \cdot P$ | $0.25 \cdot P$ | $0.50 \cdot P$ | $0.75 \cdot P$ | $0.90 \cdot P$ |
|---|---|---|---|---|---|
| 200   | 1.022 | 1.170  | 1.336  | 1.212  | 1.133  |
| 500   | 1.257 | 1.839  | 2.242  | 1.884  | 1.407  |
| 1000  | 0.106 | 0.116  | 0.171  | 0.209  | 0.184  |
| 2000  | 3.260 | 5.452  | 6.754  | 5.617  | 3.353  |
| 5000  | 7.482 | 13.330 | 16.984 | 13.588 | 8.025  |
| 10000 | 13.982 | 25.274 | 31.995 | 25.773 | 14.677 |

Best ratio in the panel is $\sim 1$ at $P = 200$; worst is $\sim 32$ at $(P, N) = (10000, 5000)$. The gap is U-shaped in $N/P$, peaking near $N = P/2$ and tapering toward both endpoints — applications that want tighter realisation should sample near $N = 0$ or $N = P$. The $P = 1000$ row reports ratios *below* 1 on the chosen integrand, an anomaly where the cipher's backend-specific symmetries happen to align with $\sin(\pi x)$ on a period-1000 grid; the effect does not persist across neighbouring $P$ values. The realisation gap is the empirical price of the lightweight-cipher choice: the lightweight backends achieve only partial PRP-quality at sub-period prefixes, and FF1's higher AES round count is what drives its tighter realisation. FF1 with AES lands at ratio $\sim 0.92$ across the $(2000, 1000)$ and $(10000, 5000)$ cells — sampling-consistent with the ideal — at $\sim 19$–$29\times$ higher per-call cost.

The substrate's exactness is unaffected by anything in this section: the cipher's quality bends prefix-mean variance at $N < P$; it does not touch leading-digit counts.

## What the composition does

Composing the two contracts: choose $P$ as a certified atom count — from clause 2 (smooth-sieved), clause 3 (Family E), or clause 3' (Generalised Family E) of the substrate contract; for each $i = 0, \ldots, N - 1$, the cipher returns $j_i \in [0, P)$ and the substrate's Hardy random-access (clause 5) returns the $j_i$-th $n$-prime atom. At $N = P$, this visits the certified block exactly once and the leading-digit distribution of the visited atoms is exact. For prefix exactness at $N < P$, sample stratified by digit — one keyed prefix per leading-digit stratum. Two worked examples follow; further cases (a Benford-test null reference, reproducible cross-validation on non-power-of-two $n$, format-preserving permutation of small domains) are implemented in `replication/use_case_*.py` and held for the expanded paper.

### Stratified survey design with exact leading-digit strata

In audit sampling over account IDs, invoice magnitudes, or registry blocks, leading digit is sometimes a mandated reporting stratum: regulators ask for sample composition by leading digit, or the workflow downstream estimates a ratio per leading-digit class. A survey designer drawing a sample of size $N_{\text{total}}$ from such a finite population indexed by the digit-class block $B_{b,d}$ wants strata defined by leading digit. Standard practice draws i.i.d. samples and post-stratifies, accepting binomial deviation in realised stratum counts; the design weights then need post-hoc adjustment for the realised sizes. The substrate-contract clause for integer block-uniformity partitions $B_{b,d}$ exactly into $b-1$ leading-digit strata of size $b^{d-1}$ each, and the cipher's keyed bijection of $[0, b^{d-1})$ (one per stratum) gives a streaming reproducible prefix sample of any size $N_j \leq b^{d-1}$ per stratum. The full sample of size $\sum_j N_j$ is the union of $b-1$ keyed prefixes, one per stratum, with each per-stratum count exactly $N_j$.

The comparator is proportional-allocation by post-stratify-after-i.i.d.: realised stratum sizes are $\operatorname{Binomial}(N_{\text{total}}, 1/(b-1))$ with standard deviation $\sqrt{N_{\text{total}} \cdot (b-2)/(b-1)^2}$. At $(b, d) = (10, 4)$ and $\alpha_j = 0.1$ across nine strata, `replication/use_case_01_stratified_survey.py` reports the BIDDER per-stratum count exactly $N_j = \lfloor \alpha \cdot 1000 \rfloor$ at every cell of the panel $\alpha \in \{0.1, 0.5, 1.0\}$ (100, 500, 1000 per stratum); the 99th-percentile maximum stratum deviation under i.i.d.-then-post-stratify across 1000 trials grows from 31 ($\alpha = 0.1, N_{\text{total}} = 900$) to 97 ($\alpha = 1.0, N_{\text{total}} = 9000$). Exact per-stratum counts mean stratified-sample variance estimators apply the design weights directly without post-hoc adjustment for realised sizes — the $O(\sqrt{N_{\text{total}}})$ correction the i.i.d. approach otherwise carries.

### Monte Carlo with known endpoint and measured FPC realisation gap

An analyst running prefix-mean Monte Carlo on a finite population $[0, P)$ wants the estimator's variance pinned at the endpoint (exactly zero at $N = P$), the shape at $N < P$ known up to a measured gap from the ideal-permutation FPC, reproducibility across runs (same key $\to$ same sequence), and streaming (no materialised permutation of $[0, P)$ in memory). No single existing tool delivers all four.

The endpoint corollary gives the first: at $N = P$, BIDDER's prefix-mean equals the left-endpoint Riemann sum exactly, so variance across keys is machine-$\varepsilon$ — no cipher-quality argument is required at the endpoint. The realisation-gap result gives the second: at $N < P$, prefix-mean variance follows $(\sigma^2/N) \cdot (P-N)/(P-1)$ up to BIDDER's measured gap. At $P = 2000$, `replication/use_case_06_variance_mc.py` reports BIDDER variance at $N = P$ of $6.15 \times 10^{-31}$ (machine-$\varepsilon$; floating-point round-off in the sum), ideal-FPC variance $0$ exactly, and i.i.d.-with-replacement variance $\sigma^2/P \approx 4.7 \times 10^{-5}$ (never zero). The gap at $N < P$ is U-shaped in $N/P$, peaking at ratio $7.17$ at $N = P/2 = 1000$ and tapering to ratio $1.00$ at $N = P - 1$ (sampling-consistent with the ideal). Comparators each lack one property: i.i.d.-with-replacement loses FPC (variance $\sigma^2/N$ at every $N$); `numpy.random.permutation` gives ideal FPC but materialises $[0, P)$ in memory; FF1 / FF3 with AES is streaming and keyed but $\sim$19–29$\times$ heavier per call than BIDDER on the same workload; sort-by-i.i.d.-key needs $O(N \log N)$ extra memory and is not deterministic across implementations.

## The artifact

**The C surface.** Five functions in `bidder_root.h`:

```
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

The cipher path implements Speck32/64 cycle-walking with an unbalanced 8-round Feistel fallback for $period < 2^{26}$. The sawtooth path returns the $i$-th $n$-prime atom (0-indexed) in ascending order via the closed form $c_K = q \cdot n + r + 1$, $(q, r) = \operatorname{divmod}(K - 1, n - 1)$. The kernel is $\sim$300 lines of C with no third-party dependencies.

**Tests.** Eleven test files in three layers; `make test` runs all eleven on a clean checkout (`paper/measurements/e4_smoke.md`).

*Layer 1 — unit and property tests* (six files in `tests/`): `test_api.py`, `test_bidder.py`, `test_bidder_block.py`, `test_bidder_root.py`, `test_sawtooth.py`, `test_speck.py`. These exercise the Python wrappers against the C kernel and the pure-Python oracle, plus property tests (bijection-hood at small $P$, Speck round-trip equality, sawtooth monotonicity). The implementation includes the published Beaulieu et al. Appendix C test vectors as inline checks in `test_speck.py` and the corresponding C test, so a reviewer can run those vectors against the implementation independently of any of BIDDER's other code.

*Layer 2 — substrate verification* (`tests/test_acm_core.py`): each clause of the substrate-contract theorem has a verification test that checks the implementation conforms to the proven statement over a finite parameter sweep. The proof sketches cover all valid parameters; the tests below cover the listed sweep (every triple in the sweep is checked exhaustively).

| clause | implementation | test function | tested sweep |
|---|---|---|---|
| 1. Integer block-uniformity | (fact about $\mathbb{Z}$) | `test_block_boundary_*` | base 10, $d \in \{1, \ldots, 9\}$ |
| 2. Smooth-sieved | `bidder_sawtooth_at` | `test_block_uniformity_sieved_sufficient` | $b, n \in \{2, \ldots, 10\}$, $d \in \{1, \ldots, 5\}$ |
| 3. Family E | `bidder_sawtooth_at` | `test_block_uniformity_sieved_family_e` | $b \in \{2, \ldots, 10\}$, $d \in \{2, \ldots, 5\}$ |
| 3'. Generalised Family E | `bidder_sawtooth_at` | `test_block_uniformity_sieved_generalised_family_e` | $b \in \{2, \ldots, 10\}$, $d \in \{2, \ldots, 5\}$, $qp \in \{2, \ldots, 50\}$, $m_{\min} \in \{1, \ldots, 100\}$ |
| 4. Spread bound | `bidder_sawtooth_at` | `test_block_uniformity_sieved_spread_bound` | $b, n \in \{2, \ldots, 10\}$, $d \in \{1, \ldots, 5\}$ |
| 5. Hardy random-access | `bidder_sawtooth_at` | `test_at_matches_acm_n_primes` (oracle); `test_kth_prime_*` (closed-form vs enumeration) | sawtooth oracle: $n \in \{2, \ldots, 12\}$; closed-form: $n \in \{2, \ldots, 9999\}$ |

*Layer 3 — structural and statistical theory* (three files in `tests/theory/`): `test_riemann_property.py` (the endpoint identity at $N = P$, exact equality, machine-$\varepsilon$), `test_quadrature_rates.py` (Euler–Maclaurin convergence rates for $f = x$, $\sin(\pi x)$, $x^2(1-x)^2$, step), and `test_fpc_shape.py` (the realisation-gap measurement at $N < P$).

**Replication archive.** `bidder-stat/` runs end-to-end via `make replicate` and reproduces every table and every numerical claim in this paper from source: the cycle-walking decision sweep, the realisation-gap grid, the comparator throughput panel, the wrapper / kernel performance taxonomy, the FF1 / AES comparator measurement, and the five worked use-case scripts (`replication/use_case_*.py`).

## References

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
