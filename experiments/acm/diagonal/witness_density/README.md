# Witness density — composite lattice scatter

`lattice_scatter.png` renders the **composite lattice**
`{(k, n) : 2 ≤ k < n, k·n ≤ 100}` as a scatter, with each point one
*non-trivial* witness pair `(k, n)` for the integer `k·n`. Color
encodes the target `k·n`, binned into 5 ascending bands at
`[6, 12, 20, 35, 60, 100]` — the lower region is split more finely
because that is where the densest lattice structure lives. Three
row-map curves and one highly-composite hyperbola are overlaid.

`witnesses.npz` is the substrate file. It maps each composite `N`
from 4 to 1000 that has at least one non-trivial witness to the
array of its witness pairs `(k, N/k)` with `k | N`, `k ≥ 2`, and
`k < √N`. Plots 6, 8, and 9 of `CANTORS-PLOT.md` consume this file
directly; rebuild it by re-running the script. The trivial row map
at `k = 1` (which catches every integer `N` as `D_1 = n_1 = N`) is
excluded throughout — primes and squares of primes therefore have no
witnesses and are omitted from the file.

## What the eye is supposed to see

**The lattice itself.** The scatter lives strictly above the
diagonal `n = k` because the constraint is `k < n`, and strictly to
the right of `k = 1` because the trivial row map is excluded. The
triangular region is the universe of non-trivial witness pairs for
composites up to 100. Columns thin out as `k` grows because the
available `n` range shrinks with each step; `k = 9` has only
`(9, 10)` and `(9, 11)`, and `k = 10` is empty.

**Row maps as curves.** Three ascending row maps are drawn as colored
lines: the pronic map `n = k + 1` (red, the shallowest possible),
`n = 2k + 1` (blue), and the prime-indexed map `n = p_k` (purple,
which curves upward as primes thin out). Each curve picks out one
lattice point per column. The diagonal stream of that row map is
exactly the sequence of `k · n` values along its curve. *That* is
the row-map ↔ curve correspondence the garden's intro paragraph
asserts; here it is, drawn.

**Constant-`N` hyperbolas, by color alone.** The 5 viridis bands
make hyperbolic structure visible without any explicit annotation.
Points sharing the same target `N` share a color band, so the eye
naturally traces curves of constant `k · n` running from upper-left
(small `k`, large `n`) to lower-right (large `k`, small `n`). The
green band, for instance, contains every witness pair with
`k · n ∈ [40, 60]`; all 5 witnesses of `N = 60` sit in this band,
along with witnesses of `42, 45, 48, 50, 54, 56, …`.

**The hyperbola of one composite, called out.** `k · n = 60` is the
dotted black curve. Its 5 non-trivial integer witnesses are marked
as labelled circles: `(2, 30), (3, 20), (4, 15), (5, 12), (6, 10)`.
Each one is a different lossy sieve that catches `60` as its
diagonal entry. The witness count of `60` under `k ≥ 2` is
`d(60)/2 − 1 = 5`, and you can read it off the picture by counting
circles.

## What it confirms (and what it doesn't)

The scatter confirms that the witness density of `N` is `⌊d(N)/2⌋`
for non-squares, which is the divisor function in the disguise the
plot's name promises. The script asserts this against a brute-force
divisor enumeration before rendering, so a wrong formula would fail
the assertion before the plot exists.

What the picture does *not* do is add new arithmetic information
about `d(N)`. Its job is structural: name the lattice as a visible
object, show how row maps live inside it, and produce the per-composite
witness data structure that downstream plots will optimize over.

## What to try next

The lattice scatter is the substrate for two natural follow-ups,
both of which can reuse `witnesses.npz` directly:

- **Plot 9 (cheapest sieve per target).** For each composite `N`,
  pick the witness pair `(k, N/k)` that minimizes some cost (smallest
  `k`, smallest description length of the implied row map, etc.) and
  re-render the scatter colored by which row map wins at each lattice
  point. The expected output is a Voronoi-style partition of the
  lattice into "cheapest-sieve regions."

- **Plot 8 (complementary curves).** Take a pair of row maps, render
  both curves on the lattice, and color points by which curve catches
  them (or both, or neither). The leaderboard is "coverage minus
  overlap" computed from `witnesses.npz`.

Both inherit the data file, the assertion harness, and the rendering
substrate from this script.

## Reproduce

```
sage lattice_scatter.py
```

Writes `lattice_scatter.png` and `witnesses.npz` in this directory.
