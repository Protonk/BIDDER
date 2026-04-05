# HCH Block Generator

Hilbert-Champernowne-Hyland uniform block generator. A pseudorandom
number generator that achieves exact output uniformity by
construction, not by statistical convergence.

Status: design sketch. Unimplemented. Unreviewed.


## Motivation

Conventional PRNGs (xoshiro, Mersenne Twister, counter-mode AES)
produce output distributions that are statistically close to
uniform. The quality is verified empirically (TestU01, PractRand).
No finite prefix of the output is exactly uniform — it converges.

HCH factors the problem in two. An algebraic substrate provides
exact uniformity. A keyed permutation provides disorder. The
substrate guarantees the distribution; the permutation guarantees
unpredictability. Neither depends on the other.


## Background

### The monoid

For a positive integer n >= 2, the set nZ+ = {n, 2n, 3n, ...} is
a multiplicative monoid. The element n*k is irreducible in nZ+ if
and only if n does not divide k. These irreducibles are the
**n-primes**: multiples of n that are not multiples of n^2.

### The encoding

Fix a base b >= 2 and a depth K >= 1. For each n, list its first
K n-primes and concatenate their base-b representations after a
radix point to form a real number C_b(n). The leading base-b digit
of C_b(n) is the leading base-b digit of n.

### The uniformity guarantee

In base b, the integers in a complete digit block
[b^(d-1), b^d - 1] have their leading base-b digits exactly
equidistributed over {1, ..., b-1}. Each digit appears exactly
b^(d-1) times. This is a consequence of positional notation.

The Champernowne encoding preserves this: the leading digit of
C_b(n) is the leading digit of n. Over a complete digit block,
the output is exactly uniform. The error is zero.


## Construction

### Operating block

Choose a base b >= 2 and a digit-class index d >= 1. The
**operating block** is B_d = {b^(d-1), ..., b^d - 1}. This
block has size (b-1) * b^(d-1). The leading base-b digits of
its elements are exactly uniform over {1, ..., b-1}.

The base b determines the output alphabet size (b-1 symbols).
The digit class d determines the block size and therefore the
generator's period before repetition.

### Keyed permutation

Let pi_K : B_d -> B_d be a keyed bijection over the operating
block, parameterized by a secret key K. This can be any keyed
permutation: a lightweight block cipher at the right width
(PRINCE, SKINNY, Simon/Speck), a Feistel network sized to the
block, or any other PRP construction.

The permutation does not need full cryptographic strength. It
needs to be a good pseudorandom permutation — its output should
be computationally indistinguishable from a random permutation
of B_d. This is a weaker requirement than resistance to
chosen-ciphertext attacks.

### Output

The generator produces a sequence by iterating over B_d in
permuted order:

    for i in B_d:
        n = pi_K(i)
        output the leading base-b digit of n

Since pi_K is a bijection on B_d, and B_d has exactly b^(d-1)
elements with each leading digit, the output stream visits each
symbol in {1, ..., b-1} exactly b^(d-1) times over a full
period. The marginal distribution is exactly uniform at the end
of each period.

Within a period, the distribution follows the same deterministic
sawtooth as the raw ACM source — but the permutation scrambles
the order, so the sawtooth's phase is unpredictable without
knowledge of K.

### Parameters

| Parameter | Controls                    | Example          |
|-----------|-----------------------------|------------------|
| b         | alphabet size (b-1 symbols) | 256 -> 255 syms  |
| d         | period = (b-1) * b^(d-1)   | d=2 -> 65280     |
| K         | which permutation           | 128-bit key      |


## Properties

**Exact uniformity.** The output distribution over {1, ..., b-1}
is exactly uniform at the end of each period. This follows from
counting and does not depend on the key or the permutation.

**Decoupled concerns.** Uniformity is structural (from the
substrate). Unpredictability is computational (from the
permutation). Changing the permutation changes the sequence
order without affecting the distribution. Changing the base
changes the distribution without affecting the security argument.

**Tunable state space.** Larger d gives a longer period and more
room for the permutation. For base 256, d=2 gives a period of
~65K; d=3 gives ~16M; d=4 gives ~4G.

**No rejection sampling.** The output domain is {1, ..., b-1},
which is exactly the set of leading digits. No outputs are
discarded, no cycle-walking is needed.


## What to verify

**Empirical quality.** Does the generator pass BigCrush and
PractRand with a reasonable choice of pi_K? Failure would
indicate the permutation is a poor PRP at the chosen block
size, not a problem with the substrate.

**Performance.** The generator does one block cipher evaluation
per output symbol. Counter-mode AES is the natural comparison.
The question is whether exact uniformity buys anything that
counter-mode AES doesn't already provide in practice.

**Interferometry.** Can the consecutive-sum crispness test
distinguish this generator from a commodity PRNG? If the
permutation is good, the consecutive-sum structure should be
destroyed — the generator should look like numpy, not like the
raw ACM source. If it still looks like the ACM source, the
permutation isn't mixing well enough.


## Open questions

1. **Multi-digit extraction.** The construction extracts only
   the leading digit. The deeper digits of C_b(n) encode the
   irreducible sequence of the monoid nZ+. Can they be used to
   extract additional uniform output per permutation evaluation,
   increasing throughput?

2. **Structure-aware permutation.** The input to pi_K has known
   structure (it's a digit block, not arbitrary). Can a
   permutation exploit this structure to reduce cost without
   sacrificing PRP quality?

3. **Reseeding.** For applications needing forward secrecy or
   stream independence, what is the right rekeying strategy?
   The simplest approach: rekey at each period boundary, where
   the distribution is exactly uniform regardless of the
   previous key.

4. **Composition.** Can HCH blocks at different bases or digit
   classes be composed to build generators over larger or
   non-standard output domains?


## Lineage

- **Hilbert** (c. 1900): introduced the arithmetic congruence
  monoid M_{1,4} = {1, 5, 9, 13, ...} to demonstrate non-unique
  factorization.
- **Champernowne** (1933): constructed a normal number by
  concatenating consecutive integers. The encoding here adapts
  this idea to irreducible elements of ACMs.
- **Hyland** (2026): identified the exact uniformity of leading
  digits in the ACM-Champernowne construction and proposed its
  application to pseudorandom generation.
