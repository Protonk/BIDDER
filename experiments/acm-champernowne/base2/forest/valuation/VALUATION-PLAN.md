# Valuation Forest — Plan

Expedition 7 of [MALLORN-SEED.md](../MALLORN-SEED.md).

The seed's question: **does 2-adic depth predict the binary stream
signature of an ACM monoid, or are there surprises?** Bit balance is
the part `v_2(n)` already cleanly predicts (closed form, see
[HAMMING-BOOKKEEPING.md](../../HAMMING-BOOKKEEPING.md)). The Walsh
signature is the part it does *not* fully predict
([WALSH.md](../walsh/WALSH.md)). Three visualizations sit between
those two facts and pull on the tension from genuinely different
angles.

The folder is named `valuation/` rather than the seed's
`twoadic_tree/`. The expedition is about the 2-adic *valuation* as
an organizing variable, and the visual treatment is broader than a
single literal tree.

## Substrate

Before any visualization, one script computes and caches a per-monoid
signature `.npz`. This is the audit-trail discipline lifted from
[../walsh/WALSH.md](../walsh/WALSH.md): the `.npz` is the source of
truth, the visuals are all rederived from it, no script ever
recomputes a stream.

`tree_signatures.py` writes `tree_signatures.npz` with:

| field | shape | meaning |
|---|---|---|
| `ns` | `(N,)` int | monoid indices `1..N_MAX` |
| `v2` | `(N,)` int | `v_2(n)` |
| `odd_part` | `(N,)` int | `m`, where `n = m · 2^v_2(n)` |
| `mean_rle0` | `(N,)` float | mean zero-run length |
| `mean_rle1` | `(N,)` float | mean one-run length |
| `entropy_def` | `(N,)` float | `1 − H_8 / 8`, entropy deficit at window `k = 8` |
| `rle0_hist` | `(N, 16)` float | normalized RLE-0 histogram, lengths 1..16 |
| `walsh_t1` | `(N,)` float | walsh tier-1 brightness, NaN for `n` outside `2..32` |

`N_MAX = 512` is the default. This gives ten levels of `v_2` along
the depth axis (`2^0` through `2^9`), enough density for the polar
layout to read as a figure rather than a sparse scatter, and matches
the upper end of the existing forest experiments. The substrate is
linear in `N`; rerunning at larger `N` later is a substrate-rerun,
not a viz redesign.

## Lead signature

Primary scalar: `mean_rle0`. Simplest, brightest, and most directly
forced by the algebra — every entry of monoid `n` has at least
`v_2(n)` trailing zeros, so `mean_rle0` rises with `v_2(n)` in the
most cleanly readable way of the candidates. This is the signature
that maps "low `v_2`" to "light color" and "high `v_2`" to "dark
color" with the least argument, which is what V1 and V2 need from
a lead.

Alternative: `entropy_def`. One-line swap in each viz script. The
swap is the right move if V3's residual map turns out silent —
i.e., if mean zero-run length really is captured by `v_2` alone and
the question becomes uninteresting under that signature.

`walsh_t1` is held in the substrate as a bonus column populated only
for `n = 2..32`, the range the walsh experiment ran on. It is not
the lead because it does not exist for the full range, but it can
be overlaid on V1 or V2 as a marker on those 31 monoids — a way of
asking whether the walsh-bright monoids land where `v_2` predicts
they should.

## V1 — Forest Grid (Cartesian, literal)

**Mapping.** Each odd `m` sprouts a vertical trunk. Position monoid
`n` at:

- `x = rank(odd_part(n))` among odd numbers `≤ N`
- `y = −v_2(n)` (trunks grow downward, odd numbers along the top)

**Glyph.** A filled circle at each `(x, y)`, colored by `mean_rle0`.

**What it tests.** Within a single trunk, do colors descend smoothly
or jump? Smooth descent says `v_2` predicts `mean_rle0` *within* an
odd family. Jumps say the odd part also matters. The leftmost trunk
(`m = 1`) is the entire powers-of-2 spine — the seed's "deepest
branches" are exactly its bottom nodes.

**Why this layout.** It draws the forest the way the seed describes
it. No tricks. The Cartesian framing makes the trunk-and-side-branch
structure immediate and lets a reader compare the `m = 1` spine
against any other family side by side.

## V2 — Spiral Chains (polar, follows the muse)

**Mapping.** Polar. Each odd-rooted chain `(m, 2m, 4m, …)` becomes
a spiral arm. The arm for odd `m` is anchored at the outer rim at
angular position `2π · rank(m) / num_odds` and winds inward as `v_2`
increases. The arm for `m = 1` is the longest — it includes every
power of 2 in range — and spirals deepest into the centre. Odd
numbers form the outer rim; powers of 2 form the central vortex.

**Glyph.** A point per chain member, colored by `mean_rle0`. Arms
are drawn as faint connecting curves so each chain reads as a unit.

**Render order.** Outer rim drawn first, inward arms drawn last.
With `N = 512` the rim has 256 points and is dense; the inward arms
are sparse but carry most of the visual interest, so drawing them
last keeps them legible through any rim occlusion. If `N` is
increased, this convention turns rim occlusion from a problem into
an artistic feature: a thick outer ring fading into a clean inward
vortex. Render-order is a parameter we control, and the right
default at high `N` is "things we want to see, last."

**What it tests.** Same question as V1, in a coordinate system
designed to *display* depth rather than just plot it. If colors at
the center are visibly different from colors at the rim, the depth
dimension is real and the basin metaphor holds. If not, depth is
bookkeeping.

**Why this layout.** Different mapping from V1 (Cartesian → polar),
different visual idiom (grid → spiral arms), and the visualization
most likely to produce a corona-style accidental image. The polar
coordinate is generous to the inward arms in a way the Cartesian
grid is not, and the integers really do cluster around `v_2 = ∞` in
2-adic space.

## V3 — Residual Map (analytic, not a tree at all)

**Mapping.** Not a tree. A standard `(odd_part_rank, monoid)` grid
in which the cell value is the *residual* of `mean_rle0` against
the depth-only prediction:

```
residual(n) = mean_rle0(n) − mean(mean_rle0 | v_2(n))
```

If `v_2` fully predicts `mean_rle0`, the map is identically zero.
If the odd part also matters, the map shows persistent bands at
specific values of `m`.

**Glyph.** Diverging colormap centered at zero (`RdBu_r`). Positive
residuals warm, negative cool, exact zero a faint background tone.

**What it tests.** The seed's research question, answered explicitly.
V1 and V2 invite the question; V3 answers it. This is the same move
the walsh experiment made when it stopped reading raw spectra and
started reading what survived after subtracting the
`v_2`-explainable component.

**Why this layout.** Three out of three viz now exercise different
mappings *and* different ideas. V1 uses `v_2` as structure (depth
in a tree). V2 uses `v_2` as emergent texture (a band that arises
from the polar layout). V3 uses `v_2` as a hypothesis to subtract
against. Each can fail or succeed independently.

## File structure

```
forest/valuation/
  VALUATION.md              report-style doc, predictions framed as observations
  VALUATION-PLAN.md         this file
  tree_signatures.py        substrate
  tree_signatures.npz       per-monoid signature cache
  forest_grid.py            V1
  forest_grid.png
  spiral_chains.py          V2
  spiral_chains.png
  residual_map.py           V3
  residual_map.png
```

Conventions match the rest of `forest/`: one script per viz, output
PNG next to it, npz cache for the substrate, doc named for the
folder.

## Order of operations

1. `tree_signatures.py` — substrate must exist before any viz.
2. `forest_grid.py` (V1) — literal layout, cheapest sanity check
   that the substrate is correct.
3. `residual_map.py` (V3) — the analytic answer to the seed's
   question. Run before V2 because if the residual map is silent,
   we may want to redesign V2's signature axis before drawing it.
4. `spiral_chains.py` (V2) — artistic exploration last.

Walsh tier-1 overlay is added to V1 or V2 after the three core viz
exist, if the substrate has the column populated and time permits.

## Possible V4: 2-adic Stern-Brocot embedding

A fractal layout that places each integer at a position determined
by its binary expansion (a Cantor-set / dyadic-rational embedding).
`v_2` shows up as trailing-zero depth in the binary representation,
and the fractal structure exposes self-similarity that the grid
and the spiral both miss. Held back from the initial three because
V3 is committed to the analytic answer rather than the artistic
exploration; this is the natural addition once the analytic answer
is in.
