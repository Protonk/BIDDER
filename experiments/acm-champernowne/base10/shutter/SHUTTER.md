# Rolling Shutter

First-digit distribution of sums of Champernowne reals, from 1 addition
(bottom) to 500 (top). A hot band sweeps diagonally through digits
1-9-1-9 forever. It never settles into Benford's law.

Run: `sage -python rolling_shutter_heatmap.py`

## Why it's art

The staircase pattern is immediately recognizable as a CMOS rolling
shutter artifact — the kind you see when you photograph a spinning
propeller with a phone camera. The "propeller" here is the cycling of
leading digits as sums cross powers of 10. The "scan rate" is one
addition per row. The shear angle (arctan(log₁₀(1.55)) ≈ 10.8°) is a
number-theoretic constant made physically visible.

## What makes it non-obvious

Multiplication converges to Benford in ~10 steps. Addition *never*
converges. A thousand additions produce a distribution further from
Benford than seven multiplications. The image is a proof-by-picture
of this asymmetry.

The leading digit of each sum is extracted by `LD10`
(`BQN-AGENT.md`; mirrors `acm_first_digit` in
`core/acm_core.py`) — the log-based real-valued extractor, not the
integer-level `LeadingInt10` used in the block-uniformity theorem:

```bqn
LD10 ← {⌊𝕩÷10⋆⌊10⋆⁼𝕩}
```

## Format

Tall vertical panel (8" x 16"), dark background, inferno colormap.
The aspect ratio emphasizes the relentless diagonal sweep.

## Next steps

- **Animation.** Let the hot band sweep in real time, one frame per
  addition step.
