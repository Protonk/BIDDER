# Within-row autocorrelation decomposition

## Statement

For prime `n = p` and fixed height `h`, the lag-`L` autocorrelation
along the `k`-axis is

    A(p, h, L; K) := (1 / (K - L))
                     Σ_{k=1}^{K - L} Q_p(p^h k) · Q_p(p^h (k + L)).

Define the class signature of `k = p^t k'` with `gcd(k', p) = 1` as

    cls(k) := (t, tau_sig(k')),

with `tau_sig(k')` the sorted-descending exponent tuple of `k'` (see
`OBJECTS.md`). By the master expansion's prime-`n` specialisation
(`MASTER-EXPANSION.md` C3),

    Q_p(p^h k) = q_value_by_class((1,), h + t, tau_sig(k')).

Then

    A(p, h, L; K) = Σ_{c1, c2} D(c1, c2; p, L, K) · V(c1; h) · V(c2; h),

with

    D(c1, c2) := #{k ∈ [1, K - L] : cls(k) = c1, cls(k + L) = c2} / (K - L)
    V((t, sig); h) := q_value_by_class((1,), h + t, sig)           ∈ ℚ.

Scope: prime `n` only. The non-prime analog requires the full
overlap tuple and a different evaluator (the prime-row formula
`q_value_by_class((1,), h + t, tau_sig)` is wrong for non-prime
`n`); see `PROPOSED-CLOSED-FORMS.md` Proposal 7.

## Proof

Partition the sum range `k ∈ [1, K - L]` by the joint class
`(cls(k), cls(k + L))`. Within one cell of this partition, both Q
values are determined by their classes and `h` via
`q_value_by_class`, so the inner average factors:

    Σ_{k: (cls(k), cls(k+L)) = (c1, c2)} Q(k) Q(k+L)
        = (count) · V(c1; h) · V(c2; h).

Dividing by `K - L` and summing over class pairs gives the
decomposition. Finiteness: only `k` whose class pair has nonzero
count contributes, and there are finitely many such pairs at finite
`K`. ∎

## BQN

```bqn
Cls ← {(𝕨 NuP 𝕩) ‿ (𝕨 CoprimePart 𝕩)}
```

`NuP`, `CoprimePart` are in `OBJECTS.md`. The full
prime-factorisation needed for `tau_sig` is in Python:
`predict_q.tau_sig_of`.

## Anchor

A4, A5 in `test_anchors.py` underwrite the algebraic factor `V` (the
master expansion is exact via `q_value_by_class`).

`test_within_row_lattice.py`: 264 spot-checks of `q_general` against
`q_lattice_4000_h{5,6,7,8}.npy` (4 heights × 6 primes × 11 sample
`k`-values); 24 autocorrelation profiles (4 heights × 6 primes)
agree between `predict_q` and the cached lattice files at `< 10^{-7}`
per lag.

`predict_correlation._self_check`: `direct_autocorr` and
`class_decomposition` agree to machine precision on a representative
panel.

## Empirical readout

`test_within_row_lattice.py` enumerates `(h, n) ∈ {5, 6, 7, 8} ×
{2, 3, 5, 7, 11, 13}` at `K = 4000` and reports the lag-`L`
autocorrelation profile for `L = 1..20`. Aggregated parity
statistics:

```
h = 5
    n   odd-L mean    even-L mean   gap          ratio (e/o)
    2   +3.12e-06     +1.76e-03     +1.75e-03    563
    3   +6.33e-04     +1.21e+00     +1.21e+00    1913
    5   +2.44e-01     +1.11e+01     +1.09e+01    46
    7   +4.95e-01     +2.18e+01     +2.13e+01    44
   11   +1.12e+00     +3.78e+01     +3.66e+01    34
   13   +1.46e+00     +4.11e+01     +3.96e+01    28

h = 6
    n   odd-L mean    even-L mean   gap          ratio
    2   +2.00e-06     +2.37e-06     +3.71e-07    1.19
    3   -7.26e-05     +2.06e-01     +2.06e-01    -2835
    5   +1.74e-02     +1.92e+00     +1.90e+00    110
    7   +2.80e-02     +3.54e+00     +3.51e+00    127
   11   +8.84e-02     +8.44e+00     +8.35e+00    96
   13   +1.15e-01     +9.09e+00     +8.98e+00    79

h = 7
    n   odd-L mean    even-L mean   gap          ratio
    2   +1.53e-06     +1.89e-06     +3.67e-07    1.24
    3   +1.46e-05     +1.10e-02     +1.10e-02    755
    5   +7.14e-05     +1.10e-01     +1.09e-01    1534
    7   +1.37e-03     +1.68e-01     +1.67e-01    123
   11   +1.21e-03     +9.33e-01     +9.32e-01    772
   13   +1.12e-03     +1.02e+00     +1.02e+00    914

h = 8
    n   odd-L mean    even-L mean   gap          ratio
    2   +1.21e-06     +1.55e-06     +3.44e-07    1.29
    3   -1.91e-06     +1.17e-06     +3.08e-06    -0.61
    5   -6.75e-06     +6.27e-07     +7.38e-06    -0.09
    7   -4.38e-05     +2.49e-03     +2.53e-03    -57
   11   -1.60e-05     +5.01e-02     +5.01e-02    -3137
   13    0.00e+00     +5.01e-02     +5.01e-02    inf
```
