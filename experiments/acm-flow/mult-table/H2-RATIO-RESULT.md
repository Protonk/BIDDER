# Ratio Test M_n(K) / M_Ford(K) — Outcome 2 (likely)

The cross-thread agent's recommended disambiguator. Per the
suggestion, we ran the ratio test before proposing any analytic
target. The result determines which analytic target to pose.

## Predictions

`BRIEF4-h2.md` derives `M_n(K) ~ ((n−1)/n)² · K · κ_F · (log K)^{−c} · (log log K)^{−3/2}`.
`M_Ford(K) ~ K · κ_F · (log K)^{−c} · (log log K)^{−3/2}`.

The ratio cancels Φ(K) exactly:

    M_n(K) / M_Ford(K)  →  α_n² = ((n−1)/n)²    (uniformly in K)

Three outcomes:

  - **Outcome 1**: ratio settles at α_n². Drift in `M_n · Φ(N)/N` is
    finite-N correction in Φ.
  - **Outcome 2**: ratio drifts upward toward α_n. Anatomy non-invariant
    on coprime-to-n; the conditional balance probability differs.
  - **Outcome 3**: ratio drifts in some other shape.

## Result — Outcome 2 (likely) or 3 (functional form unclear)

Empirical M_n(K) / M_Ford(K) at K = 10⁴ … 10⁷:

| n | α_n² | K=10⁴ | K=10⁵ | K=10⁶ | K=10⁷ | α_n |
|---|---|---|---|---|---|---|
| 2 | 0.2500 | 0.3579 | 0.3652 | 0.3712 | **0.3749** | 0.5000 |
| 3 | 0.4444 | 0.5351 | 0.5445 | 0.5499 | 0.5543 | 0.6667 |
| 5 | 0.6400 | 0.6910 | 0.7033 | 0.7099 | 0.7150 | 0.8000 |
| 7 | 0.7347 | 0.7688 | 0.7787 | 0.7856 | 0.7891 | 0.8571 |
| 11 | 0.8264 | 0.8427 | 0.8543 | 0.8573 | 0.8598 | 0.9091 |
| 13 | 0.8521 | 0.8689 | 0.8717 | 0.8773 | 0.8795 | 0.9231 |

**Two observations:**

1. **For every n, the ratio is growing with K** — drifting *toward* α_n,
   *away* from α_n². The diff from α_n² is **growing** with K, not
   shrinking. So the BRIEF4-h2 prediction `→ α_n²` is **rejected**.

2. **At K=10⁷, ratios sit close to (α_n + α_n²)/2 = α_n(1+α_n)/2**:

| n | observed | (α_n + α_n²)/2 | diff |
|---|---|---|---|
| 2 | 0.3749 | 0.3750 | −0.0001 |
| 3 | 0.5543 | 0.5556 | −0.0013 |
| 5 | 0.7150 | 0.7200 | −0.0050 |
| 7 | 0.7891 | 0.7959 | −0.0068 |
| 11 | 0.8598 | 0.8678 | −0.0080 |
| 13 | 0.8795 | 0.8876 | −0.0081 |

Match for n=2 is to 4 decimals. Larger n undershoots slightly with
non-monotone error. The drift is still upward, so even at K=10⁷ we
may be pre-asymptotic — but the convergence target may be exactly
`α_n(1+α_n)/2 = (n−1)(2n−1) / (2n²)` or it may be `α_n` reached very
slowly.

## Per-decade drift

The drift slows but doesn't stop. Drift in ratio per decade of K
between consecutive K values:

| n | 10⁴→10⁵ | 10⁵→10⁶ | 10⁶→10⁷ |
|---|---|---|---|
| 2 | +0.0073 | +0.0060 | +0.0037 |
| 3 | +0.0094 | +0.0055 | +0.0044 |
| 5 | +0.0123 | +0.0066 | +0.0051 |
| 7 | +0.0099 | +0.0069 | +0.0035 |
| 11 | +0.0116 | +0.0030 | +0.0025 |
| 13 | +0.0028 | +0.0055 | +0.0023 |

Drifts are decreasing. Whether they reach 0 (ratio settles) or
asymptote to some non-zero rate (ratio continues drifting toward α_n)
is not determined at K = 10⁷.

## Interpretation

**The α_n² prediction in `BRIEF4-h2.md` is empirically rejected.** The
"anatomy invariance applied to pairs" argument that gave α_n² is too
coarse; the conditional density of coprime-to-n integers on Ford's
multiplication-table image differs from independent-pair density.

**The drift direction (toward α_n) is consistent with the cross-thread
agent's outcome 2 reading**: anatomy invariance fails for
coprime-to-n; the conditional balance probability P(k balanced | k ⊥ n)
differs from 1/Φ(K). But the apparent intermediate limit
(α_n + α_n²)/2 — if real — points to outcome 3 with a specific
functional form, not pure outcome 2.

**The c-shift in the bare count `M_n · Φ(N)/N` is now traceable to a
real anatomy difference between coprime-to-n integers and ordinary
integers in the Ford image.** Whatever the exact asymptotic limit
(α_n, α_n + α_n², or something else), the residue restriction is *not*
Ford-flat-invisible.

## Mechanism intuition

For prime n=2, multiples of 2 are over-represented in the Ford image:
small primes contribute disproportionately to "balanced factorability"
(many divisors → many candidate factorizations → easier to land in the
multiplication-table image). Excluding multiples of 2 (residue
restriction to coprime-to-2) removes a share of the Ford image
*greater* than α_n² of pairs would suggest, but *less* than (1 − α_n)
of total integers — because some compensating effect kicks in.

The exact conditional probability `P(k ⊥ n | k ∈ Ford-image-of-K)` is
the analytic target.

## What the cross-thread agent's recommendation says next

Per their framing:

> **Outcome 2 → (α′)** with conditional balance probability as target.
> **Outcome 3 → reframe; possibly a Meisner pull.**

We're between 2 and 3. The narrower question is `P(k ⊥ n | k ∈ Ford
image)`. If it equals α_n in the limit, outcome 2 (slow convergence).
If it equals α_n(1+α_n)/2, outcome 3 with specific form.

This is **substantially narrower** than the open-ended cell-decomposition
question I had as (α′). The analytic literature on "anatomy of integers
in residue classes" (Tenenbaum's *Introduction to Analytic and
Probabilistic Number Theory*, Ch. III; Norton's papers on coprime-to-n
multiplicative functions; Koukoulopoulos's k-fold table on residue
classes) has the right tools.

## S_n(N) — Q-weighted sum data

Computed on the same enumeration. `S_n(N) = Σ_{m ∈ M_n^{(2)}(N)} Q_n(m) · log(m)`
with `N = K · n²`:

|   n | K=10⁴ | K=10⁵ | K=10⁶ | K=10⁷ |
|---|---|---|---|---|
| 2 | −29,279 | −479,270 | −7,170,312 | −100,632,123 |
| 3 | −71,541 | −1,109,686 | −16,128,356 | −221,053,363 |
| 5 | −124,300 | −1,915,052 | −27,282,884 | −368,926,702 |
| 7 | −158,551 | −2,382,792 | −33,816,003 | −452,785,909 |
| 11 | −195,263 | −2,939,498 | −41,093,401 | −546,603,801 |
| 13 | −211,071 | −3,103,177 | −43,420,294 | −576,197,710 |

Normalized `S_n(N) / N` does **not** stabilize — it grows in magnitude
with K because mean `|Q_n|` grows with `log K` via mean `d(k)`. So
`S_n / N` isn't the right Q-weighted observable for a stable
asymptote; `S_n / (N · log N)` or similar correction would be.

## Verdict on FINITE-RANK-EXPANSION speculation

The cell distribution shifts with n at fixed K (`H2-FIXEDK-RESULT.md`
established this cleanly). The bare ratio test in this doc shows the
shift's aggregate effect on M_n(K) goes beyond α_n² density. So at
h=2 we have:

- Local Q_n algebra (closed): exact and finite.
- Global anatomy on coprime-to-n image: structured, n-dependent.
- Aggregate ratio M_n / M_Ford: real n-dependent shift, not α_n².

The "shadows of rank layers" speculation has empirical support in the
form: residue restriction shifts the Ford-image's coprime-density
non-trivially. The exact mapping from Q_n's local algebra to this
global shift is the open question; the conditional-probability framing
gives it a sharper analytic target than I had before.

## What I'd do next

(α′) is now the right move with a sharp target: derive
`P(k ⊥ n | k ∈ Ford-image-of-K)` for K → ∞.

If the answer is `α_n(1 + α_n)/2 = (n−1)(2n−1)/(2n²)`, that's a
substantive new structural result. If it's α_n, outcome 2's slow
convergence holds. Either way, it tells us what residue restriction
does to the multiplication-table image at the leading order.

Composite n (δ) and Q-weighted asymptotics for S_n still deferred —
prime n's primary disambiguation isn't fully closed.

## Files

- `h2_ratio_vs_ford.py` — ratio test enumeration + S_n.
- `h2_ratio_vs_ford.csv` — per-(n, K) data.
- `h2_ratio_vs_ford_summary.txt` — full diagnostic tables.
- This document: the writeup.
