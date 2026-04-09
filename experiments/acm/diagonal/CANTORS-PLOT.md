# Cantor's Plot

A garden of ideas planted around the abductive key
(`core/ABDUCTIVE-KEY.md`). The result there is one sentence: in the
strict-ascending regime the n-prime table is a rank-1 outer product
in its leading triangle, and dividing the diagonal by position
recovers the row labels. The expeditions below all start from that
observation and walk in different directions — some computational,
some mathematical, some applied.

Several of the plots are different geometric questions on the same
object: the **composite lattice** `{(k, n) : 1 ≤ k < n}`, where each
point `(k, n)` represents the composite `k · n`. A row map `k → n_k`
is a curve through the lattice; the diagonal stream `D_k = k · n_k`
is the image of that curve in the integers. Plots 1, 2, 3, 5, 8,
and 9 are different faces of one question — *what are the natural
geometries on this lattice* — and naming the lattice up front makes
the through-lines visible.

A second through-line connects plots 4 and 7. Both ask: "local
pieces have a clean structure individually; can they be stitched
into a global structure without losing the property, and what
parameter does the stitching require?" In plot 4 the local pieces
are rank-1 patches of the n-prime table and the stitching parameter
is `n_k`. In plot 7 the local pieces are per-monoid digit-class
blocks and the stitching parameter is the alignment of digit-class
boundaries. The same abstract obstruction shows up in two places.

Each gets a subfolder in `experiments/acm/diagonal/`.


## Status

**Built (5):** plots 3, 4, 5, 8, 9 — full results in the *Built
experiments* section below.

**Planned (4):** plots 1, 2, 6, 7 — original sketches in the
*Planned experiments* section below.

**Recorded as a follow-up but not yet built:** the unordered
antidiagonal recovery conjecture, in
`cantor_walk/UNORDERED-CONJECTURE.md`. Plot 5's harness provides
the substrate; the solver itself is the new code that's missing.

**Substrate files produced so far:**

| file | source | contents |
|---|---|---|
| `witness_density/witnesses.npz` | plot 3 | 820 composites up to 1000 with non-trivial witness lists `(k, N/k)` |
| `cheapest_sieve/winners.npz` | plot 9 | the same 820 composites with their winners under three cost functions |
| `complementary_curves/pairs.npz` | plot 8 | 28 row-map pairs with union/intersection/symmetric-difference statistics at `x = 10000` |


## What we've learned so far

### What works as predicted

**The composite lattice is the right central object.** Plot 3 made
it visible. Every composite `N ≥ 4` with at least one non-trivial
witness lives at integer points `(k, n)` with `k · n = N` and
`2 ≤ k < n`. Row maps are curves through this lattice; row map
images are the curves' projections onto the integers. The lattice
scatter is now the canonical reference visualization, and
`witnesses.npz` is consumed by plots 8 and 9 directly.

**The cascade key works as predicted.** Plot 4 confirmed the rank-1
staircase structure. For row `k` of the n-prime table, the cells
factor as `j_{k'} · n_k` where `j_{k'} = k' + ⌊(k' − 1)/(n_k − 1)⌋`,
giving patches of width `n_k − 1` separated by single-step jumps
where the `j` sequence skips a multiple of `n_k`. The diagonal cell
`(k, k)` lies in the first patch by exactly the strict-ascent
inequality, and once `n_k` is decoded from there, every later patch
in row `k` decodes too — `j_{k'}` is computable from `k'` and `n_k`
alone. The framing "one key, all locks in row `k`" is now vivid.
The cascade plot's verification (brute-force sieve compared to the
closed-form expression) caught a formula error before rendering and
forced us to fix it; the formula in this document is the corrected
version.

**Recovery rate is geometric, calibrated by slope match.** Plot 5
quantified the main-diagonal, Cantor-antidiagonal, and row-by-row
walks. The diagonal recovers row `k` at step `k` (linear). Cantor
recovers it at step `k(k+1)/2` (quadratic in `k`, equivalently
`√(2m)` rows after `m` steps). Row-by-row recovers it at step
`(k − 1) · N + 1` (linear with giant slope `N`). All three reach
the same recovery cells `(k, 1)` in column 1; the difference is the
*order*, and the order is determined by how the walk's slope
relates to the rank-1 region's boundary. The diagonal is optimal
because its slope matches the boundary exactly. The plot makes this
visible as a rate, not just a structural condition.

### What surprised us

**The cost_diag / cost_prime split is structural and points one
way.** Plot 9 swept three cost functions over the witness pairs:
`cost_k` (smallest `k`), `cost_diag` (smallest `n − k`), and
`cost_prime` (`|n − p_k|`). `cost_diag` and `cost_prime` agree on
**73%** of composites and disagree on **27%** (221 of 820). The
disagreement analysis (`cheapest_sieve/disagreements.py`) showed:

- 215 of 221 disagreements are *structural* (not tie-breaking
  artifacts).
- **Every single disagreement** has `prime_k < diag_k`. Without
  exception. `cost_prime` always shifts the winner up-and-left in
  the lattice — toward smaller `k` and larger `n`.
- Disagreements concentrate sharply on highly composite numbers.
  Mean witness count: **6.08** for disagreements vs **1.96** for
  agreements. Zero disagreements have a single witness.
- The disagreement rate grows monotonically with `N`: 15.7% in
  `[4, 100]`, 25.8% in `[101, 500]`, 29.7% in `[501, 1000]`. The
  27% headline is specific to `[4, 1000]`; bumping the bound would
  push it higher.

The geometric reason is clean. The most-balanced witness sits at
`(k_max, n ≈ √N)` which is *below* the prime curve `p_k` for
typical `k`. To get closer to the prime curve, you have to move to
smaller `k` where `N/k` has grown enough to meet `p_k`. The sweet
spot is where `k · p_k ≈ N` — composites whose divisor structure
includes a witness near the prime row map.

**`cost_k` is structurally separate from the balance costs.** The
cost_k panel of plot 9 shows a comb of vertical strips at columns
2, 3, 5, 7 — *not* a curve through the lattice. The reason is that
"smallest divisor `≥ 2`" of any composite is just its smallest
prime factor, so cost_k winners are organized by smallest-prime-
factor, which is a comb structure rather than a curve. Cost_k can
*never* serve as a candidate row map for plot 8; it's a
fundamentally different kind of object.

### What didn't transfer

**Plot 9's prime-curve insight does not carry over to closed-form
row maps.** Going into plot 8, plot 9 had predicted that
`(pronic, prime)` would top the complementary-curves leaderboard,
on the reasoning that the prime row map covers exactly the
27% disagreement subset. The actual result put `(pronic, prime)` at
**rank 12 of 28**.

The reason: `cost_prime` in plot 9 is a *witness selector*. For
each composite it picks the witness *closest to* the prime curve,
even if not exactly on it. Highly composite `N` like 60, 72, 84
have witnesses near (but not on) the prime curve, and `cost_prime`
picks them up. The *prime row map itself* (`n_k = p_k`) is a
*generator*: it walks one specific witness `(k, p_k)` per `k`, and
its image is the sparse arithmetic sequence
`{2, 6, 15, 28, 55, 78, 119, …}`. Most composites `cost_prime`
likes are not in this sequence — they're *near* it.

**Selectors work in 2-D (pick from any witness pair); generators
work in 1-D (walk one curve).** The two pictures of "natural row
map" don't merge cleanly, and we don't have a generator-side
analogue of `cost_prime`'s selector behavior.

### What's degenerate at this scale

**Complementary curves at `x = 10000` is dominated by individual row
map size, not by complementarity.** Plot 8 swept 8 closed-form row
maps and computed all 28 pair statistics. Every pair has disjoint
rate in `[0.974, 1.000]` — the variation is under 3 percentage
points. Three pairs tied at the top: `(pronic, shift_2)`,
`(pronic, shift_3)`, `(shift_2, shift_3)`, all at union = 196 with
zero overlap. They win by being the three densest row maps in the
sweep, not by being especially complementary. The original
"60–70% disjoint coverage threshold" from this document is cleared
by every pair by a wide margin.

The structural reason: each row map below `x = 10000` catches
`O(√x) ≈ 100` composites, and the lattice has `O(x) = 10000` cells,
so the chance of two random row maps catching the same composite is
`O(1/√x) ≈ 1%`. **Disjointness is essentially free at this scale.**
The complementary-curves question only becomes meaningful at much
larger `x` where row maps are dense enough to collide, or with a
metric that scores coverage of a *structured* subset rather than
counting raw collisions.

### What's still open

- **Unordered antidiagonal recovery**
  (`cantor_walk/UNORDERED-CONJECTURE.md`). Original conjecture is
  **resolved at `f(N) = 0`** — greedy reconstructs the row list
  from the full multi-set with zero hints. Proof and a 15-row-list
  battery in `cantor_walk/verify_greedy.py`. The interesting
  follow-up is the *partial* multi-set version (Cantor walk
  prefix or random sample), whose picture overlays on plot 5's
  recovery curve.

- **Knife-edge caveat about productive triviality**
  (`cantor_walk/UNORDERED-CONJECTURE.md`, "The knife-edge"
  section). The leaky parameterization that makes greedy work,
  the cascade decode, and the abductive key itself is now
  responsible for three "obvious in retrospect" inversions in a
  row. That triviality is either a *foothold* (rich consequences
  from a trivial surface) or a *perimeter* (no structure beneath
  the surface, every result a relabeling) — and we are operating
  in a constructed space, so the perimeter risk is sharper than
  usual. The discipline: when proposing a result that depends on
  the parameterization, ask whether it gives us a quantity not
  already in the definition; when in doubt, prefer the perimeter
  reading.

- **Plot 4's open question on perturbed cascades.** Is there a
  table — built from spliced rows of different ACM-like
  constructions, or perturbed by inserting phantom skips — where
  the diagonal opens the first patch but the dependence on `n_k`
  is somehow not enough to open the next? Intuition says no for
  any single-row-list table; a counter-example would mean splicing
  breaks the cascade.

- **The plot 4 ↔ plot 7 parallel** is structural evidence but not
  proof. Plot 4's cascade going through cleanly is *evidence* that
  plot 7's BIDDER family extension is well-behaved (mixture-of-
  uniforms argument), but it's not a proof that the digit-class
  alignment works. Plot 7 is the highest-value experiment in the
  garden and remains unbuilt.

- **Plot 8 at larger scale.** At `x = 10^6` or `10^8`, row maps
  catch enough composites for collisions to matter. The current
  sweep would not need much modification — bump `X` and rerun.
  The interesting question is whether the leaderboard reorders.


## Built experiments

### 3. The divisor function in a sieve costume

`diagonal/witness_density/`

For a composite `N`, ask at how many positions `k` could `N` appear
as a diagonal entry in some row map. The constraint is `k | N` and
`k < √N`. The witness count is `⌊d(N)/2⌋ − 1` for non-squares (with
`k ≥ 2` excluded) — half the divisor function minus one for the
trivial `k = 1` witness.

**Result.** Built as `lattice_scatter.py` plus `witnesses.npz`. The
scatter renders the composite lattice for `k · n ≤ 100` with five
viridis bins `[6, 12, 20, 35, 60, 100]`, three row-map curves
overlaid (`pronic`, `2k+1`, `p_k`), and the hyperbola `k · n = 60`
called out with its 5 non-trivial integer witnesses. The
substrate file `witnesses.npz` (820 composites up to 1000) is the
canonical input for plots 8 and 9. The "this is the divisor
function in a costume" framing is honest — the curve as a whole is
just `d(N)/2 − 1` — but the lattice picture is genuinely useful as
the central reference visualization for the rest of the garden.

### 4. The cascade key

`diagonal/cascade_key/`

The rank-1 leading triangle ends at the column boundary
`k' = n_k − 1`, where the n-prime sequence first skips `n_k · n_k`.
Past that boundary the entries are still products `j_{k'} · n_k`,
where `j_{k'} = k' + ⌊(k' − 1)/(n_k − 1)⌋`. So each patch is
`n_k − 1` columns wide, and the patches are separated by
single-step jumps where the `j` sequence skips a multiple of `n_k`.
The full table is a *staircase of rank-1 patches*.

The structural payoff is the cascade. The abductive key decodes the
first patch, which yields `n_k`. Once `n_k` is in hand, every later
patch decodes too. The right framing is **not** "later patches
admit their own keys" — it is "there is one key, the diagonal, and
once turned it opens every lock in row `k`."

**Result.** Built as `cascade_grid.py` plus `cascade_grid.png`. The
heatmap shows the row list `{5, 7, 11, 13, 17, 19}` × 60 columns,
colored by patch parity. Each row's stripe pattern has width
`n_k − 1`, and the diagonal cell `(k, k)` for each row sits visibly
inside its first stripe — the strict-ascent inequality made
geometric. The brute-force sieve assertion in the script caught an
off-by-one error in our first-draft formula, which is why this
document now uses `j_{k'} = k' + ⌊(k' − 1)/(n_k − 1)⌋` rather than
`k' + ⌊k'/n_k⌋`. The open question (perturbed cascades) is recorded
above and not yet built.

### 5. Antidiagonal walks

`diagonal/cantor_walk/`

Cantor enumerates `ℕ × ℕ` by antidiagonals. The abductive key uses
a single main diagonal. Both walks reduce a 2-D object to a 1-D
sequence, and both can recover row labels from a prefix — but at
very different rates. The diagonal recovers row `k` at step `k`
(linear). Cantor's walk recovers it at step `k(k+1)/2` (quadratic
in `k`).

**Result.** Built as `recovery_curves.py` plus `recovery_curves.png`,
a two-panel figure for the contiguous row list `n_k = k + 1` with
`N = 20`. The left panel shows the rank-1 region (lower triangle)
with three walks overlaid: the diagonal as a single line tracing
the boundary, Cantor's antidiagonals as perpendicular sweeps in the
upper-left triangle, and row-by-row as horizontal sweeps. The right
panel shows the recovery curves: linear (diagonal), step-function
sqrt (Cantor), and large-plateau staircase (row-by-row), reaching
20 rows recovered at steps 20, 210, and 381 respectively. Closed-
form recovery positions are asserted against direct simulation in
the script.

The follow-up question — recovery from an *unordered* stream of
cell values, parameterized by hint count — is recorded in
`UNORDERED-CONJECTURE.md` and not yet built.

### 8. Complementary curves

`diagonal/complementary_curves/`

A row map `k → n_k` traces a curve through the composite lattice,
and its diagonal stream is the image of that curve in the integers.
The complementary-curves question is: which finite collections of
ascending row maps trace curves whose diagonal images *together*
cover the composites with little overlap? The clean version is a
2-coloring of the lattice such that each color class is the graph
of an ascending function.

**Result.** Built as `complementary_curves.py` plus
`complementary_curves.png` (heatmap of joint coverage on the left,
Pareto scatter of coverage vs disjoint rate on the right) and
`pairs.npz` (substrate). Eight row maps, 28 pairs, computed at
`x = 10000`.

The headline result is **negative**: the complementary-curves
question is degenerate at this scale. Every pair has disjoint rate
in `[0.974, 1.000]`. The leaderboard collapses to "rank by
individual row map size": three pairs tie at the top
(`(pronic, shift_2)`, `(pronic, shift_3)`, `(shift_2, shift_3)`),
all at union = 196 with zero overlap. The plot 9-informed
prediction `(pronic, prime)` is at rank 12 of 28.

The negative result clarified two things: (1) closed-form ascending
row maps below `x = 10000` are too sparse to collide, so
"complementary" isn't a meaningful filter at this scale; (2) plot
9's `cost_prime` is a witness *selector*, while `n_k = p_k` is a
generator, and selector behavior doesn't transfer to generator
coverage. To make the question well-posed, push `x` substantially
or change the metric to score coverage of a structured subset.

### 9. Inverse problem: cheapest sieve per target

`diagonal/cheapest_sieve/`

The optimization-side dual of plot 3. Given a target composite `N`,
find the *cheapest* witness `(k, N/k)` under several cost functions.
Plot 3 asks "how many sieves catch this number"; this plot asks
"what is the simplest sieve that catches this number" under each
of three notions of "simplest."

**Result.** Built as `cheapest_sieve.py` plus `cheapest_sieve.png`
(three panels, one per cost function) and `winners.npz` (substrate
mapping each composite to its winner under each cost). The three
costs are:

- `cost_k = k` (catch `N` at the earliest position)
- `cost_diag = n − k` (most balanced factorization)
- `cost_prime = |n − p_k|` (closest to the prime row map)

The original cost proposal had `cost_diag` and `cost_slope = n/k`
as two separate costs, but the build phase caught that they're
mathematically equivalent on this problem (both monotonic in `k` for
fixed `N`, both pick the largest valid `k`). `cost_slope` was
replaced by `cost_prime` to get a non-monotonic cost.

Headline numbers (over 820 composites in the substrate):

```
all three agree:        35.98%   (295 / 820)
cost_k    + cost_diag:  35.98%   (artifact: cost_k only agrees on single-witness composites)
cost_k    + cost_prime: 35.98%   (same artifact)
cost_diag + cost_prime: 73.05%
```

The 73% diag/prime agreement is the only nontrivial number. The
remaining 27% is the "interesting subset" that the disagreement
follow-up (`disagreements.py`) characterized: 215 structural
disagreements (out of 221 total), all pointing in the same
direction (`prime_k < diag_k`), all concentrated on highly composite
`N` with mean witness count 6.08 vs 1.96 for agreements. The
geometric reason is that the prime curve sits *above* the most-
balanced witness, so to get closer to the prime curve you have to
move to smaller `k` where `N/k` has grown enough to meet `p_k`.

The cost_k panel is qualitatively different from the other two:
it's a *comb of vertical strips* at columns `2, 3, 5, 7`, because
"smallest divisor of `N` that's ≥ 2" is just the smallest prime
factor. Cost_k cannot serve as a candidate row map for plot 8 — it
is a fundamentally different kind of object than `cost_diag` and
`cost_prime`.


## Planned experiments

### 1. Lossy Eratosthenes

`diagonal/lossy_eratosthenes/`

Pick any function `k → n_k` with `n_k ≥ 2` and emit `D_k = k · n_k`
for `k = 1, 2, …`. Every entry past the first is composite, with a
witness factor `k` available from position alone. This is a
single-parameter, storage-free composite generator: no array, no
crossing-out, no second index. It is "lossy" because the row map
fixes which composites get caught and most do not.

Two regimes to keep separate. As a *reading* of an existing ACM
table, the row map needs strict ascent and `n_k ≥ 2` — those are
the hypotheses of the abductive key. As a *generator* of factor-
tagged composites, the row map needs nothing at all: any function
`k → n_k` produces a valid `D_k = k · n_k`. The lossy-sieve
application lives in the second, freer regime.

The right cost axis is composites caught per (time × space), not
coverage. With pronic row map `n_k = k + 1`, the abductive sieve
emits `O(√x)` composites in `O(√x)` time and `O(1)` space —
asymptotically *better* than Eratosthenes on throughput, by a
factor of `x log log x`. It just covers a sparse subset.

Pieces to build: a generator that streams `(k, k·n_k, n_k)` triples
for several natural row maps (`k+1`, `2k+1`, `k`-th prime, smallest
squarefree `≥ k+1`); a visualization for each row map showing
which integers below `x` are caught; a side-by-side throughput
comparison with classical Eratosthenes at the same `x`.

**Note (post plot 8):** the row maps in this experiment overlap
heavily with plot 8's candidate set, and the row-map sizes are
already known from `pairs.npz`. The plot 8 negative result —
"complementary at this scale is degenerate" — is also relevant
here: at `x = 10000` the row maps catch ~100 composites each, and
their fingerprints will look similar in coverage maps. Plot 1
should probably target a much larger `x` (or a much smaller window
with rich texture) to be visually distinctive.

### 2. Rank-1 sweep on integer sequences

`diagonal/rank1_sweep/`

Decoupled from ACM language, the abductive test is a structural
test on integer sequences: `s_1, s_2, …` is the diagonal of a
rank-1 outer product of `(1, 2, 3, …)` with an ascending integer
sequence iff `s_k / k` is an integer for every `k`, the quotients
are strictly ascending, and all quotients are `≥ 2`. The test is
one pass. It says nothing about ACMs per se — it is a property of
integer sequences that happens to make ACM diagonals one of its
catches.

Run that test against a local mirror of OEIS b-files. Most
sequences will fail. The interesting hits will not be sequences
whose closed form contains an obvious `k` factor; they will be
sequences defined recursively or combinatorially where the rank-1
substructure is hidden. For each hit, record whether the OEIS
prose mentions an outer-product form.

A second pass for sequences that fail strict ascent: check whether
a *prefix* passes, and record the index at which each sequence
first drifts off the rank-1 substructure. The drift index is
itself a number worth computing per sequence — sequences that are
rank-1 for their first few terms and then drift may have local
rank-1 structure that some combinatorial construction is generating
before another constraint takes over.

### 6. Factor-rich test fodder

`diagonal/factor_stream/`

A diagonal stream is a sequence of integers each carrying a known
nontrivial factorization, *and* tagged by emission position. The
position is not metadata bolted on — it is one of the two factors,
recoverable as `k = D_k / n_k` or just as the streaming index.
Every composite in the stream points at its own `k`, which makes
the stream self-instrumenting: when a downstream consumer fails on
some `D_k`, the failure points at its own position, and the row
map's structure near that position is what the consumer is reacting
to.

Build a generator that emits `(k, k·n_k, n_k)` from a chosen row
map and pipe it into adversarial testing of primality routines,
factoring code, and sieve implementations as a fuzzer harness. A
free, stateless, tunable-density supply of position-tagged factor-
rich integers is genuinely useful infrastructure for the rest of
the project, and the kind of tool you will be glad to have built
whether or not it leads to a paper.

### 7. BIDDER row-family extension

`diagonal/bidder_family/`

The highest-value plot in the garden. BIDDER currently parameterizes
its substrate on a single monoid `n`. The abductive key suggests
BIDDER could instead parameterize on an entire ascending row list
and carry the commitment in one diagonal sequence.

The right way to ask the question is via mixtures. For a single
monoid `n` in base `b` at digit class `d`, the leading-digit
distribution is exactly uniform on `{1, …, b − 1}`. For a family
`{n_1, …, n_N}` sampled with weights `w_i` summing to 1, the
family-level distribution is

    Σ_i  w_i · uniform({1, …, b − 1})  =  uniform({1, …, b − 1}),

because a convex combination of identical uniforms is the same
uniform. So the family-level distribution *is* exactly uniform —
provided the weights sum to 1 and each per-monoid distribution is
itself exactly uniform. The condition that could break it is digit-
class boundaries: different monoids in the family have different
natural block sizes, and aligning them at full digit-class
boundaries may require a CRT-style argument to make the boundaries
commensurate. If alignment fails, the mixture is over *partial*
per-monoid blocks and the per-monoid uniformity guarantee no longer
holds.

This is the same question as `generator/BIDDER.md` open question 1
("composition") in different clothes, and the abstract obstruction
is the same as plot 4's cascade-stitching question. **Plot 4's
cascade has now been built and works as predicted**, which is
structural evidence (not proof) that plot 7 is well-behaved. Plot 7
remains the highest-payoff unbuilt project in the garden.


## Open follow-ups (recorded, not started)

- **Unordered antidiagonal recovery** —
  `cantor_walk/UNORDERED-CONJECTURE.md`. Conjecture: `O(log N)`
  hints suffice. Solver is the new code; harness is in plot 5.

- **Perturbed cascade counter-example search** — plot 4's open
  question. Splice rows from different ACM-like constructions and
  test whether the cascade decoding still works. No script yet.

- **Plot 8 at larger scale** — bump `X` from `10000` to `10^6` or
  `10^8` and re-run. The current sweep code is unchanged; only `X`
  changes. The interesting question is whether the leaderboard
  reorders when collisions become non-trivial.

- **Plot 8 with a structured-subset metric** — instead of disjoint
  rate, score pairs by coverage of the disagreement subset from
  plot 9 (`cheapest_sieve/winners.npz`). This directly tests
  whether the prime row map is genuinely useful for the *interesting*
  composites, not just the easy ones.


## Where to go next

Three paths, in order of how strongly I'd recommend them:

**1. Plot 7 (BIDDER row-family extension).** Highest payoff in the
garden, and now best-supported by structural evidence: plot 4's
cascade went through cleanly, and the abstract obstruction in plot 7
is the same shape. The mixture-of-uniforms argument is half-written
in this document already. The work is to operationalize it against
the BIDDER substrate (`generator/BIDDER.md`'s composition question),
which is not a small build but is the most important unbuilt thing.

**2. Plot 2 (rank-1 sweep on integer sequences).** Concrete,
computational, and tests the rank-1 framing in a domain that has
nothing to do with ACMs. The expected output is a list of OEIS
sequences that pass the rank-1 test and a list that pass on a
prefix. Either list is informative. The downside is that it
requires an OEIS mirror or some equivalent local data source —
small infrastructure cost.

**3. Plot 8 follow-ups.** The negative result is informative but
the question can probably be made well-posed at larger scale or
with a structured metric. Cheapest of all the options, because the
existing sweep just needs `X` bumped or a new score function. Worth
doing as a follow-up to confirm whether the negative result is a
small-scale artifact or a fundamental property.

The unordered conjecture (`UNORDERED-CONJECTURE.md`) is also
genuinely interesting but has more new infrastructure to build (the
solver) than the three above. I'd hold it for after at least one of
the three above gets done.

Plot 1 (Lossy Eratosthenes), plot 6 (factor-rich fodder), and plot
4's perturbed-cascade follow-up are all valuable but lower priority
right now: plot 1 mostly retreads ground that plot 8 already
covered, plot 6 is engineering rather than investigation, and the
perturbed-cascade question is more interesting once we have plot 7
to motivate it.
