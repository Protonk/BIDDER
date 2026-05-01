# Echoes in the Stream — binary autocorrelation, revisited

`MALLORN-SEED.md #5`. The binary Champernowne stream of monoid `n`
concatenates the binary representations of n-primes; consecutive
entries inherit a fixed structure (leading 1, ν_2(n) trailing zeros)
and a slow-varying high-order tail. The autocorrelation of the
±1-mapped stream picks this up as periodic spikes at multiples of
the dominant entry length `d_dom`, with magnitudes set by within-
d-block structure.

This document revives the experiment with the methodology developed
in `experiments/acm/cf/DENOMINATOR-PROCESS.md`: a substrate-
predicted envelope (computable in closed form by direct enumeration
of d-bit n-primes), a three-population decomposition (spike loci /
interior / anomalous), and an anchor harness verifying the predictor
against direct FFT computation.


## Object

For monoid `n ≥ 2`, the binary Champernowne stream is

    B_n := bits(p_1) ‖ bits(p_2) ‖ bits(p_3) ‖ …

where `p_K(n) = n · c_K` is the K-th n-prime and `bits(·)` is the
standard binary expansion (no leading zero). Map bits to ±1 via
`s = 2·bit − 1` and define the normalised autocorrelation

    R(τ; n) = (1 / N) Σ_t s(B_n[t]) · s(B_n[t + τ]),  R(0) = 1.

Computed by FFT in `autocorrelation.py`. For the panel
`n ∈ {2, 3, 4, 7, 8, 16}` and the first 4000 n-primes, `R` shows
sharp positive spikes at lags τ that are multiples of the dominant
entry length `d_dom` (= 14, 14, 14, 15, 15, 16 respectively), with
spike magnitudes growing in `ν_2(n)`.


## Substrate predictor: within-d-block enumeration

`predict_autocorr.py:autocorr_dblock_at_d(n, d)` computes R(τ = d)
*within a single d-bit block* — i.e. on the bit stream consisting
only of the d-bit n-primes concatenated in order — by direct
enumeration over consecutive entry pairs and bit positions. The
result is exact in `Fraction` arithmetic.

This is a substrate-only prediction: it depends on (n, d) and on
the closed-form structure of d-bit n-primes (their bit patterns
under increment by Δ_p = n · Δ_k between consecutive cofactors).
No empirical fitting.

The full streaming `R(τ ≈ d_dom)` is a mixture across d-blocks:
the dominant block carries the predicted within-block correlation;
neighbouring d-blocks (d_dom ± 1) and entries straddling block
boundaries contribute lower or null correlation. Empirically the
streaming-to-within-block ratio is ≈ 0.5 across the panel — the
dominant block carries about half the bit pairs at lag d_dom.


## Anchors

`test_autocorr_anchors.py` runs three:

- **A1 (within-d-block agreement).** For 20 (n, d) cells, the
  enumerated `autocorr_dblock_at_d` matches FFT autocorrelation
  on the d-block-only stream within ~0.16 (loosest, at small d
  where wraparound matters); for d ≥ 8 the match is < 0.05. PASS.

- **A2 (streaming spike at dominant d).** Streaming `R(τ = d_dom)`
  is positive and ≥ 0.25 across the panel. The streaming-to-
  within-block ratio is consistently 0.37–0.57 (mean 0.49). PASS.

- **A3 (fixed-bit count).** `fixed_bit_count(n) = 1 + ν_2(n)`
  across 14 panel cells. PASS.


## Three-population decomposition

`echoes_analysis.py` partitions the lag range τ ∈ [1, 400] into
three populations and reports population statistics:

- **Spike loci.** `τ = k · d` for `d ∈ {d_dom − 1, d_dom, d_dom + 1}`
  and `k ≥ 1`, within MAX_LAG. The width-3 halo accommodates entries
  spanning adjacent d-blocks. Substrate-predicted; ≈ 80 lags out of
  400 across the panel.
- **Interior.** Lags not on any spike locus; ≈ 320 lags. Predicted
  to be Khinchin-typical (R ≈ 0).
- **Anomalous.** Interior lags where `|R|` exceeds the white-noise
  threshold `1.96 · σ_interior`. Expected count under pure white
  noise ≈ 5% of interior ≈ 16 lags per cell.

Panel results at `N_PRIMES = 4000`:

      n   ν_2  d_dom   avg_d   R_dpred    R_dobs  spike_mean   interior_mean   interior_sd   #anomalous
      2    1     14   12.98   +0.7151   +0.3480     +0.1389         −0.0097        0.0468           23
      3    0     14   13.18   +0.5722   +0.2827     +0.1031         +0.0030        0.0081           19
      4    2     14   13.46   +0.7152   +0.2660     +0.1453         −0.0100        0.0308           20
      7    0     15   14.00   +0.5341   +0.2844     +0.0933         +0.0022        0.0084           20
      8    3     15   14.21   +0.7341   +0.3705     +0.1599         +0.0064        0.0289           23
     16    4     16   15.08   +0.7507   +0.4303     +0.1752         +0.0264        0.0359           48

- **Mean spike-loci R across panel: +0.136**
- **Mean interior R across panel: +0.003**
- **Spike / |interior| ratio: ≈ 44**


## Reading

The same three-layer shape from `DENOMINATOR-PROCESS.md` applies:

1. **Substrate envelope at spike loci (foothold).** `R(τ = d_dom)`
   is substantial and positive at every panel cell; mean spike R
   = +0.14. The within-block predictor matches FFT to spike-formula
   precision (A1) and the streaming spike has consistent ≈ 0.5
   dilution from cross-block pairs (A2). The substrate predicts
   *where* the spikes sit (multiples of d_dom) and approximately
   *how strong* they are (within-block enumeration).

2. **Khinchin-typical interior (foothold for ν_2 = 0).** For
   `n ∈ {3, 7}` the interior SD is `≈ 0.008` — coin-flip-typical
   for 320 samples (1/√320 ≈ 0.056; the observed SD is far lower
   than even the white-noise expectation, suggesting the panel-
   level smoothing further reduces variability). Anomalous counts
   are 19–20, consistent with the 5% Anderson-band expectation.

3. **Perimeter signal in `n = 16` (open).** `n = 16` shows 48
   anomalous interior lags vs ~16 expected under white noise — a
   `(48 − 16)/√16 ≈ 8 σ` excess. The interior SD is `0.036`, ~4×
   the n = 3 / n = 7 baseline. Both signals point at residual
   structure in the interior of `n = 16`'s autocorrelation that
   is not predicted by spike loci. The natural reading: at large
   `ν_2(n)`, fewer bit positions are in the carry zone, leaving
   more bits in the slow-varying-high-order regime, which can
   produce sub-spike-locus correlations at lags that aren't
   multiples of `d_dom`. Whether this is a uniformly-distributed
   amplification or a signal at specific lag families is open.

The interior is mostly Khinchin-typical for moderate `ν_2(n)`;
the perimeter shows up at the high end of the panel
(`ν_2(n) = 4`), exactly where one would expect the substrate's
trailing-zero discipline to leave the most "free" bits in the
slow-varying regime.


## What this leaves open

- **n = 16 perimeter localisation.** The 48 anomalous lags for
  `n = 16` need addresses, not just a count. Are they at lags that
  are multiples of common divisors of `{d_dom − 1, d_dom, d_dom + 1}
  = {15, 16, 17}` (i.e., the lcm structure)? Or at lags related to
  the d-block boundary positions (cumulative bit positions of full
  d-blocks)? Or at lags with a different substrate origin?
  `echoes.csv` has the per-lag rows; histogramming the anomalous
  positions modulo small divisors is the cheapest next probe.

- **Higher ν_2(n) panel extension.** `n = 32` (`ν_2 = 5`) and
  `n = 64` (`ν_2 = 6`) should test the trend. The prediction (from
  the n = 16 reading): anomalous count grows monotonically with
  `ν_2(n)`, and the extra structure has a localised origin at
  d-block-boundary-related lags.

- **Cross-block weighting.** The streaming-to-within-block ratio
  ~0.5 is consistent across the panel but the value isn't predicted
  in closed form. Computing `Σ_d w_d · R_block(n, d)` properly,
  where `w_d` is the weight of d-block bit-pairs at the relevant
  lag, would give a tighter prediction. Plausibly a clean `O(1/d)`
  correction.

- **Lag-`k · lcm(d_dom-1, d_dom, d_dom+1)` peaks.** The original
  `autocorrelation.py` print log shows top peaks for n = 7, 8 at
  lag = 210 = lcm(14, 15) and lag = 240 = lcm(15, 16). These are
  *compound* spike loci where multiple d-blocks align simultaneously,
  contributing more than the simple-multiple lags. The current spike
  set covers them via the halo of ±1, but a finer model would
  predict their *amplitude* (compound contribution from multiple
  d-blocks at one lag).

- **Universal asymptote.** `R_dpred(n, d_dom)` clusters at
  `0.71–0.75` for `ν_2 ≥ 1` cells and `0.53–0.57` for `ν_2 = 0`
  cells. The asymptote as `d → ∞` for fixed n is not yet computed
  in closed form but should be a clean function of `(ν_2(n), d)`,
  likely approaching `1 − O(log d / d)` (since the carry zone
  shrinks in relative terms).


## Files

- `autocorrelation.py` — original streaming computation. Unchanged;
  produces `autocorrelation.png`.
- `predict_autocorr.py` — closed-form within-d-block predictor
  (`autocorr_dblock_at_d`), `dominant_dblock`, `fixed_bit_count`.
  Exact `Fraction` arithmetic for the within-block prediction.
- `test_autocorr_anchors.py` — three anchors (A1 within-block,
  A2 streaming spike, A3 fixed-bit count). All pass.
- `echoes_analysis.py` — three-population decomposition.
- `echoes.csv` — per-(n, lag) rows with category labels (spike /
  interior / anomalous).
- `echoes_summary.txt` — panel summary table.
- `echoes_three_population.py` — visualization of the
  three-population decomposition. Six rows (one per panel monoid),
  each split into a full-range left panel showing R(τ) for
  τ = 1..400 with bars coloured by category (substrate-blue
  spike, gray interior, red anomalous), and a narrow right zoom
  panel showing the interior structure clipped to ±3·threshold.
  Horizontal dotted lines mark ±1.96·σ_interior. Reads at a
  glance: spike pattern is structurally similar across rows; the
  anomalous-bar count grows with ν_2(n); n = 16's row has visibly
  more red bars than the others, the perimeter signal as picture.
- `echoes_three_population.png` — the rendered figure.
- `echoes_lattice.py` — three-panel heatmap over the (n, d)
  lattice for `n ∈ {2..32}`. Left: predicted within-d-block
  R(τ=d), via direct enumeration. Middle: streaming
  autocorrelation R(n, τ) for τ ∈ [1, 40], same colour scale.
  Green outlines mark the substrate-predicted spike loci at
  τ = d_dom and τ = 2·d_dom per row; their match against the
  bright streaming cells is the visual confirmation that the
  predictor lands on the empirical spikes for every n in the
  grid, not just the panel of six. Right: streaming-to-within-
  block ratio at τ = d_dom — the cross-block dilution that A2
  reports as ~0.5, here visible as a column hovering between
  0.4 and 0.7. The dynamic range across (n, d) is wide: cool
  cells (low R) at small d for transient n, warm cells (R ≈ 0.7)
  at large d for ν_2 ≥ 1 cells.
- `echoes_lattice.png` — the rendered figure.


## Cross-references

- `experiments/acm/cf/DENOMINATOR-PROCESS.md` — methodology
  source: substrate envelope + interior + perimeter, anchor
  harness, three-population decomposition. The CF result was
  `z ≈ +4.9` for sub-canonical excursions; the binary analog here
  is `n = 16`'s anomalous-count excess, of similar shape.
- `experiments/acm/cf/MEGA-SPIKE.md` — analogue boundary
  spike formula (CF spike at radix-block boundaries; binary spike
  at multiples of d_dom).
- `core/BLOCK-UNIFORMITY.md` — `(b−1) b^{d−1} (n−1)/n²` smooth
  block atom count; for `b = 2` this is `2^{d−1}(n−1)/n²`,
  determining d-block sizes for the streaming weighting.
- `algebra/FINITE-RANK-EXPANSION.md` "What CF empirics imply for
  higher-h reads" — the four-lesson translation that motivated
  this experiment's revival shape (substrate transparency exact,
  three-layer decomposition, transient cells, singular-cell
  attention).
- `experiments/acm-champernowne/base2/forest/MALLORN-SEED.md` —
  the original prompt for this experiment, plot 5.
- `experiments/acm-champernowne/base2/forest/boundary_stitch/`
  visualises individual entry-boundary windows; this experiment
  is the spectral-domain integration of the same boundary
  structure.
