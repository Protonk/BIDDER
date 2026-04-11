# core/api_doc_examples.py — Docs-as-Assertions Verifier

source: [`core/api_doc_examples.py`](../../../core/api_doc_examples.py)  
cited in: [`COLLECTION.md` — The Discipline](../../../COLLECTION.md#chapter-5-the-discipline)  
last reviewed: 2026-04-10

---

**The mechanism that wedges English against Python in the
three-layer docs.** Not a theorem, not prose —
infrastructure. For every Python code block in
[`api.md`](api.md), [`riemann-sum.md`](riemann-sum.md), and
[`bidder-root.md`](bidder-root.md), the script classifies
the block as either a *signature block* (skipped) or an
*example block* (run), then rewrites every
`EXPR # LITERAL` line in example blocks into an
`assert EXPR == LITERAL` before executing. If any assertion
fires, the block fails. The docs cannot drift from the code
without the verifier catching it.

This is why a reader can trust the runnable examples in
the BQN / English / Python triad: the English prose says
what the code does, the Python code does what the English
prose says, and the verifier refuses to let them disagree
silently. The "trust" is mechanical — the docs are
executed as test fixtures on every run.

**Chimney-climbing role.** In the terms of
[`COLLECTION.md`](../../../COLLECTION.md#chapter-5-the-discipline)'s
Discipline chapter, this file is what turns the
*BQN / English / Python* triad from an aspiration into an
enforced invariant. BQN is the exact-math spec (see
[`bqn-agent.md`](bqn-agent.md)); Python is the
implementation; English is the doc prose. Without this
verifier, English and Python could drift. With it, they
can't — at least not silently.

**Supports.**
[`api.md`](api.md) — the docs whose examples are rewritten.
[`riemann-sum.md`](riemann-sum.md) — also verified.
[`bidder-root.md`](bidder-root.md) — also verified.
[`bqn-agent.md`](bqn-agent.md) — the fourth vertex of the
triangle this verifier enforces on the other three.

**Related.** [`generator-agents.md`](generator-agents.md) —
the C / Python parity enforcement that plays the analogous
role for the other triad, at the implementation level rather
than at the documentation level.
