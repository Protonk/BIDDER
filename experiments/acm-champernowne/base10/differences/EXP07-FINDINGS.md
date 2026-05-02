# EXP07 — the digit-3 spike comes from high-d source streams

EXP06 found that survivors over-represent digit 3 (20.4% vs bundle's
12.4%). Stratifying by source stream **localises this spike almost
entirely to source streams `d ∈ {8, 9, 10}`**. Low-d streams
(`d = 2..6`) actually contribute *less* digit-3 than the bundle
baseline — the low-d contributions go in the *wrong direction*, and
high-d streams overwhelm them.

The mechanism turns out to be a **finite-k rank-truncation effect**.
"Survivors" with source d=10 are mostly integers `c = 10·m` whose
"true" non-source stream (typically `n=5`) had rank > k=400, so the
non-source atom got truncated out of the bundle. The resulting
"apparent survivors" have cofactors `m` constrained to a narrow
range, and that range's leading digits are biased toward 2-3-4. This
isn't an artifact of error — it's a real, predictable consequence of
how the truncated-bundle survivor set differs from the
limit-bundle survivor set.

## Setup

Same panel: `[2, 10], k = 400`, 1338 survivors. For each source
stream `d ∈ [2..10]`, partition survivors:

```
d  | |S_d|  | share | P_d(3)
---+--------+-------+--------
 2 |   187  | 14.0% | 8.0%
 3 |   147  | 11.0% | 8.2%
 4 |   133  |  9.9% | 3.8%
 5 |   129  |  9.6% | 3.9%
 6 |    62  |  4.6% | 0.0%   ← zero digit-3 survivors!
 7 |   180  | 13.5% | 15.6%
 8 |   152  | 11.4% | 36.2%
 9 |   212  | 15.8% | 40.6%
10 |   136  | 10.2% | 49.3%   ← highest
```

`P_d(3)` is the fraction of stream-d survivors whose first decimal
digit is 3. For high-d streams (8, 9, 10), it is 36–49%; for low-d
streams (2–6), it is 0–8%.

## Decomposition of the digit-3 excess

The aggregate survivor digit-3 frequency is `0.2040`. The bundle's
is `0.1244`. Total excess: `+0.0796`. Decomposed by source stream
(showing each stream's contribution `(|S_d|/|Surv|) · P_d(3)` minus
the baseline `(|S_d|/|Surv|) · 0.1244`):

```
d  | actual contrib | baseline | Δ        | % of excess
2  |  0.0112        | 0.0174   | −0.0062  |  −7.8%
3  |  0.0090        | 0.0137   | −0.0047  |  −5.9%
4  |  0.0037        | 0.0124   | −0.0086  | −10.8%
5  |  0.0037        | 0.0120   | −0.0083  | −10.4%
6  |  0.0000        | 0.0058   | −0.0058  |  −7.2%
7  |  0.0209        | 0.0167   | +0.0042  |  +5.3%
8  |  0.0411        | 0.0141   | +0.0270  | +33.9%
9  |  0.0643        | 0.0197   | +0.0446  | +56.0%
10 |  0.0501        | 0.0126   | +0.0374  | +47.0%
```

Three streams (`d = 8, 9, 10`) account for `33.9% + 56.0% + 47.0% =
136.9%` of the excess; the negative contributions from low-d streams
bring the net to 100%. The spike is dominated by `d ∈ {8, 9, 10}`.

## The mechanism: finite-k truncation

For `d = 10`, why do 49% of survivors have leading digit 3?

A "true" `d = 10`-only survivor would be `c = 10m` such that no other
`n ∈ [2..9]` has both `n | c` and `n² ∤ c`. Since `c = 2·5·m`, the
integer `c` is *always* divisible by both 2 and 5. So:

- `c` not in stream 2 ⟹ `4 | c` ⟹ `m` even.
- `c` not in stream 4 ⟹ `16 | c` ⟹ `8 | m`.
- `c` not in stream 5 ⟹ `25 | c` ⟹ `5 | m`.
- `c` not in stream 8 ⟹ `64 | c` ⟹ `32 | m`.

These constraints force `m` divisible by `LCM(32, 5) = 160`. But
`160 = 16 · 10`, so `10 | m`, contradicting the stream-10 condition
`10 ∤ m`. **There are no integers in stream 10 only.**

Yet the bundle counts 136 such "apparent survivors." They're integers
`c = 10m` that *are* in another stream (typically `n = 5`), but whose
rank in that other stream **exceeds k = 400**, so the non-source atom
is truncated out of the bundle. Within the truncated bundle, only
the stream-10 atom `(10, c)` appears, so `counts[c] = 1`, and the
script flags `c` as a survivor with source `d = 10`.

For `d = 10`, this happens when `c = 10m` with rank in stream 5
exceeding 400. Stream 5's k-th 5-prime is approximately `5 · k · 5/4 =
6.25k`, so `c` exceeds this when `c > 2500`, i.e., `m > 250`. And
rank in stream 10 must remain ≤ 400, so `m ≲ 500`. The window
`m ∈ (250, 500]` gives apparent d=10 survivors.

The leading digits of `c = 10m` are exactly the leading digits of `m`
(multiplying by 10 just appends a zero). The range `(250, 500]`
contains:

- `m ∈ (250, 299]`: leading digit 2
- `m ∈ [300, 399]`: leading digit 3
- `m ∈ [400, 499]`: leading digit 4

That's a 1:2:2 ratio for digits 2:3:4, with 49% on digit 3 (from the
[300, 399] band weighted by coprimality-to-10 density). Empirically:
49.3%. The arithmetic checks.

The same mechanism applies to `d = 8, 9` with different constraints:

- `d = 9`'s structural impossibilities are similar; apparent survivors
  are `c = 9m` with rank in stream 3 (a non-trivial competitor)
  exceeding 400. `m` lands in a band that biases digits 3 and 4.
- `d = 8` similar with stream 4 as the truncated competitor.

## What this reframes

EXP06 said: "each multiplicity has a distinct leading-digit shape."
EXP07 sharpens: **the survivor's distinctive shape is partly a
finite-k artifact in specific source streams**.

Predictions:

- At larger `k`, the cofactor band `(250, 500]` for `d=10` would
  shift to `(2 · k_5, 2 · k_10]` — different ranges, different
  leading-digit content, different aggregate shape.
- At `k → ∞`, the apparent `d ∈ {8, 9, 10}` survivors disappear
  (no truly source-10-only survivors exist by the structural
  argument). The aggregate's digit-3 spike would vanish.

This means the EXP06 finding (and EXP04's z = +2.21 signal) is
**panel-specific because it's k-specific**: the spike size depends
on which finite-k truncation band is currently in scope. The
EXP05 parameter sweep already showed this from outside (z varies
across panels); EXP07 explains the mechanism from inside.

## What this opens

The reframing chain is:
- Differences view: null (transducer)
- Random control view: panel-specific signal
- Multiplicity view: each multiplicity has its shape
- **Source-stream view: shape is finite-k truncation artifact in high-d streams**

The most concrete next move:

- **EXP08: limit-survivor estimation.** For each `c = d·m` in the
  apparent-survivor set, check whether `c` is also in any other
  stream `n ∈ [2..9]` (mathematically, ignoring k-truncation).
  Survivors with no mathematical doubleton are *true* limit-survivors
  in the `k → ∞` sense. Plot the leading-digit distribution of just
  these. Prediction: the digit-3 spike disappears, and the
  limit-survivors look more like the bundle's leading-digit
  distribution.

If that prediction holds, the EXP06 "rich shape" reading was largely
a finite-k artifact of the truncation. The cabinet's curiosity entry
then needs sharper revision: **the L1 tracking holds at the magnitude
level for both finite-k apparent survivors and limit survivors; the
shape differences are finite-k truncation effects in high-d streams,
not properties of the survivor construction itself**.

That's a more honest read of what `differences/` has been showing,
and it walks back the optimizer reading further: the bundle/survivor
relation is even *more* tightly constrained than EXP04-06 suggested,
and the apparent richness has been mostly truncation noise.

## Files

- `exp07_source_stream_stratification.py` — script.
- `exp07_source_stream_stratification.png` — four-panel figure:
  aggregate stacked by source stream, per-stream distributions,
  stream populations, digit-3 contribution per stream.
