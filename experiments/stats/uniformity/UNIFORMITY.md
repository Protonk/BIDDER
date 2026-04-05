# A Uniform Digit Generator from Irreducible Elements

## Setup

Take the positive integers and pick a modulus n >= 2. Keep only the
multiples of n: the set nZ+ = {n, 2n, 3n, 4n, ...}. This is a
multiplicative monoid — closed under multiplication, with no inverses
and no unit (n * 1 = n, but 1 is not in the set).

Some elements of nZ+ factor within the monoid, and some do not. The
element n*k factors as a product of two smaller elements of nZ+ only
if k itself is divisible by n, because both factors must be multiples
of n. So:

- n*k is **irreducible in nZ+** if and only if n does not divide k.
- n*k is **reducible in nZ+** if and only if n divides k (i.e., n*k
  is a multiple of n^2).

Call the irreducibles the **n-primes**. They are exactly the multiples
of n that are not multiples of n^2.

### Examples

For n = 2, the monoid is {2, 4, 6, 8, 10, ...}. The 2-primes are the
multiples of 2 that are not multiples of 4: {2, 6, 10, 14, 18, 22, ...}.
The element 36 is reducible: 36 = 2 * 18 = 6 * 6 (and the factorization
is not unique — this is typical).

For n = 5, the monoid is {5, 10, 15, 20, 25, ...}. The 5-primes are
multiples of 5 that are not multiples of 25: {5, 10, 15, 20, 30, 35, ...}.
The value 25 = 5 * 5 is the first reducible element.

In general, the first n-1 n-primes are {n, 2n, 3n, ..., (n-1)n}, all
below n^2. The value n^2 is always the first reducible element.


## The Champernowne encoding

Fix a base b >= 2. Given n, list its first K n-primes p_1, p_2, ..., p_K.
Concatenate their base-b representations after a radix point to form
a real number:

    C_b(n) = 1 . p_1 p_2 p_3 ... p_K       (in base b)

In base 10 with K = 5:

    C(2) = 1.26101418      (2-primes: 2, 6, 10, 14, 18)
    C(7) = 1.714212842     (7-primes: 7, 14, 21, 28, 42)

The encoding packs two kinds of information into one scalar: the
number-theoretic content (which elements are irreducible) and the
typographic cost (how many base-b digits each element requires).


## Exact uniformity of leading digits

The first digit after the radix point in C_b(n) is the leading
base-b digit of the first n-prime. The first n-prime is always n
itself (since 1 * n = n and 1 is never divisible by n >= 2).

So the leading digit of C_b(n) is the leading base-b digit of n.

Now count. In any base b, the integers in a complete digit block
[b^(d-1), b^d - 1] have their leading digits exactly equidistributed
over {1, ..., b-1}. Each digit appears exactly b^(d-1) times. This is
a consequence of positional notation: the leading digit of n partitions
each digit block into b-1 equal sub-blocks.

Therefore: **the leading digits of C_b(n), taken over any complete
digit block of n values, are exactly uniform over {1, ..., b-1}
with probability 1/(b-1) each.**

This is exact. It holds for any K >= 1 and any base b >= 2.


## The generator

To produce a stream of digits uniform over {1, ..., b-1} in base b:

1. Choose K >= 1 (the number of n-primes per encoding).
2. For n = 1, 2, 3, ..., compute C_b(n).
3. Extract the leading base-b digit.

Over any complete digit block [b^(d-1), b^d - 1], the output is
exactly uniform. The longer the sequence, the more complete digit
blocks it spans, and the closer the cumulative distribution is to
exact uniformity. At each block boundary the distribution is perfect;
between boundaries it converges toward perfect as the partial block
becomes a smaller fraction of the total.

The modulus n, the count K, and the base b are all free parameters.
The uniformity depends on none of them. It depends only on the fact
that the first n-prime is always n, and that leading digits of
consecutive integers are equidistributed in any positional base.


## Precision

The encoding C_b(n) is a real number with a total digit length
determined by K and the sizes of the n-primes. Increasing K adds
more irreducible elements to the encoding, extending the fractional
part. The leading-digit uniformity is independent of K, but the
full digit string of C_b(n) carries additional structure that
depends on the sieve and the base. The generator's uniformity
guarantee applies to the leading digit; the deeper digits encode
the irreducible sequence of the monoid nZ+.
