# Erdős–Borwein, Brief #3 — first cut

`EXPERIMENTAL.md` brief #3 asks whether a Champernowne-style encoding
of `d(n)` produces a real whose continued fraction reflects the
divisor structure. The BIDDER-shaped specialisation is: *do CF spike
loci track superior highly composite numbers (SHCN), the way
ACM-Champernowne CF spikes track radix-block boundaries via
`T_k − 2 L_{k−1}` (`MEGA-SPIKE.md`)?*

This folder runs the first cut at `N = 10⁴`. The answer is
**no, at this resolution.** CF structure is real but encoding-driven;
sequential divisor correlations are statistically invisible.


## Construction

For a sequence `s = (s_1, s_2, …, s_N)` of non-negative integers and
a base `B` ≥ max `s_n + 1`, define

    R(s, B) := Σ_{n=1}^N s_n · B^{−n}    ∈ [0, 1).

Three encodings used:

- `R_d w=16`  : fixed-width 16-bit binary chunks, `B = 2^16`.
- `R_d w=8`   : fixed-width 8-bit binary chunks, `B = 2^8`.
- `R_d^65`    : one base-65 digit per `d(n)` (max d(n) = 64 in
                this range, so no padding, no separator).

For each, the corresponding `^shuf` randomly permutes the `s_n`
values. This destroys any sequential / multiplicative correlation
in `d(n)` while preserving the marginal value distribution.


## Predictions, restated

1. **Substrate transparency reaches divisor encoding.** Spike loci
   concentrate at SHCN-mapped CF indices. Spike sizes scale with
   d(m)-jump magnitude. *Methodological win — `MEGA-SPIKE`-style
   substrate machinery generalises to arithmetic-function-encoded
   reals.*

2. **Encoding does the work.** Spike density tracks `w` or
   value-distribution skew, independent of sequential structure.
   *Methodological null — the encoding has no number-theoretic
   content beyond the marginal d(n) distribution.*

3. **Khinchin-typical.** No structure of any kind. Brief #3 returns
   empty.


## Result: prediction (3)

### Erratum: Khinchin formula

The original write-up of this experiment compared spike counts to
`P(a = 2^T)` (the Gauss–Kuzmin probability *mass* at a single
value, scaling 1/k²) instead of the survival
`P(a > 2^T − 1) = log₂(1 + 1/2^T)` (scaling 1/k). The two differ
by a factor of `~2^T`, and the original "wildly non-Khinchin" claim
(200× over Khinchin at T = 8, ∞× at T ≥ 12) is an artifact of that
formula error. The correct comparison is below.

### Spike density (35K CF steps, base-65 padding-free)

CF length for `R_d^65` was 35,185 steps. Khinchin survival counts
at threshold T are `35185 · log₂(1 + 1/2^T)`.

| T  | R_d^65 | shuffle mean ± sd (n=32) | Khinchin (correct) | obs / Khinchin | z vs Khinchin |
|----|--------|--------------------------|--------------------|----------------|---------------|
| 4  | 3114   | 3088.9 ± 42.4            | 3077.4             | 1.012          |  +0.69        |
| 6  | 767    | 786.2 ± 26.1             | 787.0              | 0.975          |  −0.72        |
| 8  | 204    | 198.1 ± 18.8             | 197.9              | 1.031          |  +0.43        |
| 10 | 57     |  50.8 ± 6.9              |  49.6              | 1.150          |  +1.06        |
| 12 | 16     |  13.5 ± 3.8              |  12.4              | 1.291          |  +1.03        |
| 14 | 6      |   3.3 ± 1.5              |   3.1              | 1.937          |  +1.65        |
| 16 | 1      |   0.8 ± 0.9              |   0.8              | 1.291          |  +0.26        |

`R_d^65` is **statistically indistinguishable from Gauss–Kuzmin**
at every threshold (every `|z| < 1.7`). The shuffle distribution
also matches Khinchin (both are within Poisson noise of the
Gauss–Kuzmin survival).

So the marginal CF distribution of `R_d^65` is Khinchin-typical.
There is no encoding artifact, no skew effect, no detectable
deviation. The original write-up's claim of "wildly non-Khinchin
spike density" was wrong.

### Spike loci

In the original `R_d w=16` plot, no visible concentration of spikes
at SHCN-mapped CF indices. Top-25 spikes have `|Δ bits|` to nearest
SHCN of hundreds to thousands of bits. In `R_d^65`, top-10 spike
loci match no recognisable substrate structure either, and shuffling
moves them to entirely different positions. Still null on
prediction (1) — divisor-correlational structure is invisible in
the CF spike loci.

### Encoding controls

Fixed-width w = 8 and w = 16 encodings give similar spike densities
to the base-65 padding-free version, all consistent with Khinchin.
The leading-zero artifact hypothesis from the original write-up
was also wrong — there is no artifact to explain because there is
no excess density to explain.


## Verdict (revised)

- **Prediction (1) fails.** SHCN-tracking is not present at
  `N = 10⁴`. Divisor-correlational structure is invisible in the
  CF spike loci.
- **Prediction (2) does NOT hold** (against the original write-up).
  There is no excess CF spike density to attribute to "encoding
  doing the work" — the encoding does no work, and neither does
  the divisor function.
- **Prediction (3) holds.** The CF of the divisor-encoded real is
  Khinchin-typical, indistinguishable from a generic real's CF at
  this sample size. The brief #3 "probably nothing" outcome is
  achieved in its purest form.

Methodological note: this is the brief's "probably nothing" signal
in its strongest form. The Champernowne re-encoding of `d(n)`
flattens the multiplicative correlations the divisor function
carries; what remains is a real whose CF distribution is
indistinguishable from a Gauss–Kuzmin reference. The substrate
transparency catalogued in `experiments/math/hardy/SURPRISING-DEEP-KEY.md`
reaches ACM-Champernowne because the structure is in the *order* of
n-primes (their position in the digit stream); for d(n), the
structure is in the *correlations between values*, which the
encoding discards.

Open: a marginal hint at T = 14 (z = 1.65) of weak excess at the
extreme tail. Within multiple-comparison bounds across 7 thresholds
× 4 conditions tested. Pushing to `N = 10⁵` or `N = 10⁶` would
either confirm a sub-leading contribution or wash it out.


## Erratum trail

The original write-up of this experiment claimed `R_d` was "wildly
non-Khinchin (~17× at T = 4, ~200× at T = 8)" and concluded that
the encoding overwhelms the divisor function. That comparison used
the wrong Khinchin formula (mass instead of survival). The error
was caught in audit; the recompute showed `R_d` is in fact
Khinchin-typical. The corrected verdict (above) preserves the
"divisor structure invisible to CF" finding but removes the
"encoding does the work" mechanism (because there is nothing to
explain — the CF behaviour is just generic). The `khinchin_expected`
function in `cf_spikes_controls.py` and `cf_spikes_nopad.py` was
fixed (now uses `log2(1 + 1/2^T)` survival), and the call sites
were updated to use each run's actual CF length rather than the
fixed `MAX_CF_STEPS` cap. Summary files regenerated.
`cf_spikes_shuffle_band.py` does not reference Khinchin and was
unchanged.


## Files

- `cf_spikes.py` — initial run, `R_d w=16, N=10⁴`, with SHCN overlay.
- `cf_spikes_w16_N10000.{png,csv,_summary.txt}` — output.
- `cf_spikes_controls.py` — w=16, w=8, shuffle comparison.
- `cf_spikes_controls_{hist,trace}.png`,
  `cf_spikes_controls_summary.txt` — output.
- `cf_spikes_nopad.py` — base-65 padding-free, vs shuffle.
- `cf_spikes_nopad_{trace,hist}.png`,
  `cf_spikes_nopad_summary.txt` — output.
- `cf_spikes_shuffle_band.py` — 32-shuffle band vs true `R_d^65`.
- `cf_spikes_shuffle_band.png`,
  `cf_spikes_shuffle_band_summary.txt` — output.

Total compute: under one minute on laptop, `sage -python`.
