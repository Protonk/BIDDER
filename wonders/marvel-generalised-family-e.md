# Marvel: Generalised Family E

**Date entered.** 2026-05-03

**Category.** Marvel.

## Description

![Dark indigo background. A polar-coordinate flower with five concentric tiers of petals radiating from the center, each tier in a distinct hue: innermost lime green (d=3), then pale gold (d=4), amber (d=5), violet (d=6), and rose (d=7). Each tier consists of evenly-spaced petal shapes whose lengths vary modestly with `log10(qp + 1)` normalised within the tier. Faint baseline circles at each tier's base. Title-less; the figure is a stylised view of the 69 Generalised Family E cells in the b = 10, n ∈ [2, 200], d ∈ [1, 7] sweep, organised by `(d, qp, m_min)`.](../experiments/acm-champernowne/substrate-phase/lotus_lattice.png)

The substrate theorem in `paper/PAPER.md` §3 enumerates two exact regimes for the n-prime atom count on the digit-class block `B_{b,d} = [b^(d-1), b^d − 1]`: clause 2 (smooth-sieved, `n² | b^(d-1)`) and clause 3 (Family E, `n ∈ [b^(d-1), ⌊(b^d − 1)/(b − 1)⌋]` — exactly `{n, 2n, …, (b−1)n}`, one per leading digit). Universally, clause 4 says spread ≤ 2. The phase diagram at b = 10 (`experiments/acm-champernowne/substrate-phase/phase_diagram.png`) revealed 96 cells outside the proven regimes where spread = 0 anyway — the *lucky locus*. WORKSET.md flagged the locus as uncharacterised.

The lucky locus splits cleanly into two mechanisms. Sixty-nine of the ninety-six cells are *Generalised Family E*: for `W = b^(d-1)`, integer parameters `(qp, m_min)` with `m_max := m_min + qp(b − 1) − 1` produce exactly `qp` multiples of `n` per leading-digit strip whenever the four hypotheses hold (`m_min · n ≥ W`, `m_max · n ≤ bW − 1`, `(m_max + 1) · n > bW − 1`, and the per-strip leading-digit alignment `leading_digit(kn) = ⌈(k − m_min + 1)/qp⌉`). When the multiples of `n²` distribute uniformly across strips with `δ` per strip, the n-prime atoms are `q = qp − δ` per leading digit and the cell is exact. Clause 3 is the special case `qp = 1, m_min = ⌈W/n⌉, δ = 0` — exactly one multiple per strip, with `n²` automatically outside the block since `n ≥ b^(d-1)`. The proof is the same divmod argument as clause 3 with the parameters free.

The theorem is verified exhaustively in the swept range. `analyze_lucky.py` enumerates all 46 distinct `(d, qp, m_min)` groups in b = 10, n ∈ [2, 200], d ∈ [1, 7] and reports predicted-equals-observed `n`-range for every one. The phase-diagram lucky cells either fall inside Generalised Family E (69 of 96, closed-form characterised) or inside a separately-identified `n²`-cancellation locus where `M_k(n)` and `M_k(n²)` extras patterns coincide bit-for-bit (27 of 96, structural condition verified 27/27 but trigger set still open).

## Evidence

- `experiments/acm-champernowne/substrate-phase/LUCKY-LOCUS.md` — full theorem statement, proof of the `(qp, m_min)` characterisation, verification table (all 46 groups), and the `n²`-cancellation residual.
- `experiments/acm-champernowne/substrate-phase/analyze_lucky.py` — exhaustive enumeration over the swept range; reports `predicted = observed` per `(d, qp, m_min)` group and the Beatty pattern-alignment verification for the residual locus (27/27).
- `experiments/acm-champernowne/substrate-phase/phase_diagram.py`, `phase_diagram.png` — the rectilinear precursor that surfaced the 96 lucky cells.
- `experiments/acm-champernowne/substrate-phase/lotus.py`, `lotus_lattice.png` — the 69 Generalised Family E cells rendered in `(d, qp, m_min)` coordinates as concentric tiers of petals; the emblem above.
- `experiments/acm-champernowne/substrate-phase/PAPER-INCLUSION.md` — the case for promoting the theorem to a sixth substrate-theorem clause in `paper/PAPER.md` §3, with concrete edits.
- `experiments/acm-champernowne/substrate-phase/BRIEF.md` — directory overview.

## Status

Anchored. The theorem is proved by the same divmod argument as clause 3, with the `(qp, m_min)` parameters free. Verification: every `(d, qp, m_min)` group in the b = 10, n ∈ [2, 200], d ∈ [1, 7] sweep has predicted `n`-range equal to observed `n`-range — 46/46 groups, no exceptions. No open dependencies. The companion paper-inclusion case is independent of cabinet status.

The 27 residual `n²`-cancellation cells are *not* a dependency of this marvel — they fall under a different mechanism with its own structural condition (Beatty pattern-alignment, also verified 27/27 in the swept range), open characterisation, and separate provocation.

## Aesthetic note

TODO: aesthetic note (human)

## Provocation

- **Promote to clause 3′ in `paper/PAPER.md` §3.** `PAPER-INCLUSION.md` lays out the concrete edits — one clause line, one proof-sketch paragraph, one half-sentence in §5, one row in the §6 verification table, one footnote on the `n²`-cancellation residual. Independent of cabinet status; the marvel earns its space by being a closed-form sibling of an existing clause.
- **Close the `n²`-cancellation locus.** The 27 residual cells satisfy a single structural condition (`M_k(n)` and `M_k(n²)` extras patterns coincide bit-for-bit; both Beatty-shape spread-1) but the closed form for *which* `(b, n, d)` trigger that alignment is open. Likely Diophantine-approximation territory on `W/n` versus `W/n²`. Its own write-up if it lands.
- **Cross-base verification.** The sweep is at b = 10. The theorem statement is base-aware (the `(qp, m_min)` parameter family depends on `b, d`). A b ∈ {2, …, 16} sweep would either confirm the parameterisation generalises uniformly or reveal base-specific structure; either is informative.

## Cross-references

- `marvel-row-ogf-cliff.md` — the algebra side's marvel, also "found rather than built", also a closed form sliding into a pre-existing slot in the substrate's grammar. The Row-OGF Cliff terminates at `Ω(k') + 1` because the kernel-zero theorem forces it; Generalised Family E generalises clause 3 because the divmod-and-strip argument can run with the parameters free. Both are *the substrate paying out tighter than the construction promised*.
- `monster-lcm-not-factorial.md` — denominator side's monster, the offence trace-back to "why the bound is sharp." Generalised Family E is on the opposite aesthetic register: where the lcm denominator is forced-and-uglier, this is forced-and-cleaner.
- `curiosity-two-tongues.md` — empirical-side observation about sub-population structure inheriting from a parent. Generalised Family E is its substrate-side analogue: the lucky locus's structure is *visible* once the right parameter coordinates are chosen.
- (forthcoming, if/when promoted) — `paper/PAPER.md` §3 clause 3′ and §5.2 proof sketch.

## Discovery context

The substrate-phase work began as an "experimental wing" for what `paper/WORKSET.md` listed as "lucky-cancellation locus uncharacterised" — out of scope for the JStatSoft submission, but the empirical content was there. `phase_diagram.py` rendered the b = 10 sweep as a (n, d) cell grid coloured by which substrate clause was load-bearing; the 96 lucky cells lit up as a distinct band outside the proven regimes.

`analyze_lucky.py` then split the lucky cells by mechanism. Cells where `M_k(n)` was already constant across strips (no `n²`-correction needed for atom uniformity) were one group; cells where `M_k(n)` varied but the `n²`-correction balanced were another. The first group's structure was already visible — the integer multipliers `[m_min, m_max]` partition into `b−1` equal blocks of length `qp`. Writing that down gave the four hypotheses. Computing the predicted `n`-range from `(qp, m_min)` and comparing to observed cells: agreement on the first group exact, the second group cleanly identifying as the residual.

The verification iteration did surface one parameter trap: the original prediction formula used `m_max = m_min + q(b−1) − 1` where `q` was the *atom* count. At `d ≥ 5` cells where `n²` lies inside the block uniformly, `qp ≠ q` (multiplier count exceeds atom count by `δ`). Switching to `m_max = m_min + qp(b−1) − 1` gave 46/46 group-match. The fix moved the theorem from "predicts most groups" to "predicts every group" — the kind of one-parameter rename that turns a probe into a closed form.

The marvel reading came on writing the proof sketch: it was the same three-step argument as clause 3 (in-block range, per-strip leading-digit alignment, sieve removes `δ` per strip), with `qp` and `m_min` free instead of fixed at `1` and `⌈W/n⌉`. The *fit* of the generalisation to clause 3's existing slot in the substrate theorem is what tipped this from "experimental finding" to "marvel" — the theorem doesn't ask for a new mechanism, it asks for the existing clause's parameters to be unconstrained.
