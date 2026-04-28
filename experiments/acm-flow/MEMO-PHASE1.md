# Memo — Phase 1 status, calibrated

Date: 2026-04-28. Two controlled scans + three visualization passes
(bucket / spatial / residual-heatmap) on the four-coordinate
working hypothesis from `ACM-MANGOLDT.md`.


## What graduated

**Payload coordinate, observable = Λ_n(m).**

ξ(payload τ_2 → Λ_n) = 0.79–0.94 at h=2; varying at h=3 with a
clean prime/composite split:

- Prime n (2, 3, 5) at h=3: Λ_n ≥ 0 everywhere we sampled.
- Composite n (4, 6) at h=3: Λ_n < 0 at low payload τ_2,
  transitioning through mixed to positive at high τ_2.

The split is visually striking on the `nz_neg_frac` and
`neg_mass / abs_mass` panels of `payload_matrix.png`. The h=2
"cliff" (`τ_2(m/n²) ≥ 3 ⇒ Λ_n < 0`) is a closed-form identity
and reproduces in every cell — pipeline-correct.


## What was overstated and is now corrected

**ρ as the payload observable.** ξ(payload τ_2 → ρ) = 0.004–0.019.
ρ doesn't carry the payload signal. The four-coordinate model in
`ACM-MANGOLDT.md` framed ρ as the load-bearing observable; that
was wrong. Λ_n is the right observable.

**Cutoff coordinate at scale ~0.1.** The L4d aggregate "monotone
in τ_2(Y)" gradient (0.06–0.21) was an m-confound: at fixed
X = 10000, varying m made Y = ⌊X/m⌋ vary, sampling the early-
transient ρ ≈ 0 in low-τ_2(Y) buckets and the saturated ρ in
high-τ_2(Y) buckets. The gradient is gone at fixed (n, m).


## What survives at smaller scale (open)

Two residual signals surfaced by the residual-spectroscopy
heatmaps that the bucket-mean and ACF analyses missed:

**1. Dist-to-n² pattern at scale 10⁻⁵, cross-cell coherent.**
After row-background subtraction, every panel cell has the same
column pattern in the dist_n² scout: `dist=0` more negative than
row mean, `dist=2` less negative. Random per-cell noise would not
align across cells. Looks like a faint spectral line in the
residual.

**2. Near-saturation transient at scale 10⁻³–10⁻⁴.** Per-cell
heatmaps over (Y batch × τ_2(Y) bucket) show coherent bucket-
correlated structure in the first ~1000 Y past saturation, fading
by Y ≈ 5000.

Both are well below the payload coordinate's effect sizes (order
1). Whether they amplify at higher Y_max or higher X is open.


## Updated working model

Two coordinates, not four:

- **height ν_n(m)**: structural, sets the regime.
- **payload divisor richness τ_2(m/n^h)**: graduates on Λ_n.

ρ is downstream of (n, m) arithmetic and not a spectroscopic
observable for the local coordinate. The cutoff coordinate is
demoted to a weak refinement at scale 10⁻⁵, not eliminated.


## What's open going forward

- whether the dist-to-n² 10⁻⁵ line amplifies at longer Y;
- whether ρ retains a role in the original 1196-flow-certificate
  question (separate from spectroscopy);
- whether height × payload interactions, or the prime/composite
  split, persist at h ≥ 4;
- whether the same two-coordinate model on Λ_n predicts Brief 2's
  CF spike formula and Brief 4's M_n(N) shape.


## Files

| file | role |
|---|---|
| `cutoff_ray_scan.py` / `cutoff_ray_scan.csv` | controlled cutoff scan |
| `cutoff_ray_stripe.py` | stripe + fold visualizations |
| `cutoff_texture.py` / `cutoff_texture_summary.txt` | ACF + bucket-mean probe |
| `payload_scan.py` / `payload_scan.csv` | controlled payload scan |
| `flow_heatmaps.py` | residual-spectroscopy heatmaps |
| `PHASE1-RESULTS.md` | full write-up with the texture qualifications |
| `MEMO-PHASE1.md` | this memo |

`STRUCTURE-HUNT.md` Phases 2–5 should be reviewed against the
two-coordinate model before any are scheduled.
