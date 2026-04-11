# Block Uniformity

source: [`core/BLOCK-UNIFORMITY.md`](../../../core/BLOCK-UNIFORMITY.md)  
cited in: [`COLLECTION.md` — The Construction](../../../COLLECTION.md#chapter-1-the-construction)  
last reviewed: 2026-04-10

---

**Claim.** In base `b ≥ 2`, the integers in a complete digit class
`{b^(d−1), …, b^d − 1}` have leading base-`b` digits exactly
equidistributed over `{1, …, b − 1}`. Each digit appears as the
leading digit of exactly `b^(d−1)` integers. No error term, no
asymptotic. The sieved versions extend the same exact count to the
n-prime subset of the block under two sufficient families (the
*smooth family* `n² | b^(d−1)` and the disjoint *Family E*), and
the exact-uniformity locus is strictly broader than either
sufficient condition — see the unconditional `(4, 5, 5)` witness.

**Mechanism.** A one-paragraph counting argument. A d-digit base-b
integer has the form `d_1 d_2 … d_d` where `d_1 ∈ {1, …, b−1}` and
`d_2, …, d_d` range freely over `{0, …, b−1}`. For each choice of
`d_1` the remaining `d−1` positions give `b^(d−1)` integers, so
each of the `b−1` leading-digit classes has exactly the same
count. The sieved versions apply the same argument to
length-`b^(d−1)` strips that start at multiples of `n²` (smooth)
or that contain exactly one multiple of `n` (Family E), with a
spread bound `≤ 2` in the general case.

**Depends on.** Positional notation; the definition of n-primes
from [`acm-champernowne.md`](acm-champernowne.md) for the sieved
extensions. Nothing else upstream.

**Supports.** The exact-uniformity guarantee of the BIDDER
generator (via [`bidder-generator.md`](bidder-generator.md) and
[`bidder-root.md`](bidder-root.md)); the `1111`-per-digit count in
[`early-findings.md`](early-findings.md); the `d = 1` integer
block case that grounds [`api.md`](api.md); the n-prime BIDDER
variant that [`hardy-sidestep.md`](hardy-sidestep.md) would
supply the closed-form index for.

**Status.** Proved. The sieved-block exact-uniformity locus is
broader than the two sufficient families together — a
brute-force sweep over `b ≤ 12, d ≤ 5` finds 22,205 triples
outside both that still give exact uniformity, with `(4, 5, 5)`
pinned as the canonical witness. A closed-form characterization
of the full locus is open.
