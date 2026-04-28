# STRUCTURE-HUNT — what we go looking for after graduation

The four-coordinate decomposition in `ACM-MANGOLDT.md` is a working
hypothesis. The two scans (`CUTOFF-SCAN.md`, `PAYLOAD-SCAN.md`)
test whether the local and truncation coordinates are independent
observables. Once those land — graduate or fall — there is a
structure-hunt program the experimental apparatus is positioned
to run.

This document is the proposal. Priorities can shift as Phase 1
results come in; the phase-structure is the spine.


## Phase 1 — graduation (current)

Run `CUTOFF-SCAN`, then `PAYLOAD-SCAN`. The two outcomes determine
which coordinates are first-class.

| outcome | implication for Phase 2+ |
|---|---|
| both graduate | full decomposition. Phase 2–5 in sequence. |
| cutoff graduates, payload falls | local coordinate folds back into height; Phase 2 collapses to a single-axis interaction with cutoff. |
| payload graduates, cutoff falls | residuals are local; Phase 3 / Brief 4 prediction simplifies but the truncation arc closes. |
| both fall | the four-coordinate model is wrong and Phase 2 is moot. Hunt resumes from the residuals, not from the lines. |

Phase 1 is the gate. Nothing below assumes more than what
Phase 1 returns.


## Phase 2 — interaction matrix

If both scans graduate, the next question is whether the
coordinates are additively separable or whether they couple.
Three pairwise interaction tests, each a small extension of the
Phase 1 scan infrastructure:

| interaction | scan extension |
|---|---|
| height × payload-τ_2 | extend `PAYLOAD-SCAN` to sweep `h ∈ {2, 3, 4}` at fixed `(n, Y-bucket)`. Tests whether the U-shape's bucket boundaries shift with `h`. |
| payload × cutoff-τ_2 | joint scan: at fixed `n`, sweep both payload τ_2 and cutoff τ_2 on a grid. Tests whether the two coordinates' effects compose additively or multiplicatively. |
| block-type × cutoff | extend `CUTOFF-SCAN` to compare smooth and uncertified `m` at matched cutoff buckets. Tests whether the L4d gap-growth survives at fixed `(n, m)`. |

The interaction matrix is the first place the spectroscopic
framing pays off — clean cross-terms or selection rules would mean
the lines decompose into modes whose product structure is itself
predictable. Heavy interactions mean the coordinates are not the
primitives; some coupled basis is.


## Phase 3 — cross-experiment validation

Three other places in the repo should be predictable from the
four-coordinate model, each a separate confirmation. Phase 3 can
run in parallel with Phase 2 once Phase 1 graduates.

### Brief 2 cross-check (CF spikes)

`experiments/acm-champernowne/base10/cf/SPIKE-HUNT.md` reports
that mega-spike magnitudes scale as
`(b−1)² · b^(k−2) · (n−1) · k / n²`. The `(n−1)/n²` factor *is*
payload divisor density expressed differently. If the
spectroscopy is real, the CF spike formula should be derivable
from the four-coordinate model — the Mahler-style rational
approximant at the d=k boundary in `C_b(n)` corresponds to a
specific `(m, X)` pair whose `ρ` should sit on a known coordinate
line.

The pass/fail: does the empirical CF spike fit
`(b−1)² · b^(k−2) · (n−1) · k / n²` come out of the coordinate
model with an explicit mapping, or is it a parallel finding that
happens to use the same density factor?

### Brief 4 prediction (BPPW MC)

`EXPERIMENTAL.md` Brief 4 (rewritten) asks for the shape of
`M_n(N) · Φ(N) / N`. If the four coordinates govern `Λ_n` flow
on `M_n`, they should also govern the multiplication-table count
via the same poset structure. **Predict before measuring** — write
down what shape the four-coordinate model says `M_n(N)` should
take, then run BPPW MC and compare. A model that survives a
prediction across an entirely different observable is what
"earns its keep" looks like.

### Cross-base

The closed form `Λ_n(m) = log m · Σ (−1)^(j−1) τ_j(m/n^j)/j` is
base-agnostic. The h=2 cliff `τ_2(m/n²) ≥ 3 ⇒ Λ_n < 0` is
base-agnostic. But the cutoff `τ_2(Y)` signal, the witness-count
scout, and the smooth/Family E partition all interact with
base-specific sieve geometry through `SIEVES.md` and
`ULAM-SPIRAL.md`.

Run the same tomography in base 2 and base 12. The local
coordinate should be base-invariant; the cutoff coordinate should
be base-dependent in a *structured* way (specific scaling with
`b`, predictable from the closed form). That's a clean test of
which lines are intrinsic to the monoid and which are
positional-arithmetic artefacts.


## Phase 4 — predictive model

If Phases 1–3 land, the four coordinates are independently
observable, interactions are catalogued, and cross-experiments
agree. The final test is predictive: build a model that takes
`(h, payload τ_2, cutoff scout, block type)` and predicts `ρ`,
with quantified residuals.

Method discipline:

- the model is *prespecified*; no adjusting after seeing
  residuals;
- use bucket-level features only (matches the discipline
  in `ACM-MANGOLDT.md`);
- residuals are evaluated with the same shape-agnostic ξ
  and matched-bucket toolkit, against the held-out `Λ_n`,
  cross-base, Brief 2, Brief 4 datasets;
- a clean residual structure (all bias absorbed by the four
  coordinates plus their Phase-2 interactions) confirms the
  spectroscopy. Structured residuals point at Phase 5.


## Phase 5 — missing lines

If Phase 4 leaves systematic residuals, the structure hunt
becomes: find the coordinate that explains them. Candidates
already in the repo:

- `ν_p(n)` for each prime `p | n` (the prime-vs-composite-n
  asymmetry suggests this matters but it's not a coordinate yet);
- smallest-prime-factor of `m` (the cheapest-sieve scout);
- the Λ-on-A_n positivity locus from the previous-turn
  discussion (whether the *original-Λ* on the n-prime atoms
  themselves controls anything beyond the monoid-Λ);
- the digit-class boundary structure from `BLOCK-UNIFORMITY.md`
  beyond just smooth/Family-E/uncertified — specifically the
  spread-≤2 quantitative correction.

Each is a probe that hasn't been read into the model. Phase 5
is candidate-by-candidate, with the same controlled-source
discipline as Phase 1.


## Selection rules

A spectroscopic instrument doesn't just measure lines. It
catalogues which transitions are allowed and which are forbidden.
For us, "selection rules" are the (h, payload, cutoff, block)
combinations that exhibit specific coordinate signatures.
Examples worth looking for:

- **dark cells** — combinations where ρ ≈ 0 (no truncation defect
  beyond the universal `−1/(m log X)` term). If these cluster on
  a clean rule (e.g., "smooth m-block + low cutoff τ_2 + low
  payload τ_2"), the rule is a finding.
- **bright cells** — most-negative ρ. Likely cluster on the
  composite-n + high-cutoff-witness corner; whether they cluster
  *only* there is the test.
- **excluded shapes** — combinations the model says cannot
  produce a U-shape on the Λ_n side. Test by attempting to find
  a witness in the L1 data.

Selection rules are a Phase-4 byproduct: once the predictive
model is in hand, the rules fall out of where the model says
ρ has zeros, extrema, or sign reversals. Catalogue them as
a separate output.


## Sequencing summary

```
Phase 1   graduation               (current; CUTOFF, then PAYLOAD)
Phase 2   interaction matrix       (gate: both Phase 1 scans graduate)
Phase 3   cross-experiment val.    (parallel to Phase 2)
Phase 4   predictive model         (gate: Phases 2, 3 land)
Phase 5   missing lines            (gate: Phase 4 leaves residuals)
selection rules                     (Phase 4 byproduct)
```

Phase 1 is the only commitment. Phase 2+ shift in scope and
priority based on Phase 1 outcomes; this document is the
provisional plan, not a contract.


## Files (planned, beyond Phase 1)

| file | role | phase |
|---|---|---|
| `interaction_grid.py` | joint payload × cutoff scan | 2 |
| `cross_base.py` | re-run tomography in base 2 and 12 | 3 |
| `brief2_crosscheck.py` | CF spike formula derivation from coordinate model | 3 |
| `brief4_predict.py` | predicted `M_n(N) · Φ(N) / N` shape from coordinates | 3 |
| `predictive_model.py` | bucket-level model fit + residual analysis | 4 |
| `STRUCTURE-HUNT.md` | this document | (any) |


## Coupling

- **`ACM-MANGOLDT.md`** — the four-coordinate decomposition under
  test.
- **`CUTOFF-SCAN.md` / `PAYLOAD-SCAN.md`** — Phase 1 scans.
- **`EXPERIMENTAL.md` Brief 2 and Brief 4** — Phase 3 cross-checks.
- **`core/BLOCK-UNIFORMITY.md`** — block partition for the
  totalisation coordinate.
- **`experiments/acm-champernowne/base10/cf/SPIKE-HUNT.md`** —
  Brief 2 source of the (n−1)/n² scaling formula to predict.
- **`experiments/acm/diagonal/cheapest_sieve/README.md`** — scout
  vocabulary used across all phases.


## What this is not

- Not a replacement for `ACM-MANGOLDT.md` or the two scan briefs.
  Those are the present-tense work; this is forward-look.
- Not a commitment to Phases 2–5 in order. The phase order is
  the assumption-stack; if Phase 1 falls, the stack collapses
  and the hunt resumes from residuals.
- Not a claim that the four-coordinate model is right. It is a
  research program that takes the model seriously enough to test
  it across multiple observables.
