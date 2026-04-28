# Foray briefs

Four latches. Each structured the same way. I'm sticking to what's visible in the docs you shared and not inventing what I haven't seen.

---

## Brief 1 — Copeland-Erdős upgrade

**Question.** Is the exact block-uniformity result in `core/BLOCK-UNIFORMITY.md` a strict refinement of Copeland-Erdős (1946) for ACM-Champernowne reals? If so, where does it sit in the equidistribution literature?

**Canonical refs.**
- A.H. Copeland and P. Erdős, "Note on normal numbers," Bull. AMS 52 (1946), 857–860. Density hypothesis: #{a_n ≤ N} > N^θ for every θ < 1.
- H. Davenport and P. Erdős, "Note on normal decimals," Canad. J. Math. 4 (1952), 58–63. The standard generalization.
- L. Kuipers and H. Niederreiter, *Uniform Distribution of Sequences* (1974). Reference text.
- Y. Bugeaud, *Distribution Modulo One and Diophantine Approximation*, Cambridge Tracts 193 (2012).

**Latch.** The integer-block lemma is exact at every digit-class boundary; Copeland-Erdős is asymptotic. n-primes have density ~(n−1)/n² which clears the N^θ hypothesis for every θ < 1, so CE applies and gives normality of C_b(n). The sharper structural claim is exact equidistribution at every block boundary under the smooth condition n²|b^(d-1), with the spread bound ≤ 2 covering the rest.

**First step.** Literature search for "exact equidistribution at block boundaries" and "discrepancy of Champernowne-type constants." Identify whether Niederreiter, Sárközy, Schiffer, or anyone in the 1970s–80s ED literature stated something at the structural strength of `BLOCK-UNIFORMITY.md`.

**"Probably nothing" signal.** A pre-2000 paper stating exact block uniformity for general Copeland-Erdős sequences would collapse the contribution to "we noticed this for ACMs."

**Reach goal.** A clean theorem of the form: "For sequences A satisfying [strengthened counting condition], the base-b Champernowne real has zero discrepancy at every digit-class boundary," with the smooth and Family E lemmas as instances.

---

## Brief 2 — Continued fractions of n-Champernowne reals

**Question.** Where do unusually large partial quotients of C_b(n) sit in the CF expansion, and do their loci track the n-sieve rather than the integer block boundaries that drive Mahler's argument for Champernowne's constant?

**Canonical refs.**
- K. Mahler, "Arithmetische Eigenschaften einer Klasse von Dezimalbrüchen," Proc. Akad. Wet. Amsterdam 40 (1937), 421–428. Transcendence of 0.123456789101112…, exploiting digit-block periodicity at integer powers of 10.
- Bugeaud (2012) again for the Diophantine framing.
- Anything by Adamczewski and Bugeaud on automatic sequences and irrationality measures of explicit constants.

**Latch.** `acm_n_primes` and `NthNPn2` give arbitrary-precision random access into the n-prime stream. SageMath's `continued_fraction` on a high-precision real built from a long n-Champernowne prefix (via `mpmath` or PARI `\p`) gives the CF expansion. Compute for n ∈ {2, 3, 4, 5, 6, 10} to ~5000 partial quotients, plot magnitude vs index, look for spike loci.

**First step.** A script that reads digits from `acm_n_primes` (the exact integer list — not `acm_champernowne_real`, which truncates at IEEE 754 precision), assembles them as an mpmath/PARI real to high precision, and runs CF. Output: indices where partial quotients exceed 10^4, parameterized by n.

**"Probably nothing" signal.** Spike loci uniformly distributed over the CF expansion with no n-correlated structure. Then the analysis is just Mahler's argument carried over.

**Reach goal.** Irrationality measure of C_b(n) as an explicit function of n, with the proof tracking sieve boundaries as the approximation-spike source. A small but real contribution to Diophantine analysis of explicit reals.

---

## Brief 3 — Erdős-Borwein E via divisor digit encoding

**Question.** The Erdős-Borwein constant E = Σ 1/(2^n − 1) = Σ d(n)/2^n has known irrationality (Erdős 1948); transcendence is open. Does a Champernowne-method encoding of d(n) yield a constant whose digit-statistical properties illuminate E's, or is the encoding analytically inert?

**Canonical refs.**
- P. Erdős, "On arithmetical properties of Lambert series," J. Indian Math. Soc. 12 (1948). Original irrationality.
- D. Borwein and J. Borwein papers on Lambert-series constants; specific citation needs verification.
- OEIS A000005 (d(n) sequence) and the entry for E's decimal expansion.
- Tao's blog has accessible expositions of the Erdős irrationality argument; find the relevant post.

**Latch.** Define E_d(b) := concatenation of d(1), d(2), d(3), … in base b, parsed as 0.d(1)d(2)…, with a separator scheme (variable-length encoding, or a base large enough to hold d(n) for the range of n you compute). Compute leading-digit distribution and compare to the bound from Erdős-Kac on ω(n); compute CF; run a Pearson χ² normality test on digit blocks.

**First step.** Pick base b ≥ 12 with a pair-counting separator, or a fixed-width binary encoding. Compute E_d(b) to high precision for n up to ~10^6 (the divisor function is cheap). Compare its statistics to E's binary expansion at the same precision.

**"Probably nothing" signal.** E_d(b) statistics are generic — Benford-flat with no n-structure, CF looks like a random real's. Then the encoding has no number-theoretic content.

**Reach goal.** "The Champernowne re-encoding of an arithmetic function f gives a real whose [property] is decidable by methods that don't apply to the original Lambert/Dirichlet-series form." Methodological contribution even if the result itself is small.

---

## Brief 4 — ACM-restricted multiplication table

**Question.** When (a, b) range over atoms of an ACM rather than over ℤ_{>1}, does the deficit exponent in Ford's multiplication-table asymptotic shift? For A_n = n-primes of nℤ⁺, define M_n(N) = |{a·b : a, b ∈ A_n, a·b ≤ N}|. Does M_n(N) ≍ N / Φ(N) with the same constants, shifted constants, or different growth?

**Canonical refs.**
- K. Ford, "The distribution of integers with a divisor in a given interval," Annals of Math. 168 (2008), 367–433. The Θ(N²/Φ(N)) result with c = 1 − (1+log log 2)/log 2.
- P. Erdős's first multiplication-table paper (1955); look up the exact venue.
- P. Meisner, "Erdős' multiplication table problem for function fields and symmetric groups," arXiv:1804.08483 (2018). Function-field analog.
- R. Brent, C. Pomerance, D. Purdum, J. Webster, "Algorithms for the multiplication table problem," arXiv:1908.04251 (2019). Has efficient algorithms — exact to N = 2^30, Monte Carlo to 2^(10^8).

**Latch.** A_n is given by `acm_n_primes`. Each a · b with a, b ∈ A_n equals n²·k₁·k₂ where k₁, k₂ are not divisible by n. So M_n(N) reduces to a count of distinct products k₁k₂ with k₁, k₂ ≤ √(N/n²) and n ∤ k₁, n ∤ k₂ — the Erdős multiplication-table problem on ℤ \ nℤ. The open question is whether this restriction shifts c.

**First step.** Adapt the BPPW Monte Carlo algorithm — sample pairs and count distinct products in a hash set. Run for n ∈ {2, 3, 5, 6, 10} and N up to 10^9 or wherever M_n(N) · Φ(N) / N visibly stabilizes. Plot the ratio across n.

**"Probably nothing" signal.** M_n(N) ~ (1 − 1/n)² · M(N) with the same Φ. Then residue-class restriction is uninteresting at the exponent level. Write the negative result up briefly and move on.

**Reach goal.** Either an exponent shift (genuinely new) or a clean invariance proof: residue-class restriction does not move c. Either outcome is paper-shaped, and the function-field analog (Meisner 2018) is the likeliest first toehold.

---

A note on ordering. If you want one to start tonight, Brief 2 has the lowest activation energy: it's a single Sage script, the answer is computable in a few hours, and you'll know within the first plot whether the spike loci correlate with the sieve. Brief 1 needs library access for the lit search. Brief 4 needs the Monte Carlo algorithm. Brief 3 is the most speculative and the most likely to come back empty.
