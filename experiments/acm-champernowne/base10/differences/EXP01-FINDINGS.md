# EXP01 — δ digit-frequency, split into overlap and tail

First reading of `δ = C_Bundle − C_Surv` at the Two Tongues panel
parameters (`[n_0, n_1] = [2, 10]`, `k = 400`). The naive question:
*is δ's decimal expansion uniform, or does it carry residual
structure?* The split analysis says **both**, but for different
reasons.

## Setup

`C_Bundle` and `C_Surv` are exact reals built as
`1.<digit-concatenation>`. Both have power-of-10 denominators, so
both are *terminating* decimals with no periodic tail.

| | length | denominator |
|---|---|---|
| `C_Bundle` | `12,874` digits | `10^12,874` |
| `C_Surv`   | `4,894` digits  | `10^4,894`  |

`δ = C_Bundle − C_Surv ≈ +3.875 × 10⁻²` (positive — the bundle is
slightly *larger* as a real than the survivor's first-appearance
concatenation).

When we subtract these as reals on a common denominator `10^12,874`,
`C_Surv` contributes zeros after digit `4,894`. At this panel `δ > 0`,
so `|δ| = δ` and:

- The **first 4,894 digits** of `|δ|`'s expansion = the substantive
  bundle-vs-survivor subtraction (with possible borrows).
- The **last 7,980 digits** of `|δ|`'s expansion = bundle's last
  7,980 digits *unchanged* (since survivor contributes zero there).

(If `δ < 0` at some other panel, `|δ| = −δ` and the tail-leak
analysis would differ — the absolute value would invert the digit
arithmetic. The split below is panel-specific to `δ > 0`.)

The full δ is the concatenation of these two regions. Treating them
as one observable mixes substantive content with bundle-tail
inheritance.

## The numbers

```
region          | digits   | L1 vs 1/10 | χ² (9 dof)
----------------+----------+------------+-----------
full δ          |  12,874  | 0.1893     |  592.20
overlap (first) |   4,894  | 0.1063     |   95.38
tail (last)     |   7,980  | 0.2942     |  957.59
```

## Three readings

### 1. The full-δ bias is dominated by bundle's tail

The full-δ digit distribution is biased toward small digits
(`0, 1, 2` at ~13% each; `7, 9` at ~7-8%). This looks Benford-ish.
But the tail alone — which is *just bundle's last 7,980 digits* —
has an even more pronounced version of the same bias (`2` at 16.5%,
`9` at 6.0%, χ² = 958). The tail is leaking through the full
analysis.

This isn't surprising: bundle's atoms are integers up to `10 × 399 =
3990`, and concatenating their decimal representations naturally
produces a Benford-skewed digit stream (small leading digits are
more frequent in numbers spanning multiple decades). The *tail of
the bundle* inherits this; the full δ inherits it from the tail.

### 2. The overlap region has a *different* signature

The overlap region (first 4,894 digits — where bundle and survivor
are genuinely fighting) is closer to uniform (L1 = 0.11, χ² = 95)
but distinctively non-uniform in a different way:

- **Digit 0** spikes at 12.9% (vs 10% expected).
- **Digit 9** spikes at 12.4%.
- **Digits 1–8** are mildly suppressed (range 8.4% to 9.9%).

The "spike at both 0 and 9" pattern is the signature of *subtraction
with borrows*. Where the bundle's digit equals the survivor's digit
(no borrow needed), the difference contributes `0`. Where a borrow
propagates from a higher-order position, the immediate result is `9`.
A clean subtraction of two unrelated digit streams would produce
this signature: 0s where digits coincide, 9s where borrow chains
fire, mild suppression of intermediate digits.

The overlap region's digit distribution is *not* an inheritance of
bundle's content. It's the **arithmetic shape of the subtraction**.

### 3. The substantive question survives

Excluding digits 0 and 9, the overlap region's digits 1–8 are within
~1% of uniform. So whatever genuine content the bundle-vs-survivor
*relation* carries — beyond the L1 tracking that the cabinet's Two
Tongues curiosity records — is *small in this observable*. The
overlap region's leftover bias is mostly the borrow-signature, not
deeper structure.

This is the first answer to the perpendicular question: **the L1
tracking story is largely the whole story** at the digit-frequency
level. The relation's residual structure, if any, doesn't show up as
a clean per-digit skew in δ's overlap region.

## What's next

The result narrows the question rather than closing it:

- **Pair correlations.** The borrow-signature lives in *digit pairs*
  (a `9` is often preceded by another `9` or by a near-equal pair).
  A digram or per-position autocorrelation of the overlap region
  would isolate the subtraction-borrow content from any genuine
  structural residual.
- **Length-matched comparison.** Truncate `C_Bundle` to its first
  4,894 digits (matching `C_Surv`'s length), recompute δ, and ask
  whether the digit signature changes. If it does, the
  finite-tail effect is doing more work than this experiment
  attributes to it.
- **Parameter sweep.** Repeat at `[2, 5]`, `[2, 20]`, `[5, 15]`,
  `k ∈ {100, 200, 800}`. If the overlap signature is roughly
  invariant ("0 and 9 spike, 1–8 uniform"), the residual is
  generic; if it varies with parameters, the survivor filter
  imprints something that this analysis can detect.
- **Continued-fraction expansion.** A different lens entirely. The
  first few partial quotients of `δ`'s continued fraction are
  cheap and might reveal periodicities the digit view averages.

## Files

- `exp01_delta_digits.py` — script.
- `exp01_delta_digits.png` — three-panel figure: full δ, overlap, tail.
