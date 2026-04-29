# Spike hunt — CF spectrum of n-Champernowne reals

The overall search this directory implements. Brief 2 of
`EXPERIMENTAL.md`, with the additional structure that emerged from
the first run.


## Question

Given `C_b(n)` — the real obtained by concatenating the n-primes
of monoid `nZ⁺` after a radix point in base `b`:

    C_b(n) = 0 . p_1 p_2 p_3 …    (in base b, p_k the k-th n-prime)

— what does its continued-fraction expansion look like, and in
particular, where do the unusually large partial quotients sit?

The brief frames three outcomes:

- **Probably nothing.** Spikes uniformly distributed, no n-correlated
  structure. Then C_b(n) is just Mahler's argument carried over to a
  sparser sequence and the experiment is a non-result.
- **Reach goal.** An explicit irrationality measure `μ(C_b(n))` as a
  function of n, with the proof tracking sieve boundaries as the
  spike source. A real, if small, contribution to Diophantine
  analysis of explicit reals.
- The realistic middle: empirical evidence that spike loci are
  n-correlated, but without a closed-form proof.

After one afternoon of computation we are firmly in the middle, with
a clean enough scaling law to make the reach goal look reachable.


## Object

`C_b(n)` is the radix-point concatenation of the n-prime stream of
the multiplicative monoid `nZ⁺`. The n-primes are the multiples of
n that are not multiples of n² (`core/ACM-CHAMPERNOWNE.md`).

Two structural facts we use:

- `core/BLOCK-UNIFORMITY.md` — the n-prime count in the d-th
  digit-class block `[b^(d−1), b^d − 1]` is exactly
  `(b−1) · b^(d−1) · (n−1)/n²` under the smooth condition
  `n² | b^(d−1)`, with a universal `≤ 2` spread bound otherwise.
- `core/HARDY-SIDESTEP.md` — termwise random access to the K-th
  n-prime in `polylog(K + n)` bit operations. Not used in the first
  pass but the natural way to extend to larger K.


## Method

Single Python script, three controls: `MAX_PQ`, `PREC_BITS_LO/HI`,
`K_PRIMES`.

1. Build the exact digit string: take `K_PRIMES` n-primes from
   `core/acm_core.py:acm_n_primes`, concatenate decimal forms.
   Avoid `acm_champernowne_real` — it truncates at IEEE 754 double
   precision and is wrong for this purpose.
2. Parse to `mpmath.mpf` at `PREC_BITS_LO` bits, then again at
   `PREC_BITS_HI = 2 × LO`. CF expand both via the reciprocal-and-floor
   loop.
3. The longest prefix on which the two CFs agree is the
   precision-validated CF; PQs past that are noise from precision
   exhaustion.
4. Per n, record every `a_i > 10⁴` with its CF index, decimal-digit
   count, log₁₀ value, and 24-digit head. Plot `log₁₀ a_i` versus i.

Validated against Mahler's classical Champernowne (`MAHLER-CHECK.md`)
on every invocation.


## What we found, n ∈ {2, 3, 4, 5, 6, 10}

**Spike magnitudes scale as `(n−1)/n²`.** The largest spike per n,
multiplied by `n²/(n−1)`, is constant to within ~2%:

| n | mega-spike index | digit count | × n²/(n−1) |
|---|---:|---:|---:|
| 2 | 118 | 8268 | 33072 |
| 3 | 162 | 7342 | 33039 |
| 4 | 148 | 6187 | 32997 |
| 5 | 178 | 5266 | 32913 |
| 6 | 188 | 4560 | 32835 |
| 10 | 212 | 2908 | 32311 |

**The CF spectrum has a tiered structure** that mirrors the digit
classes of `C_b(n)`. Each n shows the same shape:

- a small d=2 spike (5–40 digits)
- a medium d=3 spike (170–620 digits)
- a mega d=4 spike (~3 000–8 300 digits)
- sometimes a d=4-tail spike at later index

The CSV in `cf_spikes.csv` records all spikes above `10⁴`; the d-class
identification is read off from the digit-count ratios (~13× between
successive tiers, matching `b^(d) / b^(d−1) · d / (d−1)`).

**Tier identification, confirmed.** For each spike `a_i`, the
identity `2 log₁₀ q_{i−1} + log₁₀ a_i` lands on the cumulative
digit count through the corresponding d-block boundary. For n=2:
i=10 → 48, i=32 → 723, i=118 → 9 723 — exactly the cumulative
ends of d=2, d=3, d=4 in C_10(2). The same check holds for the
d=4 mega-spike across all sampled n. So d-tier identification is
not ratio-matching; it is independently confirmed by the CF error
scale.

**Empirical fit.** A natural boundary heuristic for the d=k spike:

    spike_digits(n, k) ≈ D_k(n) − C_{k−1}(n)

where `D_k(n) = (b−1)·b^(k−1)·(n−1)/n²·k` is the digit count of
the d=k block of `C_b(n)` under the smooth condition, and
`C_{k−1}(n)` is the cumulative digit count through d=k−1. In
base 10 this gives the closed form

    spike_digits(n, k) ≈ (n−1)/n² · 10^(k−1) · (8k + 10/9).

For (b, k) = (10, 4) the prediction is `33 111 · (n−1)/n²`, which
matches the observed values to 97–100% — n=10 the outlier at 97.6%,
the others within 0.5%. The prefactor on `D_k` tends to 8/9 ≈ 0.889
asymptotically, not 9/10. Closed-form derivation is pending.

The scaled column `obs × n²/(n−1)` is **not** constant — it drifts
monotonically from 33 070 (n=2) to 32 311 (n=10), about 2.3%. The
`(n−1)/n²` law is therefore approximate at finite k. Whether the
drift is a finite-k correction, a smoothness-of-`n²|b^(d−1)`
correction, an n=10-style trailing-zero artifact, or something
else is open.

**Diophantine consequence.** At the d=4 mega-spike, the preceding
convergent's `log₁₀ q` varies substantially with n — smaller n
gives larger upstream spikes contributing more to `log q`. Per n
the finite convergent Diophantine exponent
`2 + log a_{i+1} / log q_i` at the d=4 spike is:

| n | log₁₀ q | log₁₀ a | 2 + log a / log q |
|---|---:|---:|---:|
| 2 | 727.7 | 8 267.6 | 13.36 |
| 3 | 650.0 | 7 342.0 | 13.29 |
| 4 | 553.4 | 6 187.0 | 13.18 |
| 5 | 479.0 | 5 266.0 | 12.99 |
| 6 | 421.0 | 4 560.0 | 12.83 |
|10 | 296.7 | 2 908.0 | 11.80 |

These are **finite convergent exponents**, not lower bounds on the
irrationality measure `μ`. `μ` is a limsup over infinitely many
convergents; one spike's exponent neither lower- nor upper-bounds
it.

Under the block-growth heuristic, the analogous ratio at the d=k
boundary is `(72k + 10)/(9k − 10) → 8` as k → ∞, so the asymptotic
boundary exponent is `2 + 8 = 10` — coincidentally Mahler's μ for
integer Champernowne. *If* off-boundary PQs stay Khinchin-typical,
the limsup is realised along the boundary-spike sequence and the
heuristic gives `μ(C_10(n)) = 10`, independent of n. Neither
boundary-spike growth nor off-boundary control is proven; both
inputs are needed for any rigorous claim about μ.

**Liouville.** Under the block-growth heuristic, boundary-spike
exponents stay bounded — so heuristically C_10(n) is not Liouville.
Establishing this rigorously requires a uniform bound on a_i across
both boundary and off-boundary indices, which we do not have. The
empirical observation is consistent with non-Liouville; it is not
yet a proof.


## Pipeline shape

```
acm_n_primes(n, K)        →  list[int]                core/acm_core.py
   ↓
'.'.join(str)             →  str (decimal digits)     cf_spikes.py
   ↓
mpf('0.' + digits)        →  mpf (LO and HI prec)     mpmath
   ↓
floor / reciprocal loop   →  list[a_i]
   ↓
stable_prefix_len(LO, HI) →  validated cutoff
   ↓
filter a_i > 10⁴          →  spike rows
   ↓
plot + CSV + summary
```

Smoke test (`MAHLER-CHECK.md`) sits before the main loop. Mpmath +
matplotlib + numpy run inside `sage -python`; nothing else is
required.


## Files

| file | role |
|---|---|
| `cf_spikes.py` | the experiment — pipeline, smoke test, plotting |
| `MAHLER-CHECK.md` | what the smoke test certifies |
| `SPIKE-HUNT.md` | this document — the overall search |
| `README.md` | quick index of outputs |
| `cf_spikes_summary.txt` | per-n: validated PQs, spike count, max digits |
| `cf_spikes.csv` | every spike `a_i > 10⁴`, recorded as digit count |
| `cf_spikes_n{2,3,4,5,6,10}.png` | per-n stem plots of log₁₀ a_i vs i |


## Precision wall

Each spike of D digits costs D digits of precision in the CF loop.
That sets a hard ceiling on validated PQs:

| n | validated PQs |
|---|---:|
| 2 | 408 |
| 3 | 487 |
| 4 | 514 |
| 5 | 613 |
| 6 | 660 |
| 10 | 843 |

Smaller n means bigger spikes means earlier ceiling. The next
boundary (d=5 → d=6) would generate spikes ~10× the d=4 mega:
~80 000 digits for n=2, ~30 000 digits for n=10. To reach them
requires `PREC_BITS_LO ≈ 800 000` and `K_PRIMES ≈ 2·10⁵`. The
smooth-condition discipline of BLOCK-UNIFORMITY.md predicts that
the same `(n−1)/n²` scaling continues; verifying it is the obvious
next compute step.


## Where the search goes next

1. **Push to d=5 at higher precision.** `PREC_BITS_LO = 800 000`,
   `K_PRIMES = 2·10⁵`, run overnight per n. If d=5 spikes also scale
   as `(n−1)/n²`, that's a multi-tier check on the empirical formula.

2. **Closed-form derivation.** The Mahler argument for integer
   Champernowne exploits the fact that within a d-block the integers
   appear in arithmetic-progression order. The n-prime block is the
   integer block sieved by the divisibility-by-n filter; the AP
   structure survives modulo `n` (since n-primes in the d-block are
   `n · k` for `k ∈ [b^(d−1)/n, b^d/n)` with `n ∤ k`). Working out
   the periodic-extension rational and its denominator should drop
   out the `(n−1)/n²` factor. This is the route to the reach-goal
   irrationality-measure theorem.

3. **Other bases.** Same script at b=2 and b=12 should test whether
   the `(b−1)/b` prefactor in the empirical fit is the right form.

4. **Non-smooth n correction.** For n ∈ {3, 6} in base 10, smoothness
   never holds; the BLOCK-UNIFORMITY spread bound says block sizes
   differ from the smooth formula by ≤ 2 per leading digit, which
   should generate sub-percent deviations in spike magnitude. Worth
   checking against the data once the asymptotic constant is fixed.

5. **n=10's special structure.** Every 10-prime ends in `0`. Spike
   magnitudes fit the d=4 prediction at 99.7% but the d=3 prediction
   at only 79%. The trailing-zero structure may produce a separate
   correction. Worth a separate brief.


## What this is not

- **Not Brief 1.** The Copeland-Erdős positioning of
  `core/BLOCK-UNIFORMITY.md` is a literature task, not a CF
  computation.
- **Not Brief 4.** The ACM-restricted multiplication table is a
  product-set problem in `experiments/acm/diagonal/`'s neighbourhood,
  unrelated to CF expansions.
- **Not a proof.** Everything above is empirical fit on six values of
  n, three (or four) spike tiers each. The closed form is the next
  step, not the current state.
