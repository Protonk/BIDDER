# BIDDER: Exact Leading-Digit Sampling with Keyed Random Access

## Abstract

We present BIDDER, a small C library for reproducible keyed random access to finite integer sets with certified leading-digit structure. The substrate is a counting result for $n$-prime atoms of $M_n = \{1\} \cup n\mathbb{Z}_{>0}$ on digit-class blocks: several regimes give exact per-leading-digit counts (notably $b^{d-1}(n-1)/n^2$ when $n^2 \mid b^{d-1}$), a universal spread bound of 2 holds outside them, and the $K$-th atom has a closed form. The cipher is a keyed stateless bijection of $[0, P)$, implemented as Speck32/64 in cycle-walking mode for $P \geq 2^{26}$ with an unbalanced 8-round Feistel fallback for smaller $P$. The sampling layer applies the cipher to certified blocks or per-stratum prefixes, supplying uniform-leading-digit controls, exact stratum sizes, and finite-population Monte Carlo with an exact endpoint identity and a measured sub-endpoint realisation gap (up to $\sim 32\times$ ideal FPC variance on the small-period backend). Roughly 300 lines of dependency-free C with Python replication scripts and tests.

## Overview

Fix $n \geq 2$. The multiples of $n$ form a semigroup under multiplication; adjoining $1$ gives a monoid $M_n = \{1\} \cup n\mathbb{Z}_{>0}$. Its atoms — indecomposable elements that cannot be written as a product of two non-units — are exactly the multiples of $n$ not divisible by $n^2$, i.e., $n\mathbb{Z} \setminus n^2\mathbb{Z}$. We call these the *$n$-prime atoms* of $M_n$: within the monoid they play the role primes play in $\mathbb{Z}$. For $n = 2$ they are $\{2, 6, 10, 14, 18, \ldots\}$ — the integers divisible by 2 but not 4.

The substantive question is how these atoms distribute across digit-class blocks $B_{b,d} = [b^{d-1}, b^d - 1]$. The answer is a counting argument from positional notation. In the smooth regime where $n^2 \mid b^{d-1}$, each leading-digit strip of length $b^{d-1}$ starts at a multiple of $n^2$; subtracting multiples of $n^2$ from multiples of $n$ per strip gives exactly $b^{d-1} \cdot (n-1)/n^2$ atoms per leading digit, independent of strip. Outside the smooth regime, a universal spread bound of 2 holds, and a Family-E construction ($n \in [b^{d-1}, \lfloor (b^d-1)/(b-1) \rfloor]$) gives exact uniformity in a disjoint range. Closed-form indexing — $c_K = q \cdot n + r + 1$ with $(q, r) = \operatorname{divmod}(K - 1, n - 1)$ — returns the $K$-th atom in $O(\log K + \log n)$-bit work, no enumeration. At $(b, n, d) = (10, 2, 4)$, for instance, the smooth condition holds ($4 \mid 1000$) and the count is exactly $250$ atoms per leading digit on $[1000, 9999]$.

To this exactly uniform sawtooth we attach a small-block cipher, a keyed bijection of $[0, P)$ where $P$ is an atom count certified by one of the substrate's exact-distribution regimes. The cipher reorders the $P$ atoms; the substrate keeps the reordering leading-digit-exact. The construction is three contracts, used separately.

| layer | contract | exact claim | limitation |
|---|---|---|---|
| substrate | Count and index $n$-prime atoms in digit-class blocks | exact per-leading-digit counts in Theorems 3.5--3.7; spread $\leq 2$ universally; closed-form $K$-th atom in Lemma 3.10 | exact uniformity only in certified regimes; Remark 3.13 leaves one base-10 trigger-set conjecture open |
| cipher | Keyed stateless bijection of $[0, P)$ | every value in $[0, P)$ appears exactly once; same key and period reproduce the same order | bijection-hood is the relied-on contract; sub-endpoint mixing is measured, not proved |
| sampling | Apply the cipher to certified blocks or per-stratum prefixes | exact endpoint for whole-block mode; exact stratum sizes in stratified mode | arbitrary prefixes are not automatically leading-digit-exact; interior Monte Carlo variance has a backend-dependent measured gap |

Operationally, BIDDER targets the intersection summarized above: streaming random-access, keyed reproducibility across runs and machines, arbitrary period $P \in [2, 2^{32} - 1]$, and no materialised permutation; exact leading-digit claims come from certified blocks or stratified prefixes. The cipher backend is Speck32/64 in cycle-walking mode (Beaulieu et al. 2013; cycle-walking from Black & Rogaway 2002) for $P \geq 2^{26}$, with an unbalanced 8-round Feistel network for smaller $P$ (Luby & Rackoff 1988); the contract relied on throughout is bijection-hood, not PRP quality. `make replicate` reproduces every table in this paper from source.

Existing tools occupy adjacent corners: random-access digit streams, low-discrepancy deterministic designs, unbiased ranged-integer samplers, and standards-track format-preserving encryption. BIDDER's target is their intersection for a narrower finite-population problem: exact leading-digit counts, keyed stateless ordering, arbitrary period up to $2^{32}-1$, and no materialised permutation. The detailed comparison is deferred to Related work so the construction can be stated once here.

The next sections prove the substrate's distribution and indexing results, describe the cipher and how it attaches to the substrate, walk three worked examples, place BIDDER against prior work, and present the artifact and tests that back it.

## The substrate

The substrate is a bundle of distribution and indexing results for the $n$-prime atoms of $M_n$ on digit-class blocks. Definitions 3.1–3.3 fix the objects; Theorem 3.4 fixes the integer baseline; Theorems 3.5–3.7 give three exact-distribution regimes for $n$-prime atoms; Theorem 3.9 gives the universal spread bound when none of those regimes applies; Lemma 3.10 gives the random-access closed form; Theorem 3.11 and Lemma 3.12 narrow the remaining spread-zero case; Remark 3.13 states the base-10 conjecture left open. Throughout, fix $(b, n, d)$ with $b \geq 2$, $d \geq 1$, $n \geq 2$.

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

**Lemma 3.10 (Closed-form indexing).** For $K \geq 1$, the $K$-th $n$-prime atom of $M_n$ is $p_K = n \cdot c_K$ with $c_K = q \cdot n + r + 1$ where $(q, r) = \operatorname{divmod}(K - 1, n - 1)$. Computing $p_K$ from $K$ is one divmod and arithmetic on $O(\log K + \log n)$-bit integers; no enumeration.

*Proof.* The $n$-prime atoms of $M_n$ are the multiples of $n$ not divisible by $n^2$, i.e., $\{cn : c \in \mathbb{Z}_{>0}, n \nmid c\}$. In each block of $n$ consecutive positive integers — $\{1, \ldots, n\}, \{n+1, \ldots, 2n\}, \ldots$ — exactly one (the multiple of $n$) is excluded, leaving $n - 1$ valid multipliers per block. So the $K$-th valid multiplier $c_K$ sits in block $q + 1$ at position $r + 1$ within the block, where $(q, r) = \operatorname{divmod}(K - 1, n - 1)$. Block $q + 1$ starts at $qn + 1$, so position $r + 1$ within it is $c_K = qn + r + 1$ (and $r + 1 \leq n - 1 < n$, so $c_K$ is not itself a multiple of $n$, as required). Therefore $p_K = n \cdot c_K = n(qn + r + 1)$. The arithmetic is one divmod and constant work on $O(\log K + \log n)$-bit integers.

**Theorem 3.11 (Structural decomposition of spread-zero, $n^2 > W$).** Let $W = b^{d-1}$ and suppose $n^2 > W$, outside the Family E regime of Theorem 3.6. For $k \in \{1, \ldots, b-1\}$, let $C_m(k)$ be the number of multiples of $m$ in the strip $S_k$. Write $C_n(k) = \lfloor W/n \rfloor + e_n(k)$, with $e_n(k) \in \{0, 1\}$, and set $r = W \bmod n$, $E_n = \#\{k : e_n(k) = 1\}$, and $M = \lfloor (bW - 1)/n^2 \rfloor$. Define

$$
I_n =
\begin{cases}
\{\lceil (jn + 1)/r \rceil - 1 : j = 1, \ldots, E_n\}, & r \geq 1, \\
\emptyset, & r = 0,
\end{cases}
\qquad
I_{n^2} = \{\lfloor jn^2/W \rfloor : j = 1, \ldots, M\}.
$$

Both are subsets of $\{1, \ldots, b-1\}$. The $n$-prime atom counts in $B_{b,d}$ have spread $= 0$ if and only if exactly one of the following three constant-difference cases holds:

1. $I_n = I_{n^2}$;
2. $I_n = \emptyset$ and $I_{n^2} = \{1, \ldots, b-1\}$;
3. $I_n = \{1, \ldots, b-1\}$ and $I_{n^2} = \emptyset$.

*Proof.* Write $W = an + r$ with $0 \leq r < n$. For $r \geq 1$,

$$
C_n(k) = a + \left\lfloor \frac{(k+1)r - 1}{n} \right\rfloor
          - \left\lfloor \frac{kr - 1}{n} \right\rfloor.
$$

The last difference is $0$ or $1$, and its $j$-th occurrence is the smallest $k$ with $(k+1)r \geq jn + 1$, namely $k = \lceil (jn + 1)/r \rceil - 1$. Thus $I_n$ is exactly the set of strips with $e_n(k) = 1$; when $r = 0$, all strips begin at multiples of $n$ and $I_n = \emptyset$.

Since $n^2 > W$, each strip contains at most one multiple of $n^2$. The multiples of $n^2$ that lie in $B_{b,d} = [W, bW - 1]$ are $jn^2$ for $j = 1, \ldots, M$, and $jn^2$ lies in strip $\lfloor jn^2/W \rfloor$. Hence $I_{n^2}$ is exactly the set of strips containing a multiple of $n^2$; write $e_{n^2}(k)$ for its indicator.

The atom count in strip $S_k$ is

$$
A_k = C_n(k) - C_{n^2}(k)
    = \lfloor W/n \rfloor + (e_n(k) - e_{n^2}(k)).
$$

The first term is constant in $k$, so spread $= 0$ is equivalent to $e_n(k) - e_{n^2}(k)$ being constant. Since both excess functions take values in $\{0, 1\}$, the constant difference can only be $0$, $+1$, or $-1$, giving cases 1, 3, and 2 respectively. These cases are exhaustive.

**Lemma 3.12 (Beatty-pair coincidence reduction).** In addition to the hypotheses of Theorem 3.11, suppose $r = s$, where $s = \lfloor W/n \rfloor \bmod n$. Then $W = r(n+1)$. Assume also $M \geq 1$ and $E_n \geq 1$, so $I_n$ and $I_{n^2}$ are non-empty. Case 1 of Theorem 3.11 holds if and only if

$$
(jn) \bmod r \geq \left\lceil \frac{jn}{n+1} \right\rceil
\qquad \text{for all } j \in \{1, \ldots, M\}.
$$

For $j \leq n$, the right-hand side is $j$; for $j > n$, it is strictly less than $j$. Both ranges occur in the regime, so the ceiling form is the universal statement.

*Proof.* Since $n^2 > W$, writing $W = Qn^2 + sn + r$ gives $Q = 0$. The condition $r = s$ therefore gives $W = r(n+1)$. For $j = 1, \ldots, M$, put

$$
X_j = \frac{jn + 1}{r},
\qquad
Y_j = \frac{jn^2}{W}.
$$

For each $j \leq M$, the $j$-th ordered candidate from the $I_n$ formula is $\lceil X_j \rceil - 1$ (if $j > E_n$, this candidate is already beyond the last strip), and the $j$-th element of $I_{n^2}$ is $\lfloor Y_j \rfloor$. Using $W = r(n+1)$, direct simplification gives

$$
X_j - Y_j = \frac{(j+1)n + 1}{r(n+1)} > 0.
$$

Thus $\lceil X_j \rceil - 1 = \lfloor Y_j \rfloor$ is equivalent to the fractional part of $jn/r$ being large enough to bridge the gap between $Y_j$ and $X_j$. The upper endpoint condition is automatic because $(jn) \bmod r \leq r - 1$; the lower endpoint condition is

$$
(jn) \bmod r \geq \frac{jn}{n+1}.
$$

The left-hand side is an integer, so this is equivalent to the displayed ceiling inequality. Applying this equality for every $j = 1, \ldots, M$ is exactly $I_n = I_{n^2}$; a cardinality mismatch fails at the first unmatched ordered candidate.

**Remark 3.13 (Base-10 trigger-set conjecture).** In the base-10, $r = s$ subcase of Theorem 3.11 with $M \geq 1$ and $E_n \geq 1$, computations support the sharper predicate

$$
I_n = I_{n^2}
\qquad \Longleftrightarrow \qquad
r \nmid n.
$$

Equivalently, the Beatty inequality in Lemma 3.12 appears to collapse to its first obstruction under the substrate constraint $W = 10^{d-1} = r(n+1)$. This has been verified empirically for $b = 10$, $n \leq 5000$, $d \leq 14$, with zero exceptions. The conjecture is base-specific: at $b = 6$, the cell $(b, n, d) = (6, 23, 4)$ satisfies $r = s = 9$, $n^2 > W = 216 = r(n+1)$, and $r \nmid n$, but the inequality fails at $j = 2$. A proof of the base-10 conjecture would close this subcase to the one-line predicate $r \nmid n$; the conjecture is left open here.

## The cipher

For any `period` $\in [2, 2^{32} - 1]$ and any key, `bidder_block_at(ctx, ·)` is a stateless keyed bijection of $[0, \mathtt{period})$. *Bijection* — every output in $[0, \mathtt{period})$ occurs exactly once. *Stateless* — `at(i)` does not mutate `ctx` and does not require `at(0)`, $\ldots$, `at(i-1)` to have been called first. *Keyed* — identical key + period produce identical permutations across runs and machines. The backend is Speck32/64 in cycle-walking mode for `period` $\geq 2^{26}$ (Beaulieu et al. 2013; cycle-walking from Black & Rogaway 2002), with an unbalanced 8-round Feistel network for smaller `period` in the textbook PRF$\to$PRP construction (Luby & Rackoff 1988). The contract relied on throughout is bijection-hood, not PRP quality.

The contract has two consequences for prefix-mean variance, one exact and one measured. Whole-block sampling at $N = P$ inherits exactness from the substrate: for any bijection $\pi : [0, P) \to [0, P)$ and any $f$,

$$
\frac{1}{P} \sum_{i=0}^{P-1} f(\pi(i)/P) = \frac{1}{P} \sum_{k=0}^{P-1} f(k/P) = R(f, P),
$$

the left-endpoint Riemann sum, since $\{\pi(0), \ldots, \pi(P-1)\}$ is the same multiset as $\{0, \ldots, P-1\}$. The identity is bijection-trivial — any keyed permutation has it — and is the reason BIDDER's prefix-mean variance at $N = P$ is machine-$\varepsilon$. **Sub-endpoint sampling at $N < P$ is a different story.** The relevant baseline is the finite-population correction (FPC) variance for a uniformly random permutation:

$$
\frac{\sigma^2}{N} \cdot \frac{P - N}{P - 1}.
$$

`replication/m2_fpc_gap.py` measures the *realisation gap* — the ratio of BIDDER's empirical prefix-mean variance to ideal FPC — by computing $R$ and $\sigma^2$ on the grid $\{f(k/P) : 0 \leq k < P\}$, generating $2000$ keyed BIDDER permutations per cell, measuring prefix-mean variance about $R$, and dividing by ideal FPC. The integrand is $f(x) = \sin(\pi x)$. All cells in the panel below have $P < 2^{26}$ and therefore use the Feistel fallback.

| $P \backslash N$ | $0.10 \cdot P$ | $0.25 \cdot P$ | $0.50 \cdot P$ | $0.75 \cdot P$ | $0.90 \cdot P$ |
|---|---|---|---|---|---|
| 200   | 1.022 | 1.170  | 1.336  | 1.212  | 1.133  |
| 500   | 1.257 | 1.839  | 2.242  | 1.884  | 1.407  |
| 1000  | 0.106 | 0.116  | 0.171  | 0.209  | 0.184  |
| 2000  | 3.260 | 5.452  | 6.754  | 5.617  | 3.353  |
| 5000  | 7.482 | 13.330 | 16.984 | 13.588 | 8.025  |
| 10000 | 13.982 | 25.274 | 31.995 | 25.773 | 14.677 |

The Feistel fallback under-mixes by up to $\sim 32\times$ ideal FPC at the worst measured cell, $(P, N) = (10000, 5000)$. The gap is U-shaped in $N/P$, peaking near $N = P/2$ and tapering toward both endpoints. It also grows monotonically with $P$ at fixed $N/P$ (modulo the $P = 1000$ row), which is the wrong direction for an asymptotically-mixing construction; we read this as the small-domain Feistel running out of mixing budget — fixed 8 rounds — as the cipher's domain widens. The $P = 1000$ row reports ratios *below* 1, an anomaly we have not investigated; it is consistent with Feistel structure happening to align with $\sin(\pi x)$ on a period-1000 grid, but the present panel does not measure neighbouring $P$ values to confirm or rule that out. Treat the table as a load-bearing limitation, not as calibration noise: workloads using interior prefixes should fold the measured gap into the error budget, or substitute FF1 (below) when tighter FPC realisation matters.

**FF1 as alternative.** FF1 with AES (NIST SP 800-38G) is a keyed bijection on the same domain with a cryptographic PRP objective. Run through the same Python wrapper on the same cells, FF1 lands at ratio $\sim 0.92$ on $(P, N) \in \{(2000, 1000), (10000, 5000)\}$ — sampling-consistent with the ideal FPC — at $\sim 19$–$29\times$ higher per-call cost than BIDDER's Feistel fallback. The choice between backends is concrete: if sub-endpoint variance is load-bearing and per-call cost is not, FF1 closes the gap; if the workload is whole-block, the gap does not apply and the choice reduces to per-call cost; if the workload is sub-endpoint and per-call cost matters at high $N$, the Feistel fallback's gap goes into the error budget and the throughput goes into the win column. The substrate's exactness is unaffected by either choice — the cipher's quality bends prefix-mean variance at $N < P$; it does not touch leading-digit counts.

## Sampling

The composition has two modes. In whole-block atom mode, choose $P$ as an atom count certified by Theorem 3.5, Theorem 3.6, or Theorem 3.7. For each $i = 0, \ldots, N - 1$, the cipher returns $j_i \in [0, P)$, and Lemma 3.10 with $K = j_i + 1$ returns the $(j_i + 1)$-th $n$-prime atom. At $N = P$, this visits the certified block exactly once, so the block's leading-digit distribution is inherited exactly. In stratified mode, instantiate one keyed prefix per leading-digit stratum and choose the prefix length $N_j$ separately in each stratum; this is the mode for exact leading-digit counts at $N < P$. Three worked examples follow.

### Uniform-leading-digit reference for Benford tests

A practitioner running a leading-digit conformity test — forensic accounting, election forensics, dataset-integrity audit — sometimes needs a uniform-leading-digit control rather than a sample from Benford's logarithmic law. The natural baseline is enumeration: list the atoms of $B_{b,d}$ (or $n$-prime atoms when $n^2 \mid b^{d-1}$), group by leading digit, hand the detector a deterministic block. For order-independent statistics — Pearson chi-squared, Kolmogorov–Smirnov, anything that consumes the multiset — enumeration suffices and BIDDER adds nothing of substance: the substrate alone delivers exact per-digit counts. The case for BIDDER is *order-dependent* detectors: sequential tests, online stopping rules, change-point monitors, anything that reads the stream and reports along the way. These need an exactly-uniform reference *plus* an order that does not leak the lexicographic magnitude structure of enumeration *plus* reproducibility across runs. BIDDER's keyed bijection over the certified block delivers the combination: exact uniformity (from the substrate), key-randomized order (decoupled from lexicographic structure), and reproducibility across machines and runs (from the key).

The chi-squared panel demonstrates the substrate baseline that both BIDDER and bare enumeration inherit. `replication/use_case_02_benford_null.py` reports Pearson chi-squared exactly $0.0000$ on a five-cell panel — integer-level $(b, d) \in \{(10, 3), (10, 4), (10, 5), (8, 5), (16, 4)\}$ and sieved $n$-prime $(b, n, d) \in \{(10, 2, 3), (10, 2, 4), (10, 2, 5), (8, 2, 5), (16, 2, 4)\}$. At $(b, n, d) = (10, 2, 4)$ the substrate yields $2{,}250$ $n$-prime atoms in $[1000, 9999]$ with exactly $250$ per leading digit (the smooth-regime count $b^{d-1}(n-1)/n^2$). The i.i.d.-uniform comparator across $1000$ trials per cell reports chi-squared distributed as $\chi^2(b-2)$ — empirical means $7.83$, $8.07$, $7.98$ at $b = 10$ (theoretical $b - 2 = 8$), $6.07$ at $b = 8$ (theoretical $6$), $14.00$ at $b = 16$ (theoretical $14$); standard deviations track $\sqrt{2(b-2)}$ — which is the per-replicate sampling noise a calibration against i.i.d. inherits and that the substrate (with or without BIDDER's shuffle) eliminates.

### Stratified survey design with exact leading-digit strata

In audit sampling over account IDs, invoice magnitudes, or registry blocks, leading digit is sometimes a mandated reporting stratum: regulators ask for sample composition by leading digit, or the workflow downstream estimates a ratio per leading-digit class. A survey designer drawing a sample of size $N_{\text{total}}$ from such a finite population indexed by the digit-class block $B_{b,d}$ wants strata defined by leading digit. The natural baseline is per-stratum simple random sampling without replacement — one `numpy.random.choice(stratum, N_j, replace=False)` per leading-digit stratum — which gives exact stratum sizes by construction. Exact-counts is therefore not BIDDER's differentiator. The differentiators are two: (a) streaming access without materializing the $b^{d-1}$-element stratum or the sample's index array, useful when the stratum is large (e.g., $b = 10$, $d = 9$ gives $10^8$ atoms per stratum) or when $N_j$ approaches $b^{d-1}$ and SRSWOR routines degrade; and (b) keyed reproducibility — two parties holding the same key reproduce the same sample across machines, RNG versions, and platforms without exchanging the sample or the population indexing, which is the operational requirement for audit chain-of-custody. Theorem 3.4 partitions $B_{b,d}$ exactly into $b-1$ leading-digit strata of size $b^{d-1}$, and a keyed bijection of $[0, b^{d-1})$ per stratum yields a streaming reproducible prefix sample of any size $N_j \leq b^{d-1}$.

`replication/use_case_01_stratified_survey.py` exercises the construction at $(b, d) = (10, 4)$ across nine strata and $\alpha \in \{0.1, 0.5, 1.0\}$ (100, 500, 1000 per stratum, $N_{\text{total}} \in \{900, 4500, 9000\}$): per-stratum counts are exactly $N_j = \lfloor \alpha \cdot 1000 \rfloor$ at every cell. The included i.i.d.-then-post-stratify comparator — `Binomial(N_{\text{total}}, 1/(b-1))` per stratum, the deviation a designer accepts when they reach for the default i.i.d. routine and fix realised sizes after the fact — reports 99th-percentile maximum stratum deviation across 1000 trials growing from 31 ($\alpha = 0.1$) to 97 ($\alpha = 1.0$). Per-stratum SRSWOR avoids that deviation; BIDDER avoids the deviation, the materialization, and the seed-versus-key reproducibility problem in one construction.

### Monte Carlo with known endpoint and measured FPC realisation gap

Monte Carlo uses whole-block mode on the finite population $[0, P)$: the estimator is the prefix mean of $f(\pi(i)/P)$ for a keyed bijection $\pi$. The natural baseline is `numpy.random.permutation(P)` — exact FPC at every $N$, but it materializes an array of size $P$. The endpoint identity (substrate-free, bijection-trivial) and the realisation gap from the cipher section are the load-bearing facts on the BIDDER side.

At $P = 2000$ and $f(x) = \sin(\pi x)$, `replication/use_case_06_variance_mc.py` reports BIDDER variance at $N = P$ of $6.15 \times 10^{-31}$ (machine-$\varepsilon$; floating-point round-off in the sum), ideal-FPC variance $0$ exactly, and i.i.d.-with-replacement variance $\sigma^2/P \approx 4.7 \times 10^{-5}$ (never zero). For interior prefixes, the measured gap peaks at ratio $7.17$ at $N = P/2 = 1000$ and tapers toward the endpoints. The four options sort cleanly: i.i.d. with replacement never gets the FPC; `numpy.random.permutation` gets the ideal FPC but materializes (impossible for $P$ above $\sim 10^9$ on a workstation, awkward well below that); BIDDER streams without materialization, exact at the endpoint and within the measured gap at sub-endpoint; FF1 closes BIDDER's gap to ratio $\sim 0.92$ at $\sim 19$–$29\times$ higher per-call cost. The BIDDER niche is whole-block at large $P$ — where the realisation gap does not apply and materialization is the binding constraint — or sub-endpoint at any $P$ where the gap fits the error budget.

## Related work

Four neighbours place BIDDER: PRNGs from normal numbers, quasi-Monte Carlo, exact ranged-integer generation, and format-preserving encryption. Each matches one part of the construction but not the whole finite-population contract.

The PRNG-from-normal-numbers construction (Bailey & Crandall 2002; Bailey 2004) builds a pseudorandom number generator from the digits of Stoneham-class normal numbers $\alpha_{b,c} = \sum_{n=0}^{\infty} 1/(c^n b^{c^n})$. The $K$-th base-$b$ digit of $\alpha_{b,c}$ can be extracted via BBP-style formulas in $O(\log K)$ work, without computing the prefix. The result is a deterministic, reproducible, random-access digit stream whose equidistribution is guaranteed asymptotically — the underlying Stoneham constant is provably normal in base $b$. The kinship with BIDDER is real: both deliver random-access, deterministic, low-per-access-cost sequences with mathematical backing on their distribution. A reader meeting Bailey–Crandall and BIDDER side by side could reasonably ask why BIDDER is more than a re-engineering of the Stoneham construction.

The differences are structural, not engineering. **Single stream vs. keyed family.** Bailey–Crandall produces one sequence per $(b, c)$ Stoneham pair; to get a different sequence, you change the constant. BIDDER's cipher is keyed: the substrate certifies a single block of $P$ atoms, and the cipher key selects among $2^{|\mathit{key}|}$ permutations of that block. **Asymptotic equidistribution vs. exact finite-block counts.** Bailey–Crandall's distributional guarantee is asymptotic — the digits equidistribute in the limit, with finite-$N$ discrepancy that approaches zero. BIDDER's substrate (Theorems 3.5–3.7) gives exact per-leading-digit counts at every finite $N$ matching the regime: at $(b, n, d) = (10, 2, 4)$ every leading digit gets exactly $250$ atoms in $[1000, 9999]$, not "approaches $250$ as $N$ grows." **Digit stream vs. finite-set bijection.** Bailey–Crandall outputs a digit stream — an infinite sequence over $\{0, \ldots, b-1\}$. BIDDER outputs a bijection of a finite set $[0, P)$, with every value visited exactly once at $N = P$. **Provable-normality theorem vs. counting argument.** Bailey–Crandall's correctness rests on the deep number-theoretic result that the Stoneham constant is normal in base $b$. BIDDER's substrate is a counting theorem: divmod arithmetic on multiples of $n$ and $n^2$ in $B_{b,d}$. The two tools answer different questions on different mathematical foundations.

Sobol' and the broader quasi-Monte Carlo literature (Halton 1960; Sobol' 1967; Niederreiter 1992; Owen 1995; Dick & Pillichshammer 2010) construct low-discrepancy sequences in $[0, 1]^d$ with star discrepancy $O((\log N)^d / N)$ asymptotically — sequences engineered to be more uniform than i.i.d. samples. Two differences place BIDDER. **Low-discrepancy vs. exact distribution.** QMC's $O((\log N)^d / N)$ is an asymptotic discrepancy bound; the sequences are approximately uniform, with discrepancy that shrinks as $N$ grows. BIDDER's substrate gives exact per-leading-digit counts at finite $N$ in the certified regimes, and the endpoint identity is a finite-set multiset identity rather than a discrepancy estimate. **Continuous cube vs. discrete blocks.** QMC operates in $[0, 1]^d$; BIDDER operates over discrete integer blocks $B_{b,d} = [b^{d-1}, b^d - 1]$ with leading-digit structure. The objects are different in kind: QMC produces low-discrepancy point sets in continuous high-dimensional spaces, where the leading-digit structure has no analogue and exact-uniform counts on integer blocks are not a meaningful target.

Exact ranged-integer generation (Lemire 2019; Saad et al. 2020) solves the one-draw problem: map random bits to an unbiased draw from $[0, s)$ or from a discrete distribution, usually with rejection or approximation guarantees. That is the right primitive for i.i.d. sampling with replacement. BIDDER fixes a finite population and returns a keyed ordering of it. The difference shows up at the endpoint: an exact ranged-integer sampler can be unbiased on every draw and still repeat values; a bijection visits every value exactly once.

Format-preserving encryption is the closest cipher-level substitute, and the comparison deserves the same structural treatment as Bailey–Crandall. FF1 and FF3-1 in NIST SP 800-38G give keyed bijections on arbitrary finite domains using AES; the cipher section above already shows that FF1 lands at FPC ratio $\sim 0.92$ on cells where BIDDER's Feistel fallback ranges from 1 to 32. The right comparison is not which tool subsumes the other but which dominates in which regime. Five differences place them.

**Backend cipher.** FF1 builds on AES, with decades of cryptanalysis and a PRP-quality argument behind it. BIDDER uses Speck32/64 (cycle-walking, $P \geq 2^{26}$) and an unbalanced 8-round Feistel (smaller $P$); the contract relied on is bijection-hood, and no PRP claim is made. **Domain handling.** FF1 supports arbitrary finite domains via radix-$r$ encoding; BIDDER supports $[0, P)$ for $P \in [2, 2^{32} - 1]$ via cycle-walking on the Speck path and direct construction on the Feistel path. **Sub-endpoint mixing.** FF1's measured FPC realisation is effectively ideal ($\sim 0.92$); BIDDER's Feistel fallback is not, with the gap growing in $P$ at fixed $N/P$ as the cipher's domain widens. **Per-call cost.** On the measured cells, FF1 costs $\sim 19$–$29\times$ more per call than BIDDER's Feistel fallback through the same Python wrapper. **Standards posture.** FF1 is NIST standards-track; BIDDER is dependency-free C, deployable wherever a build of `bidder_root.h` will go.

The pick: FF1 dominates when sub-endpoint prefix-mean variance is load-bearing and per-call cost is not. BIDDER's Feistel fallback dominates when the workload is whole-block (where the realisation gap does not apply); when per-call cost matters at high $N$ and the FPC gap is tolerable; or when AES / NIST dependencies are not available in the deployment target. In whole-block mode both backends inherit the substrate's exact leading-digit counts; that part of the construction is independent of the cipher choice.

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

**Python surface.** The replication archive uses a small Python wrapper with two constructors:

```
import bidder

block = bidder.cipher(2250, b"paper-key")
j = block.at(0)

atoms = bidder.sawtooth(2, 2250)
x = atoms.at(j)
```

Both returned objects support `.at(i)`, `len(...)`, and iteration. The C API is the stable surface; the Python layer is for tests, measurements, and examples.

**Build and replication.** At the repository root, `make` builds the shared library. The JSS replication archive lives in `paper/bidder-stat/`: `make venv` installs pinned Python dependencies, `make build` compiles the C kernel, `make test` runs the Python, C-wrapper, and theory tests, and `make replicate` rebuilds the measurements. The replication outputs cover the cycle-walking decision sweep, the realisation-gap grid, the comparator throughput panel, the wrapper / kernel performance taxonomy, the FF1 / AES comparator measurement, and the worked use-case scripts (`replication/use_case_*.py`).

## Tests

Eleven test files in `tests/` exercise three concerns: tests of the theory, tests of the artifact, and tests of the theory via the artifact. `make test` runs the lot on a clean checkout (`paper/measurements/e4_smoke.md`).

### Tests of the theory

Three files in `tests/theory/`: `test_riemann_property.py` (the endpoint identity at $N = P$, exact equality, machine-$\varepsilon$), `test_quadrature_rates.py` (Euler–Maclaurin convergence rates for $f = x$, $\sin(\pi x)$, $x^2(1-x)^2$, step), and `test_fpc_shape.py` (the realisation-gap measurement at $N < P$). These check the structural and statistical claims about the cipher independently of any specific BIDDER backend.

### Tests of the artifact

Six files in `tests/`: `test_api.py`, `test_bidder.py`, `test_bidder_block.py`, `test_bidder_root.py`, `test_sawtooth.py`, `test_speck.py`. These exercise the Python wrappers against the C kernel and the pure-Python oracle, plus property tests (bijection-hood at small $P$, Speck round-trip equality, sawtooth monotonicity). The implementation includes the published Beaulieu et al. Appendix C test vectors as inline checks in `test_speck.py` and the corresponding C test, so a reviewer can run those vectors against the implementation independently of any of BIDDER's other code.

### Tests of the theory via the artifact

`tests/test_acm_core.py` verifies the implementation-backed substrate results through Lemma 3.10. The proof-lift checks for Theorem 3.11, Lemma 3.12, and Remark 3.13 live with the Diophantine experiments. The substrate proofs cover all valid parameters; the tests below cover the listed sweep (every triple in the sweep is checked exhaustively).

| result | checked object | test function or script | tested sweep |
|---|---|---|---|
| Theorem 3.4 (Integer block-uniformity) | (fact about $\mathbb{Z}$) | `test_block_boundary_*` | base 10, $d \in \{1, \ldots, 9\}$ |
| Theorem 3.5 (Smooth-sieved) | `bidder_sawtooth_at` | `test_block_uniformity_sieved_sufficient` | $b, n \in \{2, \ldots, 10\}$, $d \in \{1, \ldots, 5\}$ |
| Theorem 3.6 (Family E) | `bidder_sawtooth_at` | `test_block_uniformity_sieved_family_e` | $b \in \{2, \ldots, 10\}$, $d \in \{2, \ldots, 5\}$ |
| Theorem 3.7 (Generalised Family E) | `bidder_sawtooth_at` | `test_block_uniformity_sieved_generalised_family_e` | $b \in \{2, \ldots, 10\}$, $d \in \{2, \ldots, 5\}$, $q' \in \{2, \ldots, 50\}$, $m_{\min} \in \{1, \ldots, 100\}$ |
| Theorem 3.9 (Spread bound) | `bidder_sawtooth_at` | `test_block_uniformity_sieved_spread_bound` | $b, n \in \{2, \ldots, 10\}$, $d \in \{1, \ldots, 5\}$ |
| Lemma 3.10 (Closed-form indexing) | `bidder_sawtooth_at` | `test_at_matches_acm_n_primes` (oracle); `test_kth_prime_*` (closed-form vs enumeration) | sawtooth oracle: $n \in \{2, \ldots, 12\}$; closed-form: $n \in \{2, \ldots, 9999\}$ |
| Theorem 3.11 (Structural decomposition) | closed-form $I_n, I_{n^2}$ vs direct strip counts | `experiments/math/diophantus/structural_theorem.py` | $b = 10$, $n^2 > W$ sub-locus outside smooth and Family E, 1925 cells |
| Lemma 3.12 (Beatty reduction) | Beatty inequality vs non-empty case 1 of Theorem 3.11 | `experiments/math/diophantus/beatty_reduction.py` | $b = 10$, $r = s$, $n^2 > W$: 17 cells total, 11 with $M \geq 1$, $E_n \geq 1$ and 6 degenerate $M = 0$ cells outside the lemma guard |
| Remark 3.13 (Base-10 conjecture) | empirical conjecture scope | `experiments/math/diophantus/conjecture_probe.py`; `experiments/math/diophantus/conjecture_A_partial.py` | $b = 10$, $M \geq 1$, $n \leq 5000$, $d \leq 14$; partial obstruction check 40/40 |

## Conclusion

BIDDER combines three layers: a counting result for $n$-prime atoms on digit-class blocks (exact per-digit counts in certified regimes, spread $\leq 2$ universally, closed-form indexing); a keyed stateless bijection of $[0, P)$ for $P \in [2, 2^{32}-1]$; and a sampling layer that turns these into uniform-leading-digit controls, exact stratum sizes, and finite-population Monte Carlo. The exactness claims are counting claims; the endpoint identity is bijection-trivial; the sub-endpoint variance behavior is measured and reported as part of the error budget. One substrate subcase — the base-10, $r = s$, $n^2 > W$ regime with $M \geq 1$, $E_n \geq 1$ — reduces by Lemma 3.12 to a Beatty inequality that empirically collapses to $r \nmid n$ (Remark 3.13); a proof would enlarge the catalogue of certified regimes but is not load-bearing for what is implemented.
