# Cascade key — heatmap

`cascade_grid.png` renders the rank-1 patch structure of the n-prime
table for the row list `{5, 7, 11, 13, 17, 19}` over the first 60
columns. Each row of the figure is one row of the table, colored by
the parity of its rank-1 patch index: alternating blue and tan
stripes are the patches.

## What the eye is supposed to see

**The staircase.** Each row breaks into patches of width `n_k − 1`.
Row `n = 5` has stripes of width 4 (15 of them across the window);
row `n = 19` has stripes of width 18 (just over 3). The patch width
*is* the row label minus one, and the row-by-row change in stripe
density is the visible record of that.

**The diagonal sits in the first patch of every row.** The white
circles mark the diagonal cells `(k, k)` for `k = 1 … 6`, i.e.,
column 1 of row 1, column 2 of row 2, …, column 6 of row 6. Every
marker lands inside the first (leftmost) stripe of its row. That
placement is exactly the strict ascent inequality `k ≤ n_k − 1`
rendered geometrically — the diagonal stays in the rank-1 region
because its slope is calibrated to the slowest patch boundary the row
list allows.

**The cascade.** The diagonal cell of row `k` decodes `n_k` by
division by `k`. Once `n_k` is in hand, the patch index of any later
column in row `k` is computable from `k'` and `n_k` alone via
`⌊(k' − 1) / (n_k − 1)⌋`, and the cell value is recovered as
`(k' + ⌊(k' − 1) / (n_k − 1)⌋) · n_k`. So the diagonal cell — the
marker — is the only place the receiver needs to look in row `k`.
Every later stripe in that row is unlocked by the same key. One key
per row, all locks.

## What to try next

The picture is the static fact. The motion to chase is in two
directions:

- **Perturbations.** Splice rows from different ACM-like
  constructions, or perturb a single row by inserting a phantom skip,
  and re-render. The cascade question (plot 4 of `CANTORS-PLOT.md`)
  is whether the diagonal still opens the entire row when the
  staircase is broken; the heatmap is the way to see whether a given
  perturbation lands the diagonal outside the first patch or whether
  the later patches stop being computable from `n_k` alone.

- **Antidiagonals.** Overlay a Cantor antidiagonal walk on the same
  grid and watch which cells it touches as a function of step count.
  This is the visual companion to plot 5 — the recovery curves
  become visible as "how quickly does the walk cross into each row's
  first patch."

## Reproduce

```
sage cascade_grid.py
```

Writes `cascade_grid.png` in this directory. The script also
brute-force sieves n-primes and asserts the closed-form expression
matches, so a wrong formula would fail the assertion before the plot
is rendered.
