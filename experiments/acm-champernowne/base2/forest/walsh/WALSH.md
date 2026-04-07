# Walsh Spectrum

Expedition 9 of [MALLORN-SEED.md](../MALLORN-SEED.md).

This folder asks what the Walsh-Hadamard transform can see in binary
ACM-Champernowne streams that the rest of the forest does not.

The answer is now fairly tight:

- there are **44** coefficient-level Walsh signals that survive a
  defensible robustness bar
- **all 44 die under entry-order shuffle**
- the 44 split into three populations:
  - `9` reproducible from length sequence plus `v_2(n)`
  - `15` reproducible from length sequence alone
  - `20` reproducible by neither synthetic control
- under the strictest bar, the stable core is **`30`, `246`, `255`**

The main transportable insight is simple: Walsh is reading the order in
which the binary entries are laid down, not just their marginal bit
content and not just the `v_2(n)` barcode.

## Portable Claims

These are the claims from this experiment that are stable enough to move
elsewhere in the repo.

1. Binary ACM streams have a real higher-order Walsh signature at the
   coefficient level.
2. Entry order is the dominant discriminator in that signature:
   shuffling the same entries destroys all 44 robust cells.
3. Walsh decomposes the signal into three populations:
   `length + v_2`, `length-only`, and `neither control reproduces`.
4. `v_2(n)` still matters, but it explains only a minority of the Walsh
   family.
5. Chunk-size stability is a stronger filter than phase stability.
6. Boundary conditioning at `k=8` is inconclusive because every chunk is
   already boundary-rich.

If another doc only needs the result and not the proof structure, those
six lines are the ones to lift.

## Setup

For a `2^k`-bit chunk mapped to `{-1,+1}`, the Walsh coefficient at
subset `S` is

```
W[S]  =  (1 / 2^k) · Σ_x  f(x) · (−1)^(|S ∩ x|)
```

and the experiment works with power

```
P[s] = mean over chunks of |W[s]|^2
```

The base run is:

- monoids `n = 2..32`
- about `2·10^6` bits per monoid
- non-overlapping 256-bit chunks (`k = 8`)
- transform via `scipy.linalg.hadamard(256)`

With this normalization:

- Parseval gives `Σ_s |W[s]|^2 = 1` for every chunk
- fair Bernoulli bits give `E[|W[s]|^2] = 1/256`

The source-of-truth artifacts are:

- [walsh_spectra.npz](walsh_spectra.npz)
- [walsh_upgrade_stage0.csv](walsh_upgrade_stage0.csv)
- [walsh_upgrade_table.csv](walsh_upgrade_table.csv)

## Robustness Ladder

The analysis uses four nested levels.

| level | criterion | count |
|---|---|---:|
| robust | `count >= 25`, `CV < 0.25`, `z >= 3` | 44 |
| tier 1 | also: above baseline in all 31 monoids | 9 |
| tier 2 | also: phase-stable | 9 |
| tier 3 | also: persists at some alternative chunk size | 3 |

The tier-1 set is:

`30, 69, 71, 143, 162, 163, 180, 246, 255`

The tier-3 core is:

`30, 246, 255`

That three-cell core is useful because it keeps one representative from
each control population:

| cell | length-ctrl | `v_2`-ctrl | interpretation |
|---|---|---|---|
| `255` | yes | yes | length + `v_2` explainable |
| `246` | yes | no | length-only explainable |
| `30`  | no  | no | ACM-specific under current controls |

## Control Split

The 44 robust cells separate cleanly under the controls:

| group | length-ctrl | `v_2`-ctrl | shuffle | count | reading |
|---|---|---|---|---:|---|
| length + `v_2` explainable | yes | yes | no | 9 | leading-1 + trailing-zero geometry |
| length-only explainable | yes | no | no | 15 | length-sequence geometry beyond `v_2` |
| neither control reproduces | no | no | no | 20 | order-dependent interior structure |

Two points matter most.

First, the `9 / 15 / 20` split is genuinely useful. It tells us Walsh is
not finding one undifferentiated phenomenon.

Second, **all 44 rows still show `shuffle = no`**. That is the cleanest
single result in the file. Whatever these cells encode, they depend on
the original concatenation order.

## What Still Tracks `v_2(n)`

Some cells do behave the way the earlier framing of the experiment
expected. The strongest `v_2(n)` correlations in the robust family are:

| cell | corr with `v_2(n)` |
|---|---:|
| `172` | +0.52 |
| `22`  | +0.51 |
| `244` | +0.45 |
| `30`  | +0.43 |
| `182` | +0.42 |
| `180` | +0.38 |

This is the part of the Walsh spectrum that translates the binary
structure already known from Hamming Strata, run geometry, and
HAMMING-BOOKKEEPING.

But this is not the dominant Walsh story. The brightest robust cells are
`69, 71, 162, 163, 255`, and all of them sit near zero correlation with
`v_2(n)`.

So `v_2(n)` is one organizing variable in Walsh-space, not the master
variable.

## Phase And Chunk-Size Filters

Two stability tests matter after the robust bar.

### Phase

The spectrum was recomputed at 32 sampled chunk origins:

`0, 8, 16, ..., 248`

Result:

- `37 / 44` robust cells survive phase averaging
- only `7` fail: `77, 105, 127, 142, 154, 218, 219`

So most of the robust family is not a single-origin artifact.

### Chunk size

The spectrum was recomputed at `k ∈ {6, 7, 9, 10}` using support-mapped
analogues of the `k=8` cells.

Result:

- only `18 / 44` robust cells persist at any alternative `k`

This is more discriminating than phase. In practice the chunk-size sweep
is the sharpest structural filter after shuffle.

That is why the tier-3 core matters. It is the part of the family that
survives robustness, uniformity, phase, and at least one alternative
window size.

## Boundary Test At `k=8`

The intended boundary split was by chunk class:

- `0` entry boundaries
- `1` entry boundary
- `>=2` entry boundaries

At `k=8`, this is degenerate. Average entry length is around 17 bits, so
every 256-bit chunk already contains many boundaries. Only the `>=2`
class is populated.

So the current boundary stage does **not** separate interior structure
from boundary structure. The right way to answer that question is to
rerun boundary conditioning at `k=4` or `k=5`.

## What This Establishes

1. Walsh sees real higher-order structure in binary ACM streams.
2. That structure is not exhausted by the `v_2(n)` story.
3. Entry order matters for every robust cell we found.
4. About half the robust family is generic to binary length geometry.
5. About half is not reproduced by the current synthetics.
6. Chunk-size persistence is a stronger discriminator than phase
   stability.

That is the result in its most compact form.

## Best Targets For Reuse

If another doc needs concrete named objects from this experiment, these
are the most useful.

- **The 44-cell robust family.**
  This is the broad result.
- **The 9 tier-1 cells.**
  These are uniformly elevated across all 31 monoids.
- **The tier-3 core `30, 246, 255`.**
  These are the best exemplars of the three control populations.
- **Cell `30`.**
  This is the cleanest current example of ACM-specific Walsh structure:
  robust, tier-3, and unreproduced by either synthetic.

## Auditing the summaries

Every Walsh artifact in this folder comes in two forms: a summary
(CSV or markdown table) and the underlying `.npz` it was generated
from. The `.npz` files are kept on disk so any claim made from a
summary can be checked against the numerics it was derived from.

The reason this matters concretely: an earlier reading of this
experiment concluded the inverse of conclusion 4 above — that the
Walsh higher-order signal was just `v_2(n)` rewritten, with nothing
beyond what Hamming Strata already accounted for. The summary that
supported that conclusion was internally consistent and looked
clean. The disagreement only became visible when the per-coefficient
spectrum was read directly from
[walsh_spectra.npz](walsh_spectra.npz). The brightest robust cells
(`69, 71, 162, 163, 255`, all near zero correlation with `v_2(n)`)
were not visible through the summary at all. Summarization had
destroyed the information needed to make the right call.

A better-designed summary might have caught that. In this case it
didn't, and the policy here is not to depend on summary design. The
per-coefficient arrays stay on disk; the summaries are the
convenient read, the `.npz` files are the audit trail behind them.
The audit is deliberately not automated: any automated check over
the `.npz` files would itself be a summarization scheme with its
own blind spots, and what the trail provides is human or agent
attention to the underlying numerics.

### Which file audits which claim

| claim type | summary | underlying `.npz` | what the summary collapses |
|---|---|---|---|
| robust-set membership | `walsh_upgrade_table.csv` | [`walsh_upgrade_stage0.npz`](walsh_upgrade_stage0.npz) | `pooled, ci, cv, z` for *all* candidates, not just survivors |
| `phase: yes/no` | upgrade table | [`walsh_phase_sweep.npz`](walsh_phase_sweep.npz) | the 32-offset × 31-monoid × cell cube |
| `k-stable: yes/no` | upgrade table | [`walsh_chunk_size_sweep.npz`](walsh_chunk_size_sweep.npz) | per-cell power at each `k ∈ {6, 7, 9, 10}` and the support mapping |
| boundary: "degenerate" | `walsh_upgrade_results.md` | [`walsh_boundary_conditioned.npz`](walsh_boundary_conditioned.npz) | the actual numerics inside the populated `2+` class |
| `length / v_2 / shuffle` calls | upgrade table | [`walsh_controls.npz`](walsh_controls.npz) | per-monoid effect sizes; the yes/no hides margin |
| phase × boundary interaction | not in any summary | [`walsh_phase_boundary.npz`](walsh_phase_boundary.npz) | a 4D `(offset × monoid × class × cell)` cube the summaries do not mention |

[walsh_spectra.npz](walsh_spectra.npz) is the source-of-truth full
spectrum at `k=8` and is the right starting point for any new
analysis, or for any disagreement with a summary.

## Method Note

Two methodological choices are worth carrying forward.

1. The unit of analysis must be the **coefficient**, not the popcount
   bucket. The bucket averages are too coarse and under-read the real
   signal.
2. Split-half equality is not the right filter for this stream family.
   The first and second halves of an ACM stream sample systematically
   different entry regimes, so a strict split-half consistency test
   confuses non-stationarity with noise.

Everything in this doc is therefore stated at coefficient level and
grounded in the `npz` and CSV artifacts above.

## Open Questions

1. **What does cell `30` encode?**
   It is the strongest current ACM-specific target.
2. **Which cells survive an independently-derived cross-`k` pipeline?**
   The mapped-support sweep is useful, but a full re-run at each `k`
   would be stronger.
3. **What happens to the family under boundary conditioning at `k=4`
   or `k=5`?**
   That is the missing boundary test.

## See Also

### Scripts and data

- [walsh.py](walsh.py)
- [walsh_upgrade.py](walsh_upgrade.py)
- [walsh_visuals.py](walsh_visuals.py)
- [walsh_spectra.npz](walsh_spectra.npz)
- [walsh_upgrade_stage0.csv](walsh_upgrade_stage0.csv)
- [walsh_upgrade_table.csv](walsh_upgrade_table.csv)
- [walsh_upgrade_results.md](walsh_upgrade_results.md)

The per-stage `.npz` files (`walsh_phase_sweep`, `walsh_chunk_size_sweep`,
`walsh_boundary_conditioned`, `walsh_controls`, `walsh_phase_boundary`,
`walsh_upgrade_stage0`) are indexed in the *Auditing the summaries*
section above with the claim each one underwrites.

### Plots

Robustness — how the 44-cell family was filtered:

- [plots/robustness/walsh_survival_cascade.png](plots/robustness/walsh_survival_cascade.png)
- [plots/robustness/walsh_robust_heatmap.png](plots/robustness/walsh_robust_heatmap.png)

Interpretation — what the surviving cells encode:

- [plots/interpretation/walsh_tier1_core.png](plots/interpretation/walsh_tier1_core.png)
- [plots/interpretation/walsh_brightness_vs_v2.png](plots/interpretation/walsh_brightness_vs_v2.png)

### Related docs

- [HAMMING-BOOKKEEPING.md](../../HAMMING-BOOKKEEPING.md)
