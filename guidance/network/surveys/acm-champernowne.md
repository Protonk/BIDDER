# ACM-Champernowne

source: [`core/ACM-CHAMPERNOWNE.md`](../../../core/ACM-CHAMPERNOWNE.md)  
cited in: [`COLLECTION.md` — The Construction](../../../COLLECTION.md#chapter-1-the-construction)  
last reviewed: 2026-04-10

---

**Claim.** For each `n ≥ 2`, the multiplicative monoid
`nZ+ = {n, 2n, 3n, …}` has irreducible elements (the *n-primes*)
that are exactly the multiples of `n` not divisible by `n²`:
`n · k` is n-prime iff `n ∤ k`. The first n-composite is always
`n²`, so `n²` is the resolution threshold of n-primality. The
n-Champernowne real `C_b(n)` is built by concatenating the first
`K` n-primes of monoid `n` in base `b` after "1.", giving a
scalar that packs both the number-theoretic content of the
monoid and the typographic cost of its elements. For `n = 1` the
construction recovers the ordinary primes and is a separate
branch of the codebase.

**Mechanism.** `n · k` factors as `n · a · n · b = n² · ab` in
the monoid only when `k = a · b · n`, i.e. when `n | k`. So the
n-primes are exactly `{n · k : n ∤ k}`, listed in ascending
order. For `n ≥ 2` the first `n − 1` n-primes are
`n, 2n, …, (n − 1) · n`, all strictly below `n²`; the value `n²`
itself is the first element divisible by `n²` and is the first
n-composite.

**Depends on.** Standard number theory. The Arithmetic
Congruence Monoid (ACM) literature the doc cites — Hilbert's
`M_{1,4}` counterexample to unique factorization, James & Niven
(1954), Geroldinger & Halter-Koch (2004), Baginski & Chapman.

**Supports.** Everything else in the repo. Every other doc
borrows this doc's vocabulary (n-primality, square boundary,
n-Champernowne real, monoid `nZ+`). The four foundational
theorems — [`block-uniformity.md`](block-uniformity.md),
[`hardy-sidestep.md`](hardy-sidestep.md),
[`riemann-sum.md`](riemann-sum.md),
[`abductive-key.md`](abductive-key.md) — each cite this as the
construction they reason about.

**Status.** Definitional, with a "What Is Possible Now" section
at the end that catalogues the consequences documented
elsewhere: exact first-digit uniformity (not Benford), the
multiplication-vs-addition asymmetry, the ε correction
connection, compositeness pressure as a base-independent
scalar. The construction is small; its consequences are what
the rest of the repo is about.
