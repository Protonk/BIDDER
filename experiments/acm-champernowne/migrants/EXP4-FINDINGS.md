# Experiment 4 — placement destroyer (migrant #7), findings

`placement_destroyer.py` ran (10.8 s on the 100 × 100 grid).
The destroyer preserves the per-cell multiset of duplicate leading
digits and randomly permutes which duplicate unique atom gets which
digit. Compared head-to-head against the full Benford-randomised
destroyer from `synthesis.py`.


## Numbers

```
metric             shuffled    destroyed
Spearman ρ          +0.9030      −0.3183
Pearson  r          +0.8601      +0.0035
sign agreement       95.4 %       29.5 %
MAE / mean|G|        31.5 %      294.5 %
```

The shuffle preserves **95.4 %** of the sign structure (vs `29.5 %`
for the full destroy), retains **86 %** linear correlation, and has
MAE roughly **9× smaller** than the full destroyer's. This lands
the verdict cleanly in the *intermediate* regime (between the < 20 %
"distribution-coupling" threshold and the > 50 %
"placement-coupling" threshold pre-set in the script).


## Three-layer decomposition

The result splits the cross-cut into three quantitative layers:

1. **Bin 1 (collision lattice)** — determines support exactly and
   row-level magnitude at ρ = +0.90 (`EXP3-FINDINGS.md`).
2. **Bin 2, distribution layer (per-cell multiset of duplicate
   leading digits)** — carries most of the signed structure of `G`.
   Preserving the multiset preserves 95 % of signs and 86 % of the
   linear signal. *This is the biggest single contributor.*
3. **Bin 2, placement layer (which specific atom gets which digit)**
   — a non-trivial residual, ~30 % MAE relative to mean `|G|`.
   Visible in `placement_destroyer.png` panel 3 as concentrated
   brightness in the low-K active wedge where the lattice is densest
   and the multiset is small (so permuting it has the biggest
   per-cell effect).

So the migrant's "bin-1 × bin-2" framing is now resolved at higher
resolution: bin 2 itself splits into a distribution component
(dominant) and a placement component (residual).


## What the figure shows

`placement_destroyer.png`:

- **Panel 1 — `G` observed**: full structure with diagonals,
  triangles, horizontal bands, phase-flip near `n_0 = 320`.
- **Panel 2 — `G_shuffled`**: visually almost indistinguishable
  from `G`. The triangles, bands, and phase-flip all survive
  multiset-preserving shuffle. Bin-2 distribution is doing most of
  the visible work.
- **Panel 3 — `G − G_shuffled`**: faint speckle plus a brighter
  patch in the low-K active wedge. The placement residual is real
  but spatially localised.


## Sharper migrant claim

The claim now reads:

> The L1 tracking gap `G(n_0, K)` is determined by:
> - **the closed-form collision lattice** (bin 1), which fixes
>   support and row scale via elementary number theory
>   (`LATTICE-CLOSED-FORM.md` §2, §4);
> - **the per-cell multiset of duplicate-atom leading digits**
>   (bin 2 distribution), which fixes ~95 % of sign and ~86 % of
>   the linear structure;
> - **the per-atom placement of those digits within the multiset**
>   (bin 2 placement), which carries the remaining ~30 % MAE
>   residual, concentrated in the low-K active wedge.

The full Benford destroyer collapses signal because it kills all
three layers simultaneously. The placement destroyer attacks only
layer 3 and shows that layer is real but smaller than layers 1 + 2.


## Where the placement residual lives

Reading panel 3 of `placement_destroyer.png`: the residual is
brightest along the diagonal `K ≈ n_0` and in the lower-left wedge
where the lattice density is highest. These are cells with many
duplicate atoms relative to bundle size — places where the
multiset can be permuted in many distinct ways, so specific
placements matter most.

This suggests the placement residual scales with lattice density
per cell (more duplicates → more permutation freedom → larger
placement effect). A small follow-up: regress `|G − G_shuffled|`
against `L(n_0, K)` per cell.


## Follow-up — placement residual scales sub-linearly with lattice density

`placement_vs_lattice.py` regresses `|R| = |G − G_shuffled|` against
two natural lattice-density measures: `L_cum` (cumulative collisions
up to K) and `COLL_at_K` (collisions in this K-block).

```
Spearman(|R|, L_cum)        = +0.599
Spearman(|R|, COLL_at_K)    = +0.408
log-log Pearson             = +0.500
power-law fit               |R| ≈ 10⁻⁴·⁶² · L_cum^0.66
```

Two findings:

- **Cumulative beats per-step.** The residual depends on total
  lattice activity in the cell, not just on whether a collision
  fires at this specific K-step (+0.60 vs +0.41). The placement
  layer integrates the cell's whole collision history.
- **Sub-linear scaling with exponent ≈ 2/3.** Doubling lattice
  density less than doubles `|R|`. Mechanistically: more duplicates
  means a larger multiset to permute, but adjacent permutations of
  similar leading digits leave the running L1 nearly invariant, so
  permutation freedom degrades sub-linearly.

The hypothesis from the EXP4 figure ("placement residual concentrates
where lattice density is highest") is confirmed quantitatively, with
a power-law form rather than a linear scaling.


## Files

- `placement_destroyer.py` — script.
- `placement_destroyer.npz` — `G_shuffled` cached.
- `placement_destroyer.png` — three-panel: G, G_shuffled, residual.
- `placement_vs_lattice.py` — follow-up regression.
- `placement_vs_lattice.png` — log-log scatter + binned mean for
  both regressors.
