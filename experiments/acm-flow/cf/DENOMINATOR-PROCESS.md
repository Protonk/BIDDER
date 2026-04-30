# Off-spike denominator process: substrate envelope plus Khinchin interior

`KHINCHIN-RESULT.md` established that the *marginal* off-spike CF
distribution on `C_b(n)` is consistent with Gauss–Kuzmin at low
thresholds (T ≤ 8). The marginal-only result left two readings open:

- **Foothold reading.** The off-spike denominator process is governed
  by substrate quantities at the block-aggregate level, with
  Khinchin-typical fluctuations within each block.
- **Perimeter reading.** The off-spike process has joint structure
  (autocorrelation, recurrence, residue dependence) not reducible to
  substrate plus Khinchin marginals.

`offspike_dynamics.py` discriminates the two by testing the *block-total*
substrate prediction directly. The result is **foothold**: the
substrate predicts the canonical-to-canonical log-denominator growth
to the spike formula's intrinsic precision floor, and the residual
small-PQ process within each block is Khinchin-typical.


## The closed-form prediction

`MEGA-SPIKE.md` and `OFFSPIKE-RESULT.md` give the convergent denominator
at the boundary just before each canonical k-th boundary spike:

    L_{k-1} := log_b q_{i_k - 1}
            = C_{k-1} + (n − 1) k + offset(n) − O(b^{−k}).

Differencing across consecutive canonical boundaries,

    Δ_k := L_{k-1} − L_{k-2} = D_{k-1} + (n − 1) + O(b^{−(k-1)}),

a substrate-only prediction for the boundary-to-boundary log-q growth.
Multi-step generalisation: when the validated CF prefix contains
canonical boundaries at k_prev and k_cur (with intermediate canonicals
possibly missing — e.g. transient-`n` cells where only k = 4 is
canonical at this resolution), the prediction is the closed-form
difference of the two endpoint formulas.


## Test A: substrate envelope

For each canonical-to-canonical block in the panel `n ∈ {2, 3, 4, 5,
6, 10}` at b = 10, observed Δ_obs vs substrate prediction Δ_pred.
Data from `cf_khinchin_probe_xxl` at LO 1.5M / HI 3M bits, validated
prefix 1193–2000 PQs per cell:

    n    k_prev → k_cur   i_prev → i_cur     Δ_obs       Δ_pred       resid
    2       1   →   2        0   →   10      4.6902      4.6990     -0.0087
    2       2   →   3       10   →   32     47.0079     47.0000     +0.0079
    2       3   →   4       32   →  118    676.0008    676.0000     +0.0008
    2       4   →   5      118   →  408   9001.0001   9001.0000     +0.0001
    3       1   →   2        0   →   16      6.0413      6.0458     -0.0044
    3       2   →   3       16   →   44     42.0040     42.0000     +0.0040
    3       3   →   4       44   →  162    602.0004    602.0000     +0.0004
    3       4   →   5      162   →  488   8002.0000   8002.0000     +0.0000
    4       1   →   4        0   →  148    553.3979    553.3979     -0.0000
    5       1   →   3        0   →   56     42.9996     43.0000     -0.0004
    5       3   →   4       56   →  178    436.0004    436.0000     +0.0004
    5       4   →   5      178   →  616   5764.0000   5764.0000     +0.0000
    6       1   →   3        0   →   72     41.0453     41.0458     -0.0004
    6       3   →   4       72   →  188    380.0004    380.0000     +0.0004
    6       4   →   5      188   →  660   5005.0000   5005.0000     +0.0000
   10       1   →   4        0   →  212    296.6989    296.6990     -0.0000
   10       4   →   5      212   →  844   3249.0000   3249.0000     +0.0000

17 canonical-block tests. Mean residual `−0.000004`, max |residual|
`0.0087`. The residuals decay as `b^{−(k−1)}` cleanly across three
layers:

- k = 2 → 3:  residuals ~`10⁻²`  (e.g. `+0.0079` for n = 2)
- k = 3 → 4:  residuals ~`10⁻³`  (e.g. `+0.0008` for n = 2)
- k = 4 → 5:  residuals ~`10⁻⁴`  (`+0.0001` for n = 2; the other
                                    four cells with a canonical
                                    k = 4 → 5 row — n = 3, 5, 6, 10
                                    — round to `0.0000`. n = 4
                                    does not yet have a canonical
                                    k = 4 → 5 row at this resolution;
                                    its k = 5 candidate is still in
                                    transient.)

This matches the spike formula's intrinsic O(b^{−(k−1)}) error term
exactly — the substrate prediction is exact to the precision the
spike formula itself gets. The pattern holds across primes,
prime powers, and composites in the panel.

Transient-`n` cells (n = 4, 10) where canonical detection skips
intermediate k still pass via the multi-step prediction (e.g. L_3
from origin for n = 4), with the same precision floor.


## Test B: Khinchin interior

Within each canonical block, partial quotients separate into:

- **Small PQs** (`log10 a ≤ 3`): the off-spike marginal that
  KHINCHIN-RESULT.md found Gauss–Kuzmin-typical at low T.
- **Sub-canonical spikes** (`log10 a > 3`, but L_obs deviates from
  the canonical prediction by more than the OFFSET_TOL = 0.05): rare
  intermediate large PQs not assigned to any canonical k.

The substrate envelope `Δ_pred` budgets the entire block-total log-q
growth. Test B asks whether the *small* PQs alone are
Khinchin-typical at the block-aggregate level, and how the
sub-canonical spikes fit in.

    n    k_prev → k_cur   M_small  M_sub  sum_small  mean_small    M_kh    M_z
    2       1   →   2          9      0     4.1754      0.4639      9.7   −0.20
    2       2   →   3         21      0     6.1796      0.2943     14.4   +1.45
    2       3   →   4         84      1    36.3089      0.4322     84.6   −0.06
    2       4   →   5        287      2   115.1504      0.4012    268.4   +0.94
    3       1   →   2         15      0     4.4348      0.2957     10.3   +1.21
    3       2   →   3         27      0     9.5614      0.3541     22.3   +0.83
    3       3   →   4        117      0    45.6125      0.3899    106.3   +0.86
    3       4   →   5        324      1   143.0225      0.4414    333.4   −0.43
    4       1   →   4        144      3    67.0985      0.4660    156.4   −0.83
    5       1   →   3         54      1    27.8872      0.5164     65.0   −1.14
    5       3   →   4        121      0    48.2190      0.3985    112.4   +0.67
    5       4   →   5        436      1   184.9767      0.4243    431.2   +0.19
    6       1   →   3         69      2    26.4713      0.3836     61.7   +0.77
    6       3   →   4        115      0    50.2887      0.4373    117.2   −0.17
    6       4   →   5        469      2   200.6163      0.4278    467.7   +0.05
   10       1   →   4        209      2    99.0062      0.4737    230.8   −1.19
   10       4   →   5        631      0   290.2535      0.4600    676.6   −1.46

`M_kh = sum_small / E[log_b a]_GK` (Khinchin renewal prediction for the
PQ count). `M_z` is the delta-method z-score of `M_small` against
`M_kh` under Gauss–Kuzmin, allowing for `Var[log_b a]_GK` per step.

Mean `|z|` is small (max 1.46 across 17 blocks, mean +0.09). The
weighted pooled small-PQ mean is `Σ sum_small / Σ M_small =
1359.27 / 3132 = 0.4340` versus the Khinchin **conditional**
prediction `E[log₁₀ a | a ≤ 1000]_GK ≈ 0.4247` (the Gauss–Kuzmin
tail above `10³` contributes `≈ 0.00495` to the unconditional mean
`0.4290`; excluding it gives the conditional). Difference
`+0.0093`, with pooled SE `≈ √(Var/M) ≈ √(0.266/3132) ≈ 0.0092`.
That is `≈ 1.0 σ` — within noise. The small-PQ marginal is
Khinchin-typical at the block level after accounting for the
cutoff.

**Sub-canonical spike rate is non-trivial.** Across the 17 blocks
there are `M_sub = 15` interior partial quotients with `a > 1000`
that are not at canonical L. Khinchin survival
`P(a > 1000) = log₂(1 + 1/1001) ≈ 1.44·10⁻³`, so the
renewal-Khinchin expectation across `Σ M_small + Σ M_sub ≈ 3147`
interior PQs is `≈ 4.53` events. Observed `15` against
`4.53 ± √4.53 ≈ ±2.13` gives Poisson-normal `z ≈ +4.9` (exact
Poisson tail `P(X ≥ 15 | λ = 4.53) ≈ 4·10⁻⁵`).

What this baseline assumes. The renewal-Khinchin expectation
is the *interpolation* between Test A (substrate at canonical L)
and Test B (Khinchin at small-PQ): "what if the interior were
Khinchin-typical at all magnitudes." Test B confirms that for
`a ≤ 1000`; Test C asks whether it extrapolates to `a > 1000`.
A genuine perimeter reading requires that the Khinchin
extrapolation *is* the right null. An alternative reading is
that the interior is a Gauss process *conditioned* on hitting
the substrate-set log-q target at the next canonical boundary —
that conditioning generically inflates large-`a` tails relative
to the unconditional renewal, and could account for some or all
of the 3× factor. The cheapest diagnostic is to compute that
conditional rate explicitly and compare; until that's done,
"3× Khinchin renewal" is the right number for the unconditional
baseline but not necessarily for the conditional one.

Block-by-block breakdown. The 15 events distribute across cells
roughly proportional to interior length, not concentrated:

  n=2:  0  + 0  + 1  + 2   = 3   (interior 9 + 21 + 85 + 289 = 404)
  n=3:  0  + 0  + 0  + 1   = 1   (interior 15 + 27 + 117 + 325 = 484)
  n=4:  3                  = 3   (interior 147; single canonical pair)
  n=5:  1  + 0  + 1        = 2   (interior 55 + 121 + 437 = 613)
  n=6:  2  + 0  + 2        = 4   (interior 71 + 115 + 471 = 657)
  n=10: 2  + 0             = 2   (interior 211 + 631 = 842)

By transition: k=1→2 contributes 0, k=2→3 contributes 0, k=1→3
and k=1→4 (multi-step from origin) contribute 8, k=3→4 contributes
1, k=4→5 contributes 6. Larger blocks dominate; the per-PQ rate is
roughly uniform across the panel. So the excess is not n-specific
and not k-specific — it has the shape of a uniform interior
phenomenon at rate `≈ 3×` Khinchin renewal, which is the
multi-seed-equivalent evidence that `z ≈ +4.9` is not a
single-block artefact.


## Reading

The off-spike denominator process between canonical boundary spikes
decomposes into three pieces:

- A **substrate envelope** (Δ_pred = D_{k-1} + (n − 1) + O(b^{−(k-1)}))
  fixes the total log-q growth between canonical boundaries. This
  matches observation to the spike formula's precision floor across
  three layers (Test A, 17 blocks). Foothold.
- A **Khinchin small-PQ interior** (`a ≤ 1000`) consumes most of the
  envelope at the Gauss–Kuzmin geometric-mean rate (Test B,
  pooled mean within `1 σ` of GK conditional prediction). Foothold.
- An **anomalous intermediate-magnitude excess** at `a > 1000` not
  located at canonical L: appears `≈ 3×` more often than the
  *unconditional* Khinchin renewal baseline (Test C, `z ≈ +4.9`,
  exact tail `≈ 4·10⁻⁵`). Distributed roughly uniformly across the
  panel — not n-specific, not k-specific. Whether this is a third
  population (perimeter) or a manifestation of conditioning the
  interior on the substrate target (foothold deeper) is open;
  see the conditional-renewal calculation noted under "What this
  leaves open."

So the foothold reading holds for the substrate envelope at all
17 canonical blocks and for the small-PQ marginal. The third
layer's reading depends on the conditional-renewal calibration —
foothold-deeper if it accounts for the 3× factor, perimeter
located if it doesn't.

The substrate transparency catalogued in
`experiments/math/hardy/SURPRISING-DEEP-KEY.md` extends two layers
deeper than the boundary spikes (envelope + small-PQ marginal),
and is pending verdict on a possible third layer.

This is the foothold reading per the symmetric foothold/perimeter
framing of `core/ABDUCTIVE-KEY.md`. The two statements compose:
substrate-driven envelope + Khinchin-typical interior gives a
**substrate–Khinchin decomposition** of the CF expansion of `C_b(n)`.


## Consequences for `MU-CONDITIONAL.md`

`MU-CONDITIONAL.md` derives `μ(C_b(n)) = 2 + (b − 1)(b − 2)/b`
conditional on the premise that boundary spikes dominate the
approximation budget. The substrate–Khinchin decomposition makes that
premise quantitative: the off-spike block contribution is bounded by
`Δ_pred = D_{k-1} + (n − 1)`, which is a closed-form quantity rather
than an empirical estimate. This converts the conditional `μ` into
something one can audit term-by-term.

The full unconditional `μ` still requires the `O(b^{−(k-1)})` residual
term to be bounded uniformly — see *What this leaves open* below.


## What this leaves open

- **Higher k.** The XXL probe at LO 1.5M / HI 3M bits reached k = 5
  canonical boundaries for **five of six** panel cells (n = 2, 3,
  5, 6, 10), with Test A residual at the k = 4 → 5 transition
  consistent with `O(b^{−4}) = 10^{−4}` (max residual `+0.0001`,
  four of five at `0.0000`). The sixth cell, n = 4, is still
  transient at k = 5 in the XXL data: the spike candidate at
  i = 516 has offset `−0.30` from the canonical L for its k, well
  outside the canonical tolerance — consistent with n = 4's
  documented transient regime in `OFFSPIKE-RESULT.md` for
  `ord(10, 4)` undefined (gcd > 1). It will become canonical at
  some higher k, but not yet here. The k = 6 boundary is beyond
  this resolution overall: the k = 5 spike for n = 2 has ~102 765
  decimal digits, k = 6 would have ~10× more, requiring LO ≥ ~3.5M
  and HI ≥ ~7M bits to validate past it. Each additional layer
  roughly doubles the precision budget. An interim attempt at LO
  400k / HI 800k (`cf_khinchin_probe_xl.py`, deprecated) did *not*
  extend the validated prefix because it sat below the k = 5
  spike's precision requirement; preserved as a documented null
  result with the diagnostic in `cf_validation_triangulate.py`.

- **Sub-canonical spike rate.** The `z ≈ +4.9` excess of `a > 1000`
  events not at canonical L (15 observed vs 4.53 Khinchin-expected
  across 3147 interior PQs) is the open perimeter signal, with
  one calibration step before it counts as a perimeter object.

  **Next probe: the conditional-renewal calculation.** The
  unconditional Khinchin-renewal baseline assumes the interior
  is Khinchin-typical at all magnitudes. The interior is in fact
  conditioned on hitting the substrate-predicted log-q target
  at the next canonical boundary. Conditioning a Gauss process
  on a cumulative-sum target generically inflates the large-`a`
  tail relative to the unconditional case. Compute the conditional
  rate `P(a > 1000 | conditioning)` and compare to the
  observed `15 / 3147`. Two outcomes:

    - The conditional rate accounts for the 3× factor →
      foothold extends one layer deeper (interior is Khinchin
      conditioned on the substrate target); the perimeter
      signal dissolves.
    - The conditional rate falls short of the observed rate →
      the perimeter is genuinely a third population of
      intermediate-magnitude excursions at non-canonical L
      that neither substrate nor (conditioned) Khinchin
      predicts. Candidate mechanisms: secondary boundary-like
      events at sub-block radix transitions (digit-class
      transitions inside a block); substrate "ghosts" — a
      sub-leading family analogous to canonical L but at a
      shifted offset; or residue-class enhancement the spike
      formula doesn't track.

  Until the conditional-renewal calculation lands, "3× Khinchin
  renewal" is the right number for the unconditional baseline
  and the wrong number for declaring perimeter located.

- **`O(b^{−(k-1)})` residual sign.** The residuals in Test A are not
  uniformly signed — k = 1 → k transitions are negative
  (`−0.0087`, `−0.0044`, `−0.0004`, ...), and k = 2 → 3 transitions
  are positive (`+0.0079`, `+0.0040`, ...), and k = 3 → 4 are
  marginally positive (`+0.0008`, `+0.0004`, ...). The pattern looks
  oscillatory rather than monotone. Whether the sign and magnitude
  follow a closed form per `(n, k)` is an open question; if yes, that
  closes one more layer of the substrate transparency.

- **Sub-canonical spikes (already flagged above).** Each block
  contains 0–3 sub-canonical spikes (log10 a > 3 but not at
  canonical-L). They sum into Δ_pred for the substrate-budget total
  but their *rate* is `≈ 3×` the Khinchin-renewal prediction, and
  their internal positions and magnitudes are unmodelled. They are
  the open perimeter signal — possibly admitting a substrate-driven
  predictor (a third layer of substrate transparency), possibly
  intrinsic CF-arithmetic structure not reducible to substrate.

- **Joint structure within blocks.** Test B confirms the *marginal*
  small-PQ distribution is Khinchin-typical. Joint statistics
  (autocorrelation, return times, dependence on substrate residue at
  the corresponding digit position) are unprobed. A Khinchin-typical
  marginal can mask non-trivial joint structure.


## Files

- `offspike_dynamics.py` / `offspike_dynamics_xxl.py` — the
  analyzer at original (80k/160k bits) and XXL (1.5M/3M bits)
  precision, respectively. The XXL run is the one whose data is
  reported above.
- `offspike_dynamics_xxl.csv` — per-block test rows.
- `offspike_dynamics_xxl_spikes.csv` — per-spike classification
  (canonical / sub-canonical).
- `offspike_dynamics_xxl_summary.txt` — text tables.
- `cf_khinchin_probe_xxl.py` — extended-precision marginal probe;
  reaches the k = 5 canonical boundary for all six panel cells.
- `cf_khinchin_probe_xl.py` — earlier attempt at LO 400k /
  HI 800k bits; did not extend the validated prefix (k = 5 spike
  is ~102k decimal digits, larger than 800k bits can resolve).
  Preserved as a documented null result.
- `cf_validation_triangulate.py` — diagnostic showing the
  validation bottleneck is the spike magnitude at the divergence
  step, not the LO/HI ratio.


## Cross-references

- `MEGA-SPIKE.md` (this folder) — the boundary spike formula.
- `OFFSPIKE-RESULT.md` (this folder) — `δ_k(n) = (n−1)k +
  offset(n)` decomposition; supplies the canonical L_{k-1}
  prediction used here.
- `KHINCHIN-RESULT.md` — marginal off-spike Khinchin probe;
  predecessor result, refined here at the block-aggregate level.
- `MU-CONDITIONAL.md` — irrationality measure conditional on
  boundary spikes dominating; this document quantifies the off-spike
  contribution that "dominates" must be measured against.
- `experiments/math/hardy/SURPRISING-DEEP-KEY.md` — symmetric
  foothold/perimeter framing; this is a foothold extension.
