# BQN Agent Guidance

source: [`guidance/BQN-AGENT.md`](../../../guidance/BQN-AGENT.md)  
cited in: [`COLLECTION.md` — The Discipline](../../../COLLECTION.md#chapter-5-the-discipline)  
last reviewed: 2026-04-10

---

**Canonical-names discipline for the repo's exact-math
annotation layer.** BQN is a fourth vertex in a
*DOCS :: C :: PYTHON* triangle, staying honest the same way
the other three do — by being tested against known values.
If a BQN block drifts from the implementation, the
implementation wins and the BQN gets updated. Adding a BQN
block to a doc is a commitment, not a decoration.

The canonical names are: `NPn2` (n-primes for `n ≥ 2`,
mirrors the sieve in
[`acm-champernowne.md`](acm-champernowne.md) and the
Python/C implementations); `NthNPn2` (the one-line Hardy
closed form, see [`hardy-sidestep.md`](hardy-sidestep.md));
`Digits10` (exact decimal digits of a positive integer);
`ChamDigits10` (exact decimal concatenation, the
specification-level Champernowne payload); `DigitCount10`
(typographic cost); `LeadingInt10` (integer leading digit,
used in block-uniformity claims); `LD10` (log-based leading
digit for positive reals, with a `+1e-9` guard against
floating-point truncation — see `nasties/FIRST-DIGIT.md`);
`Benford10` (the reference distribution to contrast the
exact-uniformity results against); `BinDigits`, `BStream`,
`V2` (binary-side names for the `base2/` subtree).

**Hard boundary.** `generator/**` is out of scope for BQN.
The cipher is not the kind of object BQN annotates. The
product side stays BQN-free; the math docs borrow
mathematical provenance from `core/` but do not import BQN
into the generator docs. This is why
[`bidder-root.md`](bidder-root.md) and
[`api.md`](api.md) use BQN for the *math layer* the API
sits on, but not for the cipher permutation itself.

**Chimney-climbing role.** The doc is one of the four
pillars of the Discipline chapter in
[`COLLECTION.md`](../../../COLLECTION.md#chapter-5-the-discipline).
The BQN / English / Python triad and the C / Python /
English triad both pass through this doc's naming
discipline: BQN is the exact-math specification, English
carries intent, Python carries behavior, and the three are
wedged against each other.

**See also.** [`api-doc-examples.md`](api-doc-examples.md) —
the mechanism that pins English to Python in the same
three-layer docs. [`generator-agents.md`](generator-agents.md)
— the C / Python parity rule that makes the second triad
concrete. [`acm-champernowne.md`](acm-champernowne.md) and
[`hardy-sidestep.md`](hardy-sidestep.md) — the docs where
the canonical names are most densely used.
