# Parity-mode falsifier — proposed follow-up to projection check

The projection check (`projection_check_SUMMARY.md`) gave r ≈ 4 on
1D axis marginals and r ≈ 2 on 2D full state for ℤ² and H_3. The
proposed mechanism is:

- **alt's slowest mode is a near-parity Fourier mode** (k = ⌊L/2⌋
  on odd L, which has cos ≈ −1).
- **full's laziness kills that mode** via (1 + cos(2πk/L))/2, so
  full's bottleneck shifts to a different (faster) slow mode.
- The r = 4 on 1D and r = 2 on 2D follow from the specific slow
  modes each walk is stuck on.

The spectral calculation matches data to three digits. But three
digits isn't a mechanism proof — it's a match between two
independent calculations. A mechanism claim earns belief when a
_different_ experiment, predicted by the same mechanism, comes
out right.

## Proposed test: lazy-alt walk

**Definition.** At each calendar step, with probability ε = 1/2
do nothing; otherwise, execute the alt step (x±1 on odd steps,
y±1 on even steps).

This is "alt with holding" — the holding probability is the
lazy-walk trick, applied to alt's schedule rather than full's.

**Predictions from the parity-mode mechanism.**

| observable | r = n_{lazy-alt} / n_{full} | predicted decay rates per step |
|:-----------|:---------------------------:|:-------------------------------|
| 2D full state | **1.00** | both at 0.00511 (full's (15,15); lazy-alt's (1,0)) |
| x-marginal    | **2.00** | lazy-alt 0.00511; full 0.01025 |

The key move: laziness on lazy-alt's odd/even schedule folds the
k=15 x-coord character through (1+cos)/2 → 0.00255 (dead), same
way full's single-step laziness does. So lazy-alt's bottleneck
shifts from (15, 0) at 0.00256 to (1, 0) at 0.00511.

On 2D, the bottleneck moves from alt's (15, 0) axis parity to
(1, 0) axis at 0.00511, which exactly matches full's (15, 15)
diagonal parity at 0.00511. Hence r = 1 on 2D.

On 1D, lazy-alt's 1D marginal slow mode becomes k = 1 at 0.00511
(same as alt at (1, 0) but slowed by a factor 2 from the
half-updates-per-axis schedule). Full's 1D slow mode stays at
0.01025. r = 2.

**Contrast with prior data:**

| walk pair | 2D r | 1D r |
|:----------|:----:|:----:|
| alt vs full (measured) | 2.00 | 4.00 |
| lazy-alt vs full (predicted) | 1.00 | 2.00 |

If both predicted r's come out right, the parity-mode mechanism
is confirmed in a surgical way — we turned off the offending
mode by adding laziness, and r dropped by exactly the expected
factor on each observable.

If instead lazy-alt vs full gives r ≈ 2 on 2D and r ≈ 4 on 1D
(same as alt), the mechanism is wrong — something else explains
the r pattern.

## Sim design

Single new walk on ℤ² (L = 31) at N = 10⁶, n_max = 2000, odd L.
Compute 2D L₁, x_1d, y_1d at each sample time; compare to the
existing `projection_check_results/z2_full.npz`.

Cost: one run, ~20–30s. Cheap.

### Walk definition (pseudocode)

```
def step_lazy_alt(x, y, rng, step_index):
    hold = rng.random(size=x.shape[0]) < 0.5
    # indices not holding
    active = ~hold
    if step_index % 2 == 1:
        choice = rng.integers(0, 2, size=x.shape[0], dtype=np.int8)
        delta = choice * 2 - 1
        x[active] += delta[active]
        x %= L
    else:
        ...
```

Seed distinct from existing projection-check seeds.

### Analysis

Same as `analyze_projection_check.py` but adding one more walk
column. Report r(N=10⁶, k) for k ∈ {5, 3, 2, 1.2} on each of
full_2d, x_1d, y_1d.

Decision rule:
- If r_2D ∈ [0.9, 1.15] and r_1D ∈ [1.8, 2.2] across all k:
  **mechanism confirmed**. The parity-mode story is the right
  explanation of the 2/4 pattern.
- If r_2D > 1.5 or r_1D > 3.0 on any k: **mechanism falsified
  or incomplete**. Report actual values and re-examine.
- Intermediate: note and diagnose which modes are actually
  dominating by looking at low-frequency Fourier content of the
  histograms.

## Alternative / complementary test: even L

A second, more qualitative probe: rerun ℤ² full and alt at
**L = 30 (even)** on the same 1D marginal.

Prediction from parity: on even L, alt's x-marginal has an
**exact conserved quantity** — after n alt-steps, x-parity =
⌊n/2⌋ mod 2 deterministic. The x-marginal cannot converge to
uniform on Z/30; it is stuck on one of the two parity classes
forever. L₁(alt, x_1d) plateaus at ~1.0 (half-mass on 15 of 30
values, zero on the other 15) and never decreases.

Full on even L: x-parity is Binomial across walkers (random).
x-marginal converges to uniform on Z/30 normally. L₁(full,
x_1d) → floor.

This is a **qualitative** falsifier: if the parity-mode story
is right, the alt-on-even-L 1D marginal should be conspicuously
stuck at ~1.0 forever, while full mixes normally. The
quantitative lazy-alt test above already predicts a specific r,
but even-L gives a "the curve just doesn't come down" visual
that's hard to mistake.

Cost: one alt run at L=30. Compare L₁(x_1d) vs the odd-L alt
run; predict plateau at ~1.0 on even but ~0 on odd.

## Why this is the right next test

- **Different mechanism lens.** The projection check tested what
  happens when we marginalize the state space. Lazy-alt tests
  what happens when we modify the _walk_ (add holding). The
  two tests are independent — if the parity-mode story is
  right, both should come out the predicted way.
- **Sharp quantitative predictions.** r = 1.0 and r = 2.0 exactly,
  not "approximately less than the alt values." A factor-2 drop
  is unambiguous against sampling noise.
- **Surgical.** We're not changing the group, the step set, the
  observable, or the schedule structure. We're adding one
  parameter (ε) and claiming the mechanism is _about_ that
  parameter. If it's not, the r's will be identical to alt's.
- **Cheap.** One run. ~20s wall time. No risk, no
  infrastructure.

## What success/failure buys us

**Success (r = 1, r = 2).** We have a clean spectral story for
the r pattern on ℤ² and H_3 that's been independently confirmed
by an experimental perturbation. This sharpens the paper's
honest footnote considerably: "slowdown is driven by specific
parity-like spectral modes that laziness can suppress." It
also makes the BS(1,2) mantissa r ≈ 1.15 more puzzling, because
the mantissa observable doesn't obviously sit in any of the
spectral regimes we've characterized — which is itself
informative.

**Failure (r unchanged from alt).** Parity-mode story is wrong;
some other mechanism produces the r pattern. We go back to
thinking. Still valuable — a falsification forces us into a
better explanation.

## Not planned in this round

- Fine ε scan. Predictions are at ε = 1/2 only. If the ε=1/2
  result is clean, a finer scan (ε ∈ {0.1, 0.25, 0.5, 0.75})
  could map the transition and verify the sharp drop in r
  predicted at small ε, but that's overshoot for falsification.
- BS(1,2) lazy-alt. Would need a full-state observable for
  BS(1,2), which is the blocker that killed
  `BS12-FULLSTATE-SIM.md`.
- Direct transfer-matrix diagonalization. Could compute exact
  spectral gaps for L=31 (961×961 matrix). Confirms the
  spectral calculation in full, not just the bottleneck
  approximation. Lower priority — the sim-based confirmation
  is more informative per unit effort.
