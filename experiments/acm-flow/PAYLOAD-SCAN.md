# PAYLOAD-SCAN — controlled scan of the local coordinate

The matched-association finding in L1d/e of `ACM-MANGOLDT.md` —
that payload divisor richness `τ_2(m/n^h)` reverses the sign of
`Λ_n` predictably at h ≥ 3 (beyond what the h=2 closed form
forces) — is at the level of "survives matching." This brief
turns it into a controlled-source measurement.


## The control

Fix `n` and a `Y`-witness bucket. Vary `m` across payloads with
different `τ_2(m/n^h)` while keeping the *cutoff environment*
held still by choosing `X` such that `⌊X/m⌋` lands in the same
target `Y`-bucket.

Concretely:

- pick a target witness-count or `τ_2(Y)` bucket,
- for each `m` in the payload sweep, choose `X_m` such that
  `Y_m = ⌊X_m/m⌋` falls in the target bucket,
- compute `ρ_n(m; X_m) = Δ'_n(m; X_m) / Out_n(m)`.

`Y` is held in a controlled bucket; `m` and its payload `τ_2(m/n^h)`
are the swept variables. So `ρ_n(m; X_m)` reads the local
coordinate, with the truncation coordinate held in a known
neighbourhood.


## What we sweep

For fixed `n` and target Y-bucket:

| payload axis | range |
|---|---|
| height `h` | 2, 3 |
| `τ_2(m/n^h)` | 1, 2, 3, 4–5, 6–8, 9–16, 17+ |
| `m`-block type | smooth, uncertified |
| sign of Λ_n | recorded per (m, X_m) |

For each combination, sample multiple `m` values to get bucket
sample size ≥ ~10. Aggregate `ρ` per `τ_2(m/n^h)` bucket.


## Cutoff target panel

The scan needs a small controlled panel of `(n, Y-bucket)` points:

| panel cell | scout target |
|---|---|
| `n=2`, low `τ_2(Y)` | `τ_2(Y) ∈ {1, 2}` (sparse Y) |
| `n=2`, mid `τ_2(Y)` | `τ_2(Y) ∈ {3–5}` |
| `n=2`, high `τ_2(Y)` | `τ_2(Y) ≥ 6` (witness-rich Y) |
| `n=3`, mid `τ_2(Y)` | matched to n=2 |
| `n=5`, mid `τ_2(Y)` | matched, smooth m-block |
| prime n vs composite n | `n=5` vs `n=6` at same Y bucket |

Five to eight `(n, Y-bucket)` points. Each gets its own `m` sweep
across the payload axes; tables are rolled up per panel cell.


## Picking X_m

For each `m`, find an `X_m` such that `Y_m = ⌊X_m/m⌋` lands in
the target Y-bucket. Constraints:

- `Y_m` falls in the target witness-count or `τ_2` bucket.
- `Y_m ≥ Y_min` (some lower bound, say `n²`, to keep the Mertens
  approximation valid).
- `X_m ≤ X_max` (to keep `Λ_n` precompute bounded).

If multiple `Y_m` candidates exist, take the smallest, or sample
several and average. Document the `Y_m` chosen for each `m` in
the output CSV — readers need to know whether a `ρ` reading was
at a generic `Y_m` or one with peculiar structure.


## Outcome rules

The provisional pattern from the L1d/e tables in
`ACM-MANGOLDT.md`, at h ≥ 3, is **U-shaped**, not monotone:

    payload τ_2 ≤ 4               → sign(Λ_n) negative-heavy
    payload τ_2 ∈ [5, 16]          → sign(Λ_n) positive-dominated
    payload τ_2 ≥ 17 + diag/prime
    disagreement                   → sign(Λ_n) negative-heavy again

The graduation criterion below tests the U-shape, not monotonicity.
A monotone `ρ` or sign-fraction would be a clean falsifier of the
shape hypothesis, even if the *direction* of the trend looks
"explanatory" — the L1d/e non-monotonicity is part of what's being
tested, not noise to average away.

The local coordinate **graduates** from "matched association" to
"controlled local observable" if, at fixed `(n, Y-bucket)`, the
controlled scan reproduces the U-shape:

- the sign-fraction of `Λ_n` is negative-heavy at low payload τ_2
  (≤ 4), flips positive-dominated through the middle (5–16), and
  re-flips negative at high τ_2 (≥ 17) + disagreement — same bucket
  boundaries as L1d/e, at h=3;
- mean `ρ` is non-flat in `τ_2(m/n^h)` and tracks the sign-fraction
  shape (its specific form is not prescribed beyond "varies in
  step with sign"; what matters is that payload τ_2 moves ρ at
  fixed Y-environment);
- the prime-n vs composite-n split persists at matched Y-bucket
  (a height-3 reversal that depends on whether `n` itself is
  prime or composite is the kind of structural fact the previous
  turn pointed at).

The coordinate **falls** if any of:

- the U-shape collapses to monotone, scrambles, or flattens at
  fixed Y-bucket — then the L1d/e pattern was carried by
  Y-correlations, not by payload structure per se;
- mean `ρ` is flat in payload τ_2 at fixed Y-bucket;
- the prime-n / composite-n split disappears at matched Y-bucket
  — then it was a confound from prime-n having different cutoff
  distributions than composite-n.

The middle-vs-tail location of the U-shape's minimum is itself
a finding to record, not a fitting parameter — if controlled
scans push the positive plateau or the high-τ_2 reflip to
different bucket boundaries than L1d/e suggests, that's
information about whether the boundaries are scout artefacts or
genuine.


## What we explicitly do not test here

The h=2 closed-form cliff (`τ_2(m/n²) ≤ 2 → no negative;
τ_2(m/n²) ≥ 3 → all negative`) is an analytic identity, not an
empirical claim. The scan does not "test" it; it should reproduce
it exactly. Reproducing the cliff is the smoke check. Failure to
reproduce it means the implementation is wrong.

The empirical content lives at h ≥ 3.


## Reporting discipline

For every `τ_2(m/n^h)` bucket in every panel cell, report:

- mean `ρ`
- median `ρ`
- sign-fraction (count of `ρ < 0`)
- sign-fraction of `Λ_n(m)` (separate from `ρ` sign)
- bucket count
- the `Y_m` distribution (so the reader can verify the target
  bucket was actually hit)

Flag any bucket where mean and median diverge.


## Files (planned)

| file | role |
|---|---|
| `payload_scan.py` | per-panel-cell m-sweep at fixed Y-bucket |
| `payload_scan.csv` | `(n, m, h, payload τ_2, X_m, Y_m, ρ, sign Λ)` |
| `payload_scan_summary.txt` | per panel cell, ρ tables across payload τ_2 buckets |
| `payload_scan_panel.png` | one figure per panel cell, ρ and sign(Λ) vs payload τ_2 |


## Coupling

- **`ACM-MANGOLDT.md`** — Tier 1 source statement (payload-side).
- **`core/BLOCK-UNIFORMITY.md`** — for the m-block classification.
- **`experiments/acm/diagonal/cheapest_sieve/README.md`** — for
  scout definitions used in the Y-bucket targeting.


## What this is not

- Not the cutoff scan. That's `CUTOFF-SCAN.md`. The two are
  duals: this fixes the cutoff Y-bucket and varies m and its
  payload; the other fixes m and sweeps Y.
- Not a re-aggregation of L1d/e from the `X=10000` tomography
  rows, where there is no control over which `Y`-bucket each `m`
  lands in. This forces `Y` into a target bucket and varies `m`
  within it.
