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
