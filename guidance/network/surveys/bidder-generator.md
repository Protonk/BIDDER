# generator/BIDDER.md — Cipher Design

source: [`generator/BIDDER.md`](../../../generator/BIDDER.md)  
cited in: [`COLLECTION.md` — The Generator](../../../COLLECTION.md#chapter-2-the-generator)  
last reviewed: 2026-04-10

---

**Bridges.** The cipher design to its mathematical foundation
and to its observed behavior. The discipline of the doc is in
its top-level section headings: *Motivation / Mathematical
foundation / Construction / Observed properties / Known
limitations / Open questions*. The "factors the problem
differently" framing is the architectural insight — an
algebraic substrate (the integer block `[b^(d-1), b^d − 1]`)
gives exact leading-digit uniformity by counting, and a keyed
permutation (Speck32/64 in cycle-walking mode, Feistel
fallback below) provides the disorder. Neither piece does the
other's job.

**Presents.** The *Proved / Measured / Not claimed* split that
is the distinctive editorial move of the repo. Proved: the
substrate is exact (via
[`block-uniformity.md`](block-uniformity.md)); the
permutation-invariance theorem gives `E_P = R` at full period
(via [`riemann-sum.md`](riemann-sum.md)); the root API is
stable. Measured: full-period digit counts exactly
`period / (b − 1)`; all `d` digit positions independently
uniform; SHA-256 rekeying with no detectable seam for
`d ≥ 3`; stratified sampling totalizing for smooth functions;
a red-team theory test front (see
[`red-team-theory.md`](red-team-theory.md)). Not claimed:
adversarial PRP properties (distinguishing advantage, key
independence beyond `E_P = R`, side-channel behavior); BIDDER
is explicitly *not* a secret-generation tool.

**Excludes.** Adversarial-grade PRP guarantees in this exact
composition — the PRP properties are inherited from Speck and
not independently verified for BIDDER. The Feistel fallback at
small block sizes has a measurable ~1.5–2.5× variance gap
against the FPC null at intermediate `N`, recorded as a
backend property and not an algebra failure. Spatial blue-noise
properties (a dithering negative result).

**See also.** [`block-uniformity.md`](block-uniformity.md) —
the substrate theorem.
[`riemann-sum.md`](riemann-sum.md) — the permutation-invariance
theorem at full period.
[`bidder-root.md`](bidder-root.md) — the root API this design
implements. [`api.md`](api.md) — the cipher-path reference.
[`generator-agents.md`](generator-agents.md) — the parity
rules that enforce C/Python byte-identical output.
[`early-findings.md`](early-findings.md) — the historical
source for the stratified, reseeding, and arithmetic
contamination observations.
