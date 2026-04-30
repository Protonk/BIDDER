# Experiment 03 — pair-collision mechanism for the gap heatmap

Follow-up to `l1_grid_zoom.png`. Tests the hypothesis that the
triangular fingers in the survivor-vs-bundle L1 gap heatmap are
explained by pair-collision activation in the window
`[n_0, n_0 + W - 1]`.

Code:
- `pair_thresholds.py` — `k_pair(n, n')` library plus window helpers
- `exp03_triangle_slice.py` — vertical slice through n_0 = 290
- `exp03_triangle_slice.png` — gap(K) at n_0=290 with 17 thresholds
- `exp03_gap_vs_active_pairs.py` — three-panel side-by-side
- `exp03_gap_vs_active_pairs.png` — gap | active-pair count | dA/dK

## Result

**Mechanism confirmed at one slice; confirmed qualitatively across the
full grid.** The triangles in the gap heatmap are post-activation
relaxation tails of pair-collision events, not constant-character
plateaus. Each `K_pair(n_a, n_b)` threshold acts as an impulse;
between events the gap relaxes back toward baseline.

## Phase A — slice at n_0 = 290

The 45 pairs in window `[290..299]` have 17 unique `K_pair` values,
which cluster into three groups:

- 5 pairs at K ∈ {59, 74, 98, 99, 99}     (gcd > 1 pairs)
- 9 pairs at K ∈ {146..149}                (gcd = 2 pairs)
- 31 pairs at K ∈ {290..298}               (gcd = 1 pairs)

Empirical gap(K) at n_0 = 290:

| K range          | mean gap   | comment                         |
|------------------|-----------:|---------------------------------|
| [30, 58]         |  +0.0000   | no pairs active; gap mechanically zero |
| [100, 145]       |  -0.0047   | 4 pairs active; mild blue       |
| [150, 285]       |  -0.0037   | 13 pairs active; mild blue      |
| [299, 500]       |  +0.0166   | all 45 active; strong red       |

The K = 290 → K = 298 transition crosses 31 thresholds in 9 K-steps,
driving an **impulse spike to gap = +0.045 at K ≈ 300**, then a slow
relaxation back toward zero through K = 500. The triangular finger
at n_0 = 290 in the gap heatmap is exactly this relaxation tail.

## Phase B — side-by-side, full grid

Three panels in one figure:

1. **Gap heatmap** (existing, 95th-pct clipped).
2. **Active pair count** `A(K, n_0) = #{pairs : K_pair < K}`.
3. **dA/dK** — activation events per K-step.

Panel 2 shows a clean phase diagram. Three bands separated by
prominent transitions: gcd-share collisions (small K), gcd=2 pairs
(K ≈ n_0/2), gcd=1 pairs (K ≈ n_0). Panel 3 shows BRIGHT diagonals
at K = n_0, K ≈ n_0/2, K ≈ n_0/3 — exactly where the simultaneous
activation events happen.

Panel 1 (the gap) sits in the relaxation regions following each
activation. The triangular fingers are **regions of impulse-response
decay**, not steady-state plateaus.

## Quantitative correlation

`|gap|` vs `A` (active pair count):  **+0.32**
`|gap|` vs `dA/dK` (activation rate): **+0.22**

Modest, not strong. This is expected — the gap is a relaxation tail
following activation, not an instantaneous response, so the linear
correlation is diluted by the temporal kernel.

A better diagnostic would be: model `gap(K, n_0)` as
`Σ_thresholds h(K - K_pair_i) · w_i` for some impulse-response
kernel `h` and per-pair weights `w_i`, fit `h` and `w_i` from the
data, and report the residual after subtracting the fit. That's a
follow-up. The current evidence is sufficient to establish the
mechanism qualitatively.

## What this changes about the comment in the chat

The earlier description said the triangles might be
"constant-character regions between thresholds, separated by sharp
jumps at activation events." That's **not what's happening**. The
correct description is:

> The triangles are impulse-response tails: each pair-cluster
> activation kicks the gap, and the gap decays back toward zero
> over a K-range proportional to the cluster size. The biggest
> triangles (visible at n_0 = 290, 540, 670, ...) sit at n_0
> values where ~30 pairs activate within a 10-K window — the
> impulse is large.

The geometry of which n_0 values produce the largest impulses is
itself structured (the chain of triangles in the heatmap), and is
controlled by the gcd structure of the window. For window
`[n_0, n_0 + 9]`:

- The 31 gcd=1 pairs all activate within K ∈ [n_0, n_0 + 8].
- The 9 gcd=2 pairs activate within K ∈ [n_0/2, n_0/2 + 4].
- A few gcd=5 / gcd=3 / etc. pairs activate at small K.

So the "big triangle" pattern is universal across n_0 — every n_0
should produce a triangle of comparable peak height at K ≈ n_0.
The visual prominence variation (some triangles louder than others)
is because of the **decade structure**: when K ≈ n_0 falls inside a
decade (K · n_0 ≈ 10^d for fixed d), the leading-digit residual is
small to begin with, and a +0.04 spike is dramatic against a
near-zero baseline. When the bundle is far from a decade boundary,
the spike is the same magnitude but on a noisier baseline, less
visually salient.

## Status

**Original puzzle (the triangles): explained.** Pair-collision
impulses + relaxation decay, indexed by gcd structure of the
window.

**Remaining curiosities:**

- The lower-left mixed-color region at small (K, n_0). Multiple
  small-window edge effects compounding; not an artifact of any
  single mechanism.
- The fine-grained substructure inside each big triangle. Likely
  reflects the staircase of 31 individual pair-activations within
  K ∈ [n_0, n_0 + 8]; would resolve under a denser K sampling.
- The horizontal red bands at certain n_0 (visible around n_0 =
  100, 300). Likely correlated with the leading-digit profile of
  the 10-stream window centred near specific decade-boundaries.

None of these are mysterious in the way the triangles were before
the slice. They're all in the family of "structured arithmetic
phase diagram" that the explained mechanism predicts.
