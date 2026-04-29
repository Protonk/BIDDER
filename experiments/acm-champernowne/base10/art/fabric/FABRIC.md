# Fabric

The `fabric/` folder is no longer one image. It is a family of
experiments built from the same base object: a rectangular field whose
rows are monoids `n` and whose columns are successive decimal digits in
the concatenated `n`-prime stream.

At the root, the fabric is simple:

- row = monoid `n`
- column = digit position
- value = a digit, a short window of digits, or a local digit relation

Everything else in this folder is a remapping of that object:

- the raw digit textile
- continuous sliding-window versions
- pairwise transition versions
- polar and inverted warps
- destruction tests under blur and scrambling

For `n >= 2`, the raw row is a finite prefix of the exact `n`-prime
digit stream. In the notation of `guidance/BQN-AGENT.md`, that source is
`ChamDigits10 (K↑ n NPn2 K)` for sufficiently large `K`. The art starts
there.

## Why "fabric"

The rectangular digit field behaves like cloth because two kinds of
structure cross each other:

- decimal position creates vertical bands and recurring columns
- the monoid sieve creates diagonal sweeps, seams, and curved boundaries

The decisive curves are where entry size changes. Roughly speaking, they
track thresholds of the form `nk = 10^d`. Those digit-length boundaries
are what make the field look woven rather than noisy. A random decimal
source would give colored static. The ACM source gives warp, weft, and
selvedge.

## How to read the family

Most images in this folder inherit the same geometry.

- Low `n` usually contains the richest visible structure.
- High `n` is often more regular and compressed.
- Straight bands usually come from fixed digit position.
- Diagonals and arcs usually come from digit-length transitions.
- When the data are turned from categorical digits into continuous
  values, seams appear where a sliding window crosses an entry boundary.

The top-level question is always the same: what happens if we keep the
same monoid digit field but change what each cell means, or how the
field is laid out in space?

## The top-level images

### `digit_fabric`

[`digit_fabric.py`](digit_fabric.py) is the canonical source image.

- Each row is one monoid `n = 1..600`.
- Each column is one digit position in the concatenated `n`-prime
  string.
- Color is the raw digit `0..9`.

This is the baseline textile. The rest of the folder should be read as
transformations of this rectangle.

### `significand_carpet`

[`significand_carpet.py`](significand_carpet.py) keeps the same rows but
replaces each cell with a 4-digit sliding-window significand in `[0,1)`.

This changes the field from categorical to continuous. Inside one
`n`-prime, adjacent windows change smoothly. At a boundary between
entries, the window suddenly blends two numbers, and that blend becomes
visible as a seam. The result is softer and more fluid than the raw
fabric, with moire and interference that are hard to see in the digit
palette version.

This is the main bridge from textile to landscape.

### `bigram_weave`

[`bigram_weave.py`](bigram_weave.py) encodes consecutive digit pairs
instead of single digits.

- red = current digit
- blue = next digit
- green = local contrast between them

This is still a fabric, but now the basic thread is a transition rather
than a digit. It reveals local Markov structure: which adjacent digit
pairs the sieve favors, and where abrupt changes occur.

[`bigram_flow.py`](bigram_flow.py) keeps the same bigram plane but draws
each transition as a short oriented stroke. Digits are placed on a
10-point ring, and each bigram becomes the chord from the current digit
to the next digit. The plane is then bent into a twisted polar shell,
with low `n` pushed outward and stroke directions transformed through
the local geometry. The same transition structure now appears as bright
currents on a curved surface rather than colored cells.

### `polar_fabric`

[`polar_fabric.py`](polar_fabric.py) wraps the rectangular digit fabric
into a disc.

- angle = digit position
- radius = monoid `n`

The rectangular warp becomes radial spokes. The diagonal sweeps become
spirals. This is the cleanest geometric warp in the folder, and it is
the conceptual doorway to the inverted branch.

## The branches

### `inverted/`

The inverted branch takes the continuous significand field and turns it
inside out.

The key move is radial inversion: low-`n` structure is pushed outward,
where it gets more visual area, while the more regular high-`n` region
compresses inward. From there the family splits into rings, shells,
blobs, lenses, and volcanic variants.

That branch now has enough internal structure to deserve its own doc:
[inverted/INVERTED.md](inverted/INVERTED.md).

### `noising/`

The noising branch asks the opposite question: how hard is it to destroy
the fabric?

It tests three different attacks:

- Gaussian blur
- digit permutation
- blur-scramble-blur "sandwich" damage

Those experiments are now best read as resilience studies on the fabric
object, not as isolated image-processing tricks. See
[noising/NOISING.md](noising/NOISING.md).

## What the family is really about

This folder is a study in representation.

The underlying mathematics does not change very much from image to
image. What changes is:

- whether we look at raw digits, windows, or transitions
- whether the value space is discrete or continuous
- whether the geometry is rectangular, polar, inverted, or deformed
- whether we preserve the structure or deliberately attack it

So the family grows along two axes:

- richer encodings of the same monoid digit field
- more aggressive spatial and tonal transformations of those encodings

## Practical reading order

If you want the family in a sensible order, use this:

1. `digit_fabric.png`
2. `significand_carpet.png`
3. `bigram_weave.png`
4. `polar_fabric.png`
5. `inverted/INVERTED.md`
6. `noising/NOISING.md`

That order moves from the canonical rectangular object outward into the
two major descendant branches: sculptural remapping and destructive
stress testing.
