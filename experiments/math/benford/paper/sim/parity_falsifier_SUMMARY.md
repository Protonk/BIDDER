# Parity-mode falsifier — results

Follow-up to `projection_check_SUMMARY.md`. We proposed a
parity-mode mechanism to explain r = 4 on 1D axis marginals and
r = 2 on full 2D state of the ℤ² torus alternating walk. Plan
in `PARITY-MODE-FALSIFIER-PLAN.md`.

**Both tests confirm the mechanism, sharply.**

Date: 2026-04-19.
Run: `run_parity_falsifier.py`.
Analysis: `analyze_parity_falsifier.py`.
Data: `parity_falsifier_results/`.

## (A) Lazy-alt at L = 31

Walk: alt schedule (x on odd steps, y on even), with ε = 0.5
holding probability per step. Compared to existing `z2_full.npz`
at L = 31, N = 10⁶.

| k   | n_full (2D) | n_lazy_alt (2D) | r_2D |     | n_full (x_1d) | n_lazy_alt (x_1d) | r_1D |
|:---:|:-----------:|:---------------:|:----:|:---:|:-------------:|:-----------------:|:----:|
| 5.0 | 510         | 510             | 1.000|     | 410           | 800               | 1.951|
| 3.0 | 620         | 620             | 1.000|     | 450           | 900               | 2.000|
| 2.0 | 710         | 710             | 1.000|     | 490           | 1000              | 2.041|
| 1.2 | 910         | 900             | 0.989|     | 570           | 1100              | 1.930|

**r_2D = 1.00 ± 0.01** across all k, versus 2.00 for pure alt.
**r_1D = 2.00 ± 0.07** across all k, versus 4.00 for pure alt.

The factor-2 drop on each observable is exactly what the
parity-mode mechanism predicts: laziness folds the near-parity
mode k ≈ L/2 through (1 + cos)/2 ≈ 0.003 (dead), shifting each
walk's bottleneck to the non-parity slow mode.

On the 2D full state, both lazy-alt and full end up bottlenecked
at the same decay rate (0.00511 per step), so r = 1. On the x_1d
marginal, lazy-alt's bottleneck (k = 1 at rate 0.00511) decays
half as fast as full's (k = 1 at rate 0.01025, faster because
full's steps always move _some_ coordinate whereas lazy-alt
wastes half of them on y), giving r = 2.

## (B) Even-L test (L = 30)

Walk: alt and full on ℤ²/(30ℤ)², L = 30 even. Predicted exact
conservation laws:

- **alt at L = 30:** after n steps, x has taken ⌈n/2⌉ ±1 steps,
  so x ≡ ⌈n/2⌉ (mod 2). Similarly y. **Two independent parity
  conservation laws**, walker pinned to 1/4 of the torus.
  Predicted L₁ plateaus: x_1d = 1.0, full_2d = 1.5.
- **full at L = 30:** each step flips (x + y) mod 2, but the
  individual x and y parities are random (Binomial across
  walkers). **One parity law**, walker pinned to 1/2 of the
  torus. Predicted L₁ plateaus: x_1d mixes (→ floor), full_2d
  = 1.0.

Results at n = 2000 (tail mean over last 20 samples):

| walk      | observable | tail L₁            | predicted | std    |
|:----------|:-----------|:-------------------|:----------|:-------|
| alt L=30  | x_1d       | **1.0000**         | 1.0       | 1e-16  |
| alt L=30  | full_2d    | **1.5000**         | 1.5       | 5e-17  |
| full L=30 | x_1d       | 4.4 × 10⁻³         | ≈ floor   | 5.5e-4 |
| full L=30 | full_2d    | **1.0000**         | 1.0       | 5e-17  |

Numerical noise is ~1e-16, so the plateau values hit their
predicted integer/half-integer values to machine precision.

The x_1d ratio between alt and full at tail is **227×**. Alt is
pinned to one of two parity classes of Z/30; full sweeps the
whole group.

Bonus finding: alt's 2D plateau at 1.5 confirms the **double**
parity conservation (x-parity and y-parity _each_ deterministic),
whereas full's 2D plateau at 1.0 confirms the single (x + y)
parity conservation. This wasn't in the original prediction —
I expected alt to plateau at 1.0 like full — but the math is
cleaner than I'd written.

## The spectral story confirmed

The projection check gave matching numerics (r = 2 and r = 4) to
a spectral calculation. That's two independent calculations
agreeing; it doesn't prove the mechanism.

This follow-up goes further:
- **Lazy-alt:** modifying the walk to kill a specific Fourier
  mode (the k ≈ L/2 near-parity mode) drops r from (2, 4) to
  (1, 2) by the predicted factor on each observable.
- **Even L:** making the near-parity mode an _exact_
  conservation law freezes alt's marginal L₁ at an exact
  integer value (1.0 on x_1d, 1.5 on 2D), while full's
  marginal L₁ mixes normally.

Both perturbations act on the same underlying object — the
spectral structure of the alternating walk — and both come out
exactly as the parity-mode story predicts. This is strong
evidence that the mechanism is correct.

## Updated implications for BS(1,2)

The parity-mode story explains r = (2, 4) for ℤ² in a clean,
falsifiable way. For BS(1,2) on the mantissa at r ≈ 1.15:

- The BS(1,2) mantissa is not an axis marginal of a lattice
  walk; it lives on the continuous circle ℝ/ℤ. The "parity
  mode" picture doesn't directly apply.
- The H_3 c-marginal result (r ≈ 1.7) gave the first clean
  datum of an _intermediate_ r on a coupled-coordinate
  projection. BS(1,2) mantissa sits even lower (~1.15), and
  its increments are also state-dependent (via E).
- Hypothesis (unproven): BS(1,2)'s small r comes from the
  mantissa observable being averaged over a continuous,
  non-compact state coordinate (E), which acts like a "strong
  averaging" in the spectral sense — smearing out any one
  mode's contribution. H_3's c-marginal averages over a
  _finite_ coupled coordinate (a), giving partial averaging.
  ℤ²'s x-marginal averages over nothing (y is trivially
  independent). This ordering — no averaging < partial
  averaging < full continuous averaging — would predict r ≈
  (4, 1.7, 1.15), which matches.

This is a hypothesis, not a proof. Testing it would require
running a BS(1,2) walk on a finite quotient — still blocked by
the issue that killed `BS12-FULLSTATE-SIM.md` (no natural
finite quotient with a walk-invariant reference).

## For the paper

The footnote drafted in `h3_contrast_SUMMARY.md` stays mostly
intact. The parity-mode confirmation sharpens this part:

> On finite-quotient full-state L₁ observables for ℤ² and H_3,
> the slowdown is driven by a near-parity spectral mode that
> the alternating-step schedule fails to suppress. Adding a
> single holding probability (ε = 0.5) to the alternating
> walk suppresses this mode and returns r to 1.0 on 2D and 2.0
> on axis marginals, matching a direct Fourier calculation to
> within sampling-grid precision. On the even-L torus, this
> mode becomes an exact conservation law and the alternating
> walk's axis marginal is permanently pinned to one parity
> class.

The BS(1,2) mantissa 1.15× remains the outlier; the
"coupled-coordinate-averaging" hypothesis offers a plausible
but unproven explanation. The most honest paper move is still
probably to omit the slowdown deep-dive and let the three-walks
figure carry the conversational point.

## What's saved

- `parity_falsifier_results/z2_lazy_alt_L31.npz`
- `parity_falsifier_results/z2_full_L30.npz`
- `parity_falsifier_results/z2_alt_L30.npz`

## What's not done

- Fine ε scan. r = 1.00 and r = 2.00 at ε = 0.5 confirms the
  mechanism; mapping r(ε) would be a nice-to-have but is not
  falsification-relevant.
- Spectral diagonalization of the L = 31 transition matrices
  (961 × 961) to exactly verify the slow-mode identification.
  The three independent numerics (projection check, lazy-alt,
  even-L) already agree with the Fourier calculation to
  sampling-grid precision; direct diagonalization would
  confirm what three experiments already show.
- Non-ℤ² groups with laziness. H_3 and F_2 laziness
  predictions would follow analogously but we haven't done
  the analysis.
