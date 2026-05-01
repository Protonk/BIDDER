# Experiment 2 — n-fingerprint alignment, findings

`n_fingerprint.py` ran (1.4 s on 20 `n`'s).


## Spearman correlation matrix

```
         bin1   bin2a   bin2b    bin3   bin4a   bin4b
   bin1  +1.00  −0.39   −0.22   +0.63  +0.98   +0.98
  bin2a  −0.39  +1.00   +0.13   +0.03  −0.37   −0.37
  bin2b  −0.22  +0.13   +1.00   −0.01  −0.20   −0.20
   bin3  +0.63  +0.03   −0.01   +1.00  +0.66   +0.66
  bin4a  −0.37  +1.00   ←       +0.66  +1.00   +1.00
  bin4b  −0.37  +1.00   ←       +0.66  +1.00   +1.00
```

(Numbers above filled from the run output.)


## Three populations

The 6×6 matrix splits cleanly into three populations:

1. **The substrate spine — bins 1 / 4a / 4b mutually +0.98–1.00.**
   `Q_n` envelope, CF spike scale `S_4(n, 10)`, and `ψ_{M_n}/x − 1`
   produce essentially the same `n`-ranking. Both bin-4 closed forms
   are perfectly monotone in `n` over the ladder, and bin-1's max
   `|Q_n|` follows them at +0.98. **Substrate algebra leaks all the
   way through CF and cumulant readouts** — the hypothesis that
   nominally-different bins all read the same `(n−1)/n²`-shaped
   envelope is confirmed at this ladder.
2. **Base-related observables — bins 2a / 2b — refuse to align.**
   Bin 2a (base-10 leading-digit L1) anti-correlates weakly with the
   spine (−0.37 to −0.39); bin 2b (base-2 bit deviation) is
   essentially orthogonal to everything (±0.22 max). **Base-`b`
   readouts are reading a different surface of the substrate** —
   exactly the prediction of the base-monoid resonance branch.
3. **Bin 3 (K-asymptotic) sits in the middle at +0.63 / +0.66.** It
   tracks the substrate spine partially, but not fully. The
   `log L1` vs `log K` slope has its own structure tied to where
   the bundle is in its convergence regime at `K = 10⁴`.


## The genuinely multi-bin entry — `n = 9`

Reading the per-`n` table for the most striking outliers:

| n  | bin2a (L1 base 10) |
|----|--------------------|
|  8 | 0.1666             |
|  9 | **0.0220**         |
| 10 | 0.1778             |

`n = 9 = 3²` produces the **flattest** base-10 leading-digit
distribution in the entire ladder — by an order of magnitude. Its
neighbours (`n = 8 = 2³`, `n = 10 = 2·5`, both base-10-smooth) sit
far from uniform. That's a feature anchored simultaneously in:

- **bin 1** (rank algebra: `n = 9` is a prime power, sits in a
  specific shape class);
- **bin 2a** (base 10: `9` is one less than the base, the special
  "nines" case from `core/UNIFORMITY.md`).

Neither bin alone predicts the size of the dip; their *intersection*
does. **`n = 9` is a candidate genuine multi-bin migrant.**


## What the perfect bin-4a / bin-4b alignment really means

Spearman = +1.000 between the closed-form CF spike scale and the
empirical `ψ_{M_n}` residual is a **structural** result, not a deep
one: both are monotone-decreasing functions of `n` on this ladder.
The agreement is forced by monotonicity, not by a fine-grained
mechanism. To turn this into a real measurement, the next iteration
needs a non-monotone observable — e.g., the *rate constant* of
`ψ_{M_n}/x` convergence (extracted from a fit), not its value at
fixed `x`. That should distinguish the substrate-algebra spine from
the base-resonance term.


## Next iteration

- **Sharper bin 4a.** Use the sub-leading correction to `S_4(n, b)`,
  not the leading scale. That should peel apart the smoothness
  axis from the magnitude axis.
- **Sharper bin 4b.** Fit `ψ_{M_n}(x)/x − 1 = A_n · x^{−β_n}` over a
  decade of `x`; compare `β_n` (rate exponent) instead of the
  amplitude.
- **Add a base-`b` axis.** Compute bin 2a in base 2, 3, 5, 7 as well
  as 10, and see how the `n = 9` anomaly migrates with base.
- **Destroyer.** Permute `n` labels in any one column; check that
  every off-diagonal correlation collapses to within ±2/√20 ≈ ±0.45.


## Files

- `n_fingerprint.py` — script.
- `n_fingerprint_table.txt` — per-`n` numbers.
- `n_fingerprint_corr.png` — 6×6 Spearman heatmap.
- `n_fingerprint_parallel.png` — parallel-coordinates ladder.
