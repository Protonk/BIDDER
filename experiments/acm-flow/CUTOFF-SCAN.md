# CUTOFF-SCAN — controlled scan of the truncation coordinate

The matched-association finding in L4d of `ACM-MANGOLDT.md` —
that `ρ = Δ'/Out` factorises monotonically through `τ_2(Y)` with
a consistent smooth-vs-uncertified offset — is at the level of
"survives matching." This brief turns it into a controlled-source
measurement.


## The control

Fix `(n, m)`. Choose `X = m·Y` for a sweep of `Y`. Then

    ⌊X / m⌋  =  Y    exactly,

so the truncation cutoff is `Y` by construction; `Y` is the
controlled variable, not a confound. Compute

    ρ_n(m; mY)  =  Δ'_n(m; mY) / Out_n(m).

`Out_n(m)` is fixed across the sweep; `Δ'_n(m; mY)` varies with
the inflow tail at cutoff `Y`. So `ρ_n(m; mY)` reads the
truncation coordinate directly, with `m` and `n` held still.


## What we sweep

For each fixed `(n, m)`:

| Y bucket | scout |
|---|---|
| witness count | `# {(k, Y/k) : k≥2, k<√Y, k|Y}` |
| smallest prime factor | `spf(Y)` |
| square / non-square | `Y == isqrt(Y)²` |
| distance to nearest multiple of `n²` | `min(Y mod n², n² − (Y mod n²))` |
| distance to nearest multiple of `n³` | analogous |
| diag/prime-row witness disagreement | from the cheapest-sieve scout |

Bucket `Y` over the sweep, aggregate `ρ` per bucket.


## Payload panel

The scan needs a small controlled panel of `(n, m)` covering
the Tier-1 cells we want to probe:

| panel cell | n | m examples |
|---|---|---|
| height 2, `τ_2(m/n²) ≤ 2` | 2, 3, 5 | `m = n²·1` (h=2 atom-square), `n²·p` (h=2 prime-payload) |
| height 2, `τ_2(m/n²) = 3–5` | 2, 3, 5 | `m = n²·k` with `τ_2(k) ∈ [3, 5]` |
| height 2, `τ_2(m/n²)` high | 2, 3, 5 | `m = n²·k` with `τ_2(k) ≥ 6` |
| height 3, payload τ_2 middle | 2, 3 | `m = n³·k` with `τ_2(k) ∈ [3, 8]` |
| prime n vs composite n | 2 vs 4, 5 vs 6, 5 vs 10 | matched payload τ_2 |
| smooth m-block vs uncertified m-block | 2, 5, 10 vs 3, 6 | matched height |

Six to twelve `(n, m)` points total. Each point gets its own
`Y`-sweep; tables are rolled up per panel cell.


## Sweep range for Y

`Y` from a small lower bound (say `Y_min = n²`) up to a large
upper bound (`Y_max = 10^6` or more — `Y` is a single integer
sweep, no precision concerns). For each `Y` in the range:

    X = m · Y,
    Δ'_n(m; X) = In_n(m; X) − Out_n(m) + 1/(m log X),
    ρ_n(m; mY) = Δ'_n(m; mY) / Out_n(m).

`In_n(m; mY) = Σ_{q ∈ M_n, q ≤ Y} Λ_n(q) / (mq · log²(mq))`,
which only needs `Λ_n(q)` for `q ≤ Y_max`. Pre-compute `Λ_n` once
on `[1, Y_max]` and reuse across all panel points.


## Outcome rules

The L4d monotone-in-`τ_2(Y)` progression is a *bucket-aggregate*
observation over many `m`. At fixed `(n, m)`, the per-cell shape
is open. Plausible shapes: monotone tracking, sieve-ray oscillation
(`ρ` spikes near `Y` ≈ multiples of `n²`, `n³`, …), a U-shape
analogous to the payload coordinate, or a hybrid. The graduation
criterion below tests for *systematic dependence*, not for any
specific shape.

The cutoff coordinate **graduates** from "matched association" to
"controlled cutoff observable" if the fixed-point sweeps show:

- at fixed `(n, m)`, `ρ` exhibits a *reproducible non-flat* shape
  in `τ_2(Y)` — any consistent shape counts (monotone, sieve-ray
  oscillation, U-shape, or hybrid), provided the shape repeats
  across panel cells in the same `(n, m)`-class;
- the smooth-vs-uncertified `m`-block split is detectable across
  matched panel cells and `τ_2(Y)` buckets, even if its magnitude
  varies (the L4d gap *grows* with `τ_2(Y)`, ≈ 0.06 at low to
  ≈ 0.21 at mid before saturating; magnitude is itself an
  observable);
- the ranking of scouts by **Chatterjee's ξ** at fixed `(n, m)`
  is stable across panel cells and `n`. ξ is shape-agnostic
  (detects U-shape, oscillation, monotone alike, with `ξ = 0`
  iff independence and `ξ = 1` iff functional dependence), so
  non-monotone per-cell shapes do not get mis-ranked as
  no-signal — which OLS R² of a continuous fit would do. See
  the statistical-method-discipline section in `ACM-MANGOLDT.md`.

The coordinate **falls** if:

- at fixed `(n, m)`, `ρ` is flat in `τ_2(Y)` — then L4d's
  monotonicity was a confound between `m`-properties and
  `Y`-properties, not a genuine cutoff effect;
- the per-cell shape is *non-reproducible* across panel cells of
  the same `(n, m)`-class — then `Y` carries information but it's
  noise-dominated at this `X`-scale and the controlled scan
  doesn't have the resolution to graduate the coordinate;
- the smooth offset disappears across matched smooth/uncertified
  panel cells — then the L3 totalisation result was a between-`m`
  artifact, not a per-cutoff property.

Either outcome is informative. Graduation promotes the truncation
coordinate to first-class. Falling tells us the ranking in
`ACM-MANGOLDT.md` was wrong, or the resolution at this `X`-scale
isn't enough.

A brief note on shape: this scan does not prescribe what shape `ρ`
takes at fixed `(n, m)`. If panel cells disagree on shape, that is
itself a finding — different `(n, m)` regimes may have different
per-cell shapes, and the aggregate L4d monotone is then a marginal
over heterogeneous per-cell behaviour. Report shapes observed; do
not bin to a pre-specified form.


## Refinement target

The diag/prime-row disagreement scout currently sits in Tier 3.
The cleanest test of whether it carries information beyond
witness count is *inside the witness-rich `Y` buckets at fixed
`(n, m)`*. If at matched witness count, disagreement explains an
additional residual signal, the scout earns Tier 2. If not, it
stays demoted.


## Reporting discipline

For every `Y`-bucket in every panel cell, report:

- mean `ρ`
- median `ρ`
- sign-fraction (count of `ρ < 0`)
- bucket count

Flag any bucket where mean and median diverge. The cutoff scan
generates dense per-`Y` data; the high-leverage-tail risk is
real, and matched buckets must be read for bulk vs tail.


## Files (planned)

| file | role |
|---|---|
| `cutoff_ray_scan.py` | per-panel-cell Y-sweep, per-scout aggregation |
| `cutoff_ray_scan.csv` | `(n, m, Y, ρ, scout features…)` |
| `cutoff_ray_summary.txt` | per panel cell, ρ tables across Y buckets |
| `cutoff_ray_panel.png` | one figure per panel cell, ρ vs scout |


## Coupling

- **`ACM-MANGOLDT.md`** — Tier 1 source statement.
- **`core/BLOCK-UNIFORMITY.md`** — for the m-block classification.
- **`experiments/acm/diagonal/cheapest_sieve/README.md`** — for
  scout definitions (witness count, diagonal/prime-row).


## What this is not

- Not the payload scan. That's `PAYLOAD-SCAN.md`. The two are
  duals: this fixes m and varies cutoff; the other fixes cutoff
  bucket and varies m.
- Not a re-aggregation of L4. L4 is `(m, X = 10000)` for
  many `m` with `Y = ⌊X/m⌋` correlated to `m`. This is
  `(m fixed, Y swept)` with `Y` independent of `m`.
