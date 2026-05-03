# Curiosity: The Two Tongues (C_Surv Tracks the Bundle)

**Date entered.** 2026-05-01

**Category.** Curiosity.

**Deadline.** 2026-Q3.

## Description

![Dark background. A single panel with horizontal axis labelled "atoms processed (read order)" running from 0 to about 3500, and logarithmic vertical axis labelled "L1 deviation (leading digit, 1-9)" ranging from about 0.01 to 2.0. Two thin curves in orange (labelled "bundle") and blue (labelled "C_Surv") trace nearly-identical paths across the panel: starting near the top (1.0–2.0) at low atom counts, descending sharply to a dramatic minimum near atom 250 where the orange curve dips to about 0.012 and the blue curve to about 0.08, then rising and oscillating between roughly 0.4 and 1.0 across the rest of the range. The two curves overlap so closely that they appear to merge along most of the trajectory. Faint section labels along the top mark n=2 through n=10 across the atom axis. A legend in the upper right identifies orange as "bundle" and blue as "C_Surv". Title: "Two Tongues — bundle vs. C_Surv on [2,10], k=400 (3600 atoms, 1338 survivors, 37.2%)".](../experiments/acm-champernowne/base10/survivors/two_tongues.png)

For a window `[n_0, n_1]` and per-stream truncation `k`, the *bundle*
is the concatenation of all `n`-prime lists for `n ∈ [n_0, n_1]`,
each truncated at `k`. The *survivors* are the atoms that appear in
exactly one stream (singletons across the bundle). The *survivor
Champernowne real* `C_Surv_{[n_0, n_1], k}` is the digit
concatenation of the survivors in order of first appearance.

The Two Tongues plot
(`experiments/acm-champernowne/base10/survivors/two_tongues.png`)
shows the running leading-digit L1 deviation from uniform — the same
observable the bundle is built to make uniform — for both the bundle
and `C_Surv`, on a shared atoms-processed axis, log-y. At
`[n_0, n_1] = [2, 10]`, `k = 400` (3600 atoms, 1338 survivors, 37.2%
survival rate) the two curves *track each other almost cell for
cell* across the entire window, including through the dramatic n=2
dip where the bundle's L1 collapses to ≈ 0.012 (near-perfect Benford)
and `C_Surv` tracks down to ≈ 0.08 — about an order of magnitude
higher, but still clearly correlated, with the dip's location and
shape preserved.

The `l1_grid` heatmap
(`experiments/acm-champernowne/base10/survivors/l1_grid.png`)
quantifies the gap (`surv_L1 − bundle_L1`, post-warmup mean) across
`(K, n_0) ∈ [10, 1000]²` at fixed window width `W = 10`. The
heatmap is overwhelmingly white — the gap is near zero across most
of the parameter space, with only faint structure near the diagonal
`n_0 ≈ K` and minor flecks at low `(K, n_0)`. The Two Tongues panel
is one cell in this grid; the heatmap shows the cell is not
exceptional, the agreement is generic.

The survivor filter is not a thinning. It is an
information-theoretic *optimizer*: an atom is a survivor exactly when
`H(stream | integer) = 0` — i.e., the integer's stream membership is
uniquely determined. Higher multiplicities (`m ≥ 2`) have `H > 0`.
Reading C_Surv as the output of this optimizer reframes the Two
Tongues observation: the L1 *magnitude* of the leading-digit deviation
is what survives the optimization, while finer features of the
leading-digit *distribution* do not. The follow-on probe (`differences/`,
seven experiments) confirms this magnitude-vs-shape split: bundle and
survivors sit at similar L1 distances from uniform on the same
trajectory, but their underlying leading-digit distributions disagree
pointwise (survivors over-represent digit 3 at 20.4% vs the bundle's
12.4%), and the disagreement decomposes cleanly by source stream and
by multiplicity. The Two Tongues plot's tightness is a real magnitude-
level property of the optimizer's output; the perpendicular richness
that "tightness" might suggest lives at a different observable layer.

## Evidence

- `experiments/acm-champernowne/base10/survivors/SURVIVORS.md` —
  definition of bundle, survivors, `C_Surv`; Proposal 2 (the Two
  Tongues visualisation).
- `experiments/acm-champernowne/base10/survivors/two_tongues.png` —
  the panel image at `[2, 10]`, `k = 400`.
- `experiments/acm-champernowne/base10/survivors/two_tongues.py` —
  the script that produced it.
- `experiments/acm-champernowne/base10/survivors/l1_grid.png` —
  tracking-gap heatmap across `(K, n_0) ∈ [10, 1000]²` with
  `W = 10`; shows the agreement is generic.
- `experiments/acm-champernowne/base10/survivors/l1_grid.py`,
  `l1_grid.npz` — the heatmap generator and cached numerics.

## Status

Sharpened. The L1-magnitude tracking is robust: observed at the Two
Tongues panel, generic across `(K, n_0) ∈ [10, 1000]²` at `W = 10` in
the `l1_grid` heatmap, and now explained in part by reading C_Surv as
an `H(stream | integer) = 0` optimizer. The seven-experiment
`differences/` probe walked back stronger readings: there is no
detectable structure in `δ = C_Bundle − C_Surv` past the digit
transducer (EXP01–02); the leading-digit *shape* of survivors differs
from the bundle's (EXP06); the digit-3 spike that distinguishes
survivor from bundle localises to source streams `d ∈ {8, 9, 10}` and
is partly a finite-k truncation artifact (EXP07). The remaining open
question is whether the magnitude-level tracking persists at
`k → ∞` and across panels under the optimizer reading.

## Aesthetic note

It approximates the bundle. It should, I suppose, but wow. The
survivor filter throws away 62.8% of atoms and the leading-digit L1
deviation of what's left tracks the bundle's curve almost cell for
cell — including through the dramatic n=2 dip where the bundle goes
to near-perfect Benford. The `l1_grid` heatmap shows the agreement
is not a one-panel coincidence but generic across the parameter
space. The wow is in the gap between knowing the agreement should
be *approximate* and seeing how tight *approximate* turns out to be.

## Provocation

Three movements, all under the optimizer reading:

- **Limit-survivor estimation (EXP08 candidate).** For each apparent
  survivor `c` at finite `k`, check whether `c` is mathematically in
  any other stream `n ∈ [n_0, n_1]` (ignoring rank truncation).
  *True* limit-survivors — atoms with `H(stream | integer) = 0` in
  the `k → ∞` sense — are the optimizer's actual output. Plot the
  leading-digit distribution of just these. Prediction: the digit-3
  spike shrinks; the magnitude-level L1 tracking of bundle vs.
  limit-C_Surv persists. Confirmation would isolate which features
  are intrinsic to the optimizer and which are k-truncation imprint.
- **Closed-form for the high-d shape.** The d=10 cofactor band
  `m ∈ (rank-bounds)` predicts the digit-3 share by simple
  bandwidth (~40% by rough count, 49.3% empirically). Tighten the
  argument across `d ∈ {7, 8, 9, 10}`: derive `P_d(leading digit)`
  from the rank-truncation bands per stream and sum to predict the
  aggregate survivor leading-digit distribution at finite `k`. If
  this closes, the EXP06 shape is *fully* a k-truncation artifact
  with a closed-form description; the optimizer's intrinsic shape is
  whatever's left after the band-prediction is subtracted.
- **Optimizer view across panels.** L1-magnitude tracking has been
  observed at the Two Tongues panel and is generic on the `l1_grid`
  heatmap. Does the *optimizer reading* extend? At `(n_0, n_1, k)`
  with very different rank-truncation regimes (e.g., narrow window
  with large `k`, vs. wide window with small `k`), does the
  magnitude tracking hold while the shape varies, or does the
  tracking itself break? The boundary, if it exists, is the
  optimizer's footprint.

## Cross-references

- `experiments/acm-champernowne/base10/differences/DIFFERENCES.md` —
  the orientation note for the seven-experiment probe of the
  bundle/survivor relation perpendicular to L1 magnitude.
- `experiments/acm-champernowne/base10/differences/REFRAMING-CHAIN.md`
  — meta-note on how the probe progressed: each null triggered an
  external reframing (transducer → optimizer → source-stream).
- `experiments/acm-champernowne/base10/differences/DIFFERENCING-AS-TRANSDUCER.md`
  — the structural note explaining why direct `δ = C_Bundle − C_Surv`
  experiments come back generic; argues for atom-aligned observables
  instead.
- `prodigy-L1-cliff-n2-h8.md` — also a within-row L1 phenomenon,
  also sharper-than-expected, also from the observable side. The
  L=1 sign-flip is autocorrelation-level; this is leading-digit
  -distribution-level. Whether these are family-related is open.
- `marvel-row-ogf-cliff.md`, `monster-lcm-not-factorial.md` — the
  algebra side's record of "the substrate's residuals carry more
  structure than expected." The Two Tongues is the empirical
  side's analogue: a sub-stream's digit statistics carry the
  bundle's structure more faithfully than the construction's
  hand-wave predicts.

## Discovery context

`SURVIVORS.md` proposed two visualisations of the bundle/survivor
digit-level structure — the Gated Champernowne Strip (Proposal 1)
and the Two Tongues running L1 plot (Proposal 2). The Two Tongues
panel was generated; the agreement was visible immediately. The
`l1_grid` follow-on probed how generic the agreement is across
parameter space, and the heatmap's near-uniform whiteness made the
agreement generic rather than coincidental. The sharpness across
both artifacts is what drove the entry into the curiosity drawer.
The *why* is the unprobed question.

The user's articulation of the affect on entering this specimen:
*"It approximates the bundle. It should, I suppose, but wow."* The
hedge "It should, I suppose" is the hand-wavy expectation; the
"wow" is the gap between the hedge and the observed sharpness.

A subsequent seven-experiment probe (the `differences/` chain,
EXP01–07 plus three meta-notes) refined the reading: the magnitude-
level tracking is real and is the optimizer's footprint, while the
perpendicular richness the tightness suggested turned out to live
elsewhere — at multiplicity-stratified shape distinctions and
finite-k truncation imprints in high-d source streams.
