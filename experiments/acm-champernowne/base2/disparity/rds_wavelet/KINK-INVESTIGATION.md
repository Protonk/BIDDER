# KINK LATTICE? — n = 3 detrended RDS Morlet scalogram, [500, 2000] band

**Status:** audited down. The low-band `n = 3` gap distribution is
non-white and visibly clustered, but the stronger reading
"the gaps lie on an arithmetic lattice with click `≈ 951`" is not
currently supported. That fit is a fragile summary of one narrow KDE
choice, not a robust invariant of the committed gap sample.

What is currently solid:

- The 580 inter-notch gaps and the four KDE-detected modes at
  `(521.2, 1464.5, 2423.2, 3335.5)` reproduce exactly from the
  committed CSV and the committed script.
- The white-noise sanity check (T1) has been run on six controls under
  the *exact* same pipeline. None reproduces the n=3 morphology, so the
  strongest "this is just white under the detector" reading is not
  tenable (see §Sanity check below for the weaker artifact stories that
  remain live).

What is not solid:

- The claim that the three sharp modes form a true 3-rung **arithmetic
  lattice** with click `≈ 951` rests on a post-hoc fit to the first
  three sorted KDE modes, i.e. 2 free parameters fit to 3 smoothed
  points with 1 residual degree of freedom.
- The same committed gap CSV does **not** give a unique click period.
  At slightly narrower KDE bandwidth (`bw = 0.08`) it resolves into 7
  modes and the first three sorted modes imply `b ≈ 483`; at default
  `scott`/`silverman` bandwidths mode A disappears and there is no
  three-mode lattice to fit.
- The quoted `5.15`-bit residual should not be over-read. The mode
  locations are read from a 1200-point grid across `[154, 4789]`, so
  the grid spacing is `≈ 3.87` bits; the residual is only about
  `1.3` grid cells.
- A 300× bootstrap of the committed 580-gap sample under the same
  `bw = 0.10` rule (committed in `kink_lattice_audit.py`, default
  `--seed 20260408`) gives mode counts from `3` to `7`, click-period
  standard deviation `≈ 240` bits, fitted-`b` interquartile range
  `[477, 950]`, and only `18/300 = 6 %` of resamples with residual
  percentage `≤ 0.54 %`. The lattice tightness is therefore not a
  stable property of the underlying gap law.
- The fourth mode at `3335` does **not** extend the lattice. Its
  residual against the `n = 3` extrapolation of the fit is 36 bits,
  i.e. **3.79 % of click**, five times worse than the fit residuals
  for the first three modes. So either the lattice has exactly three
  rungs (in which case "arithmetic lattice" is generous language for
  three points on a line) or the fourth mode is a KDE artifact.
- T2, T3, T4, T7 — band scaling, shuffle control, other monoids, and
  number-theoretic alignment — are still unrun. Each of them could
  push the reading either way.

This note states the observations precisely, lays out the procedure
that produced them, exposes the numerical evidence, lists what is and
is not ruled out, and gives concrete falsification tests for the
remaining alternatives. Anyone reading this should treat the lattice
reading as one *discardable compression* of a clustered, detector-side
summary, not as an established arithmetic law. The safer current
headline is: **the low-band `n = 3` gap distribution is nonwhite,
short-range anti-persistent, and clustered in a way the white controls
do not reproduce.**

---

## Observations

For the linearly-detrended `n = 3` ACM running-digital-sum stream of
length `1,000,000` bits, the band-`[500, 2000]` Morlet notch indicator
yields **580 inter-notch gaps** `Δt_k`. KDE on those gaps with
`bw_method = 0.10` finds **three sharp modes** at

```
Δt  ≈  521,  1464,  2423  bits
```

plus a **marginal fourth bump** at `Δt ≈ 3335` containing only 9 of the
580 gaps (`1.6 %` of the sample, relative density `0.067` against the
peak mode).

Four features of this gap distribution are unusual once compared
side-by-side with white-noise controls run through the *exact same
pipeline* (see §Sanity check: white-noise pipeline below). These four
features are the actual evidence; the lattice reading is one
interpretation of them.

1. **The smallest mode at `≈ 521` bits is well below anything any
   control produces.** Across six controls (four random walks, two
   Gaussian iid streams, all length 1M, identical band, identical KDE
   bandwidth) the smallest detected mode was `641, 817, 977, 757, 681,
   658` — i.e. nothing below `≈ 640`. The n=3 mode A sits more than
   100 bits below the lowest control mode.
2. **The gap distribution is nearly symmetric.** `skew = +0.228`,
   `excess kurt = −0.057`. The six controls give `skew ∈ [+0.66,
   +1.12]` and `kurt ∈ [+0.42, +2.10]` — they are right-skewed and
   heavier-tailed, the natural shape for a Poisson-process-like point
   pattern. The n=3 gap distribution does not look Poisson.
3. **Lag-1 autocorrelation of `Δt_k` is `−0.213`.** All six controls
   sit in `[−0.027, +0.097]`. The n=3 value is roughly five control
   standard deviations away from white. This is a *short-range only*
   anomaly — DFA on the cumulative gap profile gives `H_global =
   0.510`, indistinguishable from white at long ranges — but the lag-1
   anti-persistence itself is genuinely non-white.
4. **Under the narrow KDE setting `bw_method = 0.10`, the gap
   distribution resolves into three dominant low-order clusters near
   `521`, `1464`, and `2423` bits, plus a weak bump near `3335`.**
   That clustered picture is real as a statement about this chosen
   smoothing level. What is *not* yet earned is the stronger claim
   that those three cluster centres instantiate a discrete arithmetic
   law.

The old lattice reading took those three KDE centres and proposed:

> *the three sharp modes are samples from a 3-rung arithmetic
> lattice with click `b ≈ 951` bits and offset `a ≈ 519` bits.*

The problem is not just that this is a 2-parameter fit to 3 points.
The deeper problem is that the fitted points are themselves not stable
under ordinary smoothing choices: at `bw = 0.08` the same gap sample
shows seven modes and a very different first-three click, while at
default `scott`/`silverman` bandwidths mode A disappears entirely.
So the "lattice" is best read as one way to compress the
`bw = 0.10` picture, not as the present best description of the gap
law.

The four observations above are the headline. The arithmetic fit in
§Numerical evidence is now included as a **diagnostic stress test**:
if a real lattice were present it should survive modest bandwidth
changes, resampling, and detector swaps. At present it does not.

---

## Why this might be extraordinary (conditional)

The conditional in the heading matters: the items below describe what
*would* be surprising **if** the lattice reading survives further
tests. Right now what is solid is the four observations in the
preceding section, not the lattice interpretation.

1. The `n = 3` ACM stream is built by concatenating the binary
   expansions of consecutive primes `p ≡ 1 (mod 3)`. There is no
   periodicity in this construction.
2. The RDS is linearly detrended only. The per-entry bit-balance
   closed form from `../../HAMMING-BOOKKEEPING.md` is *available* but
   not subtracted here, since the linear detrend is sufficient to
   centre the wavelet input. (For `n = 3` the per-entry contribution
   is constant — `slope(0, d) = 1` — so the per-entry detrender would
   coincide with a linear one anyway.)
3. The Morlet wavelet at scale `s` (with `w₀ = 6`) is a smooth
   Gaussian-windowed sinusoidal kernel with Fourier period `T(s) =
   2π · s / w₀ ≈ s · 1.047`. Its scalogram is a smooth function of
   `(s, t)`. There is no construction step that would obviously inject
   a discrete arithmetic spacing into the local-maxima of the
   band-averaged log power — but as §Sanity check below shows, the
   pipeline does inject *something* (controls give 4–6 KDE modes with
   varying spacings), so "no obvious mechanism" is not the same as
   "no mechanism at all."
4. Conditional on the lattice reading: the three dominant modes are
   within `±5.2` bits of a 2-parameter arithmetic progression, i.e.
   `≤ 0.54 %` of the click period. The white-noise controls show that
   this tightness is not generic — only one of six controls gets
   within `2 %` — but neither is it astronomical.
5. The branches are still informative no matter how the tests come
   out:
   - If the same lattice appears in **other monoids** with the same
     `(b, a) ≈ (951, 519)`, the effect is wavelet- or detector-induced
     — and surprising in a different way, because then the wavelet
     does encode that specific click.
   - If it appears in other monoids with *different* `(b, a)` that
     depend on the monoid, the effect is a property of ACM dynamics.
   - If it disappears under entry shuffling, it is order-dependent
     and joins Walsh + detrended-RDS as a third order-sensitive
     observable.
   - If the click `b ≈ 951` scales with `√(s_lo · s_hi)` across
     bands, the lattice is a wavelet/scale property with a clean
     closed form.
   Each of these is a different finding, and each is a reason to run
   the corresponding test.

---

## Setup

| Component | Value |
|---|---|
| Monoid | `n = 3` |
| Stream length | `TARGET_BITS = 1,000,000` (actual: `999,989` bits, `58,763` entries) |
| Stream construction | `acm_n_primes(3, count)` from `core/acm_core.py`, primes concatenated as binary, truncated at the largest entry boundary `≤ TARGET_BITS` |
| Detrend | linear fit subtraction on the cumulative `(2·b − 1)` RDS |
| Wavelet | Morlet, `w₀ = 6.0`, manual implementation via `scipy.signal.fftconvolve` (split into real and imaginary parts) |
| Scales | `120` log-spaced in `[2, 50000]` (geomspace) |
| Kink band | `[KINK_BAND_LO, KINK_BAND_HI] = [500, 2000]` |
| Band rows kept | `17` of `120` |
| Notch indicator | `I(t) = mean_s [ −log₁₀ |W(s, t)|² ]` over band rows, then centred and uniformly smoothed with window `NOTCH_SMOOTH = 20` |
| Peak detection | `scipy.signal.find_peaks(I, prominence=0.02, distance=10)` |
| Edge trim | drop peaks within `EDGE_PAD = 1000` bits of either end of the stream |
| Fit cutoff | `T_FIT_MIN = 3000` (only peaks at `t ≥ 3000` enter the fits) |

After this pipeline: `K = 581` notches, earliest at `t = 3457`,
latest at `t = 995458`.

The implementation lives in
[`kink_decompression_n3.py`](kink_decompression_n3.py). The exact
command that produced the claim run is in the **Reproduction**
section below.

---

## Numerical evidence

### Distinctive features (the things controls do not reproduce)

These are the four numbers from §Observations, restated as a
control-vs-signal table. The control panel and pipeline are documented
in §Sanity check: white-noise pipeline below; the n=3 row is from
`kink_gaps_lowband_1M_kde2.csv`. All seven runs go through the same
script with identical parameters.

| feature | n = 3 | RW seeds 1–4 | Gauss seeds 1–2 | distinctive? |
|---|---:|---|---|---|
| smallest KDE mode | **521** | 641, 817, 977, 757 | 681, 658 | yes — n=3 sits ≥120 below all 6 |
| skewness         | **+0.228** | +0.84, +0.90, +0.80, +1.03 | +0.66, +1.12 | yes — n=3 is near-symmetric, controls are right-skewed |
| excess kurtosis  | **−0.057** | +0.56, +1.56, +0.80, +1.85 | +0.42, +2.10 | yes — n=3 is light-tailed, controls are heavy-tailed |
| lag-1 ACF of Δt  | **−0.213** | +0.10, −0.03, +0.05, −0.02 | +0.09, +0.05 | yes — `~5σ` from control distribution |
| post-hoc fit max-residual / b at `bw=0.10` | **0.54 %** | 27.3, 4.07, 11.5, 40.3 | 9.07, 1.64 | yes, but only as a secondary diagnostic |
| KDE rejects Gaussian (D, p) | 0.087, 3·10⁻⁴ | 0.080/0.059/0.066/0.075, all p ≤ 0.02 | 0.057, 0.072 | **no — all controls also reject Gaussian** |

The last row is the important footnote: the KS rejection of Gaussian
by itself is *not* a distinctive feature of the n=3 stream, because
white-noise gap distributions under this pipeline are also non-Gaussian.
The KS test cannot do work in this note. The first four rows do the
main work; the post-hoc fit row is useful only as a stress test on the
`bw = 0.10` rendering, not as an independent finding.

### Marginal distribution of `Δt_k`

580 gaps. Summary statistics:

| quantity | value |
|---|---|
| count `K − 1` | 580 |
| mean | 1,710.3 bits |
| std | 832.9 bits |
| CV | 0.487 |
| skewness | +0.228 |
| excess kurtosis | −0.057 |
| lag-1 autocorrelation | −0.213 |

For completeness, the goodness-of-fit numbers against smooth
distributions (Kolmogorov–Smirnov, parameters fitted from the data):

| reference distribution | KS statistic `D` | KS p-value |
|---|---:|---:|
| `Normal(μ = 1710, σ = 833)` | 0.0872 | 2.74 × 10⁻⁴ |
| `LogNormal(μ_log = 7.280, σ_log = 0.645)` | 0.1468 | 2.23 × 10⁻¹¹ |

Both are rejected — but as the last row of the distinctive-features
table notes, the same is true for white-noise controls under the same
pipeline. KS rejection of Gaussian is therefore necessary but not
sufficient evidence of a structural anomaly. `scipy.kstest` with
fitted parameters is conservative (Lilliefors is the strictly correct
test), so the actual p-values are smaller than reported, but this
makes the rejection *stronger* in both cases — it does not change the
fact that controls also reject.

### KDE-detected modes

Gaussian KDE with bandwidth factor `bw_method = 0.10` (≈ 10 % of the
sample std, much narrower than the default `'scott'` rule, which
gives `bw ≈ 0.28` here and over-smooths narrow clusters). Local
maxima of the resulting density, prominence threshold ≥ 3 % of max:

| Mode | `Δt` (bits) | Relative density | # gaps within ±231 |
|---:|---:|---:|---:|
| A | **521** | 0.451 | 74 |
| B | **1,464** | 1.000 | 155 |
| C | **2,423** | 0.859 | 152 |
| D | 3,335 | 0.067 | 9 |

Modes A, B, C account for `74 + 155 + 152 = 381` gaps, i.e. **65.7 %**
of the 580-gap sample, in non-overlapping windows of half-width `231`
(`= 5 % of (max − min)`, the script's automatic local-window heuristic;
not a tuned parameter).

**Mode A is bandwidth-fragile.** At `bw_method = 'scott' (≈ 0.28)`
only modes B and C survive — mode A gets smoothed away entirely. The
bw=0.10 choice was made *because* it shows mode A; the doc is up
front about that. What rescues this from being pure researcher
degree-of-freedom is the §Sanity check result: with the same bw=0.10,
none of the six white-noise controls produces any mode below 640. So
bw=0.10 is not manufacturing mode A out of nothing — but mode A's
existence does require a non-default bandwidth.

**Modes B and C are bandwidth-robust.** They survive all of `bw ∈
{0.07, 0.10, 0.15, 'scott'}`.

### Post-hoc arithmetic fit (diagnostic only)

If one insists on fitting the first three sorted KDE modes at the
committed `bw = 0.10`, OLS on `Δt(n) = a + n · b` for `n ∈ {0, 1, 2}`
gives

```
a  =  518.67  bits   (offset)
b  =  950.97  bits   (click period)
```

This fit is now produced directly by `kink_decompression_n3.py` —
search for "Lattice fit" in the run log. The fit has 2 parameters,
3 points, and 1 residual degree of freedom. Per-mode residuals:

| `n` | predicted `a + n·b` | observed | residual | as % of `b` |
|---:|---:|---:|---:|---:|
| 0   | 518.67 | 521.24 | +2.58 | +0.27 % |
| 1   | 1469.63 | 1464.48 | −5.15 | −0.54 % |
| 2   | 2420.60 | 2423.18 | +2.58 | +0.27 % |
| 3 (extrap) | 3371.57 | 3335.49 | **−36.08** | **−3.79 %** |

Two cautions matter more than the fitted `(a, b)` themselves:

1. **This is a fit to smoothed mode centres, not to the raw 580 gaps.**
   The fit quality therefore inherits every KDE choice upstream of it.
2. **The quoted residual is near the numerical resolution of the mode
   finder.** `mode_locations` are read from a 1200-point grid over
   `[154, 4789]`, so one grid step is `≈ 3.87` bits. The advertised
   `5.15`-bit max residual is only about `1.3` grid cells.

The more serious problem is **bandwidth instability** on the same
committed gap CSV. Holding the prominence rule fixed and varying only
the KDE bandwidth gives the table below. All numbers in this and the
bootstrap block are produced by `kink_lattice_audit.py
kink_gaps_lowband_1M_kde2.csv` (default `--seed 20260408 --n-boot 300`).

| KDE `bw_method` | mode count | first three sorted modes | implied `b` | max \|r\| / b | reading |
|---|---:|---|---:|---:|---|
| `0.07` | 9 | `285, 498, 1008` | `361` | `27.45 %` | mode finder fragments the lower half completely |
| `0.08` | 7 | `510, 1001, 1476` | `483` | `1.07 %` | first three modes are *neighbours* in the lower half |
| `0.09` | 4 | `514, 1468, 2400` | `943` | `0.82 %` | near the committed picture |
| `0.10` | 4 | `521, 1464, 2423` | `951` | `0.54 %` | committed run |
| `0.12` | 4 | `525, 1461, 2443` | `959` | `1.61 %` | same 4-mode regime, click drifts |
| `0.15` | 3 | `525, 1464, 2446` | `961` | `1.48 %` | extra merging, still 3-mode |
| `scott` / `silverman` | 2 | `1484, 2439` | — | — | mode A disappears; no 3-mode fit |

What this table actually says: there is no underlying lattice
parameter `b ≈ 951` that the procedure is *estimating*. Within the
narrow `bw ∈ [0.09, 0.15]` window the fit lands in the 943–961 range,
but at `bw = 0.08` the same sample's "first three sorted modes" are
the first three modes of the lower half of the distribution (because
the lower half has split into extra modes) and the implied click
collapses to `483`; at `bw = 0.07` the fragmentation is worse and the
implied click is `361`; at `scott`/`silverman` mode A vanishes
entirely and there is no three-mode fit at all. The "fitted `b`" is
therefore a parameter of one specific KDE rendering, not of the gap
law itself.

The bootstrap of that same KDE rendering points the same way. With
`bw = 0.10` held fixed and 300 resamples (with replacement) of the
committed 580-gap sample, `kink_lattice_audit.py` reports:

```
mode count distribution
   3 modes:    5
   4 modes:   96
   5 modes:  134
   6 modes:   60
   7 modes:    5
range: [3, 7]

fitted b (over 300 valid resamples)
   mean   = 718  bits
   std    = 240  bits
   median = 701  bits
   p25    = 477
   p75    = 950
   p5     = 436
   p95    = 1019

max |residual| / b
   median = 3.24 %
   p25    = 1.61 %
   p75    = 6.15 %

resamples with max |r|/b ≤ 0.54 %:  18/300  (6.0%)
```

Three things to read off this:

- **The fitted click is not bimodal around `951`.** It is a broad,
  single-mode distribution centred near `700` with `IQR ≈ [477, 950]`.
  The `951` from the committed run sits at the `p75` of the bootstrap,
  not at the median. The "click `≈ 951`" reading is one outcome of one
  resample, not the central tendency.
- **The mode count is unstable too.** Only `(5+96)/300 = 34 %` of
  resamples reproduce a 3- or 4-mode picture; `66 %` resolve into
  5–7 modes, in which case there is no obvious "first three sorted
  modes are the lattice rungs" interpretation.
- **The `0.54 %` tightness is not generic.** Only `18/300 = 6 %` of
  resamples reach it. Even after fixing the smoothing rule and
  conditioning on `≥ 3` modes, the lattice fit only looks tight for
  one in ~17 bootstrap draws.

**Mode D does not extend the lattice.** Its residual against the
extrapolation `a + 3·b = 3371.57` is `−36.08` bits, i.e. `3.79 %` of
click — five times worse than any of the fit residuals and on the
order of typical control-lattice residuals. Two honest readings of
this:

- *The lattice has at most three rungs.* In which case "arithmetic
  lattice" is generous language for three points that happen to fit a
  line; this is a descriptive convenience, not an earned law.
- *Mode D is a KDE artifact.* It contains 9 of 580 gaps (`1.6 %`),
  relative density `0.067`, and only barely passes the 3 %
  prominence threshold. At any meaningful significance level mode D
  is within KDE noise. This reading is more parsimonious.

The doc commits to neither but is explicit that **mode D should not be
cited as supporting evidence for the lattice**. More importantly, the
three-mode arithmetic fit itself should be cited only as a fragile
diagnostic of the `bw = 0.10` rendering, not as a robust signal-side
finding. An earlier draft used it as the main reading; that was too
strong.

### Long-range structure (DFA on the cumulative gap profile)

Detrended fluctuation analysis (linear-detrend, polynomial order 1)
on the cumulative integrated centred gap series, `Y(k) = Σ_{i ≤ k}
(Δt_i − ⟨Δt⟩)`. Window sizes: 23 log-spaced values from `N = 4` to
`N = 145` (i.e. up to `K / 4`).

| fit | exponent | RSS (log-space) |
|---|---:|---:|
| single global slope | `H = 0.5099` | 0.01184 |
| best two-regime split (break at `N ≈ 26`) | `H₁ = 0.4601`, `H₂ = 0.4813` | 0.00921 |

The two-regime fit improves RSS by only `1.29×`. Both `H₁` and `H₂`
sit within `0.04` of the white-noise reference `H = 0.5`. The slight
`H₁ < 0.5` is the lag-1 anti-persistence appearing at short windows;
by `N ≳ 26` it has faded. **There is no fractal break, no
multifractal scaling, and no long-range memory in the gap sequence.**

---

## Robustness checks already performed

1. **Detector `distance` is not the source of the small-Δt cluster.**
   The same configuration with `distance ∈ {10, 50, 100}` finds
   *exactly* the same 581 peaks (verified via `kink_gaps` CSV
   diffs and identical statistics to four decimal places). So the
   smallest gap in the data is at least 100 bits — and from the
   committed CSV, the actual minimum gap is `154` bits — and no
   detected peak is within 100 bits of another. The mode A cluster
   around `521` bits is therefore not a detection-floor artifact.
2. **Detector `prominence` does not visibly move the picture.**
   `prominence ∈ {0.02, 0.04}` give 581 vs 581 peaks (the looser
   value picks up the same peaks at this band; the difference was
   visible at `[3k, 15k]` but not here).
3. **The KS rejection of Gaussian and LogNormal is robust to
   binning.** It uses the empirical CDF, no histogram bins involved.
   But see §Distinctive features above: this rejection is not
   distinguishing, since controls also reject under the same test.
4. **The KDE bandwidth check is narrow on purpose, and only one
   side of scott.** At `bw_method ∈ {0.07, 0.10, 0.15}` the same
   three dominant modes appear (with `bw = 0.10` capturing them most
   cleanly). At `bw_method = 'scott'` (`≈ 0.28` for this sample) only
   modes B and C survive — mode A gets smoothed away. The robustness
   window `[0.07, 0.15]` is on one side of scott and was not chosen
   neutrally; it was chosen because it shows mode A. The honest
   reading is "modes B and C are bandwidth-robust; mode A requires a
   non-default bandwidth and would not be reported under standard
   scott or Silverman defaults." See §Sanity check below for why
   bw=0.10 is nevertheless not manufacturing mode A out of nothing.

---

## Sanity check: white-noise pipeline (T1 — partially run)

This is the test §Falsification tests below flags as T1:
the strongest alternative explanation in §A is that the three modes
are a wavelet/detector artifact — specifically, that the band-averaged
Morlet log-power signal in `[500, 2000]` naturally produces local-max
spacings at the wavelet's intrinsic Fourier periods, and that mode A
at `521` is suspiciously close to the lower-edge Fourier period
`T_lo = 2π · 500 / 6 ≈ 523.6`.

T1 is the test that distinguishes "the pipeline manufactures this
structure" from "the structure comes from the input." It has now been
run on six white-noise controls under the *exact* same band, smoothing,
peak detector, edge trim, t-fit cutoff, and KDE bandwidth as the n=3
production run. The committed script is
[`t1_white_noise_control.py`](t1_white_noise_control.py).

**Setup.** Six 1,000,000-sample control streams: four Bernoulli random
walks (`cumsum(±1)`, the closest white analogue to a binary RDS), and
two Gaussian iid streams (the doc's first-listed T1 option). All six
were run through `t1_white_noise_control.py` with seeds `1, 2, 3, 4`
(rw) and `1, 2` (gauss).

**Results table** (one row per run):

| source       | n_gaps | mean | std | skew  | ex-kurt | lag-1 | KS p   | smallest mode | mode count | post-hoc fit `b` | max resid / `b` |
|---           |---:    |---:  |---: |---:   |---:     |---:   |---:    |---:           |---:        |---:               |---:             |
| **n=3 ACM**  | 580    | 1710 | 833 | +0.23 | −0.06   | **−0.213** | 3·10⁻⁴ | **521** | **3 sharp + 1 weak** | **951** | **0.54 %** |
| RW seed 1    | 684    | 1451 | 733 | +0.84 | +0.56   | +0.097 | 3·10⁻⁴ | 641 | 4 | 924 | 27.31 % |
| RW seed 2    | 686    | 1446 | 727 | +0.90 | +1.56   | −0.027 | 2·10⁻² | 817 | 4 | 343 | 4.07 %  |
| RW seed 3    | 658    | 1511 | 758 | +0.80 | +0.80   | +0.048 | 7·10⁻³ | 977 | 6 | 270 | 11.53 % |
| RW seed 4    | 687    | 1447 | 735 | +1.03 | +1.85   | −0.017 | 9·10⁻⁴ | 757 | 4 | 811 | 40.26 % |
| Gauss seed 1 | 651    | 1528 | 744 | +0.66 | +0.42   | +0.092 | 3·10⁻² | 681 | 6 | 438 | 9.07 %  |
| Gauss seed 2 | 671    | 1481 | 776 | +1.12 | +2.10   | +0.052 | 2·10⁻³ | 658 | 5 | 479 | 1.64 %  |

(`max resid / b` is the lattice fit's worst residual against `n =
0, 1, 2`, divided by the fitted click — same metric as for the n=3 row.)

**What this rules out, and what it doesn't.**

What is ruled out:

1. **Mode A is not a wavelet edge artifact.** The lower band edge has
   Fourier period `T_lo ≈ 523.6` bits. Mode A in n=3 sits at `521`,
   which is what made §A worrying. But none of the six controls
   produces a mode below `641`. All six smallest modes lie at
   `1.22× T_lo` to `1.87× T_lo`. If the band edge alone were enough
   to manufacture a mode at `T_lo`, the controls would put one
   there; they do not. The numerical coincidence between `521` and
   `T_lo` therefore does not survive as an explanation.
2. **A `951`-bit click is not forced by the band edge alone.**
   The control click periods (from the same post-hoc fit on the first
   three sorted KDE modes of each control) are `924, 343, 270, 811,
   438, 479`. They scatter widely, and none lands within `±50` of
   `951`. This kills the strongest "the band manufactures exactly this
   click" story. It does **not** validate the lattice reading, because
   the controls also show that this detector naturally produces
   multi-mode KDE summaries and rough arithmetic compressions of them.
3. **The lag-1 anti-persistence is not white.** All six controls give
   `ρ₁ ∈ [−0.027, +0.097]`. The n=3 value of `−0.213` is roughly
   `5σ` from the control distribution. Whatever produces the `−0.213`
   is a property of the n=3 stream, not of the pipeline.
4. **The near-symmetric, light-tailed gap distribution is not white.**
   All six controls produce right-skewed (`+0.66 ≤ skew ≤ +1.12`),
   heavy-tailed (`+0.42 ≤ kurt ≤ +2.10`) gap distributions — the
   shape you get from a Poisson-process-like point pattern. The n=3
   gap distribution is closer to symmetric (`skew = +0.228`) and
   lighter-tailed (`kurt = −0.057`). This is a structural difference
   in shape, not a fluctuation.
5. **The KS rejection of Gaussian is not what distinguishes n=3.**
   All six controls also reject Gaussian under the same fit-then-test
   (`p ∈ [3·10⁻², 3·10⁻⁴]`). So the KS rejection of Gaussian by the
   n=3 stream is necessary but not sufficient evidence of structure.

What is **not** ruled out:

1. **The lattice fit is not robust enough to carry the note.**
   The n=3 max-residual / `b` of `0.54 %` is only one narrow reading
   of one narrow KDE rendering. It is unusually tight relative to six
   controls, but the same gap CSV changes click period under modest
   bandwidth changes and a bootstrap of the sample shows wide
   instability in both mode count and fitted `b`. This number cannot
   support a strong "real lattice" claim.
2. **The control panel is six runs.** Six is enough to disqualify
   the band-edge story for mode A; it is not enough to characterise
   the right tail of the lattice-fit-tightness distribution under
   white noise. Running 100+ controls would give a proper
   percentile, and might either harden or soften the `0.54 %`
   reading.
3. **Bernoulli random walk and Gaussian iid are the obvious null
   choices, but neither is "n=3 with structure removed."** The right
   conservative null is the *shuffled* n=3 stream (T3): same
   per-entry valuation distribution, same total prefix length, same
   detrend, but with entry order destroyed. T3 remains unrun and is
   the most decisive remaining test.
4. **T1 has only been run at the band `[500, 2000]`.** If the n=3
   lattice were a band-pass effect coupled to *any* input — including
   an input with the n=3 amplitude profile — it could re-emerge at
   different band placements. T2 (band-scaling) is the test for
   this.
5. **The wavelet aliasing alternative is not fully dead.** What
   survives of §A is the residual concern that the band edges might
   still inject a *small* amount of structure that, combined with the
   n=3 stream's own oscillatory content, lands on the observed
   clustering. T2 is the cleanest way to measure this.

**Net effect on §A.** The strongest version of the wavelet-aliasing
alternative — that mode A is a band-edge artifact and the click is
twice the band-edge Fourier period — is largely refuted by T1. A
weaker version, in which the band-pass interacts with n=3-specific
oscillations to amplify a particular spacing, remains live and is
what T2 will test.

**Reproducibility.** Each row in the table comes from one run of
`t1_white_noise_control.py --stream {rw,gauss} --seed N`. The script
prints the same diagnostic block as `kink_decompression_n3.py`
(KDE modes, lattice fit, residuals), so the two output blocks line
up row-for-row. Re-running the panel takes about 10 seconds on a
laptop because only the in-band scale rows are computed.

---

## Alternative explanations not yet ruled out

This is the section worth reading if you want to break the claim.

### A. Wavelet aliasing / scale-band artifact (partially refuted)

The Morlet wavelet at scale `s` (with `w₀ = 6`) has Fourier period
`T(s) = 2π · s / w₀ ≈ s · 1.047`. The kink band `[500, 2000]` covers
Fourier periods `[523, 2094]`. The original concern: mode A (`521`)
sits at the lower-edge Fourier period `T_lo ≈ 523.6`, mode C (`2423`)
sits past the upper edge, and the lattice click `≈ 951` is close to
`2 · T_lo ≈ 1047`. So the three observed modes could plausibly be
distributing themselves at multiples of `T_lo` regardless of the input.

§Sanity check above runs the exact pipeline on six white-noise
controls and measures what `T_lo`-centred structure the band-pass
actually injects when the input has *no* lattice. It does not inject
a mode at `T_lo`: all six controls put their smallest mode at
`641–977`, well above `523.6`. It does not inject the click `≈ 951`
either: control clicks scatter from `270` to `924` and never land
within `±50` of `951`. So the strong-form aliasing reading — "mode A
is the lower-edge Fourier period leaking through" — is dead.

What survives is a weaker version: the band edges plus the smoothing
window plus the find_peaks parameters do impose *some* characteristic
spacing on the local-max sequence (controls return 4–6 modes, not a
unimodal distribution). The question that remains is whether this
detector-side spacing, coupled to the n=3 stream's specific
oscillatory content, conspires to produce the `(521, 1464, 2423)`
clusters in particular. T2 (band-scaling) is the right measurement to
settle this. What it should now track is **cluster stability**, not a
presumed lattice parameter.

### B. Stream finite-size effect

580 gaps from 1M bits is a moderate sample. The mode *positions*
could shift with longer streams, the lag-1 ACF could regress toward
zero, and the lattice fit could turn out to be an artifact of where
this particular 1M-bit window happened to fall in the longer ACM
sequence. T5 (longer stream) is the test for this — but note that
the n=3 stream is deterministic, so "shift with longer streams" here
means "shift as the prefix length grows," not "vary across samples."
The right way to read T5 is as a stationarity check, not a sample-size
check.

### C. Single-segment coincidence

The `n = 3` stream is deterministic. We have one 1M-bit prefix.
Splitting it into segments and refitting the lattice on each would
detect any segment-dependence.

### D. Post-hoc lattice fitting

Three modes always admit *some* `(a, b)` lattice fit, since two
parameters trivially fit two of three points and leave 1 dof for the
third. The honest question is how tight the residual is *for this
particular data* compared to what white noise produces under the same
fit. §Sanity check has the empirical answer: across six white-noise
controls,

```
max |residual| / b   ∈   { 1.64 %, 4.07 %, 9.07 %, 11.53 %, 27.31 %, 40.26 % }
                                                                  median ≈ 10 %
```

The n=3 fit reaches `0.54 %`, which is `~3×` better than the best of
six controls and `~20×` better than the median. That is meaningfully
tight, but not overwhelming. An earlier draft of this note hand-waved
at a "100× better than chance" figure based on a uniform-random null
in `[521, 2423]`; that estimate was per-pair, ignored the joint
constraint of the lattice, did not match the empirical control
distribution, and has been removed.

But the main weakness is now clearer than mere multiplicity:

- **The fitted points are not invariant.** The note does not fit a
  lattice to the raw 580 gaps; it fits one to the first three sorted
  KDE modes after a chosen smoothing level. At `bw = 0.08` the same
  sample resolves into seven modes and the first three imply
  `b ≈ 483`; at `scott`/`silverman` mode A disappears and no three-mode
  lattice exists to fit. So `b ≈ 951` is not an underlying parameter
  waiting to be estimated more accurately; it is one description of one
  rendering.
- **The tightness is not stable under resampling.** A 300× bootstrap
  of the committed gap sample under the same `bw = 0.10` rule
  (`kink_lattice_audit.py`, default seed `20260408`) produces mode
  counts from `3` to `7`, click-period standard deviation `≈ 240`
  bits, and only `6 %` of resamples with residual percentage
  `≤ 0.54 %`. The fitted-`b` distribution is broad and centred near
  `700`, not bimodal around `951`. So even after fixing the smoothing
  rule, the fitted lattice is not a stable statistic of the sample.
  See §Numerical evidence for the full bootstrap output.

Two further multiplicity issues remain relevant:

- **Choice of which modes count as dominant.** With six controls
  giving 4–6 modes apiece and with no rule on the books for which
  ones to lattice-fit, the doc is implicitly choosing the first three
  in sorted order. The same convention applied to controls gives the
  table above, which is at least a fair comparison.
- **Choice of band.** The kink band `[500, 2000]` is not the script
  default (`[3000, 15000]`). It was selected after inspection, and
  the doc does not currently disclose how many other `(lo, hi)` pairs
  were tried before it. This is what T2 will measure honestly.

The claim "the `bw = 0.10` rendering contains three centres that are
nearly collinear in `n`" is supported. The stronger claim
"the gaps live on an arithmetic lattice with click `≈ 951`" is not.

### E. Detector regularity

`scipy.signal.find_peaks` with `(prominence, distance) = (0.02, 10)`
plus a uniform smoothing of width `20` may impose its own quasi-
regular spacing on the output. The `distance ∈ {10, 50, 100}` check
in §Robustness rules out the most obvious version of this, but a
different detector (e.g. wavelet-modulus-maxima from
`scipy.signal.find_peaks_cwt`, or thresholding the second derivative)
should give the same modes if they are real.

---

## Falsification tests

These are ordered by how decisively each one would either kill the
claim or convert it from "interesting empirical observation" to
"likely property of the n = 3 stream." T1 has been run (in
abbreviated 6-control form, see §Sanity check above); T2–T7 are still
unrun.

### T1. White-noise sanity check — **partially run, see §Sanity check above**

Run the *exact same pipeline* — Morlet CWT, scale band `[500, 2000]`,
notch indicator, peak detector, gap diagnostics — on a synthetic
1M-sample i.i.d. `Normal(0, 1)` series, and on a synthetic random
walk built by `cumsum` of `±1` Bernoulli draws (the closest white
analogue to a detrended RDS). Look at the gap distribution.

**Status.** Six controls (4 random walks, 2 Gaussian iid, all length
1M) have been run via [`t1_white_noise_control.py`](t1_white_noise_control.py).
The strong-form aliasing reading is dead: no control reproduces mode
A, the post-hoc click near `951`, the lag-1 anti-persistence, or the
near-symmetric gap shape. See §Sanity check above for the table and
the surviving weaker concerns. What still remains for a *committed*
T1 is:

- a larger control panel (100+ seeds) so that the right tail of the
  white-noise lattice-tightness distribution can be characterised,
  not just bracketed by 6 samples;
- the same panel rerun under the same `--target-bits 3000000` as T5,
  so finite-size and stationarity questions can be addressed
  jointly.

### T2. Band-scaling check

Run the same pipeline on bands `[200, 800]`, `[300, 1200]`, `[800,
3200]`, `[1500, 6000]` of the same `n = 3` stream. Track the same gap
diagnostics and, only secondarily, any implied arithmetic fit.

**Predicted outcomes:**
- If the whole clustered picture moves with the geometric mean of the
  band (`√(s_lo · s_hi)`), the structure is wavelet/scale driven.
- If the same low-order clusters recur at roughly the same `Δt` values
  across bands, the clustering is signal-side.
- If the cluster picture itself is unstable band-to-band, the current
  low-band rendering is not carrying a transportable claim.

### T3. Shuffled-entry control

Same pipeline on the `n = 3` stream with its entry sequence permuted
under `SEED = 12345` (the convention from `../detrended_rds.py`).

**Predicted outcomes:**
- If the clustered gap picture survives the shuffle, the structure
  depends only on the *value distribution* of `n = 3` entries, not
  their order.
- If the clustering collapses, the effect is order-dependent and joins
  Walsh + detrended-RDS as another "ordering matters" observable.

### T4. Other monoids

Same pipeline on `n ∈ {2, 5, 7, 8}` at the same `[500, 2000]` band.

**Predicted outcomes:**
- If each monoid yields a comparably clustered low-band gap law, the
  effect may be a generic ACM feature.
- If only `n = 3` shows the clustering, it is monoid-specific.
- If no other monoid shows it, the `n = 3` case needs even more
  scrutiny.

### T5. Longer stream

Same pipeline on `n_bits = 3 × 10⁶` (same band, same parameters).

**Predicted outcomes:**
- Clusters at roughly the same `(521, 1464, 2423)` with more support
  → the nonwhite gap picture hardens.
- Strong drift in those clusters as `K` grows → finite-size artifact.

### T6. Detector swap

Re-extract notches with a different peak detector — say,
local-minima of `+log₁₀|W|²` per scale row (no band averaging),
or zero-crossings of the band-averaged second derivative. Re-run
the gap diagnostics.

**Predicted outcomes:**
- Same lattice → not a detector artifact.
- Different lattice or unimodal → possibly a `find_peaks`-specific
  effect.

### T7. Number-theoretic alignment

Compute the positions of arithmetic events in the `n = 3` entry
sequence: where consecutive entries cross `2^k` boundaries; where
the bit-length-class `d` increments; the cumulative-bit positions
of every entry whose `v₂` exceeds some threshold. Overlay these on
the notch positions and look for alignment.

**Predicted outcomes:**
- The notch positions sit at a subset of these arithmetic events →
  the lattice has a closed-form arithmetic origin and the click
  period `950` and offset `521` should be derivable.
- No alignment → the lattice is dynamical, not arithmetic, and we
  need a different explanation.

---

## Reproduction

All the numbers in §Numerical evidence except DFA come from one
command:

```bash
sage -python experiments/acm-champernowne/base2/disparity/rds_wavelet/kink_decompression_n3.py \
    --target-bits 1000000 \
    --kink-lo 500 \
    --kink-hi 2000 \
    --smooth 20 \
    --distance 10 \
    --prominence 0.02 \
    --edge-pad 1000 \
    --suffix _lowband_1M_kde2
```

This produces:
- `kink_decompression_n3_lowband_1M_kde2.png` — 4-panel summary.
- `kink_spacing_diagnostic_n3_lowband_1M_kde2.png` — peak positions
  and gap/ratio sequences.
- `kink_gap_diagnostic_n3_lowband_1M_kde2.png` — gap histogram with
  KDE overlay (mode markers visible).
- `kink_gaps_lowband_1M_kde2.csv` — all 580 gaps as
  `gap_index,delta_t`.

It also prints, near the end of the run log, the KS-test statistics,
the four KDE mode locations, and a `Lattice fit Δt = a + n·b` block
that gives `(a, b)`, the max residual over `n = 0, 1, 2`, and the
per-mode residuals for the first four modes (with the fourth mode
labelled as an extrapolation, not a fit). The lattice block was added
to the script as part of this audit so the lattice numbers cited in
§Numerical evidence are produced by the same command that produces
the modes — they are no longer hand-computed from the printed mode
positions.

The DFA result comes from:

```bash
sage -python experiments/acm-champernowne/base2/disparity/rds_wavelet/dfa_kink_n3.py \
    experiments/acm-champernowne/base2/disparity/rds_wavelet/kink_gaps_lowband_1M_kde2.csv \
    _lowband_1M
```

producing `dfa_kink_n3_lowband_1M.png` and printing `H_global =
0.5099`.

The white-noise controls in §Sanity check come from
[`t1_white_noise_control.py`](t1_white_noise_control.py), one
invocation per row:

```bash
sage -python experiments/acm-champernowne/base2/disparity/rds_wavelet/t1_white_noise_control.py \
    --stream rw    --seed 1
sage -python experiments/acm-champernowne/base2/disparity/rds_wavelet/t1_white_noise_control.py \
    --stream rw    --seed 2
sage -python experiments/acm-champernowne/base2/disparity/rds_wavelet/t1_white_noise_control.py \
    --stream rw    --seed 3
sage -python experiments/acm-champernowne/base2/disparity/rds_wavelet/t1_white_noise_control.py \
    --stream rw    --seed 4
sage -python experiments/acm-champernowne/base2/disparity/rds_wavelet/t1_white_noise_control.py \
    --stream gauss --seed 1
sage -python experiments/acm-champernowne/base2/disparity/rds_wavelet/t1_white_noise_control.py \
    --stream gauss --seed 2
```

Each prints the same diagnostic block as `kink_decompression_n3.py`
(KDE modes + lattice fit + per-mode residuals) so the rows of the
control table can be read off directly. Pass `--save-csv` to dump the
control gap sequence as `kink_gaps_t1_<stream>_seed<k>.csv` for
offline reanalysis.

The robustness checks at `distance = 50` and `distance = 100` use
`--distance 50 --suffix _lowband_1M_d50` and `--distance 100 --suffix
_lowband_1M_d100` respectively. They produce the same 581-peak set as
`distance = 10` (verified by CSV diff).

The bandwidth sweep table and the bootstrap stats in §Numerical
evidence (and the bootstrap one-liner in §D) are produced by:

```bash
sage -python experiments/acm-champernowne/base2/disparity/rds_wavelet/kink_lattice_audit.py \
    experiments/acm-champernowne/base2/disparity/rds_wavelet/kink_gaps_lowband_1M_kde2.csv
```

The script's defaults (`--n-boot 300 --seed 20260408 --threshold-pct
0.54`) are what the doc cites. Change `--seed` to test stability of
the bootstrap under reseeding; change `--n-boot` to widen the
distribution; change `--threshold-pct` to ask "what fraction of
resamples beat *this* tightness." Pass `--save-csv` to dump a
per-resample CSV (`kink_lattice_audit_bootstrap.csv`) for offline
reanalysis.

The first thing the script prints is the KDE grid step
(`(max − min) / 1199 ≈ 3.87` bits at the committed sample), so the
relationship between any cited mode-position residual and the grid
resolution is visible at the top of the audit log.

---

## What this note does not claim

- It does not claim the arithmetic-lattice reading is currently the
  best interpretation. After audit, the safer reading is:
  clustered nonwhite gaps with short-range anti-persistence under this
  low-band detector.
- It does not claim the `n = 3` stream is aperiodic or non-stationary
  in any deep sense. The DFA result is the *opposite* of long-range
  fractal aperiodicity: the gap sequence is essentially white at long
  ranges.
- It does not claim that the observed clustering is fully
  signal-intrinsic. T1 has been run on six controls and the strong
  wavelet-aliasing reading is dead, but a weaker interaction between
  band choice and n=3-specific content remains live until T2
  (band scaling) runs.
- It does not claim the three sharp KDE modes definitively form an
  arithmetic lattice. The fit residual `0.54 %` of click belongs to
  one narrow KDE rendering of the sample. The same committed gap CSV
  yields a different first-three click at `bw = 0.08` and no three-mode
  fit at `scott`/`silverman`. The lattice is one compression of the
  `bw = 0.10` picture, not a robust observable.
- It does not claim that mode D extends the lattice. Mode D is
  either a true fourth rung that the lattice fit fails to predict by
  `3.79 %` of click, or a KDE noise bump containing 9 of 580 gaps.
  Either way, mode D should not be cited as supporting evidence.
- It does not claim the lattice is unique to `n = 3`. T4 has not
  been run.
- It does not claim the click period or offset have closed-form
  origins. T7 has not been run, and no candidate derivation of
  `b ≈ 951` or `a ≈ 519` from the n=3 prime sequence is on the
  table.
- It does not claim that mode A would be reported under standard KDE
  bandwidth defaults. Mode A requires `bw_method = 0.10`, which is
  ~`1/3` of the scott rule. The §Sanity check result rescues this from
  the strongest "pure white-noise artifact" reading, but the bandwidth
  dependence is real and should be carried by anyone citing mode A.
- It does not claim anything about other bands. The `[3k, 15k]`
  diagnostics from earlier runs were never re-analysed under the
  same KDE-mode-detection, so we do not know whether that band
  also shows a similar clustered gap law. T2 is the right test.
- It does not claim that the band `[500, 2000]` was selected
  neutrally. It was chosen by inspection after the `[3k, 15k]`
  band's geometric reading was abandoned. The doc does not currently
  disclose the search history; T2 is also the cleanest way to
  retroactively measure how much that selection mattered.

---

## See also

- [`KINK_DECOMPRESSION.md`](KINK_DECOMPRESSION.md) — the broader
  measurement programme this finding emerged from. The observations
  here **complement** the "anti-persistent Gaussian-around-affine"
  reading in that doc's "stronger reading" rather than supersede it
  (an earlier draft of this note used "supersedes," which was
  premature given that T2/T3/T4/T7 are still unrun).
- [`kink_decompression_n3.py`](kink_decompression_n3.py) — the
  measurement script. Now also produces the lattice fit and per-mode
  residuals as part of its run log; see §Reproduction.
- [`t1_white_noise_control.py`](t1_white_noise_control.py) — the T1
  white-noise control script. Six-row panel reproduces the
  §Sanity check table.
- [`kink_lattice_audit.py`](kink_lattice_audit.py) — the bandwidth
  sweep + 300× bootstrap audit of the post-hoc lattice fit.
  Reproduces the bandwidth-instability table in §Numerical evidence
  and the bootstrap stats in §1 (Status) and §D from one command
  on the committed gap CSV.
- [`dfa_kink_n3.py`](dfa_kink_n3.py) — the DFA standalone script.
- [`kink_gap_diagnostic_n3_lowband_1M_kde2.png`](kink_gap_diagnostic_n3_lowband_1M_kde2.png)
  — the figure that shows the three sharp KDE modes most clearly.
- [`dfa_kink_n3_lowband_1M.png`](dfa_kink_n3_lowband_1M.png) — the
  DFA result, showing `H ≈ 0.5`.
- [`kink_gaps_lowband_1M_kde2.csv`](kink_gaps_lowband_1M_kde2.csv) —
  the raw gap data, 580 rows, for any independent re-analysis.
- [`../DETRENDED_RDS.md`](../DETRENDED_RDS.md) — the parent
  experiment from which the `n = 3` Morlet scalogram comes.
- [`rds_wavelet_n3.py`](rds_wavelet_n3.py) — the wavelet
  decomposition that established the dominant scale at `~27,559`
  bits and the Brownian background.
