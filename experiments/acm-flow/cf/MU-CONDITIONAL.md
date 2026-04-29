# Conditional irrationality measure — μ(C_b(n)) under spikes-dominate

`arguments/MEGA-SPIKE-FOUR-WAYS.md` lines 273–289 explicitly flag
that the spike formula gives `log_b(a_k) = Θ(b^{k-1})` and so
**constrains but does not determine** the irrationality measure of
`C_b(n)`. The constraint is: along the boundary-spike subsequence,
the partial-quotient growth gives a Liouville-type lower bound on
how well rationals approximate `C_b(n)`. Whether this is the binding
contribution to `μ(C_b(n))` depends on what off-spike PQs do, which
is the same off-spike denominator process gated at step 3 of
`MECHANISTIC-DERIVATION.md`.

This note: **under the assumption that spike events dominate the
approximation budget** (i.e., off-spike partial quotients don't
beat the spike events when computing `lim sup`), the conditional
value is

    μ(C_b(n))  =  2  +  (b − 1)(b − 2) / b,    independent of n,

for `b ≥ 4` where this is the binding constraint on irrationality
above the trivial `μ ≥ 2`.

For b = 10: **μ → 9.2.**

The load-bearing premise — "spikes dominate the approximation
budget" — is the same off-spike denominator process question gated
at `MECHANISTIC-DERIVATION.md` step 3. The two open questions are
*the same gap* viewed from two angles: closing one closes the other.


## Derivation

The standard CF irrationality-measure formula:

    μ(x)  =  2  +  lim sup_i  (log a_{i+1}) / (log q_i).

Along the boundary-spike subsequence `i = i_k`, from
`MEGA-SPIKE.md`'s closed form:

    log_b(a_{i_k+1})  ≈  T_k − 2 L_{k−1} + log_b(b/(b − 1))
                       =  D_k − C_{k−1} + 2 (C_{k−1} − L_{k−1}) + log_b(b/(b − 1))
                       ≈  S_k(n, b)    (when L_{k−1} ≈ C_{k−1}, i.e., off-spike inflation neglected)

    log_b(q_{i_k})    ≈  L_{k}    
                      ≈  C_{k−1}   to leading order  
                          + (n − 1) k + offset(n)    [from `OFFSPIKE-RESULT.md`]

To leading order:

    log_b(a_{i_k+1}) / log_b(q_{i_k})
        ≈  S_k(n, b) / C_{k−1}(n, b)
        =  F(d, b) · (n−1)/n²  /  [(n−1)/n² · ((d−1) b^d − d b^{d-1} + 1)/(b−1)]
        =  F(d, b) · (b − 1) / ((d−1) b^d − d b^{d-1} + 1).

The `(n − 1)/n²` cancels — the ratio is **independent of `n`**.

Expanding numerator: `F(d, b) · (b − 1) = d(b − 2)(b − 1) b^{d-1} + b^d − 1`.

Asymptotic, `d → ∞`:

    ratio  →  d (b − 2)(b − 1) b^{d-1} / ((d − 1) b^d)  →  (b − 2)(b − 1) / b.

So along the boundary-spike subsequence:

    lim sup  log_b(a_{i_k+1}) / log_b(q_{i_k})  =  (b − 1)(b − 2) / b.


## Empirical check

Predicted ratio `[d(b − 2)(b − 1) b^{d−1} + b^d − 1] / [(d − 1) b^d − d b^{d-1} + 1]` at b = 10:

| d | predicted ratio | empirical (n=2) |
|---:|---:|---:|
| 4 | 11.46 | 11.36 |
| 5 | 10.56 | 10.56 |
| 6 | 10.05 | (predicted) |
| 8 |  9.45 | (predicted) |
| ∞ |  7.20 | (asymptote) |

(Empirical values from `D5-RESULT.md` and `MULTI-K-RESULT.md`,
computed from `2 log_b q_{i_k} + log_b a_{i_k} = T_k` plus the
observed spike sizes.) The predicted asymptote `7.2 = (10 − 1)(10 −
2)/10` is approached from above as `d → ∞`.


## The load-bearing premise

The conditional μ assumes:

> The largest partial quotients of `C_b(n)` are at the d-block
> boundaries, i.e., for any off-boundary index `i`, the ratio
> `log_b(a_{i+1}) / log_b(q_i)` is asymptotically less than the
> boundary-subsequence limit `(b − 1)(b − 2) / b`.

This is what `MEGA-SPIKE.md` calls the "two-stream hypothesis" in
its strongest form: that the off-spike CF process produces only
Khinchin-typical (i.e., `O(1)` partial quotients on average) PQs.

Empirically, `OFFSPIKE-RESULT.md` and `MEGA-SPIKE-FOUR-WAYS.md`
report that off-spike PQ *sizes* (as opposed to denominators) are
Khinchin-typical at the precision tested. Off-spike *denominators*
inflate by `(n − 1)k + offset(n)` per d-block, which is the
boundary-spike-formula companion. The "PQ size" distinction is
critical for μ: μ is governed by PQ sizes, not denominator
inflation patterns.

So the empirical premise is **partially supported** at the precision
tested but **not proven**. A rigorous derivation would need to show
that off-spike `log a_{i+1} / log q_i` doesn't asymptotically exceed
`(b − 1)(b − 2) / b`. This is the same gap as the off-spike
denominator process.


## Coupling to MECHANISTIC-DERIVATION.md step 3

`MECHANISTIC-DERIVATION.md` step 3:

> Show that the convergent denominator `q_{i_k − 1}` equals
> `b^{T_{k-1} + (n−1)k + 1} / n^{j(n)}` to within `O(b^{-k})`
> corrections. (This is the load-bearing step; it links the integer
> divisibility of M to the convergent denominator.)

The spike formula plus this step would close the picture for the
mega-spike subsequence: predicted spike size, predicted convergent
denominator, exact identity at the boundary. **What's missing on
both sides** is the off-spike behavior between consecutive spikes:

- For step 3, the off-spike intermediate convergents (the `i` indices
  between consecutive boundary spikes) are unmodelled. The Family
  A/B classification of `offset(n)` by `ord(b, n)` is empirical.
- For the conditional μ, the off-spike PQ size distribution
  determines whether the boundary-spike `lim sup` is the binding
  one.

These are the **same gap**. The off-spike denominator process is
the unmodelled scalar in `MECHANISTIC-DERIVATION.md`; the off-spike
PQ size distribution is the unmodelled premise in this note. A
closed-form description of the off-spike CF process between
boundary spikes would simultaneously:
1. Pin down `offset(n)` as a derived quantity (closing step 3),
2. Determine whether off-boundary PQs ever exceed the boundary
   ratio `(b − 1)(b − 2)/b` (closing the conditional in this note).

So **the conditional μ result and the step 3 derivation are gated on
the same off-spike question.** Closing one closes the other.


## What this is and isn't

**Is.** A conditional irrationality-measure formula derived from
the spike formula, contingent on a clean premise about off-spike
behavior. The conditional is an explicit function of `b` alone (no
`n`-dependence) — `2 + (b − 1)(b − 2)/b`. For b = 10, μ → 9.2.

**Isn't.**

- A proof of `μ(C_b(n)) = 2 + (b − 1)(b − 2)/b`. The off-spike
  premise is empirically partially supported, not derived.
- A statement about normality. Normality of `C_b(n)` is a
  digit-frequency claim (see `core/BLOCK-UNIFORMITY.md` for the
  exact-uniformity result on each digit class), not a CF claim. The
  conditional μ here is consistent with normality but doesn't bear
  on it (see `MEGA-SPIKE-FOUR-WAYS.md` lines 281–283).
- A statement about transcendence. Mahler-type transcendence
  arguments use μ < ∞; the conditional gives a finite μ, supporting
  transcendence under the same off-spike premise. But "C_b(n) is
  transcendental" requires either a finite μ proof or a different
  route entirely.


## What this buys, conditional on the premise

Under "spikes dominate the approximation budget":

- The entire family `{C_b(n) : n ≥ 2}` at fixed `b ≥ 4` shares the
  same irrationality measure, controlled by `b` alone.
- For b = 10 the value is 9.2, comparable to but distinct from
  Mahler's classical Champernowne result μ = 10 (which uses the
  n=1-equivalent all-integers concatenation and has a slightly
  different boundary-spike rate).
- The premise has the same status across `n` and across `b`: the
  off-spike question is structural in the construction, not a
  per-`n` accident.


## Status

**Conditional, derived from the spike formula and the standard CF
identity.** The numerical evidence at b = 10 supports the predicted
ratio approaching 7.2 from above (predicted vs empirical at d ∈ {4,
5} matches to ~0.1 %). The premise is the load-bearing piece; it
sits at the same level of openness as `MECHANISTIC-DERIVATION.md`
step 3.


## Provenance

The constraint that the spike formula gives `log_b(a_k) = Θ(b^{k-1})`
was made explicit in `arguments/MEGA-SPIKE-FOUR-WAYS.md` lines
273–289. The conditional μ derivation here was originally done
under a parallel framing in
`experiments/acm-flow/cf/MAHLER-DERIVATION.md`
(now superseded; see status preamble there).

The off-spike gating cross-reference is to `MECHANISTIC-DERIVATION.md`
step 3 — both this note and that step are conditional on the same
unmodelled off-spike denominator process. Closing the off-spike
process closes both.

**This is the canonical home for the conditional μ result.**
