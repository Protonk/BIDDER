# Off-spike denominator inflation: δ_k(n) = (n−1)k + offset(n)

The spike formula reads

    log_b(a_{i_k}) = T_k(actual) − 2 L_{k−1} + log_b(b/(b − 1)) − O(b^{−k})

with `L_{k−1} = log_b(q_{i_k − 1})` the previous convergent's log
denominator. The substrate-naive prediction is `L_{k−1} ≈ C_{k−1}`,
the cumulative digit count through the d=(k−1) block. The deviation

    δ_k(n) := L_{k−1}(n) − C_{k−1}(n)

— the off-spike denominator inflation — is the part of the previous
denominator that the substrate-cumulative count doesn't deliver.
Its leading-order decomposition is

    δ_k(n) = (n − 1) k + offset(n) − O(b^{−k}).


## The slope `(n − 1)`

For each panel `n`, the per-`k` step of `δ_k`:

| n | δ_2 | δ_3 | δ_4 | step 2→3 | step 3→4 | asymptotic slope |
|---|---|---|---|---|---|---|
| 2 | +2.690 | +3.698 | +4.699 | +1.008 | +1.001 | n − 1 = 1 |
| 3 | +4.041 | +6.045 | +8.046 | +2.004 | +2.000 | n − 1 = 2 |
| 4 | +6.695 | +9.096 | +12.398 | +2.402 | +3.301 | (transient at this k) |
| 5 | +8.996 | +12.000 | +16.000 | +3.004 | +4.000 | n − 1 = 4 at k≥3 |
| 6 | +10.041 | +14.045 | +19.046 | +4.004 | +5.000 | n − 1 = 5 at k≥3 |
| 10 | +3.991 | +26.398 | +35.699 | +22.406 | +9.301 | (transient at this k) |

For `n ∈ {2, 3, 5, 6}` the per-`k` step settles into `(n − 1)`
exactly, within `b^{−k}`-decaying corrections. For `n = 4` and
`n = 10` the linear regime hasn't been reached at `k = 4` (small
`d = 1` atom count makes the transient last longer).


## Why the slope is `(n − 1)`

For every `n ≥ 2`, the cofactors of n-primes are the integers not
divisible by `n` enumerated by Hardy's bijection: in any window of
`n` consecutive integers exactly `n − 1` are cofactors, so the
cofactor density is `(n − 1)/n`. The accumulated log-denominator
growth per `k`-step picks up `(n − 1)` units of `log b` from this
cofactor structure.

This is suggestive, not a proof. The cycle-disruption argument that
links cofactor structure to convergent denominator growth lives in
`MECHANISTIC-DERIVATION.md`.


## The per-`n` offset

Subtracting the linear part `(n − 1) · k` reveals the per-`n`
offset:

| n | δ_4 − (n − 1)·4 | identification |
|---|---|---|
| 2 | +0.6989 | log_{10}(5) ≈ 0.6990 |
| 3 | +0.0457 | log_{10}(10/9) ≈ 0.0458 |
| 4 | +0.3979 | (transient) |
| 5 | +0.0000 | 0 |
| 6 | −0.9543 | −1 + log_{10}(10/9) |
| 10 | −0.3011 | (transient) |

For `n ∈ {2, 3, 5, 6}`, the offset has a clean closed form. The
offsets for prime powers, composites, and larger primes are the
subject of `EXTENDED-PANEL-RESULT.md`; the family classification
by `ord(b, n)` in the coprime prime subcase is in
`PRIMITIVE-ROOT-FINDING.md`.


## Closed-form spike size in the asymptotic regime

Substituting `L_{k−1} = C_{k−1} + (n − 1) k + offset(n) − O(b^{−k})`:

    log_b(a_{i_k}) = D_k(actual)
                  − C_{k−1}(actual)
                  − 2(n − 1) k
                  − 2 · offset(n)
                  + log_b(b / (b − 1))
                  − O(b^{−k}).

Verification at `(n, k) = (2, 4)`, `b = 10`:

    9000 − 723 − 8 − 2 · log_{10}(5) + log_{10}(10/9)
    = 8267.65 (predicted)
    = 8267.6479 (observed)  ✓

The formula uses no CF data once `offset(n)` is identified — it
predicts the spike from substrate quantities alone (modulo the
per-`n` constant).


## What this leaves open

The slope `(n − 1)` is closed asymptotically; the offset is
identified per-`n` for primes with `ord(b, n) ∈ {1, 2, n−1}`
(`PRIMITIVE-ROOT-FINDING.md`); the residual lives in:

1. **`offset(n)` for intermediate `ord`.** Primes with `ord(b, n)`
   not in `{1, 2, n−1}` (e.g. `n ∈ {13, 23, 31}` at `b = 10`)
   deviate from Family A and Family B at `k = 4`. Either higher
   `k` resolves them or they are a third structural class.
2. **The transient regime at small `k` for `n ∈ {4, 10}`.** Probably
   driven by the small number of `d = 1` atoms; the linear-asymptote
   story holds at higher `k`.
3. **The `O(b^{−k})` tail.** Per-`n` coefficient; same family as
   the spike formula's residual in `MULTI-K-RESULT.md`.

The off-spike denominator process between consecutive boundary
spikes is the load-bearing unmodelled object. The decomposition
above describes only the boundary endpoints; intermediate
convergents are not modelled. This is the same gap that gates
step 3 of `MECHANISTIC-DERIVATION.md` and the "spikes dominate"
premise in `MU-CONDITIONAL.md`.


## Files

- `offspike_inflation.py` — the analysis script.
- `offspike_inflation.csv` — per-(n, k) data.
- `offspike_inflation_summary.txt` — text tables.
