# Benford migration — experiment plan

Status: execution-pass plan. Phase 1 is intentionally lean: get the
core dynamics and the two load-bearing figures first, then only add
companion plots if the first pass is already clean.

## Motive

Build a demo that shows numbers "in the world" migrating toward the
Benford / reciprocal distribution under mixed additive and multiplicative
dynamics, but never reaching it exactly in finite time. The rolling-shutter
metaphor is literal: each "scan line" of the composite figures is the
log-mantissa density after one checkpoint, stacked in time.

## Conceptual frame

Adds and mults act as opposites on the log-mantissa circle.

- `x <- r * x` is a pure translation of `log x` by `log r`. Mod 1, if
  `log_B r` is irrational, the iterated map is ergodic and equidistributes
  `log_B x mod 1` on `[0, 1)`. The stationary distribution is uniform in
  log coordinates, which is exactly Benford in base B, which is exactly
  the reciprocal distribution (density proportional to `1/x`) in linear
  coordinates.
- `x <- x + epsilon` is a linear translation. On the log axis it is
  contractive toward a point mass at whatever integer order the walker
  currently occupies: for `|epsilon| << x` the log coordinate barely
  moves, so repeated small adds concentrate leading-digit mass near 1
  (the "everything rounds up through the 1.xxx range" effect).

Pure-add flows never Benford-ize. Pure-mult flows equidistribute but in
a rigid way (a single orbit). The interleaving is what drives migration.
Mults scramble, adds collapse, and the race between them is the demo.

All Benford-facing observables are taken on `|x|`, not signed `x`.
The sign is not the story here. Exact zero is a singular state and the
plan should avoid generating it, not silently mask it away.

## Scope

**In scope (phase 1):**

- Four demo dynamics (add/mult alternating, BS(1,2) walk, front-loaded,
  contrapositive pure-add).
- One per-demo line plot: `l1` and leading-digit-1 fraction vs op index.
- Rolling-shutter composite.
- Base sweep across `{2, e, 10, pi}` for the two most informative demos.
- Short writeup (`BENFORD.md`) only after the figures exist.

**Out of scope / not yet (explicitly deferred):**

- Reciprocal-density overlay in linear coordinates.
- Mantissa renewal-time histograms.
- Additive step-size regime sweep.
- BS(1, n) family for n > 2.
- Cauchy / heavy-tailed add steps.
- Animation / GIF.
- Cross-reference figure bridging to experiments/math/arcs/.

## File layout

```
experiments/math/benford/
  PLAN.md                     this document
  BENFORD.md                  short writeup, only after figures exist
  common.py                   shared runner, histograms, I/O, constants
  add_mult_alternating.py     demo 1: runs dynamics, saves npz, emits l1 fig
  bs12_walk.py                demo 2: random walk on BS(1,2)
  front_loaded.py             demo 3: Benford first, then frozen by huge scale
  pure_add.py                 contrapositive: uniform adds only, no mults
  shutter.py                  2x2 composite rolling-shutter heatmap
  base_sweep.py               2x4 grid: {bs12_walk, pure_add} x {base 2, e, 10, pi}
  reciprocal.py               optional phase-2 plotter
  renewal.py                  optional phase-2 plotter
```

Six phase-1 scripts, two optional phase-2 plotters, `common.py`, and
two Markdown files.

## common.py API

```python
SEED                  = 0xB1DDE12         # fixed
N_WALKERS             = 20_000
TARGET_CHECKPOINTS    = 200
LOG_MANTISSA_BINS     = 256               # per checkpoint, base 10

def run_schedule(ops, initial, target_checkpoints=TARGET_CHECKPOINTS, seed=SEED):
    """Run a list of ops on an ensemble.

    ops: list of (name, count, step_fn) where step_fn(rng, x, n_steps)
         returns the new x array after n_steps applications. For large
         additive or pure-multiplicative blocks, the implementation
         should update in checkpoint-sized batches rather than one
         Python loop per op.
    initial: starting x array (shape: N_WALKERS,) or a scalar to broadcast.

    Returns a dict with keys:
      step                 (K,)          op index at each checkpoint
      log_mantissa_hist    (K, 256)      normalized, base 10
      l1                   (K,)          L1 distance to uniform log-mantissa
      leading_1_frac       (K,)          fraction of walkers with leading digit 1
      final_abs_x          (N,)          abs(x) at the final checkpoint
      schedule_summary     str           human-readable schedule description
    """

def log_mantissa(x, base=10.0):      # returns log_base(|x|) mod 1
def leading_digit(x, base=10):       # integer base only, on |x|
def l1_to_uniform(hist):             # sum(|h - 1/len|)
BENFORD_PROBS_BASE10 = ...           # np.array([log10(1 + 1/d) for d in 1..9])

def save_checkpoints(path, ckpts):   # np.savez_compressed
def load_checkpoints(path):          # returns dict

# Shared visual style, matching experiments/math/arcs:
def setup_dark_axes(ax): ...         # #0a0a0a bg, white text, #333 spines
CMAP = plt.cm.plasma
```

Step functions live in `common.py` as small factories:

```python
def add_uniform(lo, hi):             # step_fn closure
def add_constant(c):
def mul_constant(r):
def bs12_step():                     # uniform pick from {+1, -1, *2, /2}
```

Implementation note: `bs12_step()` is the only demo step that really
wants a per-op loop. The large additive and pure-multiplicative blocks
should be checkpoint-batched so phase 1 stays runnable.

## Demos

All four demos:
- Use a sharp, simple initial condition rather than a broad ambient one.
- Default to `x = 1.0` for the continuous-add demos.
- Use `x = sqrt(2)` for `bs12_walk.py` so the `x -> x-1` branch does
  not pile walkers exactly at zero.
- Use a base-10 log-uniform initial ensemble for `front_loaded.py`; a
  deterministic multiplicative pre-roll on a delta ensemble would stay a
  delta forever and would not demonstrate the freeze.
- Ensemble size `N_WALKERS = 20_000`.
- Fixed seed from `common.SEED`.
- Save their checkpoint dict to `data_<name>.npz` in the same directory.
- Emit one primary figure: a line plot of `l1` and `leading_1_frac`
  vs op index (log-y for `l1`, linear-y twin axis for the fraction).
  File: `<name>_l1.png`.

### 1. `add_mult_alternating.py`

Schedule: 20 cycles of `(500 x add_uniform(-1, 1), 1 x mul_constant(2.0))`.
Total 10_020 ops.

Expected behavior: within a few hundred adds the log-mantissa collapses
toward leading-digit 1. Each doubling kicks the distribution by
`log10 2 approx 0.301` in mantissa. After 20 kicks, 20 irrational
translations is nowhere near equidistribution — L1 stays large. This
is the "slow convergence" baseline.

### 2. `bs12_walk.py`

Schedule: `20_000` ops, each a uniform pick from `{x -> x+1, x -> x-1,
x -> 2x, x -> x/2}`. Each walker independently samples its own step
sequence (ensemble diversity). Start from `x = sqrt(2)`.

Expected behavior: the walk is transient in the group sense but each
walker's log10 mantissa receives a steady supply of irrational
translations from the doublings/halvings. L1 should decay cleanly
toward zero, visibly approaching Benford but strictly positive at every
finite op count. This is the demo that actually converges, and the one
the base sweep is built on.

### 3. `front_loaded.py`

Initial state: `x = 10**U` with `U` uniform on `[0, 1)`, independently
per walker.

Schedule: `500 x mul_constant(2.0)` then `2_000 x add_uniform(-1, 1)`
then `1 x mul_constant(2.0)` then `10_000 x add_uniform(-1, 1)`.
Total 12_501 ops.

Expected behavior:
- At step 0: the ensemble is already Benford in base 10.
- After the multiplicative pre-roll: the mantissa stays Benford while
  walker scale becomes astronomically large.
- During the add plateaus: the adds are unit-scale while walker scale is
  enormous, so log mantissa barely moves.
- After the single extra mult: still frozen.

So front_loaded actually shows the *opposite* of migration: a
Benford-equilibrated distribution staying there, because the walker's
scale has outrun the add magnitude.

### 4. `pure_add.py` (contrapositive)

Schedule: `20_000 x add_uniform(-1, 1)`.

Expected behavior: walker scale drifts as a random walk, `|x|` grows as
`~sqrt(n)`. Leading-digit-1 probability approaches 1 as n grows, because
once `|x|` is much larger than the step size the mantissa barely moves
and whatever digit you land on becomes sticky. L1 to Benford should
climb, not fall. This is the bad flow — proof by picture that adds
alone never Benford-ize. If this panel is too weak at 20k ops, the
first knob to turn is more steps, not more walkers.

## Cross-cutting plotters

Phase 1 only needs `shutter.py` and `base_sweep.py`. The other plotters
can wait until the main story is already visible.

### `shutter.py`

2x2 grid, one panel per demo:
- x axis: log10 mantissa in `[0, 1)`, 256 bins
- y axis: op index (checkpoint), top = start, bottom = end
- color: density per bin, `plt.cm.plasma`
- Vertical reference lines at the Benford leading-digit boundaries
  (log10 1, log10 2, log10 3, ..., log10 9, log10 10).

This is the central figure. The converging demo shows a colorful
vertical rainbow at top fading to flat horizontal stripes at bottom.
The pure-add demo shows stripes concentrating near the left edge (digit 1).

Output: `shutter.png`

### `base_sweep.py`

2x4 grid:
- Row 1: bs12_walk final-checkpoint mantissa histograms in base 2, base e,
  base 10, base pi.
- Row 2: pure_add final-checkpoint mantissa histograms in the same bases.
- Each panel: 64-bin histogram of `log_base(|x|) mod 1`, uniform reference
  line overlaid, empirical L1 distance to uniform in the panel title.
- Input is `final_abs_x`, not the base-10 checkpoint histograms. This
  plot recomputes mantissas from raw final magnitudes for each base.

Working hypothesis: bs12_walk is flatter in bases `{e, 10, pi}` than in
base 2, because the doubling step is a rational
(unit) translation in log2 space and cannot equidistribute there. Only
the `+/-1` steps randomize the base-2 mantissa. This shows empirically
that Benford-style behavior can depend on the base when the dynamics
have a rational log-ratio with that base. Do not bake the strong claim
into captions until the figure is on disk.

pure_add row: the non-converging behavior should remain visible, but do
not promise the same shape in every base at this runtime budget. The
load-bearing contrast is simply "less flat than `bs12_walk`."

Output: `base_sweep.png`

### `reciprocal.py` and `renewal.py` (phase 2 only)

Do not write these until the shutter and base-sweep figures are already
good. If phase 1 works cleanly, `reciprocal.py` should use `final_abs_x`
and compare against a `c / x` overlay on a positive `[P5, P95]` window.
`renewal.py` is strictly optional; it adds tracking machinery and is not
needed to establish the visual story.

## Checkpoint schema (written by each demo)

File: `data_<name>.npz`, via `np.savez_compressed`.

Fields (all numpy arrays unless noted):

| key                    | dtype | shape        | notes                                    |
|------------------------|-------|--------------|------------------------------------------|
| `step`              | i8    | (K,)      | op index at each checkpoint         |
| `log_mantissa_hist` | f4    | (K, 256)  | normalized log10 mantissa density   |
| `l1`                | f4    | (K,)      | L1 distance to uniform log-mantissa |
| `leading_1_frac`    | f4    | (K,)      | fraction with leading digit 1       |
| `final_abs_x`       | f8    | (N,)      | `abs(x)` at the final checkpoint    |
| `schedule_summary`  | str   | scalar    | human-readable schedule description |

`K` ~ 200 checkpoints per demo.

Rough size per demo: `200 * 256 * 4 + 20000 * 8` ≈ well under 1 MB
compressed. Fine, and `.npz` files live in the experiment directory
(add a gitignore entry).

## Visual style

Match `experiments/math/arcs/`:

- Dark background `#0a0a0a`, white axis labels and ticks, `#333` spines.
- Sequential colormap: `plt.cm.plasma`.
- `plt.tight_layout()`, `dpi=250`, `bbox_inches='tight'`.
- Agg backend (`matplotlib.use('Agg')`).
- Every script prints `-> <outfile>` at the end so a build log is readable.
- Every script runs with `sage -python <name>.py`.
- Scripts resolve repo-local imports via `__file__`-based path insertion,
  matching the existing experiment pattern.

## Execution order

1. `common.py`
2. `add_mult_alternating.py`, `bs12_walk.py`, `front_loaded.py`,
   `pure_add.py` — all produce `data_*.npz` and `<name>_l1.png`.
3. Cross-cutting plotters: `shutter.py`, `base_sweep.py`.
4. Optional phase 2 only if phase 1 already works: `reciprocal.py`,
   `renewal.py`.
5. `BENFORD.md` writeup — only after we have looked at every figure
   and confirmed the story.

Between each phase: eyeball the outputs, tweak parameters, re-run before
moving on.

## Validation / sanity checks

To be built into `common.py` or into a small `smoke_test.py`:

- **No singular values:** every checkpoint must have finite `x`, and
  `final_abs_x` must be strictly positive.
- **Histogram sanity:** each `log_mantissa_hist[k]` must sum to 1 within
  floating-point tolerance.
- **Front-loaded freeze sanity:** after the multiplicative pre-roll,
  the add plateau should change `l1` only slightly.
- **Base-sweep plumbing:** `base_sweep.py` must recompute mantissas from
  `final_abs_x`; it must not reuse the stored base-10 histograms.

## Parameter tuning rules

No open design questions need blocking review now. Phase 1 should use
the defaults above, then only tune if a concrete figure fails:

1. If `pure_add.py` is too weak visually, increase step count before
   increasing walker count.
2. If `shutter.png` looks blocky, raise `TARGET_CHECKPOINTS` from 200 to
   300 before changing anything else.
3. If the base-2 vs irrational-base split in `base_sweep.py` is too weak,
   extend `bs12_walk.py` before adding more demos or more bases.

## What this experiment claims when done

- There is a family of stochastic-linear dynamics (adds and mults on
  `R \ {0}` with observables taken on `|x|`) whose log-mantissa distribution migrates toward the Benford
  reciprocal but strictly never reaches it in finite time.
- Pure-add dynamics never Benford-ize; pure-mult dynamics equidistribute
  only in bases with irrational log-ratio to the mult factor.
- The rolling-shutter visualization makes the migration and the
  base-dependence both visible in one frame.

No new theorems. The claim is pedagogical: "here is what the migration
looks like when you watch it."
