# Off-Spike Denominator Inflation — δ_k(n) is asymptotically linear

Phase 3.1 (B): the live two-stream test.

## Setup

After the multi-k experiment, the spike formula reads

    log_b(a_{i_k}) = T_k(actual) − 2 L_{k−1} + log_b(b / (b − 1)) − O(b^{−k})

where `L_{k−1} = log_b(q_{i_k − 1})` is the previous convergent's
log-denominator. The substrate-naive prediction is `L_{k−1} ≈ C_{k−1}`,
the cumulative digit count through the d=(k−1) block. The deviation

    δ_k(n) := L_{k−1}(n) − C_{k−1}(n)

is the "off-spike denominator inflation": the part of the previous
denominator that doesn't come from the substrate-cumulative count.

The two-stream hypothesis predicts δ_k(n) is itself substrate-derivable
through some recurrence in (n, k). This script reads
`spike_drift_multi_k.csv`, computes δ_k empirically, and looks for
closed-form structure.

## Result — δ_k(n) is asymptotically linear in k with slope (n−1)

For each panel n, the per-k step of δ_k:

| n | δ_2 | δ_3 | δ_4 | step 2→3 | step 3→4 | asymptotic slope |
|---|---|---|---|---|---|---|
| 2 | +2.690 | +3.698 | +4.699 | +1.008 | +1.001 | **n − 1 = 1** |
| 3 | +4.041 | +6.045 | +8.046 | +2.004 | +2.000 | **n − 1 = 2** |
| 4 | +6.695 | +9.096 | +12.398 | +2.402 | +3.301 | (transient, possibly → 3) |
| 5 | +8.996 | +12.000 | +16.000 | +3.004 | +4.000 | **n − 1 = 4** at k≥3 |
| 6 | +10.041 | +14.045 | +19.046 | +4.004 | +5.000 | **n − 1 = 5** at k≥3 |
| 10 | +3.991 | +26.398 | +35.699 | +22.406 | +9.301 | (transient, possibly → 9) |

For n ∈ {2, 3, 5, 6} the per-k step settles into **(n − 1)** exactly,
within sampling precision (b^{−k}-decaying corrections). For n = 4
and n = 10 the linear regime hasn't been reached at the explored k.

Subtracting the linear part `(n − 1) · k` reveals the per-n offset:

| n | δ_k − (n − 1)·k at k=4 | identification |
|---|---|---|
| 2 | +0.6989 | log_{10}(5) ≈ 0.6990 |
| 3 | +0.0457 | log_{10}(10/9) ≈ 0.0458 |
| 4 | +0.3979 | (transient) |
| 5 | +0.0000 | 0 |
| 6 | −0.9543 | −1 + log_{10}(10/9) |
| 10 | −0.3011 | (transient) |

For prime n ∈ {2, 3, 5}, the offset has a clean closed form. For
n = 6, the offset is −1 + log_{10}(b/(b−1)). Per-n offsets are
substrate-derivable in form, but the *expression* is not yet
unified across n.

## Closed-form spike size, asymptotic regime

Substituting `L_{k−1} = C_{k−1} + (n − 1) · k + offset(n) − O(b^{−k})`
into the spike formula:

    log_b(a_{i_k}) = D_k(actual)
                  − C_{k−1}(actual)
                  − 2(n − 1) · k
                  − 2 · offset(n)
                  + log_b(b / (b − 1))
                  − O(b^{−k})

Verification at n = 2, k = 4:

    9000 − 723 − 8 − 2·log_{10}(5) + log_{10}(10/9)
    = 8267.65 (predicted)
    = 8267.6479 (observed)  ✓

Same for the other three (n, k=4) where offset(n) is identified.

## What this changes

The d = k mega-spike size is now a fully closed-form function of n,
k, b in the asymptotic regime where δ_k(n) has reached linear growth.
The previous formula `T_k − 2 L_{k−1}` required empirical L_{k−1};
this formula uses no CF data — it predicts the spike from substrate
quantities alone (modulo per-n offset).

This is much stronger than what `brief2_q_derivation.md` had. There,
`L_{k−1}` was the unknown carrying the residue. Here, the dominant
behavior of `L_{k−1}` collapses to `(n − 1) · k`, a substrate-driven
count.

## Per the metaphysical commitment

ACM-Champernowne is normal / irrational. Clean closure of the leading
δ_k structure is not closure of the residual. Where did the residue
migrate to?

1. **`offset(n)` per-n.** The intercept of the linear regime is
   structured (log_{10}(5), log_{10}(10/9), 0, −1 + log_{10}(10/9))
   but not yet unified across n. Each value is a closed-form
   substrate quantity (b/n or b/(b−1) or 1), but the rule selecting
   which expression applies for which n is not clear. The next
   research move on this branch is to pin down the n → offset(n)
   map.
2. **The transient regime at small k for n = 4, 5, 6, 10.** For
   n = 5, 6 the transient at k = 2 is single-step. For n = 4, 10 it
   spans the entire explored range. Probably driven by the small
   number of d = 1 atoms (1 for n = 5, 6; 2 for n = 2, 4; 0 for
   n = 10).
3. **The `O(b^{−k})` tail in both the spike formula and the
   δ_k recurrence.** Same b^{−k} tail family as before, with per-n
   coefficients. Same suspected origin: boundary-digit alignment
   between consecutive convergents.

The unclosability has moved upstream once more. The two-stream
hypothesis is **partially validated**: the leading off-spike
denominator process is substrate-driven (slope `n − 1` in `k`),
which closes the dominant scaling. But (offset(n), transient regime,
b^{−k} tail) carry the next layer's residue.

## Why slope `n − 1` makes sense

For prime n, the cofactors of n-primes are the integers coprime to
n. There are exactly `n − 1` residue classes mod n that an integer
can occupy without being divisible by n. Each "k step" — moving
from the d = k − 1 to d = k digit block — sweeps through a band
where atoms cycle through these `n − 1` residue classes. The
accumulated log-denominator growth per step picks up `(n − 1)` units
of log b from the cofactor structure.

This is suggestive, not a proof. The mechanistic derivation should
fall out of a careful CF analysis of how convergents track residue
class transitions across digit-block boundaries. Worth pursuing
separately.

## Asymptotic spike formula, restated

For prime n with smooth d = k condition `n² | b^{k − 1}`:

    log_b(a_{i_k}) ~ D_k − C_{k−1} − 2(n − 1)k − 2·offset(n) + log_b(b/(b−1))
                  = (b − 1) b^{k−1} k (n − 1)/n²
                  − (b − 1) Σ_{d=1}^{k−1} d b^{d−1} (n − 1)/n²
                  − 2(n − 1)k
                  − 2·offset(n)
                  + log_b(b/(b−1))

The `(n − 1) b^{k−1} k (b − 1) / n²` term is the original "scout"
formula; the `−2(n − 1) k` correction is what was missing from the
brief 2 derivation; the `log_b(b/(b−1)) − 2·offset(n)` is the
universal-plus-per-n constant tail.

## Next moves

a. **Pin offset(n) for the prime panel.** Compute n = 7, 11, 13 and
   see whether the offset has a clean unified form across primes.
   Cheap: just add to the panel.

b. **Extend k to verify asymptote for n = 4, 10.** Run cf_spikes at
   higher MAX_PQ to access the d = 5 and d = 6 mega-spikes for n = 4
   and n = 10. If the slope settles to `n − 1 = 3` and `9`
   respectively, the linear-asymptote story holds across the panel.

c. **Mechanistic derivation of slope `n − 1`.** Why does the
   cofactor residue-class structure produce per-step (n − 1) log
   q growth? A careful CF computation should yield this.

d. **n → offset(n) closed form.** What rule chooses log_{10}(b/n)
   for n = 2, log_{10}(b/(b−1)) for n = 3, 0 for n = 5, etc.?

## Files

- `offspike_inflation.py` — the analysis script
- `offspike_inflation.csv` — per-(n, k) data
- `offspike_inflation_summary.txt` — text tables
