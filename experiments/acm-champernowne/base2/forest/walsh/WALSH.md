# Walsh Spectrum

Expedition 9 of [MALLORN-SEED.md](../MALLORN-SEED.md). This folder uses
the Walsh-Hadamard transform to analyze fixed-size chunks of binary
Champernowne streams.

The current Walsh result has two layers:

- raw spectra contain many elevated high-order cells
- after an explicit robustness bar, the universal family collapses to a
  small stable core

That distinction is the main lesson of the upgraded analysis.

## Why Walsh

Walsh is the natural spectral basis for binary signals. Its basis
functions are XOR parities of subsets of bit positions:

```
W[S]  =  (1 / 2^k) · Σ_x  f(x) · (−1)^(|S ∩ x|)
```

For a `2^k`-bit chunk mapped to `{-1,+1}`, `W[S]` measures correlation
with the parity pattern indexed by subset `S`. The experiment works with
power,

```
P[s] = mean over chunks of |W[s]|^2
```

so elevated cells indicate Walsh patterns that recur reliably across the
stream.

With this normalization:

- Parseval gives `Σ_s |W[s]|^2 = 1` for every chunk
- fair Bernoulli bits give `E[|W[s]|^2] = 1/2^k`
- here `k = 8`, so the white-noise baseline is `1/256 ≈ 0.003906`

## Base Run

The base run is the original `k=8`, phase-0 experiment:

- monoids `n = 2..32`
- about `2·10^6` bits per monoid
- non-overlapping 256-bit chunks
- transform via `scipy.linalg.hadamard(256)`

The raw spectrum is saved in [walsh_spectra.npz](walsh_spectra.npz), and
the original plots remain:

- [walsh_orders.png](walsh_orders.png)
- [walsh_heatmap.png](walsh_heatmap.png)
- [walsh_high_order.png](walsh_high_order.png)

The upgraded analysis is driven by:

- [walsh_upgrade.py](walsh_upgrade.py)
- [walsh_upgrade_stage0.csv](walsh_upgrade_stage0.csv)
- [walsh_upgrade_table.csv](walsh_upgrade_table.csv)
- [walsh_upgrade_results.md](walsh_upgrade_results.md)

## Robustness Bar

The upgraded pass does not treat every hot cell in the raw heatmap as
equally meaningful. A cell counts as a robust universal candidate only if
it survives all of:

- elevation above baseline in at least `25/31` monoids
- cross-monoid coefficient of variation below `0.25`
- pooled `z >= 3` against the matched white-noise null
- split-half agreement within the bootstrap interval of the pooled
  estimate

Under that bar, the universal family is not dozens of cells. It is five.

## Robust Universal Cells

These are the cells that survive the full Stage 0 bar.

| cell `s` | popcount | geometry | sequency | mean `P[s]` | ratio vs baseline | corr with `v_2(n)` | monoids above baseline |
|---|---:|---|---:|---:|---:|---:|---:|
| 180 | 4 | mixed | 54  | 0.004969 | 1.272x | +0.377 | 31 |
| 214 | 5 | mixed | 77  | 0.004483 | 1.148x | -0.157 | 25 |
| 215 | 6 | edge-loaded | 178 | 0.004673 | 1.196x | -0.141 | 28 |
| 218 | 5 | mixed | 109 | 0.004446 | 1.138x | +0.122 | 25 |
| 246 | 6 | mixed | 74  | 0.004875 | 1.248x | +0.229 | 31 |

These are only mildly elevated in absolute size, but they are stable
enough across monoids and chunk resampling to survive the explicit bar.

Two consequences follow immediately:

- the brightest raw cells are not automatically the most trustworthy
  universal cells
- the surviving universal family is real, but much smaller than the
  raw heatmap suggests

## What Still Tracks `v_2(n)`

Walsh still sees part of the familiar binary ACM story. Some cells rise
with `v_2(n)` and behave like Walsh-language translations of structure
already visible in Hamming Strata, boundary effects, and run geometry.

That part of the spectrum is real, but it is not the whole story. The
robust universal cells above do not organize cleanly by `v_2(n)`.

## Phase And Chunk-Size Tests

The first question after Stage 0 is whether the robust cells are just
chunk-choice artifacts.

### Phase sweep

The upgrade re-ran the spectrum at 32 sampled chunk origins:

`0, 8, 16, ..., 248`

Four of the five robust cells survive phase-averaging under the same
universal-style criterion:

- `180`
- `214`
- `215`
- `246`

The pooled offset dependence is weak for all five survivors; their
offset-level coefficient of variation is only about `0.006` to `0.007`.

So the robust family is not explained by a single privileged chunk
origin.

### Chunk-size sweep

The upgrade also checked `k ∈ {6, 7, 9, 10}` using support-mapped
analogues of the `k=8` robust cells.

Persistence is limited:

- `215` persists at `k=6`
- `246` persists at `k=6`
- `218` persists at `k=9`
- `180` and `214` do not show a stable mapped analogue in the tested
  sizes

So the universal family is not scale-invariant. Some of it survives
rescaling, some of it does not.

## Boundary Test At `k=8`

The intended Stage 1 boundary split was by boundary count per chunk:

- `0`
- `1`
- `>=2`

At `k=8`, that split is degenerate. Every 256-bit chunk in the run
already contains multiple entry boundaries. In practice the populated
class is only `>=2`.

This means the `k=8` boundary-conditioned pass does **not** separate
interior structure from boundary structure. It only shows that the
survivors live on boundary-rich windows at that scale, which was
already inevitable given the chunk size.

So the boundary mechanism remains unresolved by the current window size.

## Control Results

Three controls were run against the robust family.

### 1. Length-matched synthetic

Control stream:

- same entry-length distribution
- same leading-1 constraint
- no ACM arithmetic

Result:

- `180` survives
- `246` survives
- `214`, `215`, `218` do not

So part of the robust family can be explained by generic binary
word-length geometry, but not all of it.

### 2. `v_2`-preserving synthetic

Control stream:

- same entry lengths
- same guaranteed trailing-zero count implied by `v_2(n)`
- randomized interior bits

Result:

- none of the five robust cells survive

So the robust family is not explained by trailing-zero constraints alone.

### 3. Entry-order shuffle

Control stream:

- same multiset of ACM entries
- randomized concatenation order

Result:

- none of the five robust cells survive

So original entry order matters for all five survivors. The effect is not
just “which entries appear”; it depends on how the stream is assembled.

### Fair-coin calibration

The synthetic pipeline was calibrated with fair `±1` chunks before the
controls were read. The per-cell calibration means land essentially on
the white-noise baseline, around `0.00389` to `0.00392`.

## Current Conclusion

The upgraded Walsh conclusion is:

1. Binary ACM streams do contain a small robust universal family of
   higher-order Walsh cells.
2. That family is not a pure `v_2(n)` phenomenon.
3. It is not a pure chunk-origin artifact either; most survivors persist
   under phase averaging.
4. It is not cleanly scale-invariant across the tested chunk sizes.
5. It is not explained by `v_2`-style trailing-zero constraints alone.
6. It is partly reproducible from generic binary length geometry, but
   only for a subset of the survivors.
7. It is destroyed by entry-order shuffling, so stream order matters.

The most economical present reading is:

- there is a real higher-order Walsh effect
- it has more than one mechanism
- one part looks like generic binary-concatenation geometry
- another part depends on the original ACM ordering

## What Remains Open

Three things are still open.

1. **Boundary mechanism at the right scale.**
The `k=8` boundary split is too coarse to distinguish interior from
boundary contributions.

2. **Why these five cells.**
The robust survivors are now specific enough to study directly:
`180`, `214`, `215`, `218`, `246`.

3. **Whether there is a cleaner scale than `k=8`.**
The chunk-size sweep shows partial persistence, not a single clean
cross-scale family.

## See Also

- [walsh.py](walsh.py) — original script
- [walsh_upgrade.py](walsh_upgrade.py) — upgrade runner
- [walsh_spectra.npz](walsh_spectra.npz) — base raw spectrum
- [walsh_upgrade_stage0.csv](walsh_upgrade_stage0.csv) — Stage 0
  candidate and survivor metrics
- [walsh_upgrade_table.csv](walsh_upgrade_table.csv) — Stage 3
  provenance table for the robust family
- [walsh_upgrade_results.md](walsh_upgrade_results.md) — compact result
  memo from the upgrade run
- [walsh_sequency_heatmap.png](walsh_sequency_heatmap.png) — sequency
  reorder of the base heatmap
- [walsh_phase_sweep.npz](walsh_phase_sweep.npz) — sampled-origin phase
  sweep
- [walsh_chunk_size_sweep.npz](walsh_chunk_size_sweep.npz) — chunk-size
  sweep
- [walsh_boundary_conditioned.npz](walsh_boundary_conditioned.npz) —
  boundary-conditioned spectra at `k=8`
- [walsh_controls.npz](walsh_controls.npz) — Stage 2 controls
