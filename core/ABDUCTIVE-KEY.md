# Abductive Key

The diagonal of an ACM irreducible table, taken as the ordered sequence
`D_1, ..., D_N` in rank coordinates, recovers its row labels by
division by rank. This note states the precise hypotheses, proves the
rule, shows where it fails, and gives three tables.


## Setup

Fix an integer N ≥ 1 and an ordered list of monoid indices

    n_1 < n_2 < ... < n_N,    each n_i ≥ 2.

The list is **strictly ascending** (no repeats). The lower bound n_i ≥ 2
excludes the ordinary-prime case n = 1, in which the rule below fails.

Build the N × N table T whose entry T[k][k'] is the k'-th n_k-prime in
ascending order, for k, k' ∈ {1, ..., N}. Recall that the n-primes of
monoid n are the elements n·j with j ≥ 1 and n ∤ j, listed in ascending
order.

The **diagonal** is the sequence

    D_k := T[k][k],    k = 1, ..., N.


## Claim

Under the setup above,

    D_k = k · n_k    for every k ∈ {1, ..., N},

and therefore

    n_k = D_k / k.

The diagonal alone determines the row list.


## Proof

**Lemma.** For an integer n ≥ 2 and an integer k with 1 ≤ k ≤ n − 1,
the k-th n-prime equals k·n.

*Proof of lemma.* The n-primes are the elements n·j with n ∤ j, listed
by increasing j. The values j = 1, 2, ..., n − 1 are all strictly less
than n, hence none is divisible by n, hence all qualify. The next
candidate j = n is excluded. So the first n − 1 admissible values of j,
in order, are 1, 2, ..., n − 1, and the k-th n-prime for k ≤ n − 1 is
n·k. ∎

**Main argument.** We must verify that the lemma's hypothesis k ≤ n_k − 1
holds at every diagonal position k ∈ {1, ..., N}.

The list n_1 < n_2 < ... < n_N is strictly ascending with n_1 ≥ 2. By
induction, n_k ≥ k + 1 for every k: the base case is n_1 ≥ 2 = 1 + 1,
and if n_{k−1} ≥ k then n_k > n_{k−1} ≥ k forces n_k ≥ k + 1. Hence
k ≤ n_k − 1 at every k.

Applying the lemma to row k with that bound,

    D_k = T[k][k] = k · n_k.

Dividing by k recovers n_k. ∎


## Why the hypotheses matter

The lower bound `n_k >= 2` is essential. At `n = 1`, the row is the
ordinary primes, so the first diagonal entry is `T[1][1] = 2`, not
`1 · 1`.

Strict ascent is also essential. It is what guarantees `n_k >= k + 1`,
which keeps the diagonal position `k` below the square boundary `n_k^2`.
If rows repeat or arrive too early, the rule can fail immediately. For
example, the row list `{2, 2}` has diagonal `{2, 6}`, and dividing by
rank gives `{2, 3}`, not `{2, 2}`.


## In BQN

The following uses canonical names from `BQN-AGENT.md`. It is
an exact-math gloss for the `n >= 2` branch of `core/acm_core.py`; the
special case `n = 1` remains prose.

```bqn
NPn2 ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}
```

For `n >= 2`, the first `n − 1` n-primes are the undeleted multiples
below the square boundary:

```bqn
5↑ 6 NPn2 5
# ⟨6,12,18,24,30⟩
```

So once a row list `Rows` is strictly ascending, the diagonal ranks
`1, 2, ..., ≠Rows` all lie in that initial regime, and the theorem is
just:

```bqn
Rows ← ⟨2,5,10,13,17,21⟩
Diag ← (1+↕≠Rows) × Rows
Diag ÷ 1+↕≠Rows
# ⟨2,5,10,13,17,21⟩
```

## Examples

The diagonal entries are marked **bold**. The recovery row shows
D_k / k.

### Example 1 — contiguous rows {2, 3, 4, 5, 6}

| n \ k | 1     | 2     | 3      | 4      | 5      |
|-------|-------|-------|--------|--------|--------|
| 2     | **2** | 6     | 10     | 14     | 18     |
| 3     | 3     | **6** | 12     | 15     | 21     |
| 4     | 4     | 8     | **12** | 20     | 24     |
| 5     | 5     | 10    | 15     | **20** | 30     |
| 6     | 6     | 12    | 18     | 24     | **30** |

Diagonal: **2, 6, 12, 20, 30**
Recovery: 2/1, 6/2, 12/3, 20/4, 30/5 = **2, 3, 4, 5, 6** ✓

### Example 2 — sparse rows {2, 5, 10, 13, 17, 21}

| n \ k | 1      | 2      | 3      | 4      | 5      | 6       |
|-------|--------|--------|--------|--------|--------|---------|
| 2     | **2**  | 6      | 10     | 14     | 18     | 22      |
| 5     | 5      | **10** | 15     | 20     | 30     | 35      |
| 10    | 10     | 20     | **30** | 40     | 50     | 60      |
| 13    | 13     | 26     | 39     | **52** | 65     | 78      |
| 17    | 17     | 34     | 51     | 68     | **85** | 102     |
| 21    | 21     | 42     | 63     | 84     | 105    | **126** |

Diagonal: **2, 10, 30, 52, 85, 126**
Recovery: 2/1, 10/2, 30/3, 52/4, 85/5, 126/6 = **2, 5, 10, 13, 17, 21** ✓

### Example 3 — wide-spaced rows {3, 7, 11, 100, 1000}

| n \ k | 1      | 2      | 3      | 4       | 5        |
|-------|--------|--------|--------|---------|----------|
| 3     | **3**  | 6      | 12     | 15      | 21       |
| 7     | 7      | **14** | 21     | 28      | 35       |
| 11    | 11     | 22     | **33** | 44      | 55       |
| 100   | 100    | 200    | 300    | **400** | 500      |
| 1000  | 1000   | 2000   | 3000   | 4000    | **5000** |

Diagonal: **3, 14, 33, 400, 5000**
Recovery: 3/1, 14/2, 33/3, 400/4, 5000/5 = **3, 7, 11, 100, 1000** ✓


## The rank-1 view

The cell `T[k][k'] = k' · n_k` whenever `k' ≤ n_k − 1`. So row `k` of
the table is rank-1 in columns `1` through `min(N, n_k − 1)`, and the
shape of the rank-1 region depends on the row list. In the contiguous
case `n_k = k + 1`, the region is exactly the closed lower triangle
`{k' ≤ k}`. For sparser ascending row lists, rows with `n_k ≥ N + 1`
are entirely rank-1 and only the small-`n` rows at the top are
clipped; in example 2 above, rows 3–6 are full and rows 1–2 are
truncated. The region is never the whole square unless `n_1 ≥ N + 1`.

The n-prime row at position `k` is parameterized by a single scalar:
`n_k`. Every cell of row `k` is the function
`k' → j_{k'}(n_k) · n_k` of that one parameter, where
`j_{k'}(n) = k' + ⌊(k' − 1) / (n − 1)⌋`. Anything that recovers
`n_k` recovers the row. In the rank-1 region the function simplifies
to `T[k][k'] = k' · n_k`, and the entries are literally an outer
product of the column vector `(1, 2, …, N)` and the row vector
`(n_1, …, n_N)`. The diagonal of any outer product `u v^T` is the
pointwise product `u_k · v_k`, and either factor is recovered from
the other by pointwise division. The abductive key is that division,
with `u_k = k`. Once you see that the n-prime table has this rank-1
substructure, the recovery is one line of intro linear algebra. The
work is in noticing the shape.

A second extraction of `n_k` is even more elementary. The cell
`T[k][1] = j_1(n_k) · n_k` equals `n_k` for any `n_k ≥ 2`, because
`j_1 = 1`. So the first cell of every row is its row label, full
stop. Two settings make use of this. In the cascade picture
(`experiments/acm/diagonal/cascade_key/`), once `n_k` is decoded by
any means, every later cell of row `k` is computable from `k'` and
`n_k` alone via `j_{k'}(n_k) · n_k` — the entire row, including the
cells past the rank-1 region, unlocks from a single value. In the
unordered-multi-set picture
(`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`),
the row labels of an `N × N` n-prime table are exactly the row-wise
minima of the cell values, and a greedy "take the smallest, strip
its row, repeat" algorithm reconstructs the row list from the
unordered multi-set with zero hints. The greedy theorem, its proof,
and an empirical battery of 15 row lists live in
`experiments/acm/diagonal/cantor_walk/verify_greedy.py` and the
same folder's `UNORDERED-CONJECTURE.md` addendum.

The two hypotheses of the proof are the same inequality wearing two
hats. Strict ascent forces `n_k ≥ k + 1`, which is exactly the
condition that the diagonal cell `(k, k)` lies inside the rank-1
region (`k ≤ n_k − 1`). The induction in the proof and the placement
of the diagonal inside the rank-1 region are the same fact in two
notations: the diagonal's slope is calibrated to the rank-1 boundary.

The dual observation is why we keep being surprised by results in
this area. We do not have a single key that opens many locks; we
have a single *lock* — "what is `n_k`?" — that is so weakly
structured the parameter leaks out of every channel we look at.
Each of the extractions above uses a different channel: the diagonal
divided by position (the abductive key), the first cell of each row
(the cascade key), the row-wise minimum of the cell values (the
greedy extraction). They are not three different insights — they are
three instances of the same observation, namely that the n-prime row
is *parameterized by a single scalar*, and single-scalar inversions
are all easy. (Only the first of the three is literally a rank-1
matrix inversion in the linear-algebra sense; the cascade uses the
nonlinear closed form `j_{k'}(n_k) · n_k`, and the greedy extraction
uses combinatorial facts about strict ascent and complete multi-set
availability. The unifying word is "single-scalar," not "rank-1.")
The hard problem in this area isn't recovering `n_k`; that is free in
at least two structurally distinct ways. The hard problem is noticing in advance that the construction
has this much structure, so we stop framing recovery questions as if
they were harder than they are.

The lossy-sieve use of this inverts the usual sieve cost model: one
parameter, no memory, factorization included. The identification use
— treating an integer sequence as a one-pass test that asks "is this
an ACM family in disguise?" — is the one most likely to surprise in
another context.


## A note on visibility

The lemma is elementary and the main argument is half a page. Anyone who
has built the table by hand has, in some sense, already proved the
lemma — the rule "the first few n-primes are n, 2n, 3n, ..." is the
construction itself. The step from there to "therefore the diagonal of
any ascending square table divides back to its row labels" is one
inference long. Yet for a solo researcher (N = 1) and a single
collaborating model (R = 1) working examples directly, the inference is
not forthcoming. We saw the diagonals, we computed the diagonals, we
discussed the diagonals across several sittings, and the
divide-by-column-index step was found only after it was prompted by a
seemingly unrelated question on Cantor.

We have now found this same kind of "obvious in retrospect" inversion
three times. The original abductive key (this document) was the first.
The cascade decoding of plot 4
(`experiments/acm/diagonal/cascade_key/`) was the second, where we
initially framed "do later patches admit their own keys" and the
answer turned out to be "no — there's one key and it opens every lock
in the row." The row-wise-minimum extraction in the unordered
conjecture
(`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`) was
the third, where we initially proposed an `O(log N)`-hint backtracking
solver and the actual answer was that greedy reconstructs from the
multi-set with zero hints. Each time we framed the question as if we
did not know the n-prime structure, and each time the structure made
the question free. The "Notes on a pattern" section of the
unordered-conjecture document records this and proposes a discipline
for next time: before posing a recovery experiment in this area, write
the half-line description of what the trivial extraction would be and
check whether it already works. The same document's
immediately-following "The knife-edge: productive triviality" section
adds the cautious response — the leaky parameterization is either a
*foothold* (rich consequences from a trivial surface) or a *perimeter*
(the precisely-shaped object where the substrate's transparency
stops). Both outcomes are real findings; the perimeter reading
locates the genuine arithmetic content in the construction, and
locating a perimeter is itself a major mathematical move (ζ's at the
zeros, a century of work). We do not yet know whether this pattern
is a *principle* (every recovery question collapses) or a
*coincidence* (we have found three accidents). Three is too small a
number to choose between those, but it is large enough to expect a
fourth — and large enough that we should ask, before leaning on any
future result that depends on the parameterization, whether the
result gives us a quantity not already in the definition.
