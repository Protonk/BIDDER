# d = 5 confirmation — closed form holds at one more rank

The closed form `S_k(n, b) ≈ D_k(n, b) − C_{k−1}(n, b)` from
`MEGA-SPIKE.md` lines 41–49 was empirically validated at
`k ∈ {2, 3, 4}` in `MULTI-K-RESULT.md`, with the residual at k = 4
collapsing to the universal boundary-truncation factor
`log_b(b/(b − 1)) ≈ 0.0458` once `T_k` is computed via direct atom
counting (`T_k(actual)`).

This document tests one more rank: `k = 5`, at b = 10, across the
same n-panel `{2, 3, 4, 5, 6, 10}`.

**Pure confirmation: the formula holds at k = 5 with relative gap
~10× smaller than at k = 4 across all n. No new families surface.
The `O(b^{−k})` deficit-decay rate from `MULTI-K-RESULT.md` extends
one rank.**


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
factor `b ≈ 12` per `d`-step (more precisely `F(5, 10)/F(4, 10) =
411 111 / 33 111 = 12.4`). Relative gap dropping by ~10× is the
arithmetic match: **absolute gap in base-`b` digits is roughly
constant in `d` at fixed `n`**, with the leading order absorbing the
b-scaling.


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

Gap grows 1.21–1.50× per `d`-step, while predicted spike grows 12.4×.
Sub-leading correction is bounded as `d` increases, consistent with
the `MULTI-K-RESULT.md` finding that the residual decays as
`b^{−k}` past `T_k(actual) − 2 L_{k−1} + log_b(b/(b−1))`.


## What this rules out and what it doesn't

**Rules out.** The "d = 4 coincidence" concern flagged in
`arguments/MEGA-SPIKE-FOUR-WAYS.md` and in the earlier brief 2
framing — that the cumulative-digit-gap identity `D_k − C_{k−1}`
might be a fitted match at one rank and not the actual spike size at
others. Predicted vs observed at d = 5 for n = 2 is 102 778 vs
102 766 base-10 digits — gap of 12 digits, vs the 10-digit gap at
d = 4. The closed form tracks d = 5 spikes within ~10⁻⁴ relative
error.

**Does not surface new structure.** The n-panel at k = 5 reproduces
the same monotone-in-`n` curve seen at k = 4, with no per-`n`
classification breakdown that wasn't already present at k = 4. So
this is a confirmation rank, not an exploration rank.

**Does not address.** The `O(b^{−k})` deficit's per-n coefficient
`β(n)` from `MULTI-K-RESULT.md` (some `n` share, some don't) — at
k = 5 we see relative gaps roughly 10⁻⁴, but the panel was not
designed to extract `β(n)`. That extension is straightforward but
not pursued here.

The off-spike denominator process (`L_{k−1}` structure) is also not
addressed — same gating issue as `MECHANISTIC-DERIVATION.md` step 3.


## Compute summary

Per-case timings (sage-python, mpmath), at PREC_BITS_LO scaled to
~3.5× predicted spike size in bits:

| n  | prec_LO bits | LO time | HI time | total | validated PQs |
|---:|---:|---:|---:|---:|---:|
| 2  | 1 194 971 | 134 s | 410 s |  9.1 min | 2 903 |
| 3  | 1 062 197 | 119 s | ~330 s |  7.5 min | 3 855 |
| 4  |   898 871 | 100 s | ~280 s |  6.3 min | 4 861 |
| 5  |   764 781 |  87 s |  172 s |  4.3 min | 5 731 |
| 6  |   663 872 |  82 s |  150 s |  3.9 min | 5 763 |
| 10 |   430 189 |  61 s |  111 s |  2.9 min | 6 827 |

Full panel: ~34 minutes. Memory: peak ~1 GB during n = 2 (mpf
intermediates at 2.4 M-bit HI precision).

The runner (`cf_spikes_d5.py`) uses inline spike identification
rather than storing the full convergent denominator list — at d = 5
those grow to 10⁵-decimal-digit bignums and storing 8000 of them
would use multi-GB.


## Files

- `../../../experiments/acm-flow/cf/cf_spikes_d5.py`
  — panel runner.
- `../../../experiments/acm-flow/cf/cf_d5.csv` —
  per-cell data.
- `../../../experiments/acm-flow/cf/cf_d5_summary.txt`
  — same data, table form.
- `../../../experiments/acm-flow/cf/cf_d5_run.log` —
  per-case timings and diagnostics.

(Compute artifacts live in `cf/`; analysis lives here.)


## Provenance

Closed form: `MEGA-SPIKE.md` lines 41–49. Multi-k extension at
b = 10 across `k ∈ {2, 3, 4}`: `MULTI-K-RESULT.md`. The four-ways
framing of the formula's open content:
`arguments/MEGA-SPIKE-FOUR-WAYS.md`. The empirical work for this
d = 5 push was originally done under a parallel framing in
`experiments/acm-flow/cf/SPIKE-D5-RESULT.md`
(now superseded; see status preamble there).

**This is the canonical home for the d = 5 confirmation.**
