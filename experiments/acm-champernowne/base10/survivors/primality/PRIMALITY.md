# Primality of the survivor collection

The C_Surv ↔ C_Bundle leading-digit L1 tracking is mediated by
**cofactor primality**. Survivors split roughly 52:48 by whether
`m = c / d_source` is prime; the two subsets bracket the bundle's
L1 trajectory, with C_Surv landing near the bundle as their
population-weighted mean.

This directory houses primality-flavoured probes of the survivor
construction. The Surv set and its source-stream tagging are cheap
to compute; primality of `c` and `m` are cheap by sympy. The
non-cheap thing is *n-primality* (rank-in-stream per survivor),
which would let us track each survivor's position in its source
stream's truncation. Deferred until needed.

## EXP01 — cofactor primality stratifies the L1 fit

Panel: `[n_0, n_1] = [2, 10]`, `k = 400` (Two Tongues panel).
1338 survivors out of 2171 unique bundle integers.

**Primality of `c`**: 4 prime survivors `{2, 3, 5, 7}`. Structurally
the only primes that can be in any in-window stream. Identical to
bundle primes. Degenerate.

**Primality of cofactor `m = c / d`**: 692 prime (51.7%), 646
composite (48.3%). Per source stream `d`:

```
   d   |S_d|   prime-m fraction
   2    187    0.722
   3    147    0.714
   4    133    0.714
   5    129    0.705
   6     62    0.484
   7    180    0.478
   8    152    0.217
   9    212    0.396
  10    136    0.243
```

Low source-d streams (`d ∈ [2..5]`) have ~70% prime cofactors. High
source-d streams (`d ∈ {8, 10}`) have ~22-24% prime cofactors.
The prime-cofactor share is monotone-decreasing with `d` (with a
bump at d=9). This aligns with EXP07's identification of d ∈
{8, 9, 10} as the digit-3 spike carriers via finite-k truncation:
those bands are populated by composite m, not prime m.

**Ω(c) distribution** (total prime factors with multiplicity):

```
Ω(c)    bundle frac    survivor frac    shift
  2       0.196          0.313          +0.117  (more semiprimes)
  3       0.286          0.309          +0.023
  4       0.246          0.189          −0.057
  5       0.150          0.111          −0.039
  ≥6      0.109          0.075          −0.034
```

Survivors over-represent semiprimes (Ω=2) by 12 percentage points
and under-represent Ω≥4 integers. The optimizer prefers
prime-factor-simpler integers.

## The fit answer

Stratified leading-digit L1 deviation, end-of-stream, against
uniform-1/9:

```
bundle                              L1 = 0.834
survivors, prime cofactor           L1 = 0.750   (more Benford)
survivors, composite cofactor       L1 = 0.959   (less Benford)
C_Surv (population-weighted avg)        ≈ 0.851 ≈ bundle
```

The bundle's L1 trajectory is **bracketed**: prime-cofactor
survivors sit everywhere below it (more non-uniform), composite-
cofactor survivors sit everywhere above (less non-uniform). The
bracketing holds across the full atom horizon, including through
the n=2 dip (bundle 0.012, prime-cofactor 0.12, composite-cofactor
0.18).

C_Surv lands near the bundle's curve because it is the population-
weighted mean of two populations that bracket the bundle, *not*
because either population alone matches.

This reframes the Two Tongues observation. The cabinet entry's
"survivors track bundle" reading is correct as a description of the
weighted average; the underlying mechanism is a 2-population
balance, not a single-population mimicry.

## EXP02 — residual decay confirms the disentanglement reading

The bracketing isn't startling once you see the trajectories as a
system slowly disentangling from early intransitivity toward an
asymptotic 3-line target (prime-cofactor / bundle / composite-
cofactor at L1 ≈ 0.750 / 0.834 / 0.959). At small atom counts the
populations haven't accumulated enough to resolve their intrinsic
levels and the curves cross; the wiggles in the full curve are the
system trying to reach the 3 lines forever.

Test: `|L1(n) − L1_asymptote|` per curve, viewed across the bundle's
atom-slot order, with stream transitions marked.

RMS |residual| per stream segment:

```
stream segment   bundle   prime-m   comp-m
n=2 (0-400)      0.4216   0.3694   0.5062
n=3 (400-800)    0.2507   0.2396   0.2699
n=4 (800-1200)   0.1480   0.1472   0.1174
n=5 (1200-1600)  0.0880   0.1009   0.0790
n=6 (1600-2000)  0.0503   0.0680   0.0631
n=7 (2000-2400)  0.0256   0.0311   0.0628
n=8 (2400-2800)  0.0292   0.0093   0.0298
n=9 (2800-3200)  0.0082   0.0143   0.0233
n=10 (3200-end)  0.0124   0.0070   0.0542   ← composite-m kicks back up
```

Three readings:

1. **Geometric decay across stream segments** — bundle's RMS
   residual halves roughly every two streams (factor 0.6 per
   stream): 0.42 → 0.25 → 0.15 → 0.09 → ... Same structural shape
   as the K-decade decay in `../ECHO-STRUCTURE.md` (factor ~0.8
   per K-decade there). Slow, never zero.

2. **Power-law-ish envelope on log-log**: slope between −1/2 and
   −1, around −0.6. Smooth power law would mean clean
   thermalisation; the bumps on the envelope show the
   disentanglement is being *kicked* at stream boundaries.

3. **Composite-cofactor n=10 anomaly** — at the last stream segment
   (n=10), composite-m residual jumps to 0.054, 4× the bundle's
   residual at the same segment. This is the EXP07 finite-k
   truncation imprint expressing itself in the residual: when
   stream-10 atoms enter, the composite-cofactor side gets kicked
   hardest because that's where the d=10 apparent-survivor band
   lives. Bundle and prime-cofactor barely register the same kick.

The unification with ECHO-STRUCTURE: the L1 wiggles in the
within-panel atom trajectory and the K-decade echoes in the
across-panel mean-dlen surface are the same structural phenomenon
— slow forgetting of base-aware kicks — viewed at different
observable layers.

## EXP03 — wider window flips the bracketing direction

Test: same panel at n_0=2, K=400 but W=20 instead of W=9. Window
[2, 21] gives 8000 atoms, 4064 unique bundle integers, 2348
survivors (57.8%).

Bet recorded before running:
1. bracketing compresses but holds 2-way  (correct);
2. residual decay rate ~0.6 per stream segment  (wrong — non-
   monotone hump shape instead);
3. some fracturing at high-d streams  (wrong — split is cleaner
   not richer).
Read I dismissed: direction flip  (correct).

**Outcome:**

```
                        W=9              W=20
|unique|                2171             4064
|S|                     1338 (62%)       2348 (58%)
prime-m fraction        51.7%            52.0%   ← unchanged

asymptotic L1:
  bundle                0.834            0.462
  prime-m               0.750            0.511
  composite-m           0.959            0.459

bracketing gap          +0.209           −0.052
```

The bracketing **direction reverses** at W=20: prime-m now sits
above bundle (less Benford), composite-m sits at bundle's level.
At W=9 the bracketing was prime-m < bundle < composite-m by a
total gap of 0.21. At W=20 it's composite-m ≈ bundle < prime-m by
a total gap of 0.05. Same axis (cofactor primality), different
sign.

Mechanism (sketch): at W=9, prime cofactors are mostly primes
≥ 11 (outside the window), and `c = d·p` for small d and unbounded p
gives a Benford-leaning leading-digit signature. At W=20, primes
in [11, 21] can't serve as cofactors for low-d sources (they would
place `c` in two streams), so prime cofactors are pushed to
primes ≥ 23. The denser, more constrained prime-cofactor population
has different leading-digit statistics, and the bracketing flips.

The residual decay is non-monotone:

```
stream    bundle    prime-m   comp-m
n=2       0.324     0.313     0.876
n=3       0.149     0.077     0.401   ← brief dip
n=4       0.238     0.142     0.209
n=5       0.287     0.182     0.181
n=6       0.327     0.208     0.208
n=7       0.389     0.250     0.219
n=8       0.399     0.273     0.284
n=9       0.372     0.257     0.343
n=10      0.382     0.257     0.398
n=11      0.373     0.253     0.474   ← comp-m peak
n=13      0.308     0.222     0.479   ← comp-m peak again
...
n=21      0.036     0.026     0.063
```

Bundle's residual rises from a brief dip at n=3 to a peak around
n=7-8, then decays. Composite-m has a hump n=7 to n=14 with double
peaks at n=11 and n=13. The trajectory overshoots its asymptote.

Per source d at W=20:

```
d ∈ [2..8]     prime-m fraction 88-97%
d = 9, 10      67%, 70%
d ∈ [11..21]   26-44%
```

Sharp transition at d=11. Cleaner than W=9's 70% → 22% gradient.

What this means for the disentanglement reading: wider windows
**reduce the asymptotic tangle** (gap × 0.25) but **complicate the
trajectory** (non-monotone overshoot replaces monotone decay). The
"more room to distribute energy" intuition lands only at the
asymptote; the journey there is more structured, not less.

## EXP04 — the bracketing surface (continuous rotation)

EXP03 showed the bracketing direction flipping between W=9 and
W=20. Question: discrete jump or continuous transition? This
experiment defines a complex-valued bracketing observable and
sweeps W to test.

**Observable:**

```
z(n, W) = (L1_prime_m(n, W) − L1_bundle(n, W))
        + i · (L1_comp_m(n, W) − L1_bundle(n, W))
```

|z| is the tangle magnitude (how far the stratified populations
sit from bundle). arg z is the bracketing direction in the
prime-m / comp-m deviation plane.

Sweep W ∈ [5, 30] step 1 at fixed n_0=2, K=400. For each W, take
the *asymptotic* z (last-atom value).

**Result: smooth clockwise rotation across ~178°.**

```
W      |z|      arg(deg)        regime
 5    0.197      +126           "W=9 pattern" (prime-m below bundle)
 9    0.151      +124
12    0.113      +107
15    0.046      +105   ← |z| minimum
16    0.063       +83           Re(z) flips sign
20    0.048        −4           bracketing direction passes 0°
25    0.090       −36
27    0.130       −64
30    0.082       −52
```

The asymptotic z trajectory in the complex plane is a near-spiral
clockwise around (but not through) the origin. The W=9 vs W=20
flip is two snapshots of a continuous angular sweep, sampled on
either side of the real axis.

**|z| has a minimum at W ≈ 15-20** (~0.046), then *grows again*
as W increases. The bracketing tightens going into the
transition zone, then widens past it. Wider window is not
monotonically tighter.

**arg z heatmap shows clean horizontal banding by W.** The
bracketing direction is essentially W-determined at any large-
enough atom count. The early atom-index gnarliness (bright |z|
streaks at small n for every W) is a separate universal
phenomenon — the "early intransitivity" doesn't go away with
wider windows.

The Riemann analogy lands: |z| has a magnitude minimum where the
phase is sweeping fastest. Far from the minimum, arg z stabilises
and |z| grows. We don't have an actual zero (nor would we expect
one for an empirical observable), but the structural character —
smooth complex-valued field, magnitude and phase carrying
complementary information — is the same shape.

Predictions for further W:
- Past W=30, the rotation should continue at roughly 7°/W. By
  W ≈ 50, arg z would loop back to ~+170°.
- |z| at very large W: either keeps growing (divergent spiral)
  or oscillates (bounded spiral). Cheap to test.

## EXP05 — discrepancy bracketing (Bailey-Crandall observable)

The L1 leading-digit observable is a coarse projection of the
canonical normality observable, the **star discrepancy**
`D_N({10ⁿ α})` of the orbit of shifted tails. Computing `D_N` for
the same five constructions at the Two Tongues panel:

```
                          D_N* at fixed N            D_L*       L
                    N=500   N=1000   N=2000

C_Bundle            0.1293  0.1123  0.0793   →    0.1435    12874
C_Bundle_sorted     0.2043  0.1591  0.0370   →    0.1290     7859
C_Surv              0.0711  0.0878  0.0859   →    0.1194     4894
C_Surv_prime_m      0.1001  0.0901  0.0828   →    0.0954     2434
C_Surv_comp_m       0.1119  0.1238  0.1133   →    0.1457     2460
```

Normalised to the `(log L)/√L` Erdős-Copeland-type benchmark:

```
                       D_L*    (log L)/√L    ratio
  C_Surv_prime_m      0.0954    0.158        0.60   ← lowest
  C_Surv              0.1194    0.122        0.98
  C_Surv_comp_m       0.1457    0.157        0.93
  C_Bundle_sorted     0.1290    0.101        1.28
  C_Bundle            0.1435    0.083        1.73   ← highest
```

**Three readings:**

1. **The bracketing carries.** Composite-cofactor has the highest
   `D_N`, prime-cofactor the lowest, `C_Surv` between them — the
   same ordering as the L1 bracketing, now at the sup-over-
   intervals test instead of the leading-digit projection. The
   primality stratification is structural, not an L1 artefact.

2. **Prime-cofactor survivors are *more* uniform than baseline.**
   Ratio 0.60× of `(log L)/√L`. The prime-cofactor population is
   doing better than a generic Erdős-Copeland-class real at this
   `L` — its discrepancy is structurally constrained downward by
   the primality condition.

3. **The multiset bundle is the worst.** Duplicates from cross-
   stream collisions concentrate small-value digit patterns at
   multiple orbit positions, inflating `D_N` to 1.73× baseline.
   Switching to the unique-sorted bundle (Erdős-Copeland
   Champernowne) drops it to 1.28×. The cleanest single-
   construction normality result we have, `C_Bundle_sorted`, is
   exactly the one already covered by [Copeland and Erdős 1946].

**Connection to PRNG-FRAMEWORK.** This is the empirical foothold
for the conditional theorem in `../../../../../algebra/PRNG-FRAMEWORK.md`:
finite-K `D_N` values are comparable to known-normal baselines, so
`lim_{K→∞} C_Surv^{(K)}` is *consistent with* b-normality. The next
test is K-scaling — does `D_L*(K)` decrease as K grows the way
ECHO-STRUCTURE's geometric decay predicts?

## Connection to ECHO-STRUCTURE

The high-d streams `{8, 9, 10}` that carry the digit-length echoes
(per `../ECHO-STRUCTURE.md`) are the *composite-cofactor* side of
this stratification. Plausible reading: the decade-aligned echoes
are the composite-cofactor signature, while the prime-cofactor
side provides the cleaner "bundle-matching" track.

Testable: running the K-decay sweeps separately on prime-cofactor
and composite-cofactor subsets should localise the echo structure
to the composite side.

## Files

- `primality_test.py` — script for EXP01.
- `primality_l1.png` — stratified L1 trajectory (bundle, prime-
  cofactor survivors, composite-cofactor survivors).
- `primality_zoom.py` — zoom renderer.
- `primality_l1_zoom_early.png` — atoms 0-500, log y. Captures
  the n=2 dip (bundle floors to L1 ≈ 0.012, prime-cofactor only
  to ≈ 0.12, composite-cofactor only to ≈ 0.18). Early regime is
  dynamic — bundle and prime-cofactor cross before atoms 100;
  bracketing emerges with the population.
- `primality_l1_zoom_mid.png` — atoms 1000-1500, linear y.
  Bracketing is clean and parallel: composite-cofactor [0.79,
  0.93], bundle [0.62, 0.79], prime-cofactor [0.55, 0.69]. All
  three curves track in shape; their vertical separation is
  near-constant.
- `primality_residuals.py` — residual decay analyser (EXP02).
- `primality_l1_residuals.png` — `|L1(n) − asymptote|` per curve,
  log y, with stream transitions marked.
- `primality_l1_residuals_loglog.png` — RMS residual envelope
  (50-atom window) on log-log, with reference power laws.
- `primality_W20.py` — EXP03 wider-window comparison.
- `primality_W20.png` — L1 trajectory at W=20.
- `primality_W9_vs_W20_residuals.png` — RMS residual per stream
  segment, both W's, showing the non-monotone hump at W=20.
- `primality_surface.py` — EXP04 bracketing-surface sweep.
- `primality_surface.npz` — cached `z(n, W)` for W ∈ [5, 30].
- `primality_surface.png` — four-panel: |z| heatmap, arg z
  heatmap, asymptotic z trajectory in complex plane, |z|/arg z
  curves vs W.
- `discrepancy.py` — EXP05 star-discrepancy probe across the
  bracketing stratification.
- `discrepancy.png` — `D_N*` vs `N` on log-log for all five
  constructions, with `1/√(2N)` and `(log N)/√N` reference lines.

## Cross-references

- `../SURVIVORS.md` — bundle/survivor construction.
- `../ECHO-STRUCTURE.md` — base-10 echo structure of the
  mean-digit-length bias; the composite-cofactor side is the
  candidate carrier.
- `../../differences/EXP07-FINDINGS.md` — source-stream
  stratification identifying `d ∈ {8, 9, 10}` as the spike
  carriers; this finding adds the primality dimension.
- `../../../../../wonders/curiosity-two-tongues.md` — the
  cabinet entry whose "tracking" observation is sharpened here:
  bracketing, not mimicry.
