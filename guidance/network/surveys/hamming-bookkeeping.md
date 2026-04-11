# Hamming Bookkeeping

source: [`experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md`](../../../experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md)  
cited in: [`COLLECTION.md` — The Binary Frontier](../../../COLLECTION.md#chapter-4-the-binary-frontier)  
last reviewed: 2026-04-10

---

**Status.** Closed form, proved, with a corrected per-entry
vs. per-monoid reading. The doc also documents its own
revision: an earlier per-monoid reading was wrong for all
composites and for `n = 2^m` with `m ≥ 2`, and was corrected
against the disparity-domain measurement in
[`detrended-rds.md`](detrended-rds.md).

**Current evidence.** For `n = 2^m`, the expected fraction of
1-bits in a `d`-bit n-prime is

```
bias(2^m, d) = 1/2 + (1/(2d)) · [1 − 2m + m · 2^m / (2^m − 1)]
```

valid for `d > 2m`. The asymmetry argument is the distinctive
passage: the *trailing-zero penalty* is linear in `m` (each
forced trailing zero removes `1/2` of an expected one), while
the *bottom-bit constraint bonus* from `k mod 2^m ≠ 0` decays
exponentially (one excluded pattern out of `2^m`). They cross
at exactly `m = 1`, explaining why `n = 2` is the only
non-trivial monoid whose expected bit count matches the
universal `(d+1)/(2d)` baseline. Two companion experiments
confirm the closed form at different resolutions:
per-`(n, d)`-class in the Hamming Strata experiment, and
per-entry in the Detrended RDS experiment.

**Depends on.** [`binary.md`](binary.md) for the construction
and the verdict that bit-level structure is the right object
of study; [`acm-champernowne.md`](acm-champernowne.md) for the
n-prime definition.

**Open questions.** Closed forms for the other observables
the binary forest tracks — run-length distributions,
boundary-conditioned increments, local autocorrelation — are
still open. The valuation forest experiment shows `v₂`
predicts the bulk of the mean-zero-run-length signal with
localized exceptions at small odd parts, but the closed form
for that observable (analogous to the one above) is not yet
derived.
