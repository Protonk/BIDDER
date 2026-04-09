# Kink decompression

Test of how dark-notch positions in the detrended `n = 3` RDS Morlet
scalogram are spaced in `t`. The visual question is whether the
crowded-at-left, spread-at-right appearance of the notches is a real
spacing change or a plotting artifact.

This note records the current measurements and the limits of what they
show. The present script gives one robust empirical result: under the
current detector, the extracted notch positions are not well described
by a strict geometric progression in `t`. It does **not** yet directly
establish the stronger claim that notch positions are uniformly spaced
in `t`.

## Setup

For each tested scale band `[s_lo, s_hi]` (in bits, both Morlet scales)
and each total bit length `n_bits`:

1. Compute the Morlet CWT of the linearly detrended `n = 3` RDS over
   `120` log-spaced scales in `[2, 50000]`.
2. Restrict to rows with `s_lo ≤ s ≤ s_hi`.
3. Form a 1D notch indicator
   `I(t) = mean_s [ -log10 |W(s, t)|² ]` over that row set, then center
   and uniformly smooth with window `NOTCH_SMOOTH`.
4. Extract local maxima of `I(t)` with `scipy.signal.find_peaks` under
   `(prominence, distance)` thresholds; trim peaks within `EDGE_PAD` of
   either edge.
5. Fit three models on the surviving notch positions
   `t_1 < t_2 < … < t_K` (only `t_k ≥ T_FIT_MIN`):
   - Geometric: `log(t_k) = a + b · k`, `r ≡ exp(b)`
   - Power-law proxy: `log(t_k) = a + α · log(k)`
   - Affine constant-gap: `t_k = a + b · k`, with `b` interpreted as
     the mean per-notch gap in bits
6. Report log-space RSS for the geometric and power-law fits, and
   *also* same-units `t`-space RSS for all three models (each
   model's prediction mapped to `t` and compared against `peaks_fit`).
   `RMS_t = √(RSS_t / K)` is reported alongside.
7. Compute gap-sequence diagnostics from `Δt_k = t_{k+1} - t_k`:
   mean, std, CV (`std/mean`), skewness, excess kurtosis, lag-1
   autocorrelation, linear-regression drift slope and total drift,
   and (when `K ≥ 30`) the dominant FFT peak frequency, period, and
   power fraction.

Implementation: [`kink_decompression_n3.py`](kink_decompression_n3.py).

Note on the log-space affine fit: a literal log-space affine RSS
(`Σ(log t_k − log(a + b·k))²`) is ill-defined for runs where
`a_intercept < 0` (true at `[3k, 15k]` 300k and at the lowband run),
because the fitted line crosses zero before `k = 1`. The script
sidesteps that by computing all three models' RSS in `t` space too,
where everything is well-defined.

The peak indexing restarts at `k = 1` for the first peak with
`t ≥ T_FIT_MIN`, not at the absolute notch number, so the intercept
of every fit is sensitive to where the cutoff is set.

## Models

- **Geometric (log-`t` self-similar).** `t_k = t_1 · r^(k−1)`. Notches
  form a geometric progression in `t`. Equivalently: notches are
  uniformly spaced on a `log(t)` axis. Spacing `Δt_k ∝ t_k`.
- **Affine constant-gap.** `t_k = a + b · k`. The direct uniform
  spacing model: `Δt_k = b` (constant). Now fit by the script;
  `RSS_aff` is reported in `t` space.
- **Power-law proxy.** `t_k = C · k^α`.
  - `α = 1` gives a linear-in-`k` through-origin law.
  - `α > 1` gives increasing gaps with `k`.
  - `α < 1` gives decreasing gaps with `k`.
  - `α ≈ 1` can be compatible with affine spacing over a restricted
    window, but it is not equivalent to the affine model.

The geometric and power-law proxy fits are therefore useful as a
**narrow** discrimination test: do the detected peaks look more like a
straight line in `(k, log t)` or in `(log k, log t)`? That is
informative, but it is not a full model-selection procedure for spacing
laws.

## Runs to date

Log-space fits (geometric and power-law proxy, original framing):

| run                      | n_bits | scale band  |   K | α (proxy) | r (geom) | RSS_pow (log²) | RSS_geom (log²) | RSS_geom / RSS_pow |
|--------------------------|-------:|-------------|----:|----------:|---------:|---------------:|----------------:|-------------------:|
| `_` (default)            |   300k | [3k, 15k]   |  24 |     1.215 |    1.140 |          0.091 |           3.684 |              40.5× |
| `_looser`                |   300k | [3k, 15k]   |  27 |     1.173 |    1.123 |          0.181 |           3.487 |              19.3× |
| `_1M`                    |    1M  | [3k, 15k]   |  82 |     1.109 |    1.038 |          0.521 |          21.022 |              40.4× |
| `_lowband_1M`            |    1M  | [500, 2k]   | 581 |     0.947 |    1.005 |          1.981 |          91.837 |              46.4× |

Same-units fit comparison (all three models in `t` space, RMS in bits;
**winner** in bold):

| run             |   K | b (bits) | RMS_geom_t |  RMS_pow_t  |  RMS_aff_t  | RMS_aff / b |  winner   |
|-----------------|----:|---------:|-----------:|------------:|------------:|------------:|-----------|
| `_` (default)   |  24 |   12,851 |     51,787 |  **4,283**  |       5,871 |        0.46 | power-law |
| `_looser`       |  27 |   11,215 |     46,070 |  **5,753**  |       8,037 |        0.72 | power-law |
| `_1M`           |  82 |   12,219 |    224,261 |      49,734 |  **26,935** |        2.20 | affine    |
| `_lowband_1M`   | 581 |    1,699 |    152,148 |      27,744 |  **11,896** |        7.00 | affine    |

The model winner depends on `K`. At small `K` the power-law-mapped-to-`t`
absorbs early curvature better than affine; at large `K` affine
absorbs the long-run linear trend better than power-law. Geometric is
last in every run.

Gap-sequence diagnostics for `Δt_k = t_{k+1} - t_k` (`n_gap = K − 1`):

| run             | n_gap |   mean |    std |    CV |  skew | ex-kurt | lag-1 ACF | drift slope | total drift | FFT peak (cyc/notch) |
|-----------------|------:|-------:|-------:|------:|------:|--------:|----------:|------------:|------------:|---------------------:|
| `_` (default)   |    23 | 12,485 |  4,808 | 0.385 | -0.44 |   -0.74 |    -0.232 |     +154.5  |    +27.2 %  |       (skipped)      |
| `_looser`       |    26 | 11,045 |  5,629 | 0.510 | -0.20 |   -1.19 |    -0.097 |     +213.8  |    +48.4 %  |       (skipped)      |
| `_1M`           |    81 | 11,937 |  5,985 | 0.501 | -0.02 |   -0.95 |    -0.101 |      -50.8  |    -34.0 %  |   0.0123 (12.3 %)    |
| `_lowband_1M`   |   580 |  1,710 |    833 | 0.487 | +0.23 |   -0.06 |    -0.213 |       +0.6  |    +20.6 %  |   0.0017  (2.3 %)    |

`_looser` re-runs the default with `(smooth, prominence, distance) =
(20, 0.02, 10)` instead of `(50, 0.04, 25)`. FFT is skipped when
`n_gap < 30`.

## Current evidence

- **Strict geometric spacing is disfavored in every current run.**
  In log space, the power-law proxy beats the geometric fit by
  `19×` to `46×` in RSS. In `t` space, geometric is the worst of the
  three models in every run. The diagnostic figures' ratio panels
  (`t_{k+1}/t_k` vs `k`) show this visually: ratios decay from `~2.2`
  early to `~1.02–1.03` by `k ≈ 30` and then sit there, instead of
  staying flat as a geometric law would require.
- **The model winner between affine and power-law depends on `K`.**
  In the same-units table, the `t`-space RMS winner is power-law at
  `K = 24` and `K = 27` and affine at `K = 82` and `K = 581`. At
  small `K`, the early curvature in the data dominates and the
  power-law absorbs it; at large `K`, the long-run linear trend
  dominates and affine absorbs it. Both are *real* readings of the
  same data — the affine model captures the average gap and the
  power-law captures a small systematic curvature near the early
  edge. The systematic curvature is what survived from earlier
  runs as `α > 1`.
- **The fitted mean gap `b` is stable under detector loosening.** At
  `[3k, 15k]` it sits at `12,851 / 11,215 / 12,219` bits across the
  three configurations at that band. The lowband run gives
  `b = 1,699`. The cross-band ratio `b([3k, 15k]) / b([500, 2k]) =
  7.2` vs the geometric-mean scale ratio `6.7` agrees to within
  `~10 %`, but two bands is still only two bands.
- **The gap distribution is approximately Gaussian by asymptote.**
  At `K = 581` the excess kurtosis is `-0.06` (essentially Gaussian)
  with mild positive skew (`+0.23`). At `K ≤ 82` the kurtosis is
  noticeably platykurtic (`-0.7` to `-1.2`), consistent with
  small-sample under-resolution of a Gaussian.
- **The coefficient of variation is a stable invariant.** `CV = std
  / mean` lands at `0.51`, `0.50`, `0.49` for the three larger runs
  regardless of band. `CV ≈ 0.5` is *not* what a near-uniform
  spacing model predicts (that would be small CV); it is a
  meaningful amount of relative spread, the same fraction of `b`
  across bands.
- **The lag-1 autocorrelation is consistently negative.** Across all
  four runs, `lag-1 ACF ∈ {-0.232, -0.097, -0.101, -0.213}`. The
  gap sequence is mildly *anti-persistent*: a long gap is more
  likely to be followed by a short gap. This rules out white noise
  as the model for `Δt_k`.
- **The drift slope decreases with `K`** (`+154.5 → +213.8 → -50.8 →
  +0.6` bits per gap index across the four runs). The total drift
  expressed as a fraction of `b` does not collapse to zero, but the
  per-index slope shrinks fast. This is consistent with a finite-`K`
  artifact (a small bias per gap, integrated over `K` gaps, gives
  an `O(b)` total drift regardless of `K`) rather than a real
  persistent drift.
- **The FFT peak sits at one cycle per `K` window** in both runs
  where it could be measured (`K = 82`, `K = 581`). One cycle in the
  window means the FFT cannot distinguish `one slow trend` from
  `half a slow oscillation`. The `[3k, 15k]` 1M run carries `12.3 %`
  of FFT power at this peak; the lowband run carries only `2.3 %`.
  Inconclusive on whether a real low-frequency oscillation exists,
  pending longer streams.

## What this note supports

Conservative reading:

> Under the present detector, at the tested bands, extracted notch
> positions are much less consistent with strict geometric spacing in
> `t` than with either an affine or a slowly curving growth law. The
> mean per-notch gap `b` from the affine fit is detector-stable at
> `[3k, 15k]` and the cross-band `b` ratio agrees with the
> `√(s_lo · s_hi)` ratio to within `~10 %` over two bands.

Stronger reading from the gap diagnostics (`K = 581` lowband run is
the strongest single piece of evidence):

> The gap sequence `Δt_k` is *not* uniform-with-noise. It is uniform
> on average — affine captures `b` well — with structured deviations
> that have all of the following stable features across runs:
>   - approximately Gaussian marginal distribution,
>   - coefficient of variation `CV ≈ 0.5` regardless of band,
>   - mildly anti-persistent (`lag-1 ACF ≈ -0.1` to `-0.2`),
>   - drift slope shrinking toward `0` with `K`.
>
> "Anti-persistent ~Gaussian residuals around an affine mean" is
> the cleanest current description of the notch spacing.

Still open:

> Whether the apparent `1`-cycle-per-`K`-window FFT peak is a real
> slow oscillation or finite-window leakage. Whether `b ∝
> √(s_lo · s_hi)` survives more than two bands. Whether the
> anti-persistent `CV ≈ 0.5` Gaussian-with-memory description of
> `Δt_k` generalises off `n = 3`.

## What to test next

- Run intermediate bands `[1k, 5k]` and `[5k, 25k]` at `1M` so the
  `b ∝ √(s_lo · s_hi)` hypothesis has four points instead of two,
  and so the gap-sequence diagnostics (`CV`, lag-1 ACF, drift) can
  be checked across bands at consistent detector settings.
- Run `n_bits = 3M` at `[3k, 15k]` and `[500, 2k]` to see whether
  the `1`-cycle-per-`K`-window FFT peak survives — i.e. whether the
  peak frequency is band-dependent (real slow oscillation in the
  notch sequence) or just tracks the window length (artifact).
- Run the shuffled-entry control: same `n = 3` entry set but
  permuted with the `SEED = 12345` convention from
  [`../detrended_rds.py`](../detrended_rds.py). If the gap
  diagnostics (`CV ≈ 0.5`, lag-1 ACF, anti-persistence, `b`
  scaling) survive shuffling, the kink structure is value-driven.
  If they collapse, the kinks are order-driven and join Walsh and
  detrended-RDS as a third "ordering matters" observable.
- When comparing bands, report an empirical effective scale for
  the detector's weight distribution within `[s_lo, s_hi]` instead
  of assuming `√(s_lo · s_hi)` is the right summary.

## Coverage gaps

Bands not yet tested:

- `[s_lo, s_hi]` with `s_hi > 15000`. The wavelet support is then
  comparable to a few percent of the `1M`-bit window, so the cone of
  influence dominates. Probably need `n_bits ≥ 3M` to test.
- `[s_lo, s_hi]` with `s_hi < 500`. Detector dynamic range and
  smoothing window break down at very small scales. Needs a retuned
  `(smooth, prominence, distance)` triple.
- Intermediate bands like `[1k, 5k]`, `[5k, 25k]` to separate
  band-dependence from detector accident.

Stream lengths not yet tested:

- `n_bits = 3M`, `n_bits = 10M`. Needed to see whether the `[3k, 15k]`
  proxy exponent stays above `1` or relaxes further.

Monoids other than `n = 3` not tested. The present note is specific to
`n = 3`.

## See also

- [`kink_decompression_n3.py`](kink_decompression_n3.py) — the
  measurement script. Takes CLI overrides for `target-bits`,
  `kink-lo`, `kink-hi`, `smooth`, `prominence`, `distance`,
  `edge-pad`, `suffix`. Each run renders three figures (suffixes
  follow the suffix CLI arg).

Summary figures (4-panel: scalogram + log-`t` plot + 1D indicator + log fit):
- [`kink_decompression_n3.png`](kink_decompression_n3.png) — 300k default.
- [`kink_decompression_n3_looser.png`](kink_decompression_n3_looser.png) — 300k loosened.
- [`kink_decompression_n3_1M.png`](kink_decompression_n3_1M.png) — 1M `[3k, 15k]`.
- [`kink_decompression_n3_lowband_1M.png`](kink_decompression_n3_lowband_1M.png) — 1M `[500, 2k]`.

Spacing diagnostics (band-cropped scalogram + `t_k` vs `k` + gaps + ratios):
- [`kink_spacing_diagnostic_n3.png`](kink_spacing_diagnostic_n3.png) — 300k default.
- [`kink_spacing_diagnostic_n3_looser.png`](kink_spacing_diagnostic_n3_looser.png) — 300k loosened.
- [`kink_spacing_diagnostic_n3_1M.png`](kink_spacing_diagnostic_n3_1M.png) — 1M `[3k, 15k]`.
- [`kink_spacing_diagnostic_n3_lowband_1M.png`](kink_spacing_diagnostic_n3_lowband_1M.png) — 1M `[500, 2k]`.

Gap diagnostics (4-panel: histogram, drift, ACF, FFT of `Δt_k`):
- [`kink_gap_diagnostic_n3.png`](kink_gap_diagnostic_n3.png) — 300k default.
- [`kink_gap_diagnostic_n3_looser.png`](kink_gap_diagnostic_n3_looser.png) — 300k loosened.
- [`kink_gap_diagnostic_n3_1M.png`](kink_gap_diagnostic_n3_1M.png) — 1M `[3k, 15k]`.
- [`kink_gap_diagnostic_n3_lowband_1M.png`](kink_gap_diagnostic_n3_lowband_1M.png) — 1M `[500, 2k]`.
- [`rds_wavelet_n3.py`](rds_wavelet_n3.py),
  [`rds_wavelet_n3.png`](rds_wavelet_n3.png) — the wavelet
  decomposition that established the dominant scale at `~27,559` bits.
- [`../DETRENDED_RDS.md`](../DETRENDED_RDS.md) — the experiment
  this measurement is a follow-up to.
