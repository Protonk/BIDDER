# d = 5 boundary spike result

## ⚠️ STATUS UPDATE — superseded by the mega-spike thread

This was Phase 2 of `BRIEF2-CLOSED-FORM.md`'s closed-form program —
see that document's status preamble for the full reframe. The d = 5
push extends `cf/MULTI-K-RESULT.md` (which covered
`k ∈ {2, 3, 4}` at b = 10) by one rank. **It's pure confirmation:**
the closed form holds at k = 5 with relative gap ~10× smaller than
at k = 4 across all n in the panel, no new families surface.

This finding has been promoted to `cf/D5-RESULT.md`, which
is the canonical home. The compute artifacts (`cf_spikes_d5.py`,
`cf_d5.csv`, `cf_d5_summary.txt`, `cf_d5_run.log`) remain in this
folder.

For the current state, read `cf/D5-RESULT.md`.

---

Phase 2 of `BRIEF2-CLOSED-FORM.md`. Direct d-axis test at `b = 10`,
`n ∈ {2, 3, 4, 5, 6, 10}` — the same n-panel as the original
`cf_spikes.py` at d = 4 — to determine whether the closed-form
prediction `(n − 1)/n² · F(d, b)` survives one decade further in d.

The Phase 1 panel (`SPIKE-CLOSED-FORM-PANEL.md`) confirmed the closed
form across six bases at varying d. It did not, however, sweep d at
fixed b — leaving open the "Probably-Nothing 2" outcome of
`BRIEF2-CLOSED-FORM.md`: that the d = 4 match was a numerological
coincidence and the bookkeeping identity `D_d − C_{d−1}` is not
actually the spike size.

This phase rules that out.


## Headlines

1. **The d = 4 coincidence concern is rejected.** Predicted vs observed
   at `(b, n, d) = (10, 2, 5)`: 102 778 vs 102 766 base-10 digits — a
   gap of 12 digits, vs the 10-digit gap at d = 4. The closed form
   tracks d = 5 spikes within ~10⁻⁴ relative error.

2. **Relative accuracy improves by a factor of ~10 going d=4 → d=5.**
   Across all six n values the gap percent dropped by 8–12×:

   | n  | d=4 gap% | d=5 gap% | improvement |
   |---:|---:|---:|---:|
   | 2  | −0.122% | −0.012% | 10.3× |
   | 3  | −0.220% | −0.022% | 10.0× |
   | 4  | −0.343% | −0.041% |  8.4× |
   | 5  | −0.604% | −0.062% |  9.8× |
   | 6  | −0.827% | −0.086% |  9.6× |
   | 10 | −2.420% | −0.244% |  9.9× |

   `F(d, b)` scales as `O(b^d)` so the predicted spike grows ~`b` per
   d-step (more precisely, `F(5, 10)/F(4, 10) = 411 111 / 33 111 = 12.4×`).
   gap% dropping by ~10× matches `gap_baseb / F`, i.e. the absolute gap
   in base-`b` digits is **roughly constant in `d`** at fixed `n`.

3. **Sub-leading correction is bounded in `d`.** The absolute gap
   in base-10 digits grew only 1.21–1.50× going d=4 → d=5, while the
   predicted spike grew 12.4×:

   | n  | d=4 gap | d=5 gap | gap ratio |
   |---:|---:|---:|---:|
   | 2  | −10  | −12.10 | 1.21× |
   | 3  | −16  | −20.05 | 1.25× |
   | 4  | −21  | −31.46 | 1.50× |
   | 5  | −32  | −40.71 | 1.27× |
   | 6  | −38  | −48.80 | 1.28× |
   | 10 | −72  | −90.34 | 1.25× |

   Consistent with sub-leading correction `O(d) · g(n)` rather than
   `O(b^d) · g(n)`. The Mahler-style upper bound (P4) of the closed-form
   proof looks attainable: bound the spike size by predicted ± O(d · n)
   in base-`b` digits.


## Panel data

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

(Panel runner: `cf_spikes_d5.py`. Per-case precision scaled to ~3.5×
predicted spike in bits; LO precision 430k–1.2M bits across n.)


## What this resolves vs. leaves open

**Resolved.**

- *Brief Probably-Nothing outcome 2:* "the closed form is a coincidence
  of fits at d = 4." Rejected. The same closed form predicts d = 5
  spikes correctly across the n-panel; the cumulative-digit identity
  `D_d − C_{d-1}` does map to the spike size at higher d.

- *D-axis behavior:* leading-order spike size scales as `F(d, b) ·
  (n − 1)/n²` across both d = 4 and d = 5. The asymptotic ratio
  `(b − 2)/(b − 1)` to `D_d` (which would have reached its limit only
  at large d) is already in striking distance at d = 5: for b = 10 the
  ratio gap (b − 2)/(b − 1) − F(d,b)/D_d shrinks as `O(b/(d·(b−1)²))`
  per the closed form, which at d = 5 puts F/D = 8.222 vs asymptotic
  8.889 = (b−2)/(b−1) — well within the 8 + correction structure.

**Still open.**

- *Brief Probably-Nothing outcome 1:* "sub-leading drift fully
  explained by edge-effect formula with no monoid content." This phase
  shows sub-leading correction is bounded in d (consistent with edge
  effects), but doesn't derive an explicit closed form for it.

- *Brief Probably-Nothing outcome 3:* "sub-leading drift grows
  superlinearly in n." The d = 5 panel only covers n ∈ {2..6, 10}; the
  d = 4 extended panel (`SPIKE-CLOSED-FORM-PANEL.md`) showed roughly
  `O(n)` growth with mild super-linearity through n = 20. d = 5 with
  more n values would test this, but each cell costs minutes at
  high precision; not justified at this stage.

- *Mahler-style proof:* steps (P1) – (P4) of the brief remain the
  obligation. The d = 5 data tightens the empirical target
  significantly: the proof's (P4) upper bound must give
  `log_b a_{i_d} ≤ F(d, b) · (n − 1)/n² + C·d + C'·n`
  for explicit constants, and the panel data is consistent with
  `C ≈ 0` and `C' ≈ 8` for b = 10.


## CF spike index across d

A small structural curiosity: the CF position of the d-boundary spike.

| n  | i at d=4 | i at d=5 | ratio |
|---:|---:|---:|---:|
| 2  | 118  | 408  | 3.46× |
| 3  | 162  | 488  | 3.01× |
| 4  | 148  | 516  | 3.49× |
| 5  | 178  | 616  | 3.46× |
| 6  | 188  | 660  | 3.51× |
| 10 | 212  | 844  | 3.98× |

Ratio is ~3.5× across all n. Per the cumulative-digit identity, the
spike at d-boundary lands at the i where `log_b q_{i-1} ≈
(C_d − log_b a_i)/2`. With log_b a_i ≈ F(d, b)·(n−1)/n² and
C_d ≈ d·F(d, b)/b (asymptotic), this gives log_b q_{i-1} ≈
F(d, b)·(d/b − (n−1)/n²)/2. The ratio of i across d depends on how
fast log q grows per CF step, which has structure of its own
(Khinchin-typical behavior between d-block boundaries).

That's a question for off-boundary PQ statistics, not addressed here.


## Coupling to the brief

This phase delivers the d-axis result the brief identified as
prerequisite to the conditional irrationality-measure corollary:

> Under the Khinchin-typical assumption [on off-boundary PQs], the
> irrationality measure `μ(C_b(n))` is a function of `b` alone (not
> `n`); ... `μ → 10` for `b = 10`.

The corollary requires the boundary-spike growth law to hold across
all sufficiently large d, not just d = 4. d = 5 is one more data point
in that direction. A full proof needs the Mahler argument (paper, not
compute); this phase confirms the empirical target the proof has to
match.

For the FINITE-RANK-EXPANSION speculation: the leading-order match at
d = 5 keeps the rank-1 reading intact. The cf boundary-spike
observable continues to factor through atom density × positional
skeleton, with no rank-h structure visible.


## Compute summary

Per-case timings on this machine (sage-python, mpmath):

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


## Files

- [cf_spikes_d5.py](cf_spikes_d5.py) — panel runner (uses inline
  spike search to avoid storing the full convergent denominator
  list — at d = 5 those grow to 10⁵-decimal-digit bignums and
  storing 8 000 of them would use multi-GB).
- [cf_d5.csv](cf_d5.csv) — per-cell data.
- [cf_d5_summary.txt](cf_d5_summary.txt) — same data, table form.
- [cf_d5_run.log](cf_d5_run.log) — per-case timings and diagnostics.


## What's next

In order of cost:

**(c) Mahler-argument writeup** — the brief's (P1) – (P4) carried out
explicitly. With the d = 4 and d = 5 empirical confirmations, the
proof's job is well-scoped: it has to bound the boundary-spike size
within `O(d · n)` of the leading order, uniformly across the smooth
and non-smooth cases. This is paper work, not compute.

**(b) Cross-base d-scaling spot check** — one cell at `(b, n, d) =
(8, 2, 5)` or `(12, 2, 5)` would test whether the d-scaling result
holds across bases. Cost: ~10 min per cell.

**(d) Wider-n d = 5 fill-in** — only n = 7, 11, 13, 20 added to the
existing d = 5 panel would replicate the extended-n d = 4 panel at
d = 5, testing whether the n-monotone drift stays clean. Cost:
~30 min, but lower marginal information than (c).

(c) is the natural next step. The empirical scaffolding is now
complete enough to constrain the proof's structure — the d = 5
result fixes the order of the sub-leading correction, and the
Phase 1 panel fixes the n- and b-dependence of it.
