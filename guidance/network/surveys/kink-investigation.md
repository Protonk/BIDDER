# Kink Investigation

source: [`experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK-INVESTIGATION.md`](../../../experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK-INVESTIGATION.md)  
cited in: [`COLLECTION.md` — The Binary Frontier](../../../COLLECTION.md#chapter-4-the-binary-frontier)  
last reviewed: 2026-04-10

---

**Status.** *Audited down.* An earlier reading that framed the
`n = 3` detrended-RDS Morlet scalogram as a three-rung
arithmetic lattice with click period `b ≈ 951` bits has been
walked back. The doc's status block is explicit about what is
solid and what is not, and the retraction is the distinctive
feature of the note — the longest-form worked example of the
correction discipline in the repo.

**Current evidence.** What survives: the low-band `n = 3` gap
distribution is nonwhite, short-range anti-persistent, and
clustered in a way six white-noise controls do not reproduce.
Four features separate it from controls: the smallest KDE mode
sits at `521` bits (all six controls put their smallest at
`≥ 641`); the distribution is near-symmetric (`skew = +0.23`
vs `+0.66` to `+1.12` for controls); lag-1 autocorrelation is
`−0.213` (vs roughly white in every control); Gaussian is
rejected. What does not survive: the stronger "arithmetic
lattice at click ≈ 951" reading. A bandwidth-sensitivity table
shows the fitted click is a parameter of one narrow KDE
rendering, not of the gap law itself. A 300× bootstrap of the
committed gap CSV produces fitted click in the range
`[477, 950]` interquartile; only 6% of resamples reach the
claimed `0.54%` tightness.

**Depends on.**
[`detrended-rds.md`](detrended-rds.md) — the scalogram this
note is a follow-up to.

**Open questions.** T2 through T7 of the falsification battery
are unrun: band-scaling check across multiple `[lo, hi]`
windows; shuffled-entry control (would place this as a third
"ordering matters" observable alongside Walsh and
Detrended RDS); other monoids (would establish whether the
clustering is `n = 3`-specific or generic); longer stream;
detector swap; number-theoretic alignment against power-of-two
crossings. The nine-item "what this note does not claim"
section at the bottom of the source is the correction
discipline in its sharpest worked form: every walked-back
claim is listed explicitly rather than quietly removed.
