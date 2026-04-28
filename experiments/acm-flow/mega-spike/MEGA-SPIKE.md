# Mega-Spike Experiment

This tracks the Phase 3.1 attempt to explain the base-10 continued-
fraction mega-spikes of ACM-Champernowne numbers.

The target is not another fit. The target is a mechanism. We want to
know why the largest partial quotient near the k-digit block boundary
has approximately

    (b-1)^2 * b^(k-2) * (n-1) * k / n^2

digits, and why the scaled column in `SPIKE-HUNT.md` is close but not
constant.


## Prediction Before The Run

The mega-spike is driven primarily by deterministic radix-block
boundary geometry, with the n-dependence supplied by the exact n-prime
density `(n-1)/n^2`. It is not primarily driven by the sign pattern of
`Q_n`; `Q_n` supplies the local finite-rank algebra, but the spike is
what happens when that local stream is concatenated and then truncated
at a typographic block boundary.

For a smooth block, `n^2 | b^(k-1)`, the count of k-digit n-primes is

    N_k(n,b) = (b-1) * b^(k-1) * (n-1) / n^2.

The k-digit block contributes

    D_k(n,b) = k * N_k(n,b)

digits. The preceding blocks contribute

    C_{k-1}(n,b)
      = (n-1)/n^2 * (b-1) * sum_{d=1}^{k-1} d*b^(d-1).

My prediction is that the mega-spike digit count is controlled by the
new block mass minus the cumulative old mass:

    S_k(n,b) ~= D_k(n,b) - C_{k-1}(n,b).

Equivalently,

    S_k(n,b) ~=
      (n-1)/n^2 *
      ( b^(k-1) * (k*(b-2) + b/(b-1)) - 1/(b-1) ).

For base 10 this is

    S_k(n,10) ~=
      (n-1)/n^2 * ( 10^(k-1) * (8k + 10/9) - 1/9 ).

So the earlier scout

    (b-1)^2 * b^(k-2) * (n-1) * k / n^2

is expected to be a good finite-k leading term, but not the exact
shape. The observed monotone drift in the scaled column should shrink
after comparing against the refined `D_k - C_{k-1}` prediction. If it
does not, the missing term is not just block mass.


## Working Hypothesis: Two Low-Complexity Processes

There is a second reason the mega-spike matters.

The continued-fraction spectrum may be a merge of two separately
low-complexity event streams:

    off-spike background;
    boundary-spike subsequence.

The off-spike background, after removing boundary events, appears
close to rational or finite-recurrence behaviour in its own
coordinates. The spike subsequence also appears structured: its
locations and sizes are governed by block counts, cumulative digit
mass, and boundary placement. The full continued-fraction sequence
stops looking rational-like when these two event streams are
interleaved at the actual ACM-Champernowne boundary schedule.

This is not an additive decomposition of the real. Continued fractions
are too nonlinear for that. The defensible claim is weaker and more
testable:

    CF spectrum =
        structured background
      + structured boundary-event schedule
      + nonlinear interaction from interleaving.

If true, the source of apparent complexity is not that either component
is individually wild. It is the coupling between a low-complexity
background process and a low-complexity spike process at nontrivial
block positions.


## What I Think The Residual Is

After the refined boundary-mass correction, I expect the remaining
residual to be mostly entry-boundary arithmetic:

- trailing radix zeros for cases such as `n = 10`;
- non-smooth block effects when `n^2` does not divide `b^(k-1)`;
- lower-block contamination of the preceding convergent denominator;
- finite-precision CF validation limits.

I do **not** expect the residual to require a new local arithmetic
coordinate beyond finite-rank `Q_n`. If a new coordinate appears, it
should be a global concatenation coordinate: where the digit-position
oracle lands relative to entry boundaries, not another term in the
local Q expansion.


## Checks

1. **Derivation check.** Derive `D_k - C_{k-1}` cleanly from
   `core/BLOCK-UNIFORMITY.md`. Mark which steps are exact and which
   step turns into a CF-size heuristic.

2. **Hardy block-count check.** Use Hardy Mode 3 to verify the smooth
   block counts at large d for `n in {2,5,10}` without materializing
   the prefix.

3. **Digit-position check.** Use Hardy Mode 2 to sample exact stream
   neighborhoods around predicted block joins. This tests whether the
   spike is boundary geometry in the concatenated real, not only a
   count identity.

4. **Residual check.** Compare observed spike digit counts against
   both formulas:

       scout:   (b-1)^2 * b^(k-2) * (n-1) * k / n^2
       refined: D_k - C_{k-1}

   The refined residual should be smaller and less monotone in n.

5. **Destroyer check.** Once the boundary neighborhood is isolated,
   entry-shuffle should damage position-side spike structure while
   preserving per-entry algebraic invariants. If every destroyer leaves
   the spike intact, we are not looking at boundary order.

6. **Two-stream check.** Split the CF sequence into spike indices and
   off-spike indices. Test each subsequence for finite-recurrence or
   finite-state compressibility in its own natural coordinates, then
   test whether the true interleaving schedule is what destroys the
   rational-like behaviour.


## Normality Relevance

This is connected to normality, but it is not the normality proof.
Large continued-fraction partial quotients are compatible with normal
numbers; classical Champernowne is the warning example. The reason this
matters is that a normality proof for ACM-Champernowne has to separate
two facts that visually interfere:

    digit blocks are equidistributed after the n-prime sieve;
    block boundaries create extremely good rational approximants.

If the mega-spike is explained by exact block density plus boundary
truncation, then it is evidence for a controlled boundary artifact,
not evidence against normality. If the residual demands a new
arithmetic coordinate, then the normality route has to account for that
coordinate before any proof attempt is credible.


## Status

The prediction section above is the pre-run position. The first Phase
3.1 derivation pass is now recorded in
`experiments/acm-flow/mega-spike/brief2_q_derivation.md`.

That pass keeps the block-density prediction but sharpens the residual:
the refined `D_k - C_{k-1}` law explains the scale, while the monotone
drift is almost exactly the CF denominator correction

    -2 * (log_b(q_before) - C_{k-1}).

So the current working model is

    spike_digits(k,n) ~= T_k(n) - 2*L_{k-1}(n),

where `T_k` is the boundary digit depth and `L_{k-1}` is the actual
preceding denominator depth. The next problem is no longer the
`(n-1)/n^2` factor. It is the off-spike denominator process that
inflates `q_before`.


## Inputs

Inputs already pinned:

- `core/Q-FORMULAS.md`: local Q formula verified on the Phase 2 panel.
- `experiments/acm-flow/q_n_verify.py`: 24203 CSV rows, zero
  mismatches.
- `experiments/acm-flow/hardy_composite_q.py`: deep composite Q
  witnesses, zero mismatches.
- `core/BLOCK-UNIFORMITY.md`: exact smooth-block count and spread
  bound.
- `experiments/math/hardy/DEEP-TROUBLE-No-4.md`: deep access, block
  inverse, digit-position oracle, destroyer taxonomy.

Current artifact:

    experiments/acm-flow/mega-spike/brief2_q_derivation.md
    experiments/acm-flow/mega-spike/spike_drift_table.py
    experiments/acm-flow/mega-spike/spike_drift_table.csv
    experiments/acm-flow/mega-spike/spike_drift_summary.txt
