# Running Disparity and the Binary Champernowne Stream

## Purpose

This is a working memo for experiment design.

The point is not to claim that the binary Champernowne stream of an
ACM is secretly a practical line code. The point is narrower: the
telecom and magnetic-recording literatures built a very good language
for talking about constrained binary streams, and that language gives
us useful measurements for our own source.

In particular, these tools help us reason about:

- bit imbalance over prefixes
- boundary-conditioned run structure
- spectral consequences of that structure
- what scrambling might or might not destroy


## Status Legend

This memo mixes five kinds of statements. They should not be read with
the same force.

- **Imported fact:** standard result from coding theory or symbolic dynamics
- **Local observation:** already supported by files in this repo
- **Inference:** plausible takeaway from imported facts plus local evidence
- **Conjecture:** a precisely-stated working assumption we treat as a
  boundary condition but have not proven in this repo
- **Open question:** something we do not know yet and should test


## What We Already Know Locally

This memo predates the Walsh, Hamming-bookkeeping, and Valuation
Forest results. Folding those in, the base-2 footholds are now:

- **Local observation:** the binary stream itself, not leading
  digits, is the interesting object. See [../BINARY.md](../BINARY.md)
  and [../binary_core.py](../binary_core.py).
- **Local observation:** the bit-balance of an n-prime stream has a
  *closed form* that depends only on `v_2(n)`. For `n = 2^m`, the
  expected fraction of 1-bits in a `d`-bit n-prime is
  `1/2 + (1/(2d))·[1 − 2m + m·2^m/(2^m − 1)]`, valid for `d > 2m`.
  Every monoid sharing the same `v_2` lies on the same curve. See
  [../HAMMING-BOOKKEEPING.md](../HAMMING-BOOKKEEPING.md) and the
  empirical confirmation in
  [../forest/hamming_strata/](../forest/hamming_strata/).
- **Local observation:** boundary structure depends strongly on
  `v_2(n)`. Even monoids force trailing zeros before the next entry's
  leading `1`. See
  [../forest/boundary_stitch/BOUNDARY_STITCH.md](../forest/boundary_stitch/BOUNDARY_STITCH.md)
  and
  [../forest/boundary_stitch/boundary_stitch.py](../forest/boundary_stitch/boundary_stitch.py).
- **Local observation:** run-length statistics visibly track the
  monoid's 2-adic structure. See
  [../forest/rle_spectroscopy/rle_spectroscopy.py](../forest/rle_spectroscopy/rle_spectroscopy.py)
  and [../art/rle/RLE.md](../art/rle/RLE.md).
- **Local observation:** mean zero-run length, stratified by
  `v_2(n)`, rises monotonically from `v_2 = 2` downward; the
  `v_2 = 0` and `v_2 = 1` row means are essentially equal (a
  plateau the bit-balance argument predicts only weakly).
  Within-stratum residuals are mostly faint, but the exceptions
  concentrate at the smallest odd parts and are dominated by
  `m = 1`. See
  [../forest/valuation/VALUATION.md](../forest/valuation/VALUATION.md).
- **Local observation:** the binary ACM stream's coefficient-level
  Walsh-Hadamard spectrum carries `44` cells that survive a multi-
  stage robustness bar; *all `44` die under entry-order shuffle*.
  The 44 split into three populations under length and `v_2`-based
  controls (`9` length+`v_2` explainable, `15` length-only
  explainable, `20` neither). The brightest cells are uncorrelated
  with `v_2(n)`; `v_2(n)` is *one* organizing variable in this
  family, not the master variable. See
  [../forest/walsh/WALSH.md](../forest/walsh/WALSH.md).
- **Local observation:** the all-`d`-bit baseline `(d+1)/(2d)` is a
  useful comparison, but the ACM sieve distorts it, sometimes
  strongly. See
  [../forest/one_bias/one_bias.py](../forest/one_bias/one_bias.py).
- **Conjecture:** no finite-state automaton recognizes a binary ACM
  stream. See [../FINITE-RECURRENCE.md](../FINITE-RECURRENCE.md).
  We treat this as a boundary condition on which constrained-coding
  tools apply literally and which apply only as measurements; see
  *Imported Tool: Sequence-State Coding* below.

The practical consequence is sharper than it was when this memo was
first written:

- **Inference:** the binary ACM stream should be analyzed against a
  control, not against an abstract "random binary stream" alone.
- **Inference:** for bit balance, the right *first* control is the
  closed-form `v_2`-stratified curve from
  [../HAMMING-BOOKKEEPING.md](../HAMMING-BOOKKEEPING.md). The
  all-`d`-bit baseline `(d+1)/(2d)` is the *second* control: it
  isolates the sieve residual from the ordinary fixed-MSB bias of
  binary notation. An empirical fit per monoid is the *third*
  control and should never be the first thing fit, because it
  conflates the known closed-form drift with whatever residual is
  actually interesting.
- **Inference:** for any spectral observable, the right first
  control is now the entry-order shuffle. Walsh established that
  shuffle annihilates the entire 44-cell family at coefficient
  level; that is the strongest single shuffle result we have, and
  any new spectral measurement should be reported with shuffle as
  the default null.


## The Core Problem (Theirs)

When bits move through a physical channel, three issues dominate:

1. **Clock recovery.** Long runs of identical bits starve the receiver
   of transitions.
2. **Baseline wander.** Sustained imbalance between 1s and 0s pushes
   the receiver's effective threshold on AC-coupled links.
3. **Spectral shaping.** Long-range structure moves energy toward low
   frequencies and creates periodic lines.

The standard response is to encode the data so the transmitted stream
has bounded run lengths, bounded cumulative imbalance, or both.

- **Imported fact:** constrained coding is largely about controlling
  these pathologies.
- **Inference:** our binary ACM stream is not engineered for those
  goals, but the same measurements still tell us where its structure
  lives.


## Running Digital Sum and Digital Sum Variation

Given a bit stream `b_1, b_2, ..., b_n`, define the **running digital
sum**:

```
RDS(n) = sum_{i=1}^{n} (2*b_i - 1)
```

Each `1` contributes `+1`, each `0` contributes `-1`.

The **digital sum variation** is the peak-to-peak excursion:

```
DSV = max_{m,n} |RDS(n) - RDS(m)|
```

- **Imported fact:** bounded DSV implies strong DC suppression.
- **Imported fact:** a DC-balanced code keeps RDS tightly controlled.

For our stream:

- **Local observation:** the bit-balance of an n-prime stream has a
  closed form parameterized by `v_2(n)`. For `n = 2^m`, the per-
  integer deficit from the all-`d`-bit baseline is
  `−m·(2^(m-1) − 1)/(2^m − 1)` ones, independent of `d`. See
  [../HAMMING-BOOKKEEPING.md](../HAMMING-BOOKKEEPING.md). The
  expected slope of `RDS(t)` is therefore set by `v_2(n)` and the
  current `d`, not by anything we have to fit.
- **Local observation:** monoids with `v_2 ≥ 2` drift below `1/2`
  because the trailing-zero penalty outweighs the bottom-bit
  constraint bonus. Monoids with `v_2 ≤ 1` approach `1/2` from
  above; monoids with `v_2 ≥ 2` approach from below.
- **Inference:** the right detrender for `RDS(t)` is the closed-form
  drift from `HAMMING-BOOKKEEPING`, not an empirical fit. Empirical
  fitting would conflate the known structure with whatever residual
  is actually interesting.
- **Open question:** after subtracting the closed-form drift, does
  the residual carry stable monoid-specific structure tied to entry
  boundaries, or does it look like noise once the `v_2`-driven
  trend is removed?


## Imported Tool: 8b/10b

**Paper:** Widmer & Franaszek, "A DC-Balanced, Partitioned-Block,
8B/10B Transmission Code," IBM J. Res. Dev., 27(5), 440-451, 1983.

8b/10b maps 8 data bits to 10 channel bits and gives:

- maximum run length 5
- running disparity state `RD ∈ {-1, +1}`
- DC balance through active correction

The mechanism is feedback: the encoder tracks running disparity and
chooses among alternative encodings to steer the mass back toward zero.

Comma characters are the synchronization lesson here. In practice the
important fact is not merely “there exists a run of 5,” but that a
reserved comma pattern is detectable in-stream and used for alignment.

What we should borrow:

- **Imported fact:** one scalar state can be enough to summarize
  balance history for control purposes.
- **Inference:** we should ask whether our stream has boundary-local
  signatures that play a comma-like role, even though nothing here is
  actively controlled.
- **Open question:** are there short windows that are unusually
  boundary-specific, especially as `v_2(n)` grows? The Walsh
  experiment ([../forest/walsh/WALSH.md](../forest/walsh/WALSH.md))
  showed that all `44` robust coefficient-level cells die under
  entry-order shuffle, which says short patterns *do* carry
  ordering information — but does not yet identify which short
  patterns play the comma-like role. The Walsh boundary test at
  `k = 8` was degenerate (every 256-bit chunk already contains many
  boundaries); the right rerun is at `k = 4` or `k = 5` where chunks
  are short enough to separate interior windows from
  boundary-straddling ones.


## Imported Tool: 64b/66b

**Standard:** IEEE 802.3ae.

64b/66b prepends a 2-bit sync header (`01` or `10`) to 64 bits of
scrambled payload. Its scrambler is self-synchronizing, using the
polynomial:

```
G(x) = 1 + x^39 + x^58
```

The point is the tradeoff:

- **Imported fact:** 8b/10b gives theorem-level guarantees at high
  overhead.
- **Imported fact:** 64b/66b gives statistical whitening at low
  overhead.

What we should borrow:

- **Inference:** BIDDER's permutation can be discussed in the same
  theorem-vs-statistics language.
- **Open question:** when the source is the binary ACM stream, which
  observables survive scrambling and which collapse to the control?
- **Inference:** the sync header is a useful analogy for our known
  entry boundaries, but only as an analogy. It does not mean the ACM
  stream is self-synchronizing.


## Imported Tool: RLL Codes and Capacity

A `(d, k)` run-length-limited constraint means that between
consecutive `1` bits there are at least `d` and at most `k` zeros.

Its Shannon capacity is

```
C(d, k) = log_2(lambda_max)
```

where `lambda_max` is the spectral radius of the constraint graph.

Useful anchor values:

| (d, k) | Capacity | Rate of best code | Efficiency |
|---|---|---|---|
| (0, 1) | log_2(phi) ~ 0.694 | 1/2 | 72.0% |
| (1, 3) | 0.5515 | 1/2 | 90.7% |
| (1, 7) | 0.6793 | 2/3 | 98.3% |
| (2, 7) | 0.5174 | 1/2 | 96.6% |

What we should borrow:

- **Imported fact:** capacity turns a combinatorial constraint into a
  single scalar.
- **Inference:** an empirical “effective `(d, k)`” fit could be a
  useful summary of our stream.
- **Warning:** an effective `(d, k)` fit is only a summary statistic.
  It is not the literal law of the ACM source.
- **Open question:** does a low-dimensional summary like effective
  `(d, k)` track `v_2(n)` cleanly enough to be useful?


## Imported Tool: Sequence-State Coding

**Papers:**

- Franaszek, "Sequence-State Coding for Digital Transmission," 1968
- Franaszek, "Sequence-State Methods for Run-Length-Limited Coding," 1970

This literature models a constrained channel by a state graph. The
adjacency matrix then controls counts, rates, and capacity.

What we should borrow:

- **Imported fact:** state-graph models are the right language when a
  stream really is generated by a finite constraint system.
- **Inference:** symbolic-dynamics language may still help us describe
  local forbidden patterns or boundary-conditioned subshifts.
- **Conjecture:** no finite-state automaton recognizes the binary ACM
  stream. See [../FINITE-RECURRENCE.md](../FINITE-RECURRENCE.md).
  The argument is that entry lengths are unbounded, the natural
  periodicity lives in `k`-space and is destroyed by the
  variable-length stretching into bit-stream-space, and two of the
  three quantities controlling local structure (`v_2` of the entry,
  position within bit-length class, residue mod `n`) are themselves
  unbounded. The conjecture is treated as a boundary condition on
  what we build, not as a result we have proven in this context.

What this means for the borrowed tools:

- Running digital sum, run-length distributions, power spectral
  density, disparity histograms — these are *measurements* and apply
  to any bit stream. They do not require finiteness. We use them
  freely.
- Shannon capacity of a constrained channel `C = log_2 λ_max` of the
  adjacency matrix, the state-splitting algorithm, and the eigenvalue
  characterization of the shift space all require a finite adjacency
  matrix that we conjecturally do not have. They apply only inside a
  fixed bit-length *slice* of the stream, where the constraint
  structure is locally finite.
- The productive border: each bit-length class is a finite world
  where Franaszek's tools apply fully. Per-class capacity is
  computable. Whether the per-class capacities converge to a limit
  as `d → ∞` is itself an open question, and that limit (if it
  exists) is what would replace `λ_max` in the non-finite setting.

What we should not claim:

- the binary ACM stream is a sofic shift
- there is a single shift-space entropy that the literature's tools
  compute directly
- there is a finite automaton waiting to be discovered


## Imported Tool: The Submarine Stack

Modern optical systems layer framing, scrambling, FEC, and modulation.

This matters here only as a modeling analogy:

- **Imported fact:** real systems often separate structure-preserving
  layers from whitening layers.
- **Inference:** the ACM binary stream and BIDDER permutation can be
  treated the same way: source first, scrambling second.
- **Open question:** which observables survive that second layer?

This is the right spirit in which to use the literature. It is not a
claim that our source belongs in that engineering stack.


## Immediate Experiments

These are the next useful measurements. Each one has a target plot, a
control, and a criterion for “interesting.”

### 1. Global RDS Traces

- **Plot:** `RDS(t)` for several monoids on a common bit index.
- **Control:** the all-`d`-bit baseline from
  [../forest/one_bias/one_bias.py](../forest/one_bias/one_bias.py),
  converted to expected `RDS`.
- **Interesting if:** odd and even monoids separate cleanly, or the
  slope clusters by `v_2(n)`.

### 2. Detrended RDS

- **Plot:** `RDS(t) − RDS_expected(t)`, where `RDS_expected` is the
  closed-form drift parameterized by `v_2(n)` from
  [../HAMMING-BOOKKEEPING.md](../HAMMING-BOOKKEEPING.md). The drift
  is *not* fit empirically; it is computed from `v_2(n)` and the
  per-entry bit lengths and subtracted directly.
- **Control:** entry-shuffled ACM stream with the same set of
  entries in a permuted order. The shuffled stream has the same
  closed-form drift, so its detrended residual is the natural null.
- **Interesting if:** the residual has stable monoid-specific
  structure — periodic features, staircase shape, excursions
  exceeding a fair-walk envelope, or systematic difference from the
  shuffled-control residual.

### 3. Boundary-Conditioned Increments

- **Plot:** distribution of `ΔRDS` across windows centered on entry
  boundaries.
- **Control:** windows at random interior positions with matched
  lengths.
- **Interesting if:** boundaries produce monoid-specific asymmetry or
  variance not seen in interior windows.

## What To Compare Against

These controls should be used repeatedly:

1. **All `d`-bit integers.** This is the right notation-only baseline.
2. **Fair Bernoulli bits.** This is the randomness baseline.
3. **Bias-matched Bernoulli bits.** This separates marginal imbalance
   from boundary structure.
4. **Entry-shuffled ACM stream.** This tests whether ordering matters.
5. **BIDDER-scrambled output.** This tests which observables survive
   scrambling.


## Key References

| Authors | Year | Title | Venue |
|---|---|---|---|
| Shannon | 1948 | "A Mathematical Theory of Communication" | BSTJ 27, 379-423 |
| Franaszek | 1968 | "Sequence-State Coding for Digital Transmission" | BSTJ 47(1), 143-157 |
| Franaszek | 1970 | "Sequence-State Methods for Run-Length-Limited Coding" | IBM J. Res. Dev. 14(4), 376-383 |
| Widmer, Franaszek | 1983 | "A DC-Balanced, Partitioned-Block, 8B/10B Transmission Code" | IBM J. Res. Dev. 27(5), 440-451 |
| Adler, Coppersmith, Hassner | 1983 | "Algorithms for Sliding Block Codes" | IEEE Trans. IT, IT-29(1), 5-22 |
| Immink, Siegel, Wolf | 1998 | "Codes for Digital Recorders" | IEEE Trans. IT, 44(6), 2260-2299 |
| Immink | 2004 | *Codes for Mass Data Storage Systems* (2nd ed.) | Shannon Foundation |
| Lind, Marcus | 1995 | *An Introduction to Symbolic Dynamics and Coding* | Cambridge |


## Longer-Horizon Questions

1. Does the natural ordering of `n`-primes create a detectable
   heavy/light alternation, or only a drift? **Answered in part by
   Walsh:** the entry-order shuffle test in
   [../forest/walsh/WALSH.md](../forest/walsh/WALSH.md) shows that
   *some* order-dependent structure exists for every robust
   coefficient-level cell. The narrower question — whether the
   relevant ordering is a heavy/light alternation specifically, or
   some other ordering — is still open at the bit level.
2. Can a boundary-aware permutation minimize DSV more effectively than
   naive shuffling?
3. Is there a useful closed-form approximation for any of the empirical
   observables above as a function of `n` and `v_2(n)`? **Answered
   for bit balance:** [../HAMMING-BOOKKEEPING.md](../HAMMING-BOOKKEEPING.md)
   gives the closed-form drift parameterized by `v_2(n)`. The same
   kind of closed form for run-length distributions, boundary-
   conditioned increments, and local autocorrelation is still open;
   the Valuation Forest result that mean zero-run length stratifies
   cleanly by `v_2` (with localized small-odd-part residuals) is a
   first empirical step in that direction.
4. Are there short patterns that identify entry boundaries with
   unusually high confidence? Walsh's boundary-conditioned test at
   `k = 8` was degenerate; a `k = 4` or `k = 5` rerun is the obvious
   next step and is listed as an open question in
   [../forest/walsh/WALSH.md](../forest/walsh/WALSH.md).
5. Which binary-ACM observables survive BIDDER-style scrambling, and
   which are annihilated by it? **Still open.** The Walsh experiment
   used *structural* synthetic controls (length-only, `v_2`-only,
   entry-order shuffle) but did not run the BIDDER permutation
   itself. The BIDDER question is untested.
