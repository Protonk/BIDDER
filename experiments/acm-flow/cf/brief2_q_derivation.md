# Brief 2 Derivation Attempt

Phase 3.1 asks where the ACM-Champernowne continued-fraction
mega-spike comes from.

Short answer: the main term is block-boundary geometry. The residual is
not random; it is mostly denominator inflation from earlier CF
structure. That is exactly the two-stream issue: the spike stream is
simple, the background stream is structured, and the observed spike
height depends on how the two have already interacted.


## Exact Block Algebra

Work in base `b`, digit block `k`, and monoid index `n >= 2`.
Under the smooth block condition `n^2 | b^(k-1)`,
`core/BLOCK-UNIFORMITY.md` gives the exact count of k-digit n-primes:

    N_k(n,b) = (b-1) * b^(k-1) * (n-1) / n^2.

So the k-digit block contributes

    D_k(n,b) = k * N_k(n,b)

digits to the concatenated real. The previous blocks contribute

    C_{k-1}(n,b)
      = (b-1) * (n-1)/n^2 * sum_{d=1}^{k-1} d*b^(d-1).

Using

    sum_{d=1}^{k-1} d*b^(d-1)
      = ((k-1)*b^k - k*b^(k-1) + 1) / (b-1)^2,

the naive boundary-mass prediction is

    D_k - C_{k-1}
      = (n-1)/n^2 *
        ( b^(k-1) * (k*(b-2) + b/(b-1)) - 1/(b-1) ).

For base 10:

    D_k - C_{k-1}
      = (n-1)/n^2 * ( 10^(k-1) * (8k + 10/9) - 1/9 ).

At `k = 4`, this is

    33111 * (n-1)/n^2.

The earlier scout

    (b-1)^2 * b^(k-2) * (n-1) * k / n^2

is the leading block-mass term. It misses the cumulative previous
blocks, so it should be close but not exact.


## CF-Scale Heuristic

Let `T_k` be the digit position of the k-block boundary. In the smooth
main term,

    T_k = C_{k-1} + D_k.

For a continued-fraction convergent just before the boundary,

    |x - p/q| ~ 1 / (a*q^2).

If the boundary truncation gives error scale about `b^(-T_k)`, then

    log_b(a) ~ T_k - 2*log_b(q).

The naive block-mass model assumes

    log_b(q) ~ C_{k-1},

so

    log_b(a) ~ C_{k-1} + D_k - 2*C_{k-1}
             = D_k - C_{k-1}.

This is the heuristic step. The block counts above are exact under the
smooth condition; the claim that a boundary convergent has this error
scale and denominator scale is still a CF argument, not yet a theorem.


## What The Existing d=4 Data Says

For base 10 and `k = 4`, compare the recorded mega-spikes from
`experiments/acm-flow/cf/SPIKE-HUNT.md`. The CF-scale
quantity is `log10(a)`, so the residual column below uses the recorded
`pq_log10`, not the integer digit count.

| n | observed digits | `log10(a)` | scout | `D_4-C_3` | `log10(a)` - refined |
|---|---:|---:|---:|---:|---:|
| 2 | 8268 | 8267.6479 | 8100.00 | 8277.75 | -10.1021 |
| 3 | 7342 | 7341.9542 | 7200.00 | 7358.00 | -16.0458 |
| 4 | 6187 | 6186.2497 | 6075.00 | 6208.31 | -22.0628 |
| 5 | 5266 | 5265.0456 | 5184.00 | 5297.76 | -32.7144 |
| 6 | 4560 | 4559.9542 | 4500.00 | 4598.75 | -38.7958 |
| 10 | 2908 | 2907.6474 | 2916.00 | 2979.99 | -72.3426 |

The refined block-mass formula is much better than the scout for
`n <= 6`, but it overpredicts `n = 10` and the residual is still
monotone. So the pre-run prediction was only half right: block mass
explains the scale, but not the drift.


## The Drift Is Denominator Inflation

The residual is almost exactly what the CF-scale formula predicts when
the actual preceding denominator is larger than the naive block model.

Let

    delta_n = log_10(q_before) - C_3(n,10).

Then

    observed - (D_4-C_3) ~ -2*delta_n.

Using the rounded `log_10 q` values recorded in `SPIKE-HUNT.md`:

| n | `C_3` | recorded `log10 q` | `delta_n` | `-2 delta_n` | `log10(a)` - refined |
|---|---:|---:|---:|---:|---:|
| 2 | 722.25 | 727.7 | 5.45 | -10.90 | -10.1021 |
| 3 | 642.00 | 650.0 | 8.00 | -16.00 | -16.0458 |
| 4 | 541.69 | 553.4 | 11.71 | -23.43 | -22.0628 |
| 5 | 462.24 | 479.0 | 16.76 | -33.52 | -32.7144 |
| 6 | 401.25 | 421.0 | 19.75 | -39.50 | -38.7958 |
| 10 | 260.01 | 296.7 | 36.69 | -73.38 | -72.3426 |

This is the main Phase 3.1 result so far. The mega-spike is not just
`D_k - C_{k-1}`. It is better written as

    spike_digits(k,n)
      ~ T_k(n) - 2*L_{k-1}(n),

where `L_{k-1}(n)` is the actual logarithmic denominator scale of the
preceding convergent. The block-only formula is the special case
`L_{k-1} = C_{k-1}`.

So the residual is not a new local `Q_n` coordinate. It is upstream CF
history entering through `q`.


## Consequence For The Two-Stream Hypothesis

This supports the two-stream picture in `MEGA-SPIKE.md`.

The spike subsequence has a simple block formula once the actual
denominator scale is supplied:

    spike size = boundary digit depth - 2*previous denominator depth.

The remaining problem is to understand the previous denominator depth.
That belongs to the off-spike/background CF process and earlier
boundary spikes. In other words, the spike law is simple, but it is
coupled to the background through `q`.

This is why separating the spike stream may reveal low-complexity
behaviour in both pieces while the merged CF sequence remains
non-rational-looking.


## What Is Proved, What Is Heuristic

Exact:

- smooth-block n-prime counts from `BLOCK-UNIFORMITY`;
- cumulative digit-mass formulas `C_{k-1}` and `D_k`;
- algebraic identity turning `D_k - C_{k-1}` into the displayed closed
  form.

Empirical but strongly checked:

- d-tier identification via `2 log10(q_before) + log10(a)` landing on
  block boundaries;
- residual `observed - (D_4-C_3)` matching `-2(log q - C_3)`.

Still heuristic:

- that the relevant boundary truncation always produces a convergent
  with error scale `b^(-T_k)`;
- that the off-spike/background denominator process has a finite
  recurrence or finite-state description;
- that off-boundary partial quotients stay controlled enough for any
  irrationality-measure claim.


## Next Attack

Phase 3.1 should continue in two branches.

1. **Spike branch.** Derive and test

       spike_digits(k,n) ~ T_k(n) - 2*L_{k-1}(n)

   at the next boundary, not merely with the d=4 table.

2. **Background branch.** Remove boundary spikes and model the
   off-spike denominator growth `L_k`. If `L_k - C_k` follows a finite
   recurrence, the mega-spike residual is no longer mysterious.

Hardy Mode 3 supplies exact large-d block counts. Hardy Mode 2 supplies
exact digit-position neighborhoods around block joins. The CF compute
still has the precision wall, but the block and position side no
longer do.

The d=4 comparison table is reproducible with
`experiments/acm-flow/cf/spike_drift_table.py`.
