# generator/AGENTS.md — C/Python Parity

source: [`generator/AGENTS.md`](../../../generator/AGENTS.md)  
cited in: [`COLLECTION.md` — The Discipline](../../../COLLECTION.md#chapter-5-the-discipline)  
last reviewed: 2026-04-10

---

**Cross-language parity rule for the generator.** Python
(`coupler.py`, renamed from `bidder.py` to resolve a
project-root import collision) and C (`bidder.h` + `bidder.c`)
must produce **byte-identical output** for identical inputs.
The cross-check is enforced by `tests/test_bidder.py` with
hardcoded expected values. Any change to one implementation
must be mirrored in the other. Neither implementation is "the
real one."

This is the C / Python / English triad in its most compact
enforcement. The *cost* of two implementations is that every
change costs twice; the *value* is that neither can drift on
its own. The parity test is the discipline that makes the
chimney-climbing metaphor concrete — C pushes against one
wall, Python pushes against the other, and the two wedge
each other up. Removing either breaks the arrangement.

**Feature set.** Both implementations support exactly:
Speck32/64 permutation for tight-fit blocks (cycle-walk
ratio `≤ 64`), balanced Feistel with SHA-256-derived round
keys for small blocks, `base ∈ [2, 2^32]`, block size up to
`2^32`, and the three operations *init*, *next*, *reset*.
Python exposes additional language-required conveniences
(`period` property, `__iter__`, `__next__`, `__repr__`);
these are not feature additions. Adding a feature to one
language without the other is explicitly forbidden.

**Signposting aesthetic.** The doc closes with a discipline
line that is the repo's clearest statement about
documentation style: *"when creating documentation, say what
you want to say briefly enough to not need a road map.
Agents and humans can read 400-600 word documents without
constant semaphore."* Not about parity, but worth lifting as
the editorial register.

**See also.**
[`bidder-generator.md`](bidder-generator.md) — the design
doc whose *Proved / Measured / Not claimed* discipline sits
on top of this parity rule.
[`bqn-agent.md`](bqn-agent.md) — the notation discipline for
the math side of the same layered structure, with its hard
boundary that excludes `generator/**`.
