# substrate-phase — exactness landscape of the n-prime block counts

The BIDDER paper (`paper/PAPER.md`) proves a five-clause substrate
theorem: leading-digit counts of n-prime atoms on the digit-class
block `B_{b,d} = [b^(d-1), b^d − 1]` are exact in two regimes
(smooth-sieved when `n² | b^(d-1)`; Family E for
`n ∈ [b^(d-1), ⌊(b^d − 1)/(b − 1)⌋]`) and bounded by spread ≤ 2
universally. The paper states what's true and moves on. This
directory maps **where each clause is load-bearing** across the
(n, d) parameter space at a fixed base.

## Scope

- Out of scope for the paper. WORKSET.md explicitly lists "lucky-
  cancellation locus uncharacterised" and the substrate's
  exactness-landscape mapping outside the proven bounds. This
  directory is the experimental wing for that work.
- Not load-bearing for the paper's submission. Findings here
  inform follow-up work, not the JStatSoft draft.

## What's here

- `phase_diagram.py` — sweeps (n, d) at fixed b = 10, classifies
  each cell by which substrate-clause is doing the work.
- `phase_diagram.png` — the rendered diagram.

## Cell classes

For each (n, d) at b = 10, the cell is one of:

| class | meaning | clause |
|---|---|---|
| empty | `B_{b,d}` contains no n-prime atoms | — |
| smooth | `n² ∣ b^(d−1)`; exact uniformity | clause 2 |
| family_e | `n ∈ [b^(d−1), ⌊(b^d−1)/(b−1)⌋]`; one per digit | clause 3 |
| lucky | spread = 0 with neither clause applying | (clause 4 ≤ bound is not tight) |
| spread_1 | spread = 1 | clause 4 realised |
| spread_2 | spread = 2 | clause 4 realised at the bound |

The "lucky" class is the experimental target. The paper's
clause 4 says spread ≤ 2 universally; it doesn't characterise the
*equality* and *zero* cases. Those characterisations would be a
small follow-up theorem; this experiment maps the locus.
