# BIDDER: Exact Leading-Digit Sampling with Keyed Random Access

## Abstract

We present BIDDER, an exact leading-digit sampler with keyed random access for the $n$-prime atoms of the multiplicative monoid $M_n = \{1\} \cup n\mathbb{Z}_{>0}$ (multiples of $n$ not divisible by $n^2$). Two contracts compose: an exact counting theorem on arbitrary digit-class blocks $[b^{d-1}, b^d - 1]$ ($b^{d-1} \cdot (n-1)/n^2$ atoms per leading digit when $n^2 \mid b^{d-1}$; spread $\leq 2$ universally), and a keyed stateless cipher that is a bijection of $[0, P)$ for any $P \in [2, 2^{32} - 1]$ (Speck32/64 cycle-walking with an unbalanced Feistel fallback at small $P$). The substrate is asked only to be exact; the cipher only to be a reproducible bijection. Composing them yields streaming random-access to a deterministic anti-Benford reference, exact-fold partitioning of arbitrary populations, and Monte Carlo with a known endpoint and a measured FPC realisation gap. The implementation is $\sim 300$ lines of C.

## The question and the bijection

If we got rid of the odd numbers, what numbers would be odd?

The natural reading collapses on inspection. Remove the odd integers from $\mathbb{Z}_{>0}$ and you are left with $2\mathbb{Z}_{>0} = \{2, 4, 6, 8, 10, 12, \ldots\}$. Every element is divisible by 2 by construction, so nothing in this set is "odd" in the original sense. The question has to shift: not divisible by 2, but divisible *only* by 2 — not by $2^2$. The new "odd" elements of $2\mathbb{Z}_{>0}$ are $\{2, 6, 10, 14, 18, \ldots\} = 2\mathbb{Z} \setminus 4\mathbb{Z}$. These are the atoms of $2\mathbb{Z}_{>0} \cup \{1\}$ as a multiplicative monoid — indecomposable elements that cannot be written as a product of two non-unit elements. Within the monoid, they play the role primes play in $\mathbb{Z}$.

The generalisation is mechanical. For any $n \geq 2$, the *$n$-prime atoms* of $M_n = \{1\} \cup n\mathbb{Z}_{>0}$ are $n\mathbb{Z} \setminus n^2\mathbb{Z}$: multiples of $n$ not divisible by $n^2$. The substantive question is how these atoms distribute across digit-class blocks $B_{b,d} = [b^{d-1}, b^d - 1]$. The answer is a counting argument from positional notation. In the smooth regime where $n^2 \mid b^{d-1}$, each leading-digit strip of length $b^{d-1}$ starts at a multiple of $n^2$; subtracting multiples of $n^2$ from multiples of $n$ per strip gives exactly $b^{d-1} \cdot (n-1)/n^2$ atoms per leading digit, independent of strip. Outside the smooth regime, a universal spread bound of 2 holds, and a Family-E construction ($n \in [b^{d-1}, \lfloor (b^d-1)/(b-1) \rfloor]$) gives exact uniformity in a disjoint range. Hardy random-access — the closed form $c_K = q \cdot n + r + 1$ with $(q, r) = \operatorname{divmod}(K - 1, n - 1)$ — returns the $K$-th atom in $O(\log K + \log n)$-bit work, no enumeration. At $(b, n, d) = (10, 2, 4)$, for instance, the smooth condition holds ($4 \mid 1000$) and the count is exactly $250$ atoms per leading digit on $[1000, 9999]$.

To this exactly uniform sawtooth we attach a small-block cipher, a keyed bijection of $[0, P)$ where $P$ is an atom count certified by one of the substrate's exact-distribution regimes. The cipher reorders the $P$ atoms; the substrate keeps the reordering leading-digit-exact. The attachment is what BIDDER is and asks each side only what it can deliver: the substrate is exact, the cipher is a stateless reproducible bijection of $[0, P)$. Composing them yields, as a single object, four properties that no individual existing tool delivers together — streaming random-access (no full permutation materialised), keyed reproducibility across runs and machines, arbitrary period $P \in [2, 2^{32} - 1]$, and exact leading-digit counts on arbitrary $(b, d)$. The cipher backend is Speck32/64 in cycle-walking mode (Beaulieu et al. 2013; cycle-walking from Black & Rogaway 2002) for $P \geq 2^{26}$, with an unbalanced 8-round Feistel network for smaller $P$ (Luby & Rackoff 1988); the contract relied on throughout is bijection-hood, not PRP quality. The implementation is $\sim 300$ lines of C with no third-party dependencies; `make replicate` reproduces every table in this paper from source.

Four adjacent lines of work each do part of what BIDDER does. *PRNG-from-normal-numbers* (Bailey & Crandall 2002; Bailey 2004) gives random access to the digits of a fixed Stoneham-class constant via BBP-style extraction; BIDDER gives keyed random access where the key selects among permutations rather than indexing into a single fixed digit stream. *Quasi-Monte Carlo* (Halton 1960; Sobol' 1967; Niederreiter 1992; Owen 1995; Dick & Pillichshammer 2010) gives bounded star discrepancy $O((\log N)^d / N)$ asymptotically; BIDDER gives endpoint-exact at finite $N$ with FPC-shaped interior at $N < P$. *Exact ranged-integer generation* (Lemire 2019; Saad et al. 2020) gives unbiased i.i.d. samplers over $[0, s)$; BIDDER is a bijection that visits each value exactly once. *Format-preserving encryption* (NIST SP 800-38G — FF1 and FF3-1 with AES) supplies keyed bijections of arbitrary domains sized for cryptographic-strength PRP, requires an AES library, and accepts AES-per-call cost; BIDDER asks of its cipher only bijection-hood, with no library dependency and $\sim 19$–$29\times$ lower per-call cost on the same workload. None of the four sits at all four BIDDER corners simultaneously.

The next sections prove the substrate's distribution and indexing results, describe the cipher and how it attaches to the substrate, walk three worked examples, place BIDDER against prior work, and present the artifact and tests that back it.

## The substrate

The substrate is a bundle of distribution and indexing results for the $n$-prime atoms of $M_n$ on digit-class blocks. Definitions 3.1–3.3 fix the objects; Theorem 3.4 fixes the integer baseline; Theorems 3.5–3.7 give three exact-distribution regimes for $n$-prime atoms; Theorem 3.9 gives the universal spread bound when none of those regimes applies; Lemma 3.10 gives the random-access closed form; Remark 3.11 records an open observation. Throughout, fix $(b, n, d)$ with $b \geq 2$, $d \geq 1$, $n \geq 2$.

**Definition 3.1 ($n$-prime atoms).** The multiplicative monoid $M_n$ is $\{1\} \cup n\mathbb{Z}_{>0}$. The *$n$-prime atoms* of $M_n$ are $n\mathbb{Z} \setminus n^2\mathbb{Z}$: multiples of $n$ not divisible by $n^2$.

**Definition 3.2 (Digit-class block).** The *digit-class block* is $B_{b,d} = [b^{d-1}, b^d - 1]$.

**Definition 3.3 (Leading-digit strip).** For $k \in \{1, \ldots, b-1\}$, the $k$-th *leading-digit strip* of $B_{b,d}$ is $S_k = [k \cdot b^{d-1}, (k+1) \cdot b^{d-1} - 1]$. The strips partition $B_{b,d}$, and an integer in $S_k$ has leading base-$b$ digit $k$.

**Theorem 3.4 (Integer block-uniformity).** The integers in $B_{b,d}$ have leading-digit counts exactly $b^{d-1}$ per digit $j \in \{1, \ldots, b-1\}$.

*Proof.* An integer in $B_{b,d} = [b^{d-1}, b^d - 1]$ has a unique base-$b$ representation $d_1 d_2 \ldots d_d$ with leading digit $d_1 \in \{1, \ldots, b-1\}$ and $d_2, \ldots, d_d \in \{0, \ldots, b-1\}$. Fixing $d_1$ leaves $d - 1$ positions free over $b$ values, so each leading digit accounts for exactly $b^{d-1}$ integers.

**Theorem 3.5 (Smooth-sieved uniformity).** If $n^2 \mid b^{d-1}$, the $n$-prime atoms of $M_n$ lying in $B_{b,d}$ have leading-digit counts exactly $b^{d-1} \cdot (n-1)/n^2$ per digit.

*Proof.* Suppose $n^2 \mid b^{d-1}$. The $k$-th leading-digit strip $S_k = [k \cdot b^{d-1}, (k+1) \cdot b^{d-1} - 1]$ has length $b^{d-1}$, and its left endpoint $k \cdot b^{d-1}$ is a multiple of $n^2$ (and hence of $n$). For any interval $[a, a + W)$ with $n \mid a$ and $n \mid W$, the count of multiples of $n$ is exactly $W/n$ (the multiples are $a, a + n, \ldots, a + W - n$). So $S_k$ contains exactly $b^{d-1}/n$ multiples of $n$ and exactly $b^{d-1}/n^2$ multiples of $n^2$. Subtracting, the $n$-prime atom count per strip is $b^{d-1}/n - b^{d-1}/n^2 = b^{d-1}(n-1)/n^2$, independent of $k$.

**Theorem 3.6 (Family E).** For $d \geq 2$ and $n \in [b^{d-1}, \lfloor (b^d-1)/(b-1) \rfloor]$, the $n$-prime atoms in $B_{b,d}$ are exactly $\{n, 2n, \ldots, (b-1)n\}$ — one per leading digit. (Disjoint from Theorem 3.5 in this regime.)

*Proof.* Three steps. *(In-block.)* For $k \in \{1, \ldots, b-1\}$, $k \cdot n \geq n \geq b^{d-1}$ and $k \cdot n \leq (b-1) \cdot n \leq b^d - 1$ (the upper bound follows from $n \leq \lfloor (b^d - 1)/(b - 1) \rfloor$); so each $k \cdot n$ lies in $B_{b,d}$. Conversely, no other multiple of $n$ does: $b \cdot n > b \cdot b^{d-1} = b^d > b^d - 1$. *(Leading digit.)* The lower bound $k \cdot b^{d-1} \leq k \cdot n$ follows from $n \geq b^{d-1}$. For the upper bound, the hypothesis $n \leq \lfloor (b^d - 1)/(b - 1) \rfloor$ gives $n < b \cdot b^{d-1}/(b - 1)$. The inequality $(k+1)/k \geq b/(b-1)$ holds for $k \in \{1, \ldots, b-1\}$ — cross-multiplying gives $(k+1)(b-1) \geq kb$, i.e., $b - 1 \geq k$, which holds — so $n < ((k+1)/k) \cdot b^{d-1}$ and hence $k \cdot n < (k+1) \cdot b^{d-1}$. Thus $k \cdot n$ has leading digit exactly $k$. *(Sieve removes nothing.)* For $d \geq 2$, $n^2 \geq (b^{d-1})^2 = b^{2d-2} \geq b^d$ (the last step holds for $d \geq 2$), so $n^2 > b^d - 1$ and no multiple of $n^2$ lies in $B_{b,d}$. The atoms $\{n, 2n, \ldots, (b-1)n\}$ are therefore $n$-primes (multiples of $n$ not of $n^2$) and exhaust the $n$-prime atoms in the block.

**Theorem 3.7 (Generalised Family E).** Let $W = b^{d-1}$. For integers $(q', m_{\min})$ with $m_{\min} \geq 1$, $q' \geq 1$, set $m_{\max} := m_{\min} + q'(b-1) - 1$. Suppose

$$
\begin{aligned}
(m_{\min} - 1) \cdot n &< W \leq m_{\min} \cdot n, \\
m_{\max} \cdot n &\leq bW - 1 < (m_{\max} + 1) \cdot n,
\end{aligned}
$$

so that $[m_{\min}, m_{\max}]$ is exactly the integer multiplier range whose product with $n$ lands in $B_{b,d}$. Suppose further that for each $k \in [m_{\min}, m_{\max}]$ the leading digit of $kn$ equals $\lceil (k - m_{\min} + 1)/q' \rceil$. Then the multiples of $n$ in $B_{b,d}$ distribute as exactly $q'$ per leading digit. If additionally the multiples of $n^2$ in $B_{b,d}$ distribute uniformly across strips with $\delta$ per strip, the $n$-prime atoms distribute as exactly $q' - \delta$ per leading digit.

*Proof.* The four bracketing hypotheses say exactly that $[m_{\min}, m_{\max}]$ is the set of multipliers $k$ for which $k \cdot n \in B_{b,d}$: $(m_{\min} - 1) \cdot n < W \leq m_{\min} \cdot n$ identifies $m_{\min}$ as the smallest such $k$ (equivalently, $m_{\min} = \lceil W/n \rceil$), and $m_{\max} \cdot n \leq bW - 1 < (m_{\max} + 1) \cdot n$ identifies $m_{\max}$ as the largest (equivalently, $m_{\max} = \lfloor (bW - 1)/n \rfloor$). The relation $m_{\max} = m_{\min} + q'(b-1) - 1$ partitions $[m_{\min}, m_{\max}]$ into $b - 1$ consecutive blocks of length $q'$: the $\ell$-th block is $\{m_{\min} + (\ell - 1)q', \ldots, m_{\min} + \ell q' - 1\}$ for $\ell \in \{1, \ldots, b-1\}$. By the leading-digit hypothesis, $k$ in the $\ell$-th block satisfies $\lceil (k - m_{\min} + 1)/q' \rceil = \ell$, so $kn$ has leading digit $\ell$ and lies in strip $S_\ell$. Therefore each strip $S_\ell$ contains exactly the $q'$ products $kn$ for $k$ in the $\ell$-th block, giving $q'$ multiples of $n$ per strip. The atom count subtracts the per-strip multiples of $n^2$; if these distribute uniformly with $\delta$ per strip, the per-strip $n$-prime count is $q' - \delta$, independent of $\ell$.

**Corollary 3.8 (Family E as special case).** Theorem 3.6 follows from Theorem 3.7 by setting $q' = 1$, $m_{\min} = \lceil W/n \rceil$, $\delta = 0$.

**Theorem 3.9 (Universal spread bound).** Per-leading-digit $n$-prime counts in $B_{b,d}$ differ by at most 2.

*Proof.* The same divmod argument as Theorem 3.5, applied to generic intervals $[L, L + W)$ with $W = b^{d-1}$ and $L$ not necessarily a multiple of $n$ or $n^2$. For any such interval, the count of multiples of $n$ is $\lfloor (L + W - 1)/n \rfloor - \lfloor (L - 1)/n \rfloor$, which equals either $\lfloor W/n \rfloor$ or $\lfloor W/n \rfloor + 1$ depending on $L \bmod n$. Each leading-digit strip $S_k$ is such an interval of length $W$, so its multiples-of-$n$ count lies in a two-element set $\{\lfloor W/n \rfloor, \lfloor W/n \rfloor + 1\}$; the same argument with $n^2$ gives the multiples-of-$n^2$ count in an analogous two-element set. The per-strip $n$-prime count is the difference of these two values; values from two two-element sets differ across strips by at most $1 + 1 = 2$.

**Lemma 3.10 (Hardy random-access).** For $K \geq 1$, the $K$-th $n$-prime atom of $M_n$ is $p_K = n \cdot c_K$ with $c_K = q \cdot n + r + 1$ where $(q, r) = \operatorname{divmod}(K - 1, n - 1)$. Computing $p_K$ from $K$ is one divmod and arithmetic on $O(\log K + \log n)$-bit integers; no enumeration.

*Proof.* The $n$-prime atoms of $M_n$ are the multiples of $n$ not divisible by $n^2$, i.e., $\{cn : c \in \mathbb{Z}_{>0}, n \nmid c\}$. In each block of $n$ consecutive positive integers — $\{1, \ldots, n\}, \{n+1, \ldots, 2n\}, \ldots$ — exactly one (the multiple of $n$) is excluded, leaving $n - 1$ valid multipliers per block. So the $K$-th valid multiplier $c_K$ sits in block $q + 1$ at position $r + 1$ within the block, where $(q, r) = \operatorname{divmod}(K - 1, n - 1)$. Block $q + 1$ starts at $qn + 1$, so position $r + 1$ within it is $c_K = qn + r + 1$ (and $r + 1 \leq n - 1 < n$, so $c_K$ is not itself a multiple of $n$, as required). Therefore $p_K = n \cdot c_K = n(qn + r + 1)$. The arithmetic is one divmod and constant work on $O(\log K + \log n)$-bit integers.

**Remark 3.11 ($n^2$-cancellation residual).** Across the swept range $b = 10$, $n \in [2, 200]$, $d \in [1, 7]$, 27 cells exhibit per-leading-digit spread $= 0$ outside the regimes of Theorems 3.5, 3.6, and 3.7. The mechanism is identified — *Beatty pattern-alignment*, where the per-strip excess multiples of $n$ match the per-strip excess multiples of $n^2$ bit-for-bit, exactly cancelling in the atom count — and the alignment condition is verified $27/27$ in the swept range.

The closed form for *which* integer triples $(b, n, d)$ trigger the alignment is open; characterising the trigger set is left as an open question on this paper. Theorem 3.9's universal spread $\leq 2$ covers these cells; the spread $= 0$ observation is sharper than the contract guarantees, and is reported here as such.

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

Composing the two contracts: choose $P$ as a certified atom count — from Theorem 3.5 (smooth-sieved), Theorem 3.6 (Family E), or Theorem 3.7 (Generalised Family E); for each $i = 0, \ldots, N - 1$, the cipher returns $j_i \in [0, P)$ and Lemma 3.10 with $K = j_i + 1$ returns the $(j_i + 1)$-th $n$-prime atom. At $N = P$, this visits the certified block exactly once and the leading-digit distribution of the visited atoms is exact. For prefix exactness at $N < P$, sample stratified by digit — one keyed prefix per leading-digit stratum. Three worked examples follow. 

### Benford-test null reference with exact leading-digit counts

A practitioner running a leading-digit conformity test — forensic accounting, election forensics, dataset-integrity audit — needs the null distribution of the test statistic at finite $N$. Standard practice is Monte Carlo from the assumed null. For the uniform-leading-digit alternative (the "anti-Benford" reference against which Benford-conformity tests are calibrated), i.i.d.-uniform sampling on $B_{b,d}$ gives leading-digit counts distributed as $\operatorname{Multinomial}(N, 1/(b-1), \ldots, 1/(b-1))$ on every replicate, so the empirical critical-value estimate carries Multinomial sampling noise per digit on top of the test statistic's own variability. Theorem 3.4 (at the integer level) and Theorem 3.5 (at the sieved $n$-prime level when $n^2 \mid b^{d-1}$) yield references whose per-digit counts are exact by construction; Pearson chi-squared on the leading-digit counts is exactly $0$, structurally rather than statistically. Combined with Lemma 3.10 for indexing and the cipher for keyed reordering, the reference is streaming, keyed, and reproducible across runs and machines.

The contrast is sharp at every cell. `replication/use_case_02_benford_null.py` reports BIDDER's Pearson chi-squared as exactly $0.0000$ on a five-cell panel — integer-level $(b, d) \in \{(10, 3), (10, 4), (10, 5), (8, 5), (16, 4)\}$ and sieved $n$-prime $(b, n, d) \in \{(10, 2, 3), (10, 2, 4), (10, 2, 5), (8, 2, 5), (16, 2, 4)\}$. At $(b, n, d) = (10, 2, 4)$ the substrate yields $2{,}250$ $n$-prime atoms in $[1000, 9999]$ with exactly $250$ per leading digit (the smooth-regime count $b^{d-1}(n-1)/n^2$). The i.i.d.-uniform comparator on the same blocks across $1000$ trials per cell reports chi-squared distributed as $\chi^2(b-2)$: empirical means $7.83$, $8.07$, $7.98$ at $b = 10$ (theoretical mean $b - 2 = 8$), $6.07$ at $b = 8$ (theoretical $6$), $14.00$ at $b = 16$ (theoretical $14$); standard deviations track $\sqrt{2(b-2)}$. A Benford-detector calibrated against BIDDER reflects only the detector's own properties; calibrated against an i.i.d. reference, it carries the Multinomial noise of every replicate as critical-value uncertainty. BIDDER is the uniform-leading-digit null; sampling from Benford's distribution itself remains the correct reference when conformity, not anti-conformity, is the alternative.

### Stratified survey design with exact leading-digit strata

In audit sampling over account IDs, invoice magnitudes, or registry blocks, leading digit is sometimes a mandated reporting stratum: regulators ask for sample composition by leading digit, or the workflow downstream estimates a ratio per leading-digit class. A survey designer drawing a sample of size $N_{\text{total}}$ from such a finite population indexed by the digit-class block $B_{b,d}$ wants strata defined by leading digit. Standard practice draws i.i.d. samples and post-stratifies, accepting binomial deviation in realised stratum counts; the design weights then need post-hoc adjustment for the realised sizes. Theorem 3.4 partitions $B_{b,d}$ exactly into $b-1$ leading-digit strata of size $b^{d-1}$ each, and the cipher's keyed bijection of $[0, b^{d-1})$ (one per stratum) gives a streaming reproducible prefix sample of any size $N_j \leq b^{d-1}$ per stratum. The full sample of size $\sum_j N_j$ is the union of $b-1$ keyed prefixes, one per stratum, with each per-stratum count exactly $N_j$.

The comparator is proportional-allocation by post-stratify-after-i.i.d.: realised stratum sizes are $\operatorname{Binomial}(N_{\text{total}}, 1/(b-1))$ with standard deviation $\sqrt{N_{\text{total}} \cdot (b-2)/(b-1)^2}$. At $(b, d) = (10, 4)$ and $\alpha_j = 0.1$ across nine strata, `replication/use_case_01_stratified_survey.py` reports the BIDDER per-stratum count exactly $N_j = \lfloor \alpha \cdot 1000 \rfloor$ at every cell of the panel $\alpha \in \{0.1, 0.5, 1.0\}$ (100, 500, 1000 per stratum); the 99th-percentile maximum stratum deviation under i.i.d.-then-post-stratify across 1000 trials grows from 31 ($\alpha = 0.1, N_{\text{total}} = 900$) to 97 ($\alpha = 1.0, N_{\text{total}} = 9000$). Exact per-stratum counts mean stratified-sample variance estimators apply the design weights directly without post-hoc adjustment for realised sizes — the $O(\sqrt{N_{\text{total}}})$ correction the i.i.d. approach otherwise carries.

### Monte Carlo with known endpoint and measured FPC realisation gap

An analyst running prefix-mean Monte Carlo on a finite population $[0, P)$ wants the estimator's variance pinned at the endpoint (exactly zero at $N = P$), the shape at $N < P$ known up to a measured gap from the ideal-permutation FPC, reproducibility across runs (same key $\to$ same sequence), and streaming (no materialised permutation of $[0, P)$ in memory). No single existing tool delivers all four.

The endpoint corollary gives the first: at $N = P$, BIDDER's prefix-mean equals the left-endpoint Riemann sum exactly, so variance across keys is machine-$\varepsilon$ — no cipher-quality argument is required at the endpoint. The realisation-gap result gives the second: at $N < P$, prefix-mean variance follows $(\sigma^2/N) \cdot (P-N)/(P-1)$ up to BIDDER's measured gap. At $P = 2000$, `replication/use_case_06_variance_mc.py` reports BIDDER variance at $N = P$ of $6.15 \times 10^{-31}$ (machine-$\varepsilon$; floating-point round-off in the sum), ideal-FPC variance $0$ exactly, and i.i.d.-with-replacement variance $\sigma^2/P \approx 4.7 \times 10^{-5}$ (never zero). The gap at $N < P$ is U-shaped in $N/P$, peaking at ratio $7.17$ at $N = P/2 = 1000$ and tapering to ratio $1.00$ at $N = P - 1$ (sampling-consistent with the ideal). Comparators each lack one property: i.i.d.-with-replacement loses FPC (variance $\sigma^2/N$ at every $N$); `numpy.random.permutation` gives ideal FPC but materialises $[0, P)$ in memory; FF1 / FF3 with AES is streaming and keyed but $\sim 19$–$29\times$ heavier per call than BIDDER on the same workload; sort-by-i.i.d.-key needs $O(N \log N)$ extra memory and is not deterministic across implementations.

## Related work

We examine two lines of work; each is a precise neighbour to part of what BIDDER does. Bailey–Crandall (PRNG-from-normal-numbers) and BIDDER's substrate emerge from the same kind of process: a number-theoretic structure exposed through a closed-form, random-access extraction that needs no enumeration of the prefix. Their construction is the closest available structural analogue to ours, and the comparison is what most clearly places BIDDER's substrate mathematically. Sobol' and the broader quasi-Monte Carlo literature are the textbook home for "deterministic sequences more uniform than i.i.d. samples" — exactly the effect BIDDER pursues, in the discrete-block-with-leading-digit-structure setting where QMC's continuous-cube tools don't apply natively.

The PRNG-from-normal-numbers construction (Bailey & Crandall 2002; Bailey 2004) builds a pseudorandom number generator from the digits of Stoneham-class normal numbers $\alpha_{b,c} = \sum_{n=0}^{\infty} 1/(c^n b^{c^n})$. The $K$-th base-$b$ digit of $\alpha_{b,c}$ can be extracted via BBP-style formulas in $O(\log K)$ work, without computing the prefix. The result is a deterministic, reproducible, random-access digit stream whose equidistribution is guaranteed asymptotically — the underlying Stoneham constant is provably normal in base $b$. The kinship with BIDDER is real: both deliver random-access, deterministic, low-per-access-cost sequences with mathematical backing on their distribution. A reader meeting Bailey–Crandall and BIDDER side by side could reasonably ask why BIDDER is more than a re-engineering of the Stoneham construction.

The differences are structural, not engineering. **Single stream vs. keyed family.** Bailey–Crandall produces one sequence per $(b, c)$ Stoneham pair; to get a different sequence, you change the constant. BIDDER's cipher is keyed: the substrate certifies a single block of $P$ atoms, and the cipher key selects among $2^{|\mathit{key}|}$ permutations of that block. **Asymptotic equidistribution vs. exact finite-block counts.** Bailey–Crandall's distributional guarantee is asymptotic — the digits equidistribute in the limit, with finite-$N$ discrepancy that approaches zero. BIDDER's substrate (Theorems 3.5–3.7) gives exact per-leading-digit counts at every finite $N$ matching the regime: at $(b, n, d) = (10, 2, 4)$ every leading digit gets exactly $250$ atoms in $[1000, 9999]$, not "approaches $250$ as $N$ grows." **Digit stream vs. finite-set bijection.** Bailey–Crandall outputs a digit stream — an infinite sequence over $\{0, \ldots, b-1\}$. BIDDER outputs a bijection of a finite set $[0, P)$, with every value visited exactly once at $N = P$. **Provable-normality theorem vs. counting argument.** Bailey–Crandall's correctness rests on the deep number-theoretic result that the Stoneham constant is normal in base $b$. BIDDER's substrate is a counting theorem: divmod arithmetic on multiples of $n$ and $n^2$ in $B_{b,d}$. The two tools answer different questions on different mathematical foundations.

Sobol' and the broader quasi-Monte Carlo literature (Halton 1960; Sobol' 1967; Niederreiter 1992; Owen 1995; Dick & Pillichshammer 2010) construct low-discrepancy sequences in $[0, 1]^d$ with star discrepancy $O((\log N)^d / N)$ asymptotically — sequences engineered to be more uniform than i.i.d. samples. Two differences place BIDDER. **Low-discrepancy vs. exact distribution.** QMC's $O((\log N)^d / N)$ is an asymptotic discrepancy bound; the sequences are approximately uniform, with discrepancy that shrinks as $N$ grows. BIDDER's substrate (Theorems 3.5–3.7) gives exact per-leading-digit counts at finite $N$ in the certified regimes, and the cipher's endpoint corollary gives prefix-mean equal to the left-endpoint Riemann sum exactly at $N = P$ — bijection-hood alone, no discrepancy bound needed. **Continuous cube vs. discrete blocks.** QMC operates in $[0, 1]^d$; BIDDER operates over discrete integer blocks $B_{b,d} = [b^{d-1}, b^d - 1]$ with leading-digit structure. The objects are different in kind: QMC produces low-discrepancy point sets in continuous high-dimensional spaces, where the leading-digit structure has no analogue and exact-uniform counts on integer blocks aren't a meaningful target.

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

The cipher path implements Speck32/64 cycle-walking with an unbalanced 8-round Feistel fallback for $period < 2^{26}$. The sawtooth path returns the $i$-th $n$-prime atom (0-indexed) in ascending order via the closed form $c_K = q \cdot n + r + 1$, $(q, r) = \operatorname{divmod}(K - 1, n - 1)$. The kernel is $\sim 300$ lines of C with no third-party dependencies.

**Replication archive.** `bidder-stat/` runs end-to-end via `make replicate` and reproduces every table and every numerical claim in this paper from source: the cycle-walking decision sweep, the realisation-gap grid, the comparator throughput panel, the wrapper / kernel performance taxonomy, the FF1 / AES comparator measurement, and the worked use-case scripts (`replication/use_case_*.py`).

## Tests

Eleven test files in `tests/` exercise three concerns: tests of the theory, tests of the artifact, and tests of the theory via the artifact. `make test` runs the lot on a clean checkout (`paper/measurements/e4_smoke.md`).

### Tests of the theory

Three files in `tests/theory/`: `test_riemann_property.py` (the endpoint identity at $N = P$, exact equality, machine-$\varepsilon$), `test_quadrature_rates.py` (Euler–Maclaurin convergence rates for $f = x$, $\sin(\pi x)$, $x^2(1-x)^2$, step), and `test_fpc_shape.py` (the realisation-gap measurement at $N < P$). These check the structural and statistical claims about the cipher independently of any specific BIDDER backend.

### Tests of the artifact

Six files in `tests/`: `test_api.py`, `test_bidder.py`, `test_bidder_block.py`, `test_bidder_root.py`, `test_sawtooth.py`, `test_speck.py`. These exercise the Python wrappers against the C kernel and the pure-Python oracle, plus property tests (bijection-hood at small $P$, Speck round-trip equality, sawtooth monotonicity). The implementation includes the published Beaulieu et al. Appendix C test vectors as inline checks in `test_speck.py` and the corresponding C test, so a reviewer can run those vectors against the implementation independently of any of BIDDER's other code.

### Tests of the theory via the artifact

`tests/test_acm_core.py`: each substrate result has a verification test that runs the implementation through `bidder_sawtooth_at` and confirms the output matches the proven statement over a finite parameter sweep. The substrate proofs cover all valid parameters; the tests below cover the listed sweep (every triple in the sweep is checked exhaustively).

| result | implementation | test function | tested sweep |
|---|---|---|---|
| Theorem 3.4 (Integer block-uniformity) | (fact about $\mathbb{Z}$) | `test_block_boundary_*` | base 10, $d \in \{1, \ldots, 9\}$ |
| Theorem 3.5 (Smooth-sieved) | `bidder_sawtooth_at` | `test_block_uniformity_sieved_sufficient` | $b, n \in \{2, \ldots, 10\}$, $d \in \{1, \ldots, 5\}$ |
| Theorem 3.6 (Family E) | `bidder_sawtooth_at` | `test_block_uniformity_sieved_family_e` | $b \in \{2, \ldots, 10\}$, $d \in \{2, \ldots, 5\}$ |
| Theorem 3.7 (Generalised Family E) | `bidder_sawtooth_at` | `test_block_uniformity_sieved_generalised_family_e` | $b \in \{2, \ldots, 10\}$, $d \in \{2, \ldots, 5\}$, $q' \in \{2, \ldots, 50\}$, $m_{\min} \in \{1, \ldots, 100\}$ |
| Theorem 3.9 (Spread bound) | `bidder_sawtooth_at` | `test_block_uniformity_sieved_spread_bound` | $b, n \in \{2, \ldots, 10\}$, $d \in \{1, \ldots, 5\}$ |
| Lemma 3.10 (Hardy random-access) | `bidder_sawtooth_at` | `test_at_matches_acm_n_primes` (oracle); `test_kth_prime_*` (closed-form vs enumeration) | sawtooth oracle: $n \in \{2, \ldots, 12\}$; closed-form: $n \in \{2, \ldots, 9999\}$ |

## Conclusion

BIDDER is a substrate (exact leading-digit counts of $n$-prime atoms on digit-class blocks; Theorems 3.4–3.7) attached to a stateless keyed cipher (a bijection of $[0, P)$ for any $P \in [2, 2^{32} - 1]$) via a closed-form random-access (Lemma 3.10). The substrate's exactness is structural, the cipher's PRP quality is measured, and the $n^2$-cancellation trigger set (Remark 3.11) is the open question this paper leaves on the table.
