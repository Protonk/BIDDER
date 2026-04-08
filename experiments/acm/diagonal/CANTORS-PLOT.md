# Cantor's Plot

A garden of ideas planted around the abductive key
(`core/ABDUCTIVE-KEY.md`). The result there is one sentence: in the
strict-ascending regime the n-prime table is a rank-1 outer product in
its leading triangle, and dividing the diagonal by position recovers
the row labels. The expeditions below all start from that observation
and walk in different directions — some computational, some
mathematical, some applied.

Several of the plots are different geometric questions on the same
object: the **composite lattice** `{(k, n) : 1 ≤ k < n}`, where each
point `(k, n)` represents the composite `k · n`. A row map `k → n_k`
is a curve through the lattice; the diagonal stream `D_k = k · n_k`
is the image of that curve in the integers. Plots 1, 2, 3, 5, 8, and
9 are five faces of one question — *what are the natural geometries
on this lattice* — and naming the lattice up front makes the
through-lines visible.

A second through-line connects plots 4 and 7. Both ask: "local pieces
have a clean structure individually; can they be stitched into a
global structure without losing the property, and what parameter does
the stitching require?" In plot 4 the local pieces are rank-1 patches
of the n-prime table and the stitching parameter is `n_k`. In plot 7
the local pieces are per-monoid digit-class blocks and the stitching
parameter is the alignment of digit-class boundaries. The same
abstract obstruction shows up in two places.

Each gets a subfolder in `experiments/acm/diagonal/`. Build order
prioritized by expected payoff: **7, 4, 2** at the top.


## 1. Lossy Eratosthenes

`diagonal/lossy_eratosthenes/`

Pick any function `k → n_k` with `n_k ≥ 2` and emit `D_k = k · n_k`
for `k = 1, 2, …`. Every entry past the first is composite, with a
witness factor `k` available from position alone. This is a
single-parameter, storage-free composite generator: no array, no
crossing-out, no second index. It is "lossy" because the row map
fixes which composites get caught and most do not.

Two regimes to keep separate. As a *reading* of an existing ACM
table, the row map needs strict ascent and `n_k ≥ 2` — those are the
hypotheses of the abductive key, and they are what makes `D_k / k`
recover meaningful row labels of an actual ACM family. As a
*generator* of factor-tagged composites, the row map needs nothing at
all: any function `k → n_k` produces a valid `D_k = k · n_k` and the
recovery `D_k / k = n_k` works trivially. The lossy-sieve application
lives in the second, freer regime.

The right cost axis is composites caught per (time × space), not
coverage. With pronic row map `n_k = k + 1`, the abductive sieve
emits `O(√x)` composites in `O(√x)` time and `O(1)` space — `O(1)`
per time-space unit. Eratosthenes catches `O(x)` composites in
`O(x log log x)` time and `O(x)` space — `O(1/(x log log x))` per
time-space unit. On throughput, the abductive sieve wins by a factor
of `x log log x`. It just covers a sparse subset, and whether that
sparsity is acceptable depends on the consumer.

Pieces to build: a generator that streams `(k, k·n_k, n_k)` triples
for several natural row maps (`k+1`, `2k+1`, `k`-th prime, smallest
squarefree `≥ k+1`); the visualization companion — for each row map,
render which integers below `x` show up in the diagonal stream
(x-axis: integer line, y-axis: row-map family, color: caught vs
missed, with composite density laid behind as baseline); a side-by-
side throughput comparison with classical Eratosthenes at the same
`x`. Pronic gaps, prime-indexed gaps, squarefree gaps should each
have a distinctive texture, and the texture is the fingerprint of the
row map as a curve through the composite lattice.


## 2. Rank-1 sweep on integer sequences

`diagonal/rank1_sweep/`

Decoupled from ACM language, the abductive test is a structural test
on integer sequences: `s_1, s_2, …` is the diagonal of a rank-1 outer
product of `(1, 2, 3, …)` with an ascending integer sequence iff
`s_k / k` is an integer for every `k`, the quotients are strictly
ascending, and all quotients are `≥ 2`. The test is one pass. It says
nothing about ACMs per se — it is a property of integer sequences
that happens to make ACM diagonals one of its catches.

Run that test against a local mirror of OEIS b-files. Most sequences
will fail. The interesting hits will not be sequences whose closed
form contains an obvious `k` factor; they will be sequences defined
recursively or combinatorially where the rank-1 substructure is
hidden. For each hit, record whether the OEIS prose mentions an
outer-product form.

A second pass for sequences that fail strict ascent: check whether a
*prefix* passes, and record the index at which each sequence first
drifts off the rank-1 substructure. The drift index is itself a
number worth computing per sequence — sequences that are rank-1 for
their first few terms and then drift may have local rank-1 structure
that some combinatorial construction is generating before another
constraint takes over.


## 3. The divisor function in a sieve costume

`diagonal/witness_density/`

For a composite `N`, ask at how many positions `k` could `N` appear
as a diagonal entry in some row map. The constraint is `k | N` and
`k < √N` (equivalently, the implied row label `N/k` must exceed `k`
so that ascent can place row `N/k` at position `k`). The witness
count of `N` is therefore the number of divisors of `N` strictly
below `√N`, which is `⌊d(N)/2⌋` for non-squares and `(d(N) − 1)/2`
for squares — half the divisor function.

So the experiment as written rediscovers `d(N)/2`. The interesting
question is not the curve's shape (it is `d(N)`); it is whether
thinking of `d(N)/2` as "number of stateless one-parameter sieves
catching `N`" gives a useful new handle on a classical object. It
probably does, because it reframes divisor-counting as sieve-coverage
and connects the divisor function directly to plot 9 (the inverse
problem). Worth one paragraph and a small plot, then move on — the
heavy lifting is in plot 9.


## 4. The cascade key

`diagonal/cascade_key/`

The rank-1 leading triangle ends at the column boundary
`k' = n_k − 1`, where the n-prime sequence first skips `n_k · n_k`.
Past that boundary the entries are still products `j_{k'} · n_k`,
where `j_{k'}` is the `k'`-th positive integer not divisible by
`n_k`:

    j_{k'}  =  k' + ⌊(k' − 1)/(n_k − 1)⌋

So each patch is `n_k − 1` columns wide, and the patches are
separated by single-step jumps where the `j` sequence skips a
multiple of `n_k`. The full table is a *staircase of rank-1 patches*.
Plot it as a heatmap with the patches in alternating colors and the
skip lines overlaid.

The structural payoff is the cascade. The abductive key decodes the
first patch, which yields `n_k`. Once `n_k` is in hand, every later
patch decodes too, because `j_{k'}` is computable from `k'` and `n_k`
alone. So the right framing is **not** "later patches admit their
own keys" — it is "there is one key, the diagonal, and once turned
it opens every lock in row `k`." The patches don't have their own
keys; they have their own *locks*, all of which open from the same
key.

This sharpens the open question: is there a constructed table — one
built from spliced rows of different ACM-like constructions, or
perturbed in some natural way — where the diagonal opens the first
patch but the dependence on `n_k` is somehow not enough to open the
next? My intuition is no for any table built from a single n-prime
row, but maybe yes for spliced or perturbed tables. Worth searching
for a counter-example.

The abstract shape of the cascade — local pieces stitched together by
a single decoded parameter — is the same shape as plot 7. Building
plot 4 first gives evidence (not proof) that plot 7 is well-behaved.


## 5. Antidiagonal walks

`diagonal/cantor_walk/`

Cantor enumerates `ℕ × ℕ` by antidiagonals. The abductive key uses a
single main diagonal. Both walks reduce a 2-D object to a 1-D
sequence, and both can recover row labels from a prefix — but at very
different rates. The main diagonal recovers row `k` at enumeration
position `k`, because cell `(k, k)` is in the rank-1 region by
exactly the strict ascent inequality. Cantor's walk recovers row `k`
at enumeration position `k(k+1)/2`, when it first reaches column 1 of
row `k` (and column 1 is trivially rank-1, since `T[k][1] = n_k` for
any `n_k ≥ 2`). Linear vs quadratic.

The plot is the recovery curve — number of row labels reconstructable
as a function of steps taken — for both walks. The gap is the cost of
having position-as-decoder fail to line up with the rank-1 slope, and
it makes the diagonal's calibration to strict ascent visible as a
recovery rate rather than a structural condition.

A follow-up question worth a sentence: in an *unordered* version of
the problem — where the receiver gets cell values without knowing
which `(k, k')` each came from — how many row labels does the
receiver need handed in before the antidiagonal stream becomes
recoverable? Each antidiagonal cell value has two unknowns; each
known row label collapses one equation. A guess of `O(log N)` hints
feels right but is worth checking.


## 6. Factor-rich test fodder

`diagonal/factor_stream/`

A diagonal stream is a sequence of integers each carrying a known
nontrivial factorization, *and* tagged by emission position. The
position is not metadata bolted on — it is one of the two factors,
recoverable as `k = D_k / n_k` or just as the streaming index. Every
composite in the stream points at its own `k`, which makes the stream
self-instrumenting: when a downstream consumer fails on some `D_k`,
the failure points at its own position, and the row map's structure
near that position is what the consumer is reacting to.

Build a generator that emits `(k, k·n_k, n_k)` from a chosen row map
and pipe it into adversarial testing of primality routines, factoring
code, and sieve implementations as a fuzzer harness. A free,
stateless, tunable-density supply of position-tagged factor-rich
integers is genuinely useful infrastructure for the rest of the
project, and the kind of tool you will be glad to have built whether
or not it leads to a paper.


## 7. BIDDER row-family extension

`diagonal/bidder_family/`

The highest-value plot in the garden. BIDDER currently parameterizes
its substrate on a single monoid `n`. The abductive key suggests
BIDDER could instead parameterize on an entire ascending row list and
carry the commitment in one diagonal sequence.

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
natural block sizes, and aligning them at full digit-class boundaries
may require a CRT-style argument to make the boundaries commensurate.
If alignment fails, the mixture is over *partial* per-monoid blocks
and the per-monoid uniformity guarantee no longer holds.

This is the same question as `generator/BIDDER.md` open question 1
("composition") in different clothes, and the abstract obstruction is
the same as plot 4's cascade-stitching question. If plot 4's cascade
goes through cleanly, that is structural evidence that the alignment
problem here is also resolvable. Build plot 4 first; build this
second.


## 8. Complementary curves

`diagonal/complementary_curves/`

A row map `k → n_k` with strict ascent traces a curve through the
composite lattice `{(k, n) : 1 ≤ k < n}`, and the diagonal stream
`D_k = k · n_k` is the image of that curve in the integers. Every
composite `m` with a divisor strictly below `√m` lives somewhere in
that lattice; perfect squares `a²` migrate to position `k = 1` under
row map `n_1 = a²`. The lossy-sieve question reframes: which finite
collections of ascending row maps trace curves whose diagonal images
*together* cover the composites with little overlap?

The clean version is a 2-coloring problem. Color the lattice points
`{(k, n) : k < n}` such that each color class is the graph of an
ascending function `k → n_k`. Each color class then yields a
stateless one-parameter composite stream, and together the two
streams cover the union of their images. A strict partition of the
composites is unlikely (Beatty's theorem needs irrationals; integer
products do not partition cleanly), but a near-partition with bounded
overlap is plausible and would be the natural analog of Beatty pairs
for the abductive sieve.

The first experiment is small and concrete: take the pair
`(k+1, 2k+1)`, measure overlap and gap below `x = 10^4`, then sweep
ascending row-map pairs with simple closed forms (`k+1, k+2`;
`k+1, p_k`; `k+1, k²+1`; `2k+1, 2k+3`) and rank them by *coverage
minus overlap*. The output is a leaderboard of complementary pairs
and an empirical sense of how close to partition any pair gets. If a
pair clears 60–70% disjoint coverage of the composites below `10^4`,
the question of three-stream coverings becomes worth asking.


## 9. Inverse problem: cheapest sieve per target

`diagonal/cheapest_sieve/`

The optimization-side dual of plot 3. Given a target composite `N`,
what is the *cheapest* row map (under some natural cost on the
function `k → n_k`) whose diagonal stream catches `N`? Plot 3 asks
"how many sieves catch this number"; this plot asks "what is the
simplest sieve that catches this number."

Cost candidates worth trying: description length of a closed form
for `n_k`; slope (max `n_k / k` over the prefix needed to reach `N`);
sparsity (number of nonzero terms in some natural basis); index `k`
at which `N` first appears (smaller is cheaper because the stream
reaches `N` faster). Run each cost on the composites below some
bound, plot the cheapest-sieve-per-composite map, look at the
distribution of "winners."

The connection to plot 8 is direct. If the cheapest sieves across all
composites concentrate on a small number of curves in the lattice,
those curves are candidates for plot 8's complementary partition. If
they spread chaotically, the sieve-coverage view of `d(N)/2` from
plot 3 is bounded above by a curve-counting argument worth working
out. Either outcome is informative.
