# Conditional irrationality measure of C_b(n)

The spike formula

    log_b(a_{i_k}) = T_k − 2 L_{k−1} + log_b(b/(b − 1)) − O(b^{−k})

(`MEGA-SPIKE.md`) gives `log_b(a_k) = Θ(b^{k−1})` along the
boundary-spike subsequence. Under the assumption that boundary
spikes dominate the approximation budget — i.e., off-spike partial
quotients don't beat the spike events when computing `lim sup` —
the irrationality measure of `C_b(n)` has the closed form

    μ(C_b(n)) = 2 + (b − 1)(b − 2) / b,    independent of n,

valid for `b ≥ 4` where this is the binding constraint above the
trivial `μ ≥ 2`. For `b = 10` the conditional value is `9.2`.


## Derivation

The standard CF irrationality-measure formula:

    μ(x) = 2 + lim sup_i  (log a_{i+1}) / (log q_i).

Along the boundary-spike subsequence `i = i_k`, from the spike
formula:

    log_b(a_{i_k+1}) ≈ T_k − 2 L_{k−1} + log_b(b/(b − 1))
                     = D_k − C_{k−1} + 2(C_{k−1} − L_{k−1}) + log_b(b/(b − 1))
                     ≈ S_k(n, b)    (when L_{k−1} ≈ C_{k−1}, off-spike inflation neglected),
    log_b(q_{i_k})    ≈ L_k
                      ≈ C_{k−1} + (n − 1) k + offset(n)    (`OFFSPIKE-RESULT.md`).

The leading-order ratio:

    log_b(a_{i_k+1}) / log_b(q_{i_k})
        ≈ S_k(n, b) / C_{k−1}(n, b)
        =  F(d, b) · (b − 1) / ((d − 1) b^d − d b^{d−1} + 1).

The `(n − 1)/n²` factor cancels — the ratio is independent of `n`.
Expanding the numerator: `F(d, b) · (b − 1) = d (b − 2)(b − 1) b^{d−1} + b^d − 1`.
Asymptotic in `d`:

    ratio  →  d (b − 2)(b − 1) b^{d−1} / ((d − 1) b^d)  →  (b − 2)(b − 1) / b.

So along the boundary-spike subsequence,

    lim sup  log_b(a_{i_k+1}) / log_b(q_{i_k}) = (b − 1)(b − 2) / b.


## Empirical check

Predicted ratio
`[d (b − 2)(b − 1) b^{d−1} + b^d − 1] / [(d − 1) b^d − d b^{d−1} + 1]`
at `b = 10`:

| d | predicted ratio | empirical (n=2) |
|---:|---:|---:|
| 4 | 11.46 | 11.36 |
| 5 | 10.56 | 10.56 |
| 6 | 10.05 | (predicted) |
| 8 |  9.45 | (predicted) |
| ∞ |  7.20 | (asymptote) |

Empirical values from `D5-RESULT.md` and `MULTI-K-RESULT.md`,
computed from `2 log_b q_{i_k} + log_b a_{i_k} = T_k` plus the
observed spike sizes. The predicted asymptote
`7.2 = (10 − 1)(10 − 2)/10` is approached from above as `d → ∞`,
giving `μ → 2 + 7.2 = 9.2`.


## The load-bearing premise

The conditional μ assumes:

> The largest partial quotients of `C_b(n)` are at the d-block
> boundaries, i.e., for any off-boundary index `i`, the ratio
> `log_b(a_{i+1}) / log_b(q_i)` is asymptotically less than the
> boundary-subsequence limit `(b − 1)(b − 2) / b`.

Empirically, off-spike partial-quotient *sizes* (as opposed to
denominators) are Khinchin-typical at the precision tested
(`OFFSPIKE-RESULT.md`). Off-spike *denominators* inflate by
`(n − 1) k + offset(n)` per d-block, but `μ` is governed by PQ
sizes, not denominator inflation patterns.

So the premise is partially supported empirically, not proven. A
rigorous derivation would need to show that off-spike
`log a_{i+1} / log q_i` does not asymptotically exceed
`(b − 1)(b − 2) / b`. This is the off-spike denominator process
question.


## Coupling to step 3 of MECHANISTIC-DERIVATION

`MECHANISTIC-DERIVATION.md` step 3:

> Show that the convergent denominator `q_{i_k − 1}` equals
> `b^{T_{k−1} + (n−1)k + 1} / n^{j(n)}` to within `O(b^{−k})`
> corrections.

The spike formula plus this step would close the picture for the
mega-spike subsequence: predicted spike size, predicted convergent
denominator, exact identity at the boundary. What's missing on
both sides is the off-spike behaviour between consecutive spikes:

- For step 3, the off-spike intermediate convergents (between
  consecutive boundary spikes) are unmodelled.
- For the conditional μ, the off-spike PQ size distribution
  determines whether the boundary-spike `lim sup` is the binding
  one.

These are the same gap. A closed-form description of the off-spike
CF process between boundary spikes would simultaneously pin
`offset(n)` as a derived quantity (closing step 3) and determine
whether off-boundary PQs ever exceed the boundary ratio
`(b − 1)(b − 2)/b` (closing the conditional). Closing the
off-spike process closes both.


## What this is and isn't

This is a conditional irrationality-measure formula derived from
the spike formula and the standard CF identity. The conditional
is an explicit function of `b` alone (no `n`-dependence):
`2 + (b − 1)(b − 2) / b`. For `b = 10`, μ → 9.2.

Not a proof of `μ(C_b(n)) = 2 + (b − 1)(b − 2)/b`. The off-spike
premise is empirically partially supported, not derived.

Not a statement about normality. Normality of `C_b(n)` is a
digit-frequency claim (`core/BLOCK-UNIFORMITY.md` gives the
exact-uniformity result on each digit class), not a CF claim.

Not a statement about transcendence. Mahler-type transcendence
arguments use `μ < ∞`; the conditional gives a finite μ, supporting
transcendence under the same off-spike premise. But "C_b(n) is
transcendental" requires either a finite μ proof or a different
route entirely.


## Consequences, conditional on the premise

Under "spikes dominate the approximation budget":

- The entire family `{C_b(n) : n ≥ 2}` at fixed `b ≥ 4` shares the
  same irrationality measure, controlled by `b` alone.
- For b = 10 the value is `9.2`, comparable to but distinct from
  Mahler's classical Champernowne result `μ = 10`.
- The premise has the same status across `n` and across `b`: the
  off-spike question is structural in the construction, not a
  per-`n` or per-`b` accident.
