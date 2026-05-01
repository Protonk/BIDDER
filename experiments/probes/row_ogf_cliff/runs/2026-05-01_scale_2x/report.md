# Run 2026-05-01_scale_2x

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
  "substrate": "algebra",
  "transducer": "scale_2x"
}
```

Tolerance TOL = 1e-12.

## Channel results (aggregated over all cells)

| channel | n_present | n_partial | n_absent | mean strength | min strength | max strength |
|---|---|---|---|---|---|---|
| `no_op` | 0 | 16 | 0 | 0.722222 | 0.555556 | 0.888889 |
| `cliff` | 16 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |
| `leading_multinomial` | 0 | 0 | 16 | 0.000000 | 0.000000 | 0.000000 |
| `qe_closed_form` | 0 | 16 | 0 | 0.722222 | 0.555556 | 0.888889 |
| `prime_row_identity_at_h1` | 0 | 0 | 16 | 0.000000 | 0.000000 | 0.000000 |

## Per-cell verdicts

| (p, q, e) | `no_op` | `cliff` | `leading_multinomial` | `qe_closed_form` | `prime_row_identity_at_h1` |
|---|---|---|---|---|---|
| (2, 3, 1) | partial (0.8889) | present (1.0000) | absent (0.0000) | partial (0.8889) | absent (0.0000) |
| (2, 3, 2) | partial (0.7778) | present (1.0000) | absent (0.0000) | partial (0.7778) | absent (0.0000) |
| (2, 3, 3) | partial (0.6667) | present (1.0000) | absent (0.0000) | partial (0.6667) | absent (0.0000) |
| (2, 3, 4) | partial (0.5556) | present (1.0000) | absent (0.0000) | partial (0.5556) | absent (0.0000) |
| (3, 2, 1) | partial (0.8889) | present (1.0000) | absent (0.0000) | partial (0.8889) | absent (0.0000) |
| (3, 2, 2) | partial (0.7778) | present (1.0000) | absent (0.0000) | partial (0.7778) | absent (0.0000) |
| (3, 2, 3) | partial (0.6667) | present (1.0000) | absent (0.0000) | partial (0.6667) | absent (0.0000) |
| (3, 2, 4) | partial (0.5556) | present (1.0000) | absent (0.0000) | partial (0.5556) | absent (0.0000) |
| (5, 2, 1) | partial (0.8889) | present (1.0000) | absent (0.0000) | partial (0.8889) | absent (0.0000) |
| (5, 2, 2) | partial (0.7778) | present (1.0000) | absent (0.0000) | partial (0.7778) | absent (0.0000) |
| (5, 2, 3) | partial (0.6667) | present (1.0000) | absent (0.0000) | partial (0.6667) | absent (0.0000) |
| (5, 2, 4) | partial (0.5556) | present (1.0000) | absent (0.0000) | partial (0.5556) | absent (0.0000) |
| (7, 2, 1) | partial (0.8889) | present (1.0000) | absent (0.0000) | partial (0.8889) | absent (0.0000) |
| (7, 2, 2) | partial (0.7778) | present (1.0000) | absent (0.0000) | partial (0.7778) | absent (0.0000) |
| (7, 2, 3) | partial (0.6667) | present (1.0000) | absent (0.0000) | partial (0.6667) | absent (0.0000) |
| (7, 2, 4) | partial (0.5556) | present (1.0000) | absent (0.0000) | partial (0.5556) | absent (0.0000) |

## Anomalies

None.
