# Closed-form panel — empirical results

## ⚠️ STATUS UPDATE — superseded by the mega-spike thread

This was Phase 1 of `BRIEF2-CLOSED-FORM.md`'s closed-form program —
see that document's status preamble for the full reframe. The panel
here mixes two different contributions:

1. **A b = 10 d = 4 sub-panel** filling in `n ∈ {7, 8, 9, 11, 12, 13,
   15, 20}` — extending `cf/EXTENDED-PANEL-RESULT.md`'s
   six-cell panel. Genuinely useful for dissolving the "n = 10
   outlier" reading at d = 4 (now seen as a finite-panel artifact),
   but doesn't add structural insight beyond what
   `EXTENDED-PANEL-RESULT.md` already classifies.

2. **A cross-base panel** at `b ∈ {3, 4, 6, 8, 12}` testing the
   `(b − 2)/(b − 1)` prefactor structure of the closed form. This
   was b = 10 only in the existing mega-spike thread; the cross-base
   data is genuine new validation.

The cross-base finding is the cleanest piece of brief 2's empirical
work. It has been promoted to `cf/CROSS-BASE-RESULT.md`,
which is the canonical home. The b = 10 sub-panel data is included
there too.

**What's preserved here.** The compute artifacts
(`cf_spikes_extended.py`, `cf_extended.csv`,
`cf_extended_summary.txt`) remain in this folder; they're the run
output and are referenced from the new mega-spike doc by relative
path.

For the current state, read `cf/CROSS-BASE-RESULT.md`.

---

Phase 1 of `BRIEF2-CLOSED-FORM.md`. Extended `(b, n, d)` panel for the
predicted spike formula

    spike_baseb_digits(n, d, b)  ≈  (n − 1)/n² · F(d, b)
    F(d, b)  =  d (b − 2) b^(d−1) + (b^d − 1) / (b − 1).

Two extension axes, run as `cf_spikes_extended.py` against
`cf_extended_summary.txt` and `cf_extended.csv`.

The panel confirms the leading-order prediction across 23 cells, maps
the sub-leading drift, and dissolves a finite-panel artifact in the
original `SPIKE-HUNT.md` analysis.


## Headlines

1. **Leading-order closed form confirmed across six bases.** All 23
   cells match prediction to within 0.05 % – 9.4 % in base-`b` digits.
   The base-b axis sweep `b ∈ {3, 4, 6, 8, 10, 12}` fixes the
   asymptotic ratio `(b − 2)/(b − 1)` as the right structure; the
   prediction is not a base-10 coincidence.

2. **The "n = 10 outlier" reading from the original 6-cell panel
   dissolves.** With n filled in across `{2..20}` at `(b, d) = (10, 4)`,
   n = 10's gap fits a smooth monotone curve between n = 9 and n = 11.
   The trailing-zero specialness of n = 10 may operate at d = 3 (per
   `SPIKE-HUNT.md`) but does not show up at d = 4.

3. **Sub-leading drift is monotone in `n` at fixed `(b, d)` and roughly
   base-invariant in decimal digits at fixed `n`.** The empirical drift
   shape is consistent with an `O(n)` per-monoid edge correction at the
   d-to-d+1 transition; this is exactly the candidate sub-leading term
   that a careful Mahler-style argument would extract.

4. **For FINITE-RANK-EXPANSION:** the leading-order prediction is rank-1
   atom density (`(n−1)/n²`) times a base-`b` positional skeleton
   (`F(d, b)`), with **no higher-rank Q_n quantities entering**. The
   sub-leading drift is also monotone with no apparent rank-h structure
   — at this resolution, the cf boundary spike at d = 4 looks like a
   purely height-1 phenomenon. Same outcome shape as Phase 4 (B′) on
   the multiplication table: bare counts factor through density ×
   universal projection.


## Panel

The full 23-cell table (smoke test passes; predicted spike size is
computed from the closed form; observed spike found by the cumulative-
digit identity `2 log_b q_{i−1} + log_b a_i ≈ C_d(n)`):

```
  b   n   d   pred_b-d    obs_b-d       gap     gap%      i  valid
------------------------------------------------------------------------
 10   7   4    4054.41    4006.74    -47.67  -1.176%    218   3161
 10   8   4    3621.52    3564.85    -56.66  -1.565%    208   3073
 10   9   4    3270.22    3209.86    -60.36  -1.846%    200   2923
 10  11   4    2736.45    2665.21    -71.24  -2.603%    258   2526
 10  12   4    2529.31    2438.76    -90.55  -3.580%    260   2383
 10  13   4    2351.08    2257.07    -94.01  -3.998%    288   2368
 10  15   4    2060.24    1950.75   -109.49  -5.314%    298   2159
 10  20   4    1572.77    1425.45   -147.32  -9.367%    322   2030
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


## Axis 1 — n-monotone drift at b = 10, d = 4

Combining the existing 6 cells of `cf_spikes.py` with the 8 new cells
in this panel, the full picture at `(b, d) = (10, 4)`:

| n | gap (b-d) | gap % | smooth? |
|---:|---:|---:|:--|
| 2  | −10  | −0.122 % | ✓ (4 \| 1000) |
| 3  | −16  | −0.220 % |  |
| 4  | −21  | −0.343 % |  |
| 5  | −32  | −0.604 % | ✓ (25 \| 1000) |
| 6  | −38  | −0.827 % |  |
| 7  | −48  | −1.176 % |  |
| 8  | −57  | −1.565 % |  |
| 9  | −60  | −1.846 % |  |
| 10 | −72  | −2.420 % | ✓ (100 \| 1000) |
| 11 | −71  | −2.603 % |  |
| 12 | −91  | −3.580 % |  |
| 13 | −94  | −3.998 % |  |
| 15 | −109 | −5.314 % |  |
| 20 | −147 | −9.367 % |  |

Two structural readings.

**The n = 10 anomaly is not real (at d = 4).** The original 6-cell
table showed n = 10 at 97.6 % match with n = 2..6 all above 99 %. The
extended table shows n = 10 sitting smoothly between n = 9 (98.2 %) and
n = 11 (97.4 %). The "trailing-zero specialness" reading in
`SPIKE-HUNT.md` was a 6-cell artifact at d = 4. (The 79 % match at
d = 3 reported in that doc may be genuine; this panel does not address
d = 3.)

**Smooth and non-smooth n sit on the same curve.** Smooth at
`(b, d) = (10, 4)` requires `n² | 10³ = 1000`, satisfied only by
`n ∈ {2, 5, 10}`. Their gap percents (−0.122, −0.604, −2.420) sit on
the same monotone curve as the non-smooth `n` values around them. So
the spread-bound correction (block-count drifting from the smooth
formula by ≤ 2 per leading-digit strip) is **not** the dominant source
of sub-leading drift. Whatever drives the curve operates uniformly in
smoothness.

**Drift shape.** `gap` (in base-b digits) grows roughly linearly in n.
Empirically `|gap| / n` ranges from 5.0 (n=2) to 7.5 (n=20), with mild
super-linearity. A pure-linear fit `gap ≈ −c·n` with `c ≈ 7.5` is
within ~50 % across the panel; a `gap ≈ −c·n + d·log n` fit is closer
but still not crisp. The signature is **`O(n)` correction with a
slowly-growing residual**.


## Axis 2 — base-b sweep

Predicted asymptotic ratio `gap / D_d → (b − 2)/(b − 1)` from the
closed form. Direct check via the per-base panel for n = 2 (smooth
or spread-bounded):

| b  | d  | pred (b-d)  | obs (b-d)   | gap (b-d) | gap (decimal) | gap % |
|---:|---:|---:|---:|---:|---:|---:|
| 3  | 8  | 5194.00     | 5172.89     | −21.11    | −10.07        | −0.406 % |
| 4  | 6  | 3413.25     | 3400.21     | −13.04    | −7.85         | −0.382 % |
| 6  | 5  | 6868.75     | 6858.10     | −10.65    | −8.28         | −0.155 % |
| 8  | 4  | 3218.25     | 3208.73     | −9.52     | −8.59         | −0.296 % |
| 10 | 4  | 8277.75     | 8267.65     | −10.10    | −10.10        | −0.122 % |
| 12 | 4  | 17751.25    | 17742.48    | −8.77     | −9.46         | −0.049 % |

(Last column is gap × log₁₀(b), giving gap in decimal digits.)

**Decimal-digit gap is base-invariant for n = 2.** Across `b` from 3 to
12 — at `d`-values chosen so the spike is comfortably above the noise
floor — the gap is consistently `−7.8 to −10.1` decimal digits.
Consistent enough to read as an `O(1)` decimal-digit edge-effect, base-
invariant, with the leading-order `(b − 2)/(b − 1)` ratio carrying all
of the b-dependence.

**Same picture at n = 3 and n = 5.**

| b  | d  | n=3 gap (decimal) | n=5 gap (decimal) |
|---:|---:|---:|---:|
| 3  | 8  | −15.5             | −29.0             |
| 4  | 6  | −16.0             | −26.3             |
| 6  | 5  | −15.9             | −32.9             |
| 8  | 4  | −16.7             | −26.7             |
| 10 | 4  | −16               | −32               |
| 12 | 4  | −18.8             | −29.3             |

n = 3 gap-decimal-digits is ~16 across all bases; n = 5 is ~28 ± 4
across all bases. The base-invariance of the decimal-digit gap holds
fact-by-`n`. Combined with the `n`-monotone read on Axis 1, the
sub-leading correction is:

  `O(n)` in `n`,  `O(1)` in `b` (decimal digits),  no `d`-dependence
  apparent in the panel.

This is the signature of an edge-effect at the d-to-d+1 transition —
specifically, the position of the first n-prime in the (d+1)-block
relative to the natural-extension prediction from the d-block. That
position depends on `n` (via the AP residue offset at `b^d mod n²`)
and is `O(1)` in absolute base-`b` digit terms.


## What this confirms

**Leading-order closed form.** The predicted formula
`(n − 1)/n² · F(d, b)` is correct as the leading-order spike magnitude
across all six bases tested, three values of n in each base, and 14
values of n at b = 10. The `(b − 2)/(b − 1)` asymptotic prefactor is
the right structural element; the naive `(b − 1)/b = 9/10` reading
that one might have guessed (if one weren't paying attention to
cumulative-vs-block bookkeeping) is excluded.

**Drift is monotone and structured.** The sub-leading correction is
not noise; it has a clean `O(n) × O(1)_decimal` shape that is the
expected form of an edge-effect at the d-block boundary. This is
exactly the kind of correction a careful Mahler-style argument should
extract (steps (P3) and (P4) of `BRIEF2-CLOSED-FORM.md`).

**FINITE-RANK-EXPANSION cf-projection: rank-1 only.** The leading
order factors as

  `spike(n, d, b) ≈ atom-density(n) × positional-skeleton(b, d)`
                = `(n − 1)/n²       × F(d, b)`

with no Q_n / Λ_n / divisor-stack quantities entering at any visible
order. The empirical drift is also monotone in `n` with no rank-h
signature.

The cf boundary-spike observable is thus a height-1 projection: it
sees the count of atoms in a digit class and the positional skeleton
of base `b`, but not the divisor-multiplication algebra of `M_n`.

This is the same outcome shape as Phase 4 (B′) of the multiplication-
table thread: a "global counting" observable factors through density ×
a universal anatomy, with rank-h structure showing up only in
conditional / cell-resolved / weighted projections, not bare counts.

**Not refuted but not supported either:** the FINITE-RANK-EXPANSION
speculation is consistent with this finding — global cf-counting
projections wouldn't be expected to expose Q_n directly. Other cf
projections might (off-boundary partial-quotient distributions, cf
partial-quotient cumulants conditioned on residue class, etc.); this
panel doesn't address those.


## What this does not yet establish

1. **The closed form at d = 5 and beyond.** The whole panel is at
   `d ∈ {4, 5, 6, 8}`. Without a confirmation that the same prediction
   tracks `(b, n, d) = (10, n, 5)`, the formula could in principle be
   a coincidence at the d-values tested. The d = 5 push (compute B in
   the brief) is the natural next step to rule this out.

2. **The Mahler-style proof itself.** The closed form is empirically
   confirmed but algebraic identity ≠ proof. Steps (P1) – (P4) of
   `BRIEF2-CLOSED-FORM.md` remain the obligation for a `Theorem (closed
   form)` statement.

3. **A closed form for the sub-leading drift.** The `O(n) × O(1)_decimal`
   shape is empirical; the brief's reach goal would derive it as an
   explicit function of `(b, n, b^d mod n²)` from the AP-and-edge
   structure. Not done in this pass.

4. **Off-boundary partial-quotient distribution.** An irrationality-
   measure claim needs control on `a_i` for `i` away from the d-class
   boundaries, not just the boundary spike sizes. This panel only
   touches the boundary spikes.


## Concrete next steps

In order of cost:

**(a) d = 5 push at `b = 10`** — single overnight run with
`PREC_BITS_LO ≈ 800 000`. Predicted spike magnitudes:
`F(5, 10) · (n − 1)/n²` ≈ `102 778 · (n − 1)/n²` decimal digits, so
`~25 700` decimal digits at `n = 2`. Confirms the closed form's
d-scaling (the d-axis hasn't been swept).

**(b) Wider-`n` sweep on lower bases** — fill in `n ∈ {7, 11, 13}`
at `(b, d) = (8, 4)` and `(b, d) = (12, 4)`. Cost is small (`b = 8`
panel cells take a few seconds, `b = 12` cells take ~20 seconds at
the precision floor of 80 000 bits). Tests whether the `O(n) ×
O(1)_decimal` drift extends to lower bases the same way.

**(c) Mahler argument writeup (paper, not compute)** — the brief's
(P1) – (P4) carried out explicitly for the AP-sieved case. This is
where the empirical drift shape gets explained as `n · (b^d mod n²)`-
arithmetic plus boundary cancellations.

(a) and (c) are the two paths to firming up the leading-order
finding. (b) is a robustness check that would fit an afternoon.


## Files

- [cf_spikes_extended.py](cf_spikes_extended.py) — panel runner.
- [cf_extended.csv](cf_extended.csv) — all 23 panel cells.
- [cf_extended_summary.txt](cf_extended_summary.txt) — same data,
  human-readable.
- [cf_extended_run.log](cf_extended_run.log) — per-cell run details
  (precision, validated prefix, timings).


## Coupling

This panel is the empirical complement to `BRIEF2-CLOSED-FORM.md`.
The brief states the closed form and the proof obligation; this doc
provides the data the proof has to match. It does not replace the
proof.

The panel does not address briefs 1 (Copeland-Erdős literature search)
or 3 (Erdős-Borwein E). Coupling to brief 4 is the parallel observation
about rank-1 / rank-h projection structure across observables: same
outcome shape — leading order is density × universal projection, with
rank-h structure absent from bare global counts.
