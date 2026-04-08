# Valuation

These images are art experiments built from the *residual* of the
binary stream signature against its 2-adic-depth prediction. The
mathematical companion lives in
[`../../forest/valuation/`](../../forest/valuation/), and the source
of truth is [`tree_signatures.npz`](../../forest/valuation/tree_signatures.npz):
no script in this folder regenerates a stream.

The view we're stylizing is V3 of the Valuation Forest expedition.
V3 has the data — a per-monoid residual against the within-depth
leave-one-out mean, gated by a blockwise z-statistic — but its
literal layout is a `(v_2, odd_part_rank)` rectangle that wastes most
of the canvas: nine populated rows of decreasing width over a 2048-
column field, with the only intense cells crowded into the leftmost
columns. The right-hand `~1500` columns and the bottom four rows are
faint or empty by construction.

The art folder asks: same data, what coordinate system?

## Why this data wants a different coordinate system

V3's recorded result, in one sentence: depth captures most of the
mean-zero-run-length signal, the exceptions are localized at small
odd parts, and the `m = 1` column carries both the largest negative
residual and the largest positive residuals in the figure.

A rectangular grid will always under-show that result. The
interesting cells are concentrated in a small region, the rest of
the rectangle is empty, and a viewer's eye spends most of its budget
on the empty part. The stripped-down spiral arms of V2
([`spiral_chains.png`](../../forest/valuation/spiral_chains.png))
already prove this point in the other direction: the same kind of
data, on a polar layout, fills its canvas and surfaces the
m = 1 column as a structural feature rather than a one-pixel
sliver.

The art folder takes V3's color/alpha and puts it on layouts that
fill the canvas. Two starting variants. Both are dots only — no
connecting curves, no trunk lines, nothing that the residual map
itself does not already imply.

## Variant A — Treefan Rose

A polar treefan in the V2 idiom, colored by residual instead of by
mean zero-run length.

**Layout.** Identical in spirit to
[`spiral_chains.py`](../../forest/valuation/spiral_chains.py).
Each odd `m` anchors a spiral arm at angular position
`2π · rank(m) / num_odds`; the arm winds inward as `v_2` grows. Arm
length is the chain length; `m = 1` reaches the centre and is the
deepest. No connecting curves — only dots.

**Glyph.** A dot per monoid. Color is the V3 residual on a diverging
scale (`RdBu_r` is the obvious starting palette). Alpha is `|z_res|`
clipped to a `[0, 1]` band so that low-confidence cells fade and
high-confidence cells burn.

**What it does.** The brightest cells in the figure are forced to
sit on the `m = 1` arm — the spiral that reaches the centre — so
the cumulative effect is a fan of mostly-faint dots with a single
luminous radial spike running from the rim through the central
vortex. The half-circle structure of V2 is preserved (only the small
odd parts have inward arms, and they live in the right hemisphere),
which means the empty left hemisphere becomes negative space rather
than wasted page.

**What to vary.**

- Palette. `RdBu_r` is the literal V3 colormap; `coolwarm`,
  `seismic`, or a custom two-hue palette will give the same
  diverging structure with different temperature.
- Alpha curve. Linear `|z_res|` is one choice; a sigmoid centred at
  `|z| = 2` gives a sharper "stars on black" reading.
- Dot size. Constant size is the simplest. Scaling size by `|z_res|`
  in addition to alpha doubles the contrast and risks overwhelming
  the rim, but is worth trying.
- Twist. The V2 plan uses `0.18 rad` per `v_2` step. Larger twist
  curls the arms tighter; zero twist makes them straight radial
  spokes.

## Variant B — Stratum Triangle

A triangular Cartesian layout that mirrors the natural shape of the
data: row width halves with each step in `v_2`.

**Layout.** Vertical axis is `v_2`, growing downward from `v_2 = 0`
at the top. Each row is centred horizontally and has width
proportional to `2^(V2_MAX − v_2)`, so the row for `v_2 = 0` is the
widest and the row for `v_2 = 8` is sixteen times narrower. Cells
within a row are placed at angular ranks of `odd_part(n)` among that
row's odd parts. The result is a downward-narrowing triangle that
fills its bounding region efficiently.

**Glyph.** A dot per monoid, color and alpha as in Variant A.

**What it does.** The triangle is the data's natural shape: at
`v_2 = t` there are `N_ANALYTIC / 2^(t+1)` monoids, exactly half the
count of the row above it, so the triangular envelope encodes the
stratum sizes directly. Hot cells at small odd parts pull toward
the centre line of the triangle (small `m` → small angular rank →
near the row centre), turning the `m = 1` outliers into a vertical
luminous axis running through the apex.

**What to vary.**

- Triangle vs trapezoid. Strict halving gives a sharp triangle.
  Linear narrowing gives a trapezoid that surfaces deeper rows
  better at the cost of stratum-size honesty.
- Apex. Apex-down is the literal mapping. Apex-up reverses the
  visual hierarchy and may read better as "growing downward into
  unknown depth."
- Row spacing. Equal row heights are the obvious default; spacing
  proportional to `1 / sqrt(stratum_size)` would give the deeper
  rows more pixels.
- Column ordering. Numerical `m` is one choice. `m` reflected so
  the centre line is `m = 1` (instead of "between" odd parts) makes
  the m = 1 spike land on the actual axis of the triangle.

## Variant C — Stratum Fan

A white-background variant that makes the chain structure of the
triangle visible as a skeleton.

**Layout.** Same triangular footprint as Variant B, with two changes:
linear (trapezoidal) row narrowing instead of strict halving, and a
centered column ordering that places the smallest odd part of each
row on the central axis with subsequent odd parts placed alternately
to either side. Linear narrowing makes column spacings grow with
depth, so doubling chains for different `m` no longer run parallel —
they fan out as they descend toward the apex. Centered ordering puts
the `m = 1` chain on the vertical axis through the apex, so the
spine reads as the central trunk of the fan.

**Glyph.** Each odd-rooted doubling chain (with at least
`MIN_CHAIN_LEN = 5` nodes inside the supported region) is drawn as a
thin dark polyline through its members. Hot cells (cells with
`|z_res| ≥ 1.5`) are drawn on top as filled dots in the V3
diverging palette at high opacity. Faint cells, the chain tails in
under-supported rows, and the alpha-gated background of Variants A
and B are all dropped: the only marks on the canvas are chain lines
and bright residuals.

**What it does.** The picture reads as a fan or feather. The dense
grey wedge at the top is the bundle of `~128` chain lines whose
ranks all sit close to the centre of the 2048-rank top row; as the
bundle descends through rows that shed shorter chains the lines
separate and the fan opens. Hot cells punctuate the lines in three
visible horizontal bands corresponding to the dominant `v_2` rows
in the residual map. The `m = 1` spine traces the central column
through every row.

**What to vary.**

- `MIN_CHAIN_LEN`. Lower (e.g., 3) keeps shorter chains and gives a
  fuller fan; higher (e.g., 8) keeps only the chains that reach the
  deepest supported row and gives a sparser, more legible
  skeleton.
- Width function. Strict halving collapses the fan into parallel
  lines; linear narrowing is the trapezoidal default; intermediate
  power laws (`(1 - t/V2_MAX)^p` for `p > 1`) give intermediate
  fan angles.
- Line alpha and weight. Lower alpha + more lines reads as a soft
  texture; higher alpha + fewer lines reads as a tight skeleton.
- Background. White is the default for this variant. The same
  layout would also work on dark with light lines, inverting the
  colour contract from Variants A and B.

## Variant D — Hyperbolic Chord

A faux-hyperbolic disk in which each doubling chain becomes an arc
through the Poincaré disk model.

**Layout.** The unit disk has a fixed focal point on the boundary
at `(1, 0)`. Each odd-rooted chain `m` is assigned a bend-back
point `P_m` on the boundary at angle `β_m`, with the longest chains
(longest first by chain length, ties broken by `m`) placed at the
antipode `β = π` and shorter chains spiralling outward toward the
focal in alternating directions. A small angular gap around the
focal keeps the very shortest chains from collapsing onto it. For
each chain, the layout draws the unique circle through `(1, 0)` and
`P_m` that is perpendicular to the unit circle at both endpoints —
i.e., the actual hyperbolic geodesic between those two ideal
points. Chain members are placed along the arc at fractions
`(V2_SUP_MAX − v_2) / V2_SUP_MAX`, so the deepest member sits
closest to the focal and the shallowest sits at `P_m` on the
boundary.

The geometry is honest hyperbolic; what's *for effect* is using it
as a layout primitive. We aren't claiming the data lives in
hyperbolic space — we're using hyperbolic geodesics because they
give us a way to bend the chain skeleton through a disk that
matches the visual idiom of a Poincaré tiling.

**Glyph.** Each chain (with at least `MIN_CHAIN_LEN = 5` supported
nodes) is drawn as a thin dark arc from its `P_m` to the focal-side
fraction reached by its deepest member. The disk's boundary is a
faint outline. Hot cells (`|z_res| ≥ 1.5`) are drawn on top as
filled dots in the V3 diverging palette.

**What it does.** The picture reads as a forced chord diagram in a
hyperbolic disk: 128 arcs all passing through the same focal point,
bending across the disk to bend-back points distributed around the
boundary. The `m = 1` chain lands at `β = π` and its arc is the
horizontal diameter; its hot cells (`n = 2, 32, 64, 128, 256`)
trace a row along that diameter from the cold outlier on the far
left to the warm cluster near the focal on the right. Adjacent
chains (`m = 3, 5, 7, ...`) sit on slightly off-diameter arcs and
their hot cells form a small constellation just above and below
the central row. Short chains (`m = 17, 19, ...`) bend tightly
near the focal and form the dense angular fringe at the right of
the disk.

**What to vary.**

- `MIN_CHAIN_LEN`. Lower (e.g., 3) gives ~512 arcs and a much
  denser fringe near the focal; higher (e.g., 7) gives a clean
  fan of ~30 arcs with the chain skeleton fully legible.
- `ANGULAR_GAP`. The fraction of `2π` reserved as a gap around the
  focal. A larger gap pulls all bend-back points away from the
  focal, opening the right side of the disk; a smaller gap fills
  the disk more uniformly at the cost of crowding near the focal.
- Sort key. Sorting chains by length descending puts the longest
  chain at the antipode and the shortest near the focal.
  Sorting by `m` instead would put `m = 1` near the focal and
  `m = 4095` at the antipode — the inverse visual.
- `FOCAL_ANGLE`. Currently fixed at 0 (focal at `(1, 0)`). Any
  other angle is a rigid rotation of the picture; useful for
  matching adjacent figures or printed orientation.

## Coordinate spaces worth trying after these two

The two variants above are the cheapest moves. There are richer
embeddings if either of them disappoints.

- **Concentric strata.** Each `v_2` row becomes a ring; rim is
  `v_2 = 0`, centre is `v_2 = 8`. Angular position is rank within
  the stratum. This is V2's layout with no spiral twist and no arm
  identity — pure concentric rings, color from V3.
- **Dyadic embedding.** Place each integer at coordinates derived
  from its binary expansion (Stern-Brocot, Z-curve, Hilbert curve,
  or a Cantor-set dyadic-rational placement). `v_2` shows up as
  trailing-zero depth and the layout is intrinsically fractal. Held
  back from the initial two because it does more work and the
  result is harder to read at a glance.
- **Hyperbolic disk.** A Poincaré-disk projection of the polar
  layout amplifies the rim and shrinks the centre. This is the
  right move if Variant A's central vortex is *too* sparse to read
  even with the m = 1 spike highlighted.
- **Cone projection.** Treat `v_2` as depth and project a 2D cone
  into the page. The forest grid becomes a literal forest receding
  toward a horizon. Most expensive to implement and the most
  literal of the options.

## What to keep across variants

These are the choices that should stay constant so the variants are
genuinely comparable.

1. **Residual is the signal.** Always color by the V3 residual,
   never by raw `mean_rle0`. The art folder is for the data V3
   surfaces — mean-zero-run length itself already has its picture.
2. **Confidence gates visibility.** Always alpha-gate by `|z_res|`,
   or threshold on `|z_res|` and only draw cells above the bar. A
   cell whose residual is not stable across the eight blocks of
   `rle0_block_means` should not draw the eye, no matter what its
   sign.
3. **Under-supported rows are context.** `v_2 ≥ 9` is never given
   the same visual weight as `v_2 = 0..8`. It can be present (faint
   halo, neutral grey, or simply omitted) but it never carries
   chroma.
4. **Background is uniform per piece.** Variants A and B default to
   the dark base2 palette (`#0a0a0a` background, white text,
   diverging palette whose endpoints are visible against the dark).
   Variant C inverts to white (`#f8f8f5`) so that the chain skeleton
   reads as dark structure on a light field; the diverging palette
   stays the same. Either pole is fine; mixed fields inside one
   piece are not.

## Files

```
art/valuation/
  VALUATION.md                this file
  treefan_rose.py             Variant A
  treefan_rose.png
  stratum_triangle.py         Variant B
  stratum_triangle.png
  stratum_fan.py              Variant C
  stratum_fan.png
  hyperbolic_chord.py         Variant D
  hyperbolic_chord.png
```

The substrate dependency is one line: each script reads
[`../../forest/valuation/tree_signatures.npz`](../../forest/valuation/tree_signatures.npz)
and rederives the residual and the z-statistic locally, the same
way [`residual_map.py`](../../forest/valuation/residual_map.py)
does. No new computation enters this folder.
