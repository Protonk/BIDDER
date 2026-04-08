# Valuation Forest

Expedition 7 of [MALLORN-SEED.md](../MALLORN-SEED.md).

The seed's question: **does 2-adic depth predict the binary stream
signature of an ACM monoid?** This expedition answers it three ways.
V1 lays the depth structure out as a literal Cartesian forest. V2
redraws the same data as a polar fan. V3 subtracts the depth-only
prediction and shows what survives.

The substrate, the layout choices, the order of operations, and the
file plan live in [VALUATION-PLAN.md](VALUATION-PLAN.md).

## What the forest grid shows

The figure is a Cartesian forest. There are 256 odd-rooted trunks,
one per odd `m ≤ 511`, arranged left to right in order of `m`. The
trunk for `m = 1` is the powers-of-2 spine and is the longest in
the figure: ten nodes from `n = 1` down to `n = 512`. The next
trunks shorten quickly. `m = 3` has eight nodes (`3, 6, 12, …, 384`).
`m = 5` and `m = 7` have seven nodes each. By `m = 17` the trunks
are five nodes; by `m = 65` they are three; everything from
`m = 257` onward is a single solitary node sitting at depth zero.

Each node is colored by mean zero-run length: light at the crown
(low `v_2`, short zero-runs), dark at the base (high `v_2`, long
zero-runs). The widest color range belongs to the `m = 1` spine,
which traverses the deepest range of `v_2` values and reads as a
column descending from light cream at the top through orange and
magenta toward near-black at `v_2 = 9`. Shorter trunks descend
through narrower color ranges and read as faded copies of the
spine.

The top two rows of the forest are nearly indistinguishable. The
`v_2 = 0` and `v_2 = 1` row means are flat to three decimal places
(`1.926` and `1.929`), and most trunks show no visible color step
between their crown node and the node immediately below it. The
trunk darkening that the bit-balance argument of
[HAMMING-BOOKKEEPING.md](../../HAMMING-BOOKKEEPING.md) predicts
becomes visible at `v_2 = 2` and accelerates from there. From the
`v_2 = 2` level downward every trunk in the figure descends
monotonically.

The image reads as an actual forest: a leftmost dark evergreen
spine with a wide stand of shorter trees behind it, each tree
darker at its base than at its crown. The visual repetition of
"darker at the base" is the bit-balance theorem doing its work in
the picture, with the very top of every trunk held back by a
`v_2 = 0/1` plateau the theorem does not yet distinguish.

## What the spiral chains image shows

The figure is polar. The outer rim is a dense circle of 256 points,
one per odd `m`, all colored at the lighter end of the scale because
`v_2 = 0` everywhere on the rim. Each odd `m ≤ 256` anchors a spiral
arm that winds inward as `v_2` increases; the 128 odd `m` between
`257` and `511` contribute only a single rim point and no inward
arm.

The 128 inward arms occupy the right hemisphere of the figure. The
odd parts that have inward chains are the small odd parts, and they
map to small angular ranks, which sit in `θ ∈ [0, π]`. The arm for
`m = 1` is the longest and reaches the very middle as the
powers-of-2 spiral. Shorter arms shorten quickly: `m = 3` has seven
inward steps, `m = 5` has six, and the deepest tip of any arm
except `m = 1` sits well outside the central vortex.

Color descends along each arm from the rim inward, lightest at the
outside, darkest at the inward tip. The cumulative effect is a fan
of arms shading from a bright outer rim toward a dark central
vortex. The vortex itself is sparse — only the few longest chains
reach deep — so the centre reads as a clean dark hole rather than as
a crowded smudge.

The polar coordinate is generous to the inward arms in a way the
Cartesian grid is not. What the eye sees is a fan with a
singularity, which is what the algebra has been claiming all along:
the integers really do cluster around `v_2 = ∞` in 2-adic space,
and only a small handful of long chains live deep enough to reach
the centre.

## What the residual map shows

The figure is not a tree. It is a rectangular `(odd_part_rank, v_2)`
grid in which each cell shows the residual of `mean_rle0(n)` against
the within-depth leave-one-out mean — the part of the per-monoid
mean zero-run length that is *not* explained by `v_2(n)`. Cell color
is the residual on a diverging scale; cell alpha is driven by a
blockwise z-statistic computed from the eight cached blocks of the
prefix, so cells whose residual is not stable across blocks fade
out. Rows with fewer than `MIN_V2_SUPPORT = 8` monoids (`v_2 ≥ 9`)
are repainted in neutral grey and labeled under-supported; they
hold no analytic weight in this figure.

Most of the map is faint. The gross structure of mean zero-run
length is captured by `v_2`, and once that mean is subtracted there
is no large remaining signal across the bulk of the monoids. Median
`|z_res|` stays under 1 across `v_2 = 0..6`, and creeps above 1
only at `v_2 = 7` and `v_2 = 8`, where row support is small. The
depth-only predictor is mostly enough.

But the map is not silent. The largest residuals concentrate in the
leftmost columns of the grid — at the smallest odd parts. Mean
`|z_res|` by odd part:

| `m` | mean `\|z_res\|` |
|---|---:|
| 1 | 2.59 |
| 3 | 1.75 |
| 7 | 1.26 |
| 15 | 1.09 |
| 13 | 1.02 |
| 5 | 0.90 |
| 9 | 0.89 |
| ... | |
| 99 | 0.49 |

The five small odd parts `m ∈ {1, 3, 5, 7, 9}` together carry a
median `|z_res|` of `1.26`; the other 4043 supported cells carry a
median of `0.37`. The bands at small odd parts are weak compared to
the raw signal V1 and V2 are showing, but they are coherent enough
to read as a real structural feature of the forest, not noise.

The largest single residuals come from a handful of individual
monoids in the leftmost column. The seven hottest cells in the
supported map cluster on the `m = 1` spine. `n = 2` sits below its
`v_2 = 1` row by `|z_res| ≈ 6.96`. The high powers of two — `n = 64`,
`128`, `256` — sit above their respective `v_2` rows by `|z_res| ≈
2.6, 3.6, 4.1`. The leftmost column carries both the largest
negative residual in the figure and the largest positive residuals.

The map is the analytic counterpart of the Walsh result: most of
the visible structure is `v_2`-explainable, but a real minority is
not, and the part that is not lives at specific named odd parts.
V1 and V2 dramatize how well `v_2` does. V3 is what shows where
`v_2` falls short.

## What this establishes

The three figures together answer the seed's question with a clean
qualified yes: 2-adic depth predicts the bulk of the binary stream
signature, the exceptions are real but localized, and `v_2(n)` is
one organizing variable in this family rather than the master
variable.

V1 and V2 dramatize how cleanly `v_2` does its job at the level of
the gross signal. V3 dramatizes where it falls short. The Walsh
result and the Valuation Forest result agree, in different
vocabularies, on the same boundary: depth explains most of what
there is to explain, and the interesting remainder lives in the
structure of the *odd* part — concentrated, in this experiment, at
the smallest odd parts and most prominently at `m = 1`.

The bands at small odd parts are the natural next thing to chase.
They are quiet at this resolution and they survive the blockwise
confidence test, which is the minimum bar for calling them real.
An experiment that targets them directly — at higher per-monoid
sample size, or with a signature richer than `mean_rle0` — is the
obvious continuation.
