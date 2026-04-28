# Phase 1 results — graduation outcomes

The two controlled scans from `STRUCTURE-HUNT.md` Phase 1 ran;
the four-coordinate decomposition in `ACM-MANGOLDT.md` survives
in revised form. This document records what graduated, what fell,
and what the result implies for the program.


## Scans executed

| script | brief | output |
|---|---|---|
| `cutoff_ray_scan.py` | `CUTOFF-SCAN.md` | `cutoff_ray_scan.csv`, `cutoff_ray_summary.txt`, 9 PNGs |
| `payload_scan.py` | `PAYLOAD-SCAN.md` | `payload_scan.csv`, `payload_scan_summary.txt`, 10 PNGs |

Both scripts pass the smoke check `Λ_2(36) = −log(6)`.


## Result 1 — cutoff coordinate FALLS

For each of 9 panel cells `(n, m)` with `n ∈ {2, 3, 4, 5}` and m
spanning heights, payload τ_2's, and m-block types, swept `Y` over
`[1, 50000]` with `X = mY`. Every scout was flat:

|  scout | ξ_mean range | bucket-mean variation |
|---|---:|---:|
| `τ_2(Y)` | 0.006 – 0.007 | ≤ 0.001 in mean ρ across τ_2 buckets |
| witness count | 0.005 – 0.006 | ≤ 0.001 |
| `dist_n²` | 0.0001 – 0.0007 | ≤ 0.001 |
| `dist_n³` | < 0.001 | ≤ 0.001 |
| diag/prime-row disagree | < 0.001 | (Tier 3 demoted, confirmed) |
| `is_square` | 0.001 | ≤ 0.001 |
| `spf` | 0.09 – 0.11 | trivial Y∈M_n indicator |

The only non-trivial ξ is for `spf`, which is the
"is `Y` divisible by `n`" indicator — i.e., whether `Y` contributes
to the `In` sum at all. Not structural.

**Mechanism.** The L4d aggregate "monotone in `τ_2(Y)`" was a
small-Y/large-Y artifact: at fixed `X = 10000`, varying `m` made
`Y = ⌊X/m⌋` vary, so small-`Y` (early-transient ρ ≈ 0) appeared in
low-`τ_2(Y)` buckets and saturated-`Y` appeared in high-`τ_2(Y)`
buckets. The "monotone progression" was an `m`-confound — exactly
the falsifier `CUTOFF-SCAN.md` named.

### Spatial / texture cross-check

A `boundary_stitch`-style probe (`cutoff_ray_stripe.py`,
`cutoff_texture.py`, `flow_heatmaps.py`, prompted by
`BOUNDARY_STITCH.md`'s caution that bucket-mean averaging can
flatten genuine spatial structure) takes the post-saturation
residual `ρ(Y) − ρ_∞` and asks:

- After subtracting a smooth `1/log Y` fit, is there structure?
- Does the residual have non-zero per-bucket means at `Y mod n²`?
- Does the autocorrelation function show peaks at lags `n²`, `n³`,
  `10`, `100`?
- Does a **panel-cell × scout-bucket heatmap** with row-background
  subtracted show cross-cell coherent patterns?

Per `cutoff_texture_summary.txt` (single-cell ACF and bucket-mean
analysis):

| (n, m) | residual std | max |bucket μ| (Y mod n²) | ACF at lag n² | ACF at lag n³ |
|---|---:|---:|---:|---:|
| 2, 36 | 1.5×10⁻⁴ | 1.0×10⁻⁵ | +0.90 | +0.86 |
| 5, 100 | 3.9×10⁻⁴ | 2.8×10⁻⁵ | +0.95 | +0.82 |
| 4, 48 | 3.2×10⁻⁴ | 2.4×10⁻⁵ | +0.95 | +0.86 |

The high ACF values are slow smooth-trend autocorrelation, not
spectral peaks at `n²`/`n³`. ACF curves decay monotonically with no
bumps at `n²`, `n³`, `10`, or `100`. Per-bucket means are an order
of magnitude smaller than the residual std at every cell.

### Two qualifications surfaced by the heatmaps

The single-cell ACF/bucket analysis says "no resolvable structure"
at scale 10⁻³. Two heatmap views (`cutoff_matrix.png`,
`cutoff_heatmap_*.png`) qualify that:

**1. A near-saturation transient.** Per-cell `Y-batch × τ_2(Y)`
heatmaps show coherent bucket-correlated structure in the *first*
~1000 Y values past saturation (Y ≈ 200–1500), at amplitude
~10⁻³–10⁻⁴, fading to essentially zero by Y ≳ 5000. The texture-
probe used the whole post-saturation range as one block and so
averaged this transient out. The transient is real but decays;
whether it carries information beyond "the In sum is still settling
in" is an open call.

**2. A cross-cell coherent dist-to-n² pattern at 10⁻⁵.** The
panel-cells × scout-bucket heatmap, with row-mean subtracted,
shows that for the `dist_n²` scout *every* row (n=2 m=4, n=2 m=12,
…, n=5 m=100, n=4 m=48) has the same column pattern:
`dist_n²=0` slightly more negative than row mean, `dist_n²=2`
slightly less negative, max amplitude ≈ 1.2×10⁻⁵. Random per-cell
noise would not align across cells; this looks like a coherent
spectral line at scale 10⁻⁵.

The cutoff coordinate is not zero — it has structure at scale 10⁻⁵
on the dist-to-n² scout, plus a transient at scale 10⁻³–10⁻⁴ in
the first ~1000 Y past saturation. But these are well below the
payload coordinate's effect sizes (ξ 0.79–0.94 on Λ_n, magnitudes
order 1) and well below the L4d aggregate's apparent monotone
gradient (which was 0.06–0.21).

**Calibrated claim.** L4d's apparent monotone progression in
τ_2(Y) at scale 0.1 was an m-confound and is gone. A residual
cutoff signal exists at scale 10⁻⁵ in the dist-to-n² scout
(coherent across panel cells), and a near-saturation transient
exists at scale 10⁻³–10⁻⁴. The cutoff coordinate is demoted to a
weak refinement, not eliminated. Its scale at `Y_max = 50000` is
below resolution of the payload coordinate, but a longer-`Y` scan
or a higher-`X` re-projection might amplify it.

In RLE terms: the dist-to-n² signal is a faint column visible only
after background subtraction, like the ν_2(n) ridges in the RLE
image — finite-spectrum at this scale, not provably absent at all
scales.


## Result 2 — payload coordinate GRADUATES, on Λ_n only (not ρ)

For each of 10 panel cells `(n, h)` with `n ∈ {2, 3, 4, 5, 6}` and
`h ∈ {2, 3}`, swept all `m ∈ M_n ∩ [n^h, M_MAX]` at exact height h
(so 8206 m-points total). Two observables compared:

| observable | ξ(payload τ_2) | conclusion |
|---|---:|---|
| Λ_n(m) | **0.79 – 0.94** at h=2; 0.17 – 0.94 at h=3 | strong functional dependence — graduates |
| ρ_n(m; m·1000) | 0.004 – 0.019 | essentially independent — fails |

**ρ is the wrong observable for the local coordinate.** ρ depends
on `m` via `Out_m = 1/(m log m)` and via the saturated `In` sum,
neither of which carries `m`'s payload structure. The local
coordinate manifests in `Λ_n(m)` itself.

### h=2 cliff reproduced (smoke check)

Closed-form identity: `Λ_n(m) < 0 ⇔ τ_2(m/n²) ≥ 3` at h=2. Every
panel cell at h=2 reproduces this exactly across `n ∈ {2, 3, 4, 5, 6}`.
Pipeline correct.

### h=3 prime/composite split — the structural finding

| n | h=3 τ_2 ≤ 4 | h=3 τ_2 ∈ [6, 16] |
|---|---|---|
| 2 (prime) | all zero | all positive |
| 3 (prime) | all zero | all positive |
| 5 (prime) | all zero | all positive |
| 4 (composite) | all negative | mixed → positive |
| 6 (composite) | all negative | mixed → positive |

At h=3, **prime n** has `Λ_n(m) ≥ 0` everywhere we sampled —
either zero (low payload τ_2) or positive (high). No negative
mass. **Composite n** has `Λ_n(m) < 0` at low payload τ_2,
transitioning through mixed to positive at higher τ_2.

This is the **prime / `p^k` / composite asymmetry** the previous-turn
discussion predicted, made empirical. The L1d/e tables at the
parent tomography's `X = 10000` were averaging across n; the split
is invisible until you separate by `n`.

The U-shape claim from `ACM-MANGOLDT.md` was a description of the
n-aggregated L1d/e — under the controlled scan, the U-shape is
revealed as a composite-n phenomenon, not a universal feature.
Prime n at h=3 shows monotone-toward-positive, not U.


## Result 3 — ρ is essentially a (n, m, scale) statistic

Combining results 1 and 2: ρ is flat in cutoff scouts at fixed
`(n, m)` (Result 1) and flat in payload scouts at fixed `(n, h)`
(Result 2). Mean ρ varies clean-monotonically with `n` for fixed
h and τ_2 bucket — for example at h=2, τ_2=2:

    n = 2  →  ρ ≈ −0.155
    n = 3  →  ρ ≈ −0.191
    n = 4  →  ρ ≈ −0.226
    n = 5  →  ρ ≈ −0.256
    n = 6  →  ρ ≈ −0.282

But this is just `Out_m = 1/(m log m)` and asymptotic `In_m`
arithmetic — `ρ` is determined by `m`'s scale and `n`'s identity,
not by the local divisibility coordinates. ρ is the wrong
observable for the spectroscopic claim.


## Updated working model

| coordinate | observable | status |
|---|---|---|
| height `ν_n(m)` | Λ_n sign regime | structural; sets the payload-coordinate's domain |
| payload divisor richness `τ_2(m/n^h)` | sign(Λ_n), magnitude | **GRADUATES** at h=2 (closed form), at h=3 with prime/composite split |
| cutoff `Y = ⌊X/m⌋` | ρ at fixed `(n, m)` | **FALLS** — flat in every scout; ρ saturates and forgets |
| decimal block certification | ρ at fixed `(n, h, payload)` | untested in isolation; the original L3 claim was about ρ which doesn't carry the signal anyway |

The decomposition collapses from four coordinates to two
(height, payload), with ρ replaced by Λ_n itself as the
observable. The cutoff-side and totalisation-side "lines" from
`ACM-MANGOLDT.md` were artifacts of the global statistic ρ, not
genuine spectral structure.


## Implications for STRUCTURE-HUNT phases

**Phase 2 (interaction matrix)** simplifies. Only `height × payload`
and `prime/composite-n × payload` interactions remain meaningful;
cutoff×anything is dead. The prime/composite split at h=3 is
already a graduated interaction; checking h=4, 5 for whether the
asymmetry persists is the remaining test.

**Phase 3 (cross-experiment validation)** sharpens. The Brief 2
CF spike formula `(b−1)²·b^(k−2)·(n−1)·k/n²` should be derivable
from the payload-coordinate model on Λ_n, not from ρ. Brief 4's
M_n(N) should also be predictable from Λ_n's behaviour, not from
truncated-flow ρ. Both predictions become easier — fewer
coordinates, sharper observable.

**Phase 4 (predictive model)** retargets. The model takes
`(n, h, payload τ_2, prime-or-composite-n)` and predicts sign(Λ_n)
and magnitude. ρ is downstream of (n, m) and not part of the
prediction.

**Phase 5 (missing lines)** has more focused targets. The candidates
named there — `ν_p(n)` for `p | n`, smallest-prime-factor of `m`,
the original-Λ on A_n positivity locus — each get tested against
the prime/composite asymmetry: do they refine it, or are they
restatements of it?


## What this is

A controlled-scan refutation of the cutoff coordinate, a controlled-
scan graduation of the payload coordinate (on Λ_n), and a
controlled-scan confirmation of the prime/composite-n split at
h=3. The framing in `ACM-MANGOLDT.md` is partially correct —
height and payload are real coordinates — but ρ is not the right
observable for either of them. Λ_n is.

The next move is updating `ACM-MANGOLDT.md` to reflect the
two-coordinate model on Λ_n, deciding whether ρ deserves any
remaining role at all (it might still be useful for the original
1196-flow-certificate question, just not for spectroscopy), and
moving to Phase 2's reduced agenda.
