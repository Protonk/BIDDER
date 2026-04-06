# ACM-Champernowne Experiments

Experiments whose source object is the ACM-Champernowne construction
itself — concatenating n-primes into a positional real.

Split by base because base changes the construction fundamentally:

- **base10/** — Decimal concatenation. The leading-digit uniformity is
  non-trivial (9 equiprobable symbols). This is where the sawtooth,
  the rolling shutter, the digit fabrics, and the statistical tests
  live.

- **base2/** — Binary concatenation. Leading-digit uniformity collapses
  to triviality (the leading bit is always 1), but RLE becomes a
  structural fingerprint of the monoid's 2-adic valuation. This is
  where the forest experiments, disparity analysis, and RLE art live.

See [BINARY.md](base2/BINARY.md) for the full argument about why the
base-2 construction is a different mathematical object.
