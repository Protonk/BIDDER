# cascade_key/README — The Cascade Heatmap

source: [`experiments/acm/diagonal/cascade_key/README.md`](../../../experiments/acm/diagonal/cascade_key/README.md)  
cited in: [`COLLECTION.md` — The Recovery Thread](../../../COLLECTION.md#chapter-3-the-recovery-thread)  
last reviewed: 2026-04-10

---

**Setup.** Row list `{5, 7, 11, 13, 17, 19}` over the first
60 columns of the n-prime table. Each row of the heatmap is
one row of the table, colored by the parity of its rank-1
patch index. Alternating blue and tan stripes mark the
patches. White circles mark the diagonal cells `(k, k)` for
`k = 1..6`.

**Headline.** *One key, all locks in row k.* Each row breaks
into patches of width `n_k − 1`, because that is how many
n-primes sit between consecutive skips of multiples of
`n_k²`. The diagonal cells land visibly inside the first
patch of their row — this is the strict-ascent inequality
`k ≤ n_k − 1` rendered geometrically, the same inequality
that forces `D_k = k · n_k` in
[`abductive-key.md`](abductive-key.md). Once `n_k` is
decoded from the diagonal cell, every later patch in the row
is computable from `k'` and `n_k` alone via
`j_{k'}(n_k) · n_k`, so every later cell decodes too. The
framing shift the doc introduces: *not* "each later patch
has its own key," but "there is one key and once turned it
opens every lock in the row."

**Control.** A brute-force sieve assertion in the script
verifies the closed-form expression for every cell before
rendering. An earlier-draft formula error was caught by this
assertion; the corrected expression
`j_{k'} = k' + ⌊(k' − 1) / (n_k − 1)⌋` is the form the
abductive-key essay now uses.

**Open.** *Perturbed cascades.* Splice rows from different
ACM-like constructions, or perturb a single row by inserting
a phantom skip. Does the cascade still decode the entire row
from the diagonal cell, or does perturbation land the
diagonal outside the first patch and break the cascade? This
is the plot 4 open question in
[`cantors-plot.md`](cantors-plot.md).
