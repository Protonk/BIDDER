# Noising

Three experiments on destroying the digit fabric's structure.


## Gaussian Blur (noising_gaussian.py)

The fabric survives Gaussian blur far longer than expected.
Structure spans scales from 1 pixel to 500 pixels:

- sigma=2: pixel-level sieve texture gone, all arcs intact
- sigma=8: fine arcs gone, broad arcs sharp
- sigma=32: 3-4 broad bands, hyperbolic sweep visible
- sigma=128: one soft gradient, corner barely present

The resilience comes from the hyperbolas nk = 10^d, which are
self-similar across scales. Each successive arc is a copy of
the same curve at a different scale. Blur removes arcs from
fine to coarse but cannot attack them all at once.


## Digit Permutation (noising_permutation.py)

A random permutation of {0,...,9} applied to all pixel values
does zero structural damage. The arcs recolor but never move,
blur, or break. The composition of any number of permutations
is another permutation — invertible, information-preserving.

The structure is geometric (spatial arrangement of digit-class
boundaries), not chromatic (which digit has which color).
Permutation changes the color of the paint. The paint is still
there, covering the same surface, in the same pattern.


## The Sandwich (noising_sandwich.py)

Gaussian sigma=2, then a nonlinear value scramble, then
Gaussian sigma=2 again. More destructive than Gaussian sigma=4
alone (same total blur budget).

The mechanism:
1. First blur makes values continuous (integers become reals)
2. Nonlinear scramble distorts the continuous values — smooth
   ramps between arcs become jagged, non-monotone
3. Second blur smooths the jagged damage into something
   irreversible

The first blur creates vulnerability. The scramble exploits it.
The second blur locks in the damage. Neither blur alone
accomplishes this — it is the nonlinearity between two linear
operations that breaks the structure's resilience.

This is the mixing strategy that beats Gaussian alone: insert
a nonlinear operation between two small blurs. The total blur
is modest but the damage is disproportionate.
