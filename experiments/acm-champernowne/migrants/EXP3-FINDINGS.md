# Experiment 3 — lattice subtraction (κ-derivative as bin-1 isolator), findings

`exp07_kappa_derivative.py` and `lattice_alignment.py` ran. The
collision lattice from EXP07 was used as a bin-1 isolator on the
L1 tracking gap from `l1_grid.npz`.


## The lattice predicts the support of the gap exactly

```
lattice-quiet cells (no collisions): n = 718,  |G| = 0.0000 exactly
lattice-active cells:                n = 9282, mean |G| = 0.0064
```

Where the lattice predicts no collisions, the gap is **identically
zero**. Trivially derivable (no collisions ⇒ survivors = bundle ⇒
gap = 0), but worth stating: **bin 1 perfectly predicts the support
of bin 2.** This is the strongest cross-bin link possible.


## Cell- and row-level alignment

```
cell-level Spearman(|G|, L_cumulative): +0.504
row-level  Spearman(row-sum L, row-RMS |G|): +0.896
```

- **Cell ρ = +0.50** — the lattice partially predicts gap magnitude
  per cell. Where the lattice fires more, the gap *tends* to be
  larger. The arithmetic substrate leaks through.
- **Row ρ = +0.90** — at the `n_0`-row level the link is very strong.
  **The horizontal bands the L1-gap zoom showed are bin 1 × bin 2
  coupling at the row scale**, exactly as predicted in the
  examination of EXP07. Lattice density per row predicts gap RMS
  per row at ~0.9.


## Per-row α(n_0): a phase transition near n_0 ≈ 320

The most surprising finding. Per-row LS fit `G[i] ≈ α_i · L[i]`
gives a coefficient `α(n_0)` that *changes sign sharply* at
`n_0 ≈ 320`:

- `n_0 ∈ [10, 310]`: `α ≈ +0` to `+3 · 10⁻⁵` — bin 1 raises gap.
- `n_0 ∈ [320, 770]`: `α ≈ −2` to `−5 · 10⁻⁵` — **bin 1 suppresses
  gap.**
- `n_0 ∈ [780, 1000]`: `α` swings positive again, with growing
  amplitude.

The transition at `n_0 ≈ 320` lines up with the diagonal-decade
intersection: `n_0 ≈ √10⁵ = 316.2`, so the first-collision diagonal
`K = n_0 + 1` crosses the `K · n_0 = 10⁵` decade hyperbola right
there. That intersection is the canonical bin-1-meets-bin-2 event.
**The horizontal red band the L1 zoom showed at `n_0 ≈ 290–330`
is the leading-digit-phase flip captured by α(n_0).**

This is a genuinely multi-bin feature: it is forced by the algebraic
event (lcm collision, bin 1) AND by the base-10 decade geometry
(`K · n_0 = 10⁵`, bin 2) AND by the K-magnitude they jointly index
(bin 3). It cannot be reduced to any single bin.


## What the projection captures and what it doesn't

```
|G| total:                  59.30
|αL| bin-1 projection:      25.40 (42.8%)
|G − αL| bin-2 residual:    48.80 (82.3%)
σ_R / σ_G:                  0.928
```

The per-row linear projection eats ~14 % of the variance — better
than EXP1's 7.8 % from smooth templates, but still leaves most of
the structure unexplained. The four-panel figure
(`lattice_alignment.png`) shows where: the **horizontal bands** are
captured by α·L; the **diagonal triangles** are not. Triangles are
where lattice-firing × leading-digit-phase produce a coherent signed
gap that a row-scalar α can't reproduce. Triangles are the irreducible
bin 1 × bin 2 product structure.


## Cross-cutting verdict

The κ-derivative is a clean bin-1 isolator on the same `(n_0, K)`
substrate as the L1 gap. With both substrates aligned:

1. **Bin 1 → bin 2 support transmission:** perfect (lattice-quiet
   cells have gap = 0 exactly).
2. **Bin 1 → bin 2 row-magnitude transmission:** very strong
   (ρ = 0.90).
3. **Bin 1 → bin 2 sign transmission:** captured by α(n_0), with a
   **sign-flip phase transition at `n_0 ≈ √10⁵`** locating the
   cross-cutting bin 1 ∩ bin 2 ∩ bin 3 event.

Migrant claim graduates: the L1 tracking-gap heatmap is, structurally,
`(bin 1 lattice) × (leading-digit lens with n_0-dependent phase)`.
The lens has its own non-trivial structure tied to base-10 decade
boundaries.


## Next iteration

- **Map the α(n_0) structure.** What controls the sign-flip
  besides the `n_0 ≈ √10^d` threshold? Are there finer-grained flips
  at smaller decade roots (n_0 ≈ √10^4 ≈ 100)? Re-fit with a finer
  K-grid to resolve.
- **Bin-2 lens model.** Replace per-row α with a lens predictor
  computed from the leading digit of `K · n_0` directly. If
  `α_predicted(n_0)` matches the empirical α(n_0), the bin-2 lens is
  determined by base-radix geometry alone.
- **Extend to base 2.** Re-run on a base-2 leading-bit gap; the
  decade-roots become `n_0 ≈ √2^d`, and the phase-flip locations
  should migrate with base.


## Files

- `exp07_kappa_derivative.py` — collision-lattice computation
  (copied from `survivors/`, modified to save `exp07_lattice.npz`).
- `exp07_kappa_derivative.png` — left/right panel: lattice + smooth κ-integral.
- `exp07_lattice.npz` — cached `COLL`, `S_GRID`, `N0_VALUES`, `K_MAX`, `W`.
- `lattice_alignment.py` — cross-cut script.
- `lattice_alignment.png` — four-panel: G, L, α·L, G − α·L.
- `lattice_alpha_per_row.png` — α(n_0) trace showing the n_0 ≈ 320 sign-flip.
