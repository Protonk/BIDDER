# The unordered antidiagonal recovery problem

A follow-up to `recovery_curves.py` (plot 5 of `CANTORS-PLOT.md`).
Recorded now, to be built later.

## The problem

The ordered Cantor walk recovers row labels at quadratic rate: row
`k` is reconstructable at step `k(k+1)/2`, because that is when the
walk first reaches cell `(k, 1)` and the receiver, knowing they are
at `(k, 1)` via the walk pattern, computes `n_k = T[k][1] / 1 = n_k`
directly. The receiver's recovery work is being split between the
cell *value* and the cell *position*; position is doing as much
work as value.

The **unordered version** strips position. The receiver gets the
cell values as an unlabeled multi-set (or as a stream whose order
has been permuted) and must reconstruct the row labels using only:

1. The values themselves — each is `j_{k'}(n_k) · n_k` for some
   unknown `(k, k')`.
2. The structural constraint that the values came from an `N × N`
   n-prime table with strictly ascending row list `n_1 < n_2 <
   … < n_N`, every `n_k ≥ 2`.

Without the second constraint, the values could be anything and
reconstruction is hopeless. The constraint is what makes the problem
well-posed.

## Why this is interesting

**It separates position-as-decoder from value-as-decoder.** The
ordered version mixes them; the unordered version asks how much of
the recovery work the values were doing on their own. If the
unordered version is *easy*, the diagonal walk's linear-rate
advantage in plot 5 isn't really a recovery advantage — it's a
*labeling* advantage. The information was always in the values; the
diagonal walk just labels it for free.

**Hints become a currency.** Adding "row label hints" — known
`(k, n_k)` pairs given to the receiver — partially restores
position information. The natural question becomes: how many hints
are enough? That number is a measurable quantity, and its growth
rate in `N` is the answer.

**It tests how over-determined the n-prime construction is.** The
multi-set `V` of all cell values has `N²` elements; the row list has
`N` unknowns. The system is massively over-determined by counting,
but the equations are nonlinear (multiplication) and degenerate
(many divisor pairs), so the practical question is whether the
over-determination is *informational* or only *combinatorial*.

## The conjecture

Let `f(N)` be the smallest number of hints such that the receiver
can reconstruct the entire row list `n_1, …, n_N` from the unordered
multi-set `V` with high probability over a natural distribution of
row lists (e.g., uniformly random strictly-increasing sequences with
bounded gaps).

**Primary conjecture:** `f(N) = O(log N)`.

**Weaker fallback:** `f(N) = O(√N)`.

**Stronger version:** `f(N) = O(1)` — a constant number of hints
(maybe 2 or 3) suffices for all `N` above some threshold.

I don't know which is right. The experiment is to sweep `(N, h)`
pairs and measure success rates. The boundary in the resulting phase
diagram *is* the function `f(N)`.

## Why we think `f(N)` is small

Three pieces of intuition that cap `f(N)` below the trivial `N`:

1. **The smallest values in `V` are typically the row labels
   themselves.** Column 1 of every row contributes `n_k`, and these
   are the smallest values in their row. For typical row lists they
   dominate the lower end of `V`, so sorting `V` and taking the
   smallest `N` distinct values often gives back the row list
   directly — *zero hints needed*. The conjecture is essentially
   saying that this heuristic mostly works, with hints used only to
   handle the cases where it doesn't.

2. **Strict ascent is a strong constraint.** Once a few row labels
   are pinned, ascent eliminates large blocks of candidate
   decompositions for the remaining values. The constraint
   propagates.

3. **Rank-1 cells dominate.** In the contiguous case `n_k = k + 1`,
   the rank-1 region is the lower triangle (~`N²/2` cells), so most
   cell values factor as `k' · n_k` with `k' ≤ n_k − 1` and have a
   small set of valid decompositions. Most divisor pairs of any
   given value `v` are eliminated by ascent before backtracking is
   even needed.

## Counterexamples to watch for

The conjecture might fail when the row list is structured to
maximize value collisions:

- **Adjacent labels.** `n_k = m`, `n_{k+1} = m + 1` makes `k · m`
  and `k · (m + 1)` differ by only `k`, which is small compared to
  the values themselves. Hard to distinguish without other
  constraints.

- **Highly composite labels.** If `n_k` has many small divisors,
  the values `k' · n_k` collide with values from other rows because
  `k' · n_k = k'_alt · n_{k_alt}` has many integer solutions.

- **Geometric growth.** `n_k = 2^k` produces cell values
  `2^k · k'`, which are distinct but have unusual collision
  structure. Possibly easier (more uniqueness) or possibly harder
  (large search space).

The experiment should include adversarial row lists in the sweep,
not just uniform random ones.

## What the experiment looks like

The pieces, in order of how much new code they need:

1. **Generator** (free, already exists). Build the n-prime table for
   a given row list using `recovery_curves.py`'s `n_prime_value` and
   dump the unordered multi-set of cell values.

2. **Solver** (the hard part, new code). Takes:
   - the multi-set `V`
   - the integer `N`
   - a list of `h` hints `[(k_i, n_{k_i})]`

   Returns either the reconstructed row list or "failure." Likely
   approach: constraint propagation. Treat each value as a
   constraint of the form "this value equals `j_{k'}(n_k) · n_k`
   for some `(k, k')` consistent with already-known labels and
   strict ascent." Propagate forced assignments; backtrack on
   ambiguity. The strict-ascent constraint should prune aggressively.

3. **Sweep** (small loop). For each `(N, h)` pair, run `K` trials
   with random row lists and random hint subsets. Record success
   rate.

4. **The picture** (single image, the deliverable). A phase
   diagram: `N` on the x-axis, `h` on the y-axis, color = success
   rate. Above some boundary curve, color is uniform "100%
   recovered." Below it, "0% recovered." The shape of the boundary
   is `f(N)`. If logarithmic, the primary conjecture wins; if
   square-root, the fallback; if linear, the conjecture fails and
   position-as-decoder is essential.

5. **Solver verification** (assertion harness). For `N` small enough
   to brute-force, check the solver's output against the known row
   list. The recovery_curves.py infrastructure already has
   brute-force n-prime sieves; reusing them as the oracle costs
   nothing.

## What this would teach

**If `f(N) = O(log N)`** (or smaller): the unordered antidiagonal
stream carries almost all the structural information about the row
list. Position-as-decoder is doing surprisingly little work, and the
diagonal walk's linear-rate advantage in plot 5 is a labeling
convenience, not an informational one. The information was always
there in the values; the diagonal walk just hands it to you indexed.

**If `f(N) = O(√N)` or larger**: position-as-decoder is essential.
The unordered problem is meaningfully harder than the ordered one,
and the abductive key's "diagonal stays in the rank-1 region"
property is a real informational shortcut, not just a labeling
shortcut.

Either answer reframes the abductive key: the rank-1 substructure
is either *recoverable from values alone* (with a few hints) or
*only recoverable with position information*. Right now we don't
know which.

## Status

**Resolved at `f(N) = 0`** for the full multi-set version. See the
*Abductive addendum* below for the proof and the empirical
verification (`verify_greedy.py`). The interesting follow-up is the
*partial* multi-set version, sketched at the bottom of the
addendum.

The expected output of the original experiment was "one of three
answers: `O(log N)`, weaker, or fails." The actual answer is
**below all three**: zero hints suffice. The structure is much
stronger than the original conjecture imagined.


## Abductive addendum: a trivial-greedy proof

While briefing the next experiment, we realized the conjecture
admits a trivial proof. Greedy reconstruction works on the full
multi-set with zero hints, deterministically, in `O(N²)` time, on
every row list we tested. This addendum records the proof and
notes the pattern: this is the **third time** the n-prime
construction has surprised us with an "obvious in retrospect"
linear-algebra-style inversion.

### The theorem

Let `n_1 < n_2 < … < n_N` be a strictly ascending row list with
each `n_k ≥ 2`. Let `T` be the `N × N` n-prime table with
`T[k][k'] = j_{k'}(n_k) · n_k`, where
`j_{k'}(n) = k' + ⌊(k' − 1) / (n − 1)⌋`. Let `V` be the multi-set
`{T[k][k'] : 1 ≤ k, k' ≤ N}`.

**Theorem.** The following deterministic algorithm reconstructs
the row list `(n_1, …, n_N)` from `V` and `N` alone, with zero
hints:

```
greedy(V, N):
    rows = []
    for i = 1, 2, …, N:
        n_i = min(V)
        rows.append(n_i)
        for k' = 1, 2, …, N:
            v = j_{k'}(n_i) · n_i
            V.remove(v)        # remove one copy
    return rows
```

### The proof

Define `R_i = {T[i][k'] : k' = 1..N}`, the set of cells of row `i`.
Each `R_i` has exactly `N` distinct values, because `j_{k'}` is
strictly monotonic in `k'` and so `j_{k'}(n_i) · n_i` is too.

We prove by induction on `i` that at the start of step `i` of the
algorithm, the working multi-set `V_i` is the multi-set union
`⋃_{k = i}^N R_k`.

**Base case.** `V_1 = V = ⋃_{k = 1}^N R_k` by definition. ✓

**Inductive step.** Assume `V_i = ⋃_{k = i}^N R_k`. We show:

(a) `min(V_i) = n_i`.

The smallest cell in row `k` is `T[k][1] = j_1(n_k) · n_k`, and
`j_1(n_k) = 1 + ⌊0 / (n_k − 1)⌋ = 1` for any `n_k ≥ 2`. So the
smallest cell in row `k` is exactly `n_k`. The smallest cell in
`V_i` is therefore `min_{k ∈ {i, …, N}} n_k`, which is `n_i` by
strict ascent.

(b) Removing one copy of each value in `R_i` from `V_i` yields
`V_{i+1} = ⋃_{k = i + 1}^N R_k`.

For each value `v`, let `m_i(v) = |{k ∈ {i, …, N} : v ∈ R_k}|` be
the number of rows in `i..N` that contain `v`. Then `v` has
multiplicity `m_i(v)` in `V_i`. After removing one copy of each
element of `R_i`:

- If `v ∈ R_i`, then row `i` contributes exactly one copy of `v`
  (because `j_{k'}` is strictly monotonic, so `v` appears at most
  once in row `i`). So `m_i(v) = m_{i+1}(v) + 1`, and after removal
  the multiplicity is `m_i(v) − 1 = m_{i+1}(v)`. ✓
- If `v ∉ R_i`, then `m_i(v) = m_{i+1}(v)` and the multiplicity is
  unchanged.

So the resulting multi-set has exactly the multiplicities of
`⋃_{k = i + 1}^N R_k`, completing the inductive step.

After `N` iterations, `V_{N+1} = ∅` and the algorithm has output
`(n_1, n_2, …, n_N)` in order. ∎

### Empirical verification

`verify_greedy.py` runs the algorithm against 15 hand-picked row
lists, including:

- contiguous (`{2, 3, 4}`, `{2..6}`, `{2..21}`)
- sparse (`{2, 5, 10, 13, 17, 21}`)
- very sparse (`{3, 7, 11, 100, 1000}`)
- adversarial-by-design: geometric powers of 2, multiples of 3,
  Fibonacci-like, `n_2` a multiple of `n_1`, dense with heavy
  collisions, two close + one far, adjacent + power of 2

All 15 cases pass. The script asserts the recovered row list
exactly equals the input row list and that the multi-set is empty
after `N` iterations. Run it with `sage verify_greedy.py`.

### Three corollaries

1. **`f(N) = 0`** for the unordered conjecture as originally
   stated. Below all three proposed bounds (`O(log N)`, `O(√N)`,
   `O(1)`). Hints are unnecessary for the full multi-set case.

2. **The algorithm is `O(N²)`** in arithmetic operations: it
   computes `N` rows of `N` cells each, plus `O(N²)` multi-set
   operations. No backtracking, no constraint propagation, no
   search.

3. **The row labels are *literally embedded* in `V` as values.**
   Each `n_k` is the cell `T[k][1]`, and these `N` cells are the
   row-wise minima. The receiver doesn't *decode* `n_k` from `V` —
   they *read it off* the surface of `V` after stripping the
   earlier rows. The "abductive" reading isn't an inference at all
   in the unordered setting; it's an extraction.


## Notes on a pattern: three surprises now

This is the third time the n-prime construction has handed us an
"obvious in retrospect" inversion that we initially framed as a
hard problem. Worth recording the pattern.

### The three surprises

**1. The abductive key itself** (`core/ABDUCTIVE-KEY.md`). The
diagonal of the n-prime table, divided pointwise by position,
recovers the row labels. This is the Hadamard inverse of a rank-1
outer product `(1, 2, …, N)ᵀ ⊗ (n_1, …, n_N)` — one line of intro
linear algebra. We didn't see it across several sittings of working
with the table directly; it took a question about Cantor's diagonal
to surface it. The note in `ABDUCTIVE-KEY.md` says: "the lemma is
elementary and the main argument is half a page... yet for a solo
researcher (N = 1) and a single collaborating model (R = 1)
working examples directly, the inference is not forthcoming."

**2. The cascade key** (`cascade_key/`, plot 4). Once `n_k` is
decoded from the first patch via the abductive key, every later
patch in row `k` decodes too — `j_{k'}` is computable from `k'` and
`n_k` alone, so the entire row is unlocked from a single diagonal
cell. We initially framed this as "do later patches admit their
own keys?" The answer turned out to be "no — there's one key, and
once turned it opens every lock in the row." The patches have
their own *locks*, not their own keys.

**3. This addendum.** The unordered multi-set `V` carries the row
labels as its row-wise minima. The greedy "strip the smallest"
algorithm reconstructs the row list with no hints, in `O(N²)`. We
initially framed this as a constraint satisfaction problem
requiring `O(log N)` hints solved by backtracking propagation. The
real answer is `f(N) = 0` and the algorithm is six lines.

### What the three have in common

All three start from a question of the form *"given an impoverished
view of the n-prime structure, can we recover the row list?"* — and
all three resolve to *"yes, and trivially, because the structure is
much stronger than the impoverished view suggests."*

The common mechanism: **the n-prime construction is rank-1 in
several different senses, and rank-1 inversions are all easy.** The
abductive key inverts a rank-1 outer product of two vectors. The
cascade key inverts a one-parameter family from a single value. The
greedy extraction inverts a multi-set by reading off the row-wise
minima. Each of these is the kind of move an introductory linear
algebra student would call obvious. Each was a real surprise to us
because we kept *posing the problem as if we didn't know the
structure*, and then the structure made the problem free.

### A sharper statement of the pattern

**Whenever we ask "can we recover X from a partial view of the
n-prime table," the answer is almost certainly yes, and the
construction is almost certainly trivial.** We have empirical
evidence for this from three independent attempts. The hard
questions are *not* the recovery questions — those keep collapsing
— they are the questions about *what the structure itself
implies*: whether the cascade survives perturbation (plot 4's open
question), whether the BIDDER family extension preserves block
uniformity (plot 7), whether the rank-1 substructure shows up in
unrelated integer sequences (plot 2). Those questions are hard
because they ask whether the structure *holds* in regimes we
haven't tested, not whether the structure can be inverted.

### A meta-lesson for future planning

When proposing a new recovery experiment in this area, the first
thing to check is whether greedy or some equally trivial extraction
already solves it. If yes, the experiment is moot and we should
fold it into the README of the relevant plot rather than building
infrastructure for it. If no, *that's* the informational claim
worth testing.

Concretely: before briefing on a future "given X, recover the row
list" experiment, write the half-line description of what the
greedy or matching extraction would be, and check whether it
trivially works. The brief should *include* the trivial-extraction
check as the first paragraph.

We have now spent three brief-write cycles on recovery problems
that turned out to be free. The fourth time would be embarrassing.


## The knife-edge: productive triviality

The leaky parameterization is *productively trivial*. It is also
a knife-edge, and we should record where the edge is so we do not
forget.

Triviality of a structural fact can mean two things. It
can mean **the construction has rich consequences that follow from
a trivial surface presentation** — the way `(AB)^T = B^T · A^T` is
one symbol-pushing line and underlies most of matrix theory. The
trivial presentation is then a **foothold**: results that depend
on it are real, the elementary fact is doing real work, and we
should expect more uses to emerge. Or it can mean **the trivial
presentation is precisely where the substrate's transparency
stops** — the parameterization captures what the construction has
to say, and results that depend on it locate a particular
arithmetic object rather than uncover further structure. The
trivial presentation is then a **perimeter**: not a relabeling
exercise but a localisation, identifying where genuine arithmetic
content begins. Both readings are real findings. ζ's perimeter sits
at the zeros, and locating that perimeter has been a century of
work; a perimeter on the n-prime construction would be informative
in the same shape, even at a smaller scale.

The danger is sharper in this project than in most settings,
because **we constructed the n-prime table on purpose**. In
discovered spaces — the integers, the primes, the digit
distributions of real-world data — the structure we find is not
ours and tells us something. In constructed spaces we defined the
object ourselves, and any "structure" we discover risks being
structure we put in by definition. The parameterization
`T[k][k'] = j_{k'}(n_k) · n_k` is literally part of the definition
of the n-prime table. Everything that follows from "the row
depends on `n_k`" carries a tautological risk by default.

Mixed evidence so far. **In favor of foothold**: plot 4's cascade
gave us decoding past the rank-1 region — knowing `n_k` lets you
compute cells the original abductive key didn't reach. Plot 5's
recovery rates calibrated the diagonal walk against the rank-1
boundary in a way the definition did not immediately give us. The
unordered greedy is a deterministic algorithm with a clean
complexity bound, derived from the parameterization but not
identical with it. The abductive key itself supports a one-pass
identification test on integer sequences that has nothing to do
with the n-prime construction's original intent. **In favor of
perimeter**: weaker but worth tracking. Plot 8's failed prediction
showed the parameterization does not cleanly transfer between
contexts — plot 9's selector behavior (`cost_prime` picks
witnesses *near* the prime curve) does not become generator
behavior (`n_k = p_k` walks witnesses *on* the prime curve), and
a prediction that assumed it would was wrong. That is not a
perimeter on its own, but it is a hint that the parameterization
is local: each result is real on its own, but the structure does
not extrapolate freely. A second or third such non-transfer would
start to look like a perimeter.

**The discipline**, when proposing a future result that depends
on the parameterization, has a framing-invariant form: rewrite the
question as **what is `n_k`, given what data?** If the data
includes any injective function of `n_k` — the diagonal cell, the
first cell of the row, the row-wise minimum of the cells, the GCD
of the row, or any other obvious extraction — stop. The answer is
whatever inversion you can write down in one line, and the
experiment is moot. Write the trivial extraction down honestly and
move on. This rewrite is vocabulary-independent: it lands the same
way whether the question comes wearing tables, patches, multi-sets,
walks, or whatever framing the next surprise wears. Foothold and
perimeter are symmetric outcomes — both are findings, both locate
something real about the construction. The discipline is to identify
which one a given result is, not to default to either.

**The operational shape: recovery, dynamics, and transport.** The
discipline above has a sharper version that classifies questions in
advance. The classification has *three* buckets, not two. The
first two are easy to state; the third is where most of the
remaining ambiguity lives.

*Recovery questions* — "given some view of the n-prime table, can
we reconstruct the row list, the row labels, or some property of
the cells?" — live in the definition. The construction is one
scalar per row, and any injection from data to scalar inverts
trivially. Expect these to collapse; they have, three times. The
abductive key, the cascade key, the greedy extraction, plot 3, and
plot 9 are all recovery-flavored.

*Dynamical questions* — "given the stream produced by the
construction, how does it behave under operations that are not
part of the construction (multiplication, addition, RLE, Walsh,
PCA, sieving by `v_2`, leading-digit extraction)?" — live in the
discovery layer. The leading-digit uniformity from
`core/BLOCK-UNIFORMITY.md`, the bit-balance closed forms in the
binary subtree, the Walsh signatures, the rolling shutter
relationship between addition and multiplication — none of these
are in the definition. They are statements about what the
construction does *under transformations the construction did not
specify*. The rank-1 perimeter worry does not bite them on the
input side, though see the prediction below for how it can bite
on the *output* side.

*Transport questions* — "does the structure survive perturbation,
extend to a related construction, or appear as a hidden substrate
in an unrelated object?" — are the third bucket and the one the
recovery/dynamics dichotomy alone misclassifies. Plot 4's open
question (does the cascade survive splicing rows from different
ACM-like constructions?) is transport. Plot 7 (does the
mixture-of-uniforms argument carry over to a BIDDER row-family
extension?) is transport. Plot 2 (does an arbitrary OEIS sequence
have the abductive-key structure hidden inside?) is transport.
None of these are pure inversion-from-cells, and none of them are
pure stream-under-operation. They ask whether the structure
*travels* between settings the construction did not anticipate.

Transport questions are where the foothold/perimeter question
genuinely bites, because some transport claims are vacuous (the
structure trivially extends because the construction's definition
admits the extension) and some are real (the structure
non-trivially survives because of something the original
construction did not specify but happens to support). The
recovery/dynamics first-sieve doesn't help with transport
questions; the discipline question needs to be applied at one
level higher than for recovery: not "is the answer in the
definition" but "is the *transport itself* in the definition, or
is it genuinely about the structure crossing into a setting the
definition did not address?"

**The classifier, in one line each.** *Recovery*: given cells,
recover something about the rows. (Will collapse.) *Dynamics*:
given the stream, behavior under `T`. (May be hard.) *Transport*:
does the structure survive perturbation / extension / recognition
in a different setting. (Hard or vacuous; check carefully.)

Most of what we have built so far is recovery-flavored, and the
recovery side has been collapsing as expected. Most of what is
*unbuilt and worth building* is split between dynamics (the binary
stream's behavior under operations, the open question about finite
automata) and transport (plot 7, plot 4's perturbation question,
plot 2's OEIS sweep). Plot 7 is the highest-payoff transport
question and the highest-payoff unbuilt experiment full stop.

**One edge case worth flagging.** *Partial-data* recovery — the
"partial multi-set" follow-up sketched in "What's still open"
below — looks like a recovery question but is structurally closer
to dynamics. Greedy collapses the full-data version because the
row labels are exposed as row-wise minima of the complete
multi-set, but the partial version asks "as the data arrives,
when does each row become recoverable?" That is a question about
the *dynamics of the data stream as it arrives*, not just about
the table. The recovery-collapses heuristic does not bite there.
The partial multi-set follow-up is worth building *despite* the
discipline above, because it lives on the dynamics side of the
distinction even though its surface presentation is recovery-
shaped. The lesson: surface presentation can mislead. The
discipline question — "what is the transformation a function of,
and is the answer in the construction or in the operation?" —
needs to be asked at the right level.

**A sharpened prediction: operation-side collapse.** The next
surprise will probably *not* be another recovery collapse. The
recovery side has been mined out and the discipline above should
catch any further attempts on contact. The next surprise will
probably arrive on the dynamics side, but in a specific failure
mode that the discipline as currently stated does not catch:
**a supposedly dynamical observable will turn out to factor
through a tiny invariant**. Residue data, valuation data,
digit-block counts, a finite-state summary, a low-rank Walsh
support — some rich-looking transform of the stream will turn out
to depend on far less of the stream than expected, and the
"dynamics is where the genuine work lives" framing will need
qualification.

**This is not hypothetical.** The binary subtree of the project
already shows the pattern in three places: bit balance has a
closed form depending only on `v_2(n)` (a tiny invariant);
the Walsh signature collapses to ~44 robust universal cells out
of 1024 (a low-complexity support); the conjecture that no finite
automaton recognizes binary ACM streams is the *contrapositive* of
this prediction — it asserts that ACM streams are *not* finite-
state, against an implicit worry that they might be. If a fourth
surprise comes, it will probably be a result on the n-prime
construction proper that mirrors one of these binary findings:
the kind of result where a transform you expected to spread
information evenly turns out to concentrate it.

**Two-sided discipline.** The single-question discipline above
("is the answer already in the definition?") is a check on the
input side: it asks whether the recovery question has content.
The operation-side prediction implies we also need a check on
the output side: **is the chosen observable reducible to a
low-complexity invariant of the stream?** Both questions need to
come back "no" before we trust a result. The full discipline:

  1. *Input side.* What is `n_k` (or, more generally, the
     answer-shaped quantity), given what data? If the data
     includes any injective function of `n_k`, the question is
     recovery in costume and will collapse. Stop.
  2. *Output side.* What is the chosen observable (or transform)
     a function of? If it factors through a small invariant —
     `v_p(n)` for some prime `p`, a digit-block count, a
     finite-state summary, a low-dimensional Walsh support — the
     question is operation-side collapse and the observable is
     not seeing what you thought it was seeing. Stop, or
     reframe to ask whether the small invariant *itself* is
     interesting.

The fourth surprise, when it comes, will most likely fail check
(2) rather than check (1). Watch for it.


## What's still open

The original conjecture is resolved. The interesting follow-up is
the **partial multi-set version**: what happens when the receiver
has only some of `V`?

Two natural sub-versions:

- **Cantor walk prefix.** The receiver gets the first `m` cells in
  Cantor antidiagonal order, as an unordered multi-set (so they
  know `m` and that the cells came from the first `m` walk steps,
  but not which value corresponds to which step). For each `m`,
  ask: how many rows are reconstructable? This is the unordered
  analog of plot 5's recovery curve. Greedy needs all `N` cells of
  row `k` to peel off `n_k`, and the latest cell of row `k` in
  Cantor order is `(k, N)` at antidiagonal `k + N`, so the
  unordered Cantor recovery is *quadratic in `(k + N)`* — slower
  than the ordered version.

- **Random sample of size `m`.** The receiver gets `m` random
  elements of `V`. For each `m`, ask: success rate of greedy
  reconstruction. This is a sample-complexity question. Greedy
  needs row `k`'s cells to be present in full for each `k`, so the
  threshold is probably close to `m = N²` — but the per-row
  breakdown is unknown.

Either sub-version is non-trivial because greedy fails as soon as
even one cell of a row is missing. The picture is the same shape
as plot 5's recovery curve, and the harness in `recovery_curves.py`
plus the verifier in `verify_greedy.py` provide the substrate. The
solver itself is just greedy with a "have we seen all cells of the
candidate row?" check.

The Cantor walk prefix version is the one I'd build first. It
extends plot 5's story directly and the picture overlays on plot
5's recovery curve panel.
