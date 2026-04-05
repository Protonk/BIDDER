# Experiment Audit Plan

Scope: review `experiments/` excluding `experiments/wibblywobblies/`.

This file captures the current audit of the experiment suite, what is stale, what should be rerun, and what new experiments would materially improve the project.

## Priority 0

- Fix or retire `experiments/shutter/acm_benford.py` plot 1.
  The first panel claims "exact uniformity" of the first digit of
  `acm_champernowne_array(N)`, but those values are in [1.1, 2.0),
  so `acm_first_digit_array` returns 1 for every element. The plot
  shows a single bar at digit 1, not the uniform distribution the
  title promises. The remaining four panels (multiplication
  convergence, addition rolling shutter, dual heatmap, crispness
  comparison) are correct — they extract first digits from sums and
  products, which do land on real digit boundaries.
  Options: (a) retitle panel 1 to say what it actually shows
  ("all Champernowne reals have leading digit 1"), (b) replace
  panel 1 with a histogram of leading digits of n=1..N (the actual
  uniformity the project proves), or (c) drop the panel entirely.
  Option (b) is the strongest.

- Additionally, `acm_benford.py` has a latent bug in its
  `first_digits` local function (line 43-45 of the original): it
  uses `int(10**frac)` without the `+ 1e-9` fix that was applied
  to `acm_first_digit` in acm_core.py. This means its
  multiplication and addition heatmaps have the same truncation
  errors on exact-integer mantissas that we fixed in
  `nasties/FIRST-DIGIT.md`. Fix: replace local `first_digits` with
  a call to `acm_first_digit_array` from acm_core.

- `experiments/art/contamination/contamination.py` has the same
  local `first_digits` function (line 43-48) with the same unfixed
  truncation bug. Same fix.

## Tighten Existing Experiments

- Tighten `experiments/others/other_digits.py`.
  The docstring (line 10) promises "permuted vs raw" but only
  analyzes the permuted path. The `full_digit_analysis` function
  (line 35) generates the permuted indices via `gen._permute()` but
  never computes the un-permuted (sequential) baseline alongside it.
  Add an explicit raw operating-block baseline.
  Count unseen digit pairs explicitly (the code at line 120 checks
  `n_seen` but doesn't flag shortfalls).
  Extend from pairwise to full d-tuple occupancy where tractable.

- Tighten `experiments/stratified/stratified.py`.
  Fairness issues:
  (a) BIDDER uses one key and one realization. numpy gets a
  100-trial envelope (line 130-140). Add a key ensemble for BIDDER.
  (b) "Systematic" uses n bins (line 76-81), not b-1 strata. Add a
  fixed-strata midpoint baseline matching BIDDER's alphabet size.
  (c) No Latin hypercube baseline, which is the modern comparator.
  (d) 1D only. Multi-digit extraction (already proved uniform in
  `other_digits.py`) enables 2D integration via digit pairs.

- Tighten `experiments/reseed/reseed_test.py`.
  The seam test is single-setting (base=10, dc=3, 100 periods).
  The chi-squared threshold is hand-rolled (line 117-118) using
  a normal approximation (`df + 3 * sqrt(2*df)`). This is fine
  as a smoke test but doesn't constitute strong evidence.
  Sweep base and digit class.
  Replace hand-rolled threshold with scipy.stats.chi2.sf or a
  permutation test.
  Report effect sizes, not only "seam detected: True/False."

- Tighten `experiments/art/contamination/contamination.py`.
  The docstring (lines 14-15) says addition "un-contaminates"
  multiplication. `single_mul.py` and `adds_then_muls.py` show
  this is wrong — a single multiplication leaves a permanent scar,
  and `BIDDER.md` explicitly says "multiplication is a one-way
  contaminant." The docstring should say addition *smears* the
  Benford signal but does not restore the original uniform source.

- Tighten the ACM-vs-numpy family (`rolling_shutter_heatmap.py`,
  `shutter_dual.py`, `compare_sources.py`, `interferometry.py`).
  These compare raw ACM against numpy. BIDDER is never included.
  Since the project's engineered output surface is BIDDER (not raw
  ACM), BIDDER should appear as a first-class source in at least
  one member of this family.

## Rerun Existing Experiments

- Rerun the shutter family with four sources.
  Sources: raw ACM order, order-shuffled ACM, BIDDER, numpy.
  Isolates whether rolling-shutter structure comes from marginal
  distribution, source ordering, or the keyed permutation.

- Rerun interferometry with BIDDER included.
  Key question: does BIDDER track numpy under random draws and
  diverge from raw ACM under order-sensitive views?

- Rerun source-comparison plots with a fixed ablation ladder.
  Same plotting code and seeds for raw ACM, shuffled ACM, BIDDER,
  numpy. Identical sample counts, colormap, scaling.

- Rerun `other_digits.py` after adding the raw baseline and
  unseen-pair accounting.

- Rerun `stratified.py` with multiple keys and more baselines.

- Rerun `reseed_test.py` across several bases and periods.

## New Experiments

- **Source-ablation ladder.**
  Compare raw ACM, shuffled ACM, BIDDER, raw Speck counter mode,
  numpy under the same addition and multiplication workflows.
  This is the single most clarifying new experiment because it
  isolates which properties come from the algebra (ACM), the
  ordering (permutation), and the distribution (uniform marginals).

- **Key-ensemble robustness.**
  For every BIDDER-based experiment that makes a scientific claim,
  report median and percentile bands across many keys.

- **Base sweep.**
  Repeat the main science experiments in bases 2, 7, 10, 16, 256.
  Claims currently read as structural. If they're decimal-specific,
  we need to know.

- **Higher-order discrepancy.**
  Track prefix discrepancy for single digits, digit pairs, and
  digit tuples across the period. The exact-at-boundary property
  is proven; the trajectory between boundaries is the interesting
  open question.

- **Multidimensional quadrature.**
  Map digit pairs and triples to (x, y) and (x, y, z). Compare
  BIDDER against Latin hypercube and Sobol. This is the natural
  extension of `stratified.py` using the multi-digit uniformity
  proved in `other_digits.py`.

### Deprioritized

- **Lag structure** (autocorrelation, mutual information).
  Useful but lower priority than the ablation ladder and base
  sweep. The PractRand results already show the Speck permutation
  destroys sequential structure. Lag analysis would confirm this
  but is unlikely to surprise.

## Lower-Priority Reruns

- `experiments/sawtooth/`. Conceptually aligned. Low priority
  unless `acm_core` changes again or the running-mean conjecture
  is being pushed further.

- `experiments/sunflower/`, `experiments/art/fabric/`,
  `experiments/sieves/`, `experiments/art/collapse/`. Art and
  structural visualization. Not the best place to spend rigor
  budget unless the underlying data changes.

## Suggested Execution Order

1. Fix P0: `acm_benford.py` panel 1 and local `first_digits` bugs.
2. Build the source-ablation ladder (new experiment).
3. Rebuild shutter/comparison/interferometry around the 4-source
   ablation (raw ACM, shuffled ACM, BIDDER, numpy).
4. Tighten and rerun `other_digits.py` (add raw baseline).
5. Tighten and rerun `stratified.py` (key ensemble, LHS baseline).
6. Tighten and rerun `reseed_test.py` (base/dc sweep).

## Working Rule

For any experiment that makes a scientific claim rather than just
producing an image:

- Include at least one control.
- Include at least one ensemble result when BIDDER keys are involved.
- State exactly what is being held constant across comparisons.
- Prefer ablations over isolated pretty outputs.
