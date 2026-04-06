# RLE

These images are art experiments built from the binary Champernowne
streams of ACM monoids. They are not separate mathematical objects; they
are stylized views of one underlying measurement:

1. Generate the binary stream for a monoid `n` by concatenating the
   binary expansions of its first `n`-primes.
2. Run-length encode that stream into consecutive `(bit, length)` pairs.
3. Turn the resulting run statistics into an image.

The shared implementation lives in [`../../binary/binary_core.py`](../../binary/binary_core.py).
The quantitative argument for why this matters lives in
[`../../binary/BINARY.md`](../../binary/BINARY.md) and the more analytic
companions under [`../../binary/forest/`](../../binary/forest/).

## Why RLE matters here

RLE is unusually natural on the binary side of this project.

For a random bit stream, run lengths decay geometrically: short runs are
common, long runs are rare, and the expected run length is `2`. If the
binary ACM stream were visually random, its run statistics would mostly
look like that universal background.

But the ACM stream is not just "some bits." Every entry is a multiple of
`n`, and in binary that means every entry has at least `v_2(n)` trailing
zeros. Every next entry also begins with a leading `1`. So the entry
boundary has a built-in pattern:

`... 0 0 0 | 1 ...`

with the guaranteed zero block controlled by `v_2(n)`, the 2-adic
valuation of the monoid. That makes run lengths a structural
fingerprint. In particular:

- `0`-runs carry most of the monoid signal, because trailing zeros are
  algebraically forced.
- `1`-runs are still useful, but mostly as contrast and control.
- Powers of `2` and high-`v_2` multiples should stand out immediately.
- The universal geometric decay is always present, so the real structure
  lives in departures from that decay.

That last point matters for reading these images. RLE art works best
when it highlights deviations from the background, not when it gives the
background the whole canvas.

## How to read these images

Across the set, the same rules mostly apply:

- Brightness means "this run length is common for this monoid" or "this
  scalar summary is large."
- Cool colors usually encode `0`-run information.
- Warm colors usually encode `1`-run information.
- Short runs dominate the raw mass. Any layout that maps run length
  directly to a large spatial dimension will naturally over-brighten the
  short-run region.
- Vertical or radial eruptions usually indicate large `v_2(n)`.
- Powers of `2` are the cleanest cases; nearby multiples such as
  `3*2^k` and `5*2^k` often echo the same structure more weakly.

These are not boundary images. They do not preserve the exact local
position of every run. They preserve the distribution of run lengths.
That makes them good at showing global algebraic bias and weaker at
showing local syntax. For the exact boundary object, see
[`../../binary/forest/boundary_stitch/`](../../binary/forest/boundary_stitch/).

## The experiments

### `rle_mirror`

[`rle_mirror.py`](rle_mirror.py) renders the cleanest direct picture in
this folder.

- The x-axis is monoid index `n`.
- The top half is the `0`-run histogram, flipped so long runs sit at the
  outer top edge and short runs sit at the center seam.
- The bottom half is the `1`-run histogram, with short runs at the seam
  and longer runs lower down.
- The final image is cropped to `n = 1..128`, which keeps the square
  format and makes early monoid structure legible.

This is the easiest image to parse as data. The seam is the short-run
zone. The top half carries the stronger structure. The bottom half is
more uniform and acts as a foil. Read it as a mirrored heatmap with the
axes removed.

### `rle_ridgeline`

[`rle_ridgeline.py`](rle_ridgeline.py) is the most interpretive and,
arguably, the most revealing.

It uses only `0`-runs and subtracts the mean `0`-run distribution before
plotting. That is the right move artistically and scientifically: it
removes the universal exponential decay and shows the residual shape,
which is where the monoid fingerprint actually lives.

- Each row is one monoid from a curated subset.
- The x-axis is run length.
- Only positive residuals are rendered, as ridges.
- Color and line weight increase with `v_2(n)`.

This is why the image has periodic eruptions rather than a smooth slope.
It is not showing "all the runs"; it is showing excess mass over the
generic background. High-`v_2` monoids bulge to the right because they
create more medium and long `0`-runs than the average monoid does.

If the question is "where is the algebra in the RLE distribution?",
this is the strongest image in the set.

### `rle_spiral`

[`rle_spiral.py`](rle_spiral.py) wraps the two histograms around a
single spiral arm.

- Moving along the arm advances through monoids.
- Moving inward from the arm's midline reads `0`-run lengths.
- Moving outward from the arm's midline reads `1`-run lengths.
- Cool inner colors are `0`-runs; warm outer colors are `1`-runs.

This works better than the pure polar attempt because it keeps monoid
order on a continuous path rather than distributing it only by angle.
The image is less literal than `rle_mirror`, but it preserves the
duality between the two run families and makes the two-sided structure
feel like one object.

Use this one to see continuity and recurrence. Use `rle_mirror` if you
need the cleanest reading.

### `sunflower_attempt`

[`sunflower_attempt.py`](sunflower_attempt.py) is a scalar reduction:
each monoid becomes one point on a phyllotaxis lattice, colored by its
mean `0`-run length.

This is attractive, but it throws away most of the distributional
information. It keeps only one number per monoid. That makes it useful
for one narrow question:

- Which monoids have unusually large average `0`-runs?

The answer is mostly "the powers of `2`, then the high-`v_2`
multiples," which is exactly what the underlying algebra predicts. The
golden-angle placement has no mathematical connection to the binary ACM
structure, so the visible spirals are interference between the layout
and the data, not a theorem.

This is an exploratory art piece, not the best explanatory one.

### `corona_attempt`

[`corona_attempt.py`](corona_attempt.py) is included because it teaches
something important by failing.

It maps monoid to angle and run length to radius inside a disk. That is
the wrong geometry for these data. Since run-length frequencies decay so
quickly, almost all visual mass collapses into the inner bins. The
result is an overexposed bright core with faint outer flares.

Those flares are not meaningless; high-`v_2` monoids really do push more
mass outward. But the coordinate system gives far too much area to the
part of the distribution with almost no weight. So the picture is mostly
about the decay law, not about the algebraic deviations.

This is the negative lesson in the folder: for RLE, direct radius is too
expensive a coordinate.

## What the set shows overall

Taken together, these experiments make a simple point:

- RLE is not just a compression trick here.
- On the binary side, it becomes a probe of monoid structure.
- The main signal is 2-adic.
- `0`-runs are the primary carrier of that signal.
- Good visualizations either compare `0`-runs and `1`-runs directly, or
  subtract the universal background before rendering.

So the folder is really a study in representational choices:

- `rle_mirror` is the cleanest direct map.
- `rle_ridgeline` is the best deviation map.
- `rle_spiral` is the most successful ornamental transformation.
- `sunflower_attempt` is a plausible scalar summary with real loss.
- `corona_attempt` is an instructive failure.

## Practical reading order

If you are new to the set, read the images in this order:

1. `rle_mirror.png`
2. `rle_ridgeline.png`
3. `rle_spiral.png`
4. `sunflower_attempt.png`
5. `corona_attempt.png`

That order moves from "closest to the underlying histogram" to
"farthest from it."
