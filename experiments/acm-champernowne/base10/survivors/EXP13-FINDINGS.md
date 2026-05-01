# EXP13 — exact GAP decomposition with closed-form residue

EXP12 found a linear predictor matching `87%` of GAP variance and
identified the leftover as L1-norm sign-flip residue. Here we close
the loop with an exact, per-digit-explicit decomposition that holds
to machine precision.

## The exact identity

For each `(K, n_0)` cell, with the EXP12 setup
(`v_B = p_B − u`, `v_S = p_S − u`, `δ = p_B − p_C`, `ε = (N_C/N_S)·δ`):

> **`GAP  =  GAP_LIN  +  R_TOTAL`**

where

> `GAP_LIN  =  (N_C / N_S) · Σ_d sign(v_B[d]) · (p_B[d] − p_C[d])`

> `R_TOTAL  =  Σ_d (1 − sign(v_B[d]) · sign(v_S[d])) · |v_S[d]|`

with `sign(0) = 0` (any consistent convention).

Per-digit residue:

| case | condition | `R_d` |
|---|---|---|
| linear regime | `v_B[d]·v_S[d] > 0` (same sign, both nonzero) | `0` |
| sign flip | `v_B[d]·v_S[d] < 0` (strictly opposite signs) | `2·|v_S[d]|` |
| boundary in | `v_B[d] = 0`, `v_S[d] ≠ 0` (uniform digit gets perturbed) | `|v_S[d]|` |
| boundary out | `v_S[d] = 0` (perturbation lands on uniform) | `0` |

This is a closed-form scalar per cell, derived by component-wise
casework on the L1 norm `|x|₁ = Σ_d |x_d|` and its left/right
derivative at `x_d = 0`.

## Verification

`exp13_gap_exact_residue.py` computes both sides at unit resolution
over `n_0 ∈ [10, 300]`, `K ∈ [1, 300]`, `W = 10`:

> **`max |GAP − (GAP_LIN + R_TOTAL)| = 4.28 × 10⁻¹⁶`** (machine ε).

Identity verified across all 80,515 valid cells.

## What R_TOTAL looks like

Statistics over the grid:

| metric | value |
|---|---|
| range | `[0, 0.315]` |
| median `|R_TOTAL|` | `0.000` (most cells in the linear regime) |
| fraction of cells with `R_TOTAL > 0` | `10.99%` |
| `R_TOTAL > 0` lives on | structured lattice-aligned curves (figure top-right) |

Compare to `|GAP|`: median `0.011`, range `[−0.296, +0.412]`. So in
89% of cells, `GAP = GAP_LIN` exactly. In the remaining 11%, the
residue is concentrated on identifiable curves in the `(K, n_0)`
plane.

## Flip count distribution

`R_TOTAL` is structured by the number of digits whose `(v_B, v_S)`
sign-pair flips:

| # digits flipped | cells | % of grid |
|---|---|---|
| 0 | 71,821 | 89.20% |
| 1 |  6,095 |  7.57% |
| 2 |  1,424 |  1.77% |
| 3 |    711 |  0.88% |
| 4 |    342 |  0.42% |
| 5 |     79 |  0.10% |
| 6 |     37 |  0.05% |
| 7 |      6 |  0.01% |

Multi-digit flips happen at "phase transitions" where the
collision perturbation simultaneously flips several digits — these
are cells with high `N_C / N_S` (heavy culling) and `δ` aligned
with several near-zero `v_B[d]` components.

## Per-digit residue

Sum of `R_d` across the entire grid, by digit:

| digit `d` | total `Σ R_d` |
|---|---|
| 1 |  2.61 |
| 2 | 37.01 |
| 3 | 46.91 |
| 4 | 48.35 |
| 5 | **52.04** |
| 6 | 45.11 |
| 7 | 32.87 |
| 8 | 16.23 |
| 9 |  4.12 |

Middle digits (4, 5, 6) contribute the most: the Benford-like bundle
has `|v_B[d]|` smallest near digit 5 (where `p_B[d] ≈ 1/9`), so the
collision perturbation most easily crosses zero there. Extreme
digits (1 and 9) have large `|v_B|` and are nearly never flipped.

This matches the geometric intuition: residue concentrates where
`|v_B[d]|` is smallest, because the collision perturbation
`(N_C/N_S) δ_d` needs only modest magnitude to flip `v_B[d]`'s
sign there.

## Structure of the flip set

The residue heatmap (figure, top-right) shows `R_TOTAL > 0` on a
sparse set of CURVES, not diffuse noise. Each curve is the locus

> `Curve_d := { (K, n_0) : (N_C/N_S) · |δ_d| ≈ |v_B[d]| }`,

i.e., where the per-digit perturbation magnitude crosses the
per-digit bundle deviation magnitude. As `K` grows along a fixed
`n_0`-row, `(N_C/N_S)` grows monotonically (more atoms culled,
fewer survivors); `|δ_d|` and `|v_B[d]|` evolve more slowly. So
the crossing is a single line per digit per `n_0`, and the union
over `d` is `Curve_d` for `d = 1, …, 9` — a fan-like structure
visible in the figure.

The middle-row's "# digits flipped" panel quantifies this directly:
flip events cluster on these curves, with multi-digit flip cells
at curve intersections.

## Closing line

The L1-gap heatmap is now decomposed into:

1. A linear closed-form term `GAP_LIN` capturing the dominant
   (87%-correlation, 89%-of-cells-exact) structure.

2. A residue `R_TOTAL` that is **exactly closed-form per digit**,
   nonzero only on a sparse, structurally identifiable
   sign-flip set, with explicit per-digit and per-cell descriptions.

`GAP = GAP_LIN + R_TOTAL` to machine precision. No empirical walk
involved beyond computing `(p_B, p_C, N_C, N_S)`, all of which are
derivable from the K_pair lattice (`N_C = Δ` exactly; `p_C` from
the (pair, t) lattice events with the multi-share corrections of
`LATTICE-CLOSED-FORM.md §3`).

The remaining "residual" in the figure's middle-left panel
(`|GAP − (GAP_LIN + R_TOTAL)|`) is `4.28 × 10⁻¹⁶` — pure
floating-point error.

## Files

- `exp13_gap_exact_residue.py` — computes decomposition, verifies
  identity, plots all components.
- `exp13_gap_exact_residue.png` — 9-panel figure: top row
  (GAP, GAP_LIN, R_TOTAL); middle row (identity check, flip
  count, lattice reference); bottom row (per-digit residue for
  digits 3, 5, 7).
- `exp13_decomposition.npz` — cached arrays.
