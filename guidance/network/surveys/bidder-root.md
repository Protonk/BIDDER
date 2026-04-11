# BIDDER (root API)

source: [`BIDDER.md`](../../../BIDDER.md)  
cited in: [`COLLECTION.md` — The Generator](../../../COLLECTION.md#chapter-2-the-generator)  
last reviewed: 2026-04-10

---

**Bridges.** The two user-facing entry points — `bidder.cipher`
for a keyed permutation of `[0, P)`, and `bidder.sawtooth` for
the first `count` n-primes of monoid `nZ+` — to the math
layers that back each. The cipher path grounds in the `d = 1`
integer block (see [`api.md`](api.md)). The sawtooth path
grounds in the Hardy closed form (see
[`hardy-sidestep.md`](hardy-sidestep.md)). Both share the same
interface shape — `.at(i)`, `.period`/`.count`, iteration,
`repr` — so caller code can work with either, once the caller
has decided whether it wants a shuffle or an ascending
sequence.

**Presents.** Three layers for each entry point. English for
intent, Python for behavior (signatures and examples verified
by [`api-doc-examples.md`](api-doc-examples.md)), BQN for the
math-layer specification. For the cipher path BQN is the
integer-block form from [`block-uniformity.md`](block-uniformity.md).
For the sawtooth path BQN is `NthNPn2 ← {𝕨 × 1 + ((𝕨-1)|𝕩-1)
+ 𝕨 × ⌊(𝕩-1)÷𝕨-1}` from [`bqn-agent.md`](bqn-agent.md), the
one-line exact-math form of the Hardy closed form.

**Excludes.** Cipher internals (out of BQN scope per the
BQN-AGENT hard boundary), cipher periods `> 2^32 − 1`,
`n = 1` in the sawtooth path (the Hardy closed form requires
`n ≥ 2`), infinite sawtooth iteration, the running mean and
Champernowne real as derived properties. The "what is not yet
supported" table at the bottom of the doc is where the
anti-over-claim register is most visible at the API surface.
BIDDER is explicitly *not* a secret-generation tool, and the
root README carries that warning verbatim.

**See also.** [`api.md`](api.md) — the detailed cipher-path
reference. [`bidder-generator.md`](bidder-generator.md) — the
cipher design doc whose cap is inherited here.
[`hardy-sidestep.md`](hardy-sidestep.md) — the closed form the
sawtooth path rests on. [`block-uniformity.md`](block-uniformity.md)
— the theorem the cipher path rests on.
[`bqn-agent.md`](bqn-agent.md) — the canonical BQN names.
