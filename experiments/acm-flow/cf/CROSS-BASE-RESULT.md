# Cross-base validation — closed form holds across b ∈ {3, 4, 6, 8, 10, 12}

The closed-form spike size

    S_k(n, b)  ≈  D_k(n, b)  −  C_{k-1}(n, b)
                =  (n − 1)/n²  ·  (b^{k−1} · (k(b − 2) + b/(b − 1))  −  1/(b − 1))

was first written in `MEGA-SPIKE.md` lines 41–49 and empirically
validated at b = 10, d = 4 across n ∈ {2, 3, 4, 5, 6, 10} in
`EXTENDED-PANEL-RESULT.md`. Empirical state going in: the formula
is sharp at b = 10 across primes and prime-powers; cross-base
behavior was untested.

This document tests the closed form across b ∈ {3, 4, 6, 8, 10, 12},
choosing d per base so the predicted spike sits comfortably above
the noise floor. **The (b − 2)/(b − 1) prefactor structure of the
closed form is not a base-10 artifact.** All 23 cells match
prediction within 0.05 % – 9.4 % in base-`b` digits, with the
sub-leading drift in *decimal* digits roughly base-invariant.


## Headline

Across the 23-cell panel, the leading-order match holds with the
predicted ratio `(b − 2)/(b − 1)` to base-`b` block size `D_k`
(equivalently, the formula's `S_k` works as written). No base
exhibits a structural anomaly. The decimal-digit gap at fixed `n` is
**flat across `b`**, supporting the reading that the sub-leading
correction is an `O(1)` decimal-digit edge-effect with the leading
order absorbing all of the `b`-dependence.


## Panel

```
  b   n   d   pred_b-d    obs_b-d       gap     gap%      i  valid
------------------------------------------------------------------------
  3   2   8    5194.00    5172.89    -21.11  -0.406%    860   5226
  3   3   8    4616.89    4584.37    -32.52  -0.704%    986   5012
  3   5   8    3324.16    3263.23    -60.93  -1.833%    962   4269
  4   2   6    3413.25    3400.21    -13.04  -0.382%    310   2364
  4   3   6    3034.00    3007.38    -26.62  -0.877%    296   2185
  4   5   6    2184.48    2140.85    -43.63  -1.997%    350   1962
  6   2   5    6868.75    6858.10    -10.65  -0.155%    202   1848
  6   3   5    6105.56    6085.10    -20.45  -0.335%    244   2626
  6   5   5    4396.00    4353.69    -42.31  -0.962%    284   2864
  8   2   4    3218.25    3208.73     -9.52  -0.296%     88   1105
  8   3   4    2860.67    2842.18    -18.49  -0.646%    118   1402
  8   5   4    2059.68    2030.16    -29.52  -1.433%    146   1464
 12   2   4   17751.25   17742.48     -8.77  -0.049%    136   1285
 12   3   4   15778.89   15761.48    -17.41  -0.110%    182   1649
 12   5   4   11360.80   11333.63    -27.17  -0.239%    250   2161
```

Plus the b = 10 sub-panel filling in `n ∈ {7, 8, 9, 11, 12, 13, 15, 20}`
at d = 4 (extends `EXTENDED-PANEL-RESULT.md`):

```
 10   7   4    4054.41    4006.74    -47.67  -1.176%    218   3161
 10   8   4    3621.52    3564.85    -56.66  -1.565%    208   3073
 10   9   4    3270.22    3209.86    -60.36  -1.846%    200   2923
 10  11   4    2736.45    2665.21    -71.24  -2.603%    258   2526
 10  12   4    2529.31    2438.76    -90.55  -3.580%    260   2383
 10  13   4    2351.08    2257.07    -94.01  -3.998%    288   2368
 10  15   4    2060.24    1950.75   -109.49  -5.314%    298   2159
 10  20   4    1572.77    1425.45   -147.32  -9.367%    322   2030
```

The b = 10 d = 4 sub-panel **dissolves a finite-panel artifact**:
the 6-cell panel in `EXTENDED-PANEL-RESULT.md` showed n = 10 at
97.6 % match while n = 2..6 sat above 99 %. With n filled in across
{2..20}, n = 10 sits smoothly between n = 9 (98.2 %) and n = 11
(97.4 %). No d = 4 anomaly. (The `SPIKE-HUNT.md` claim of 79 %
match for n = 10 at d = 3 is a separate finding for a different
d-block and is not addressed here.)


## Decimal-digit base-invariance check

For fixed `n`, the gap in **decimal** digits across bases:

| b  | n=2 gap (dec) | n=3 gap (dec) | n=5 gap (dec) |
|---:|---:|---:|---:|
| 3  | −10.07 | −15.51 | −29.04 |
| 4  | −7.85  | −16.02 | −26.27 |
| 6  | −8.28  | −15.91 | −32.93 |
| 8  | −8.59  | −16.69 | −26.66 |
| 10 | −10.10 | −16    | −32    |
| 12 | −9.46  | −18.79 | −29.32 |

`gap_decimal` is roughly base-invariant for each `n`:
- n = 2: ~−9 ± 1 across bases
- n = 3: ~−16 ± 2
- n = 5: ~−29 ± 4

This says the sub-leading correction is `O(1)` in `b` (in
decimal-digit terms) with all of the `b`-dependence carried by the
leading-order `(b − 2)/(b − 1)` factor. The closed form's b-shape is
correct; what's left is a per-`n` `O(1)`-decimal-digit edge-effect
that doesn't track `b`.


## What this confirms vs. doesn't

**Confirms.**

1. The closed-form prefactor `(b − 2)/(b − 1)` is the correct base
   shape. A naive guess `(b − 1)/b` would fit b = 10 within 1 % at
   k = 4 and would be hard to distinguish from `(b − 2)/(b − 1)` at
   that single base; the cross-base panel separates them sharply.
   Empirical asymptotic ratio `gap / D_k → (b − 2)/(b − 1)` is now
   constrained at six bases.

2. The closed form is structural, not a b = 10 numerical fit. The
   formula

       S_k(n, b) = (n − 1)/n² · (b^{k−1} · (k(b − 2) + b/(b − 1)) − 1/(b − 1))

   is empirically sharp at all six tested bases.

3. The b = 10 d = 4 n-monotone curve is smooth across the full
   tested range `n ∈ {2..20}`. The "n = 10 outlier" reading from
   the original 6-cell panel was an artifact.

**Does not address.**

- The off-spike denominator process (`L_{k-1}` structure;
  `δ_k(n) = (n − 1) k + offset(n)` decomposition from
  `OFFSPIKE-RESULT.md`). The cross-base panel only checks the
  leading-order prediction, not the per-base structure of `offset`.
  Whether the Family A / B classification of `offset(n)` reproduces
  across `b` is open. (In particular, the `ord(b, n)` map shifts
  with `b`, so per-`b` family compositions differ; the
  `EXTENDED-PANEL-RESULT.md` framing is b-specific.)

- The d-axis. Each base in this panel was tested at one `d` only,
  chosen so the predicted spike was tractable. d-scaling at fixed
  base is the subject of `D5-RESULT.md`.

- The off-spike denominator is the load-bearing open piece flagged
  by `MECHANISTIC-DERIVATION.md` step 3. Cross-base data does not
  illuminate it.


## Files

- `../../../experiments/acm-flow/cf/cf_spikes_extended.py`
  — panel runner.
- `../../../experiments/acm-flow/cf/cf_extended.csv` —
  per-cell data.
- `../../../experiments/acm-flow/cf/cf_extended_summary.txt`
  — same data, table form.

(Compute artifacts live under `cf/` because the run was set up there;
they could be migrated to cf/ in a future cleanup. The
analysis lives here in cf/ where the closed form's home is.)


## Provenance

The closed form is from `MEGA-SPIKE.md` lines 41–49. The b = 10 d = 4
panel that this work extends across bases is `EXTENDED-PANEL-RESULT.md`.
The four-ways framing of what's substrate-transparent vs. open in
that closed form is `arguments/MEGA-SPIKE-FOUR-WAYS.md`. The
empirical work for this cross-base extension was originally done
under a parallel framing in
`experiments/acm-flow/cf/SPIKE-CLOSED-FORM-PANEL.md`
(now superseded; see status preamble there).

**This is the canonical home for the cross-base finding.**
