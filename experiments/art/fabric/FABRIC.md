# Digit Fabric

Each row is one n (1-600). Each column is a digit position in the
concatenated n-prime string. Color encodes digit value (0-9). For
n >= 2, each row is `ChamDigits10 (K↑ n NPn2 K)` — the exact
digit stream of the first K n-primes (`guidance/BQN-AGENT.md`).
The result is a 600 x 80 textile whose warp and weft are number
theory and typography.

Run: `sage -python digit_fabric.py`

## Why it's art

It looks like woven cloth. The vertical color bands (certain positions
favor certain digits) create the warp. The diagonal sweeps (as n
increases, the n-primes shift) create the weft. The black curves where
zeros cluster are the selvedge. You can see the decimal system's
structure — the transition from 1-digit to 2-digit n-primes, the ripple
when carries propagate — without knowing any mathematics.

## What makes it non-obvious

The fabric is not random. A uniform random source would produce visual
static. The structure you see is the sieve nZ+ imposing order on the
digit stream — the same order that produces exact uniformity in first
digits and the rolling shutter under addition. The textile *is* the
monoid.

## Format

Wide horizontal panel (20" x 14"), dark background. The 10-color palette
is chosen for perceptual distinctness, not mathematical ordering.

## Next steps

- **Higher resolution.** Push n to 10000 and digits to 200. The fabric
  at that scale would show the full digit-class transitions and could
  be printed at textile resolution.

- **Base variation.** Repeat in base 2, 3, 6, 12. The textile patterns
  will differ because the digit boundaries fall at different powers.
  Base 6 (highly composite) vs base 10 (semi-prime) would be a clean
  comparison.
