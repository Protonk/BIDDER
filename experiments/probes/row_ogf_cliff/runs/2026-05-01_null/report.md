# Run 2026-05-01_null

## Config

```json
{
  "H_max": 9,
  "exponents": [
    1,
    2,
    3,
    4
  ],
  "primes": [
    2,
    3,
    5,
    7
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
| `no_op` | 0 | 0 | 16 | 0.000000 | 0.000000 | 0.000000 |
| `cliff` | 0 | 0 | 16 | 0.000000 | 0.000000 | 0.000000 |
| `leading_multinomial` | 0 | 0 | 16 | 0.000000 | 0.000000 | 0.000000 |
| `qe_closed_form` | 0 | 0 | 16 | 0.000000 | 0.000000 | 0.000000 |
| `prime_row_identity_at_h1` | 0 | 0 | 16 | 0.000000 | 0.000000 | 0.000000 |

## Per-cell verdicts

| (p, q, e) | `no_op` | `cliff` | `leading_multinomial` | `qe_closed_form` | `prime_row_identity_at_h1` |
|---|---|---|---|---|---|
| (2, 3, 1) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (2, 3, 2) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (2, 3, 3) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (2, 3, 4) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (3, 2, 1) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (3, 2, 2) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (3, 2, 3) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (3, 2, 4) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (5, 2, 1) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (5, 2, 2) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (5, 2, 3) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (5, 2, 4) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (7, 2, 1) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (7, 2, 2) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (7, 2, 3) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |
| (7, 2, 4) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) | absent (0.0000) |

## Anomalies

None.
