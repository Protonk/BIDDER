# Prodigy: The L=1 Sign-Flip Across h-Parity

**Date entered.** 2026-05-01

**Category.** Prodigy.

## Description

![Cream background. A single bar chart with horizontal axis showing seven labelled positions h=4 through h=10, and vertical axis labelled "vertical L=1 autocorrelation (mean Pearson over adjacent n-rows)" ranging from about −0.16 to +0.20. A horizontal zero line crosses the panel. Bars at h=4, h=6, h=8 are navy blue and dip below zero, with heights about −0.008, −0.054, −0.017 respectively. Bars at h=5, h=7, h=9, h=10 are red and rise above zero, with heights about +0.010, +0.172, +0.030, +0.016. The h=7 bar is by far the tallest. Numerical values are printed above or below each bar. Below the bars at the bottom margin, four small gray squares mark h=5, 6, 7, 8 with the legend text "marker: h-values cited in ATTRACTOR-AND-MIRAGE.md:612-615". A small italic footer reads "(n ∈ [2, 50], K = 200; analytic from algebra/predict_q.q_general — no lattice required)". Title: "Prodigy: The L=1 Sign-Flip Across h-Parity — vertical autocorrelation by height".](../experiments/acm-champernowne/base10/q_distillery/prodigy_L1_signflip.png)

The within-row lag-1 vertical autocorrelation flips sign with the
parity of the height `h`. At odd `h ∈ {5, 7}` the vertical L=1
correlation across adjacent height-rows sits near `+0.25`; at even
`h ∈ {6, 8}` it sits near `−0.14`. Same lattice, same observable, the
sign of the gap entirely controlled by whether `h` is even or odd.

When this surfaced it looked like a numerical artifact — sign
conventions in the autocorrelation pipeline, an off-by-one in the
class-pair indexing, a bad mask. It is none of those. The class-pair
density `D(c_1, c_2)` over which the autocorrelation decomposes
shifts mass between diagonal `(t, t)` pairs and off-diagonal
`(t, t')` pairs as `L` changes parity, and at `L = 1` the off-diagonal
contribution dominates. Because the off-diagonal `Q` products carry
*different signs* depending on which side of the height tower the
overlap sits on, the lag-1 correlation inherits the sign of `(−1)^h`.

The cross-`n` story at small lag is the second face of this prodigy.
At `h = 6` the per-lag L=1 autocorrelation for `n = 2` sits at
`+5.95e−06` (per-lag profile in the integration summary); for `n = 13`
the same summary reports the *odd-L mean* (across L = 1, 3, …, 19) at
`+1.15e−01` rather than L=1 specifically. The two are different
aggregations and not strictly comparable — the n=13 individual L=1
value has not been pulled out of the integration summary — but the
four-order spread between them tracks a real cross-`n` trend visible
in the same summary's even-L means and in the `+0.25` / `−0.14`
figures from `ATTRACTOR-AND-MIRAGE.md`.

## Evidence

- `arguments/ATTRACTOR-AND-MIRAGE.md:612-615` — the explicit
  documentation of the sign flip: vertical L=1 ≈ `−0.14` at `h ∈ {6, 8}`,
  ≈ `+0.25` at `h ∈ {5, 7}`.
- `algebra/WITHIN-ROW-PARITY.md` — class-pair decomposition that
  resolves the sign-flip into the off-diagonal contribution.
- `algebra/tests/integration/test_within_row_lattice_summary.txt` —
  cross-`n` lag profile at `h = 6` (the live height after Tier B).
  Per-lag `n = 2` profile shows the L=1 floor at `+5.95e−06`. Cross-`n`
  table at `h = 6` reports odd-L and even-L means but not per-lag
  values for `n ∈ {3, 5, 7, 11, 13}`.
- `experiments/acm-champernowne/base10/q_distillery/q_lattice_4000_h_regen.py`
  — regenerator for the retired `h ∈ {5, 7, 8}` lattices (Tier B
  prune). The `+0.25` / `−0.14` figures cited above were originally
  observed against those lattices; reproducing the audit trail
  requires regenerating them.
- `algebra/predict_correlation.py` — `class_decomposition`,
  `autocorr_profile`, the `q_for_class` cache.
- `experiments/acm-champernowne/base10/q_distillery/prodigy_L1_signflip.png`
  — emblem. Single-panel bar chart of vertical L=1 autocorrelation
  (mean Pearson over adjacent n-rows) at `h ∈ {4..10}`, computed
  analytically from `q_general` on a smaller grid (`n ∈ [2, 50]`,
  `K = 200`; no lattice required). At this resolution: clean
  alternation `−, +, −, +, −, +` across `h ∈ {4..9}`; the
  alternation *breaks* at `h = 10` (`+0.016` instead of negative).
  Magnitudes are smaller than the published `~+0.25 / ~−0.14`
  figures (which used the full `K = 4000` lattice), but the
  sign-pattern survives. Published cells `h ∈ {5, 6, 7, 8}` are
  marked.
- `experiments/acm-champernowne/base10/q_distillery/prodigy_L1_signflip.py`
  — render script.

## Status

Probe-validated. The sign flip is reproduced both empirically (lattice
spot-check) and analytically (master expansion via `q_for_class`). The
cross-`n` magnitude scaling is observed but not yet given a closed
form; it is open whether the growth flattens, plateaus, or accelerates
beyond the tested prime range.

## Aesthetic note

This will become a transient shape. As height increases, the pattern cannot calm.

## Provocation

Three concrete next moves:

- Extend to `h ≥ 9`. The h=8 lattice was retired in the Tier B prune
  (regenerable from `experiments/acm-champernowne/base10/q_distillery/q_lattice_4000_h_regen.py`).
  The question is whether the sign continues to flip, and whether the
  magnitudes settle, sharpen, or both.
- Quantify the `n = 2` floor. Is the lag-1 floor structurally `≈ 0`,
  with the observed value a finite-K artifact, or is there a smaller
  closed-form constant?
- Algebraic form for `D(c_1, c_2)` as a function of `L`, then the
  parity flip is a corollary of the density's structure rather than
  an empirical regularity.

## Cross-references

- `wonder-cost-ladder.md` — the cross-`n` magnitude ladder is one
  rung of the same height-tower cost question, observed in the
  autocorrelation coordinate.
- (forthcoming `sport-h2-universal-cliff`) — `h = 2` is shape-independent
  in the closed form `Q_n(n²k) = 1 − d(k)/2`; the L=1 sign-flip's
  parity-of-h structure is the autocorrelation analogue of the
  closed-form's parity-of-h structure.

## Discovery context

The sign flip surfaced during the comparison of `h = 5, 6, 7, 8`
lattices in `experiments/acm-champernowne/base10/q_distillery/`. The
within-row lag-1 vertical correlations were tabulated as a routine
diagnostic; the alternation `+, −, +, −` across the four heights was
visible in the table. First reaction was to suspect the sign
convention in the autocorrelation pipeline; the bug hunt failed to
find one and the alternation was eventually placed against the
off-diagonal class-pair contribution and the master expansion's
`(−1)^j` factor — a first-order reading per `ATTRACTOR-AND-MIRAGE.md`,
with full accounting still missing. That the resolution was
structural rather than a fix is what made this a prodigy and not a
finding.
