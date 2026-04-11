# core/API.md — Cipher-Path API

source: [`core/API.md`](../../../core/API.md)  
cited in: [`COLLECTION.md` — The Generator](../../../COLLECTION.md#chapter-2-the-generator)  
last reviewed: 2026-04-10

---

**Bridges.** The user-facing cipher-path API to the `d = 1`
degenerate case of the block-uniformity lemma. With base
`b = P + 1` and digit class `d = 1`, the integer block in
BQN is `b⋆d-1 + ↕ (b-1)×b⋆d-1`, which evaluates to `1 + ↕ P`.
The `BidderBlock` adapter shifts the output range from
`{1, …, P}` to `[0, P)`, so externally the set being permuted
is `↕ P`. The keyed permutation picks one specific bijection
from the symmetric group on that set.

**Presents.** Three layers for each method: English (what the
function does, in user terms), Python (actual signature plus a
runnable example, verified by
[`api-doc-examples.md`](api-doc-examples.md) as an assertion
before execution), and BQN (the math-layer operator the method
corresponds to — `⊑` for `at(i)`, `≠` for `len`, etc.). The
cipher itself is out of scope for BQN per
[`bqn-agent.md`](bqn-agent.md)'s hard boundary.

**Excludes.** The v1 API explicitly does not: certify
leading-digit uniformity in any base, search a `(b, n, d)`
catalogue, compose blocks, or accept periods larger than
`2^32 − 1`. The `UnsupportedPeriodError` discipline makes the
exclusion visible: the cipher backend cap is a property of the
cipher, not of the math, and the exception exists so callers
can distinguish "the math is fine, the backend can't handle
it" from "the request was invalid." The math layer of
[`block-uniformity.md`](block-uniformity.md) and the closed
form of [`hardy-sidestep.md`](hardy-sidestep.md) work for any
`P` and any `(n, K)`; the v1 API just doesn't visit that
space yet.

**See also.** [`block-uniformity.md`](block-uniformity.md) —
the `d = 1` case this API sits on.
[`hardy-sidestep.md`](hardy-sidestep.md) — the closed form for
the sawtooth path; mathematically adjacent, not yet wired into
the API. [`bidder-root.md`](bidder-root.md) — the root API
that bundles this with the sawtooth path.
[`bidder-generator.md`](bidder-generator.md) — the cipher
backend whose cap is the source of `UnsupportedPeriodError`.
[`bqn-agent.md`](bqn-agent.md) — the canonical BQN names used
in the third layer.
