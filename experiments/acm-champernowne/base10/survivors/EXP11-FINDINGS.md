# EXP11 — leading-digit projection of the K_pair lattice

EXP05 said the L1-gap triangles are NOT in κ but in the leading-digit
projection of the survivor set. With the closed-form lattice
(`LATTICE-CLOSED-FORM.md`) and EXP10's full-resolution render, we can
now ask: what is the projection mechanism, and which lattice features
map to which triangle features?

This memo records what unit-resolution computation reveals.

## Setup

For each `(K, n_0)` cell, define:

- `p_B(d)` = bundle leading-digit distribution (fraction of B(K, n_0)
  atoms with leading digit `d`, weighted by multiplicity).
- `p_S(d)` = survivor leading-digit distribution (over singletons).
- `p_C(d)` = culled-atom leading-digit distribution
            = `(bundle_ld − surv_ld) / N_C` (each multi-shared atom
            counted with its multiplicity).
- `u`     = uniform-9 = `(1/9, …, 1/9)`.
- `GAP`   = `|p_S − u|₁ − |p_B − u|₁` (the static endpoint of the
            l1_grid running quantity).
- `BE`    = Benford excess of culled atoms = `p_C[1] + p_C[2] + p_C[3]
            − p_C[7] − p_C[8] − p_C[9]`, **signed**: `+` ⇒ culled
            atoms heavy on small digits, `−` ⇒ heavy on large digits.

## Findings

### 1. Triangle structure survives unit resolution

The original `l1_grid` was at 10×10 cells. Computing GAP at unit
resolution over `n_0 ∈ [10, 300]`, `K ∈ [1, 300]` reproduces the
triangular fingers cleanly. They are not aliasing; they are real.

Range of GAP: `[−0.296, +0.412]`. Median `|GAP| = 0.010`. Fingers
are large-amplitude regions sticking out of a near-zero background.

### 2. The triangle SIGN is set by Benford direction of culled atoms

| metric | corr with GAP | reading |
|---|---|---|
| `|p_C − u|₁` (magnitude) | −0.35 | weak; magnitude alone doesn't determine sign |
| `|p_B − u|₁` (bundle non-uniformity) | −0.30 | weak; Benford-like bundle is the substrate |
| **`BE` (Benford excess of culled)** | **−0.40** | **strongest; directional** |
| `Λ_W` (lattice count) | +0.00 | as expected — gap is leading-digit, not multiplicity |

The negative BE-vs-GAP correlation is the mechanism: when culled
atoms are heavy on small digits (Benford-like, BE > 0), removing
them makes the survivor set LESS small-digit-heavy than the bundle,
hence MORE uniform — `|p_S − u|₁ < |p_B − u|₁`, GAP < 0. When culled
atoms are heavy on large digits (BE < 0), survivor is pushed
further from uniform, GAP > 0.

`Λ_W` correlation is essentially zero. This is the cleanest way to
say "the triangles are NOT in the lattice multiplicity": the lattice
counts events; the gap reflects the leading-digit signature of those
events.

### 3. Two extreme cells confirm the mechanism

- **Most positive GAP** at `n_0 = 23, K = 31`, `GAP = +0.412`. 77
  cumulative culled events. Leading-digit histogram:
  `[4, 5, 7, 8, 6, 15, 15, 12, 5]` (digits 1..9). 51% of events on
  digits 6, 7, 8 — large-digit-heavy. Removing them makes survivor
  more biased toward small digits, hence MORE non-uniform than bundle.

- **Most negative GAP** at `n_0 = 10, K = 17`, `GAP = −0.296`. 62
  cumulative culled events. Leading-digit histogram:
  `[33, 14, 3, 1, 0, 3, 2, 2, 4]`. 76% on digits 1, 2 — strongly
  Benford. Removing them makes survivor LESS Benford, hence MORE
  uniform than the (also Benford-like) bundle.

### 4. The Benford-excess heatmap is the visual explanation

`exp11_leading_digit_projection.png`, top-middle panel: signed
Benford excess of culled atoms. Most cells are orange (BE > 0,
culled is Benford), reflecting that lattice events on average produce
small-digit-heavy atoms (multiplicative Benford bias of `t·L`). The
purple bands where BE < 0 (culled atoms unusually large-digit-heavy)
correspond to the red GAP triangles. The map is not an exact inverse
of GAP — it is GAP minus the bundle's own bias — but the structural
correspondence is visually clear and quantitatively captured by
corr ≈ −0.40.

### 5. Which lattice features map to which triangle features?

Reference rays drawn on all panels:

- **`K = a` (slope-1 leading edge)** sits on the boundary between
  the central red triangle and the blue region above it. The slope-1
  band's strong activity around `K ≈ n_0` is where the "central
  triangle" structure starts.
- **`K = n_0 / 2` (slope-1/2 ray)** is the diagonal that traces the
  upper boundary of the second-largest red triangle (the one in
  `n_0 ∈ [50, 200], K ∈ [25, 100]`).
- **`K = n_0 / 3, n_0 / 4`** rays trace the boundaries of progressively
  smaller triangles below.

The **interiors** of the triangles are the cumulative effect of all
lattice events with `K_event ≤ K`, weighted by leading digit. The
**boundaries** are crossings where new lattice rays activate, shifting
the cumulative leading-digit distribution.

So the picture is:

> Lattice rays at slopes `1/d` deposit culled atoms in
> magnitude-bands `≈ n_0² / d`. As `n_0` varies, `log₁₀(n_0² / d)
> mod 1` sweeps leading digits. The gap heatmap is the
> superposition of these sweeps from `d = 1, 2, …, W − 1`. Each `d`
> contributes a sweep with period in `log n_0`; their interference
> gives the triangle interiors and ray-aligned boundaries.

This is the EXP05 "lens-induced clustering" picture made
quantitative: the lens is the leading-digit projection, and the
clustering is the lattice rays projecting magnitude-bands through
that lens.

## What this closes (and what it doesn't)

**Closed.** The original `l1_grid` triangle/finger heatmap is now
explained: at unit resolution, the gap is anti-correlated with the
Benford excess of culled atoms (`r ≈ −0.40`). The triangles align
qualitatively with the slope-`1/d` lattice rays. The mechanism
(magnitude bands of culled atoms sweeping leading digits as `n_0`
varies) is concrete and computable from the closed form.

**Not closed.** The correlation `r ≈ −0.40` is moderate, not tight.
A more refined predictor would account for:
- The bundle's own leading-digit bias (`p_B`) interacting with
  `p_C`: when both are biased the same way, removing duplicates of
  the bias direction makes survivor more uniform; when opposite,
  it amplifies non-uniformity.
- The W·K denominator: gap is normalized by N_S, which scales
  the effective contribution of each culled atom.

A tighter analytical formula for GAP in terms of `(p_B, p_C, N_S, N_B)`
would push correlation closer to 1. That's a follow-up if needed,
but the qualitative picture is in place.

## Files

- `exp11_leading_digit_projection.py` — compute script
- `exp11_leading_digit_projection.png` — six-panel figure (GAP,
  Benford excess of culled, lattice Λ, GAP overlay with rays,
  bundle L1, survivor L1)
- `exp11_static_gap.npz` — cache of all heatmaps
