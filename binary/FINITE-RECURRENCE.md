# Finite Recurrence

## The Conjecture

**No finite-state automaton can generate or recognize the binary
Champernowne stream of any arithmetic congruence monoid.**

More precisely: for any n >= 2 and any finite automaton M reading
one bit at a time, the set of bit streams accepted by M either
excludes infinitely many valid binary Champernowne streams of
monoid n, or includes infinitely many invalid ones. The constraint
structure of the stream is not a regular language. It is not a
sofic shift. No finite adjacency matrix captures it.

This is scoped to binary for discipline, but it is true in every
base. The mechanism is the same: the stream encodes growing integers,
and the constraints depend on those integers' values, not on a
bounded window of recent symbols.


## Why

Three interlocking reasons.

**1. Entry lengths are unbounded.** The k-th n-prime has bit-length
floor(log_2(nk)) + 1, which grows without bound. A finite automaton
reading the bit stream must determine where each entry ends and the
next begins. This requires counting to d (the current entry's
bit-length), but d is unbounded. No fixed number of states can count
to an arbitrary integer. The entry boundaries are invisible to any
finite-state reader.

**2. Periodicity lives in the wrong space.** The sieve structure of
n-primality is periodic in k (period n). The boundary pattern at
entry k depends on k mod n — a genuinely finite-state fact. But
this periodicity in k-space maps to a non-periodic pattern in
bit-stream-space, because consecutive entries have different lengths.
Entry k contributes d_k bits and entry k+1 contributes d_{k+1} bits;
the boundary positions in the stream are cumulative sums of the d_k,
which grow logarithmically. The finite-state pattern (period n in k)
is stretched by a non-constant, non-periodic factor (bit-length per
entry). The stretching destroys the periodicity that a finite
automaton would need to exploit.

**3. The constraints depend on values, not on windows.** The 8b/10b
encoder needs 1 bit of history: the current running disparity. Our
stream needs to know the current n-prime's value — specifically its
2-adic valuation, its position within its bit-length class, and its
residue modulo n. The first of these (v_2 of the n-prime) depends
on v_2(k), which is itself unbounded. The second (position in class)
depends on log_2(nk), which grows. Only the third (k mod n) is
bounded. Two of the three quantities that determine the stream's
local structure are unbounded. No finite state vector can track them.


## What This Means for Borrowed Tools

The constrained coding literature (Franaszek 1968/1970, Adler-
Coppersmith-Hassner 1983, Immink 2004) provides:

**Instruments that work.** Running digital sum, run-length
distributions, power spectral density, disparity tracking — these
are measurements. They don't require the stream to be finite-state.
They apply to any bit stream. We use them freely.

**Theory that doesn't apply.** Shannon capacity of a constrained
channel (C = log_2(lambda_max) of the adjacency matrix) requires
a finite adjacency matrix. We don't have one. The capacity formula,
the state-splitting algorithm, the eigenvalue characterization of
the shift space — these are tools for regular languages. Our stream
is more complex.

**The border is productive.** We can compute effective capacity
*within* each bit-length class, where the structure is locally
finite. The d-bit class of monoid n contains a finite number of
entries, each of length d, with sieve statistics determined by
k mod n. This local slice IS a finite-state object. Its capacity
is computable. The question is whether the per-class capacities
converge to a limit as d grows. If they do, that limit is the
stream's asymptotic information rate — the number that replaces
lambda_max in our non-finite setting.

We can stand at this border and look backward: each bit-length
class is a finite world where Franaszek's tools apply fully. The
infinite stream is the limit of these finite worlds. The limit
exists as a mathematical object. But it cannot be captured by any
single finite world — we can approximate it from inside but never
arrive.


## Connection to Other Work

The non-finite-state character of sequences encoding growing
integers is not unique to ACMs. It appears wherever positional
notation meets multiplicative structure. The binary Champernowne
stream is one instance. The conjecture is that this is a theorem,
established in adjacent work. We state it as a conjecture here
to maintain discipline: within the binary/ tree, we treat it as a
boundary condition on what we build, not as a result we have proven
in this context.

The practical consequence: every visualization, every measurement,
every statistic we compute in the forest is a *finite slice* of a
non-finite object. The slices are informative. The object is real.
But no finite collection of slices constitutes the object, and no
finite machine generates it. We measure what we can, note the
horizon, and keep walking.
