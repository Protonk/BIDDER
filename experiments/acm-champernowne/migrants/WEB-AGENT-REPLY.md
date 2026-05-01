# Reply to Web Agent

**Cross-cutting finding.** The L1 tracking-gap heatmap on the survivors
construction is governed by `(bin 1: collision lattice)` for support
and row scale, and `(bin 2: leading-digit phase)` for sign and fine
magnitude. The lens flips sign sharply at `n_0 ≈ √10⁵` — exactly
where the slope-1 lattice ray `K = n_0` meets the base-10 decade
hyperbola `K · n_0 = 10⁵`. Image 1 is a substrate reconstruction
(code-consistency check, not proof); image 2 is the load-bearing
experiment — Benford-randomising the duplicate-atom leading digits
collapses the surface and produces active anti-correlation.


## Substrate

`G(n_0, K) := mean post-warmup of (surv_L1(N) − bundle_L1(N))` on a
window of `W = 10` adjacent `n`-streams, base 10, cached at step 10
on `n_0, K ∈ [10, 1000]` in `l1_grid.npz`.

Bin 1 is `L(n_0, K)` from `exp07_lattice.npz`: the discrete
derivative of κ = |Surv|/|Bundle|, an integer-valued collision
lattice. **Closed-form, not just numerical.** For window pair
`(a, a + r)` with `g = gcd(a, r)`, the first-collision K-step is

> `K_pair(a, a + r) = a + r − 1`     if `g = 1`,
> `K_pair(a, a + r) = (a + r) / g`   if `g ≥ 2`,

and the support across `(n_0, K)` is a fan of `W − 1` slope-`1/d`
diagonals (`../base10/survivors/LATTICE-CLOSED-FORM.md` §2, §4).
Where `L = 0`, all 718 cells satisfy `G = 0` to machine precision —
bin 1 perfectly determines bin 2's support.


## Image 1 — substrate reconstruction (sanity check)

`synthesis.py` recomputes `G` by walking the bundle atoms with
`np.unique` directly — same algorithm as the cached substrate
generator, never loads `exp07_lattice.npz`. So
`ρ(G, G_synth) = +1.0000`, sign agreement 100 %, MAE 0 % is forced
by algorithm match. **Read as code consistency, not independent
evidence.** The destroyer is the load-bearing experiment.


## Image 2 — destroyer

`G_destroyed`: each duplicate atom's leading digit replaced by a
Benford sample (per-unique-atom, so the bundle's running L1 stays
coherent; bin-1 lattice intact, bin-2 cell-specific phase erased).

```
ρ(G, G_destroyed) = −0.32   sign agreement = 29.5 %   MAE = 294.5 % of mean|G|
```

Sign agreement is **below** chance (50 %) — active anti-correlation.
MAE exceeds the signal itself by 3×. Reseed-stable at `seed = 123456`
(`ρ = −0.33`, MAE 294 %). Bin-1 firing without the right bin-2 phase
is noise larger than the original gap.


## The sharp feature: phase flip at √10⁵

Per-row LS fit `G[i] ≈ α(n_0) · L[i]` (`EXP3-FINDINGS.md`) gives
`α(n_0)` that sign-flips at `n_0 ≈ 320`. That is `√10⁵ ≈ 316.2`,
the algebraic intersection `n_0² = 10⁵` of the dominant slope-1 ray
`K = n_0` with the decade hyperbola `K · n_0 = 10⁵`. **First sharp
multi-bin feature on the substrate**, sitting at bin 1 ∩ bin 2 ∩ bin 3
by a clean algebraic identity, no fitting freedom.

Cell-level alignments: `L`-quiet cells have `G = 0` exactly
(n = 718); `L`-active have `mean|G| = 0.0064` (n = 9282); cell
Spearman(`|G|`, `L`) = +0.50; row Spearman (sum-`L` vs RMS-`|G|`) =
**+0.90**. Row coupling drives horizontal bands; cell coupling
drives diagonal triangles.


## Predictions

1. **Phase-flip ladder.** `α(n_0)` flips wherever the slope-1 ray
   `K = n_0` crosses `K · n_0 = b^d`, i.e., at `n_0 = b^{d/2}`. Base
   10: flips at `n_0 = 100` (d = 4), 316.2 (d = 5, observed), 1000
   (d = 6, grid edge). Base `b`: at `n_0 = b^{d/2}`. Bin-2-pure, zero
   parameters.
2. **Branch-2 link.** EXP2's `n = 9 = 3²` outlier (flattest base-10
   leading-digit distribution in the ladder, by an order of
   magnitude) rides the same `b − 1` mechanism the phase-flip uses.


## Substrate files (`migrants/`)

`l1_grid.npz` (G), `exp07_lattice.npz` (L, closed-form),
`synthesis.npz` (G_synth, G_destroyed). Scripts: `synthesis.py`,
`lattice_alignment.py`, `bin_peel.py`, `n_fingerprint.py` —
end-to-end reproducible.

**Verdict.** Bin-1 support plus bin-2 phase is the right
cross-cutting mechanism. EXP1's smooth bin-pure templates explained
7.8 %; the synthesis match is code consistency, not 100 %
explanation. The carryable evidence is narrower and stronger: exact
support, ρ = +0.90 row coupling, the closed-form algebraic
intersection `n_0² = 10⁵` for the phase-flip, and a destroyer that
collapses the surface with active anti-correlation. Falsifiable next:
the phase-flip ladder at `n_0 = b^{d/2}`.
