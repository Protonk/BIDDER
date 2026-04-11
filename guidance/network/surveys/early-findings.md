# Early Findings

source: [`sources/EARLY-FINDINGS.md`](../../../sources/EARLY-FINDINGS.md)  
cited in: [`COLLECTION.md` — The Construction](../../../COLLECTION.md#chapter-1-the-construction)  
last reviewed: 2026-04-10

---

**Status.** Historical first-findings doc. The seeds of
everything. Cited by every subsequent seed theorem as the
place where the open questions that drove the rest of the
repo came from.

**Current evidence.** Six findings, each of which became the
starting point of a later cluster. (1) **Exact uniformity.**
Over `n = 1..9999`, each leading digit 1–9 appears exactly
`1111` times as the leading digit of `C(n)`. Not
approximately — exactly. This is the empirical observation
that became the theorem in
[`block-uniformity.md`](block-uniformity.md). (2) **The
sawtooth and its range.** `C(n)` traces a sawtooth on
`[1.1, 2.0]` with teeth at powers of 10, slope `~10^{-d}` per
`d`-digit tooth, drop at decade boundaries. (3) **Running mean
convergence.** The running mean of `C(n)` approaches `31/20 =
1.55` from below — conjectured to never arrive. (4) **Multiplication
vs addition.** Multiplication converges to Benford in about
10 operations; addition never converges, producing the
rolling-shutter artifact that sweeps digits 1→9→1→… forever.
(5) **Crispness.** ACM sliding-window sums preserve phase
information that stochastic sources destroy via CLT —
*crispness = deterministic structure surviving under
addition*. (6) **The ε connection.** The sawtooth
`ln(C(n)) ~ ln(1 + m)` peaks at mantissa midpoint, which is
where numbers have the richest factorization structure, and
is the same function that later turns into the binary
identity of [`binary.md`](binary.md).

**Depends on.** [`acm-champernowne.md`](acm-champernowne.md)
for the construction being probed.

**Open questions.** The doc closes with eight open questions,
several of which are still open: the running mean conjecture;
exact rate of convergence to Benford under multiplication;
closed form for the significand distribution under k-fold
multiplication; information-theoretic content of crispness;
BS(1,2) behavior under addition/multiplication mixing. The
historical value of the doc is in recording what the author
was surprised by *first* — the order in which the
construction's consequences became visible — and in anchoring
the provenance of nearly every later finding.
