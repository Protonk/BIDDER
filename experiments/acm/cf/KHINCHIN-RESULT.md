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
foothold reading** at the marginal level. At the resolution
where the test has power (T ≤ 8), the off-spike marginal
distribution looks like Gauss–Kuzmin. At higher T the test is null
because Khinchin itself predicts almost no events.

The marginal-only result is refined at the block-aggregate level
in `DENOMINATOR-PROCESS.md`, which tests the substrate prediction
`Δ_k = D_{k-1} + (n − 1) + O(b^{−(k-1)})` for canonical-to-canonical
log-q growth directly. That test passes to the spike formula's
intrinsic precision floor across three layers (k = 2 → 3 residuals
~`10⁻²`, k = 3 → 4 ~`10⁻³`, k = 4 → 5 ~`10⁻⁴`) over 17 canonical
blocks across the panel. The block-level test does not depend on
having Khinchin-typical tail events; it tests substrate envelope
plus Khinchin interior and finds the substrate–Khinchin
decomposition holds.

The XXL probe (`cf_khinchin_probe_xxl.py` at LO 1.5M / HI 3M bits)
extended the validated CF prefix from 400–840 PQs per cell to
1193–2000 PQs, capturing k = 5 canonical boundary spikes for all
six panel cells. With the larger sample, the marginal Khinchin
test now has cleanly-powered results at T ∈ {4, 6, 8} (max
|z| ≈ 2.16), with T ≥ 10 still bounded by an interaction between
the survival threshold (`a ≥ 1024` at T = 10) and the spike mask
(`a > 1000`): off-spike tail observations at T ≥ 10 are
artificially zeroed by the mask, so survival counts at high T are
not informative under the current cutoff. Lifting that requires a
higher `LOG10_SPIKE` threshold (so the mask sits above the survival
range tested) and more validated PQs.

So the foothold reading is established at the block-aggregate
level across k = 2 → 5 (substrate predicts Δ exactly) and at the
small-PQ marginal level for T ≤ 8. The high-T marginal tail
remains masked-out at the current cutoff. Per the symmetric
foothold/perimeter framing in
`experiments/math/hardy/SURPRISING-DEEP-KEY.md`, the
`DENOMINATOR-PROCESS.md` result extends the foothold reading two
layers deeper than the boundary spikes (the boundary-to-boundary
substrate envelope at k = 5 was the immediate target).


## What this rules out and what it doesn't

**Rules out at this resolution.**

- Gross deviation from Khinchin in the off-spike marginal at
  thresholds T ∈ {4, 6, 8}, where the test has Poisson-effective
  power (~10–800 expected events per cell).
- A "second spike family" hiding in the upper range of the
  off-spike distribution at low T — there isn't one with effect
  size large enough to push the |z| > 2 over the panel.

**Does not resolve at the marginal level (this probe).**

- **Sample size at the original 80k/160k bit precision.** Validated
  CF prefixes are short (400–840 PQs per cell). The XXL probe at
  LO 1.5M / HI 3M bits extends them to 1193–2000 PQs, but T ≥ 10
  observations are forced to zero by the interaction between
  the survival threshold (`a ≥ 1024` at T = 10) and the spike mask
  (`a > 1000`); see "Reading" above. The high-T marginal tail
  remains open, and would need either a raised `LOG10_SPIKE`
  threshold or a different test statistic to interrogate.
- **Marginal vs joint distribution.** The probe checks marginal
  partial-quotient distribution. A process can have Gauss–Kuzmin
  marginals and non-trivial autocorrelation, recurrence, or spectral
  structure. The off-spike process *between* consecutive spikes is
  Gauss-typical in distribution; whether it has hidden joint
  structure (e.g. recurrence between consecutive PQs or correlation
  with substrate residue class) is open. The block-aggregate test
  in `DENOMINATOR-PROCESS.md` constrains the *block totals*; joint
  *positions* of large PQs within a block are unprobed.
- **Intermediate-ord primes** (`n ∈ {13, 23, 31}`) not in the
  panel; the probe should be extended to confirm.
- **Higher k.** At the original 80k/160k bit precision, the
  validated CF prefix barely reaches `k = 4`. The XXL probe extends
  this to `k = 5` for five of six panel cells (n = 4 still
  transient at k = 5). The k ≥ 6 region needs a further precision
  step (LO ≥ ~3.5M / HI ≥ ~7M bits); not pursued here.

- **Sub-canonical spike rate.** The XXL block-aggregate analysis
  in `DENOMINATOR-PROCESS.md` shows `≈ 3×` Khinchin-expected rate
  of intermediate-magnitude (`a > 1000`) excursions that are not
  at canonical L. This is a real perimeter signal, not addressed
  by the marginal probe.


## Files

- `cf_khinchin_probe.py` — the script.
- `cf_khinchin_probe.csv` — per-(n, i): log10(a_i), log2(a_i+1),
  is_spike flag.
- `cf_khinchin_probe_summary.txt` — survival table per n.
- `cf_khinchin_probe_survival.png` — survival curves overlaid on
  Khinchin reference.
- `cf_khinchin_probe_run.log` — runtime log.
