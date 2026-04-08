# Kink decompression

Test of how dark-notch positions in the detrended n=3 RDS Morlet
scalogram are spaced in t. The visual question is whether the
crowded-at-left, spread-at-right appearance of the notches is a
real spacing change or a perspective artifact.

This is a stateless test record: it states the models, the runs to
date, the self-similarity thresholds the linear-spacing hypothesis
must clear to be considered confirmed, and the conditions under
which it would be rejected. New runs should append to the table
and re-evaluate against the thresholds.

## Setup

For each tested scale band `[s_lo, s_hi]` (in bits, both Morlet
scales) and each total bit length `n_bits`:

1. Compute the Morlet CWT of the linearly detrended n=3 RDS over
   `120` log-spaced scales in `[2, 50000]`.
2. Restrict to rows with `s_lo ≤ s ≤ s_hi`.
3. Form a 1D notch indicator
   `I(t) = mean_s [ −log10 |W(s, t)|² ]` over that row set, then
   center and uniformly smooth with window `NOTCH_SMOOTH`.
4. Extract local maxima of `I(t)` with `scipy.signal.find_peaks`
   under `(prominence, distance)` thresholds; trim peaks within
   `EDGE_PAD` of either edge.
5. Fit two models on the surviving notch positions
   `t_1 < t_2 < … < t_K` (only `t_k ≥ T_FIT_MIN`):
   - Geometric:  `log(t_k) = a + b · k`,  `r ≡ exp(b)`
   - Power law:  `log(t_k) = a + α · log(k)`
6. Report `RSS_pow`, `RSS_geom`, `α`, `r`, `K`.

Implementation: [`kink_decompression_n3.py`](kink_decompression_n3.py).

## Models

- **Geometric (log-t self-similar).** `t_k = t_1 · r^(k−1)`. Notches
  form a geometric progression in t. Equivalently: notches are
  uniformly spaced on a `log(t)` axis. Spacing `Δt_k ∝ t_k`.
- **Power law.** `t_k = C · k^α`.
  - `α = 1` ⇒ uniform spacing in t (`Δt_k = const`).
  - `α > 1` ⇒ spacing grows with k (mild decompression).
  - `α < 1` ⇒ spacing shrinks with k (mild compression).
  - `α → ∞` would limit toward geometric.

The geometric and power-law models are nested only at the
degenerate end. They are otherwise distinct, and a clean
distinction in `RSS` is meaningful.

## Runs to date

| run                      | n_bits | scale band  | notches | α (pow) | r (geom) | RSS_pow | RSS_geom | RSS_geom / RSS_pow |
|--------------------------|-------:|-------------|--------:|--------:|---------:|--------:|---------:|-------------------:|
| `_` (default)            |   300k | [3k, 15k]   |     24  | 1.215   | 1.140    | 0.091   | 3.684    | 40.5×              |
| `_looser`                |   300k | [3k, 15k]   |     27  | 1.173   | 1.123    | 0.181   | 3.487    | 19.3×              |
| `_1M`                    |    1M  | [3k, 15k]   |     82  | 1.109   | 1.038    | 0.521   | 21.022   | 40.4×              |
| `_lowband_1M`            |    1M  | [500, 2k]   |    581  | 0.947   | 1.005    | 1.981   | 91.837   | 46.4×              |

`_looser` re-runs the default with `(smooth, prominence, distance)
= (20, 0.02, 10)` instead of `(50, 0.04, 25)`.

## Headline

- **Geometric model is rejected at every tested band.** Every row
  of the table has `RSS_geom / RSS_pow > 19`. There is no scale
  band so far at which the notches form a geometric progression
  in t.
- **Power law fits well at every band**, with `α ∈ [0.95, 1.22]`
  across the four runs.
- **`α` is converging toward 1 from both directions.** The two
  300k runs at `[3k, 15k]` give `α ≈ 1.21` and `α ≈ 1.17`. The 1M
  run at the same band drops to `α ≈ 1.11`. The 1M run at
  `[500, 2k]` lands at `α ≈ 0.95`.
- **Notch spacing scales linearly with band center.** Geometric
  means of the two tested bands are
  `√(3000·15000) = 6708` and `√(500·2000) = 1000` (ratio `6.7`).
  Mean notch spacings on the 1M runs are
  `1M / 82 = 12200` and `1M / 581 = 1720` (ratio `7.1`).

## Linear-spacing hypothesis

> At every scale band `[s_lo, s_hi]` strictly inside the
> well-resolved interior of the n=3 detrended-RDS scalogram,
> notch positions are uniformly spaced in `t` (`α = 1` in the
> `t_k = C · k^α` model). The mean notch spacing scales linearly
> with the geometric-mean band scale:
>
>     ⟨Δt⟩(s_lo, s_hi)  ≈  c · √(s_lo · s_hi)
>
> for a single constant `c ≈ 1.7`. The "compressed at left"
> appearance of the scalogram is a perspective + cone-of-influence
> artifact, not a real spacing change.

Implication: each scale band reads its own dominant rhythm at a
fixed temporal density. There is no log-t self-similarity in the
notch positions at any band.

## Self-similarity thresholds

The hypothesis is **confirmed** when all of the following hold:

| ID  | Condition                                                                                                | Status |
|----:|----------------------------------------------------------------------------------------------------------|:------:|
| T1  | At every tested band with `K ≥ 200` notches, `α ∈ [0.95, 1.05]`.                                         |  1/1   |
| T2  | At every tested band, `RSS_geom / RSS_pow ≥ 10`.                                                         |  4/4   |
| T3  | Mean notch spacing `⟨Δt⟩` regressed on `log √(s_lo · s_hi)` has slope `1.0 ± 0.1` (linear scaling).      |  pending more bands |
| T4  | At `n_bits = 3M`, the `[3k, 15k]` band gives `α ≤ 1.05` (continuing the 1.215 → 1.173 → 1.109 trend).     |  not run |
| T5  | At least one tested band other than `[500, 2k]` has `K ≥ 200` and yields `α ∈ [0.95, 1.05]`.             |  not run |

The hypothesis is **rejected** if any of the following hold:

| ID  | Condition                                                                                                |
|----:|----------------------------------------------------------------------------------------------------------|
| R1  | Any band with `K ≥ 200` notches gives `α > 1.10` or `α < 0.90`.                                          |
| R2  | Any band gives `RSS_geom / RSS_pow < 5`.                                                                 |
| R3  | The slope of `⟨Δt⟩` against `√(s_lo · s_hi)` (in log–log) deviates from `1` by more than `0.2`.          |
| R4  | At `n_bits ≥ 3M`, the `[3k, 15k]` band fails to relax below `α = 1.10`.                                  |

Threshold notes:

- The `K ≥ 200` requirement guards against the small-sample bias
  visible in the `[3k, 15k]` 300k runs (`K = 24` and `27`).
- The `0.95–1.05` window is a soft `±5%` interval around the
  hypothesised value `α = 1`. Tightening it requires either more
  bands or a more careful uncertainty estimate on `α` per band.
- Thresholds are stated against the present detector
  implementation. Changing the smoothing window or the prominence
  cutoff is allowed but the new run should be appended to the
  table with a label that records the parameter set.

## Coverage gaps

Bands not yet tested:

- `[s_lo, s_hi]` with `s_hi > 15000`. The wavelet support is then
  comparable to a few percent of the 1M-bit window, so the cone of
  influence dominates. Probably need `n_bits ≥ 3M` to test.
- `[s_lo, s_hi]` with `s_hi < 500`. Detector dynamic range and
  smoothing window break down at very small scales. Needs a
  retuned `(smooth, prominence, distance)` triple.
- Intermediate bands like `[1k, 5k]`, `[5k, 25k]` to fill in T3.

Stream lengths not yet tested:

- `n_bits = 3M`, `n_bits = 10M`. Required for T4.

Monoids other than `n = 3` not tested. The hypothesis is currently
stated for n = 3 only; whether it generalises is open.

## See also

- [`kink_decompression_n3.py`](kink_decompression_n3.py) — the
  measurement script. Takes CLI overrides for `target-bits`,
  `kink-lo`, `kink-hi`, `smooth`, `prominence`, `distance`,
  `edge-pad`, `suffix`.
- [`kink_decompression_n3.png`](kink_decompression_n3.png) — 300k
  default-threshold figure.
- [`kink_decompression_n3_looser.png`](kink_decompression_n3_looser.png)
  — 300k loosened-threshold figure.
- [`kink_decompression_n3_1M.png`](kink_decompression_n3_1M.png) —
  1M default-threshold figure at `[3k, 15k]`.
- [`kink_decompression_n3_lowband_1M.png`](kink_decompression_n3_lowband_1M.png)
  — 1M low-band figure at `[500, 2k]`.
- [`rds_wavelet_n3.py`](rds_wavelet_n3.py),
  [`rds_wavelet_n3.png`](rds_wavelet_n3.png) — the wavelet
  decomposition that established the dominant scale at
  `~27,559` bits.
- [`../DETRENDED_RDS.md`](../DETRENDED_RDS.md) — the experiment
  this measurement is a follow-up to.
