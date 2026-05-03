# First-digit fingerprint of A_⟨3,5⟩

`interlock/INTERLOCKING-DEFECTS.md` §"What's open" item 1: how does the
leading-digit distribution of the multiplicative atoms of `S = ⟨3, 5⟩`
compare with primes (the conjectured nearest neighbour) and with `M_n`
atoms (the substrate baseline, exactly uniform per the substrate
clauses)?

## Setup

- `N = 10⁶`.
- `A_⟨3,5⟩` enumerated via the gap-determination predicate
  (`interlock/ns_atoms.py`), with a reducibility-sieve fast path in
  the experiment script.
- Primes via Eratosthenes; `M_n` atoms via the closed form
  `{n·k : 1 ≤ k ≤ N/n, n ∤ k}`.
- Per-decade leading-digit counts aggregated into a single length-9
  histogram per sequence.
- Distance to references measured by total variation:
  `TVD(p, q) = ½ ∑_d |p_d − q_d|`.

## Result

```
sequence          count  TVD(unif)  TVD(Benf)   TVD(NS)
--------------------------------------------------------
A_⟨3,5⟩         155,333     0.0205     0.2484    0.0000
primes           78,498     0.0197     0.2494    0.0015
M_2-atoms       250,000     0.0000     0.2687    0.0205
M_3-atoms       222,222     0.0000     0.2687    0.0205
M_5-atoms       160,000     0.0000     0.2687    0.0205
```

Per-digit frequencies (× 10⁴):

```
  d         A_⟨3,5⟩        primes     M_2-atoms     M_3-atoms     M_5-atoms
  1          1227.3        1221.1        1111.1        1111.1        1111.1
  2          1169.3        1164.6        1111.1        1111.1        1111.1
  3          1139.8        1141.4        1111.1        1111.3        1111.1
  4          1113.4        1114.3        1111.1        1111.1        1111.1
  5          1093.6        1097.5        1111.1        1111.1        1111.1
  6          1081.2        1077.5        1111.1        1111.3        1111.1
  7          1069.4        1074.5        1111.1        1111.1        1111.1
  8          1058.0        1060.7        1111.1        1111.1        1111.1
  9          1047.9        1048.4        1111.1        1111.1        1111.1
```

See `first_digit.png` for the five-panel comparison and
`first_digit_summary.txt` for the raw output.

## What this says

1. **`A_⟨3,5⟩` tracks primes essentially exactly.** TVD against the
   prime histogram is `0.0015`, an order of magnitude below TVD against
   any `M_n` (`0.0205`). The shape — monotone-decreasing from
   `1227 / 10⁴` at digit 1 to `1048 / 10⁴` at digit 9 — is the
   characteristic Cramér-density tilt for prime-rate sequences:
   slightly biased toward Benford but nowhere near it (TVD against
   full Benford is `≈ 0.25` for both `A_⟨3,5⟩` and primes).

2. **`M_n` atoms are exactly uniform.** TVD against `1/9` is `0.0000`
   to four decimals for `n ∈ {2, 3, 5}`, with per-strip count
   `1111.1 / 10⁴` matching `1/9` to the precision of the readout. This
   is the substrate clauses (`paper/PAPER.md` §3) realised at scale —
   regular per-strip counts give exact leading-digit uniformity.

3. **The §5 prediction lands the way it was hedged.** The doc said
   "close to uniform at leading order, with gap-dependent residuals
   from the scaled-prime layers." At this scale the residual against
   uniform is small (`0.02`) but stable, and matches the prime
   residual to `0.001`. The "gap-dependent" part of the prediction is
   *not* tested here — that requires comparing different generator
   sets and is the topic of the next experiment.

4. **The shifted-prime-layer mixture does not measurably distort the
   prime shape at `N = 10⁶`.** `A_⟨3,5⟩` past `F = 7` is a union of
   primes-in-`S`, `2p`, `4p`, `7p`, plus a finite gap-stuck tail
   (§3). Multiplying a Benford-tilted set by a constant preserves the
   tilt, so a mixture should also be tilted; the empirical match
   (TVD ≈ 0.0015) confirms the layers behave additively in
   leading-digit space at this resolution.

## What this does not say

- Whether the gap set leaves a *fingerprint* in the residual against
  uniform. At fixed `S`, the prime baseline and the atom baseline
  agree to `0.0015`. The fingerprint claim requires comparing
  `A_⟨3,5⟩` against `A_⟨3,7⟩, A_⟨4,5⟩, …` and looking for shape
  variation between them, not against a fixed external reference.
  That is the next experiment.
- Anything about per-decade behaviour. The aggregate hides per-decade
  fluctuations; if any single decade carries a sharp deviation it
  would be averaged out here.
- Anything about block-uniformity / spread (item 3 in
  `INTERLOCKING-DEFECTS.md` §"What's open"), which probes a strict
  per-strip count rather than a frequency.

## Files

- `first_digit.py` — experiment script.
- `first_digit.png` — five-panel histogram comparison.
- `first_digit_summary.txt` — counts, TVDs, per-digit table.
