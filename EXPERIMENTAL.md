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

## Brief 4 (rewritten) — Multiplication table on M_n

> **STATUS (2026-04):** Brief 4 (h=2) has been executed empirically in
> `experiments/acm-flow/mult-table/`. The K=10⁸ ratio test
> (`h2_ratio_n1e8.py`) found `M_n(K) / M_Ford(K) → α_n = (n−1)/n`,
> i.e. the asymptotic deficit exponent is **Ford's c, unchanged**;
> there is no asymptotic c-shift. Finite-K convergence is slow and the
> functional form is not yet pinned (three live candidates remain;
> see `core/FINITE-RANK-EXPANSION.md` and `mult-table/H2-RATIO-RESULT.md`).
> The Λ_n-sign-gating story below was a pre-empirical framing; the
> finite-rank closed form `Q_n` (`core/Q-FORMULAS.md`) supersedes
> the Λ_n / antichain diagnostic as the local algebraic object.
> The (α′) analytic chunk — Ford-anatomy of `P(k ⊥ n | k ∈ Ford-image)`
> — is deferred.

**Reframe.** The original brief asked whether Ford's deficit exponent c shifts when (a, b) range over A_n. That's a question about the answer. The better question is about the structure: what is the right poset on M_n, and does the multiplication-table count factor through that poset? The Λ_n / antichain framing from the previous turn is upstream of this; this brief assumes you've done that diagnostic and want to know what the multiplication table looks like *given* whatever the Λ_n picture turned out to be.

**Question.** Define M_n(N) = |{a · b : a, b ∈ A_n, a · b ≤ N}|. Does M_n(N) follow Ford's Θ(N / Φ(N)) shape with the same constant c = 1 − (1+log log 2)/log 2, a shifted constant c(n), or a different growth law entirely? And — this is the new part — does the answer depend on whether Λ_n stays nonnegative on the relevant range, or is it independent of the flow story?

**Canonical refs.** Same as before. K. Ford, "The distribution of integers with a divisor in a given interval," Annals 168 (2008). Erdős's 1955 and 1960 papers. Meisner (arXiv:1804.08483) on the function-field analog. Brent-Pomerance-Purdum-Webster (arXiv:1908.04251) on algorithms — they have Monte Carlo code that scales to N ≈ 2^(10^8), and adapting it to count distinct products restricted to A_n is a small modification, not a reimplementation. Add: Koukoulopoulos (arXiv:1102.3236) on the generalized k-fold multiplication table, since the M_n version sits closer to a constrained k-fold table than to the bare 2-fold one.

**What changed.** Two things.

First, products in A_n × A_n have a clean reduction. Every element of A_n is n · k with n ∤ k. So a · b = n²·k₁·k₂ where k₁, k₂ are not divisible by n. The distinct-product count on A_n is therefore the distinct-product count of the *coprime-to-n* multiplication table, scaled by n². That changes the question from "is the residue restriction Ford-flat?" to "what does Ford-style anatomy look like inside a residue class?" — which has a literature (Tenenbaum, Koukoulopoulos) but isn't directly the multiplication-table problem.

Second, the Λ_n diagnostic from the previous turn determines whether the *poset* M_n supports flow certificates at all. The multiplication-table count is a function on this poset (it counts the codomain of the multiplication map A_n × A_n → M_n, restricted to a sub-level set). If Λ_n ≥ 0 in the regime you're testing, the count has a clean probabilistic interpretation as the size of the image of a Markov-style map. If Λ_n goes negative, the image has structure that the standard anatomy machinery doesn't see. So the result of brief 4 is *conditioned* on what brief 3-equivalent (the Λ_n sign-table) returns.

**Latch.** `acm_n_primes` gives you A_n directly. The BPPW Monte Carlo algorithm samples (i, j) pairs uniformly, computes ij, and counts distinct products via a hash set. Modification: sample (k₁, k₂) uniformly from {k ≤ √(N)/n : n ∤ k}, compute n²·k₁·k₂, hash. The reduction to the coprime-to-n table means you're really running BPPW on a sieved domain, which is a one-line change to their sampling step.

**First step.** Run BPPW-modified Monte Carlo for n ∈ {2, 3, 5, 6, 10}, N ∈ {10^6, 10^7, 10^8, 10^9}. For each (n, N), compute M_n(N) · Φ(N) / N and plot vs N. Three diagnostic shapes:

- *Flat across N at a constant that depends on n only.* Ford-flat with a residue-class prefactor; the deficit exponent c is invariant under residue restriction. Negative result, but a clean one — write it up briefly.

- *Drifts logarithmically.* The Φ in the denominator has the wrong shape; the true deficit for M_n has a different power of log log N, and you've found it numerically.

- *Drifts polynomially in log N.* The exponent c itself has shifted to some c(n). This would be a real result, and the function-field analog (Meisner) tells you where to look for the proof — Meisner's c shift in 𝔽_q[t] tracks q, and a shift in your case would track n similarly.

**"Probably nothing" signal.** Flat-with-prefactor across all tested n. Then the multiplication table doesn't see the M_n structure at all and the Λ_n / antichain story is the only research direction worth pursuing. This is the most likely outcome and isn't a waste — it tells you the multiplication table is anatomy-flat under residue restriction, which is itself a fact worth recording.

**Reach goal.** A theorem of the form M_n(N) ≍ N / Φ_n(N), with an explicit Φ_n that either matches Ford's Φ (the residue restriction is invisible) or differs in a way that's diagnostic of M_n's poset structure. The function-field analog gives the cleanest path to a proof if the numerics show a shift; the BPPW algorithm gives the cleanest path to the numerics regardless of which way it goes.

**Coupling to brief on Λ_n.** Don't run brief 4 before the Λ_n sign-table. If Λ_n goes negative for some n at small m, that locus may be visible in M_n(N) as a non-monotonicity in the prefactor — small effect, but if you're not looking for it you'll miss it. Conversely, if Λ_n ≥ 0 everywhere for some n, M_n(N) for that n should behave most like the Ford case, and divergence between Ford's predicted Φ and your measured ratio at that specific n is the cleanest evidence that the residue restriction is doing something.

**A note on tractability.** BPPW's Monte Carlo gives error scaling as 1/√(samples), and the deficit exponents you're trying to detect are small — c ≈ 0.086. To distinguish c = 0.086 from c = 0.10 in the prefactor, you need enough samples to resolve a factor of (log N)^0.014, which at N = 10^9 is about 1%. That's ~10^4 samples for 1% Monte Carlo error, which is cheap. So the experiment is genuinely feasible at the laptop scale; you don't need cluster time to see the answer if the answer exists.

---

A note on ordering. If you want one to start tonight, Brief 2 has the lowest activation energy: it's a single Sage script, the answer is computable in a few hours, and you'll know within the first plot whether the spike loci correlate with the sieve. Brief 1 needs library access for the lit search. Brief 4 needs the Monte Carlo algorithm. Brief 3 is the most speculative and the most likely to come back empty.
