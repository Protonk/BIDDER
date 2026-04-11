# Walsh Spectrum

source: [`experiments/acm-champernowne/base2/forest/walsh/WALSH.md`](../../../experiments/acm-champernowne/base2/forest/walsh/WALSH.md)  
cited in: [`COLLECTION.md` — The Binary Frontier](../../../COLLECTION.md#chapter-4-the-binary-frontier)  
last reviewed: 2026-04-10

---

**Setup.** Monoids `n = 2..32`, about `2 × 10^6` bits per
monoid, non-overlapping 256-bit chunks (`k = 8`), transformed
via `scipy.linalg.hadamard(256)`. Per chunk, the Walsh
coefficient at subset `S` is
`W[S] = (1/2^k) Σ_x f(x) · (−1)^(|S ∩ x|)`. The statistic is
the mean squared power `P[s] = mean |W[s]|²` across chunks.
Robustness ladder: count ≥ 25, CV < 0.25, z ≥ 3.

**Headline.** **44 robust cells** survive the bar. **All 44
die under entry-order shuffle.** Entry order is the dominant
discriminator — whatever these cells encode, it depends on
the original concatenation order, not on the marginal
distribution of bit patterns. The 44 split into three
populations under length and `v₂(n)` synthetic controls: 9
reproducible from length sequence plus `v₂(n)`, 15 from
length sequence alone, 20 from neither. Tier-3 core (survives
phase averaging *and* alternative chunk sizes):
`{30, 246, 255}`. Cell 30 is the cleanest current example of
ACM-specific Walsh structure.

**Control.** Four layers. (1) Length-matched synthetic stream
with the same `d` distribution. (2) `v₂(n)`-preserving
synthetic. (3) Entry-order shuffle of the same n-primes. (4)
Phase sweep across 32 chunk offsets. The shuffle control is
the sharpest — it kills every robust cell, which is the
strongest single ordering-matters result in the repo.

**Open.** What does cell 30 encode? Boundary conditioning at
`k = 8` is degenerate (every 256-bit chunk already contains
many entry boundaries at `n ≤ 32`), so whether these cells
are boundary-driven or interior-driven is unresolved. The
obvious rerun is at `k = 4` or `k = 5`, where chunks are
short enough to separate boundary-straddling from interior
windows. The audit-trail-per-`npz` discipline the doc
establishes — every summary is checkable against the
underlying per-coefficient `.npz` file — is its own
distinctive contribution; an earlier summary that looked
clean had misled the authors until the per-coefficient array
was read directly.
