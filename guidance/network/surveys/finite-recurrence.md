# Finite Recurrence

source: [`experiments/acm-champernowne/base2/FINITE-RECURRENCE.md`](../../../experiments/acm-champernowne/base2/FINITE-RECURRENCE.md)  
cited in: [`COLLECTION.md` — The Binary Frontier](../../../COLLECTION.md#chapter-4-the-binary-frontier)  
last reviewed: 2026-04-10

---

**Status.** Conjectured, argued but not formally proved in
this context. The doc is explicit about this: the conjecture
is treated as a *boundary condition on what can be built*, not
as an established result. The argument is strong enough to
rule out naive applications of constrained-coding tools, weak
enough that a formal proof is still open.

**Current evidence.** Three interlocking reasons a finite
automaton cannot recognize a binary ACM stream. (1) *Entry
lengths are unbounded.* The k-th n-prime has bit-length
`⌊log₂(nk)⌋ + 1`, which grows without bound. A finite-state
reader must count to `d` to know where each entry ends, and
no fixed state count can count to an arbitrary integer. (2)
*Periodicity lives in the wrong space.* The sieve structure
of n-primality is periodic in `k` (period `n`), but that
periodicity maps to a non-periodic pattern in bit-stream
space because consecutive entries have different lengths. The
stretch destroys the periodicity a finite automaton would need
to exploit. (3) *The constraints depend on values, not on
windows.* Two of the three quantities that determine the
stream's local structure — `v₂(entry)` and position within
the bit-length class — are themselves unbounded.

**Depends on.** [`binary.md`](binary.md) for the stream
construction and the background against which the conjecture
is stated; [`hamming-bookkeeping.md`](hamming-bookkeeping.md)
for the per-entry value dependence that makes (3) work.

**Open questions.** A formal proof in this context (the
conjecture is stated here for the first time, though
non-finite-state character of sequences encoding growing
integers is adjacent to published work). The "productive
border" is the right way to use constrained-coding tools —
*measurements* like RDS and run-length distributions apply
directly, but *theory* like Shannon capacity of a constrained
channel requires a finite adjacency matrix that the stream
does not provide. Per-bit-length-class capacity is computable
and whether the per-class capacities converge to a limit is
the natural finite-to-infinite bridge, unaddressed so far.
