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

This memo mixes four kinds of statements. They should not be read with
the same force.

- **Imported fact:** standard result from coding theory or symbolic dynamics
- **Local observation:** already supported by files in this repo
- **Inference:** plausible takeaway from imported facts plus local evidence
- **Open question:** something we do not know yet and should test


## What We Already Know Locally

The local base-2 work already gives us several strong footholds:

- **Local observation:** the binary stream itself, not leading digits, is
  the interesting object. See [../BINARY.md](../BINARY.md) and
  [../binary_core.py](../binary_core.py).
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
- **Local observation:** the all-`d`-bit baseline
  `(d+1)/(2d)` is a useful comparison, but the ACM sieve distorts it,
  sometimes strongly. See
  [../forest/one_bias/one_bias.py](../forest/one_bias/one_bias.py).

The practical consequence is important:

- **Inference:** the binary ACM stream should be analyzed against a
  control, not against an abstract “random binary stream” alone.
- **Inference:** for bit balance, the right first control is “all
  `d`-bit integers,” because that isolates the sieve residual from the
  ordinary fixed-MSB bias of binary notation.


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

- **Local observation:** there is no single universal ACM bit-balance
  law analogous to the all-`d`-bit formula `(d+1)/(2d)`.
- **Local observation:** even monoids can drift below `1/2` because
  forced trailing zeros outweigh the ordinary fixed-MSB excess.
- **Inference:** RDS should be treated as an empirical observable by
  monoid, not something already captured by a closed-form positive
  drift.
- **Open question:** after removing the empirical trend, do the
  boundary effects leave a stable monoid-specific residual shape?


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
  boundary-specific, especially as `v_2(n)` grows?


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
- **Open question:** is there any finite or finitely-presented model
  here that is honest enough to be useful?

What we should not claim yet:

- the binary ACM stream is already known to define a finite-state shift
- the exact entropy of a relevant shift space is already in hand
- the spectral radius of a yet-to-be-built automaton already measures
  “the information content of the stream per bit”

Those are research directions, not present results.


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

- **Plot:** `RDS(t) - alpha*t`, with `alpha` fit empirically per
  monoid.
- **Control:** shuffled-entry or shuffled-bit versions with the same
  marginal 1-fraction.
- **Interesting if:** the residual shows periodic or staircase
  structure tied to entry boundaries rather than generic noise.

### 3. Boundary-Conditioned Increments

- **Plot:** distribution of `ΔRDS` across windows centered on entry
  boundaries.
- **Control:** windows at random interior positions with matched
  lengths.
- **Interesting if:** boundaries produce monoid-specific asymmetry or
  variance not seen in interior windows.

### 4. Run Histogram vs. `v_2(n)`

- **Plot:** 0-run and 1-run histograms as a function of `n`, extending
  [../forest/rle_spectroscopy/rle_spectroscopy.py](../forest/rle_spectroscopy/rle_spectroscopy.py).
- **Control:** the same histograms for shuffled entries and for a fair
  Bernoulli stream with the same global 1-fraction.
- **Interesting if:** a low-dimensional parameterization by `v_2(n)`
  explains most of the 0-run structure.

### 5. Power Spectral Density

- **Plot:** PSD of the `±1` stream for several monoids.
- **Control:** fair Bernoulli and Bernoulli-with-matched-bias.
- **Interesting if:** there are stable low-frequency peaks or boundary
  harmonics that survive increasing prefix length.

### 6. Boundary Disparity Histogram

- **Plot:** histogram of `RDS` values sampled only at entry boundaries.
- **Control:** `RDS` sampled at equally spaced non-boundary positions.
- **Interesting if:** the boundary sample has a visibly different shape
  or drift rate, which would mean mass accumulation is not spatially
  uniform in the stream.


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
   heavy/light alternation, or only a drift?
2. Can a boundary-aware permutation minimize DSV more effectively than
   naive shuffling?
3. Is there a useful closed-form approximation for any of the empirical
   observables above as a function of `n` and `v_2(n)`?
4. Are there short patterns that identify entry boundaries with
   unusually high confidence?
5. Which binary-ACM observables survive BIDDER-style scrambling, and
   which are annihilated by it?
