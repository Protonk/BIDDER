# Higher-h Lattice: What to Expect at h = 6, 7, 8

The lattice visualisations at `h ∈ {2, 3, 4, 5}` give us a fairly
complete read of the local rank stack at low h. The cached
`q_lattice_4000_h{6,7,8}.npy` arrays are the natural next reads.
This doc records concrete predictions for those reads, derived from
the CF off-spike denominator analysis
(`experiments/acm-flow/cf/DENOMINATOR-PROCESS.md`).

The high-level theoretical justification lives in
`algebra/FINITE-RANK-EXPANSION.md` ("What CF empirics imply for
higher-h reads"). What this doc adds: cell-level addresses to flag
when rendering the higher-h lattices, statistics to compute, and the
two-outcome diagnostic that distinguishes foothold-deeper from
perimeter-located on each prediction.


## Predictions

### P1. Closed-form residuals decay geometrically in h

The CF result: `Δ_k = D_{k−1} + (n−1) + O(b^{−(k−1)})`, with
residuals decaying `10⁻²` → `10⁻³` → `10⁻⁴` at successive layers.

For the Q lattice the corresponding statement is: whatever closed
form governs the leading-order behaviour at `h = 5` should match
observation at `h = 6, 7, 8` with residuals that shrink by a
geometric factor in `h`, not at constant scale.

**Concrete check.** Compute `Q_n(n^h k)` against the master
expansion's leading piece at fixed `k = 1` for `n ∈ {2, 3, 5, 7}`,
across `h = 5, 6, 7, 8`. The residual `|Q_n(n^h k) −
leading_form(n, h, k)|` should fall by a fixed ratio per `h`-step,
not stay constant.

**Two outcomes.**

- *Geometric decay observed.* Foothold extends; the leading form
  captures the asymptotic shape and the lattice at higher h is
  predicted by a closed expression with shrinking error.
- *Constant or growing residual.* The leading form is incomplete at
  higher h; the missing term is sub-leading at h = 5 and rises to
  comparable magnitude. Worth identifying analytically before
  declaring the local algebra closed.


### P2. Three populations, not one shape

The CF result: substrate envelope + Gauss-typical small-PQ interior
+ anomalous intermediate-magnitude excess.

For the Q lattice the analogous decomposition is:

- **Closed-form leading population**: cells where the dominant
  τ_j(m/n^j) term sets `Q_n` magnitude and sign. These should look
  most like the h = 5 visual archetype.
- **Alternating-series fluctuation population**: cells where the
  signed sum across `j` largely cancels and `Q_n` lands at modest
  magnitude with sign-cycling structure. The lattice "noise" between
  the bright structural rows.
- **Intermediate-magnitude population**: cells where `Q_n` is
  neither at the closed-form magnitude nor in the cancellation
  regime — values that the leading-form prediction misses by
  amounts larger than alternation noise but smaller than the
  closed-form scale. These are the perimeter analogue of CF's
  Test C.

**Concrete check.** Histogram `log|Q_n(n^h k)|` per `h` across the
lattice. A clean two-population mixture (leading + fluctuation)
fits the CF Test A + Test B picture; a residual middle bump or
heavy intermediate tail is the perimeter analogue of CF Test C.

**Two outcomes.**

- *Two populations only.* The local algebra at higher h decomposes
  cleanly into closed-form + cancellation-noise; no third
  population. This would be a *narrower* outcome than CF.
- *Three populations.* The intermediate-magnitude population is
  the natural Q-lattice analogue of CF's sub-canonical excess;
  same open-perimeter shape, different observable.


### P3. Transient cells stabilise at higher h

The CF panel: `n ∈ {4, 10}` are still transient at `k = 5`.
`PRIMITIVE-ROOT-FINDING.md` predicts which cells canonicalise when,
by `ord(b, n)`.

For the Q lattice the analogous expectation is that some `(n, k)`
cells that look "wrong" or unstructured at `h = 5` will first
become legible at `h = 6, 7, 8`. Specifically:

- **n = 4, 8, 9, 16, 25, 27, …** — prime powers `p^a` with
  `gcd(p, b) > 1` (here b = 10, so `p ∈ {2, 5}`). These are the
  CF analogues of the transient cells.
- **n = 6, 12, 14, 15, …** — composites where the smooth-block
  hypothesis `n² | b^{d−1}` fails at low d.

**Concrete check.** Fix `k` (e.g., `k = 1, 2, …, 10`) and walk the
above `n` cells across `h = 5, 6, 7, 8`. The h at which `Q_n`
matches the closed-form prediction (within geometric residual) is
the asymptotic-stabilisation threshold for that cell. Tabulate.

**Two outcomes.**

- *Stabilisation threshold matches `ord(b, n)` classification.*
  Foothold extends; the same axis that classified CF transients
  classifies Q-lattice transients.
- *Different stabilisation pattern.* The Q lattice has its own
  classification, likely tied to the structure of `n` itself
  (radical, exponent, primality) rather than `ord(b, n)`.


### P4. Singular cancellation cells, not uniform precision walls

The CF result: validation broke at i = 408 due to a single
mega-spike (~10⁵ decimal digits), not at smooth precision
exhaustion. Higher-h analogues are specific cells with
combinatorial blow-up.

For the Q lattice: `τ_j(m/n^j)` involves products of binomial
coefficients `comb(exp_in_x + j − 1, j − 1)`. As `h` grows, these
combinatorial factors can grow rapidly at specific cells. Expect
the lattice at `h = 8` to have:

- **Singular cells with extreme magnitude** — single positions
  where one binomial factor dominates and `Q_n` writes hundreds or
  thousands of digits.
- **Singular cells with extreme cancellation** — adjacent positions
  where the alternating sum cancels to near-zero, with small
  perturbations dominating.

These are the visual signatures of "structure failing in a
specific way." They are *not* uniformly distributed across the
lattice; they cluster at specific `(n, k)` addresses.

**Concrete check.** For `h = 8`, identify the top 10 cells by
`|Q_n|` and the top 10 cells by `1/|Q_n|` (smallest non-zero).
Expect both lists to land at non-random positions — clusters at
specific n with specific k mod something, not uniform across the
lattice.

**Two outcomes.**

- *Singular cells cluster at predictable addresses.* Foothold for
  precision-management at higher h; the same set of cells will be
  "where the lattice breaks" at h = 9, 10 too.
- *Singular cells uniformly distributed.* Higher-h Q lattice
  behaves more like a generic numerical computation — random
  cancellations, not structurally-driven ones. Less interesting,
  flag as a null prediction.


## Cross-references

- `algebra/FINITE-RANK-EXPANSION.md` — high-level rationale; the four
  predictions above are concretisations of its "What CF empirics
  imply for higher-h reads" section.
- `algebra/Q-FORMULAS.md` — the master expansion that supplies the
  closed-form leading prediction in P1.
- `core/BLOCK-UNIFORMITY.md` — the smooth-block atom count
  `(b−1)b^{d−1}(n−1)/n²` that anchors the leading-form bet.
- `experiments/acm-flow/cf/DENOMINATOR-PROCESS.md` — the CF result
  these predictions extrapolate from.
- `experiments/acm-flow/cf/PRIMITIVE-ROOT-FINDING.md` — the
  `ord(b, n)` classification that P3 hypothesises governs
  transient stabilisation.
- `Q_DISTILLERY.md` (this folder) — rendering style for the Q
  lattice; the predictions here concern *which cells* to render
  and *what to extract*, complementing the rendering doc.

## Files in this folder relevant to the predictions

- `q_lattice_4000_h5.npy`, `q_lattice_4000_h6.npy`,
  `q_lattice_4000_h7.npy`, `q_lattice_4000_h8.npy` — cached
  4000-cell lattices at successive heights, the natural input for
  the predictions above.
- `q_lattice_4000.py`, `q_lattice_full_bleed.py` — rendering
  scripts; reuse for higher-h reads.
- `q_lattice_iter_*.py`, `q_lattice_taurand.py` — diagnostic
  scripts that probe lattice structure under perturbation; useful
  for P4 (singular cells).
