# Wonder: The Cost Ladder

**Date entered.** 2026-05-01

**Category.** Wonder.

## Description

Working at successive heights of the height tower costs roughly an
order of magnitude more per rung. Sometimes more. The growth rate is
not constant; the rate's *rate* is not characterised. The estimate is
informal — it comes from the lived experience of running probes at
`h = 5`, then at `h = 6`, then at `h = 7`, then at `h = 8`, watching
the wall clock of the same procedure climb from seconds to minutes to
hours. There is no theory yet for why the climb has the shape it has,
and no clean instrumentation that would convert the lived estimate
into a measured one.

The cost ladder seems to live in three distinct coordinates that may
or may not climb at the same rate:

- **Combinatorial.** The `j`-sum of the master expansion runs to
  `h_eff = h + ν_n(k)`; the binomial-product term grows polynomially
  in `j`, and the `τ_j(k')` factor grows polynomially in `j` per
  prime of `k'`. The overall arithmetic load per cell of the lattice
  is loosely cubic in `h`, but with cancellation regions where the
  alternating sum collapses several digits of intermediate work.
- **Numerical.** Float arithmetic loses the lattice at
  `h = 8` (master-expansion alternating terms reach `10^5`,
  cancel to `10^{−1}`; ULP error of `10^{−12}` on boundary cells).
  The exact-rational implementation is what `predict_q.py` uses and
  what `algebra/tests/integration/test_within_row_lattice.py` validates;
  cost in this coordinate climbs in the *bignum width* of the
  numerator and denominator.
- **Cognitive.** The number of distinct (shape × tau-sig) cells one
  has to visualize to understand what is happening at height `h`
  appears to grow faster than linearly. The 8 × 6 matrices in
  `KERNEL-ZEROS.md` exhaust the load at `h = 5`; at `h = 8` the same
  matrix shape spans from `−5775/8` and `−4130` up through `151200`,
  with fractions, integers, zeros, and large negatives intermixed,
  and the eye loses the local pattern.

These three coordinates may or may not be aspects of one rate.
Whether they are is part of what the wonder is.

## Evidence

The closest existing framing is `arguments/THE-WHOLE-MACHINE.md` §9,
the *cost ledger*, which decomposes path-cost across the
factorisation graph into three coordinates (CF, mult-table,
digit-frequency). Those are *path coordinates*, not *height
coordinates*; the cost ladder asks what happens to each of them as
the height index climbs.

- `arguments/THE-WHOLE-MACHINE.md:82` — cost ledger §9, the existing
  cost framing.
- `experiments/acm-champernowne/base10/q_distillery/q_lattice_4000_h_regen.py`
  — the regenerator's docstring records the float-arithmetic failure
  at `h = 8` and the switch to exact-rational; concrete data on the
  numerical coordinate.
- `experiments/acm-champernowne/base10/q_distillery/HIGHER-H-EXPECTATIONS.md`
  — predictions for the `h = 6, 7, 8` reads that implicitly assume
  the cost ladder climbs in roughly the shape observed.
- `arguments/ATTRACTOR-AND-MIRAGE.md` — references a 12-minute
  empirical chain at the heights it studies, which is a single point
  on the cost ladder.

The specific "one to four orders of magnitude per rung" articulation
is not yet documented in the repo. This entry is the act of naming
the wonder so it can be measured.

## Status

Suggestive. The estimate is point-estimate at best; no instrumentation
yet exists that would turn the lived experience into a measurable
slope. There may not even be a single slope to measure — the three
cost coordinates may diverge in growth rate, in which case the
"ladder" is three ladders.

The wonder is open in the strong sense: not just unresolved but
under-articulated. The first move is to name what we mean by *cost*
at each rung.

## Aesthetic note

TODO: aesthetic note (human)

## Provocation

- Instrument the height tower. Run a fixed probe — say, the
  cross-`n` lag-1 autocorrelation profile at `h = 4, 5, 6, 7, 8` —
  with wall-clock, bignum-width, and arithmetic-op-count tracked
  separately. One canonical procedure measured at five heights gives
  the ladder its first quantitative read.
- Ask the *shape* question. Is the per-rung cost growth shape-dependent?
  At fixed `h`, do prime-row `n = 2` and squarefree-multi-prime `n = 30`
  climb at the same rate? Or is the cost ladder a function of `(h, shape)`,
  not just `h`?
- Articulate the three coordinates separately and then ask whether
  they correlate. If the combinatorial and numerical coordinates climb
  together but the cognitive coordinate climbs faster, the cost ladder
  is partly a fact about the substrate and partly a fact about how
  human readers (or agent readers) parse height-tower outputs.

## Cross-references

- `prodigy-L1-cliff-n2-h8.md` — the cross-`n` magnitude growth at fixed
  `h` is one rung of the cost ladder seen in the autocorrelation
  coordinate.
- `marvel-row-ogf-cliff.md` — the row-OGF cliff *bounds* the cost in
  one coordinate (row-sums collapse to `1/e` or `0`); part of why the
  cost ladder is interesting is that other coordinates are not similarly
  bounded.

## Discovery context

The wonder was articulated in the 2026-05 manifesto pitch for the
`wonders/` register; it consolidates a feeling that has been
accumulating across the project — that working "one rung up" was
reliably an order-of-magnitude harder than working at the rung below,
and that nobody had named the regularity. The articulation is itself
the first move: one cannot probe what one has not named. This entry
is the naming. Whether it survives a quarter without aging into a
suggestive null result, or sharpens into a measurable slope, or
splinters into three separate ladders, is the substantive question
the wonder poses.
