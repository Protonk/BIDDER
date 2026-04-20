# F2 contrast — results

Run: `run_f2_contrast_torus.py` + `run_f2_contrast_tree.py` +
`analyze_f2_contrast.py` (2026-04-19).

Outputs:

- `sim/f2_contrast_results/torus/{full,alt}_N1e{5,6,7}.npz`
- `sim/f2_contrast_results/tree/{full,alt}_tree.npz`
- `sim/f2_contrast_results/analysis.npz`

## Headline

The plan's soft prior for the odd-`L` torus was wrong. `Z^2` does
**not** land near `r = 1`. It lands at essentially **`r = 2`**:
alternating takes about twice as many steps as the full torus walk
to reach the same `L1` threshold.

The free-group tree sanity check lands exactly where expected:
full-walk drift is `~0.5`, alternating drift is `1.0`, so the
time-ratio convention gives **`r ~ 0.5`**. Alternating is 2x
faster on `F_2`.

So the three-group contrast is:

| group / observable | time ratio `r = n_alt / n_full` | interpretation |
|:-------------------|:-------------------------------:|:---------------|
| `BS(1,2)` / mantissa `L1` | `~1.15` | modest slowdown |
| `Z^2` odd torus / cellwise `L1` | `~2.0` | strong slowdown |
| `F_2` tree / word-length drift | `~0.5` | strong speedup |

That is a genuine group-dependent contrast. It is **not** a clean
story of "more free means less penalty," and it is certainly not
evidence isolating `bab^{-1} = a^2` as the cause of the BS(1,2)
number.

## Torus result

Parameters:

- `L = 31`
- `N in {10^5, 10^6, 10^7}`
- `n_max = 2000`
- sample every 10 steps
- `theta_N ~= sqrt(2 L^2 / (pi N))`

Measured ratios:

### `N = 10^5`

| `k` | `theta_k` | `n_full` | `n_alt` | `r` |
|---:|---:|---:|---:|---:|
| 5.0 | `3.9109e-01` | 290 | 580 | 2.000 |
| 3.0 | `2.3465e-01` | 400 | 790 | 1.975 |
| 2.0 | `1.5643e-01` | 490 | 980 | 2.000 |
| 1.2 | `9.3861e-02` | 690 | 1320 | 1.913 |

### `N = 10^6`

| `k` | `theta_k` | `n_full` | `n_alt` | `r` |
|---:|---:|---:|---:|---:|
| 5.0 | `1.2367e-01` | 510 | 1010 | 1.980 |
| 3.0 | `7.4203e-02` | 620 | 1220 | 1.968 |
| 2.0 | `4.9469e-02` | 710 | 1430 | 2.014 |
| 1.2 | `2.9681e-02` | 900 | 1770 | 1.967 |

### `N = 10^7`

| `k` | `theta_k` | `n_full` | `n_alt` | `r` |
|---:|---:|---:|---:|---:|
| 5.0 | `3.9109e-02` | 730 | 1460 | 2.000 |
| 3.0 | `2.3465e-02` | 840 | 1670 | 1.988 |
| 2.0 | `1.5643e-02` | 930 | 1860 | 2.000 |
| 1.2 | `9.3861e-03` | 1130 | censored by `n=2000` | — |

Cross-`N` stability is extremely tight for the uncensored rows:

- `k = 5.0`: max/min = `1.010`
- `k = 3.0`: max/min = `1.010`
- `k = 2.0`: max/min = `1.007`
- `k = 1.2`: max/min = `1.028` on the two uncensored panels

So the torus result is not only far from `1`; it is stably near
`2` across the whole sampled range.

## Tree sanity check

The tree run was implemented on the exact word-length process,
since the observable is `|X_n|` rather than the reduced word
itself:

- full walk: from length `> 0`, decrement with probability `1/4`,
  increment with probability `3/4`; from `0`, increment to `1`
- alternating walk: deterministic `|X_n| = n`

Fit on `n in [100, 500]`:

- `slope_full ~= 0.50019`
- `slope_alt  ~= 1.00000`
- implied time ratio `r = drift_full / drift_alt ~= 0.50019`

This matches the algebraic prediction almost exactly.

## Interpretation

The original hoped-for torus story was "close to `1` on `Z^2`,
close to `0.5` on `F_2`, and `1.15` on `BS(1,2)`." The actual
story is sharper and less convenient:

- `BS(1,2)` gives a mild slowdown
- `Z^2` gives a strong slowdown
- `F_2` gives a strong speedup

So the sign and magnitude of the alternation penalty are genuinely
group-dependent, but not in a way captured by a simple
"non-abelian relation present or absent" slogan.

The torus result also means the proposed soft footnote

> "`Z^2` shows no measurable slowdown"

is dead. The honest footnote, if we use one at all, is:

> The effect of alternating-step sub-sampling is strongly
> group-dependent: on `BS(1,2)` we measure a modest slowdown
> (`~1.15x`), on the odd torus `Z^2/(31Z)^2` a much larger
> slowdown (`~2x`), and on the free group `F_2` a speedup
> (`~0.5x` in time-ratio convention). We do not attempt a general
> classification here.

## Caveats

- The torus observable is `L1` to uniform on a finite abelian
  state space, not the mantissa statistic from `BS(1,2)`.
- The tree observable is drift, not `L1`, so it is a directional
  comparison rather than an apples-to-apples rate measurement.
- The `N = 10^7`, `k = 1.2` torus point is censored by
  `n_max = 2000`, but every shallower threshold already lands near
  `r = 2`.
- Actual runtime on the local M1 was closer to 8 minutes total
  than the plan's optimistic 5-minute estimate, dominated by the
  `N = 10^7` torus runs.
