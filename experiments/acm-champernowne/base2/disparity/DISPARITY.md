# Running Disparity and the Binary Champernowne Stream

## Why This Matters

The binary Champernowne stream of an ACM has a 1-bias, structured
run-length statistics, and boundary effects determined by the 2-adic
valuation of the monoid parameter. These are exactly the properties
that the telecommunications and magnetic recording industries spent
fifty years learning to measure, control, and exploit.

We did not set out to build a line code. But the binary Champernowne
stream *is* a constrained binary sequence — constrained by the algebra
of n-primality. The question is: what tools from constrained coding
theory can we borrow to characterize and understand our streams?

This document collects what we know about those tools.


## The Core Problem (Theirs)

When you send bits down a wire, through a fiber, or onto a magnetic
platter, the physical channel imposes constraints:

1. **Clock recovery.** The receiver's PLL needs transitions (0→1 or
   1→0) to stay synchronized. A long run of identical bits starves
   the PLL. After ~16 identical bits, clock drift causes bit errors.

2. **Baseline wander.** AC-coupled channels (transformers, series
   capacitors) block DC. If the stream has more 1s than 0s over a
   sustained interval, the coupling capacitor charges, shifting the
   receiver's decision threshold. The receiver can no longer tell
   0 from 1.

3. **Spectral flatness.** FEC decoders and DSP equalizers assume the
   signal has roughly flat spectral content. Long runs create
   low-frequency peaks that violate this assumption.

The solution: **encode the data** so the transmitted stream has
bounded run lengths and bounded cumulative imbalance between 1s and
0s. This is constrained coding.


## Running Digital Sum and Digital Sum Variation

The fundamental measurement. Given a bit stream b_1, b_2, ..., b_n,
the **running digital sum** (RDS) at position n is:

```
RDS(n) = sum_{i=1}^{n} (2*b_i - 1)
```

Each 1-bit contributes +1, each 0-bit contributes -1. The RDS is
a random walk on the integers, biased by the stream's bit balance.

The **digital sum variation** (DSV) of a sequence is the peak-to-peak
excursion of the RDS:

```
DSV = max_{m,n} |RDS(n) - RDS(m)|
```

A bounded DSV implies a spectral null at DC — the power spectral
density S(f) vanishes at f = 0 and grows as f^2 nearby. The tighter
the DSV bound, the wider the spectral notch.

**For our binary Champernowne stream:** The 1-bias of 1/(2d) means
the RDS has a positive drift of approximately 1/(2d) per bit. The
DSV is unbounded — it grows without limit. The stream is not DC-free.
But the *rate* of drift is algebraically determined and shrinks as
n-primes grow. The boundary effects (long 0-runs at high v_2(n))
create periodic downward excursions in the RDS. The RDS curve is a
biased random walk with algebraically-determined kicks.


## 8b/10b: The Gold Standard

**Paper:** Widmer & Franaszek, "A DC-Balanced, Partitioned-Block,
8B/10B Transmission Code," IBM J. Res. Dev., 27(5), 440-451, 1983.

Maps 8 data bits to 10 channel bits. Guarantees:
- Maximum run of 5 identical bits
- Running disparity bounded to {-1, +1} at symbol boundaries
- DC-free (bounded DSV)

**How it works.** The 8-bit input is split: 5 bits → 6b sub-block,
3 bits → 4b sub-block. Each sub-block has a *codeword digital sum*
(CDS) of 0 or ±2.

The encoder maintains a running disparity state: RD ∈ {-1, +1},
initialized to -1. At each sub-block:

| Current RD | Sub-block CDS | Encoding chosen | Next RD |
|---|---|---|---|
| -1 | 0 | neutral form | -1 |
| -1 | ±2 | +2 form (more 1s) | +1 |
| +1 | 0 | neutral form | +1 |
| +1 | ±2 | -2 form (more 0s) | -1 |

The encoder always selects the encoding that pushes RD back toward
zero. The two columns (RD- and RD+) of the encoding table are the
two complementary forms: one with two extra 1s, one with two extra
0s. The code is a *feedback system* — mass-aware, tracking the
cumulative imbalance and steering it.

**Special cases for run-length control.** Even with the disparity
machinery, some neutral-CDS symbols could create runs > 5 at
sub-block boundaries. Three special cases are handled:

- D.07 (input 00111): uses alternate 6b encodings (000111 or 111000)
  depending on RD, to break potential runs at the 5b/6b boundary
- D.x.3 (input 011): uses 0011 or 1100 depending on RD
- D.x.A7 (alternate for input 111): six specific input values use an
  alternate 4b encoding to prevent 4+ identical bits at the sub-block
  join

**Comma characters.** Control symbol K.28.5 encodes as 0011111010 or
1100000101 — the only valid patterns with a run of exactly 5. Since
data sequences never produce 5-run, the receiver can detect K.28.5
anywhere in the stream for bit-level synchronization. The maximum
run length is not just bounded — it is *reserved* as a signaling
channel.

**What we learn from this:**
- The RD tracking mechanism is a *single scalar summary* of the
  entire history of the stream. At any point, the encoder knows
  whether the stream is "heavy" (+1) or "light" (-1) and chooses
  the variant that rebalances. Our binary Champernowne stream has
  an analogous scalar: the running 1-bit fraction, which is
  (d+1)/(2d) per bit-length class.
- The two-column table (positive and negative disparity variants)
  is a controlled form of the same thing our n-primes do
  accidentally: some n-primes are "heavy" (many 1-bits) and some
  are "light" (many 0-bits). The question is whether the ordering
  imposed by n-primality has any tendency to alternate heavy and
  light, or whether it drifts.
- The reserved maximum run (comma character) suggests we look for
  whether certain run lengths in our stream are *impossible* or
  *uniquely identifying* — run lengths that could serve as
  boundary markers.


## 64b/66b: Statistical vs. Deterministic

**Standard:** IEEE 802.3ae (10 Gigabit Ethernet).

Prepends a 2-bit sync header (always 01 or 10 — guaranteed
transition every 66 bits) to 64 bits of scrambled payload.

**The scrambler.** Self-synchronizing LFSR with polynomial
G(x) = 1 + x^39 + x^58. Each output bit is XOR of the input bit
with taps at positions 39 and 58 of the shift register. The
descrambler is the same circuit, self-synchronizing after 58 bits.

**Key difference from 8b/10b:** The scrambler provides only
*statistical* guarantees. A run of 64 identical bits is possible
(probability ~2^{-64}; one expected occurrence per ~29 years at
10 Gbps). But the overhead is only 3.125% vs. 25%.

**The tradeoff:** 8b/10b is a *theorem* (max run = 5, always). 64b/66b
is a *confidence interval* (long runs are exponentially unlikely).
The industry moved from theorem to confidence interval because the
bandwidth cost of the theorem was too high.

**What we learn from this:**
- Our work moves in the opposite direction. BIDDER's value is the
  theorem, not the confidence interval. The exact uniformity at
  block boundaries is a deterministic guarantee, not a statistical
  one. The telecom industry's experience shows that deterministic
  guarantees are worth paying for — until the cost gets too high.
- The scrambler is a bijection (invertible), like our Speck
  permutation. It destroys structure in the bit stream. The
  question for us: does the Speck permutation destroy the
  run-length structure of the binary Champernowne stream, or
  does some of it survive?
- The sync header (guaranteed transition every 66 bits) is a form
  of the boundary structure we already have: every entry in our
  stream starts with 1. The question is whether the bit before
  that leading 1 (the trailing bit of the previous entry) creates
  a reliable transition.


## Run-Length Limited (RLL) Codes and Channel Capacity

**(d, k)-RLL constraint:** between consecutive 1-bits, there are at
least d and at most k consecutive 0-bits. The parameter d suppresses
high-frequency content (reducing intersymbol interference); k
guarantees transitions for clock recovery.

**Shannon capacity of the (d, k)-constrained channel:**

```
C(d, k) = log_2(lambda_max)
```

where lambda_max is the largest positive real root of the
characteristic polynomial of the constraint's adjacency matrix. This
result is from Shannon (1948), formalized for RLL by Franaszek (1968,
1970) and Adler, Coppersmith & Hassner (1983).

**Key capacities:**

| (d, k) | Capacity | Rate of best code | Efficiency |
|---|---|---|---|
| (0, 1) | log_2(phi) ~ 0.694 | 1/2 | 72.0% |
| (1, 3) | 0.5515 | 1/2 | 90.7% |
| (1, 7) | 0.6793 | 2/3 | 98.3% |
| (2, 7) | 0.5174 | 1/2 | 96.6% |

The capacity of a (d, k)-channel is irrational for all valid (d, k),
meaning no finite block code achieves exactly 100% efficiency.

**Historical application:** RLL codes dominated magnetic recording.
MFM = (1,3)-RLL at rate 1/2, used in hard drives from 1973 into the
1980s. (2,7)-RLL at rate 1/2 replaced it (IBM 3370, 1979), offering
50% more storage density. (1,7)-RLL at rate 2/3 became the standard
by the early 1990s.

**What we learn from this:**
- Our binary Champernowne stream satisfies a natural (d, k)
  constraint determined by the monoid. For monoid n with v_2(n) = m:
  every boundary creates a 0-run of length >= m, so the stream
  has a *minimum* 0-run length of m at periodic intervals. This is
  not exactly a (d, k) constraint (which applies between 1-bits
  globally), but it is a related structural property.
- The capacity formula gives us a way to measure the "cost" of our
  stream's constraints. If the binary Champernowne stream of monoid
  n can be characterized by effective (d, k) parameters, then
  C(d, k) tells us how much information-carrying capacity the
  algebraic structure destroys. The deficit 1 - C is the price of
  n-primality in bits per bit.
- The irrationality of capacity is intriguing. The golden ratio
  appears in the simplest case (0,1). Our stream's effective
  capacity might connect to algebraic numbers determined by n.


## Franaszek's Framework: Sequence-State Coding

**Papers:**
- "Sequence-State Coding for Digital Transmission," BSTJ 47(1),
  143-157, 1968.
- "Sequence-State Methods for Run-Length-Limited Coding," IBM J.
  Res. Dev. 14(4), 376-383, 1970.

Franaszek's insight: model the constrained channel as a deterministic
finite automaton (DFA). The set of allowed sequences forms a *sofic
shift* — a shift-invariant set describable by a labeled directed
graph. The states of the DFA capture exactly the information needed
to determine which symbols can legally follow.

The **state-splitting algorithm** (Adler, Coppersmith, Hassner 1983)
provides a constructive method to build finite-state encoders
achieving any rate below capacity. The key object is the *adjacency
matrix* A of the constraint graph. Its spectral radius
(largest eigenvalue) determines the capacity.

**What we learn from this:**
- Our binary Champernowne stream is generated by a deterministic
  process (enumerate n-primes, convert to binary, concatenate). This
  process can be modeled as a finite automaton whose states encode
  the current position within the binary representation of the
  current n-prime, plus the position within the sieve (k mod n).
  The adjacency matrix of this automaton would encode the stream's
  constraint structure.
- Franaszek's framework connects constraints to *eigenvalues*. If we
  build the automaton for our stream, its spectral radius gives the
  capacity — the information content of the stream per bit. This is
  a precise, computable measure of how much algebraic structure the
  ACM injects.
- The sofic shift perspective connects to symbolic dynamics (Lind &
  Marcus, 1995). Our stream is a specific element of a shift space
  defined by n-primality constraints. The entropy of that shift
  space is another way to quantify the algebraic content.


## Submarine Cables: The Full Stack

Modern undersea fiber optic cables use:

**Modulation:** Coherent DP-QPSK (4 bits/symbol) or DP-16QAM
(8 bits/symbol) with probabilistic constellation shaping (PCS) for
approaching Shannon capacity.

**FEC:** Soft-decision LDPC codes with ~20% overhead, achieving
net coding gain of ~12 dB at BER 10^{-15}. Three generations:
1st (Reed-Solomon hard-decision), 2nd (concatenated codes),
3rd (soft-decision iterative: LDPC, turbo product codes).

**Framing:** OTN (ITU-T G.709) with scrambler polynomial
1 + x + x^3 + x^12 + x^16, reset each frame. Frame alignment
bytes are NOT scrambled — they are the comma characters of the
optical layer.

**What we learn from this:**
- The submarine stack is a sequence of transformations that
  progressively shape the bit stream: data → FEC encoding →
  scrambling → modulation → physical channel. Each layer
  imposes and removes constraints. Our ACM construction is
  analogous: algebra → binary encoding → concatenation →
  stream. The "channel" is the mathematical analysis we
  perform on the stream.
- Probabilistic constellation shaping (PCS) is particularly
  interesting. It assigns non-uniform probabilities to symbols
  to approach channel capacity. Our n-primes have non-uniform
  bit patterns (the 1-bias, the v_2 trailing zeros). PCS
  suggests we ask: is the non-uniformity of our stream
  capacity-approaching for some natural channel, or is it
  just noise?
- The un-scrambled frame alignment bytes are exactly analogous
  to our entry boundaries: known, structured positions in the
  stream that carry algebraic rather than data content.


## What We Can Measure

The constrained coding literature gives us a toolkit for
characterizing our binary Champernowne streams:

1. **Running digital sum.** Plot RDS(n) for the stream. The slope
   is the 1-bias. The excursions around the trend are the boundary
   effects. The DSV (peak-to-peak excursion after detrending)
   measures how "wild" the stream is.

2. **Effective (d, k) parameters.** Measure the empirical minimum
   and maximum run lengths (separately for 0-runs and 1-runs).
   Compute the Shannon capacity C(d, k) as a function of n. This
   gives a channel-theoretic measure of the algebraic content.

3. **Power spectral density.** Fourier-transform the ±1 stream.
   Look for spectral nulls (DC balance) or spectral peaks
   (periodic structure). The boundary spacing creates a
   characteristic frequency; the v_2 trailing zeros modulate it.

4. **Automaton construction.** Build the DFA that generates the
   stream. Compute the adjacency matrix. Find the spectral radius.
   This is the most precise measure — it gives the exact entropy
   of the constrained shift space.

5. **Disparity histogram.** At each entry boundary, record the
   current RDS value. The distribution of RDS at boundaries
   characterizes how the stream's mass accumulates across entries.
   For 8b/10b, this would be a delta function at {-1, +1}. For
   our stream, it will be a drifting distribution whose shape
   encodes the interplay between the 1-bias and the v_2 kicks.


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


## Open Questions

1. Does the ordering of n-primes (by value) tend to alternate
   "heavy" and "light" entries, creating natural disparity
   control? Or does it drift systematically?

2. Can we define a "disparity-aware" ordering of n-primes —
   a permutation that minimizes DSV — and is that permutation
   related to the Speck permutation or to any natural algebraic
   ordering?

3. What are the effective (d, k) parameters of the binary
   Champernowne stream as a function of n and v_2(n)? Is there
   a closed form?

4. Does the DFA for the binary Champernowne stream have a
   spectral radius expressible in terms of known constants
   (related to n, or to the density of n-primes)?

5. The 8b/10b comma character (the unique maximum-run pattern)
   suggests: are there run-length patterns in our stream that
   uniquely identify entry boundaries? If so, the stream is
   self-synchronizing — you can find the boundary positions
   without external metadata.

6. Probabilistic constellation shaping makes non-uniform symbol
   distributions capacity-approaching. Our stream's 1-bias is
   non-uniform. Is it capacity-approaching for any natural
   channel model, or is the non-uniformity pure overhead?
