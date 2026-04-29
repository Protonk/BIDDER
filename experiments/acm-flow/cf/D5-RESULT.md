# d = 5 confirmation of the spike formula at b = 10

The closed-form spike scale `S_k(n, b) ≈ D_k(n, b) − C_{k−1}(n, b)`
(`MEGA-SPIKE.md`) was empirically validated at `k ∈ {2, 3, 4}` in
`MULTI-K-RESULT.md`, with the residual at `k = 4` collapsing to
the universal boundary-truncation factor `log_b(b/(b − 1)) ≈ 0.0458`
once `T_k` is computed via direct atom counting.

Extending one rank to `k = 5` at `b = 10` across the panel
`n ∈ {2, 3, 4, 5, 6, 10}`: the formula holds with relative gap
roughly 10× smaller than at `k = 4` across all `n`. No new
families surface; the `O(b^{−k})` deficit-decay rate from
`MULTI-K-RESULT.md` extends one rank.


## Headline

| n  | k=4 gap%  | k=5 gap% | improvement |
|---:|---:|---:|---:|
| 2  | −0.122 % | −0.012 % | 10.3× |
| 3  | −0.220 % | −0.022 % | 10.0× |
| 4  | −0.343 % | −0.041 % |  8.4× |
| 5  | −0.604 % | −0.062 % |  9.8× |
| 6  | −0.827 % | −0.086 % |  9.6× |
| 10 | −2.420 % | −0.244 % |  9.9× |

`F(d, b)` scales as `~ b^{d-1}` so the predicted spike grows by a
factor `b ≈ 12` per `d`-step (`F(5, 10)/F(4, 10) = 411 111 / 33 111
= 12.4`). Relative gap dropping by ~10× is the arithmetic match:
absolute gap in base-`b` digits is roughly constant in `d` at fixed
`n`, with the leading order absorbing the b-scaling.


## Panel

```
  n    pred_b-d     obs_b-d       gap      gap%     i  valid
------------------------------------------------------------------
  2   102777.75   102765.65    -12.10  -0.0118%   408   2903
  3    91358.00    91337.95    -20.05  -0.0219%   488   3855
  4    77083.31    77051.85    -31.46  -0.0408%   516   4861
  5    65777.76    65737.05    -40.71  -0.0619%   616   5731
  6    57098.75    57049.95    -48.80  -0.0855%   660   5763
 10    36999.99    36909.65    -90.34  -0.2442%   844   6827
```

Compare absolute base-10 digit gap k=4 → k=5:

| n  | k=4 gap | k=5 gap | gap ratio |
|---:|---:|---:|---:|
| 2  | −10  | −12.10 | 1.21× |
| 3  | −16  | −20.05 | 1.25× |
| 4  | −21  | −31.46 | 1.50× |
| 5  | −32  | −40.71 | 1.27× |
| 6  | −38  | −48.80 | 1.28× |
| 10 | −72  | −90.34 | 1.25× |

Gap grows 1.21–1.50× per `d`-step while the predicted spike grows
12.4×. Sub-leading correction is bounded as `d` increases,
consistent with `MULTI-K-RESULT.md`'s finding that the residual
decays as `b^{−k}` past `T_k(actual) − 2 L_{k−1} + log_b(b/(b−1))`.


## What this rules out and what it doesn't

The `k = 4` panel could in principle have been a fitted match at
one rank only, with the cumulative-digit-gap identity `D_k − C_{k−1}`
not the actual spike size at other ranks. d=5 rules this out:
predicted vs observed at `n = 2` is 102 778 vs 102 766 base-10
digits — gap of 12 digits, vs the 10-digit gap at `k = 4`. The
closed form tracks d=5 spikes within `~10⁻⁴` relative error.

The n-panel at `k = 5` reproduces the same monotone-in-`n` curve
seen at `k = 4`, with no per-`n` classification breakdown that
wasn't already present at `k = 4`. So this is a confirmation rank,
not an exploration rank.

What this does not address:

- The `O(b^{−k})` deficit's per-`n` coefficient `β(n)` from
  `MULTI-K-RESULT.md` (some `n` share, some don't). The panel was
  not designed to extract `β(n)`; that extension is straightforward
  but not pursued here.
- The off-spike denominator process. Same gating issue as step 3
  of `MECHANISTIC-DERIVATION.md`.


## Compute

Per-case timings (sage-python, mpmath), with `PREC_BITS_LO` scaled
to `~3.5×` predicted spike size in bits:

| n  | prec_LO bits | LO time | HI time | total | validated PQs |
|---:|---:|---:|---:|---:|---:|
| 2  | 1 194 971 | 134 s | 410 s |  9.1 min | 2 903 |
| 3  | 1 062 197 | 119 s | ~330 s |  7.5 min | 3 855 |
| 4  |   898 871 | 100 s | ~280 s |  6.3 min | 4 861 |
| 5  |   764 781 |  87 s |  172 s |  4.3 min | 5 731 |
| 6  |   663 872 |  82 s |  150 s |  3.9 min | 5 763 |
| 10 |   430 189 |  61 s |  111 s |  2.9 min | 6 827 |

Full panel: ~34 minutes. Memory: peak ~1 GB during `n = 2` (mpf
intermediates at 2.4 M-bit HI precision).

`cf_spikes_d5.py` uses inline spike identification rather than
storing the full convergent denominator list — at `d = 5` those
grow to `10⁵`-decimal-digit bignums and storing 8 000 of them
would use multi-GB.


## Files

- `cf_spikes_d5.py` — panel runner.
- `cf_d5.csv` — per-cell data.
- `cf_d5_summary.txt` — same data, table form.
- `cf_d5_run.log` — per-case timings and diagnostics.
