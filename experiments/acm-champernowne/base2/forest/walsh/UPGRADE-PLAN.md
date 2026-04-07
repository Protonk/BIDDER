# Walsh Upgrade Plan

The current Walsh result has two halves:

- part of the spectrum tracks `v_2(n)`
- another part is persistently elevated across monoids and does not
  obviously track `v_2(n)`

The mechanism for the second half is open. Four candidates:

1. chunk-grid artifact
2. boundary-geometry effect
3. generic binary-concatenation effect
4. ACM-specific higher-order signature

These are not mutually exclusive. The universal cells could come from
a combination, and the experiments below narrow rather than pick a
single winner.

## Working principles

- [walsh_spectra.npz](walsh_spectra.npz) is the source of truth for the
  current `k=8` run. New runs save raw arrays first, plots second.
- Compare at the coefficient level, not by popcount buckets alone.
- Sharpen what we have before running anything new.

## Robustness bar

Every spectrum reported by every stage must come with all four of:

- **Split-half agreement.** Compute the spectrum on the first and
  second halves of each monoid's chunk set independently and require
  per-cell agreement within bootstrap intervals.
- **Bootstrap CI.** Resample chunks with replacement and report a
  per-cell 95% interval.
- **Per-cell z-score** against a matched white-noise null (fair `±1`
  bits, same chunk count). Threshold for "elevated": `|z| ≥ 3`
  (starting value, tunable).
- **Cross-monoid agreement.** For a cell to count as "universal", its
  coefficient of variation across monoids must be `< 0.25` (starting
  value, tunable).

The robust set is the cells that pass all four. Every later stage
analyzes that set and only that set.

A cell that fails any of these is treated as noise. If the first
application of this protocol leaves only a small number of robust
universal cells, keep all survivors and treat the result as a
low-cardinality regime rather than as a failed experiment. In that
case Stage 1 becomes more important, not less, because the remaining
question is whether the survivors are stable stream structure or
chunking artifacts.

## Stage 0: Sharpen the existing data (no rerun)

Both 0A and 0B re-use [walsh_spectra.npz](walsh_spectra.npz) and
operate on the robust set produced by the robustness bar.

**0A. Support-geometry classification.** Label each robust cell by
the shape of its bit mask (contiguous, alternating, low/high-bit-heavy,
edge-loaded). Look for shared geometry within the universal family.

**0B. Sequency-ordered replot.** Replot the spectrum sorted by
sequency rather than popcount. Sequency may group the universal
family cleanly when popcount does not.

## Stage 1: Test chunking and boundary mechanisms

Determine whether the universal cells are intrinsic to the stream or
induced by the chunking choice.

**1. Phase sweep.** Repeat at chunk origins `r = 0..255` (or a dense
sample) with `k=8` fixed. Hot cells that move or collapse with phase
are chunk-grid artifacts; cells that survive phase-averaging are
intrinsic at this scale.

**2. Chunk-size sweep.** Repeat for `k ∈ {6, 7, 9, 10}`. Phase tests
*where* the window starts; size tests *how big* it is. Together with
1, these discriminate "chunk choice" from "stream property".

**3. Boundary-conditioned chunks.** Annotate each chunk by entry-
boundary count (0, 1, ≥2) and compute spectra per class. Concentration
in boundary-rich chunks points to concatenation geometry; persistence
in boundary-poor chunks points to intrinsic interior structure.

**4. Phase × boundary interaction.** Combine 1 and 3. Strong phase
dependence only in boundary-rich chunks points to chunk-boundary
coupling. Run only if 1 and 3 each show non-trivial structure on
their own.

## Stage 2: Source separation via controls

Once mechanism candidates are narrowed, separate ACM structure from
generic binary-concatenation effects.

**Calibration first.** Before trusting any control in this stage,
verify the synthetic-stream pipeline reproduces a known closed-form
Walsh spectrum on a known-good input (a fair-coin stream gives
`P[s] = 1/256` to within bootstrap CI). A control with a buggy
generator is worse than no control.

**5. Length-matched synthetic.** Concatenate random binary words with
the same entry-length distribution and the leading-1 constraint, no
ACM arithmetic. Universal cells lighting up here means they are
generic positional-length geometry, not ACM-specific.

**6. `v_2`-preserving synthetic.** As in 5, but also preserve each
entry's guaranteed trailing-zero count. If the `v_2`-tracking cells
survive and the universal cells vanish, the two populations are
cleanly separated.

**7. Entry-order shuffle.** Keep the multiset of ACM entries for a
monoid but randomize concatenation order. Tests whether arithmetic
progression order matters versus the entry library alone.

## Stage 3: Consolidation table

Synthesize Stages 0–2 into a single result table. Rows are cells in
the robust set. Columns, in this order:

| field | source | meaning |
|---|---|---|
| `s` | — | Walsh subset index |
| `popcount` | — | `|S|` |
| `mean P[s]` | initial run | average power across monoids |
| `ratio` | initial run | `mean P[s] · 256` |
| `corr v_2` | initial run | Pearson correlation with `v_2(n)` |
| `geometry` | 0A | mask shape class |
| `sequency` | 0B | sequency-order rank |
| `phase` | Exp 1 | survives phase averaging? |
| `k-stable` | Exp 2 | stable across chunk sizes? |
| `boundary` | Exp 3 | concentration class (0 / 1 / ≥2) |
| `length-ctrl` | Exp 5 | survives length-matched control? |
| `v_2-ctrl` | Exp 6 | survives `v_2`-preserving control? |
| `shuffle` | Exp 7 | survives entry-order shuffle? |

Each row is one cell's full provenance. The result memo is one
paragraph describing what the columns say across the robust set.
Disagreements between columns are themselves the finding.

The table format is fixed in advance. Every stage must produce data
in a form that fits its assigned column.

## Mechanism map

| hypothesis | discriminating experiments |
|---|---|
| 1. chunk-grid artifact | 1, 2 |
| 2. boundary geometry | 3, 4 |
| 3. generic binary concatenation | 5, 6 |
| 4. ACM-specific | 6, 7 |

## Stopping rules

- If the robustness bar leaves only a few universal cells, continue
  with those survivors. Do not treat low cardinality by itself as a
  reason to abandon Stage 1.
- If Stage 1 shows all survivor cells collapsing under phase or
  chunk-size variation, mark the claimed universality as chunk-choice
  dependent at the tested scales and consolidate. Stage 2 becomes
  optional confirmation, not a requirement.
- If a Stage 2 control reproduces the survivor cells closely, those
  cells are not strong evidence of ACM-specific structure; consolidate
  and stop.
- The upgrade is also "done" the moment Stage 3's table can answer,
  for each robust cell, whether it survives phase averaging, boundary
  stratification, and at least one non-ACM control. Pending
  secondary analyses do not block the result memo.

## Implementation notes

- Save raw spectra to new `.npz` files at every stage.
- All bootstraps and synthetic streams use a fixed random seed
  recorded in the script header.
- Track the same robust cell set across all stages so comparisons
  are apples-to-apples.
- Stage 0 re-uses saved data; Stages 1–2 are new runs.
