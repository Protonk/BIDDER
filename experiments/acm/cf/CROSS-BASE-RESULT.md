# Cross-base validation of the closed-form spike scale

The closed-form spike scale

    S_k(n, b) = D_k(n, b) − C_{k−1}(n, b)
              = (n − 1)/n² · (b^{k−1} (k(b − 2) + b/(b − 1)) − 1/(b − 1))

(`MEGA-SPIKE.md`) is base-agnostic in its statement. Across
`b ∈ {3, 4, 6, 8, 10, 12}`, the `(b − 2)/(b − 1)` prefactor
structure holds: leading-order match within `0.05 %` to `9.4 %` in
base-`b` digits, with the sub-leading correction roughly
base-invariant in *decimal* digits.


## Panel

```
  b   n   d   pred_b-d    obs_b-d       gap     gap%
------------------------------------------------------------
  3   2   8    5194.00    5172.89    -21.11  -0.406%
  3   3   8    4616.89    4584.37    -32.52  -0.704%
  3   5   8    3324.16    3263.23    -60.93  -1.833%
  4   2   6    3413.25    3400.21    -13.04  -0.382%
  4   3   6    3034.00    3007.38    -26.62  -0.877%
  4   5   6    2184.48    2140.85    -43.63  -1.997%
  6   2   5    6868.75    6858.10    -10.65  -0.155%
  6   3   5    6105.56    6085.10    -20.45  -0.335%
  6   5   5    4396.00    4353.69    -42.31  -0.962%
  8   2   4    3218.25    3208.73     -9.52  -0.296%
  8   3   4    2860.67    2842.18    -18.49  -0.646%
  8   5   4    2059.68    2030.16    -29.52  -1.433%
 12   2   4   17751.25   17742.48     -8.77  -0.049%
 12   3   4   15778.89   15761.48    -17.41  -0.110%
 12   5   4   11360.80   11333.63    -27.17  -0.239%
```

`d` is chosen per base so the predicted spike sits comfortably
above the noise floor.


## Extended b = 10 sub-panel at d = 4

Filling in `n ∈ {7, 8, 9, 11, 12, 13, 15, 20}`:

```
 10   7   4    4054.41    4006.74    -47.67  -1.176%
 10   8   4    3621.52    3564.85    -56.66  -1.565%
 10   9   4    3270.22    3209.86    -60.36  -1.846%
 10  11   4    2736.45    2665.21    -71.24  -2.603%
 10  12   4    2529.31    2438.76    -90.55  -3.580%
 10  13   4    2351.08    2257.07    -94.01  -3.998%
 10  15   4    2060.24    1950.75   -109.49  -5.314%
 10  20   4    1572.77    1425.45   -147.32  -9.367%
```

The sub-panel dissolves a finite-panel artifact: the original
6-cell panel showed `n = 10` at 97.6 % match while `n ∈ {2..6}`
sat above 99 %. With `n` filled in across `{2..20}`, `n = 10`
sits smoothly between `n = 9` (98.2 %) and `n = 11` (97.4 %). No
d = 4 anomaly at `n = 10`.


## Decimal-digit base-invariance

For fixed `n`, the gap in *decimal* digits across bases:

| b  | n=2 gap (dec) | n=3 gap (dec) | n=5 gap (dec) |
|---:|---:|---:|---:|
| 3  | −10.07 | −15.51 | −29.04 |
| 4  | −7.85  | −16.02 | −26.27 |
| 6  | −8.28  | −15.91 | −32.93 |
| 8  | −8.59  | −16.69 | −26.66 |
| 10 | −10.10 | −16    | −32    |
| 12 | −9.46  | −18.79 | −29.32 |

`gap_decimal` is roughly base-invariant for each `n`:

- n = 2: ~−9 ± 1 across bases.
- n = 3: ~−16 ± 2.
- n = 5: ~−29 ± 4.

The sub-leading correction is `O(1)` in `b` (in decimal-digit
terms) with all of the `b`-dependence carried by the leading-order
`(b − 2)/(b − 1)` factor.


## What the cross-base panel confirms

1. The closed-form prefactor `(b − 2)/(b − 1)` is the correct base
   shape. A naive guess `(b − 1)/b` would fit `b = 10` within 1 %
   at `k = 4` and would be hard to distinguish from `(b − 2)/(b − 1)`
   at one base; the cross-base panel separates them sharply.
   Empirical asymptotic ratio `gap / D_k → (b − 2)/(b − 1)` is
   constrained at six bases.

2. The closed form is structural, not a `b = 10` numerical fit.
   The formula `S_k(n, b)` is empirically sharp at all six tested
   bases.

3. The b = 10 d = 4 n-monotone curve is smooth across the full
   tested range `n ∈ {2..20}`. The "n = 10 outlier" reading from
   the original 6-cell panel was an artifact of the finite panel.


## What the cross-base panel does not address

- The off-spike denominator process. Each base in this panel was
  tested at one `d` only, and only the leading-order `S_k` was
  checked. The Family A/B classification of `offset(n)` is
  base-specific (because `ord(b, n)` shifts with `b`), so per-`b`
  family compositions need to be redone separately.
- The d-axis at fixed base. d-scaling is the subject of
  `D5-RESULT.md`.
- Step 3 of `MECHANISTIC-DERIVATION.md`. Cross-base data does not
  illuminate the off-spike denominator process.


## Files

- `cf_spikes_extended.py` — panel runner.
- `cf_extended.csv` — per-cell data.
- `cf_extended_summary.txt` — same data, table form.
- `cf_extended_run.log` — per-case timings and diagnostics.
