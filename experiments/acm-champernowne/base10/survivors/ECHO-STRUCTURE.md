# Echo structure: the survivor digit-length bias is base-aware

The C_Surv mean-digit-length bias against the bundle has a deep,
self-similar echo structure across decades of K. Each new decade
brings a new echo. The structure persists across as many decades as
we are willing to compute — amplitude decays geometrically with
ratio ≈ 0.80 per echo, slow enough to remain visible at every
decade we have tested.

The deeper observation: this structure is the *natural* outcome.
Smooth convergence of a base-aware construction to a base-blind
limit would itself require a mechanism that suppresses the base.
The construction has no such mechanism. So the convergence inherits
base-10 structure, and "echoes forever" is what you get.

## Setup

For window `[n_0, n_0 + W − 1]` and per-stream truncation `K`, the
mean-digit-length bias is

```
ratio(K, n_0) = (L_surv / |Surv|) / (L_b_set / |Unique|)
```

where `L_surv` is the total decimal-digit length of survivor
integers, `|Surv|` the survivor count, `L_b_set` the digit length
of the unique bundle integers, and `|Unique|` their count. Bias
is `(ratio − 1) · 100%`. At `(W=9, n_0=2, K=400)` (the Two Tongues
panel) the bias is +1.0% (set basis).

Magnitude-level tracking ⇒ the bias should be small. The question
asked here: how does it behave as K varies across many decades?

## The observation

Sweeps at `W = 9` over `K ∈ [10, 500000]` (combined low-K, dense,
large-K, and extended grids; ~12000 cells total). For small n_0,
the bias is *not* a smooth decay. It has four (and counting)
distinct peaks, each centered at a power-of-ten K.

```
n_0    main K   e1 K     e2 K       e3 K
  2      160    1640     16000      160000
  3      160    1640     16000      160000
  5      140    1370     14000      140000
  8      110     980     10000      100000
 12       90     720      7500       75000
```

Each echo sits at ~10× the previous in K. Peak amplitudes (set
basis):

```
n_0    main %   e1 %    e2 %    e3 %    decay ratio (e_n / e_(n−1))
  2    +2.68   +2.13   +1.75   +1.46    ≈ 0.80
  3    +3.68   +2.87   +2.34   +1.96    ≈ 0.80
  5    +3.24   +2.14   +1.79   +1.49    ≈ 0.81
  8    +2.45   +1.63   +1.31   +1.09    ≈ 0.81
 12    +1.13   +1.01   +0.70   +0.59    ≈ 0.86
```

Detection method: combined-cache local-maxima search with a 5%-of-
main-amplitude prominence filter (`echo_test.py`,
`echo_extend.py`). 14 of 17 tested rows show ≥ 1 echo.

## Mechanism

EXP07 identified the d=10 source-stream apparent-survivor population
as integers `c = 10m` whose alternative-stream atom (typically
n=5) was rank-truncated past K. The cofactor band for these
apparent survivors sits at `c ∈ (~6.25K, ~11.1K]`.

This band straddles a base-10 decade boundary `10^d` precisely
when

```
K ∈ (10^d / 11.1, 10^d / 6.25] = (~0.09 · 10^d, ~0.16 · 10^d]
```

Predicted peak K-windows:

```
d = 3   K ∈ (90,    160)    — observed main peak  K = 90–160
d = 4   K ∈ (900,   1600)   — observed e1         K = 720–1640
d = 5   K ∈ (9000,  16000)  — observed e2         K = 7500–16000
d = 6   K ∈ (90000, 160000) — observed e3         K = 75000–160000
```

Every observed echo is the d=10 apparent-survivor cofactor band
straddling the next decade up. The base-10 structure is in the
construction — there is no smooth-decay version of this.

## The lesson

The naive expectation under the "limit-survivor reading" of EXP07
is: as K → ∞, all apparent survivors disappear (every integer is
eventually rank-included in every stream it belongs to), so the
bias goes to zero. That is correct in the limit. The route to the
limit is what's surprising.

A smooth, monotone decay of the bias to zero would require that
whatever drives the bias damps at every K. But the d=10 mechanism
is *base-10-specific*: it re-fires at every base-10 decade because
that is when the apparent-survivor band crosses a digit-length
boundary. Smooth decay would mean the bias's K-dependence forgets
which base it is being measured in. That cannot happen, because
the digit-length observable is base-10 by definition.

The convergence does happen — geometric amplitude decay across
decades — but base-10-shaped, not smooth.

The broader lesson: when an asymptotic limit looks like it
"obviously converges to zero," check whether the path inherits
structure from the construction. A base-aware mechanism cannot
have a base-blind decay. What looks like clean convergence often
hides decade-spaced (or scale-spaced) staircase structure.

## Predictions

- **Other bases.** In base `b`, run the same sweep on streams
  defined by `b`-prime atoms. Echoes should appear at K ≈ b^d for
  d = 2, 3, 4, ... Echo spacing × b instead of × 10. Geometric
  amplitude decay may shift; the exponent depends on the cofactor
  band width relative to the decade width.

- **Other high-d streams.** d ∈ {7, 8, 9} have their own
  apparent-survivor bands with different straddling K-windows.
  The full echo structure is a superposition of contributions from
  all source streams. The current finding has the d=10 fingerprint
  separated implicitly via the W=9, low-n_0 windows it lives in.
  Source-stream stratification of the K-decay is the natural next
  step.

- **n_0 ≥ 11 transition.** n_0=11 and beyond show different peak
  structure (peak K not at d=3 location, only one echo found
  within K=50000). Streams [11..19] have `n=10` outside the
  window; the d=10 mechanism doesn't fire. Other source-stream
  echoes drive the structure there, with different K-locations.

- **Persistence of echoes.** Pushing further (K → 5×10^6) should
  find a fourth echo near K = 1.6M for n_0 ∈ {2, 3} with amplitude
  ≈ 1.21%. At K = 10^9 the bias is still ≈ 26% of the main peak
  if the geometric decay holds.

## What this combines with

- **L1-magnitude tracking** (`l1_grid.png` / `wonders/curiosity-
  two-tongues.md`): the original observation. C_Surv and the
  bundle have similar L1 deviation across atom positions.

- **Mean-digit-length tracking** (`l1_grid_lengths.py`): a second
  magnitude-level "tracking" property. Median bias ≈ 0 across most
  parameter space. This finding probes the structure of the
  deviation from neutrality.

- **EXP07 source-stream stratification** (`differences/EXP07-
  FINDINGS.md`): identified the d ∈ {8, 9, 10} apparent-survivor
  mechanism. This finding is the K-evolution of that mechanism.

The C_Surv-as-optimizer reading needs an addendum: the optimizer's
output approaches the bundle's leading observables in the limit,
but the convergence carries the base's fingerprint.

## Files

- `l1_grid_lengths.py` / `.npz` / `.png` — original W=10 grid
  showing near-perfect neutrality at large n_0.
- `l1_grid_lengths_dense.py` — W=9 dense grid at n_0 ∈ [2, 50],
  K ∈ [100, 2000]. First place the structure became visible.
- `l1_grid_lengths_largeK.py` — W=9 extension to K = 50000.
- `l1_grid_lengths_lowK.py` — W=9 extension to K = 10. Found the
  main peak at K ≈ 100–160.
- `l1_grid_lengths_decay_zoom.py` — closer look at decay curves.
- `echo_test.py` — local-maxima test combining caches; first
  detection of echoes.
- `echo_extend.py` / `echo_extend.npz` — K → 500000 extension
  confirming the third echo at K ≈ 100000–160000.
- `echo_barcode.py` / `echo_barcode.png` — the reduction
  visualization.

## Cross-references

- `wonders/curiosity-two-tongues.md` — the cabinet entry that
  motivated this length probe. The C_Surv-as-optimizer reading
  there should be amended: magnitude-level tracking holds, but
  the route to it is base-aware and decade-staircased.
- `differences/EXP07-FINDINGS.md` — the source-stream
  stratification that identified the d=10 truncation mechanism.
- `differences/REFRAMING-CHAIN.md` — the meta-note on how the
  understanding of C_Surv has been progressively sharpened. This
  finding extends that chain: the optimizer reading predicts
  magnitude-level tracking; the base-aware echo structure is what
  the prediction looks like in detail.
