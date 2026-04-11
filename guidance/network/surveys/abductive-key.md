# Abductive Key

source: [`core/ABDUCTIVE-KEY.md`](../../../core/ABDUCTIVE-KEY.md)  
cited in: [`COLLECTION.md` — The Recovery Thread](../../../COLLECTION.md#chapter-3-the-recovery-thread)  
last reviewed: 2026-04-10

---

**Claim.** Under the setup — strictly ascending row list
`n_1 < n_2 < … < n_N` with each `n_k ≥ 2`, and the `N × N` table
whose entry `T[k][k']` is the `k'`-th `n_k`-prime — the diagonal
is `D_k = k · n_k`, and therefore `n_k = D_k / k`. The diagonal
alone determines the row list.

**Mechanism.** The first `n_k − 1` n-primes of monoid `n_k` are
`n_k, 2n_k, …, (n_k − 1) · n_k` (all below the square boundary
`n_k²`). Strict ascent forces `n_k ≥ k + 1` at every position,
so `k ≤ n_k − 1`, which keeps the diagonal cell `(k, k)` inside
the rank-1 region `{(k, k') : k' ≤ n_k − 1}` of its row. In
that region `T[k][k'] = k' · n_k`, so `D_k = k · n_k`. Dividing
by `k` recovers `n_k`. Half a page of proof.

**Depends on.** The definition of n-primes from
[`acm-champernowne.md`](acm-champernowne.md). Nothing else.

**Supports.** The "three surprises now" retrospective and the
leaky-parameterization taxonomy in
[`unordered-conjecture.md`](unordered-conjecture.md); the
cascade-key reading in
[`cascade-key-readme.md`](cascade-key-readme.md) ("one key, all
locks"); the recovery-rate geometry in
[`cantor-walk-readme.md`](cantor-walk-readme.md); the
garden-level index at
[`cantors-plot.md`](cantors-plot.md). Together these form the
recovery thread.

**Status.** Proved. The theorem is elementary. The doc's
distinctive content is not the proof but the long "rank-1 view"
essay and its "note on visibility" — a careful record of the
fact that the inference did not come easily despite being one
symbol-pushing line, and a naming of *leaky parameterization*
as the pattern behind a sequence of obvious-in-retrospect
recoveries. The meta-essay's "productive triviality / knife-edge"
caveat is where the open content lives: whether the leakiness is
a *foothold* (rich consequences from a trivial surface) or a
*perimeter* (every result a relabeling), and the repo is
operating in a constructed space where the perimeter risk is
sharper than usual.
