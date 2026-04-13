# Benford migration

Four ensemble demos plus several views of the same checkpoint data.

**Core figures** (10):
- `shutter.png` — continuous log10 mantissa, 256 bins, rolling shutter.
- `shutter_digits.png` — same data projected into 9 first-digit bins.
- `shutter_polar.png` — first-digit dial, time as radius, for the
  two contrasting mixed-walk demos.
- `base_fingerprint.png` — L1-to-uniform of `log_b` mantissa on the
  final step, scanned continuously for `b` in `[2, 40]`, including
  the biased walk.
- `bs12_rate.png` — dedicated 1M-walker short run showing exponential
  L1 decay with half-life ~20 steps.
- `tracers_v2.png` — three-panel exact-state tracer (log10|x|,
  mantissa convergence, group-element complexity growing as t^0.50).
- `bidder_shutter.png` — BIDDER cipher vs numpy PRNG, 2x2 comparison.
- `art_groove.png` — four demos rendered as vinyl records.
- `art_skyline.png` — BS(1,2) vs pure-add as a nighttime skyline.

Checkpoint data is written to `data_<name>.npz` and ignored by git.


## What is in the figures

`shutter.png` is the load-bearing picture. Each row is one
checkpointed log-mantissa histogram, stacked top-to-bottom in time.
The four panels show the four regimes: add/mult alternating (stripe
pattern), BS(1,2) walk (converges to flat), front-loaded freeze
(vertical barcode), pure add (Champernowne diagonal sweep).

`shutter_digits.png` projects the same data into 9 first-digit bins.
More immediately readable as "which digit has the mass."

`shutter_polar.png` is the dial form: angle is first-digit sector (1
at top, reading clockwise), radius is op index (centre is the initial
state, edge is the final state). Two panels: the slow add/mult
alternation and the fast-converging BS(1,2) walk.

`base_fingerprint.png` plots the terminal `L1` curve over `b` in
`[2, 40]` for `pure_add`, `bs12_walk`, and `bs12_biased`.

`tracers_v2.png` shows 32 exact-state walkers across three panels:
scale diffusion (log10|x|), mantissa convergence (the spectral gap
made visible as individual walkers filling [0,1)), and group-element
complexity (sqrt(t) growth).


## What the runs showed

`bs12_walk.py` is the cleanest migration demo. It starts from a delta at
`sqrt(2)` and mixes `+1`, `-1`, `*2`, `/2`. By the final checkpoint its
base-10 log-mantissa L1 distance to uniform is about `0.083`, and the
fraction with leading digit 1 is about `0.299`, close to the Benford
value `log10(2) ≈ 0.301`.

`add_mult_alternating.py` is the slow-convergence baseline. Long additive
plateaus collapse the ensemble toward digit 1, and occasional doublings
kick the mantissa by `log10(2)`. After 20 kicks it is still visibly far
from flat: final L1 is about `0.218`.

`front_loaded.py` is the opposite story. It starts from a base-10
log-uniform ensemble, blows the scale out with repeated doublings, then
shows that unit-scale adds no longer move the mantissa once the walker
scale is huge. It begins and ends near the Benford reference: final L1
is about `0.093`, and the leading-digit-1 fraction stays near `0.299`.

`pure_add.py` is the contrapositive. Additive drift alone does not
settle into the Benford profile. At this runtime budget the final base-10
L1 is about `0.215`, worse than the mixed walk and comparable to the
alternating baseline.


## BS(1,2) walk: quantitative findings

Three properties of the symmetric BS(1,2) random walk now have
empirical numbers:

**Convergence rate: exponential, not polynomial.** A dedicated 1M-walker
run (`bs12_rate.py`) gives an approximately exponential L1 decay on a
lin-log plot, with a fitted half-life of about 20 steps and a decay
constant lambda of about 0.035 per step. The fit has R^2 ~ 0.99 on the
canonical window (steps 20..100) and the rate shifts ~10% with window
width, suggesting some multi-mode structure beneath the single
exponential, but the dominant decay is clearly exponential, not the
t^(-1/2) expected from naive irrational-rotation equidistribution. This
is a spectral-gap signature.

**State complexity: diffusive (sqrt(t)).** Tracking the exact group
element (N, num/2^q) for 64 walkers over 20_000 steps
(`bs12_tracer.py`) gives a mean bit-length complexity that scales as
t^0.501 — essentially exact sqrt(t). The walker "folds back on itself"
at a rate that keeps each component (|N|, bit_length(num), q) diffusive.

**Biased weights: still Benford.** A biased walk
(`bs12_biased.py`, weights +1:-1:*2:/2 = 0.20:0.20:0.40:0.20) with
a net +0.20 mult drift per step sends walkers to ~10^1200 within 20k
steps. Despite this, the final L1 is 0.091 (at the finite-sample noise
floor) and the leading-digit-1 fraction is 0.308 (Benford: 0.301).
The base-fingerprint curve for the biased walk is flat across [2, 40],
matching the symmetric walk. Equidistribution is robust to generator
bias.

All three findings are empirical at specific parameter settings (20k
walkers, 20k steps, fixed seeds). They are not proven theorems.


## Base dependence is not a resonance

The continuous base scan in `base_fingerprint.png` is the cleanest view
of what is and is not true about base-dependence at these parameters.

Both `bs12_walk` and `bs12_biased` are flat at `L1 ~ 0.05` across every
base in `[2, 40]`. Their ensembles span many orders of magnitude, so the
log-base mantissa covers the circle fully whatever base is chosen. This
is the clean statement of "base-agnostic Benford" at equilibrium.

`pure_add` rises monotonically from `L1 ~ 0.05` at `b = 2` to
`L1 ~ 0.48` at `b = 40`. The rise is geometric, not a resonance: after
`20_000` unit adds the ensemble has a fixed width in linear `|x|`, so
the ensemble's width in `log_b` shrinks as `log(b)` grows. When the
`log_b` width drops below one full circle, the `mod 1` mantissa stops
covering uniformly. Base 10 sits mid-rise at `L1 ~ 0.20`, not at a peak.

So the real claim is narrower: the converging walk's Benford is genuinely
base-independent, and the non-converging walk's base sensitivity is a
scale-width artifact with no resonance at any particular base.


## What is deferred

`renewal.py` is still deferred. Phase 1 does not record the per-walker
event stream needed for renewal-gap histograms, so the file is present
only as an explicit placeholder.
