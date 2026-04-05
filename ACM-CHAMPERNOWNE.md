# ACM-Champernowne Process

## Origin

This construction emerged from a conversation about even and odd integers
as subgroups. The even integers form a subgroup under addition (kernel of
ℤ → ℤ/2ℤ); the odds do not (they lack the identity). This asymmetry led
to the question: what if the only numbers that existed were even?

The answer: multiples of 4 become the new "composites," and {2, 6, 10, 14, ...}
become the new "primes." Unique factorization immediately fails:
36 = 2 × 18 = 6 × 6.

## Construction

**n-primality.** For each positive integer n ≥ 1, define the multiplicative
monoid nℤ⁺ = {n, 2n, 3n, ...}. The irreducible elements of this monoid
are called *n-primes*.

**n-prime criterion.** The element n·k is n-prime if and only if n does
not divide k. Equivalently, the n-primes are multiples of n that are not
multiples of n².

For n = 1, this recovers the ordinary primes (with the special case that
1-prime testing requires standard primality checking).

**The square boundary.** The first n-composite is always n² = n·n. The
first n−1 n-primes are {n, 2n, ..., (n−1)n}, all strictly below n². So
n² is the resolution threshold of n-primality.

**n-Champernowne real.** Given the first K n-primes p₁, ..., p_K,
concatenate their decimal representations after "1." to form a real:

| n | First 5 n-primes     | n-Champernowne real |
|---|----------------------|---------------------|
| 1 | 2, 3, 5, 7, 11      | 1.235711            |
| 2 | 2, 6, 10, 14, 18    | 1.26101418          |
| 3 | 3, 6, 12, 15, 21    | 1.36121521          |
| 4 | 4, 8, 12, 20, 24    | 1.48122024          |
| 5 | 5, 10, 15, 20, 30   | 1.51015203          |
| 6 | 6, 12, 18, 24, 30   | 1.61218243          |
| 7 | 7, 14, 21, 28, 42   | 1.71421284          |
| 8 | 8, 16, 24, 32, 40   | 1.81624324          |
| 9 | 9, 18, 27, 36, 45   | 1.91827365          |

## Connection to Arithmetic Congruence Monoids

The monoid nℤ⁺ ∪ {1} is denoted M_{n,n} in the literature on non-unique
factorization theory. This is a well-studied object:

- **Hilbert (c. 1900)** used M_{1,4} = {1, 5, 9, 13, 17, 21, 25, ...} to
  demonstrate non-unique factorization: 441 = 9 × 49 = 21².
- **James and Niven (1954)** proved that for each modulus, exactly one
  congruence monoid admits unique factorization.
- **Geroldinger and Halter-Koch (2004)** developed the general theory of
  congruence monoids in Dedekind domains.
- **Baginski and Chapman** wrote the modern survey classifying all ACMs into
  regular, local, and global types.

The key invariants studied in this literature — elasticity, sets of lengths,
catenary degree — measure how badly unique factorization fails. Our
contribution is the Champernowne encoding, which turns the algebraic
structure into a real-valued signal amenable to statistical and harmonic
analysis.

## The Sieve Table

Dividing each n-prime by n reveals the underlying sieve. Row n is the
positive integers with every multiple of n deleted:

| n | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 1 |  2  |  3  |  5  |  7  | 11  | 13  | 17  | 19  | 23  |
| 2 |  1  |  3  |  5  |  7  |  9  | 11  | 13  | 15  | 17  |
| 3 |  1  |  2  |  4  |  5  |  7  |  8  | 10  | 11  | 13  |
| 4 |  1  |  2  |  3  |  5  |  6  |  7  |  9  | 10  | 11  |
| 5 |  1  |  2  |  3  |  4  |  6  |  7  |  8  |  9  | 11  |
| ...| ... | ... | ... | ... | ... | ... | ... | ... | ... |

Row 1 is the only row that applies further filtering (primality testing)
beyond the single deletion rule. All other rows accept all survivors.

## What Is New Here

The ACM literature studies the algebraic structure of non-unique factorization.
The Champernowne encoding is a bridge to:

1. **Significand analysis.** The first-digit distribution of n-Champernowne
   reals is exactly uniform (1/9 each), not Benford.

2. **Addition vs. multiplication.** Multiplying n-Champernowne reals
   converges to Benford in ~10 operations. Adding them produces a rolling
   shutter effect that never converges.

3. **The correction function ε.** The sawtooth shape of ln(n-Champernowne)
   is ln(1+m) where m is the base-10 mantissa, connecting to the floating-point
   residual ε(m) = log₂(1+m) − m from the SlideRule project.

4. **Compositeness damage.** The ε-bump (error of the linear approximation
   of ln(1+m)) peaks at the mantissa midpoint (~0.505), where numbers have
   the richest factorization structure. This may serve as a base-independent
   scalar measure of compositeness pressure.
