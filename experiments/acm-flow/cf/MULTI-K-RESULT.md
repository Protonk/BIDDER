# Multi-k closure of the spike formula at b = 10

The spike formula

    log_b(a_{i_k}) = T_k − 2 L_{k−1} + log_b(b/(b−1)) − O(b^{−k})

(`MEGA-SPIKE.md`) holds across `k ∈ {2, 3, 4}` at `b = 10` for the
panel `n ∈ {2, 3, 4, 5, 6, 10}` once two refinements are made:
`T_k` is computed by direct atom counting rather than from the
smooth-block formula, and the residual is read at the universal
`log_b(b/(b−1))` constant.


## Smooth `T_k` is not enough

If `T_k` is computed from the smooth-block expression
`T_k = Σ d · (b−1) b^{d−1} (n−1)/n²`, the residual
`log_b(a) − (T_k − 2 log_b(q_{i−1}))` is roughly constant in `k`
for fixed `n`, but per-`n` offsets range from `+0.04` to `+1.04`:

| n | k=2 | k=3 | k=4 |
|---|---|---|---|
| 2 | +0.78 | +0.79 | +0.80 |
| 3 | +0.03 | +0.04 | +0.05 |
| 4 | −1.40 | −0.64 | +1.36 |
| 5 | +0.78 | +0.80 | +0.81 |
| 6 | +0.78 | +0.79 | +0.80 |
| 10 | +1.04 | +1.03 | +1.04 |

The per-`n` offset and the n=4 oscillation reduce to smooth-vs-actual
block-count error: when `n^2 | b^{k−1}` fails, the smooth formula
misses by an `O(1)` integer per block, accumulating into the `T_k`
displacement.


## Actual `T_k` collapses the offsets

Switching `T_k` to direct atom counting collapses every per-`n`
offset, including the `n = 4` oscillation:

| n | k=2 | k=3 | k=4 |
|---|---|---|---|
| 2 | +0.0322 | +0.0444 | +0.0456 |
| 3 | +0.0322 | +0.0444 | +0.0456 |
| 4 | +0.0408 | +0.0453 | +0.0455 |
| 5 | +0.0195 | +0.0431 | +0.0455 |
| 6 | +0.0318 | +0.0444 | +0.0456 |
| 10 | +0.0453 | +0.0410 | +0.0453 |

At `k = 4` the residuals are uniformly `~0.0455` across every `n`,
matching the universal boundary-truncation constant

    log_b(b / (b − 1)) = log_{10}(10/9) = 0.045757…


## Geometric decay of the deficit

The deficit `log_{10}(10/9) − r(n, k)` decays geometrically with `k`:

| n | deficit k=2 | deficit k=3 | deficit k=4 | ratio 2→3 | ratio 3→4 |
|---|---|---|---|---|---|
| 2 | +0.0136 | +0.0014 | +0.0002 | 9.99 | 8.62 |
| 3 | +0.0136 | +0.0014 | +0.0002 | 9.99 | 8.62 |
| 5 | +0.0263 | +0.0027 | +0.0003 | 9.88 | 10.32 |
| 6 | +0.0140 | +0.0014 | +0.0002 | 10.28 | 8.62 |

The deficit ratio is `b = 10` per `k` step, so

    deficit(n, k) = β(n) · b^{−k} + higher order.

`n = 2` and `n = 3` produce identical deficits at this precision,
so the coefficient `β` is shared between at least these two `n`.
For `n = 5`, `β` is roughly twice as large.


## The formula at this resolution

    log_b(a_{i_k}) = T_k(actual) − 2 log_b(q_{i−1}) + log_b(b/(b − 1)) − β(n) · b^{−k} + …

Substrate-transparent on the right-hand side:

- `T_k(actual)` — exact atom count, closed form in `n`, `b`, `k`.
- `log_b(b/(b − 1))` — universal across `n`. The boundary-truncation
  factor at the d=k boundary, where the convergent matches the
  digit expansion to slightly more than `T_k` digits, with the
  fractional excess approaching this constant.

Not yet substrate-transparent:

- `log_b(q_{i−1}) = L_{k−1}` — the previous convergent's log
  denominator, consumed empirically here. The leading-order
  decomposition `L_{k−1} = C_{k−1} + (n−1)k + offset(n)` is in
  `OFFSPIKE-RESULT.md` and `PRIMITIVE-ROOT-FINDING.md`.
- `β(n)` — the `b^{−k}` coefficient; some `n` share it, others
  differ. Probably encodes fine-scale boundary alignment of the
  convergent with the next n-prime.


## d=5 confirmation

The same formula holds at `k = 5` with relative gap roughly 10×
smaller than at `k = 4`, consistent with the geometric decay of
the residual. Details in `D5-RESULT.md`.


## Files

- `spike_drift_multi_k.py` — multi-k script with smooth and actual
  `T_k` columns.
- `spike_drift_multi_k.csv` — per-(n, k) results.
- `spike_drift_multi_k_summary.txt` — text table.
