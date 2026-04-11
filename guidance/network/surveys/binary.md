# Binary Champernowne of ACMs

source: [`experiments/acm-champernowne/base2/BINARY.md`](../../../experiments/acm-champernowne/base2/BINARY.md)  
cited in: [`COLLECTION.md` — The Binary Frontier](../../../COLLECTION.md#chapter-4-the-binary-frontier)  
last reviewed: 2026-04-10

---

**Status.** Exploratory theorem note. The verdict is explicit:
base 2 is *not a better generator; a better lens for the pure
mathematics*. The doc is the chapter's vocabulary anchor and
the rest of the base-2 subtree depends on the terms it
establishes.

**Current evidence.** Four structural moves, organized by
"what collapses / sharpens / emerges / is conjectured." The
leading-digit uniformity that drives
[`bidder-generator.md`](bidder-generator.md) *collapses* in
base 2: the alphabet `{1}` is trivially uniform and destroys
information under the projection that is BIDDER's distinctive
step. The sawtooth-vs-ε connection *sharpens* to an identity:
`log₂(C₂(n))` is not an analog of the SlideRule `ε(m) =
log₂(1 + m) − m` function, it *is* that function exactly.
The bit-balance of an n-prime stream *emerges* as a closed
form parameterized by `v₂(entry)` (see
[`hamming-bookkeeping.md`](hamming-bookkeeping.md)). And the
finite-state conjecture (see
[`finite-recurrence.md`](finite-recurrence.md)) is the
structural boundary the measurement cluster lives inside. RLE
becomes a 2-adic fingerprint rather than a compression trick
because every n-prime has at least `v₂(n)` trailing zeros.

**Depends on.** [`acm-champernowne.md`](acm-champernowne.md)
for the n-prime construction and
[`block-uniformity.md`](block-uniformity.md) for the
counting argument that collapses.

**Open questions.** The nine expeditions in the
`forest/MALLORN-SEED.md` index, of which several have been
built: the Walsh 44-cell family (see
[`walsh.md`](walsh.md)), the detrended RDS residual (see
[`detrended-rds.md`](detrended-rds.md)), the valuation
forest. The deeper question is whether the base-2 results
generalize back to integer-level structure claims, or whether
they live entirely inside the RLE / v₂ / Walsh world and
never cross back.
