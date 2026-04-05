# Boundary Stitch

## What We're Doing

Extract a window of bits around every entry boundary in the binary
Champernowne stream. Stack these windows vertically to form an image.
Each row is one boundary. Columns are bit positions relative to the
join point (negative = trailing bits of outgoing entry, positive =
leading bits of incoming entry).

Do this for several values of n, side by side.


## What We Expect

**The v_2 barcode.** For n = 2^m, every n-prime is divisible by 2^m,
so the last m bits of every entry are 0. These guaranteed trailing
zeros should appear as m solid dark columns immediately to the left
of the join. The join itself (column 0, the leading 1 of the next
entry) is a solid bright column. The pattern is:

```
n = 2   (v_2 = 1):   ?  ?  ?  0 | 1  ?  ?  ?
n = 4   (v_2 = 2):   ?  ?  0  0 | 1  ?  ?  ?
n = 8   (v_2 = 3):   ?  0  0  0 | 1  ?  ?  ?
n = 16  (v_2 = 4):   0  0  0  0 | 1  ?  ?  ?
```

The stripe width IS v_2(n). This should be immediately visible as a
physical barcode embedded in the image.

For mixed n (e.g., n = 12, v_2 = 2): two guaranteed dark columns,
but the columns further left are noisy (they depend on the specific
n-prime, not just on n).

For odd n (v_2 = 0): no guaranteed pattern. The column immediately
left of the join is sometimes dark, sometimes bright. The barcode
dissolves into noise.


## What We Hope

**Self-synchronization.** If the boundary pattern is distinctive
enough — strong vertical stripes against a noisy background — then
a receiver could detect boundaries from the stream alone, without
knowing where entries begin. This is the comma-character question
from DISPARITY.md. The 8b/10b code reserves its longest run (5
identical bits) exclusively for comma characters, making them
uniquely detectable. Our question: does v_2(n) create a natural
comma — a run-length pattern that appears only at boundaries and
never in the interior of an entry?

For powers of 2 with large v_2, this seems plausible. A run of 8
zeros (for n = 256) is rare in a ~50/50 bit stream. If such runs
occur almost exclusively at boundaries, the stream is
self-synchronizing. If they also occur frequently in entry interiors
(from n-primes that happen to have internal zero runs), then the
signal is contaminated and boundary detection requires more context.


## What Might Surprise Us

**Structure on the RIGHT side of the join.** The left side (trailing
bits) is where the v_2 barcode lives. The right side (leading bits
of the incoming entry) should be... what? Pure noise?

Maybe not. Consider: the n-primes are enumerated in order. Consecutive
n-primes nk and n(k+1) — or nk and n(k+2) when k+1 is a multiple
of n — differ by n or 2n. For small n relative to the n-prime's
magnitude, consecutive entries have similar values and therefore
similar leading bits. The MSB is always 1 (column 0). But columns
+1, +2, +3 (the next most significant bits) reflect where the
n-prime sits within its bit-length class.

Early in a bit-length class (n-primes just above 2^(d-1)), the
leading bits are 10000... Late in the class (n-primes just below
2^d), the leading bits are 11111... If the stitch image covers
boundaries across an entire bit-length class, the right-side columns
should show a **gradient** — a smooth transition from dark (0) to
bright (1) as n-primes progress through the class.

This gradient would mean boundaries carry directional information.
You could tell "early" boundaries from "late" ones. The left side
of the join encodes v_2(n) (a property of the monoid). The right
side encodes position within the bit-length class (a property of
the specific n-prime). The boundary is a two-faced object: algebraic
on the left, arithmetic on the right.

**Bit-length transitions.** When consecutive n-primes cross a
power-of-2 boundary (e.g., the outgoing entry has 10 bits but the
incoming entry has 11 bits), the window is asymmetric — different
numbers of "real" bits on each side. These transitions create
anomalous rows in the stitch image. They might appear as a
horizontal band of disrupted pattern. How frequent are they? For
monoid n, the spacing between bit-length transitions is ~2^(d-1)/n
entries, so transitions are rare for small n (many entries per class)
and frequent for large n (few entries per class). The disruption
rate is itself a function of n.

**Correlation across the join.** The trailing bits of entry k and the
leading bits of entry k+1 come from different n-primes, but those
n-primes are close in value (they differ by ~n). If n is small
relative to the n-primes, then nk and n(k+2) share most of their
leading bits. This means the RIGHT side of boundary k is correlated
with the RIGHT side of boundary k+1 — the gradients are smooth. But
the LEFT side of boundary k (trailing bits of nk) is NOT correlated
with the LEFT side of boundary k+1 (trailing bits of n(k+2)) — the
trailing bits depend on the specific factorization of k and k+2.

So the stitch image should have smooth vertical gradients on the
right and noisy texture on the left (beyond the v_2 guaranteed
zeros). The join is the frontier between order and disorder, and
which side is which depends on whether you're looking at leading
or trailing bits.
