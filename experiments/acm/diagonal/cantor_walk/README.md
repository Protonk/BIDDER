# Recovery curves — geometry causes rate

`recovery_curves.png` is a two-panel figure for the contiguous row
list `n_k = k + 1` with `N = 20` (so the table has rows for
`n = 2, 3, …, 21`). The left panel shows three walks through the
n-prime table; the right panel shows how fast each walk recovers
the row labels as a function of enumeration step.

## What the eye is supposed to see

**Left panel (geometry).** The rank-1 region of the table is shaded
in light blue. For contiguous rows `n_k = k + 1`, this region is
exactly the closed lower triangle `{(k, k') : k' ≤ k}` — the
densest case, where the rank-1 region pulls back to its smallest
extent and the diagonal lies right on its boundary.

Three walks are overlaid:

- **Main diagonal** (black, 20 steps): a single straight line from
  `(1, 1)` to `(20, 20)`. Its slope is `+1` in matrix coordinates,
  exactly the slope of the rank-1 boundary. Every diagonal cell is
  in the rank-1 region by exactly the strict ascent inequality, so
  the walk recovers one row per step.

- **Cantor antidiagonal** (red, 210 steps): a family of slope-`−1`
  segments perpendicular to the diagonal. Cantor visits cells in
  order of antidiagonal `d = k + k'`, sweeping from the top-right of
  each antidiagonal toward the bottom-left. After 210 steps it has
  covered all of antidiagonals `d = 2 … 21`, which is the full
  upper-left triangle `{k + k' ≤ 21}`.

- **Row-by-row** (purple, 381 steps): horizontal sweeps through
  rows 1 through 19, plus the single cell `(20, 1)` where row 20
  is finally recovered. The purple region nearly fills the grid
  because row-by-row has to traverse most of the table before
  reaching the leftmost cell of the bottom row.

The recovery cells — where each walk first reaches a rank-1 cell of
each row — are marked with small dots. The diagonal recovers at
`(k, k)` (black dots along the diagonal); row-by-row and Cantor both
recover at `(k, 1)` (white-with-black-edge dots in column 1). They
recover at the *same cells*; the difference is *when*.

**Right panel (rate).** The recovery curves plot rows recovered
against enumeration step:

- The diagonal curve is `y = m`. Linear, slope 1. Reaches `y = 20`
  at step 20.

- The Cantor curve is `y ≈ √(2m)`, formally a step function with
  one new row recovered at each step `k(k+1)/2`. Reaches `y = 20`
  at step 210.

- The row-by-row curve is a staircase with 20-step plateaus
  (because every row takes `N = 20` steps to traverse before the
  next row's column-1 cell is reached). Reaches `y = 20` at
  step 381.

The horizontal dashed line at `y = 20` is "all rows recovered." The
gap between the curves' completion points — 20 vs 210 vs 381 — is
the rate cost of having position-as-decoder fail to line up with the
rank-1 boundary.

## What this teaches

The diagonal isn't just a transversal that happens to land in the
rank-1 region. It is the *minimum-effort* traversal of the region:
its slope matches the region's boundary exactly, so every step it
takes is a recovery. Any walk whose slope differs from the
boundary's slope will recover at a worse rate, with the gap given
by how perpendicular the walk's slope is to the boundary.

Cantor and row-by-row recover the same `(k, 1)` cells; what differs
is the *order* in which they reach them. Cantor's antidiagonal
sweeps reach column 1 of each new row at quadratic cost; row-by-row's
horizontal scans reach it at linear-but-`N`-times cost. Both walks
have to leave the rank-1 region to make progress, and the structure
of how they leave determines the rate.

This is the picture that makes the abductive key's "wearing two
hats" observation graduate from notation to rate. Strict ascent and
"the diagonal lies in the rank-1 region" are the same inequality —
and that inequality buys you `N` instead of `N(N+1)/2` or
`(N − 1) · N + 1`.

## What to try next

Two natural variants the script supports with one-line changes:

- **Sparse row list.** Replace `ROWS = [k + 1 for k in range(1, N + 1)]`
  with something like `ROWS = [2, 5, 10, 13, 17, 21, 25, 31, 37, 41, …]`.
  The rank-1 region balloons out (rows with large `n_k` are entirely
  rank-1), and Cantor's recovery rate improves because more cells in
  each row become decodable. The diagonal still wins, but by less.
  Worth rendering to see the geometric shift.

- **Add a Hilbert curve walk.** Hilbert curves have local geometry
  that doesn't match either the diagonal or the antidiagonal slope,
  so their recovery rate is interesting — probably worse than the
  diagonal but the constant matters. The cell visit order is the
  only thing the script needs to consume.

A more ambitious follow-up: the **unordered version** of the
problem, where the receiver gets cell values without knowing which
`(k, k')` each came from. Each antidiagonal cell value has two
unknowns (`k'` and `n_k`); each known row label collapses one
equation. The natural question is how many label hints are needed
before the antidiagonal stream becomes recoverable from cell values
alone. The guess is `O(log N)`. Worth checking once the recovery
curves are committed.

## Reproduce

```
sage recovery_curves.py
```

Writes `recovery_curves.png` in this directory. The script also
brute-force sieves n-primes for the contiguous row list and asserts
the closed-form recovery positions for all three walks against
direct simulation, so a wrong walk implementation would fail the
assertion before the figure is rendered.
