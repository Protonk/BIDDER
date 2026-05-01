# Run 2026-05-01_null

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
  "primes": [
    2,
    3,
    5,
    7,
    11,
    13
  ],
  "seed": 0,
  "substrate": "synth_uniform",
  "transducer": "identity"
}
```

Tolerance TOL = 1e-12.

## Channel results (aggregated over all cells)

| channel | n_present | n_partial | n_absent | mean strength | min strength | max strength |
|---|---|---|---|---|---|---|
| `no_op` | 0 | 0 | 24 | 0.000000 | 0.000000 | 0.000000 |
| `zero_count` | 0 | 0 | 24 | 0.000000 | 0.000000 | 0.000000 |
| `value_multiset` | 0 | 0 | 24 | 0.000000 | 0.000000 | 0.000000 |
| `prime_row_identity_at_k1` | 0 | 0 | 24 | 0.000000 | 0.000000 | 0.000000 |

## Per-cell verdicts

| (p, h) | `no_op` | `zero_count` | `value_multiset` | `prime_row_identity_at_k1` |
|---|---|---|---|---|
| (2, 5) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (2, 6) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (2, 7) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (2, 8) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (3, 5) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (3, 6) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (3, 7) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (3, 8) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (5, 5) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (5, 6) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (5, 7) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (5, 8) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (7, 5) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (7, 6) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (7, 7) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (7, 8) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (11, 5) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (11, 6) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (11, 7) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (11, 8) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (13, 5) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (13, 6) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (13, 7) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (13, 8) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |

## Anomalies

None.
