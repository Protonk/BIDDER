# Continued fractions of n-Champernowne reals

Brief 2 of `EXPERIMENTAL.md`. Where do unusually large partial quotients
of `C_10(n)` sit, and do their loci track the n-sieve rather than the
integer block boundaries that drive Mahler's argument for the classical
Champernowne constant?

`cf_spikes.py` builds `C_10(n) = 0.p_1 p_2 p_3 …` from the exact
n-prime list (via `core/acm_core.py:acm_n_primes`), runs a CF
expansion to up to 5000 partial quotients at two precisions
(80 000 and 160 000 bits), and keeps the longest agreeing prefix as
the precision-validated CF.

```
sage -python cf_spikes.py
```

Outputs:

| file | contents |
|---|---|
| `cf_spikes_n{n}.png` | log10(a_i) stem plot for each n |
| `cf_spikes.csv` | every (n, i, a_i) with a_i > 10^4, recorded as digit count + 24-char head |
| `cf_spikes_summary.txt` | per-n counts and validated-prefix length |

## Sanity check

The pipeline reproduces the OEIS A030167 partial quotients of the
classical Champernowne `0.123456789101112…`, including Mahler's famous
spike `a_4 = 149083`. See `smoke_test()`.

## Headline finding

**Spike magnitudes scale roughly as the n-sieve density `(n−1)/n²`,**
with a ~2.3% monotone drift across the six n we sampled.

Largest spike per n in the validated prefix:

| n | mega-spike index | digit count | × n²/(n−1) |
|---|---:|---:|---:|
| 2 | 118 | 8268 | 33072 |
| 3 | 162 | 7342 | 33039 |
| 4 | 148 | 6187 | 32997 |
| 5 | 178 | 5266 | 32913 |
| 6 | 188 | 4560 | 32835 |
| 10 | 212 | 2908 | 32311 |

The drift in the scaled column is real, not rounding noise. Whether
it's a finite-k correction, a smoothness-of-`n²|b^(d−1)` correction,
or n=10's trailing-zero structure leaking in, is open.

Each n shows the same tiered signature: a small d=2 spike (5–40
digits), a medium d=3 spike (170–620 digits), a mega d=4 spike
(2908–8268 digits), and sometimes a tail spike — the d-block
structure of `core/BLOCK-UNIFORMITY.md` projecting into the CF
spectrum. Identification of i=118 as the d=4 boundary (etc.) is
**confirmed** by `2 log₁₀ q_{i−1} + log₁₀ a_i` landing exactly on
the cumulative digit count through that boundary, not just by
ratio-matching.

Empirical fit for the d=k spike magnitude in C_10(n) (boundary
heuristic, base 10):

```
spike_digits(n, k)  ≈  D_k(n) − C_{k−1}(n)
                    =  (n−1)/n² · 10^(k−1) · (8k + 10/9)
```

For (b, k) = (10, 4) this is `33 111 · (n−1)/n²`, matching observed
values to 97–100% (n=10 the outlier at 97.6%). The asymptotic
prefactor on `D_k` is **8/9**, not 9/10. Closed-form derivation
pending.

## Diophantine consequence

For the d=4 mega-spike, the preceding convergent's `log₁₀ q`
varies with n (smaller n → larger upstream spikes → larger log q).
Per-n finite convergent Diophantine exponents
`2 + log a_{i+1} / log q_i`:

| n | log₁₀ q | log₁₀ a | exponent |
|---|---:|---:|---:|
| 2 | 727.7 | 8 267.6 | 13.36 |
| 3 | 650.0 | 7 342.0 | 13.29 |
| 4 | 553.4 | 6 187.0 | 13.18 |
| 5 | 479.0 | 5 266.0 | 12.99 |
| 6 | 421.0 | 4 560.0 | 12.83 |
|10 | 296.7 | 2 908.0 | 11.80 |

These are **finite convergent exponents**, not lower bounds on the
irrationality measure `μ` (which is a limsup over infinitely many
convergents; one spike doesn't bound it from below).

Under the block-growth heuristic the analogous ratio at the d=k
boundary is `(72k + 10)/(9k − 10) → 8` as `k → ∞`, giving an
asymptotic boundary exponent of `2 + 8 = 10` — coincidentally
matching Mahler's μ=10 for integer Champernowne. If off-boundary
PQs stay Khinchin-typical, this would yield `μ(C_10(n)) = 10`
independent of n. Neither boundary-spike growth nor off-boundary
control is proven.

## What this is not

- **Not Liouville (heuristically).** Under the block-growth model,
  boundary-spike exponents stay bounded as k → ∞. A rigorous
  non-Liouville claim needs uniform a_i bounds across both boundary
  and off-boundary indices, which we lack. The empirics are
  consistent with non-Liouville; not a proof.
- **Not "Mahler carried over without n-structure"** — the brief's
  "probably nothing" outcome. Spike magnitudes track `(n−1)/n²`
  with sieve-density-explained drift across six values of n.

## Precision wall

The validated prefix is short (408–843 PQs out of 5000 requested)
because each spike of D digits burns D digits of precision in the
mpmath CF loop. Smaller n means larger spikes means earlier prefix
truncation:

| n | validated PQs |
|---|---:|
| 2 | 408 |
| 3 | 487 |
| 4 | 514 |
| 5 | 613 |
| 6 | 660 |
| 10 | 843 |

The next spike past the d=4 mega is the d=5 boundary, predicted
size ≈ 10× the d=4 mega = ~80 000 digits for n=2. Detecting it
would need PREC_BITS_LO ≈ 800 000, a few minutes of mpmath work
per n, and K_PRIMES bumped to ~2·10⁵. Not done here.

## Open

- A clean derivation of the spike-magnitude formula
  `(b−1)² · b^(k−2) · (n−1) · k / n²` from BLOCK-UNIFORMITY.md's
  block-size lemma and a Mahler-style periodic-extension argument.
- Behaviour of n=10, which fits the d=4 prediction at 99.7% but
  the d=3 prediction at only 79%. n=10 is structurally special
  (every n-prime ends in `0`) and may have its own correction.
- Non-smooth n (n ∈ {3, 6} in base 10): the spread-≤2 correction
  from BLOCK-UNIFORMITY.md should generate sub-percent deviations
  in spike magnitude. Not extracted from the data here.
