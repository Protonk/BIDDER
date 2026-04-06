# Entropy Landscape

## Setup

20 monoids spanning v_2 = 0..7, 10,000 n-primes each (~167,000 bits
per stream), k-gram entropy for k = 1..16. The deficit from 1.0 (a
fair coin) measures the algebraic content the ACM structure injects.


## Findings

### The deficit grows with k

At every v_2 level, the entropy deficit increases as the window
size k grows. There is no plateau at k=16. The algebraic content
extends to longer and longer windows — the ACM structure creates
correlations that single-bit entropy cannot see.

### Two regimes

**Low v_2 (odd n, v_2 = 0-2):** Deficit at k=1 is near zero
(~0.001). By k=16 it reaches 0.025-0.039. The ratio k=16 / k=1
is enormous — 25x to 650x. These streams look nearly random at
the single-bit level but carry substantial structure in their
16-grams. The algebra hides in long-range correlations.

The extreme case is n=6 (v_2=1): deficit at k=1 is 0.000054 (nearly
perfect single-bit randomness), but at k=16 it is 0.035 — a ratio
of 652x. The boundary stitch experiment showed why: the k mod n
statistics create inter-bit correlations that only become visible
in longer windows.

**High v_2 (n = 32, 64, 128):** Deficit at k=1 is already
substantial (0.04-0.08). By k=16 it reaches 0.10-0.17. The ratio
is only 2x. These streams are visibly structured at every scale.
The trailing zeros create a baseline deficit present at k=1, and
growth with k adds to it but does not dominate.

### v_2 stratification

The top 10 highest-deficit monoids are, without exception, ranked
by v_2. n=128 (v_2=7) has the highest deficit at every k. Then
n=64 (v_2=6), then n=192 (v_2=6), then n=32 (v_2=5). The same
grading found in:

- RLE spectroscopy (run-length ridges)
- Boundary stitch (trailing-zero barcode width)
- One bias (sieve residual magnitude)
- Autocorrelation (peak amplitude)

appears here unchanged. At every scale we have measured, the binary
Champernowne stream's algebraic content is dominated by the 2-adic
valuation.

### No new structure beyond v_2

We hoped that at high k, new structure might emerge — dependencies
on the odd part of n, or on the multiplicative order of 2 mod n'.
This does not happen in the range k=1..16, n=1..200. The entropy
landscape is stratified by v_2 alone. If there is structure from
the odd part, it lives at k > 16 or n > 200, below the resolution
of this measurement.


## Files

- `entropy_landscape_deep.py` — computation and plotting
- `entropy_landscape_deep.png` — heatmap (monoid x k)
- `entropy_landscape_traces.png` — line traces colored by v_2
