# EXP12 — closed-form linear predictor for GAP

EXP11's signed Benford excess of culled atoms gave `corr(GAP, BE) =
−0.40` — captured the SIGN of the gap but not its magnitude. This
memo derives a tighter predictor from the L1-norm derivative
identity and shows it captures correlation `+0.87` with the same
ingredients.

## The identity

At each `(K, n_0)` cell, with `u = (1/9, …, 1/9)` and `v_B = p_B −
u`, `v_S = p_S − u`:

> `v_S = v_B + (N_C / N_S) · δ`,    where `δ = p_B − p_C`.

(Direct from `N_B p_B = N_S p_S + N_C p_C`.)

For the L1 norm, `d|x|/dx = sign(x)` componentwise, so

> `|x + ε|₁ ≈ |x|₁ + ⟨sign(x), ε⟩` &nbsp;&nbsp; (small `ε`, no sign flips).

Apply with `x = v_B`, `ε = (N_C/N_S) δ`:

> **`GAP_LIN := (N_C / N_S) · ⟨sign(v_B), δ⟩`**
> &nbsp;&nbsp;&nbsp;`= (N_C / N_S) · Σ_d sign(p_B[d] − 1/9) · (p_B[d] − p_C[d])`.

This is a closed-form scalar predictor of `GAP = |v_S|₁ − |v_B|₁`,
linear in `δ` and in the `N_C/N_S` scaling.

## Predictor performance

Over `n_0 ∈ [10, 300]`, `K ∈ [1, 300]`, `W = 10` (80,515 valid cells):

| predictor | description | corr with GAP |
|---|---|---|
| `BE` (EXP11) | `p_C[1-3] − p_C[7-9]` | `−0.40` |
| `|v_B|₁` | bundle non-uniformity (1 number) | `−0.33` |
| **`GAP_LIN`** | **(N_C/N_S) ⟨sign v_B, δ⟩** | **`+0.87`** |
| `GAP_RECON` | `|v_B + (N_C/N_S)δ|₁ − |v_B|₁` (no approximation) | `+1.000` |

The reconstruction is `+1.000` by construction (it is the full
formula); listed as a sanity check that the identity is implemented
correctly. The substantive result is the linear predictor: `+0.87`,
roughly halving the unexplained variance from `1 − 0.40² = 0.84` to
`1 − 0.87² = 0.24`.

A naive least-squares fit `GAP ≈ a·BE + b·|v_B|₁ + c` achieves only
`R² = 0.16`. The linear predictor's `R² = 0.75` (= 0.87²) is much
larger because it uses the full 9-vectors `(p_B, p_C)`, not their
1-number summaries — the directional information matters.

## Why the linear predictor works

`GAP_LIN` factors as

> `GAP_LIN = (N_C / N_S) · [⟨sign(v_B), p_B⟩ − ⟨sign(v_B), p_C⟩]`.

The first inner product depends only on the bundle: for Benford-like
`p_B`, `sign(v_B) ≈ (+, +, +, −, −, −, −, −, −)` (over-uniform on
small digits, under-uniform on large), and `⟨sign(v_B), p_B⟩` is the
"signed bundle excess" `≈ A_+ − A_-` where `A_±` are bundle masses
on over- and under-uniform digits.

The second inner product `⟨sign(v_B), p_C⟩` is the projection of the
culled-atom distribution onto the bundle's sign pattern. This is a
**direction-aware Benford excess**: instead of the fixed mask
`[+,+,+,0,0,0,−,−,−]` of EXP11's BE, it uses the bundle's actual
sign pattern (which can shift cell-by-cell). That alone improves the
correlation; the `N_C/N_S` scaling further amplifies it where many
atoms are culled.

## Where the linear predictor fails

The remaining `0.13` correlation gap (`1.00 − 0.87`) comes from
sign-flip events: cells where `(N_C/N_S) δ_d` is large enough to
flip the sign of some `v_B[d]` component. The L1 norm has a kink at
zero, and the linear approximation overestimates the perturbation
across a sign flip.

The residual heatmap `GAP − GAP_LIN` (figure, bottom-right) localizes
the breakdown to:
- The **slope-1 band region** (where `K` is close to `n_0` and
  `N_C/N_S` is largest from heavy `r = 1` family activity).
- **Small-K cells** where `N_S` is small and the relative scale
  `N_C/N_S` is large.

Residual scale is `±0.056`, vs the original GAP scale `±0.41` — the
linear predictor captures the dominant structure cleanly, with
residuals concentrated in physically interpretable regions.

## A closed-form expression for GAP using only (p_B, p_C, N_C, N_S)

Combining the identity and the linear approximation:

> `GAP(K, n_0) ≈ (N_C / N_S) · ⟨sign(p_B − u), p_B − p_C⟩`

with the exact value being `|p_B − u + (N_C/N_S)(p_B − p_C)|₁ − |p_B
− u|₁`. Both forms use only the four cell-local quantities
`(p_B, p_C, N_C, N_S)`. The lattice contributes through `p_C` and
`N_C`: `p_C` is the leading-digit distribution of culled atoms
(controlled by which `t·L` magnitudes have been hit by step `K`),
and `N_C` is the cumulative deficit (= the K_pair-lattice's
running count, exactly `Δ(K, n_0)` from `LATTICE-CLOSED-FORM.md
§5`).

So the gap heatmap is a closed-form function of:
1. The K_pair lattice (gives `N_C` exactly, `p_C` up to multi-share
   correction).
2. The bundle's leading-digit distribution `p_B` (a smooth
   Benford-like function of the magnitude range
   `[n_0, K·(n_0 + W − 1)]`).

Both are computable without an empirical walk.

## What this closes

EXP05 said gap-triangles are a leading-digit projection of κ.
EXP10 gave the lattice in closed form. EXP11 explained the SIGN of
the gap. **EXP12 gives a quantitative predictor** at `r = +0.87`,
with the residual structure traced to a known approximation
(L1-norm sign-flip kink). The remaining open direction would be a
sign-flip-aware correction, which would be exact by construction
but no longer a simple closed-form scalar — at that point one is
just computing `|v_S|₁` from the 9-vector directly.

## Files

- `exp12_gap_predictor.py` — compute and compare predictors
- `exp12_gap_predictor.png` — six-panel figure (three scatters
  on top: BE, |v_B|₁, linear; three heatmaps on bottom: GAP,
  GAP_LIN, residual)
