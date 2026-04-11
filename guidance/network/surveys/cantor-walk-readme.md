# cantor_walk/README — Recovery Curves

source: [`experiments/acm/diagonal/cantor_walk/README.md`](../../../experiments/acm/diagonal/cantor_walk/README.md)  
cited in: [`COLLECTION.md` — The Recovery Thread](../../../COLLECTION.md#chapter-3-the-recovery-thread)  
last reviewed: 2026-04-10

---

**Setup.** Contiguous row list `n_k = k + 1` with `N = 20`,
giving an n-prime table of size `20 × 20`. Three walks
through the table overlaid on the rank-1 region (the closed
lower triangle for this row list): the main diagonal, the
Cantor antidiagonal, and the row-by-row scan. The recovery
cell for row `k` is the first cell at which the walk
reveals `n_k` — either the diagonal cell `(k, k)` or the
first-column cell `(k, 1)`.

**Headline.** *Geometry causes rate.* The main diagonal
recovers row `k` at step `k` — linear, slope 1. The Cantor
walk recovers at step `k(k + 1) / 2` — quadratic. The
row-by-row walk recovers at step `(k − 1) · N + 1` — linear
with giant slope `N`. All three walks reach the same
recovery cells; the only difference is the *order* in which
they reach them, and the order is determined by how the
walk's slope relates to the rank-1 boundary. The diagonal
wins because its slope matches the boundary exactly — every
diagonal step is a recovery. The picture turns strict
ascent from a structural condition
([`abductive-key.md`](abductive-key.md)) into a
quantitative rate.

**Control.** Closed-form recovery positions for all three
walks are asserted against direct simulation in the script
before the plot is rendered. A wrong walk implementation
would fail the assertion first.

**Open.** Sparse row lists balloon the rank-1 region and
improve Cantor's recovery rate, but the diagonal still
wins — by how much is worth rendering. A Hilbert-curve walk
has local geometry that doesn't match either axis, and its
recovery rate is unknown. The unordered follow-up
(documented in [`unordered-conjecture.md`](unordered-conjecture.md))
removes position information entirely and asks how many
hints are needed to recover the row list from values alone;
that turned out to be zero.
