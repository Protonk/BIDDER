# PRIOR-ART

Who else is in the room. Five neighbouring lines of work; the
combined picture at the bottom. Cites verified
(see "Verification notes" at the end).

---

## Bailey–Crandall–Borwein: PRNGs from normal numbers

The closest design-space neighbour. The genre move — use the digit
stream of a constructible normal real as a deterministic uniform
source — is theirs. Three to engage:

- Bailey, D. H., & Crandall, R. E. (2002). *Random Generators
  and Normal Numbers.* Experimental Mathematics, 11(4),
  527–546. b-normality for an uncountable class of explicit
  constants `Σ 1/(b^{m_i} c^{n_i})`.

- Bailey, D. H. (2004). *A Pseudo-Random Number Generator Based
  on Normal Numbers.* Lawrence Berkeley National Laboratory
  Technical Report LBNL-57489 (manuscript dated 11 Dec 2004). A
  working PRNG built on the specific Bailey–Crandall constant
  `α_{2,3} = Σ_{k≥1} 1/(3^k · 2^{3^k})`. The paper exhibits an
  explicit closed-form formula for the n-th binary digit,
  `x_n = (2^{n-3^m} · ⌊3^m/2⌋) mod 3^m / 3^m + ε` with `m` the
  largest power of 3 not exceeding `n` (and `|ε| < 10^{-30}`
  outside narrow windows around powers of 3). This is the
  structural parallel to BIDDER's Hardy `c_K = q·n + r + 1` —
  both deliver a closed-form digit-position map via one modular
  operation. The PRNG iterates `z_k = (2^{53} · z_{k-1}) mod
  3^{33}` with period `2·3^{32} ≈ 3.7 × 10^{15}`; the modulus is
  a power of three, deliberately chosen to avoid power-of-two
  stride pathologies in scientific codes. The "seed" is a
  starting position `a` in the digit stream of `α_{2,3}`, not a
  key; the output is a deterministic bit stream, not a
  permutation. Parallel-deterministic: each processor
  independently computes its starting `z_0` from the global
  index, and the collective sequence equals the single-processor
  sequence — the same property BIDDER's stateless
  `bidder_block_at(ctx, i)` provides for keyed bijections.

- Bailey, D. H., & Borwein, J. M. (2013). *Normal Numbers and
  Pseudorandom Generators.* In Bailey, D. H. et al. (eds.),
  Computational and Analytical Mathematics. Springer Proceedings
  in Mathematics & Statistics, vol. 50, pp. 1–18.

The clash. Theirs gives *asymptotic* b-normality — limiting
frequency `b^{-k}` for every length-`k` digit string — for digit
streams from constructible reals: Stoneham `α_{b,c}`, Korobov
`β_{b,c,d}`, and an uncountable `(b, c, m, n)`-PRNG class. Yours
gives *exact* per-block leading-digit uniformity (`b^{d-1}` per
digit on the complete digit-class block `B_{b,d}`) from
ACM-Champernowne, a sieved digit-concatenation construction in
the Champernowne / Erdős–Copeland line that Bailey & Crandall
explicitly situate in their landscape (Champernowne at p. 528,
Erdős–Copeland at p. 541). They have random access via BBP-style
digit extraction at `O(log² n)` bit-complexity from a single
fixed constant (p. 537); yours is keyed, with the key selecting
among permutations of `[0, P)`.

Bailey & Crandall raise BIDDER's question explicitly. Open
problem 5 (p. 544): *"Does polynomial-time (in log n) resolution
of the n-th digit for our `α_{b,c}` and similar constants give
rise to some kind of 'trap-door' function, as is relevant in
cryptographic applications? The idea here is that it is so very
easy to find a given digit even though the digits are 'random.'"*
BIDDER is one realisation of what they conjectured: substitute a
keyed cipher for the polynomial-time digit map, get a per-key
permutation of an exact-uniform-leading-digit substrate. Same
room, different substrate (sieved-Champernowne rather than
Stoneham / Korobov), and a keying layer they raised as a question
and we instantiate as a tool.

## Quasi-Monte Carlo, low-discrepancy sequences

The dominant community for "deterministic substitute for Monte
Carlo with a known error structure." Their guarantee is bounded
star discrepancy `O((log N)^d / N)`; yours is exact endpoint plus
FPC-shaped interior. Different bounds, same use case. The
"non-power-of-two" line has limited bite here because Halton has
always used coprime radices. The distinguishing pitch is
endpoint-exact at finite `N`, where QMC is asymptotic.

- Halton, J. H. (1960). *On the efficiency of certain quasi-random
  sequences of points in evaluating multi-dimensional integrals.*
  Numerische Mathematik, 2, 84–90.

- Sobol', I. M. (1967). *On the distribution of points in a cube
  and the approximate evaluation of integrals.* USSR Computational
  Mathematics and Mathematical Physics, 7(4), 86–112. (Russian
  original: Zh. Vychisl. Mat. Mat. Fiz., 7(4), 784–802.)

- Niederreiter, H. (1992). *Random Number Generation and
  Quasi-Monte Carlo Methods.* SIAM CBMS-NSF Regional Conference
  Series in Applied Mathematics, vol. 63. SIAM, Philadelphia.

- Owen, A. B. (1995). *Randomly Permuted (t,m,s)-Nets and
  (t,s)-Sequences.* In Niederreiter, H. & Shiue, P. J.-S. (eds.),
  Monte Carlo and Quasi-Monte Carlo Methods in Scientific
  Computing. Springer Lecture Notes in Statistics, vol. 106,
  pp. 299–317.

- Dick, J., & Pillichshammer, F. (2010). *Digital Nets and
  Sequences: Discrepancy Theory and Quasi-Monte Carlo
  Integration.* Cambridge University Press.

- Kirk, N., & Lemieux, C. (2024). *An improved Halton sequence
  for implementation in quasi-Monte Carlo methods.* In
  Proceedings of the 2024 Winter Simulation Conference.
  arXiv:2405.15799.

## Exact ranged-integer generation

The reflexive "but isn't this just X?" reach for most reviewers.
These are i.i.d. samplers, not deterministic permutations. The
point of contact is "exact uniformity over arbitrary domain"; the
difference is that BIDDER is a *bijection* that visits each value
once. Say so in one sentence.

- Lemire, D. (2019). *Fast Random Integer Generation in an
  Interval.* ACM Transactions on Modeling and Computer
  Simulation, 29(1), Article 3. (arXiv:1805.10941, May 2018.)
  Bias-free integer in `[0, s)` for any `s`. Adopted by Go's
  shuffle, the GNU and Microsoft C++ standard libraries, the
  Linux kernel, and the standard libraries of Swift, Julia, C#
  and Zig.

- Saad, F. A., Freer, C. E., Rinard, M. C., & Mansinghka, V. K.
  (2020). *Optimal Approximate Sampling from Discrete
  Probability Distributions.* Proceedings of the ACM on
  Programming Languages, 4(POPL), Article 36.

- Draper, T. L., & Saad, F. A. (2025). *Efficient Rejection
  Sampling in the Entropy-Optimal Range.* arXiv:2504.04267.

## Verifiable random functions, cryptographic sortition

The dominant audit story. Trust model is different — VRF gives a
non-interactive proof of correctness from a committed asymmetric
key; yours is symmetric, with verifiability of the *marginal* by
inspecting the algebra. A reviewer reading "auditable" will assume
VRF; head them off in one paragraph.

- Micali, S., Rabin, M., & Vadhan, S. (1999). *Verifiable Random
  Functions.* In Proceedings of the 40th Annual Symposium on
  Foundations of Computer Science (FOCS '99), pp. 120–130.

- Gilad, Y., Hemo, R., Micali, S., Vlachos, G., & Zeldovich, N.
  (2017). *Algorand: Scaling Byzantine Agreements for
  Cryptocurrencies.* In Proceedings of the 26th ACM Symposium on
  Operating Systems Principles (SOSP '17), pp. 51–68. Algorand
  sortition and its descendants in Cardano, Polkadot, Internet
  Computer.

## Benford goodness-of-fit

The trivial-null neighbours. They use uniform `1/(b−1)` as the
trivial null already. What they lack is an addressable streaming
realisation of that null at arbitrary offsets. That's a real but
small contribution — frame it as a computational instrument, not
a new distribution.

- Cerioli, A., & Perrotta, D. (2022). *On Characterizations and
  Tests of Benford's Law.* Journal of the American Statistical
  Association, 117(540), 1887–1903. (Online April 2021.)

- Lesperance, M., Reed, W. J., Stephens, M. A., Tsao, C., &
  Wilton, B. (2016). *Assessing Conformance with Benford's Law:
  Goodness-of-Fit Tests and Simultaneous Confidence Intervals.*
  PLoS ONE, 11(3), e0151235.

---

## The combined picture

Each of the five neighbours has done one of the things BIDDER
does. None has done all of them in the same object. That
intersection — keyed deterministic permutation of `[0, P)` for
arbitrary `P`, with marginal uniformity verifiable by inspecting
the algebra rather than by running test suites — is the niche.
Narrow on purpose. Worth saying that explicitly: the paper isn't
claiming a new theorem, it's claiming a small instrument that
occupies an empty cell in an existing table.

---

## Standing on (cipher provenance)

Different rhetorical register from the five neighbour-sections
above. Those are claims we stake out a niche against; these are
claims we *stand on*. The Speck-related-work paragraph in the
paper is short, narrow, and structurally separate: two or three
sentences, three or four citations. The brevity is the move — it
says the cipher isn't where the paper's argument lives. We do not
compare Speck to AES, do not argue Speck is better than
alternatives, and do not survey the lightweight-cipher landscape.
Any of those would read as a cipher-choice defense; a cipher-
choice defense would read as a cipher-design contribution claim,
which we are not making. The right posture is "we picked a
publicly studied PRP whose block size fits, and any equivalent
choice would serve."

### Specification (one sentence in the paper)

- Beaulieu, R., Treatman-Clark, S., Shors, D., Weeks, B., Smith,
  J., & Wingers, L. (2013). *The SIMON and SPECK Families of
  Lightweight Block Ciphers.* IACR Cryptology ePrint Archive
  Report 2013/404. The original spec; test vectors live in
  Appendix C.

- Beaulieu, R., Shors, D., Smith, J., Treatman-Clark, S., Weeks,
  B., & Wingers, L. (2017). *Notes on the Design and Analysis of
  SIMON and SPECK.* IACR Cryptology ePrint Archive Report
  2017/560. The NSA-followup post-publication design-and-analysis
  reference.

### Public cryptanalysis (one sentence in the paper; representative, not exhaustive)

- Dinur, I. (2014). *Improved Differential Cryptanalysis of
  Round-Reduced Speck.* SAC 2014. IACR Cryptology ePrint Archive
  Report 2014/320. Standard reach for differential cryptanalysis
  on Speck32/64.

- Song, L., Huang, Z., & Yang, Q. (2016). *Automatic Differential
  Analysis of ARX Block Ciphers with Application to SPECK and
  LEA.* IACR Cryptology ePrint Archive Report 2016/209. SAT/SMT-
  driven trail search; extends differential bounds further.

The paper isn't relying on a particular cryptanalytic bound; it
is relying on the fact that bounds exist and a reader can find
them.

### Feistel fallback (one sentence in the paper)

- Luby, M., & Rackoff, C. (1988). *How to Construct Pseudorandom
  Permutations from Pseudorandom Functions.* SIAM Journal on
  Computing, 17(2), 373–386. The original three-round PRF→PRP
  construction.

- Naor, M., & Reingold, O. (1999). *On the Construction of
  Pseudorandom Permutations: Luby–Rackoff Revisited.* Journal of
  Cryptology, 12(1), 29–66. Two Feistel rounds plus pairwise-
  independent wrappers; cleaner proof.

This is enough to say "this is a textbook construction with a
well-understood security model" without claiming new work on the
construction itself.

### Small-domain caveat (one clause in the paper)

- Durak, F. B., & Vaudenay, S. (2017). *Breaking the FF3 Format-
  Preserving Encryption Standard over Small Domains.* CRYPTO
  2017. The benchmark "small-domain Feistel can fail" result.

The paper acknowledges the caveat in one clause, then notes that
BIDDER's correctness claim does not route through the fallback's
PRP advantage — the substrate's algebra gives the marginal
regardless.

### Audit-side move (one sentence in the paper)

`speck.py` carries the published Appendix C test vectors verbatim;
the corresponding C tests check the same vectors. A reviewer can
run those vectors against the implementation independently of any
of BIDDER's other code. The line in the paper is something like
*"the implementation includes the published Appendix C test
vectors as inline checks,"* and it does more work than a paragraph
of cipher justification would.

---

## Verification notes

All sixteen citations cross-checked against publisher records,
arXiv, and OSTI. Three corrections from the inbound brief:

- *Bailey LBNL technical report:* dated **2004** (LBNL-57489), not
  2010. The "avoids power-of-two stride pathologies" claim is in
  the report's abstract.
- *Cerioli "et al." 2021:* the JASA paper has two authors
  (**Cerioli & Perrotta**), not three or more. Online publication
  was April 2021; print publication is JASA Vol. 117 No. 540
  (2022).
- *"Halton–Lemieux 2024":* the recent Halton-improvement paper is
  by **Kirk & Lemieux**, 2024 (arXiv:2405.15799). Lemieux's 2009
  Springer textbook *Monte Carlo and Quasi-Monte Carlo Sampling*
  (Springer Series in Statistics) is a separate work and is not
  cited above.

Cipher-line cites cross-checked against IACR ePrint, Springer,
SIAM, and Journal of Cryptology records. One drift to log:

- *"Beaulieu et al. ToSC 2015":* IACR Transactions on Symmetric
  Cryptology began publishing in 2016, so a 2015 Beaulieu ToSC
  paper does not exist. The intended NSA-followup canonical is
  **ePrint 2017/560**, *"Notes on the Design and Analysis of
  SIMON and SPECK"* (same authors); cited above as the design-
  and-analysis follow-up to the 2013/404 spec.
