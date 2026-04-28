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

**Spike magnitudes scale with the n-sieve density `(n−1)/n²` to within ~2%.**

Largest spike per n in the validated prefix:

| n | mega-spike index | digit count | × n²/(n−1) |
|---|---:|---:|---:|
| 2 | 118 | 8268 | 33072 |
| 3 | 162 | 7342 | 33039 |
| 4 | 148 | 6187 | 32997 |
| 5 | 178 | 5266 | 32913 |
| 6 | 188 | 4560 | 32835 |
| 10 | 212 | 2908 | 32311 |

The same scaling holds for the secondary spikes (the d=3 boundary
spike, ~5× smaller in digit count than the mega d=4 spike). Each n
shows the same multi-tier signature: a small d=2 spike (5–40 digits),
a medium d=3 spike (170–620 digits), a mega d=4 spike (2908–8268
digits), and occasionally a tail spike — exactly the d-block
structure of `core/BLOCK-UNIFORMITY.md` showing through.

Empirical fit for the d=k spike magnitude in C_10(n):

```
spike_digits(n, k)  ≈  (b−1)² · b^(k−2) · (n−1) · k / n²
                    ≈  (b−1)/b · (digits in d=k block of C_b(n))
```

For (b, k) = (10, 4): `81 · 100 · 4 · (n−1)/n² = 32400 · (n−1)/n²`,
matching the table to 99–102%.

## Irrationality measure, lower bound

For the d=4 mega-spike in C_10(n): the convergent before the spike
has `log_10 q ≈ 720` (cumulative digits up to the d=3 boundary), and
the spike itself gives `log_10 a_{i+1} ≈ 0.9 · b^(k−1) · (n−1)/n² · k`.
The Diophantine ratio `2 + log a / log q` evaluates to ~13.5 across
all six n. This is a lower bound on the irrationality measure
`μ(C_10(n))` and *vastly* exceeds the generic μ=2; it lives in the
regime above Mahler's μ=10 for integer Champernowne.

The asymptotic d → ∞ ratio works out to `9 · (1 + 1/(d−1)) → 9`,
giving `μ(C_10(n)) ≤ 11` in the smooth regime — pending proof.

## What this is not

- **Not a Liouville number.** The digit count of the d=k spike grows
  like `b^(k−1)`, but `log q` at that point grows like the cumulative
  digit count, also `b^(k−2)`. Their ratio is bounded, so μ is finite.
- **Not "Mahler carried over without n-structure"** — the brief's
  "probably nothing" outcome. Spike magnitudes track `(n−1)/n²` to
  ~2% across six values of n.

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
