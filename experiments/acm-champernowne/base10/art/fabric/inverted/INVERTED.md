# Inverted

The `inverted/` branch takes the continuous fabric field and turns it
inside out.

These images do not introduce a new data source. They are descendants of
the same object used in [`../significand_carpet.py`](../significand_carpet.py):

- rows are monoids
- columns are sliding-window positions
- values are short decimal significands in `[0,1)`

What changes here is geometry, tone, and emphasis.

## The core move

The baseline inversion takes a polar significand field and applies a
radial inside-out map.

That does one very useful thing: it gives the dense low-`n` region more
space. In the flat fabric, and even in the plain polar warp, the richest
early rows are crowded together. After inversion, that structure moves
out toward the rim, where it can breathe. The more regular high-`n`
region is compressed inward.

So inversion is not arbitrary decoration. It is a reallocation of visual
resolution.

## How to read the branch

Across most of these images:

- angle still corresponds to position in the digit window
- radius still corresponds, directly or indirectly, to monoid index
- the outer region usually carries the richest low-`n` interference
- the inner region usually carries compressed high-`n` regularity

Some pieces preserve the circular geometry. Others deform it into eggs,
blobs, or lens-distorted sheets. But the same field is underneath.

## The family

### `significand_inverted`

[`significand_inverted.py`](significand_inverted.py) is the clean
baseline.

This is the inside-out version of the significand carpet with minimal
extra styling. If you want to understand the branch, start here. It
shows what inversion alone buys you: the low-`n` structure opens up at
the rim, and the central region becomes a dense, regular core.

### `smoke_ring`

[`smoke_ring.py`](smoke_ring.py) softens the baseline with heavy blur, a
cyclic colormap, lifted midtones, and a larger central hole.

This turns the inverted disc into an atmospheric ring. The geometry is
still there, but it stops reading as mosaic and starts reading as cloud,
aurora, or gas. This is the gentlest stylization in the branch.

### `chrysalis`, `splat`, `bent`

These three keep the same general softened/significand logic but deform
the carrier surface itself.

- [`chrysalis.py`](chrysalis.py) maps the ring to a limaçon or egg-like
  shell
- [`splat.py`](splat.py) uses an irregular harmonic boundary to create a
  wobbling organic blob
- [`bent.py`](bent.py) lens-distorts the field in Cartesian space, as if
  the data were seen through singularities

This is the sculptural branch. The point is not new arithmetic. The
point is how much the same data can survive deformation and still retain
its characteristic banding and seam structure.

### `shattered`

[`shattered.py`](shattered.py) changes tone and grain aggressively.

- window width drops to `W = 2`
- gamma crush pushes most values into darkness
- only the hottest fragments burn through

This turns the inverted field into obsidian and lava. It is one of the
most transformed images in the entire fabric family, but it still reads
as a descendant of the same continuous field.

### `strata`

[`strata.py`](strata.py) extends `shattered` by multiplying the
significand frequency before the crush.

That creates contour-like repetition: several lava bands instead of one.
Structure that was hidden below the single-band threshold becomes
visible as repeated rings and layers.

If `shattered` is the volcanic image, `strata` is the geological one.

## What the branch shows

The inverted family makes three things clear.

- The significand field is rich enough to survive large geometric warps.
- Low-`n` detail often deserves more area than the raw rectangular view
  gives it.
- Once the field has been made continuous, tone mapping becomes as
  important as geometry.

That is why this branch feels different from the raw fabric. The raw
fabric is about digits as threads. The inverted family is about the same
field treated as atmosphere, shell, mineral, or lensing medium.

## Reading order

Read the branch in this order:

1. `significand_inverted.png`
2. `smoke_ring.png`
3. `chrysalis.png`
4. `splat.png`
5. `bent.png`
6. `shattered.png`
7. `strata.png`

That order moves from the clean inverted baseline through soft and
deformed variants, then ends with the two high-contrast geological
transformations.
