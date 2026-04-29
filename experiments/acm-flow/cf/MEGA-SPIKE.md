# Boundary-spike size for ACM-Champernowne reals

The base-`b` ACM-Champernowne real for `n ≥ 2` is

    x = C_b(n) = 0 . p_1(n) p_2(n) p_3(n) …

where `p_K(n) = n · c_K`, `c_K = q_K n + r_K + 1`,
`(q_K, r_K) = divmod(K-1, n-1)`. The K-th n-prime in ascending
order is the K-th positive integer not divisible by `n`, scaled by
`n`. For prime `n`, this is the same as scaling the K-th positive
integer coprime to `n`.

The continued-fraction expansion of `x` carries large partial
quotients near each radix-block boundary. This document derives
the closed form for the largest of these, the d=k boundary spike,
and locates the residual content in the off-spike denominator
process.


## The master statement

For `n ≥ 2`, base `b`, and actual atom counts through the d=k
radix block, the d=k boundary spike satisfies

    log_b(a_{i_k}) = T_k − 2 L_{k−1} + log_b(b/(b−1)) − O(b^{−k}),

where:

- `a_{i_k}` is the partial quotient at the boundary index `i_k`;
- `T_k = Σ_{d=1}^{k} d · N_d^{actual}(n,b)` is the cumulative
  digit count through the d=k atom block;
- `L_{k−1} := log_b(q_{i_k − 1})` is the log denominator of the
  convergent immediately before the boundary;
- `log_b(b/(b−1))` is the universal boundary-truncation factor.

The two derivable terms (`T_k` and the truncation factor) come from
substrate counting and a single CF identity. In any smooth d-block
(`n² | b^{d−1}`), `core/BLOCK-UNIFORMITY.md` gives
`N_d(n,b) = (b−1) b^{d−1} (n−1)/n²`; otherwise `T_k` is computed by
the exact atom count. The third term `L_{k−1}` is what the off-spike
CF process delivers up to the boundary; its leading-order
decomposition is empirical and documented in `OFFSPIKE-RESULT.md`.


## Block algebra

`core/BLOCK-UNIFORMITY.md` gives the smooth-block n-prime count
for any d-block satisfying `n² | b^{d−1}`:

    N_d(n, b) = (b − 1) b^{d−1} (n − 1) / n²

Using that smooth-block count, the d=k atom block contributes

    D_k(n, b) = k · N_k(n, b)

digits to the concatenated real, and the preceding blocks contribute

    C_{k−1}(n, b) = (b − 1)(n − 1)/n² · Σ_{d=1}^{k−1} d · b^{d−1}.

Using

    Σ_{d=1}^{k−1} d · b^{d−1} = ((k − 1) b^k − k b^{k−1} + 1) / (b − 1)²,

the closed-form digit-mass increment is

    S_k(n, b) := D_k − C_{k−1}
              = (n − 1)/n² · (b^{k−1} (k(b − 2) + b/(b − 1)) − 1/(b − 1)).

For base 10, `S_k(n, 10) = (n − 1)/n² · (10^{k−1}(8k + 10/9) − 1/9)`.
At `k = 4` this is `33 111 · (n − 1)/n²`.

`S_k` is the smooth substrate-transparent piece. Everything in it —
the density `(n−1)/n²`, the cumulative digit count, the
`(b − 2)/(b − 1)` prefactor structure — is closed-form in
`(n, b, k)`. The actual-count version of `T_k` is used when the
smooth condition fails at small blocks. The cross-base panel in
`CROSS-BASE-RESULT.md` confirms the prefactor structure across
`b ∈ {3, 4, 6, 8, 10, 12}` to within the sub-leading correction.


## The CF correction

Let `p_i / q_i` be the i-th convergent of `x`. The standard CF
identity is

    | x − p_i / q_i | = 1 / (q_i · (a_{i+1} q_i + q_{i−1})).

Taking `log_b` and dropping the `log_b(1 + α / a_{i+1})` term where
`α = q_{i−1}/q_i ∈ (0, 1)`, valid for large `a_{i+1}`:

    log_b(a_{i+1}) ≈ L_{match}(i) − 2 log_b(q_i),

with `L_{match}(i) := −log_b |x − p_i / q_i|` the convergent's
log-matching length to `x`.

For the convergent `p_{i_k − 1} / q_{i_k − 1}` immediately before
the d=k boundary, the matching length is

    L_{match}(i_k − 1) = T_k + log_b(b/(b − 1)).

The `log_b(b/(b − 1))` says the convergent matches `T_k` digits
plus a fractional digit's worth of agreement at position `T_k + 1`:
the residual `x − p/q` past `T_k` is approximately `(b−1)/b · b^{−T_k}`,
not `b^{−T_k}` exactly. The factor `(b−1)/b` reflects that the
digits past `T_k` start with the leading digit of the smallest
(k+1)-digit n-prime, which is bounded below by 1 and averages out
to that ratio over the block.

Substituting and writing `L_{k−1} := log_b(q_{i_k − 1})`:

    log_b(a_{i_k}) ≈ T_k − 2 L_{k−1} + log_b(b/(b − 1)).


## The substrate-naive prediction and where it misses

If one assumed `L_{k−1} ≈ C_{k−1}` (the convergent denominator
matches the cumulative substrate digit count), the formula collapses
to

    log_b(a_{i_k}) ≈ T_k − 2 C_{k−1} + log_b(b/(b−1))
                  = D_k − C_{k−1} + log_b(b/(b−1))
                  = S_k + log_b(b/(b−1)).

This is the "substrate-naive" prediction. It is correct in scaling
but misses by a per-`n` amount that grows linearly in `k`:

    L_{k−1} = C_{k−1} + δ_k(n),
    δ_k(n) = (n − 1) k + offset(n) − O(b^{−k}).

The difference `−2 δ_k(n) = −2(n−1)k − 2·offset(n) + O(b^{−k})`
appears as a per-`n` correction that the substrate-naive prediction
misses. The decomposition `δ_k(n) = (n−1) k + offset(n)` is the
content of `OFFSPIKE-RESULT.md`. The slope `(n − 1)` reaches its
asymptote uniformly across the tested panel; the per-`n` constant
`offset(n)` is classified by `ord(b, n)` in
`PRIMITIVE-ROOT-FINDING.md`.

The fully closed-form spike size in the asymptotic regime is

    log_b(a_{i_k}) = D_k − C_{k−1} − 2(n − 1) k − 2 · offset(n)
                   + log_b(b/(b−1)) − O(b^{−k}).

Verification at `(n, k) = (2, 4)`, `b = 10`: predicted 8267.65,
observed 8267.6479. The other low-`n` k=4 cases match similarly;
see `EXTENDED-PANEL-RESULT.md` for the full panel.


## What is exact, what is heuristic

Exact:

- the actual atom counts `N_d^{actual}(n, b)` and cumulative digit
  count `T_k`;
- the smooth-block n-prime count
  `N_d(n, b) = (b−1)b^{d−1}(n−1)/n²` whenever `n² | b^{d−1}`;
- the algebraic identity giving `S_k = D_k − C_{k−1}` in closed form
  for the smooth-count model.

Standard CF identity (textbook):

- `|x − p/q| = 1/(q · (a q + q_prev))` and its log form.

Heuristic, supported by empirics:

- the boundary convergent achieves matching length
  `L_{match} = T_k + log_b(b/(b−1))`. The `+ log_b(b/(b−1))` part
  is the leading-digit averaging argument, which gives the right
  asymptotic value but leaves an `O(b^{−k})` residual;
- the boundary convergent's denominator scale is `L_{k−1}`, not
  `T_k/2`. The convergent is *better than Khinchin-typical* because
  of substrate structure; see `MECHANISTIC-DERIVATION.md` for the
  partial proof and the open analytic step.

Confirmed empirically across the panel:

- multi-`k` consistency at `b = 10`, `k ∈ {2, 3, 4, 5}`, with
  residuals decaying as `b^{−k}` (`MULTI-K-RESULT.md`,
  `D5-RESULT.md`);
- cross-base consistency at `b ∈ {3, 4, 6, 8, 10, 12}` with the
  `(b − 2)/(b − 1)` prefactor structure intact (`CROSS-BASE-RESULT.md`);
- `δ_k(n)` slope `(n − 1)` asymptotically across the tested panel
  (`OFFSPIKE-RESULT.md`, `EXTENDED-PANEL-RESULT.md`);
- `offset(n)` family classification by `ord(b, n)` for
  `ord ∈ {1, 2, n−1}` (`PRIMITIVE-ROOT-FINDING.md`).


## Where the residual lives

`L_{k−1}` is the load-bearing unmodelled scalar. The closed-form
piece of it (`C_{k−1} + (n − 1) k + offset(n)`) covers the leading
order at boundary indices for primes where `ord(b, n) ∈ {1, 2, n−1}`.
What remains:

- **Off-spike intermediate convergents.** Between consecutive
  boundary spikes at `i_{k−1}` and `i_k`, the CF runs through many
  intermediate convergents whose denominators are not modelled.
  The decomposition `δ_k(n) = (n−1)k + offset(n)` describes only
  the boundary endpoints.
- **Intermediate-`ord` primes.** For `n ∈ {13, 23, 31}` with
  `ord(b, n) ∉ {1, 2, n−1}`, the offset at `k = 4` doesn't fit
  Family A or B. Either higher `k` resolves them into a third
  family or they remain transient.
- **The mechanism for `offset(n)` itself.** The slope `(n − 1)`
  has a heuristic cofactor-cycle argument; the offset has a
  divisibility argument that works for `ord = 1` and fails for
  `ord = 2` (`MECHANISTIC-DERIVATION.md` §"Empirical check of the
  divisibility mechanism"). The right replacement for ord=2 is open.
- **The `O(b^{−k})` tail.** Per-`n` coefficient `β(n)` for the
  geometric decay of the residual; some primes share, some don't
  (`MULTI-K-RESULT.md`).

The first item — characterising the off-spike denominator process
— is the load-bearing open problem. It gates step 3 of
`MECHANISTIC-DERIVATION.md` and the "spikes dominate" premise
in `MU-CONDITIONAL.md` simultaneously; closing one closes the other.


## Consequences

The conditional irrationality measure of `C_b(n)` follows from the
spike formula by the standard CF identity, under the assumption
that boundary spikes dominate the approximation budget:

    μ(C_b(n)) = 2 + (b − 1)(b − 2) / b,    independent of n.

Derivation and load-bearing premise in `MU-CONDITIONAL.md`. For
`b = 10` the conditional value is `9.2`, comparable to but distinct
from Mahler's classical Champernowne `μ = 10`.

The structural reading of the spike formula — what's grand,
mundane, beautiful, and contingent in it — is in
`arguments/MEGA-SPIKE-FOUR-WAYS.md`.


## Files

- `spike_drift_table.py` — d = 4 reproducibility script for the
  spike formula's match against the CF data.
- `spike_drift_table.csv`, `spike_drift_summary.txt` — output.
- `spike_drift_multi_k.py` (and CSV / summary) — multi-k panel
  consumed by `MULTI-K-RESULT.md`.
- `offspike_inflation.py` (and CSV / summary) — δ_k(n) decomposition
  consumed by `OFFSPIKE-RESULT.md`.
- `spike_drift_extended.py` (and CSV / summary) — extended `n`
  panel consumed by `EXTENDED-PANEL-RESULT.md` and
  `PRIMITIVE-ROOT-FINDING.md`.
- `cf_spikes.py`, `cf_spikes_extended.py`, `cf_spikes_d5.py` (and
  outputs) — CF panel runners at b = 10 d ∈ {2,3,4} / cross-base /
  d = 5.
