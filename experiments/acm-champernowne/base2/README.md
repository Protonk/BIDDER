# ACM-Champernowne — Base 2

Binary Champernowne streams of arithmetic congruence monoids.

The construction and what changes from base 10:
[BINARY.md](BINARY.md)

## Experiment families

- **forest/** — Ten expeditions into the binary stream's structure:
  RLE spectroscopy, autocorrelation, entropy landscape, boundary
  stitch, epsilon teeth, violin diagnostics, and more.
  [MALLORN-SEED.md](forest/MALLORN-SEED.md)

- **disparity/** — Bit-balance (1-bias) analysis across monoids.

- **art/rle/** — RLE-based visualizations of binary streams.
  [RLE.md](art/rle/RLE.md)

## Shared code

[binary_core.py](binary_core.py) — stream generation, RLE, and
entry-boundary tracking for all experiments in this subtree.

## Theory

[FINITE-RECURRENCE.md](FINITE-RECURRENCE.md) — conjecture that no
finite automaton can recognize binary ACM streams.
