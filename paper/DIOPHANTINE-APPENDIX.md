## Appendix A: The spread-zero locus and an open base-10 problem

Theorem 3.10 bounds the spread of counts of $A_n \cap B_{b,d}$ across leading-digit strips by 2. When the spread equals zero, a finer analysis applies. This appendix carries that analysis as far as we have it: a structural decomposition of the spread-zero locus when $n^2 > W$ and outside Family E (Theorem A.1); a Beatty-pair coincidence reduction of one of its three cases (Lemma A.2); and an open problem on the base-10 form of A.2's inequality (A.3).

**Theorem A.1 (Structural decomposition of spread-zero, $n^2 > W$).** Let $W = b^{d-1}$ and suppose $n^2 > W$, outside the Family E regime of Theorem 3.7. For $k \in \{1, \ldots, b-1\}$, let $C_m(k)$ be the number of multiples of $m$ in the strip $S_k$. Write $C_n(k) = \lfloor W/n \rfloor + e_n(k)$, with $e_n(k) \in \{0, 1\}$, and set $r = W \bmod n$, $E_n = \#\{k : e_n(k) = 1\}$, and $M = \lfloor (bW - 1)/n^2 \rfloor$. Define

$$
I_n =
\begin{cases}
\{\lceil (jn + 1)/r \rceil - 1 : j = 1, \ldots, E_n\}, & r \geq 1, \\
\emptyset, & r = 0,
\end{cases}
\qquad
I_{n^2} = \{\lfloor jn^2/W \rfloor : j = 1, \ldots, M\}.
$$

Both are subsets of $\{1, \ldots, b-1\}$. The counts of $A_n \cap B_{b,d}$ across leading-digit strips have spread $= 0$ if and only if exactly one of the following three constant-difference cases holds:

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

The count of elements of $A_n$ in strip $S_k$ is

$$
A_k = C_n(k) - C_{n^2}(k)
    = \lfloor W/n \rfloor + (e_n(k) - e_{n^2}(k)).
$$

The first term is constant in $k$, so spread $= 0$ is equivalent to $e_n(k) - e_{n^2}(k)$ being constant. Since both excess functions take values in $\{0, 1\}$, the constant difference can only be $0$, $+1$, or $-1$, giving cases 1, 3, and 2 respectively. These cases are exhaustive.

**Lemma A.2 (Beatty-pair coincidence reduction).** In addition to the hypotheses of Theorem A.1, suppose $r = s$, where $s = \lfloor W/n \rfloor \bmod n$. Then $W = r(n+1)$. Assume also $M \geq 1$ and $E_n \geq 1$, so $I_n$ and $I_{n^2}$ are non-empty. Case 1 of Theorem A.1 holds if and only if

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

**A.3 (Open problem: base-10 form of Lemma A.2).** Specialize Lemma A.2 to $b = 10$. Across $b = 10$, $n \leq 5000$, $d \leq 14$ — every $(n, d)$ pair satisfying the hypotheses of A.2 — the equivalence

$$
I_n = I_{n^2} \qquad \Longleftrightarrow \qquad r \nmid n
$$

was checked computationally and held without exception. Whether the equivalence extends to all $(n, d)$ in the $b = 10$ specialization of A.2 is open.

The equivalence is base-specific. At $b = 6$, the cell $(b, n, d) = (6, 23, 4)$ satisfies $r = s = 9$, $n^2 > W = 216 = r(n+1)$, and $r \nmid n$, but the inequality of Lemma A.2 fails at $j = 2$. A proof of the $b = 10$ form would reduce the corresponding spread-zero subcase to the one-line predicate $r \nmid n$. A counterexample at $b = 10$ would extend the $b = 6$ phenomenon into the base-10 specialization at scope beyond what is verified here.
