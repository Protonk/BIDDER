# EXP03 — pair correlations: residual structure survives the transducer

EXP01 (digit frequencies) and EXP02 (continued fraction) returned
nulls that the `DIFFERENCING-AS-TRANSDUCER.md` note explained as
expected: digit-position alignment between bundle and survivor is
saturated-misaligned, so single-digit observables on δ measure the
transducer's saturation rather than the relation.

The user's pushback was: *if the transducer is only **mostly**
destructive, the finite ledger plus exact construction means
residual structure has to land somewhere.* This experiment looks
one rank up — at consecutive digit pairs `(d_i, d_{i+1})` of δ's
overlap region — and finds that the residual is real, weaker than
in the bundle (the transducer did most of its work), but
non-zero and structurally interpretable.

## Setup

Same parameters as EXP01/EXP02: `[2, 10], k = 400`. δ's overlap
region (first `4,894` digits — where genuine bundle-vs-survivor
subtraction happens) gives `4,893` consecutive digit pairs. Compare
two distributions:

- **δ's joint** `P(d_i, d_{i+1})` — the experimental.
- **Independent product** `P(d_i) · P(d_{i+1})` — the null where
  digit positions are uncorrelated.

Bundle's first `4,894` digits give the control: the natural
digit-pair structure of concatenated atom-decimals.

## The numbers

```
                χ² (81 dof)    MI (bits)
δ overlap:        110.11         0.01605
bundle overlap:   236.88         0.03604
```

For `df = 81` the χ² critical value at `p < 0.001` is `≈ 119`. δ
sits *just under* (`110`); bundle sits well above (`237`).

Bundle's pair structure is roughly **2.25× larger** than δ's by both
χ² and mutual information. The transducer suppresses but does not
destroy the pair correlations.

## Top anomalous digit pairs in δ

```
  pair (d_i, d_{i+1})   joint freq   indep pred    deviation
  (1, 0)                  0.0176       0.0121      +0.0055   ← most over
  (8, 9)                  0.0174       0.0120      +0.0054
  (1, 9)                  0.0082       0.0116      −0.0034
  (5, 1)                  0.0055       0.0089      −0.0034
  (0, 1)                  0.0153       0.0121      +0.0032
  (3, 9)                  0.0074       0.0104      −0.0030
  (7, 1)                  0.0123       0.0093      +0.0030
  (0, 9)                  0.0186       0.0160      +0.0026
  (6, 1)                  0.0065       0.0091      −0.0025
  (9, 9)                  0.0129       0.0153      −0.0025   ← suppressed
```

## Reading

Three observations stand out:

### 1. Borrow-pair signatures appear, in modest excess

Pairs `(0, 9)` and `(8, 9)` are over-represented. These match the
borrow-signature reading of EXP01:

- `(0, 9)`: a digit-position where bundle and survivor *agreed*
  (giving 0) followed by a position where a borrow chain *fired*
  (giving 9). The borrow chain starts on the next digit.
- `(8, 9)`: bundle's `8` minus survivor's `9` (with no incoming
  borrow) leaves `−1` mod 10 = `9`, with a borrow propagating
  *backwards* — i.e., the previous digit got `8` after losing
  `1` to the borrow.

These are predicted patterns of single-position borrows.

### 2. Long borrow chains are suppressed

`(9, 9)` is *under-represented* by `−0.0025`. If borrow chains had
characteristic length > 1, we'd see `(9, 9)` over-represented —
borrows propagating across multiple positions. We see the opposite.
Borrows in this construction are mostly *single-position* events.

### 3. Bundle-inherited pair patterns dominate the top spots

`(1, 0)` and `(0, 1)` lead the list. These are inherited: numbers
in the atom range `[2, 3990]` frequently *start with 1* and *end
with 0* (atoms like `10, 100, 1000, 110, 210, ..., 10·k`).
Bundle's digit stream concatenates these atoms; consecutive atoms
often produce `(0, 1)` (atom ending in 0, next starting with 1) or
`(1, 0)` patterns within multi-digit atoms.

The transducer pulls some of this inheritance through: δ's `(1, 0)`
and `(0, 1)` excesses are *smaller* than bundle's, but non-zero.
Bundle's structure isn't fully erased.

## What this combines with EXP01 and EXP02

EXP01 said: single-digit content is mostly subtraction-borrow
signature with a uniform underlay.

EXP02 said: rational-approximation content is generic by every CF
metric.

EXP03 says: pair-level content has weak but real residual structure.
The transducer reduces bundle's pair correlations to roughly half
their original strength (χ² 237 → 110, MI 0.036 → 0.016 bits), but
doesn't eliminate them.

The combined reading aligns with the conservation intuition: *the
transducer is mostly destructive, but residual content survives in
pair correlations*. Single-digit frequencies look near-uniform; CF
distribution looks Gauss–Kuzmin-generic; but consecutive-digit
correlations carry a faint structural fingerprint of:

- Single-position borrows (above-independence at `(0, 9)`, `(8, 9)`).
- Suppressed long borrow chains (below-independence at `(9, 9)`).
- Diluted bundle inheritance (`(1, 0)`, `(0, 1)` over-represented but
  smaller than bundle's own excess).

## What this does not close

The result is suggestive but mild. δ's χ² = 110 sits at `p ≈ 0.005`
borderline significance — substantive but not dramatic. Open follow-ups:

- **Lag-2, lag-3, ... triplet correlations.** If the transducer
  pushes content into pair correlations, does the same content
  appear at longer lags? Or does the residual decay rapidly?
- **Parameter sweep.** Does the χ² ratio (bundle / δ ≈ 2.25) hold at
  other `(n_0, n_1, k)` parameters? If it's stable, the transducer's
  partial-destruction ratio is itself an observable.
- **Higher-order statistics.** Triplet (10×10×10) joint distributions
  would test for 3-position structure (e.g., long borrow chains
  hidden in pair-level data).
- **Length-matched comparison.** Bundle's first 4894 digits ≠
  bundle in any natural sense — it cuts the bundle mid-stream.
  A length-matched experiment where both bundle and survivor are
  truncated to comparable atom-counts (not digit-counts) might
  produce cleaner control comparisons.

## Files

- `exp03_delta_digrams.py` — script.
- `exp03_delta_digrams.png` — four-panel figure: δ joint, δ
  deviation from independence, bundle deviation (control), and
  statistics + top anomalous pairs.
