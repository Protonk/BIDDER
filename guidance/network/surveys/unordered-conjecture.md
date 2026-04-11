# Unordered Conjecture

source: [`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`](../../../experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md)  
cited in: [`COLLECTION.md` — The Recovery Thread](../../../COLLECTION.md#chapter-3-the-recovery-thread)  
last reviewed: 2026-04-10

---

**Thesis.** A deterministic greedy algorithm reconstructs the
row list of an `N × N` n-prime table from the **unordered
multi-set** of cell values with **zero hints**, in `O(N²)`.
The row labels are literally the row-wise minima of the
multi-set at each peeling step. The original conjecture was
that `O(log N)` hints would be needed; the answer is below all
three proposed bounds. Around this proof the doc builds the
strongest meta-layer in the repo: a retrospective on why the
same kind of recovery question keeps collapsing to trivial
inversions, and a careful knife-edge caveat about what that
pattern means in a constructed space.

**Case studies.** Three worked surprises, all framed as hard
recovery problems that turned out free. (1) The **abductive
key**: diagonal divided by position recovers the row list.
(2) The **cascade key**: one diagonal cell unlocks the entire
row via `j_{k'}(n_k) · n_k`. (3) The **greedy extraction**:
the row labels are the row-wise minima of the multi-set, and
peeling gives the row list with no hints. [`hardy-sidestep.md`](hardy-sidestep.md)
is a fourth instance of the same leaky-parameterization
observation in a different channel (the K-th n-prime recovered
from `(n, K)` alone).

**Discipline prescribed.** Before briefing any future recovery
experiment in this area, write the half-line description of
what the trivial extraction would be and check whether it
already works. Classify each question as *recovery* (will
collapse), *dynamics* (may be hard), or *transport* (hard or
vacuous; check carefully). Apply the two-sided check: *input
side* — "is the answer already in the definition?" — and
*output side* — "does the chosen observable factor through a
tiny invariant?" Trust a result only when both come back "no."
In constructed spaces like this one, prefer the *perimeter*
reading when in doubt: the parameterization may be the entire
surface area, in which case every "result" is a relabeling.

**See also.** [`abductive-key.md`](abductive-key.md) — the
first surprise and the "note on visibility."
[`cascade-key-readme.md`](cascade-key-readme.md) — the second
surprise made geometric.
[`cantor-walk-readme.md`](cantor-walk-readme.md) — strict
ascent as a rate, the fifth plot the doc's experiment family
lives inside. [`cantors-plot.md`](cantors-plot.md) — the
garden context.
[`pair-programming.md`](pair-programming.md) — the
phenomenological account of how these corrections actually
got found.
