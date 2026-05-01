# EXP10 — full-resolution K_pair lattice render

EXP07 rendered the lattice at 10×10 averaging; with Theorem 1 (see
`LATTICE-CLOSED-FORM.md`) we can compute `Λ_W(K, n_0)` at unit
resolution by direct enumeration. This memo records what becomes
visible.

## Headline visual

For W = 10, n_0 ∈ [10, 1000], K ∈ [1, 1000]: 19070 nonzero cells out
of ~991k (~1.9% lit). Of those, 10164 (~53%) have multiplicity ≥ 2,
i.e., multiple pairs share the same `(K, n_0)` point. Maximum
multiplicity per cell is 9 = W − 1.

## What the slope-1 band actually looks like

The `r = 1, g = 1` family contributes one pair per `r` per window,
landing at `K_pair = a` for `a ∈ {n_0, …, n_0 + W − 2}`. But the
slope-1 BAND (not just the leading ray) is wider than that: every
`r ∈ {1, 2, …, W − 1}` with `gcd(a, r) = 1` contributes at
`K_pair = a + r − 1`, all of which are slope-1 lines offset
horizontally from each other.

Concretely, at fixed `n_0`:

- **Leading edge** `K = n_0`: only the pair `(n_0, n_0 + 1)` lands
  here. Multiplicity 1.
- **Cell `K = n_0 + j`** for `0 ≤ j ≤ W − 2`: contributions from
  every `r` with `r ≤ j + 1` and `gcd(n_0 + j + 1 − r, r) = 1`.
  Multiplicity grows roughly with `j`.
- **Trailing edge** `K = n_0 + W − 2`: up to `W − 1` pairs (one per
  `r` from 1 to `W − 1`) land here, *if* every `(a = K - r + 1, r)`
  is coprime. Multiplicity peaks here.

Empirical max-multiplicity cell at `n_0 = 10, K = 18`: 9 pairs land,
all coprime because `b = 19` is prime so `gcd(a, 19) = 1` for all
`a ∈ [10, 18]`.

## What 10×10 averaging hides

Side-by-side comparison (panel 3 of the figure) shows that 10×10
averaging:

- **Collapses the slope-1 band into a single bright diagonal.** The
  band's W − 1 cell width fits inside one downsampled cell, so the
  multiplicity gradient (1 → W − 1) is smoothed away.
- **Almost erases the slope-1/d rays for d ≥ 2.** Each cell on these
  rays has multiplicity 1, so a 10×10 box typically contains just
  one or two lit cells. After averaging by sum (or worse, by mean),
  the rays drop to barely-visible.

This is why EXP07's heatmap visually emphasized the slope-1 band
and made the slope-1/d fan look fainter than it really is. At unit
resolution all `W − 1` slope-1/d rays are first-class structure.

## What the EXP07 reference line was

EXP07 drew a guide at `K = n_0 + 1`. Earlier drafts of
`LATTICE-CLOSED-FORM.md` framed this as "off by one". A fairer
reading: `K = n_0 + 1` sits on the second sub-ray of the slope-1
band — specifically, the r=2, g=1 sub-ray contributes there (when
`a = n_0` is odd). It is one cell into the band, not the band's
leading edge. The original guide was loose, not strictly wrong.

The leading edge of the slope-1 band is `K = a` (cyan in the
figure); the trailing edge is `K = a + W − 2` (gold).

## Numerical fan statistics

For W = 10 across the rendered grid:

| metric | value |
|---|---|
| nonzero cells | 19,070 |
| total pair-events `Σ Λ` | 44,443 |
| cells with multiplicity ≥ 2 | 10,164 |
| max multiplicity per cell | 9 (= W − 1) |

The total 44,443 is consistent with `(W·(W−1)/2) · n_0_count` minus
edge losses near `n_0 = N0_MAX`: at high `n_0` some pairs have
`K_pair > K_MAX` and aren't counted. (See script's row-sum sanity
check.)

## Why this is enough for now

EXP10 confirms the `LATTICE-CLOSED-FORM.md` picture visually at
unit resolution and quantifies the multi-ray-overlap rate. Two
follow-ups that are worth doing but not yet done:

- **L1-gap-projection-from-lattice.** Now that we have the lattice
  exact, project it through the leading-digit lens (EXP03's
  observable) and compare to the original triangle/finger heatmap.
  This should close the loop on EXP03's "fingers as projections".
- **Multi-share rate scan.** As W grows, the rate of 3+-shared
  atoms grows (we saw 1 cell at W = 10; for W = 30, 50 the rate
  may be non-trivial). Scan and report.

## Files

- `exp10_full_resolution_lattice.py` — render script
- `exp10_full_resolution_lattice.png` — main figure (3 panels:
  full-res lattice, zoom, EXP07-style 10×10 downsample)
