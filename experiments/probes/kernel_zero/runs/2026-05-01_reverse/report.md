# Run 2026-05-01_reverse

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
  "transducer": "reverse"
}
```

Tolerance TOL = 1e-12.

## Channel results (aggregated over all cells)

| channel | n_present | n_partial | n_absent | mean strength | min strength | max strength |
|---|---|---|---|---|---|---|
| `no_op` | 0 | 24 | 0 | 0.946763 | 0.824225 | 0.996991 |
| `zero_count` | 24 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| `value_multiset` | 21 | 3 | 0 | 0.999969 | 0.999750 | 1.000000 |
| `prime_row_identity_at_k1` | 0 | 0 | 24 | 0.000000 | 0.000000 | 0.000000 |

## Per-cell verdicts

| (p, h) | `no_op` | `zero_count` | `value_multiset` | `prime_row_identity_at_k1` |
|---|---|---|---|---|
| (2, 5) | partial (0.9835) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (2, 6) | partial (0.9947) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (2, 7) | partial (0.9965) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (2, 8) | partial (0.9970) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (3, 5) | partial (0.9141) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (3, 6) | partial (0.9621) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (3, 7) | partial (0.9829) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (3, 8) | partial (0.9914) | present (1.0000) | partial (0.9998) | absent (0.0000) |
| (5, 5) | partial (0.8637) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (5, 6) | partial (0.9398) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (5, 7) | partial (0.9725) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (5, 8) | partial (0.9873) | present (1.0000) | partial (0.9998) | absent (0.0000) |
| (7, 5) | partial (0.8458) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (7, 6) | partial (0.9318) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (7, 7) | partial (0.9701) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (7, 8) | partial (0.9868) | present (1.0000) | partial (0.9998) | absent (0.0000) |
| (11, 5) | partial (0.8290) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (11, 6) | partial (0.9235) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (11, 7) | partial (0.9669) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (11, 8) | partial (0.9855) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (13, 5) | partial (0.8242) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (13, 6) | partial (0.9221) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (13, 7) | partial (0.9656) | present (1.0000) | present (1.0000) | absent (0.0000) |
| (13, 8) | partial (0.9853) | present (1.0000) | present (1.0000) | absent (0.0000) |

## Anomalies

- (3, 8) `value_multiset`: got `partial` (strength 0.999750), expected `present`
- (5, 8) `value_multiset`: got `partial` (strength 0.999750), expected `present`
- (7, 8) `value_multiset`: got `partial` (strength 0.999750), expected `present`
