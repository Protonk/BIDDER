# Off-spike CF on C_b(n): consistent with Khinchin at low thresholds

The Khinchin-typicality probe (`cf_khinchin_probe.py`) tests whether
the CF expansion of `C_b(n)` has structure beyond the boundary
spikes characterised by `MEGA-SPIKE.md`. With boundary-suspicious
partial quotients masked, the residual distribution is **consistent
with Gauss–Kuzmin at the low thresholds where the test has
statistical power** (T ≤ 8). At higher thresholds the probe is
underpowered (Khinchin expected count below 1) and the result is
*indeterminate*, not confirmatory.

The probe rules out *large* deviations from Khinchin in the
off-spike marginal distribution. It does not close the off-spike
frontier — the validated CF prefix is too short (400–840 PQs per
panel cell) to discriminate at the high-threshold tail where
substrate-correlated structure would be most likely to show.


## What was measured

For each `n ∈ {2, 3, 4, 5, 6, 10}` at `b = 10`:

1. CF of `C_10(n)` computed with two-precision validation
   (LO 80 000 bits, HI 160 000 bits); the validated prefix is the
   longest agreeing initial segment between the two runs.
2. Partial quotients with `log10(a_i) > 3` flagged as
   **boundary-suspicious** and masked. This is **more inclusive**
   than `cf_spikes.py`'s canonical `SPIKE_THRESHOLD = 10⁴`
   (`log10 > 4`) — the probe deliberately masks any 4-digit-or-larger
   PQ to avoid leaking sub-leading boundary structure into the
   off-spike distribution. So the probe's mask is a few PQs larger
   than the strict MEGA-SPIKE event count: e.g. n=4 gets 5 masked
   vs 4 spikes in `cf_spikes.csv`; n=6 gets 6 vs 4. The "extra"
   masks are intermediate-magnitude events at smaller k that would
   pollute the tail. This is a conservative choice in the direction
   that *makes* the off-spike distribution look more Khinchin-like;
   it does not affect the underpowered-tail caveat below.
3. Off-spike survival counts `S(T) = #{i not spike : log2(a_i + 1) > T}`
   computed for `T ∈ {4, 6, 8, 10, 12, 14, 16}`.
4. Compared to the Gauss–Kuzmin (Khinchin) survival
   `P(a > k) = log2(1 + 1 / (k + 1))`, evaluated at `k = 2^T - 1`,
   so that `P_Khinchin(T) = log2(1 + 1 / 2^T)`.


## Result

| n  | validated PQs | spike PQs | off-spike PQs |
|----|---------------|-----------|---------------|
| 2  | 408           | 6         | 402           |
| 3  | 487           | 4         | 483           |
| 4  | 514           | 5         | 509           |
| 5  | 613           | 4         | 609           |
| 6  | 660           | 6         | 654           |
| 10 | 843           | 3         | 840           |

Off-spike vs Khinchin survival, with z-scores:

| n  | T = 4 (z) | T = 6 (z) | T = 8 (z) | T ≥ 10 |
|----|-----------|-----------|-----------|--------|
| 2  | −1.62     | −0.33     | −0.17     | 0 obs vs 0.57 expected at T=10; null below |
| 3  | −0.52     | −0.25     | −1.04     | null |
| 4  | +1.02     | +1.08     | +0.67     | null |
| 5  | −0.32     | −0.72     | −0.77     | null |
| 6  | −0.30     | +0.36     | +0.17     | null |
| 10 | +1.65     | +0.28     | −0.33     | null |

Across 42 cells (6 n's × 7 thresholds), every `|z| < 1.7`, with most
under 1. No cell approaches significance after multiple-comparison
correction. The off-spike empirical survival curve overlays
Khinchin's at every panel cell — see
`cf_khinchin_probe_survival.png`.


## Reading

The result is **consistent with — but does not confirm — the
foothold reading** for the off-spike CF process. At the resolution
where the test has power (T ≤ 8), the off-spike marginal
distribution looks like Gauss–Kuzmin. At higher T the test is null
because Khinchin itself predicts almost no events; we cannot tell
whether the absence of observations matches Khinchin's tail or
masks a real deviation that would only emerge at much larger
sample sizes.

The compatible foothold story is: the CF expansion of `C_b(n)`
decomposes as boundary spikes (substrate-transparent closed form
per `MEGA-SPIKE.md`) plus Gauss–Kuzmin everywhere else. The
present probe is consistent with this picture. It is *also*
consistent with a perimeter story where the off-spike process has
high-tail structure invisible at 400–840 PQs per cell. To
discriminate the two, the validated prefix has to be longer; that
needs higher mpmath precision (currently 80k–160k bits) and more
n-primes feeding the digit stream.

Per the symmetric foothold/perimeter framing in
`experiments/math/hardy/SURPRISING-DEEP-KEY.md`, neither outcome
is yet established. What is established is that *gross* deviation
from Khinchin in the off-spike marginal is ruled out at this
resolution.


## What this rules out and what it doesn't

**Rules out at this resolution.**

- Gross deviation from Khinchin in the off-spike marginal at
  thresholds T ∈ {4, 6, 8}, where the test has Poisson-effective
  power (~10–800 expected events per cell).
- A "second spike family" hiding in the upper range of the
  off-spike distribution at low T — there isn't one with effect
  size large enough to push the |z| > 2 over the panel.

**Does not resolve.**

- **Sample size.** Validated CF prefixes are short (400–840 PQs per
  cell). Khinchin survival expected count drops below 1 at `T = 10`
  across the panel, so the probe has no power to detect deviation
  at high thresholds. The most extreme partial quotients above the
  boundary-spike threshold could carry structure not visible at
  this resolution.
- **Marginal vs joint distribution.** The probe checks marginal
  partial-quotient distribution. A process can have Gauss–Kuzmin
  marginals and non-trivial autocorrelation, recurrence, or spectral
  structure. The off-spike process *between* consecutive spikes is
  Gauss-typical in distribution; whether it has hidden joint
  structure (e.g. recurrence between consecutive PQs or correlation
  with substrate residue class) is open.
- **Intermediate-ord primes** (`n ∈ {13, 23, 31}`) not in the
  panel; the probe should be extended to confirm.
- **Higher k.** All boundary spikes captured were at low k (the
  validated CF prefix barely reaches `k = 4` for some panel cells).
  The off-spike behaviour at high k is unprobed.


## Files

- `cf_khinchin_probe.py` — the script.
- `cf_khinchin_probe.csv` — per-(n, i): log10(a_i), log2(a_i+1),
  is_spike flag.
- `cf_khinchin_probe_summary.txt` — survival table per n.
- `cf_khinchin_probe_survival.png` — survival curves overlaid on
  Khinchin reference.
- `cf_khinchin_probe_run.log` — runtime log.
