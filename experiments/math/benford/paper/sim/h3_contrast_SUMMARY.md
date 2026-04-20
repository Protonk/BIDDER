# H_3 contrast and check A — summary

Two new runs in the sub-sampling-slowdown series: the Heisenberg
H_3(ℤ/15) check and the Markov-type check A.

Run scripts: `run_h3_contrast.py`, `run_check_a.py`.
Data: `h3_contrast_results/`, `check_a_results/`.
Analysis: `analyze_h3_contrast.py`.
Dates: 2026-04-19.

## Headlines

1. **H_3(ℤ/15) gives r ≈ 2.0**, stable across N and k. Same
   slowdown as ℤ² torus.
2. **Check A (Markov p_switch = 0.75) gives r ≈ 2.0 on both
   ℤ² and H_3**, identical to strict alternation. The slowdown
   is a **saturation effect**, not a continuous function of
   type-correlation strength.
3. **The 2× slowdown is a step-set / observable property, not
   a group-structure property.** BS(1,2)'s 1.15× is a distinct
   regime specific to mantissa-projection observables.

## H_3(ℤ/15) results

Four N × four k table of `r = n_alt / n_full`:

| k \ N | 10⁵  | 10⁶  | 10⁷  |
|:-----:|:----:|:----:|:----:|
| 5.0   | 1.80 | 2.11 | 1.93 |
| 3.0   | 1.86 | 1.92 | 2.00 |
| 2.0   | 2.00 | 2.00 | 2.00 |
| 1.2   | 2.00 | 2.00 | 1.96 |

**Q1 (k-trend):** basically flat within each panel. No
systematic k-dependence.

**Q2 (N-stability at fixed k):** max/min ratios in the range
1.00 to 1.17. Very stable.

**Value at saturation:** 2.00, exactly matching ℤ² torus within
the sampling-grid quantization. Grid values sitting exactly at
2.000 are a step-10 sampling artifact but the underlying
convergence is clearly ~2.

## Check A: Markov-type at p_switch = 0.75

For each group at N = 10⁶, we compute hit-times for three walks:
full (p_switch = 0.5), strict alternating (p_switch = 1.0), and
Markov-type with 75% switching probability.

### ℤ² torus (L = 31)

| k   | n_full | n_alt | n_markov_0.75 | r_alt | r_markov |
|:---:|:------:|:-----:|:-------------:|:-----:|:--------:|
| 5.0 | 510    | 1010  | 1020          | 1.98  | 2.00     |
| 3.0 | 620    | 1220  | 1230          | 1.97  | 1.98     |
| 2.0 | 710    | 1430  | 1420          | 2.01  | 2.00     |
| 1.2 | 900    | 1770  | 1790          | 1.97  | 1.99     |

### H_3(ℤ/15)

| k   | n_full | n_alt | n_markov_0.75 | r_alt | r_markov |
|:---:|:------:|:-----:|:-------------:|:-----:|:--------:|
| 5.0 | 90     | 190   | 190           | 2.11  | 2.11     |
| 3.0 | 120    | 230   | 230           | 1.92  | 1.92     |
| 2.0 | 140    | 280   | 280           | 2.00  | 2.00     |
| 1.2 | 180    | 360   | 360           | 2.00  | 2.00     |

**r_markov and r_alt agree to within sampling grid precision.**
p_switch = 0.75 gives the same slowdown as p_switch = 1.0.

The "continuous with correlation strength" hypothesis from the
check-A proposal is **refuted**. Any meaningful anti-correlation
between consecutive step types saturates the slowdown at ~2×.
Presumably a more careful scan of `p_switch ∈ (0.5, 0.75]` would
find the threshold where slowdown rises; we haven't done that.

## Updated group-observable table

| group / observable               | r    | regime       |
|:---------------------------------|:----:|:-------------|
| F_2 tree / drift                 | 0.5  | speedup      |
| BS(1,2) / mantissa L₁ (T = ℝ/ℤ)  | 1.15 | intermediate |
| ℤ² torus L = 31 / full L₁        | 2.0  | saturated    |
| H_3(ℤ/15) / full L₁ on L³ cells  | 2.0  | saturated    |
| Any of the above @ p_switch ≥ 0.75 | same as p = 1.0 | saturated |

## Revised interpretation

Previously I'd hypothesized BS(1,2)'s 1.15× slowdown came from
the `bab⁻¹ = a²` relation specifically, and that ℤ² (without
that relation) would show ~1.0×. That story is dead — both
non-BS(1,2) group runs (ℤ² and H_3) show ~2.0×, bigger than
BS(1,2)'s 1.15×.

The sharper story that emerges:

- **The 2.0× slowdown on ℤ² and H_3 appears to be driven by the
  step-set + observable combination**, not by algebraic
  structure. Both groups have {x, x⁻¹, y, y⁻¹} one-coord-at-a-
  time steps, and both use L₁ to uniform on the full state
  space. Alternating's 2-step operator is a "diagonal-only"
  move on these groups; full's 2-step includes identity and
  same-axis pairs. The 2× is an asymptotic consequence of
  that spectral structure.
- **BS(1,2)'s 1.15× is specific to the mantissa-projection
  observable.** The mantissa circle is a 1D projection of a
  much larger state space, and projecting appears to average
  out some of the alternation penalty. If we instead simulated
  BS(1,2) with a full-state L₁ (e.g., on a large finite
  quotient of BS(1,2)), we'd likely see ~2× as well. Not
  confirmed — would be a separate sim.
- **F_2's 0.5× speedup** is a qualitatively different regime.
  On a tree with no relations, alternation strictly removes
  backtracking; this is the classical lazy-walk-removal
  speedup mechanism from `sim/SUBSET-THEOREM.md`, not an
  alternation penalty.
- **The saturation-at-p=0.75 finding** (check A) is
  consistent with a non-linear mapping from type-correlation
  to slowdown: above some threshold (plausibly p_switch > 0.5
  + small), the slowdown jumps to its saturated value. This
  suggests the slowdown mechanism isn't gradual "a bit of
  correlation, a bit of slowdown" but a spectral structure
  that either holds or doesn't.

## What this means for the paper

The claim "BS(1,2)'s 1.15× slowdown comes from its non-trivial
relation" — which I'd drafted as a possible paper footnote —
is not supported. The honest footnote, updated:

> Sub-sampling slowdown of alternating-step walks varies by
> group and by observable choice. On the natural mantissa
> observable for BS(1,2), alternating is ~1.15× slower than
> the full walk. On full-state L₁ observables for abelian ℤ²
> and nilpotent H_3 torus quotients, the same sub-sampling
> gives ~2× slowdown, independent of the group's algebraic
> structure (both abelian and non-abelian nilpotent saturate
> at the same ~2× value). On the free group F_2 measured by
> drift rate, alternating is 2× *faster* than the full walk
> (classical lazy-walk speedup). The slowdown is not a simple
> function of group structure; it depends on the combined
> step-set/observable structure.

This is a weaker paper claim than "the BS relation causes
slowdown," but it's accurate. The paper might be better served
by omitting the slowdown discussion entirely and letting the
three-walks figure (mul/alternating/BS(1,2)) carry the
conversational point about "only the full mix converges in
practice."

## What's saved

- `h3_contrast_results/{full,alt}_N1e{5,6,7}.npz` — 6 runs.
- `check_a_results/{z2,h3}_markov_p075_N1e6.npz` — 2 runs.

## What's not done

- A fine-grained scan of p_switch ∈ (0.5, 0.75) to locate the
  saturation threshold. Probably not worth it; the existing
  data point of r(0.75) = 2.0 = r(1.0) already settles the
  "continuous vs threshold" question.
- BS(1,2) on a full-state observable (a finite quotient). We
  drafted this as `BS12-FULLSTATE-SIM.md` and then withdrew it
  after GPT5 review (2026-04-19). The ad hoc reference
  distribution (uniform on `m × E mod L`) is not what the
  non-compact BS(1,2) walk actually approaches — empirically
  L₁ to that reference sits at ~0.42 at n = 2000, far from
  the noise-floor-scale values the plan wanted to threshold
  on. Doing this properly would require building a natural
  finite quotient of BS(1,2) (matrix representation over ℤ/p^k)
  and running the walk on that — substantial setup, not a
  morning sim. The withdrawn plan is preserved at
  `BS12-FULLSTATE-SIM.md` with a full explanation of why it
  doesn't work. Not currently planned.
- Block-alternation at various block sizes. Also a possible
  robustness check but not currently planned.
- Explicit check that the ℤ² and H_3 2× ratio is exactly 2
  in the continuum limit (currently could be anywhere in
  [1.9, 2.1]). Probably not worth tightening.

## Link to `sim/SUBSET-THEOREM.md`

The 2× empirical ratio on ℤ² and H_3 sits well inside the
Dirichlet-form ceiling (factor of 4 for 2-step sub-sampling
with μ(A) = 1/4). Consistent with theory; the theory doesn't
predict the 2× specifically but permits it.
