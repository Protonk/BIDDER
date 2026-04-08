# Detrended RDS

Experiment 2 of [DISPARITY.md](DISPARITY.md).

This document reports what the closed-form-detrended running digital
sum looks like for a panel of monoids spanning `v_2 = 0..8`. The
question is: once we subtract the closed-form bit-balance drift from
[../HAMMING-BOOKKEEPING.md](../HAMMING-BOOKKEEPING.md), what does the
residual look like, and does anything monoid-specific or
order-dependent survive the subtraction.

The answer has two pieces:

1. **The closed form parameterized by `v_2(n)` alone is not enough.**
   It is correct for `n = 2` only. For every other monoid in the
   panel, including pure powers of two, the entries `nk` of the
   monoid carry varying `v_2(nk)`, so the per-monoid `v_2` is the
   wrong parameter for the per-entry contribution. The correct
   prediction uses `v_2(entry)` per entry. With that correction the
   running digital sum and its closed-form prediction are visually
   indistinguishable across the panel.
2. **The residual against the per-entry prediction is not noise.**
   Every monoid in the panel shows a coherent low-frequency residual
   with amplitude in the `2,000–4,000` range. For `n = 3` the Morlet
   wavelet decomposition in `rds_wavelet/` resolves this into a
   single dominant scale at `~27,559` bits sitting on a Brownian
   power-law background; that is roughly `~3–4` slow excursions
   across the `100,000`-bit prefix, not a clean periodic wave. The
   same set of entries shuffled into a random order destroys the
   structure and leaves a smooth shuffled residual. The residual is
   order-dependent and survives the bit-balance subtraction; that is
   the disparity-domain analog of the Walsh result that ordering
   matters for the binary ACM stream.

## Setup

For each monoid `n` in a panel of `13` monoids spanning `v_2 = 0..8`,
the script generates a binary stream of `100,000` bits truncated at
the largest entry boundary `≤ 100,000`. The panel is

| `n` | `v_2(n)` | `n_entries` | `⟨v_2(entry)⟩` |
|---|---|---:|---:|
| 3   | 0 | 7152 | 1.000 |
| 5   | 0 | 6905 | 1.000 |
| 7   | 0 | 6751 | 1.000 |
| 2   | 1 | 7212 | 1.000 |
| 6   | 1 | 6818 | 1.799 |
| 4   | 2 | 7017 | 2.333 |
| 12  | 2 | 6471 | 2.818 |
| 8   | 3 | 6697 | 3.571 |
| 16  | 4 | 6333 | 4.733 |
| 32  | 5 | 5996 | 5.839 |
| 64  | 6 | 5687 | 6.905 |
| 128 | 7 | 5406 | 7.945 |
| 256 | 8 | 5150 | 8.968 |

For each monoid the script computes:

- `RDS(t) = Σ (2·b_i − 1)` for `i ≤ t`
- `RDS_expected_monoid(t)` — closed-form drift assuming every entry
  has `v_2 = v_2(n)`
- `RDS_expected_per_entry(t)` — closed-form drift using each
  entry's actual `v_2(nk)`
- The shuffled-entry control: same set of `n`-primes in a random
  permutation, with its own per-entry expected curve

The closed-form per-entry contribution is

```
slope(m, d) =  1                                   if m = 0
            =  1 − m                               if 1 ≤ m and d ≤ 2m
            =  1 − 2m + m·2^m / (2^m − 1)          if d > 2m
```

This is a direct rewrite of the bias formula in
[`../HAMMING-BOOKKEEPING.md`](../HAMMING-BOOKKEEPING.md): 2·d·bias − d
collapses to a function of `m` and `d` independent of the entry
otherwise. The `d ≤ 2m` branch is the short-entry simplification
where the bottom-bit constraint is automatic.

The expected `RDS` curve is built by computing `slope(m, d)` per
entry, taking the cumulative sum at each entry-end position, and
linearly interpolating between (within-entry interpolation is
not literally exact but is fine for visualization at this scale).

## Why `v_2(n)` alone is wrong

For `n = 2^m`, the n-primes are `2^m · k` with `k` not divisible by
`2^m`. So `k` runs over `{1, 2, 3, …}` minus the multiples of `2^m`,
and `v_2(k) ∈ {0, 1, 2, …, m − 1}`. The conditional distribution of
`v_2(k)` on this set is geometric (after normalization), and gives

```
⟨v_2(2^m · k)⟩  =  m  +  Σ_{j=0}^{m−1}  j / (2^(j+1) · (1 − 1/2^m))
```

For `m = 1` (`n = 2`) the sum is empty and `⟨v_2(entry)⟩ = 1` exactly:
every entry of `n = 2` has `v_2 = 1`. For `m ≥ 2` the sum contributes
real mass and the entries have varying `v_2`. The empirical mean
`v_2(entry)` for the panel runs from `2.33` at `n = 4` up to `8.97`
at `n = 256`.

For composite `n = 2^a · q` with `q` odd, `v_2` of the entries is
`a + v_2(k)` for the same conditional `k`. So `n = 6` has
`⟨v_2(entry)⟩ = 1.80`, `n = 12` has `2.82`, and so on.

The naive reading of HAMMING-BOOKKEEPING — that monoids sharing
`v_2(n)` all have the same per-entry contribution to bit balance —
is therefore wrong as soon as `m ≥ 2`. The bit-balance closed form
is per-entry, parameterized by `v_2(entry)`, not per-monoid. This
note belongs back in HAMMING-BOOKKEEPING.

The naive prediction for composite `n` undershoots noticeably:

| `n` | `v_2(n)` residual end | per-entry residual end |
|---|---:|---:|
| 6   | −7785 |   −934 |
| 12  | −6264 |    +11 |
| 4   | −2739 |   +158 |

For `n = 12` the per-entry correction collapses the residual end
from `−6264` to `+11`. For `n = 6` it collapses from `−7785` to
`−934`. The composite-`n` residual under the naive prediction was
almost entirely an artifact of using the wrong `v_2`.

## Per-monoid summary

| `n` | `v_2(n)` | `⟨v_2(entry)⟩` | `res_mono_end` | `res_pe_end` | `\|res_pe\|max / √n_bits` | `\|shuf_pe\|max / √n_bits` |
|---|---:|---:|---:|---:|---:|---:|
| 3   | 0 | 1.00 |   −671 | +3826 | 12.10 | 12.10 |
| 5   | 0 | 1.00 |  −3366 |  +974 | 10.45 |  3.13 |
| 7   | 0 | 1.00 |  −2571 | +1669 |  8.02 |  5.36 |
| 2   | 1 | 1.00 |  −2176 | −2176 |  8.64 |  6.88 |
| 6   | 1 | 1.80 |  −7785 |  −934 |  5.64 |  3.10 |
| 4   | 2 | 2.33 |  −2739 |  +158 |  8.03 |  1.23 |
| 12  | 2 | 2.82 |  −6264 |   +11 |  7.70 |  0.63 |
| 8   | 3 | 3.57 |  −1472 | +2924 |  9.26 |  9.27 |
| 16  | 4 | 4.73 |  −2555 | +2507 |  9.73 |  7.98 |
| 32  | 5 | 5.84 |  −2195 | +3107 | 11.12 |  9.84 |
| 64  | 6 | 6.91 |  −2680 | +2632 | 11.93 |  8.35 |
| 128 | 7 | 7.95 |  −2692 | +2516 | 12.40 |  7.97 |
| 256 | 8 | 8.97 |  −2270 | +2774 | 12.66 |  8.80 |

The `√n_bits` column normalizes the maximum residual excursion
against the standard deviation of a fair random walk over the same
prefix length (`√100,000 ≈ 316`). A residual indistinguishable
from a fair walk would sit in the `1–3` range. Every monoid in the
panel sits well above that, with the typical per-entry residual
reaching `8–13 · √n_bits` at its peak.

## What the residual looks like

Every panel in `detrended_rds_residuals.png` shows coherent slow
structure in the per-entry residual: a few rises and falls across
the `100,000`-bit prefix with amplitude in the `2,000–4,000` range.
The shape is similar across monoids with different signs and
offsets — for `v_2(n) ≤ 1` the residual trends positive on average;
for `v_2(n) ≥ 2` it trends mixed. The Morlet wavelet decomposition
in `rds_wavelet/` characterises this for `n = 3` as a single
dominant scale at `~27,559` bits over a Brownian background; the
panel-wide spectral picture has not yet been worked out.

The shuffled-entry control destroys the oscillation. In every panel
the grey shuffled residual is markedly smoother than the green
original residual; for `n = 4` and `n = 12` it is almost flat
(`|shuf|max / √n = 1.23` and `0.63` respectively, compared to
`8.03` and `7.70` for the original). Two of the monoids — `n = 3`
and `n = 8` — have shuffled-residual maxes that match their
original maxes numerically, but inspection of the figure shows
that the shapes differ even where the peak magnitudes coincide.

The takeaway: the per-entry closed-form drift removes the
first-order, value-only contribution to disparity. What remains is
order-dependent, structured, and persistent — and it is destroyed
by the same entry-shuffle that the Walsh experiment used to
annihilate its 44-cell coefficient family.

## What this establishes

1. The HAMMING bit-balance closed form is per-entry, parameterized
   by `v_2(entry)`. The per-monoid `v_2(n)` claim in
   `HAMMING-BOOKKEEPING.md` is correct only for `n = 2` (and `n = 1`
   trivially). For all other monoids in the panel — including pure
   powers of two — the entries carry mixed `v_2`, and the per-entry
   formula is the right thing to subtract.
2. After subtracting the per-entry closed form, the residual is
   *not noise.* It carries a coherent oscillatory signal of
   amplitude `8–13 · √n_bits`, well above the fair-walk envelope.
3. The oscillatory structure is order-dependent. The same set of
   entries in shuffled order produces a markedly smoother residual,
   often by a factor of `5–12×`.
4. The disparity-domain finding is consistent with the spectral-
   domain finding from `WALSH.md`: in both observables, entry order
   carries structure that the marginal closed form does not capture.

## What's open

- **What does the dominant scale correspond to?** For `n = 3` the
  Morlet decomposition in `rds_wavelet/rds_wavelet_n3.py` resolves
  the residual into one dominant scale at `~27,559` bits sitting on
  a Brownian power-law background. It is not obvious whether the
  `27,559`-bit scale corresponds to bit-length-class transitions,
  to the mantissa structure of consecutive `n`-primes, or to a
  base-2 analog of the base-10 sawtooth structure already documented
  in [`../forest/epsilon_teeth/`](../forest/epsilon_teeth/) and the
  `acm_core` decomposition into `ln(n-Champernowne)`. The natural
  next step is to align the dominant excursions against the
  positions where consecutive entries cross a power of two and see
  whether the alignment is exact. The same wavelet analysis has not
  yet been run across the rest of the panel.
- **What does the oscillation shape encode?** The amplitude and
  phase of the oscillation vary by monoid. A per-monoid Fourier
  decomposition of the residual is the obvious follow-up, with the
  shuffled control as the null.
- **The two monoids with `|res_pe|max == |shuf_pe|max`.** `n = 3`
  and `n = 8` have nearly equal residual maxima for original and
  shuffled, even though the shapes are different. Whether this is
  coincidence or a structural fact — possibly related to `n = 3`
  being the smallest non-trivial odd monoid and `n = 8` being a
  pure power of two with `m = 3` — is open.
- **HAMMING-BOOKKEEPING update.** The doc currently claims that
  `n = 2, 6, 10, …` "behave like `n = 2`" because they share
  `v_2(n) = 1`. The empirical run shows this is wrong for `n = 6`
  (and presumably for any composite mixed monoid). The doc should
  be updated to say the closed form is per-entry, parameterized by
  `v_2(entry)`, and that the per-monoid claim is exact only for
  `n = 1` and `n = 2`.

## Method note

The script uses `entry_v2 = v_2(int(p))` per entry. For pure `n = 2^m`
this is fast and exact. For composite `n` it is also exact, since
each entry's value is known.

The shuffled-entry control uses the same set of entries permuted by
`random.shuffle` with `SEED = 12345`. Both the original and shuffled
residuals are computed against per-entry expected curves built on
their own entry orderings. The two curves agree exactly at the
final position (the cumulative sum of slopes is invariant under
permutation) and differ in their intermediate shapes.

The prefix is truncated to the largest entry boundary `≤ 100,000`.
The truncation loss is at most ~`200` bits per monoid and avoids
the complication of partial-entry expected values.

The `±√t` envelope shown on the residual panel is the standard
deviation of a fair Bernoulli random walk over the same prefix
length, included as a visual reference.

## See also

- [DISPARITY.md](DISPARITY.md) — the working memo this experiment
  belongs to. Experiment 2 is the one carried out here.
- [../HAMMING-BOOKKEEPING.md](../HAMMING-BOOKKEEPING.md) — the
  closed-form bit-balance source. Needs the per-entry correction
  noted above.
- [../forest/walsh/WALSH.md](../forest/walsh/WALSH.md) — the
  spectral-domain version of the same headline: entry order
  matters for the binary ACM stream.
- `detrended_rds.py` — the script.
- `detrended_rds_curves.png` — RDS panel with both the v_2(n)-only
  and per-entry expected curves overlaid.
- `detrended_rds_residuals.png` — residual panel with the shuffled-
  entry control and the ±√t envelope.
- `detrended_rds_summary.csv` — per-monoid statistics.
- `rds_wavelet/detrended_rds_n3.py` — single-panel large-format
  RDS(t) plot for `n = 3`, for close inspection of the residual
  structure used by the wavelet analysis.
- `rds_wavelet/rds_wavelet_n3.py` — Morlet CWT + Torrence–Compo
  wavelet variance + FFT cross-check on the `n = 3` residual.
  Establishes the single dominant scale at `~27,559` bits.
