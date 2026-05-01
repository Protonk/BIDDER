# Run 2026-05-01_identity

## Config

```json
{
  "K": 4000,
  "heights": [
    5,
    6,
    7,
    8
  ],
  "lattice_dir": "/Users/achyland/Desktop/Math/Tokoyami/forays/BIDDER/experiments/acm-champernowne/base10/art/q_distillery",
  "primes": [
    2,
    3,
    5,
    7,
    11,
    13
  ],
  "substrate": "lattice",
  "transducer": "identity"
}
```

Tolerance TOL = 1e-12.

## Channel results (aggregated over all cells)

| channel | n_present | n_partial | n_absent | mean strength | min strength | max strength |
|---|---|---|---|---|---|---|
| `no_op` | 24 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| `zero_count` | 24 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| `value_multiset` | 21 | 3 | 0 | 0.999969 | 0.999750 | 1.000000 |
| `prime_row_identity_at_k1` | 24 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |

## Per-cell verdicts

| (p, h) | `no_op` | `zero_count` | `value_multiset` | `prime_row_identity_at_k1` |
|---|---|---|---|---|
| (2, 5) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (2, 6) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (2, 7) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (2, 8) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (3, 5) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (3, 6) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (3, 7) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (3, 8) | present (1.0000) | present (1.0000) | partial (0.9998) | present (1.0000) |
| (5, 5) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (5, 6) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (5, 7) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (5, 8) | present (1.0000) | present (1.0000) | partial (0.9998) | present (1.0000) |
| (7, 5) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (7, 6) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (7, 7) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (7, 8) | present (1.0000) | present (1.0000) | partial (0.9998) | present (1.0000) |
| (11, 5) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (11, 6) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (11, 7) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (11, 8) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (13, 5) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (13, 6) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (13, 7) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |
| (13, 8) | present (1.0000) | present (1.0000) | present (1.0000) | present (1.0000) |

## Anomalies

- (3, 8) `value_multiset`: got `partial` (strength 0.999750), expected `present`
- (5, 8) `value_multiset`: got `partial` (strength 0.999750), expected `present`
- (7, 8) `value_multiset`: got `partial` (strength 0.999750), expected `present`
