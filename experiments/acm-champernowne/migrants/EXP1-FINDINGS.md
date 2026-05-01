# Experiment 1 — bin-peel of the L1 tracking-gap, findings

`bin_peel.py` ran. Substrate: cached `l1_grid.npz` (100 × 100 grid,
`n_0, K ∈ [10, 1000]` step 10, `W = 10`).


## Numerical readout

```
α_1  Bin 1: rank algebra (K ≥ n_0)               −0.00031
α_2  Bin 2: decade ridges (K·n_0 = 10^d)         −0.01065
α_3  Bin 3: K-asymptotic (1/√K)                  −0.00959
α_4  Bin 4: Mertens envelope (1/log K·n_0)       +0.01924

variance explained:  0.078
σ_R / σ_G:           0.96
residual L1 / |G|:   91.1%
```

Predictor cross-correlation: bins 3 and 4 are **+0.68** correlated;
all other pairs are below 0.43 in absolute value.


## What the figures show

- **`bin_peel.png`** — the four fitted components are visibly smooth
  and almost featureless next to `G`. Bin 1's sigmoid-on-`K − n_0`
  collapses to `α ≈ 0` because the diagonal activation is sharp,
  not soft. Bin 4 (Mertens) carries a uniform red offset; bin 2
  carries the only visible structured smooth ridge.
  The residual `R` is **visually indistinguishable from `G`** — the
  fit removed essentially nothing.
- **`bin_attribution.png`** — left: every cell is either bin 2
  (decade) or bin 4 (Mertens) by argmax, because bins 1 and 3 carry
  near-zero magnitude. Right: pan-bin candidates light up the entire
  active wedge above `K = n_0`, with concentrated brightness along
  the first-collision diagonal and along the horizontal residue band
  near `n_0 ≈ 290–330`.


## Interpretation

The bin-pure **smooth** templates explain ~8% of the gap structure.
The remaining 92% is sharp arithmetic detail that no global smooth
predictor captures. This is a usable negative result: it tells us
the harmonics in the L1 tracking gap are not "smooth bin 1" or
"smooth bin 4" features in the simple sense, but live in genuinely
arithmetic local structure (divisor counts, modular residues,
exact decade boundaries).

The "pan-bin candidates" map should therefore be read as **"where the
smooth-template fit underperforms,"** which is essentially everywhere
the gap has nonzero magnitude — not as a clean attribution map.

Bin 3 / bin 4 colinearity (`+0.68`) is structural: `1/√K` and
`1/log(K·n_0)` are both monotone-in-`K` envelopes that flatten in
similar regions. The next iteration needs a sharper bin-4 proxy that
is not a smooth function of `K·n_0` alone.


## Next iteration — sharper predictors

The smooth-template peel is the wrong shape for this gap. The
harmonics demand integer-valued predictors:

- **Bin 1.** Exact indicator `(K, n_0) : lcm(n_0, n_0 + 1) ≤ K · n_0`,
  not a sigmoid; combined with a divisor-count term `d(K · n_0)`
  for the rank-2+ activations.
- **Bin 2.** `(K · n_0) mod 10^d` distance to the nearest decade
  boundary, integer-valued, with a residue-class flag for the
  leading digit of `K · n_0`.
- **Bin 3.** Replace `1/√K` with the *empirical* row-mean of the
  bundle L1 at fixed `n_0`; subtract row-by-row before any global
  fit.
- **Bin 4.** Replace `1/log(K · n_0)` with `μ`-conditional CF spike
  positions from `cf/MEGA-SPIKE.md` evaluated at the active depth
  `d = ⌊log₁₀(K · n_0)⌋`.

Variance-explained should rise substantially before any pan-bin
attribution is meaningful.


## Files

- `bin_peel.py` — the script.
- `bin_peel.png` — six-panel figure: `G`, four `α_i P_i`, residual `R`.
- `bin_attribution.png` — argmax bin map + pan-bin residual map.
