# EXP02 — Ambient-S phase space

Fix the ACM survivor bundle at rows `n = 2..20`, `k = 80`. Vary the
ambient numerical semigroup over coprime two-generator cells
`S = ⟨a,b⟩`, with `2 ≤ a ≤ 18`, `3 ≤ b ≤ 30`, and `a < b`.

For each cell, `C_SurvA` is the ACM survivor stream restricted to
multiplicative atoms of `(S, ·)`, in the same row-major survivor order.
The discrepancy is the dsubn observable: star discrepancy `D_L*` of the
shifted decimal-tail orbit of the `C_SurvA` digit string.

## Empirical readout

```
bundle atoms       = 1520
ACM survivors      = 408
max bundle integer = 1680
phase cells        = 205
```

The smallest stream is `S = ⟨2,3⟩`: `8` atoms, `12` digits,
`D_L* = 0.3096`. The largest stream in this grid is `S = ⟨13,16⟩`:
`366` atoms, `1198` digits, `D_L* = 0.1008`.

The lowest raw discrepancy occurs at `S = ⟨9,10⟩`:

```
atoms = 290, L = 903, D_L* = 0.0558, ratio = 0.246
```

where `ratio = D_L* / ((log L)/sqrt L)`. The strongest raw
discrepancies are concentrated in tiny streams (`⟨2,3⟩`, `⟨2,5⟩`,
`⟨2,7⟩`). After normalisation by `(log L)/sqrt L`, the low-ratio region
is no longer just "longer is better"; cells such as `⟨9,10⟩`,
`⟨5,17⟩`, and `⟨3,17⟩` become the visible targets.

The phase-space plot separates two effects. Length increases broadly
with the size of the ambient gap set, because more ACM survivors become
private atoms of `(S, ·)`. Raw `D_L*` mostly follows that length
gradient. The normalized panel is the first place where the ambient
semigroup shape appears as something other than size.

## Files

- `exp02_phase_space.py` — generator-grid sweep.
- `exp02_phase_space.txt` — ranked cells by length, `D_L*`, and
  benchmark ratio.
- `exp02_phase_space.png` — heatmaps for atom count, digit length,
  `D_L*`, and normalized discrepancy.
