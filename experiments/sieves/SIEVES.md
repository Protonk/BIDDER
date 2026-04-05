# Sieves

Two visualizations of the n-prime sieve structure.

Run: `sage -python moire_sieves.py` and `sage -python sieve_carpet.py`


## Moire Sieves

A bitmap where pixel (k, n) is lit if integer k is an n-prime. Rows are
monoid indices n = 1..400. Columns are integers 1..600. The fan of
diagonal rays — each the line val = n*k for successive k — creates
natural moire interference.

### Why it's art

The image is a pure combinatorial object rendered without smoothing,
interpolation, or aesthetic intervention. The moire is structural, not
artifactual. The ray slopes are 1, 1/2, 1/3, ... (the harmonic series),
and their interference pattern encodes the multiplicative relationships
between monoids. The dense region in the lower right, where many monoids
overlap, is where compositeness pressure is highest.

### What makes it non-obvious

Row 1 (ordinary primes) is visibly different from every other row — its
points are sparse and irregular. Every other row has the same density
(fraction (n-1)/n of integers survive) but shifted. The moire between
these near-identical sieves is a visual metaphor for the near-misses
of unique factorization.

### Format

Wide landscape (18" x 10"), hot colormap on black. Meant to be viewed
at a distance where the interference dominates.


## Sieve Carpet

Each row is a monoid (n = 2..500). Each column is a position in the
n-prime sequence (1..200). Color encodes the gap between consecutive
n-primes, normalized by n. Most gaps are 1 (adjacent survivors); the
bright rays mark positions where the sieve deletes a cluster, creating
a double gap.

### Why it's art

The diagonal rays are hyperbolas in (position, n) space, marking the
loci where the k-th n-prime crosses a multiple of n^2. They fan out
from the origin like searchlight beams. Between the rays, the carpet is
a uniform dark field — the "expected" gap structure of a single deletion
sieve. The rays are where expectation breaks.

### Format

Wide landscape (18" x 10"), inferno colormap on dark background.
Clipped at gap/n = 4 to preserve dynamic range.


## Next steps

- **Interactive moire.** Let the viewer select which rows (monoid
  indices) to overlay. The interference pattern changes as you add
  or remove sieves — a direct manipulation of multiplicative structure.
