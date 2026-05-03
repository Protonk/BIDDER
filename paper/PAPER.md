# BIDDER: Exact Leading-Digit Sampling with Keyed Random Access

## Abstract

We present BIDDER, a small software package for reproducible keyed random access to finite integer sets with certified leading-digit structure. The substrate is a counting result for the multiples of $n$ not divisible by $n^2$ on digit-class blocks: several regimes give exact per-leading-digit counts (notably $b^{d-1}(n-1)/n^2$ when $n^2 \mid b^{d-1}$), a universal spread bound of 2 holds outside them, and the $K$-th element has a closed form. The cipher is a keyed stateless bijection of $[0, P)$, implemented as Speck32/64 in cycle-walking mode for $P \geq 2^{26}$ with an unbalanced 16-round Feistel fallback (build-time configurable) for smaller $P$. The sampling layer applies the cipher to certified blocks or per-stratum prefixes, supplying uniform-leading-digit controls, exact stratum sizes, and finite-population Monte Carlo with an exact endpoint identity; sub-endpoint variance is measured and backend-dependent. The software exposes two addressable sequence objects, `cipher(period, key)` and `sawtooth(n, count)`, backed by a small dependency-free C kernel and accompanied by a replication archive.

## Overview

If you take away the odd numbers, which of the remaining numbers are odd? In the ordinary integers the answer is "none," but multiplicatively the even numbers have their own atoms. Work inside $M_2 = \{1\} \cup 2\mathbb{Z}_{>0}$: every product of two non-units is divisible by 4, so the even numbers not divisible by 4, $\{2,6,10,14,\ldots\}$, cannot be decomposed further inside $M_2$. They are even in $\mathbb{Z}$, but they are the residual "odd" elements of the even-number monoid.

The same picture extends to any $n \geq 2$: the multiples of $n$ not divisible by $n^2$ — write $A_n = n\mathbb{Z}_{>0} \setminus n^2\mathbb{Z}_{>0}$ — are exactly the elements of $\{1\} \cup n\mathbb{Z}_{>0}$ that cannot be decomposed multiplicatively. The analogy motivates the object; the proofs use only divmod arithmetic on $A_n$, so we work with the set directly from here on.

The substantive question is how the elements of $A_n$ distribute across digit-class blocks $B_{b,d} = [b^{d-1}, b^d - 1]$. The answer is a counting argument from positional notation. In the block-aligned regime where $n^2 \mid b^{d-1}$, each leading-digit strip of length $b^{d-1}$ starts at a multiple of $n^2$; subtracting multiples of $n^2$ from multiples of $n$ per strip gives exactly $b^{d-1} \cdot (n-1)/n^2$ elements per leading digit, independent of strip. Outside the block-aligned regime, a universal spread bound of 2 holds, and a Family-E construction ($n \in [b^{d-1}, \lfloor (b^d-1)/(b-1) \rfloor]$) gives exact uniformity in a disjoint range. Closed-form indexing — $c_K = q \cdot n + r + 1$ with $(q, r) = \operatorname{divmod}(K - 1, n - 1)$ — returns the $K$-th element of $A_n$ in $O(\log K + \log n)$-bit work, no enumeration. At $(b, n, d) = (10, 2, 4)$, for instance, the block-alignment condition holds ($4 \mid 1000$) and the count is exactly $250$ elements per leading digit on $[1000, 9999]$.

To this exactly uniform finite block we attach a keyed finite-domain permutation, a bijection of $[0, P)$ where $P$ is a count certified by one of the substrate's exact-distribution regimes. The substrate supplies a leading-digit-balanced multiset; the cipher supplies a keyed reorder. Composition preserves the balance trivially — any bijection of a finite set preserves its multiset — so the leading-digit exactness at $N = P$ is inherited from the substrate alone. The construction is three contracts, used separately.

| layer | contract | exact claim | limitation |
|---|---|---|---|
| substrate | Count and index elements of $A_n$ in digit-class blocks | closed-form $K$-th element in Lemma 3.4; exact per-leading-digit counts in Theorems 3.6--3.7 and Criterion 3.8; spread $\leq 2$ universally | exact uniformity only in certified regimes; Appendix A audits spread-zero boundary cases outside the implementation contract |
| cipher | Keyed stateless bijection of $[0, P)$ | every value in $[0, P)$ appears exactly once; same key and period reproduce the same order | bijection-hood is the relied-on contract; sub-endpoint mixing is measured, not proved |
| sampling | Apply the cipher to certified blocks or per-stratum prefixes | exact endpoint for whole-block mode; exact stratum sizes in stratified mode | arbitrary prefixes are not automatically leading-digit-exact; interior Monte Carlo variance has a backend-dependent measured gap |

Operationally, BIDDER targets the intersection summarized above: streaming random-access, keyed reproducibility across runs and machines, arbitrary period $P \in [2, 2^{32} - 1]$, and no materialized permutation; exact leading-digit claims come from certified blocks or stratified prefixes. The cipher backend is Speck32/64 in cycle-walking mode (Beaulieu et al. 2013; cycle-walking from Black & Rogaway 2002) for $P \geq 2^{26}$, with an unbalanced 16-round Feistel network for smaller $P$ (Luby & Rackoff 1988; round count configurable at build time); the contract relied on throughout is bijection-hood, not PRP quality. `make replicate` reproduces every table in this paper from source.

Existing tools occupy adjacent corners: random-access digit streams, low-discrepancy deterministic designs, unbiased ranged-integer samplers, and standards-track format-preserving encryption. BIDDER's target is their intersection for a narrower finite-population problem: exact leading-digit counts, keyed stateless ordering, arbitrary period up to $2^{32}-1$, and no materialized permutation. The detailed comparison is deferred to Related work so the construction can be stated once here.

The next sections prove the substrate's distribution and indexing results, describe the cipher and how it attaches to the substrate, walk three worked examples, present the software interface, place BIDDER against prior work, and describe the validation archive that backs it.

## The substrate

The substrate gives indexing and distribution results for two finite-integer populations on digit-class blocks. The integer baseline (Theorem 3.5) is what most of the use cases below actually consume. The sparser sieved population $A_n$ — addressable via Lemma 3.4 in $O(\log K + \log n)$-bit work, distributed by Theorems 3.6–3.7 and Criterion 3.8, bounded by Theorem 3.10 and tightened in the half-aligned regime by Corollary 3.11 — is the natural extension for workflows that want a uniform-leading-digit reference at lower density than full integers, or that come from the broader multiplicative-monoid setting motivated in the overview. Appendix A audits uncertified spread-zero boundary cases: a structural decomposition into three constant-difference cases when $n^2 > W$ (Theorem A.1), a Beatty-pair reduction of one of them (Lemma A.2), and a base-10 conjecture for that case verified at $n \leq 5000$, $d \leq 14$ (A.3). Those cases characterize where spread = 0 holds outside the certified regimes, but they are not part of the implementation contract. Throughout, fix $(b, n, d)$ with $b \geq 2$, $d \geq 1$, $n \geq 2$.

**Definition 3.1 ($A_n$).** Let $A_n = n\mathbb{Z}_{>0} \setminus n^2\mathbb{Z}_{>0}$: the positive multiples of $n$ not divisible by $n^2$.

**Definition 3.2 (Digit-class block).** The *digit-class block* is $B_{b,d} = [b^{d-1}, b^d - 1]$.

**Definition 3.3 (Leading-digit strip).** For $k \in \{1, \ldots, b-1\}$, the $k$-th *leading-digit strip* of $B_{b,d}$ is $S_k = [k \cdot b^{d-1}, (k+1) \cdot b^{d-1} - 1]$. The strips partition $B_{b,d}$, and an integer in $S_k$ has leading base-$b$ digit $k$.

**Lemma 3.4 (Closed-form indexing).** For $K \geq 1$, the $K$-th element of $A_n$ in ascending order is $p_K = n \cdot c_K$ with $c_K = q \cdot n + r + 1$ where $(q, r) = \operatorname{divmod}(K - 1, n - 1)$. Computing $p_K$ from $K$ is one divmod and arithmetic on $O(\log K + \log n)$-bit integers; no enumeration.

*Proof.* Write $A_n = \{cn : c \in \mathbb{Z}_{>0}, n \nmid c\}$. In each block of $n$ consecutive positive integers — $\{1, \ldots, n\}, \{n+1, \ldots, 2n\}, \ldots$ — exactly one (the multiple of $n$) is excluded, leaving $n - 1$ valid multipliers per block. So the $K$-th valid multiplier $c_K$ sits in block $q + 1$ at position $r + 1$ within the block, where $(q, r) = \operatorname{divmod}(K - 1, n - 1)$. Block $q + 1$ starts at $qn + 1$, so position $r + 1$ within it is $c_K = qn + r + 1$ (and $r + 1 \leq n - 1 < n$, so $c_K$ is not itself a multiple of $n$, as required). Therefore $p_K = n \cdot c_K = n(qn + r + 1)$. The arithmetic is one divmod and constant work on $O(\log K + \log n)$-bit integers.

**Theorem 3.5 (Integer block-uniformity).** The integers in $B_{b,d}$ have leading-digit counts exactly $b^{d-1}$ per digit $j \in \{1, \ldots, b-1\}$.

*Proof.* An integer in $B_{b,d} = [b^{d-1}, b^d - 1]$ has a unique base-$b$ representation $d_1 d_2 \ldots d_d$ with leading digit $d_1 \in \{1, \ldots, b-1\}$ and $d_2, \ldots, d_d \in \{0, \ldots, b-1\}$. Fixing $d_1$ leaves $d - 1$ positions free over $b$ values, so each leading digit accounts for exactly $b^{d-1}$ integers.

**Theorem 3.6 (Block-aligned uniformity).** If $n^2 \mid b^{d-1}$, the elements of $A_n$ lying in $B_{b,d}$ have leading-digit counts exactly $b^{d-1} \cdot (n-1)/n^2$ per digit.

*Proof.* Suppose $n^2 \mid b^{d-1}$. The $k$-th leading-digit strip $S_k = [k \cdot b^{d-1}, (k+1) \cdot b^{d-1} - 1]$ has length $b^{d-1}$, and its left endpoint $k \cdot b^{d-1}$ is a multiple of $n^2$ (and hence of $n$). For any interval $[a, a + W)$ with $n \mid a$ and $n \mid W$, the count of multiples of $n$ is exactly $W/n$ (the multiples are $a, a + n, \ldots, a + W - n$). So $S_k$ contains exactly $b^{d-1}/n$ multiples of $n$ and exactly $b^{d-1}/n^2$ multiples of $n^2$. Subtracting, the count of elements of $A_n$ per strip is $b^{d-1}/n - b^{d-1}/n^2 = b^{d-1}(n-1)/n^2$, independent of $k$.

**Theorem 3.7 (Family E).** For $d \geq 2$ and $n \in [b^{d-1}, \lfloor (b^d-1)/(b-1) \rfloor]$, the elements of $A_n$ in $B_{b,d}$ are exactly $\{n, 2n, \ldots, (b-1)n\}$ — one per leading digit. (Disjoint from Theorem 3.6 in this regime.)

*Proof.* Three steps. *(In-block.)* For $k \in \{1, \ldots, b-1\}$, $k \cdot n \geq n \geq b^{d-1}$ and $k \cdot n \leq (b-1) \cdot n \leq b^d - 1$ (the upper bound follows from $n \leq \lfloor (b^d - 1)/(b - 1) \rfloor$); so each $k \cdot n$ lies in $B_{b,d}$. Conversely, no other multiple of $n$ does: $b \cdot n > b \cdot b^{d-1} = b^d > b^d - 1$. *(Leading digit.)* The lower bound $k \cdot b^{d-1} \leq k \cdot n$ follows from $n \geq b^{d-1}$. For the upper bound, the hypothesis $n \leq \lfloor (b^d - 1)/(b - 1) \rfloor$ gives $n < b \cdot b^{d-1}/(b - 1)$. The inequality $(k+1)/k \geq b/(b-1)$ holds for $k \in \{1, \ldots, b-1\}$ — cross-multiplying gives $(k+1)(b-1) \geq kb$, i.e., $b - 1 \geq k$, which holds — so $n < ((k+1)/k) \cdot b^{d-1}$ and hence $k \cdot n < (k+1) \cdot b^{d-1}$. Thus $k \cdot n$ has leading digit exactly $k$. *(Sieve removes nothing.)* For $d \geq 2$, $n^2 \geq (b^{d-1})^2 = b^{2d-2} \geq b^d$ (the last step holds for $d \geq 2$), so $n^2 > b^d - 1$ and no multiple of $n^2$ lies in $B_{b,d}$. The set $\{n, 2n, \ldots, (b-1)n\}$ therefore lies in $A_n$ (multiples of $n$ not of $n^2$) and exhausts $A_n \cap B_{b,d}$.

**Criterion 3.8 (Generalized Family E certificate).** Let $W = b^{d-1}$. For integers $(q', m_{\min})$ with $m_{\min} \geq 1$, $q' \geq 1$, set $m_{\max} := m_{\min} + q'(b-1) - 1$. The following finite check is a certificate for exact uniformity. Suppose

$$
\begin{aligned}
(m_{\min} - 1) \cdot n &< W \leq m_{\min} \cdot n, \\
m_{\max} \cdot n &\leq bW - 1 < (m_{\max} + 1) \cdot n,
\end{aligned}
$$

so that $[m_{\min}, m_{\max}]$ is exactly the integer multiplier range whose product with $n$ lands in $B_{b,d}$. Suppose further that for each $k \in [m_{\min}, m_{\max}]$ the leading digit of $kn$ equals $\lceil (k - m_{\min} + 1)/q' \rceil$. Then the multiples of $n$ in $B_{b,d}$ distribute as exactly $q'$ per leading digit. If additionally the multiples of $n^2$ in $B_{b,d}$ distribute uniformly across strips with $\delta$ per strip, this certifies exactly $q' - \delta$ elements of $A_n$ per leading digit.

*Proof.* The four bracketing hypotheses say exactly that $[m_{\min}, m_{\max}]$ is the set of multipliers $k$ for which $k \cdot n \in B_{b,d}$: $(m_{\min} - 1) \cdot n < W \leq m_{\min} \cdot n$ identifies $m_{\min}$ as the smallest such $k$ (equivalently, $m_{\min} = \lceil W/n \rceil$), and $m_{\max} \cdot n \leq bW - 1 < (m_{\max} + 1) \cdot n$ identifies $m_{\max}$ as the largest (equivalently, $m_{\max} = \lfloor (bW - 1)/n \rfloor$). The relation $m_{\max} = m_{\min} + q'(b-1) - 1$ partitions $[m_{\min}, m_{\max}]$ into $b - 1$ consecutive blocks of length $q'$: the $\ell$-th block is $\{m_{\min} + (\ell - 1)q', \ldots, m_{\min} + \ell q' - 1\}$ for $\ell \in \{1, \ldots, b-1\}$. By the leading-digit hypothesis, $k$ in the $\ell$-th block satisfies $\lceil (k - m_{\min} + 1)/q' \rceil = \ell$, so $kn$ has leading digit $\ell$ and lies in strip $S_\ell$. Therefore each strip $S_\ell$ contains exactly the $q'$ products $kn$ for $k$ in the $\ell$-th block, giving $q'$ multiples of $n$ per strip. The count of elements of $A_n$ subtracts the per-strip multiples of $n^2$; if these distribute uniformly with $\delta$ per strip, the per-strip count is $q' - \delta$, independent of $\ell$.

**Corollary 3.9 (Family E as special case).** Theorem 3.7 follows from Criterion 3.8 by setting $q' = 1$, $m_{\min} = \lceil W/n \rceil$, $\delta = 0$.

**Theorem 3.10 (Universal spread bound).** Per-leading-digit counts of $A_n \cap B_{b,d}$ differ by at most 2.

*Proof.* The same divmod argument as Theorem 3.6, applied to generic intervals $[L, L + W)$ with $W = b^{d-1}$ and $L$ not necessarily a multiple of $n$ or $n^2$. For any such interval, the count of multiples of $n$ is $\lfloor (L + W - 1)/n \rfloor - \lfloor (L - 1)/n \rfloor$, which equals either $\lfloor W/n \rfloor$ or $\lfloor W/n \rfloor + 1$ depending on $L \bmod n$. Each leading-digit strip $S_k$ is such an interval of length $W$, so its multiples-of-$n$ count lies in a two-element set $\{\lfloor W/n \rfloor, \lfloor W/n \rfloor + 1\}$; the same argument with $n^2$ gives the multiples-of-$n^2$ count in an analogous two-element set. The per-strip count of elements of $A_n$ is the difference of these two values; values from two two-element sets differ across strips by at most $1 + 1 = 2$.

The bound is tight: at $(b, n, d) = (4, 3, 2)$, $A_n \cap B_{b,d} = \{6, 12, 15\}$ has per-leading-digit counts $[1, 0, 2]$ on digits $\{1, 2, 3\}$, spread $= 2$. The implementation sweep at $b, n \in \{2, \ldots, 10\}$, $d \in \{1, \ldots, 5\}$ contains this single spread-$2$ cell; all other cells have spread in $\{0, 1\}$.

**Corollary 3.11 (Half-aligned regime).** If $n \mid b^{d-1}$ but $n^2 \nmid b^{d-1}$, the per-leading-digit counts of $A_n \cap B_{b,d}$ have spread at most 1.

*Proof.* Set $W = b^{d-1}$. For each strip $S_k = [kW, (k+1)W - 1]$, the left endpoint $kW$ is a multiple of $n$ (since $n \mid W$), and $W$ itself is a multiple of $n$, so by the divmod count for intervals $[a, a+W)$ with $n \mid a$ and $n \mid W$, every strip contains exactly $W/n$ multiples of $n$ — the per-strip multiples-of-$n$ count is constant across the block. The multiples-of-$n^2$ count, by Theorem 3.10's proof applied to $S_k$, lies in $\{\lfloor W/n^2 \rfloor, \lfloor W/n^2 \rfloor + 1\}$ across strips, so its spread is at most 1. The per-strip count of $A_n$ is the difference; spread $\leq 0 + 1 = 1$. At $b = 10$ this regime catches $n \in \{2, 5\}$ at $d = 2$, $n = 4$ at $d \in \{3, 4\}$, $n = 25$ at $d \in \{3, 4\}$, and similar — the cells between Theorem 3.6's certified regime ($n^2 \mid b^{d-1}$, spread 0) and Theorem 3.10's universal bound.

## The cipher

For any `period` $\in [2, 2^{32} - 1]$ and any key, `bidder_block_at(ctx, ·)` is a stateless keyed bijection of $[0, \mathtt{period})$. *Bijection* — every output in $[0, \mathtt{period})$ occurs exactly once. *Stateless* — `at(i)` does not mutate `ctx` and does not require `at(0)`, $\ldots$, `at(i-1)` to have been called first. *Keyed* — identical key + period produce identical permutations across runs and machines. The backend is Speck32/64 in cycle-walking mode for `period` $\geq 2^{26}$ (Beaulieu et al. 2013; cycle-walking from Black & Rogaway 2002), with an unbalanced 16-round Feistel network for smaller `period` in the textbook PRF$\to$PRP construction (Luby & Rackoff 1988); the round count is the `BIDDER_FEISTEL_ROUNDS` build constant. The contract relied on throughout is bijection-hood, not PRP quality.

The contract has two consequences for prefix-mean variance, one exact and one measured. Whole-block sampling at $N = P$ inherits exactness from the substrate: for any bijection $\pi : [0, P) \to [0, P)$ and any $f$,

$$
\frac{1}{P} \sum_{i=0}^{P-1} f(\pi(i)/P) = \frac{1}{P} \sum_{k=0}^{P-1} f(k/P) = R(f, P),
$$

the left-endpoint Riemann sum, since $\{\pi(0), \ldots, \pi(P-1)\}$ is the same multiset as $\{0, \ldots, P-1\}$. The identity is bijection-trivial — any keyed permutation has it — and is the reason BIDDER's prefix-mean variance at $N = P$ is machine-$\varepsilon$. **Sub-endpoint sampling at $N < P$ is a different story.** The relevant baseline is the finite-population correction (FPC) variance for a uniformly random permutation:

$$
\frac{\sigma^2}{N} \cdot \frac{P - N}{P - 1}.
$$

`replication/m2_fpc_gap.py` measures the *realization gap* — the ratio of BIDDER's empirical prefix-mean variance to ideal FPC — by computing $R$ and $\sigma^2$ on the grid $\{f(k/P) : 0 \leq k < P\}$, generating $2000$ keyed BIDDER permutations per cell, measuring prefix-mean variance about $R$, and dividing by ideal FPC. The integrand is $f(x) = \sin(\pi x)$. All cells in the panel below have $P < 2^{26}$ and therefore use the Feistel fallback.

| $P \backslash N$ | $0.10 \cdot P$ | $0.25 \cdot P$ | $0.50 \cdot P$ | $0.75 \cdot P$ | $0.90 \cdot P$ |
|---|---|---|---|---|---|
| 200   | 1.016 | 1.000 | 1.029 | 1.018 | 0.948 |
| 500   | 1.015 | 0.958 | 1.005 | 1.001 | 1.002 |
| 1000  | 0.103 | 0.103 | 0.121 | 0.165 | 0.168 |
| 2000  | 1.101 | 1.274 | 1.320 | 1.234 | 1.101 |
| 5000  | 1.409 | 1.681 | 1.898 | 1.718 | 1.384 |
| 10000 | 1.917 | 2.583 | 2.960 | 2.569 | 1.945 |

The panel should be read as an operational measurement of the Feistel fallback, not as part of the exact substrate contract. Across non-power-of-2 Feistel side lengths $s = \lceil\sqrt{P}\rceil$, the realization gap stays within $3\times$ ideal at the worst cell ($P = 10\,000$, $N = P/2$), with sampling-noise-floor ratios at $P \in \{200, 500\}$; the U-shape in $N/P$ peaks near $N = P/2$ as the FPC variance peaks. The kernel ships at 16 Feistel rounds; the round count was chosen by sweeping $r \in \{8, 12, 16\}$, where the gap at $(P, N) = (10\,000, 5000)$ collapses from $\sim 32\times$ at 8 rounds to $\sim 8\times$ at 12 to $\sim 3\times$ at 16, roughly geometric in extra rounds — each four-round bump buys about $3\times$ variance reduction at the peak of the FPC curve.

**At power-of-2 Feistel side lengths, more rounds does not monotonically reduce the realization gap.** The $P = 1000$ cell ($s = 32$) shows the gap *inverting sign* with round count: ratio $\sim 0.1$ at 8 rounds (underdispersion), $\sim 5$ at 12 rounds (overdispersion), $\sim 0.1$ again at 16 rounds. The pattern is consistent with cycle-parity interaction — each four rounds completes one Luby–Rackoff PRP cycle, and at power-of-2 $s$ the round function's residue arithmetic against $L\_\text{size}$ aligns with bit-block structure, so cycle-count parity flips the *sign* of residual bias rather than reducing its magnitude. Ratios at neighboring non-power-of-2 side lengths sit on the rule-of-thumb curve (e.g. $s \in \{63, 65\}$ at $\sim 1.3$–$1.4$, $s \in \{127, 129\}$ at $\sim 2.2$), while $s = 64$ and $s = 128$ stay anomalous (ratios $\leq 0.07$ and $\leq 0.03$ respectively, dropping to $\sim 0.004$ and $\sim 0.002$ at the perfect-square fit $P = s^2$). 

**The kernel ships at 16 rounds.** That count is empirically near-FPC-ideal across the non-power-of-2 panel and lands at a stable sign state for power-of-2 $s$. The round count is exposed as a build-time setting (`BIDDER_FEISTEL_ROUNDS`) for embedded users who want to trade FPC fidelity for cipher cost — but only along the non-power-of-2 trade curve. A re-implementer who tunes the knob expecting monotone improvement at power-of-2 $\lceil\sqrt{P}\rceil$ will not get it: 12 rounds or 20 rounds (different Luby–Rackoff cycle parity than 16's) lands at the *opposite* sign of the same anomaly, not at a smaller bias. Two safe options: pick $P$ such that $\lceil\sqrt{P}\rceil$ is non-power-of-2 (rule of thumb applies, predictable trade curve), or measure the realization gap empirically at the deployed $(P, \text{rounds})$ before relying on it. Whole-block use does not pay the gap and relies only on bijection-hood.

**FF1 as comparator backend.** FF1 with AES (NIST SP 800-38G) is a keyed bijection on the same domain with a cryptographic PRP objective. Run through the same Python wrapper on the measured cells, FF1 lands at ratio $\sim 0.92$ on $(P, N) \in \{(2000, 1000), (10000, 5000)\}$ — sampling-consistent with ideal FPC at this measurement scale — at $\sim 10$–$15\times$ higher per-call cost than 16-round BIDDER. This makes FF1 the right backend for power-of-2 $\lceil\sqrt{P}\rceil$ workloads where the BIDDER anomaly is intolerable, or for sub-endpoint Monte Carlo at large $P$ where the residual $\sim 3\times$ gap does not fit the error budget. It is not part of BIDDER's exactness claim: the substrate's leading-digit guarantees and the $N = P$ endpoint identity depend only on counting and bijection-hood; cipher quality bends prefix-mean variance at $N < P$.

## Sampling

The composition has two modes. In whole-block mode, choose $P$ as a count of $A_n \cap B_{b,d}$ certified by Theorem 3.6, Theorem 3.7, or Criterion 3.8, and let $K_0$ be the number of elements of $A_n$ below the certified block's left endpoint. For each $i = 0, \ldots, N - 1$, the cipher returns $j_i \in [0, P)$, and Lemma 3.4 with $K = K_0 + j_i + 1$ returns the corresponding element in the certified block. At $N = P$, this visits the certified block exactly once, so the block's leading-digit distribution is inherited exactly. In stratified mode, instantiate one keyed prefix per leading-digit stratum and choose the prefix length $N_j$ separately in each stratum; this is the mode for exact leading-digit counts at $N < P$.

The three use cases below share a niche: a finite population must be visited in keyed order, reproducibly, in a setting where materializing the permutation is not on the table — large enough that materialization becomes the design constraint (stratified audit sampling at $b=10, d=9$, or finite-population Monte Carlo at very large $P$) or too dependency-heavy for embedded hardware (a leading-digit conformity detector). In each, the natural alternatives — `numpy.random.permutation` over an enumerated index, FF1 over a precomputed element list — need either an array you cannot store or a dependency you cannot ship. BIDDER trades a modest residual sub-endpoint gap (within $\sim 3\times$ ideal FPC at the worst measured cell, sampling-noise-consistent at small $P$) for a small, self-contained, keyed construction that runs without materializing the population or shipping anything beyond the kernel — and replays from the key alone, on any machine and any library version. Each example below names its binding constraint; where it doesn't bind, the simpler alternative is the better choice.

### Uniform-leading-digit reference for Benford tests

A practitioner running a leading-digit conformity test — forensic accounting, election forensics, dataset-integrity audit, or a memory-constrained field device — sometimes needs a uniform-leading-digit control rather than a sample from Benford's logarithmic law. The natural baseline is enumeration: list the integers in $B_{b,d}$ (or the elements of $A_n \cap B_{b,d}$ when $n^2 \mid b^{d-1}$), group by leading digit, hand the detector a deterministic block. For order-independent statistics — Pearson chi-squared, Kolmogorov–Smirnov, anything that consumes the multiset — enumeration suffices and BIDDER adds nothing of substance: the substrate alone delivers exact per-digit counts. The case for BIDDER combines two regimes: *order-dependent* detectors (sequential tests, online stopping rules, change-point monitors — anything that reads the stream and reports along the way) need an order that does not leak the lexicographic magnitude structure of enumeration; *deployment-constrained* detectors (embedded compliance monitors, field-deployed audit tools) need a self-contained construction without a materialized element list or a heavy library. Both also need an exactly-uniform reference and reproducibility across runs. BIDDER's keyed bijection over the certified block delivers the combination in a small dependency-free kernel.

The chi-squared panel demonstrates the substrate baseline that both BIDDER and bare enumeration inherit. `replication/use_case_02_benford_null.py` reports Pearson chi-squared exactly $0.0000$ on a five-cell panel — integer-level $(b, d) \in \{(10, 3), (10, 4), (10, 5), (8, 5), (16, 4)\}$ and sieved $(b, n, d) \in \{(10, 2, 3), (10, 2, 4), (10, 2, 5), (8, 2, 5), (16, 2, 4)\}$. At $(b, n, d) = (10, 2, 4)$ the substrate yields $2{,}250$ elements of $A_n$ in $[1000, 9999]$ with exactly $250$ per leading digit (the block-aligned count $b^{d-1}(n-1)/n^2$). The i.i.d.-uniform comparator across $1000$ trials per cell reports chi-squared distributed as $\chi^2(b-2)$ — empirical means $7.83$, $8.07$, $7.98$ at $b = 10$ (theoretical $b - 2 = 8$), $6.07$ at $b = 8$ (theoretical $6$), $14.00$ at $b = 16$ (theoretical $14$); standard deviations track $\sqrt{2(b-2)}$ — which is the per-replicate sampling noise a calibration against i.i.d. inherits and that the substrate (with or without BIDDER's shuffle) eliminates.

Order-sensitive diagnostics separate BIDDER from bare enumeration. We use an exact-balanced integer block $[1000,9999]$, with $1000$ values at each leading digit, and measure the maximum finite-population standardized leading-digit deviation over all prefixes. Lexicographic enumeration has worst prefix imbalance $D_{\max} = 94.863$ at the first digit boundary; one BIDDER key gives $D_{\max} = 3.948$; across $64$ BIDDER keys the median is $3.946$ and the 95th percentile is $4.920$; across $256$ uniformly random permutations the median is $3.534$ and the 95th percentile is $4.499$. BIDDER's keyed order removes the lexicographic pathology — about a $24\times$ reduction in $D_{\max}$ — and at 16 rounds its noise floor sits within $\sim 12\%$ of uniformly random permutations at this scale, sampling-noise-consistent with $P = 9000$ and $\lceil\sqrt{P}\rceil = 95$ on the non-power-of-2 trade curve from the cipher section. The case for BIDDER over `numpy.random.permutation` here is therefore operational rather than statistical: stateless keyed reproducibility across machines and library versions, without materializing the certified block. At $P = 9000$ the materialization claim is not binding (the array is about 36 KB); the cross-machine, cross-version replay claim is. Order-sensitive workflows that do not need that replay should prefer a seeded uniformly random permutation.

### Stratified survey design with exact leading-digit strata

In audit sampling over account IDs, invoice magnitudes, or registry blocks, leading digit is sometimes a mandated reporting stratum: regulators ask for sample composition by leading digit, or the workflow downstream estimates a ratio per leading-digit class. A survey designer drawing a sample of size $N_{\text{total}}$ from such a finite population indexed by the digit-class block $B_{b,d}$ wants strata defined by leading digit. The statistical baseline is per-stratum simple random sampling without replacement — one `numpy.random.choice(stratum, N_j, replace=False)` per leading-digit stratum — which gives exact stratum sizes by construction. BIDDER does not improve that design statistically. It implements the same exact-stratum, without-replacement design as a stateless keyed prefix: no materialized stratum, no materialized index array, and reproducible reconstruction from `(key, stratum, i)` across machines and library versions — the auditor's record is the key, not a saved index array. At $b = 10$, $d = 9$, each leading-digit stratum has $10^8$ indices; materializing one `uint64` stratum is about 800 MB, and all nine strata are about 7.2 GB before sample arrays.

The demo below lives at $(b, d) = (10, 4)$ to exercise the construction, where each stratum is a few KB and materialization is free; the binding-constraint regime is the $(10, 9)$ scale named above. `replication/use_case_01_stratified_survey.py` runs the demo across nine strata and $\alpha \in \{0.1, 0.5, 1.0\}$ (100, 500, 1000 per stratum, $N_{\text{total}} \in \{900, 4500, 9000\}$): per-stratum counts are exactly $N_j = \lfloor \alpha \cdot 1000 \rfloor$ at every cell. The included i.i.d.-then-post-stratify comparator is a failure-mode baseline, not the main competitor: `Binomial(N_{\text{total}}, 1/(b-1))` per stratum reports 99th-percentile maximum stratum deviation across 1000 trials growing from 31 ($\alpha = 0.1$) to 97 ($\alpha = 1.0$). Per-stratum SRSWOR and BIDDER both avoid that deviation; BIDDER's additional claim is operational rather than statistical: exact strata without materialization, with keyed replay as the audit record.

### Monte Carlo with known endpoint and measured FPC realization gap

Monte Carlo uses whole-block mode on the finite population $[0, P)$: the estimator is the prefix mean of $f(\pi(i)/P)$ for a keyed bijection $\pi$. The natural baseline is `numpy.random.permutation(P)` — exact FPC at every $N$, but it materializes an array of size $P$. The endpoint identity (substrate-free, bijection-trivial) and the realization gap from the cipher section are the load-bearing facts on the BIDDER side.

At $P = 2000$ and $f(x) = \sin(\pi x)$, `replication/use_case_06_variance_mc.py` reports BIDDER variance at $N = P$ of $7.88 \times 10^{-31}$ (machine-$\varepsilon$; floating-point round-off in the sum), ideal-FPC variance $0$ exactly, and i.i.d.-with-replacement variance $\sigma^2/P \approx 4.7 \times 10^{-5}$ (never zero). For interior prefixes at the 16-round default, the measured ratio peaks at $\sim 1.32$ at $N = P/2 = 1000$ and tapers toward the endpoints. The four options sort cleanly: i.i.d. with replacement never gets the FPC; `numpy.random.permutation` gets the ideal FPC but materializes (impossible for $P$ above $\sim 10^9$ on a workstation, awkward well below that); BIDDER streams without materialization, exact at the endpoint and within $\sim 30\%$ of ideal at sub-endpoint at this $P$; FF1 is the higher-cost backend for sub-endpoint at very large $P$ or for power-of-2 $\lceil\sqrt{P}\rceil$ workloads, landing near ideal on the measured cells. The BIDDER niche is whole-block at large $P$ — where the realization gap does not apply and materialization is the binding constraint — or sub-endpoint at any $P$ where the measured structural deviations fit the error budget.

## Software interface

The package exposes two constructors and a random-access operation. `cipher(period, key)` returns a keyed bijection of $[0, P)$; `sawtooth(n, count)` returns the first `count` elements of $A_n$ in ascending order; both support `.at(i)`. A whole-block workflow at $(b,n,d)=(10,2,4)$ — where Theorem 3.6 gives $P=2250$ with exactly $250$ per leading digit — checks the construction end-to-end:

```
import bidder

b, n, d = 10, 2, 4
W = b ** (d - 1)
P = (b - 1) * W * (n - 1) // (n * n)
offset = (W - 1) // n - (W - 1) // (n * n)

block = bidder.cipher(P, b"paper-key")
seq = bidder.sawtooth(n, offset + P)
sample = [seq.at(offset + block.at(i)) for i in range(P)]

counts = [sum(digit * W <= x < (digit + 1) * W for x in sample) for digit in range(1, b)]
assert counts == [W * (n - 1) // (n * n)] * (b - 1)
```

The reference kernel is $\sim 300$ lines of C with no third-party dependencies, exposed through five functions in `bidder_root.h` (`bidder_cipher_init/at/backend`, `bidder_sawtooth_init/at`) — the stable boundary used by the Python wrapper and any future binding.

## Related work

Four neighbors place BIDDER: PRNGs from normal numbers, quasi-Monte Carlo, exact ranged-integer generation, and format-preserving encryption. Each matches one part of the construction but not the whole finite-population contract.

Normal-number digit-stream constructions are the closest mathematical neighbor. Bailey and Crandall's Stoneham construction (Bailey & Crandall 2002; Bailey 2004) gives a deterministic, reproducible, random-access digit stream: the $K$-th base-$b$ digit of $\alpha_{b,c} = \sum_{n=0}^{\infty} 1/(c^n b^{c^n})$ can be extracted without computing the prefix, and the distributional guarantee is asymptotic normality. BIDDER shares the random-access and reproducibility shape, but not the object. Bailey-Crandall gives one infinite digit stream per $(b, c)$ pair; BIDDER gives a keyed family of finite bijections. Bailey-Crandall gives asymptotic equidistribution of digits; BIDDER gives exact finite-block leading-digit counts in certified regimes. Bailey-Crandall rests on a normality theorem; BIDDER rests on divmod counts for multiples of $n$ and $n^2$ in $B_{b,d}$. The resemblance is real, but the contract is different: infinite digit stream versus keyed finite-population ordering.

Quasi-Monte Carlo is the closest statistical-design neighbor. Halton, Sobol', and their descendants (Halton 1960; Sobol' 1967; Niederreiter 1992; Owen 1995; Dick & Pillichshammer 2010) construct deterministic or scrambled point sets in $[0, 1]^d$ with low discrepancy, typically controlled asymptotically as $O((\log N)^d/N)$ for fixed dimension. That is a stronger target for numerical integration than i.i.d. sampling, but it is not the same target as BIDDER. QMC controls geometric discrepancy in a continuous cube; BIDDER controls exact counts in discrete digit-class blocks and keyed orderings of finite populations. Scrambling gives randomized QMC variants, but not a reproducible bijection of an arbitrary finite set with endpoint multiset identity. Conversely, BIDDER is not a low-discrepancy sequence in $[0,1]^d$ and makes no integration-error claim beyond the measured finite-population behavior in the cipher section.

Exact ranged-integer generation (Lemire 2019; Saad et al. 2020) solves the one-draw problem: map random bits to an unbiased draw from $[0, s)$. That is the right primitive for i.i.d. sampling with replacement; BIDDER fixes a finite population and returns a keyed ordering, so the endpoint property is different. Format-preserving encryption is the closest cipher-level substitute: FF1 and FF3-1 in NIST SP 800-38G give AES-based keyed bijections on finite domains. In the measurements above, FF1 is the right backend for power-of-2 $\lceil\sqrt{P}\rceil$ workloads where BIDDER's structural anomaly is intolerable, or for sub-endpoint Monte Carlo at very large $P$ where BIDDER's $\sim 3\times$ residual gap does not fit the budget; for the rest, BIDDER's 16-round Feistel is sampling-consistent with FF1 at one-tenth the per-call cost, dependency-free, and keeps the substrate's whole-block exactness through bijection-hood. The choice is contractual: PRP-strength and uniformly near-ideal sub-endpoint FPC versus small dependency-free C implementation, keyed random access, exact finite-block substrate counts, and a residual gap on the documented trade curve.

## Validation and replication

The validation story is claim-based. From a clean checkout, build the package kernel with `make` at repository root. In `paper/bidder-stat/`, `make venv` installs pinned dependencies, `make test` runs the Python wrapper, C-wrapper, and theory tests, and `make replicate` rebuilds the reported measurements under `replication/*_results.md`. The manuscript snapshots those outputs in `paper/measurements/*_results.md`; the smoke-test output is recorded in `paper/measurements/e4_smoke.md`.

The first validation layer checks the package behavior exposed above:

| contract | public behavior checked | validation target |
|---|---|---|
| keyed bijection | `cipher(period, key).at(i)` is pure, in range, and bijective on checked small domains | `tests/test_api.py`, `tests/test_bidder_block.py`, `tests/test_bidder_root.py` |
| backend parity | Python wrapper, C wrapper, and pure-Python oracle agree on checked calls | `tests/test_bidder.py`, `tests/test_bidder_root.py` |
| Speck backend | published Beaulieu et al. Appendix C vectors and round-trip behavior hold | `tests/test_speck.py` and the corresponding C test |
| sawtooth sequence | `sawtooth(n, count).at(i)` is monotone, in range, and matches the closed-form $A_n$ oracle | `tests/test_sawtooth.py`, `tests/test_acm_core.py` |
| endpoint and FPC claims | endpoint identity and sub-endpoint realization-gap measurements reproduce | `tests/theory/test_riemann_property.py`, `tests/theory/test_quadrature_rates.py`, `tests/theory/test_fpc_shape.py` |

The second validation layer checks the substrate claims through the implementation. The proofs cover all valid parameters; the table gives the exhaustive sweeps exercised by the package test suite, plus the Appendix A diagnostic scripts that support the non-contract boundary discussion.

| result | public behavior checked | validation target | tested sweep |
|---|---|---|---|
| Lemma 3.4 (Closed-form indexing) | `bidder_sawtooth_at` | `test_at_matches_a_n_oracle` (closed-form vs enumeration) | $n \in \{2, \ldots, 12\}$ |
| Theorem 3.5 (Integer block-uniformity) | (fact about $\mathbb{Z}$) | `test_block_boundary_*` | base 10, $d \in \{1, \ldots, 9\}$ |
| Theorem 3.6 (Block-aligned) | `bidder_sawtooth_at` | `test_block_uniformity_sufficient` | $b, n \in \{2, \ldots, 10\}$, $d \in \{1, \ldots, 5\}$ |
| Theorem 3.7 (Family E) | `bidder_sawtooth_at` | `test_block_uniformity_family_e` | $b \in \{2, \ldots, 10\}$, $d \in \{2, \ldots, 5\}$ |
| Criterion 3.8 (Generalized Family E certificate) | `bidder_sawtooth_at` | `test_block_uniformity_generalized_family_e` | $b \in \{2, \ldots, 10\}$, $d \in \{2, \ldots, 5\}$, $q' \in \{2, \ldots, 50\}$, $m_{\min} \in \{1, \ldots, 100\}$ |
| Theorem 3.10 (Spread bound) | `bidder_sawtooth_at` | `test_block_uniformity_spread_bound` | $b, n \in \{2, \ldots, 10\}$, $d \in \{1, \ldots, 5\}$ |
| Corollary 3.11 (Half-aligned spread) | `bidder_sawtooth_at` | `test_block_uniformity_half_aligned` | half-aligned subset of the $b, n \in \{2, \ldots, 10\}$, $d \in \{1, \ldots, 5\}$ sweep — 31 triples |
| Appendix A boundary checks | structural diagnostic, Beatty reduction, base-10 conjecture scope | `experiments/math/diophantus/structural_theorem.py`; `beatty_reduction.py`; `conjecture_probe.py`; `conjecture_A_partial.py` | structural sweep 1925 cells; Beatty sweep 17 cells; base-10 conjecture sweep $n \leq 5000$, $d \leq 14$ |

## Conclusion

BIDDER is useful in the narrow arena where exact leading-digit composition, keyed replay, random access, and no materialized permutation must all hold at once — settings where `numpy.random.permutation` materializes too much and FF1 brings more cryptographic machinery and per-call cost than the use needs. Its contribution is the substrate-and-bijection contract. Counting proves the certified block and stratum exactness; closed-form indexing makes the certified population addressable; the keyed bijection supplies reproducible order without changing the endpoint multiset.

The measurements make the boundary explicit. Whole-block use inherits exactness from counting and bijection-hood; sub-endpoint Monte Carlo uses the measured realization gap as part of the error budget; order-sensitive leading-digit controls use BIDDER to remove lexicographic enumeration pathology at near-parity with uniform random permutations on non-power-of-2 side lengths. The resulting object is small but real: a reproducible finite-population sampler for certified leading-digit blocks and exact strata, with every exact claim tied to a proof and every statistical claim tied to a regenerable measurement.
