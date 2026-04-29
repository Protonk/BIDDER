# Q Distillery

`q_distillery.py` renders the master expansion from
`core/Q-FORMULAS.md` as a finite-rank distillation.

For each sampled exact-height payload `m = n^h k`, the script evaluates

    Q_n(m) = sum_j (-1)^(j-1)
             structure(n, h, t, j) * tau_j(k') / j.

The visual split follows the algebra:

- the binomial-product coefficient determines the **stratum** a glyph
  sits in within its (h, j) strip
- `tau_j(k')` controls glyph **size**: large residue grain = large dot
- alternating signs paint the strips warm (j odd) and cool (j even)
- the bottom row of each h-band is the **distillate**: signed `Q_n`
  per sampled payload, summed across all j layers

Layout: four canonical vessels, one per factorisation type — `n=2`
(prime), `n=4` (prime power), `n=6` (squarefree), `n=12` (mixed) —
arranged 2 × 2 in portrait. Inside each vessel, h-bands stack from
`h=1` at top to `h=5` at bottom, with each band's height growing in
proportion to its j-stack depth (the vessel literally widens
downward as more layers are summed). Inside each band, j-strips
stack `j=1` (top) through `j=h` (bottom), each strip annotated `j1`,
`j2`, … on the left edge.

The categorical claim — primes are clean, prime powers sharpen,
multi-prime rows braid — reads off the page as **stratum count per
strip**:

- **prime n=2**: one stratum per (h, j); every glyph in a strip lies
  on a single horizontal line. The overlap tuple is `(0,)` always,
  so the binomial coefficient is determined by `(h, j)` alone.
- **prime power n=4**: two strata at `j ≥ 2`; the t=0 and t=1
  payload populations land at distinct y-positions within each strip.
- **squarefree n=6 = 2·3**: overlap pairs `(t₁, t₂)` multiply through
  two binomial factors, producing several strata that braid together.
- **mixed n=12 = 4·3**: the densest stratification — strips smear
  into dense streams.

The point is not to chart individual formula values. The point is to
show the finite-rank machine: every band stops at height `h`, each
layer peels off a structural term, and only the residual divisor
texture is passed down to the next layer; the categorical type of
`n` is legible at first glance from how many horizontal lines its
strips collapse to.

`q_distillery_n2.py` is the single-pane variant. It keeps only the
prime case `n = 2`, samples more odd payloads, and spends the whole
canvas on one enlarged vessel.

`q_distillery_h3_ns.py` fixes the height at `h = 3` and changes `n`
across the Phase 1 panel `2, 3, 5, 4, 6, 10`. Payloads are grouped by
their overlap exponents, making the prime, prime-power, and squarefree
cancellation regimes directly comparable.

`q_cancellation_furnace_h3_ns.py` uses the same fixed-height panel but
makes signs primary. Warm positive mass descends, cool negative mass
rises, and the central burn line is scaled by
`1 - abs(Q)/(positive + negative)`. The residual cinders below the burn
line keep the sign and size of the surviving `Q_n`.

`q_rank_lemma_skylight.py` is the rank-lemma sibling. Each panel fixes
`n` and arranges sampled `m = n^h k` (with `gcd(k, n) = 1`) as columns,
sorted by `h` then `k`. Rows are `j = 1, …, J_GHOST`. Active panes
(`j <= h`) are coloured by the signed Mercator term; ghost panes
(`j > h`) are faded grey, with a few labelled by the non-integer
fraction `k / n^(j-h)` that makes the term vanish. The bright staircase
running across each panel is `ν_n(m)` — the rank-lemma boundary made
literal. Above it hang the would-be Mercator panes that the integer
divisibility kills.

`q_loom.py` is the integer-language sibling. Each panel fixes one
`(n, h, k)` and renders every ordered `j`-tuple `(n·d_1, …, n·d_j)`
with product `m = n^h · k` as a cell in the `j`-th weave row. Odd-`j`
rows are warm (positive contribution), even-`j` rows are cool
(negative); cell saturation drops with `j` to mirror the Mercator
weight `1/j`. Each factor is rendered explicitly as `n·d_i` so the
constraint "every factor is a multiple of `n`" stays on the page. The
balance ledger at the bottom shows the cancellation directly: a warm
bar of total `Σ_{j odd} (count_j / j)`, a cool bar of total
`Σ_{j even} (count_j / j)`, and a diamond at the signed difference
`Q_n(m)`. For prime `n` at `h = 3` with single-prime `k`, the diamond
lands dead-centre — the low-payload zero band as perfect cancellation.

`q_merger_h5.py` and `q_merger_345.py` thread the towers (warm + cool
pre-cancellation mass) and the polyline (signed surviving `Q_n`) into
one canvas across the four-column panel `n ∈ {2, 4, 6, 12}`. `_h5`
zooms to `h = 5` only; `_345` stacks `h = 3, 4, 5`. Highlighted `k`
are labelled by τ-signature (`k=25 [p²]`, `k=49 [p²]`, …) so that
structural identities — same τ-signature ⇒ same `Q` at every
`(n, h)` — are readable from the legend rather than discoverable
only by overlapping numeric labels. The `n=2` column at `h=5`
carries an explicit annotation: the prime-h=5 coefficient kernel
`(+1, −2, +2, −1, +1/5)` annihilates polynomials of degree 1..4
in `j`, which kills `τ_j(k)` for any `k` coprime to 2 with
`Ω(k) ∈ [1, 4]` — five of the six highlighted `k` vanish exactly,
not by coincidence.

`q_h5_full_scan.py` extends the four-column merger to all `n ∈
[2, 30]`, sorted by n-shape class (sorted-exponent signature). The
shape determines the binomial-product coefficient pattern; `k`'s
τ-signature determines the residue; `Q` is a function of
`(shape(n), τ-signature(k))`. Inside each shape class the coloured
horizontal segments connecting `Q` dots are dead flat by
construction — flatness IS the structural identity. Heights jump
only at class boundaries. The headline structural fact: across the
ten-column prime block (`n = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29`)
five of six highlighted `k` stack on `Q = 0` exactly, by the kernel
identity above. Outside the prime block the kernel partially
extends to `p²` for the linear-τ case (`k = 31`) and breaks
elsewhere; the visualisation lets the reader see exactly where the
zero band ends.

`q_h5_shape_tau_matrix.py` is the structural skeleton extracted
from the 29-column scan. Rows are the eight n-shape classes
(`p, p², pq, p³, p²q, pqr, p⁴, p³q`); columns are six τ-signatures
(`const, p, p², pq, p³, pqr`); cells carry `Q_n(n^5 k)` for any
`(n, k)` of those classes with `gcd(k, n) = 1`. Cells where `Q = 0`
exactly are gold-ringed and dotted. The kernel zeros cluster in the
upper-left corner: the prime row has five (the alternating-binomial
identity kills τ-polynomials of degree 1..4); the `p²` and `p³`
rows each have one (linear-τ kernel: `Σ_j (−1)^(j−1) C(a(h-j)+j-1,
j-1) = 0` for `a ∈ {1, 2, 3}` at `h = 5`); the `p⁴` row breaks the
linear kernel, recording where the alternating sum stops vanishing.
Squarefree multi-prime shapes (`pq, p²q, p³q, pqr`) carry no
kernel zeros at this height. The right-side strip prints each
row's coefficient pattern `(c_1, c_2, c_3, c_4, c_5)` so the
zeros can be checked by inspection against any τ-signature.
