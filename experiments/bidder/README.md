# BIDDER Experiments

Experiments whose primary source is BIDDER generator output — already
scrambled and exactly uniform by design. These test the generator's
properties, not the raw ACM construction.

## Experiment families

- **dither/** — Dithering comparison: BIDDER vs numpy PRNG. (Negative
  result: exact marginal uniformity does not help dithering.)

- **reseed/** — Rekeying via SHA-256, checking for detectable seams.

- **stratified/** — Stratified sampling at block boundaries.

- **digits/** — Multi-digit extraction beyond the leading digit.

- **art/contamination/** — Using BIDDER as a calibration source to
  characterize how arithmetic operations (multiplication, addition)
  contaminate uniform distributions.
