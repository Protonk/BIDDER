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

Not built. The harness in `recovery_curves.py` provides the table
construction, the walk enumeration, the rank-1 test, and the
brute-force assertions; the unordered solver is new code that
consumes that harness. When we build it, the deliverable is one
image (a phase diagram) plus the solver itself, plus a `README.md`
recording the experiment's outcome. Same shape as plots 3, 4, 5.

The expected output is one of three answers: the conjecture holds
at `O(log N)`, holds at a weaker rate, or fails. All three are
informative, so the experiment is worth running regardless of which
way it lands.
