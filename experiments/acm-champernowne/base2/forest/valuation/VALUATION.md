# Valuation Forest

Expedition 7 of [MALLORN-SEED.md](../MALLORN-SEED.md).

This document is pre-registered. It is written *before* the
experiment runs, in the present-tense voice of a results report,
so the predictions can be checked against the actual visualizations
the moment they exist. Where the real outputs disagree with what is
described here, the disagreements are exactly the "surprises" the
seed asked for, and this file gets rewritten around them.

The substrate, the layout choices, the order of operations, and the
file plan live in [VALUATION-PLAN.md](VALUATION-PLAN.md).

## What the forest grid shows

The figure is a Cartesian forest. There are 256 odd-rooted trunks,
one per odd `m ≤ 511`, arranged left to right in order of `m`. The
trunk for `m = 1` is the powers-of-2 spine and is the longest in
the figure: ten nodes from `n = 1` down to `n = 512`. The next
trunks shorten quickly. `m = 3` has eight nodes (`3, 6, 12, …, 384`).
`m = 5` has seven (`5, 10, 20, …, 320`). By `m = 17` the trunks are
six nodes; by `m = 65` they are four; everything past `m = 257` is
a single solitary node sitting at depth zero.

Each node is colored by mean zero-run length. Within every trunk
the color descends smoothly from light at the top (`v_2 = 0`, short
zero-runs) toward dark at the bottom (high `v_2`, long zero-runs).
The descent is most regular along the `m = 1` spine — the case the
closed-form bit-balance result of
[HAMMING-BOOKKEEPING.md](../../HAMMING-BOOKKEEPING.md) predicts most
cleanly. Shorter trunks descend less monotonically; a small number
show single-node jumps where the per-monoid value departs from the
gradient set by the rest of the trunk. Those are the trunks worth
reading individually.

The image reads as an actual forest: a leftmost dark evergreen
spine with a wide stand of shorter trees behind it, each tree
darker at its base than at its crown. The visual repetition of
"darker at the base" is the bit-balance theorem doing its work in
the picture.

## What the spiral chains image shows

The figure is polar. The outer rim is a dense circle of 256 points,
one per odd `m`, all colored at the lighter end of the scale because
`v_2 = 0` everywhere on the rim. Each odd `m` anchors a spiral arm
that winds inward as `v_2` increases. The arms shorten as `m` grows,
the same way the trunks of the grid did, but here their length
becomes radial reach into the centre. The arm for `m = 1` is the
deepest, reaching the very middle as the powers-of-2 spiral.

Color descends along each arm from the rim inward, lightest at the
outside, darkest at the inward tip. The cumulative effect is a fan
of arms shading from a bright outer rim toward a dark central
vortex. The vortex itself is sparse — only the few longest chains
reach deep — so the centre reads as a clean dark hole rather than
as a crowded smudge.

This is the visualization most likely to produce a corona-style
accidental image. The polar coordinate is generous to the inward
arms in a way the Cartesian grid is not, and the structure of the
integers really does cluster around `v_2 = ∞` in 2-adic space.
What the eye sees is a fan with a singularity, which is what the
algebra has been claiming all along.

## What the residual map shows

The figure is not a tree. It is an `(odd_part_rank, monoid)` grid
in which each cell shows
`mean_rle0(n) − mean(mean_rle0 | v_2(n))` — the part of the
per-monoid mean zero-run length that is *not* explained by `v_2(n)`.

Most of the map is faint. The gross structure of mean-zero-run
length is captured by `v_2`, and once that mean is subtracted there
is no large remaining signal across the bulk of the monoids. But
the map is not silent. There are persistent faint bands at small
odd parts — `m = 3, 5, 7` in particular — where the residuals are
systematically non-zero across multiple `v_2` levels. The bands are
weak compared to the raw signal that V1 and V2 are showing, but
they are coherent enough to read as a real structural feature of
the forest, not noise. The largest single residuals come from a
small number of individual monoids where the actual mean zero-run
length departs noticeably from what `v_2` alone would predict.

The map is the analytic counterpart of the WALSH result: most of
the visible structure is `v_2`-explainable, but a real minority is
not, and the part that is not lives at specific named odd parts.
V1 and V2 dramatize how well `v_2` does. V3 is what shows where
`v_2` falls short.

## What is at stake

If the predictions above are roughly right, the expedition has
confirmed a moderate version of the seed's question: 2-adic depth
*does* predict the bulk of the binary stream signature, the
exceptions are real but localized, and the Walsh result and the
Valuation Forest result agree, in different vocabularies, that
`v_2(n)` is one organizing variable in this family rather than the
master variable.

If the predictions are wrong, the most informative ways for them to
be wrong are:

1. **The residual map is silent.** Mean zero-run length really is
   captured by `v_2(n)` alone. This would mean the Walsh signature
   has access to structure that the RLE statistics do not, and the
   right next step is to swap V3's signature to `entropy_def` or
   to a Walsh-derived scalar and see whether the residual map
   becomes loud.

2. **The forest grid is illegible.** The trunks do not descend
   smoothly because `mean_rle0` does not actually rise with `v_2`
   in the simple way the trailing-zero argument suggests. This
   would mean some other effect is dominant in the RLE statistic
   and the substrate needs an additional signature column to find
   it.

3. **The spiral chains image looks generic.** The center is no
   darker than the rim. This would mean the polar layout is buying
   nothing beyond V1, and V2 should be reworked — most likely by
   changing what gets colored along each arm rather than by
   changing the layout itself.

The most interesting failure mode is the first. The least
interesting is the second.
