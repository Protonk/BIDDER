# EXP01 — Shared survivors

This ports the ACM survivor window into the interlock setting. The
bundle is still the ACM read order: rows `n = 2..20`, `k = 28` atoms per
row. The ambient numerical semigroup is `S = ⟨5,7⟩`, with

    G = {1, 2, 3, 4, 6, 8, 9, 11, 13, 16, 18, 23}.

Each bundle atom is classified as a gap, an element of `S` reducible in
`(S, ·)`, or an atom in `A_S`. The shared survivor stream `C_SurvA` is
the ACM survivor subsequence restricted to `A_S`.

## Empirical readout

```
bundle atoms          = 532
distinct integers     = 251
ACM survivors         = 113
gap hits              = 17
S-reducible hits      = 247
A_S hits              = 268
C_SurvA atoms         = 51
C_SurvA digit length  = 134
```

The first shared survivors are

    46, 58, 62, 74, 82, 86, 94, 106, 69, 87, 93, 111, 123,
    92, 116, 124, 148, 5, 115, 138, 174, 186, 7, 161.

The plot has four panels: the ordered ACM bundle with semigroup status
overlaid; the leading-digit L1 traces for the bundle, `C_Surv`, and
`C_SurvA`; per-row counts; and the first 134 digits of `C_SurvA`.

The first visible fact is that the shared filter is not a small
perturbation of ACM survival. Of 113 ACM survivors, only 51 remain in
`A_S`. Rows `10`, `14`, `15`, and `20` have ACM survivors but no shared
survivors; rows `2`, `3`, `4`, `16`, and `18` carry most of the shared
mass. That row imbalance is the first signal to follow.

## Files

- `exp01_shared_survivors.py` — experiment script.
- `exp01_shared_survivors.txt` — counts and first survivor values.
- `exp01_shared_survivors.png` — ordered bundle, L1 traces, row
  composition, and `C_SurvA` digit strip.
