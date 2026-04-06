# Sieve Interference Rings

A polar rendering of **sieve density**: how many monoids nZ+
(for n = 2..N) claim each integer k as an n-prime.

## What it encodes

For each positive integer k, the sieve density is:

    density(k) = |{ n in 2..N : k is an n-prime }|

An integer k is an n-prime when n divides k but n² does not.
So density(k) counts the divisors of k that appear exactly
once in its factorization — divisors n where k/n is not itself
divisible by n.

- **Primes** have density 1. A prime p is only divisible by p
  itself (among n >= 2), so only the monoid pZ+ claims it.
  They're the dimmest points in the image.
- **Highly composite numbers** (12, 24, 36, 60, 120, 360)
  have many divisors, many of which divide them exactly once.
  They're the brightest points. 60 has density 10: claimed by
  {3, 4, 5, 6, 10, 12, 15, 20, 30, 60}.
- **Prime powers** p^a have low density (only n=p^a claims
  them, since every smaller power of p divides them to a
  higher multiplicity). They sit near the primes in brightness.

The image is a continuous map of divisor richness as the
monoids collectively see it. Bright clusters mark integers
with many single-multiplicity divisors. Dark voids mark
integers the monoids mostly ignore.

## The spiral

Integers are laid out on a golden-angle spiral: k maps to
angle k * golden_angle and radius sqrt(k). This gives roughly
equal area per point and avoids the radial-spoke artifacts of
a fixed-step Archimedean spiral.

Brightness encodes sieve density normalized to [0, 1]. The
color ramp runs from deep navy (low density: primes, prime
powers) through red to gold/white (high density: highly
composite numbers).

## Connection to the project

The sieve density at k counts divisors n where k is
irreducible in nZ+. This is the same divisor structure that
drives the epsilon function (ARCS.md) and the compositeness
pressure that shapes the sawtooth between block boundaries.
The epsilon landscape shows where compositeness peaks in
(mantissa, base) space; the interference rings show where it
peaks in integer space. Two views of the same phenomenon, but
inverted: epsilon is highest where primes are most isolated,
while sieve density is highest where composites are richest.

## Script

`sieve_interference_rings.py` — one script, no dependencies
beyond acm_core, numpy, matplotlib. Produces a full view
(k = 1..10,000) and a zoom (k = 1..2,000).
