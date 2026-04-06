# Binary Champernowne of ACMs

## The Construction

Current setup: take n-primes, write each in decimal, concatenate after a radix point.

Proposed: take the same n-primes, write each in **binary**, concatenate.

For n=2 (2-primes: 2, 6, 10, 14, 18, 22, 26, 30, ...):

```
Decimal:  2     6     10      14      18       22       26       30
Binary:   10    110   1010    1110    10010    10110    11010    11110
Stream:   0.10|110|1010|1110|10010|10110|11010|11110|...
Flat:     0.101101010111010010101101101011110...
```

In BQN (`BinDigits`, `BStream` from `guidance/BQN-AGENT.md`; mirrors
`experiments/binary/binary_core.py`):

```bqn
NPn2      ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}
BinDigits ← {𝕩<2 ? ⟨𝕩⟩ ; (𝕊⌊𝕩÷2)∾⟨2|𝕩⟩}
BStream   ← {⥊ BinDigits¨ 𝕩}

BStream (8↑ 2 NPn2 8)
# ⟨1,0,1,1,0,1,0,1,0,1,1,1,0,1,0,0,1,0,1,0,1,1,0,1,1,0,1,0,1,1,1,1,0⟩
```

The entry boundaries disappear into a single bit stream. What follows is
what changes, what breaks, and what becomes visible.


## 1. The Sawtooth Gets Faster

In base 10, the sawtooth has teeth at 10, 100, 1000, ... — each tooth
10x longer than the last. The Champernowne real sweeps [1.1, 2.0] per
tooth.

In base 2, teeth occur at 2, 4, 8, 16, 32, 64, ... — each tooth only
2x longer. The binary Champernowne fraction sweeps [0.5, 1.0) per tooth
(in decimal terms), or equivalently [0.1, 1.0) in binary.

| Property | Base 10 | Base 2 |
|---|---|---|
| Teeth per decade of n | 1 | ~3.32 |
| Length ratio, tooth k+1 / tooth k | 10 | 2 |
| Range per tooth | [1.1, 2.0] | [0.5, 1.0) |
| Running mean limit | 31/20 = 1.55 | 3/4 = 0.75 |

The base-2 sawtooth is much more granular. On a log-n axis, all teeth
have identical shape (linear sweep from 0.5 to ~1.0, then drop). The
base-10 sawtooth has the same self-similarity, but teeth are stretched
by a factor of 10 each time, making the pattern appear sparser.

The "drops" at powers of 2 are more frequent but less dramatic in terms
of the surrounding context — each drop is followed by a tooth only 2x
long (not 10x), so recovery is faster. The running mean should approach
3/4 with less dramatic oscillation than the base-10 mean approaching
31/20.


## 2. Leading-Digit Uniformity Collapses to Triviality

This is the biggest structural change.

In base b, the leading digit of integers in [b^(d-1), b^d - 1] is
uniform over {1, ..., b-1}. This gives b-1 equiprobable symbols. In
base 10: 9 symbols, each at probability 1/9.

**In base 2: the leading bit of every positive integer is 1.** The
alphabet is {1} — a single symbol. The uniformity guarantee becomes
vacuous: 1 symbol appearing with probability 1/1 = 1.

The foundational theorem of BIDDER ("leading digits are exactly uniform
over complete blocks") is *true* in binary — trivially, uninformatively
true. The entire leading-digit analysis framework, which is the engine
of the project, has nothing to grab onto.

This means: **binary Champernowne is not a generator.** It cannot
produce varied output from leading-digit extraction. The construction
produces an interesting mathematical object (a bit stream), but the
*mechanism* that makes BIDDER work — projecting to a non-trivial
alphabet via leading-digit extraction — has no purchase in base 2.


## 3. The Interesting Object: The Bit Stream Itself

With leading digits dead, the natural object of study shifts from
"sequence of leading digits" to "the raw bit stream produced by
concatenation." This stream has genuine structure.

**Bit balance (the 1-bias):**

A d-bit positive integer has its MSB fixed at 1 and d-1 free bits. Over
all 2^(d-1) numbers in the d-bit class, the expected fraction of 1-bits
is:

```
fraction of 1s = (d + 1) / (2d)
```

In BQN: `{(𝕩+1)÷2×𝕩}` for bit-length d. This approaches 1/2 from
above but never reaches it.

| Bit-length d | Fraction of 1s | Excess over 1/2 |
|---|---|---|
| 1 | 1.000 | 0.500 |
| 2 | 0.750 | 0.250 |
| 3 | 0.667 | 0.167 |
| 4 | 0.625 | 0.125 |
| 10 | 0.550 | 0.050 |
| 20 | 0.525 | 0.025 |
| d | (d+1)/(2d) | 1/(2d) |

The stream has a **persistent 1-bias** of 1/(2d) that shrinks as
n-primes grow but never reaches zero at any finite prefix. This is
fundamentally different from base 10, where the deviation is *exactly
zero* at block boundaries.

In base 10, the boundary story is: "at n = 10^d - 1, every digit
appears equally often." In base 2, the boundary story is: "at the d-bit
boundary, bit positions 1..d-1 are individually balanced, but position 0
(MSB) is all-1." The uniformity is **per-position**, not aggregate.


## 4. RLE Becomes a Structural Fingerprint

In a binary stream, Run-Length Encoding (counting consecutive 0s or 1s)
is the most natural compression. For a truly random bit stream, the
expected run length is 2, and runs of length k appear with probability
1/2^k.

The binary Champernowne of n-primes departs from this in structurally
informative ways:

**Boundary signatures depend on the 2-adic valuation of n.**

Every n-prime is a multiple of n. The trailing zeros of a multiple of n
in binary are determined by v_2(n) (the largest power of 2 dividing n).
Meanwhile, every entry starts with a leading 1. So at each entry
boundary in the concatenation:

```
...trailing bits of p_k | leading 1 of p_{k+1}...
```

The trailing bits are predictable:

| n | v_2(n) | Trailing pattern of n-primes | Boundary pattern |
|---|---|---|---|
| 2 | 1 | always ...0 | ...0\|1... |
| 4 | 2 | always ...00 | ...00\|1... |
| 8 | 3 | always ...000 | ...000\|1... |
| 3 | 0 | ...0 or ...1 (mixed) | variable |
| 6 | 1 | always ...0 | ...0\|1... |
| 5 | 0 | ...0 or ...1 (mixed) | variable |

**For powers of 2:** n = 2^m forces exactly m trailing zeros before
every boundary's leading 1. This creates a guaranteed "01" transition
at every boundary (for n=2), or "001" (for n=4), or "0001" (for n=8).
These are **invisible in base 10** but glaringly visible in RLE.

The 2-adic valuation that drives this (`V2` from
`guidance/BQN-AGENT.md`; exact math — local `v2` helpers appear in
experiment scripts like `forest/rle_spectroscopy/rle_spectroscopy.py`):

```bqn
V2 ← {0=2|𝕩 ? 1+𝕊⌊𝕩÷2 ; 0}    # positive integers only
```

The trailing-zero count of an n-prime n×k is at least `V2 n`.
For even n, every boundary has a guaranteed dark stripe of width
`V2 n` in the stitch image.

**RLE as an n-detector:** The run-length distribution of the binary
Champernowne stream carries a fingerprint of n's 2-adic structure.
Given the stream, you could estimate v_2(n) from the excess of short
0-runs at boundary-like intervals. This is a genuinely new observable
connecting ACM structure to information-theoretic measures. The base-10
construction has no clean analog.

**Compression ratio as a randomness measure:** RLE compression of a
truly random bit stream yields ~50% compression. The binary Champernowne
stream will compress *slightly better* (due to the 1-bias and structured
boundaries), and the deviation from 50% is a scalar measure of the
algebraic content.


## 5. The epsilon Connection Becomes Exact

This might be the deepest observation.

In base 10, the sawtooth ln(C_10(n)) ~ ln(1 + m) where m is the
base-10 mantissa was identified as a "base-10 cousin" of the
floating-point correction epsilon(m) = log_2(1+m) - m from SlideRule.

In base 2, the sawtooth **IS** epsilon. Not an analog — the function
itself. In BQN:

```bqn
{(2⋆⁼1+𝕩)-𝕩}                    # ε₂(m) = log₂(1+m) − m
```

for mantissa m ∈ [0, 1). This is the exact SlideRule function.

The binary Champernowne fraction for n in the d-bit class:

```
C_2(n) ~ n / 2^d = 2^(d-1+f) / 2^d = 2^(f-1)
```

where f = {log_2(n)} is the fractional part of log_2(n), i.e., the
base-2 mantissa.

So:

```
ln(C_2(n)) ~ (f - 1) * ln(2) = ln(2) * ({log_2(n)} - 1)
```

The sawtooth sweeps [{log_2(n)} - 1] * ln(2) as n traverses a
bit-length class. The correction between the sawtooth and its secant
is:

```
epsilon_2(m) = log_2(1 + m) - m
```

This is the *exact* SlideRule function. The base-10 connection required
a translation (base-10 mantissa, base-10 logs). The binary connection
is identity.

**Implication:** Everything discovered about epsilon in SlideRule —
the bump at m ~ 0.5, the peak height ~0.0861, the concavity
structure — maps directly onto the binary Champernowne sawtooth
without any base conversion. The "compositeness pressure"
interpretation of epsilon-peaks applies verbatim.


## 6. The Rolling Shutter Gets Faster

Under addition of binary Champernowne reals (mean mu = 3/4), the sum
S_N ~ N*mu, and the fractional part of log_2(S_N) advances at rate:

```
Delta{log_2(S_N)} ~ log_2(1 + mu/S_N) ~ mu/(S_N * ln 2) per addition
```

Comparing to base 10 at the same N:

```
rate_2 / rate_10 = ln(10) / ln(2) ~ 3.32
```

The binary rolling shutter rotates ~3.32x faster per addition. The
shear angle is steeper. The stripes in the heatmap are narrower and
more numerous.

But there's a deeper difference: since the leading bit is always 1, the
rolling shutter for "bit position" distributions is qualitatively
different. In base 10, the leading digit cycles 1->9->1 as the sum
crosses powers of 10. In base 2, it's the *mantissa bits* (positions
1, 2, 3, ...) that cycle as the sum crosses powers of 2. The cycling
is in a higher-dimensional space (multiple bit positions simultaneously)
rather than a single digit cycling through 9 values.


## 7. The Mental Pictures Change

**Digit Fabric -> Binary Matrix:**

The 10-color textile (digit fabric) becomes a **black-and-white ragged
matrix**:
- Each row = one n-prime in binary
- Rows grow in length (ragged right)
- Left column: solid white (all leading 1s)
- Moving right: increasing balance, approaching 50/50

The visual effect: a white wedge on the left fading into salt-and-pepper
noise. The fadeout rate depends on d (bit-length). For n=2, the second
column is also structured (all n-primes are even -> second-to-last bit
follows a pattern), adding additional texture.

**Sawtooth -> Ripple Chain:**

Instead of dramatic decadal teeth, you get a chain of gentle ripples at
every doubling. On a log-n axis, the ripples are equally spaced and
identically shaped — a *periodic* waveform rather than a self-similar
expanding one.

**Sieve -> Binary Sieve:**

The moire sieve (pixel (k,n) lit if k is n-prime) doesn't change — it's
about n-primality, not representation. But if you instead plot the
*bits* of n-primes (bit position j of the k-th n-prime of monoid n),
you get a 3D object: axes are (n, k, j). Slices along j show how each
bit position's statistics depend on the monoid.


## 8. What the Binary View Reveals About BIDDER

The binary Champernowne perspective makes the generator's design logic
crisper:

**The projection step is the key.** BIDDER's novelty is not the
permutation (that's standard counter-mode), nor the block structure
(that's positional notation). It's the **projection from d-digit
numbers to their leading digit** — a many-to-one map that preserves
exact uniformity.

In base 2, this projection maps everything to 1. It destroys all
information. This shows that the projection's power depends entirely on
the base: **the larger the base, the more information survives the
projection** (b-1 output symbols from each evaluation). Base 2 is the
degenerate limit.

Conversely, the multi-digit extraction route (using ALL d bits, not just
the leading one) works equally well in any base. In binary, it gives you
d-1 independent fair bits per evaluation (dropping the deterministic
leading 1). This is just counter-mode PRNG with known good statistical
properties — the ACM structure adds nothing that the permutation doesn't
already provide.

**The takeaway:** BIDDER's distinctive value — exact uniformity proven
algebraically — lives specifically in the leading-digit projection for
b >= 3. The binary case shows what happens when you remove that
projection: you get a perfectly good PRNG, but the algebraic proof of
uniformity becomes either trivial (leading bit) or reduces to the
standard counting argument for counter-mode (all bits).


## 9. What's Genuinely New in the Binary Space

Despite the generator collapsing, the binary Champernowne *as a
mathematical object* opens several doors:

1. **RLE as structural spectroscopy.** Run-length statistics of the bit
   stream depend on v_2(n) — the 2-adic valuation of the monoid
   parameter. This is a genuinely new observable connecting ACM structure
   to information-theoretic measures. The base-10 construction has no
   clean analog.

2. **The epsilon identity.** The sawtooth-secant error in binary IS the
   floating-point epsilon function, not just its cousin. This closes the
   BIDDER <-> SlideRule bridge completely.

3. **The 1-bias as a universal tax.** The persistent 1/(2d) excess of
   1-bits is the cost of positional notation applied to positive
   integers. It exists in every base (leading digit d has frequency
   (d+1-d)/(d*something)) but is maximally stark in binary because the
   "digit" has only one possible value.

4. **Entropy rate as algebraic content.** The Shannon entropy of the bit
   stream measures how far it deviates from random. The deficit =
   information injected by the ACM structure. This is a single scalar
   that captures algebraic content in information-theoretic units.

5. **The boundary theorem splits by position.** In base 10: "all digits
   equal at block boundary." In binary: "positions 1..d-1 balanced,
   position 0 maximally biased." This decomposition by bit position is
   finer-grained and may extend to intermediate bases: which digit
   positions are balanced at the boundary, and which carry leading-digit
   bias?


## 10. Summary Table

| Aspect | Base-10 Champernowne | Binary Champernowne |
|---|---|---|
| Leading-digit uniformity | 1/9 each, exact at boundaries | Trivial (always 1) |
| Sawtooth range | [1.1, 2.0] | [0.5, 1.0) |
| Tooth frequency | Every 10x | Every 2x |
| Running mean | -> 31/20 = 1.55 | -> 3/4 = 0.75 |
| epsilon connection | Analogy (base-10 cousin) | Identity (IS the epsilon function) |
| RLE value | Low (10-valued alphabet) | High (structural fingerprint) |
| 2-adic valuation visible | No | Yes (trailing zeros -> run patterns) |
| Rolling shutter rate | log_10(mu) ~ 0.19 | ~3.32x faster |
| Generator utility | Full (b-1 = 9 symbols) | Degenerate (b-1 = 1 symbol) |
| Uniformity proof character | Non-trivial and distinctive | Trivial for leading bit; per-position for interior bits |
| Natural analysis tools | Digit histograms, heatmaps | RLE, entropy rate, autocorrelation, spectral |


## Verdict

The binary Champernowne of ACMs is a different beast. It **dissolves
the leading-digit engine** that powers BIDDER as a generator, but
**sharpens the mathematical connections** — especially the exact
identification with epsilon and the RLE fingerprinting of 2-adic
structure. It's not a better generator; it's a better lens for the
pure mathematics. The base-10 construction is where the engineering
lives. The base-2 construction is where the number theory is most naked.
