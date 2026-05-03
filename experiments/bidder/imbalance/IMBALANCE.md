# Prefix imbalance

Endpoint leading-digit exactness does not say whether the order is usable. The
block `[1000, 9999]` contains exactly 1000 integers with each leading digit
`1` through `9`, so lexicographic order and any permutation of the block have
the same terminal counts.

`prefix_imbalance.py` measures the maximum finite-population standardized
deviation over all prefixes:

```text
max_t max_digit |C_digit(t) - t/9| / sd_hypergeometric(t)
```

It compares three order families:

- lexicographic block order;
- 64 BIDDER keyed orders over the same exact-balanced block;
- 256 random permutations of the block.

The visual is `prefix_imbalance.png`; the numeric summary is
`prefix_imbalance_summary.txt`; the plotted paths are in
`prefix_imbalance_paths.csv`.

This is a diagnostic comparison, not a claim that BIDDER keys are distributed
as uniformly random permutations.
