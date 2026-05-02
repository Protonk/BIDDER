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

There is a hand-wavy reason this might be expected: the survivors
are a structured subset of the bundle, and leading-digit Benford-like
statistics are robust under "uniform-random-ish" sub-sampling. The
sharpness of the agreement — tracking through specific dips, holding
across (K, n_0)-space — is not predicted by that hand-wave. The
structured survivor filter, when read through the leading-digit
observable, *behaves like* a uniform-random thinning. Or the
leading-digit profile is robust enough that even highly-structured
sub-sampling preserves it. Or both. The mechanism is not yet probed.

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

Suggestive. Phenomenon observed in one Two Tongues panel and
characterised quantitatively in the `l1_grid` heatmap; the
agreement is robust across `(K, n_0) ∈ [10, 1000]²` at `W = 10`. No
mechanism is given for the sharpness of agreement, and the
parameter regime where the agreement breaks (if any) has not been
mapped.

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

Three movements:

- **Multiset vs. sequence decomposition.** EXP04's
  `placement_destroyer.py` decomposed the L1-gap heatmap into a
  multiset-of-leading-digits component and a sequence-placement
  component, and found the multiset component dominant (~95% of
  signs, ~86% of linear structure). The same decomposition applied
  to `C_Surv` vs. bundle would localise the agreement: if the
  survivor filter preserves the *multiset* of leading digits at
  each prefix, the tracking is mostly explained; if not, the
  sequence structure carries the agreement and is the more
  surprising fact.
- **Map the disagreement.** The `l1_grid` heatmap's faint structure
  near the diagonal `n_0 ≈ K` is the address. Zoom in: at
  `(n_0, K)` with `n_0 ≈ K`, what does the C_Surv curve do that
  the bundle doesn't? Specifying *where* the agreement weakens
  would constrain the mechanism.
- **Vary the window width.** `l1_grid` is at fixed `W = 10`. At
  `W = 2` the survivor filter is at its most restrictive (half the
  atoms maximally collide); at `W = 100` it relaxes. Whether the
  tracking holds at both extremes, or sharpens at one and breaks
  at the other, distinguishes "the survivor filter is benign by
  construction" from "the survivor filter happens to be benign at
  W = 10."

## Cross-references

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
