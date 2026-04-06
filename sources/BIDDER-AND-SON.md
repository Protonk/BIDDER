# Bidder and Son: Two Approaches to Mental Logarithms

Source: W. Pole, F.R.S., "Mental Calculation. A Reminiscence of
the late Mr. G. P. Bidder, Past-President." Paper No. 2486,
Institution of Civil Engineers. Published posthumously from a
memorandum prepared during Bidder's lifetime with his approval.


## The problem

Compute log₁₀(n) to seven or eight decimal places, mentally,
for any positive integer n — including large primes where no
factorization shortcut is available.


## The father: G. P. Bidder (1806–1878)

### Stored constants

The logarithms of nearly all primes under 100, and a few above,
all computed mentally and never written down or looked up in
tables. Additionally, the following correction table:

    log(1.01)    = 0.0043214
    log(1.001)   = 0.00043407
    log(1.0001)  = 0.0000434
    log(1.00001) = 0.0000043

### Method for composite numbers

Factor the target into known primes and sum their logarithms.
The factorization is performed by direct perception — Bidder
could see instantly that 17,861 = 337 × 53, or that
1,659 = 79 × 7 × 3. He described this as natural instinct.

### Method for primes and difficult numbers

Find a nearby composite that factors into known primes,
differing from the target by a small residual. Correct for the
residual using the stored correction table and simple proportion.

The residual should be less than 1/1000 of the number. If no
nearby composite is close enough, multiply the target by a small
known factor to produce one.

### Worked example: log(877)

877 is prime and does not have a convenient neighbor. Bidder
multiplies by 13:

    877 × 13 = 11401 = (609 × 19) + 1

Now the problem decomposes:

    log(600)     = 2.7781512    (known factorization)
    log(19)      = 1.2787536    (memorized)
    correction   = 0.0000381    (for the +1, via proportion)
    ─────────────────────────
    log(11401)   = 4.0569429

    subtract log(13) = 1.1139433

    log(877)     = 2.9429996

The correction for +1 is computed as 0.00043428 / 11.4,
using the log(1.001) entry scaled by proportion.

### Worked example: log(369353)

    369353 = (9 × 41000) + 369 − 16

Bidder first adds a correction for 369/369000 (approximately
1/1000), then subtracts a correction for 16. The composition of
two corrections demonstrates flexibility in choosing the
approach path.

### Character of the method

Each problem is a fresh navigation. The solver looks at the
target, perceives a nearby landmark — a factorable composite —
and walks to it. The art is in choosing which landmark gives
the cleanest path: which helper multiplier, which nearby
composite, which way to split the residual.

The method is powerful when good landmarks exist. It rewards
deep familiarity with the multiplicative structure of the integers
and an intuitive sense for which numbers factor cleanly.


## The son: G. P. Bidder Jr. (1836–1896)

### Stored constants

The logarithms of four primes — 2, 3, 7, and 11 — and the
modulus 0.4343 (= log₁₀ e). Additionally, the logarithms of the
multi-scale correction factors:

    log(1.1)     (known)
    log(1.01)    (known)
    log(1.001)   (known)
    log(1.0001)  (known)
    log(1.00001) (known)

### Method for small numbers

Find m + n where m is a multiple of {2, 3, 7, 11} and n is
small. Then:

    log₁₀(m + n) = log₁₀(m) + log₁₀(1 + n/m)

    log₁₀(1 + n/m) = 0.4343 × [n/m − ½(n/m)² + ⅓(n/m)³ − ...]

A few terms of the series suffice when n/m is small.

### Method for large numbers

Decompose the target as a multi-scale product:

    n = (small factorable core) × (1.001)^a × (1.0001)^b × (1.00001)^c

Each factor accounts for one decimal scale of precision. The
exponent at each scale is determined by how much of the target
remains unexplained by the coarser scales.

The logarithm is then a weighted sum:

    log(n) = log(core) + a·log(1.001) + b·log(1.0001) + c·log(1.00001)

All terms are products of a small integer (the exponent) and a
memorized constant.

### Worked example: log(724871)

    724871 = 72 × (1.001)⁶ × (1.0001)⁷ × (1.00001)^4.5

The logarithm is the sum:

    log(72) + 6·log(1.001) + 7·log(1.0001) + 4.5·log(1.00001)

Result: 5.860261 (six places).

The son notes that the mental strain is much less than it
appears, because each step is a small multiplication and an
addition to a running total.

### Character of the method

Every problem is solved by the same procedure. The solver
imposes a fixed multi-scale coordinate system onto the space of
positive reals and reads off the target's position within it. The
coordinates are the exponents at each scale. The answer is a
weighted sum of those coordinates against memorized constants.

The method is uniform. It does not require perceiving nearby
factorable composites, and it does not depend on the target
being close to a convenient landmark. Prime or composite,
large or small, the procedure is the same.


## Comparison

Both methods decompose a multiplicative problem into additive
steps via the logarithm identity log(a × b) = log(a) + log(b).
Both rely on memorized constants. Both navigate from known
territory to an unknown target.

They differ in how they navigate.

### What is decomposed

The father decomposes the *target* into factors. The factors
are classical primes, or products of classical primes, specific
to the number at hand.

The son decomposes the *space* into scales. The scales are
fixed — they do not depend on the target. The target is
located within the pre-existing grid.

### The role of the residual

For the father, the residual is a local correction applied once,
at the end. It bridges the gap between the nearest factorable
composite and the target. The entire method is organized to
make this residual as small as possible.

For the son, the residual is distributed across all scales. There
is no single correction step. Each scale absorbs its portion of
the discrepancy, and the sum of all contributions constitutes
the answer.

### Dependence on the target's structure

The father's method is sensitive to the target. A number near
a highly factorable composite is easy. A number in a sparse
region of the multiplicative landscape is hard and may require
an indirect approach (the helper multiplier trick).

The son's method is indifferent to the target. The procedure
does not change based on whether the number is prime or
composite, isolated or surrounded by factorable neighbors.

### What must be memorized

The father memorizes many logarithms — nearly all primes
under 100. The method draws on a large library of known
landmarks.

The son memorizes few logarithms — four primes and a handful
of correction constants. The method draws on a small set of
universal reference points.

### Where the difficulty lies

For the father, the difficulty is perception: seeing the factors,
choosing the path, selecting the helper multiplier. The
computation at each step is straightforward (addition of known
values, simple proportion). The challenge is strategic.

For the son, the difficulty is registration: holding a running
total across several scales while computing each contribution.
There is no strategic choice — the procedure is fixed. The
challenge is bookkeeping.

### What each method shares with computation

The father's method resembles table lookup with interpolation.
A large precomputed table (memorized logarithms), a nearest-
entry lookup (find the nearby composite), and a linear
correction for the remainder.

The son's method resembles positional encoding. A fixed set
of basis functions (the multi-scale correction factors), a set of
coefficients (the exponents), and a summation. In base 2, the
correction factors become (1 + 2⁻ᵏ), and multiplication by
them reduces to a shift and an add — the CORDIC algorithm.


## Coda

Both methods were devised independently for the same
problem. The father developed his approach first and used it
to compute eight-place logarithms of arbitrary primes in under
four minutes, mentally. The son learned the general principles
from his father, arrived at his own details independently, and
found them practical for six-place results.

The father considered the power of perceiving factors to be
innate and unteachable. The son considered his own method —
the multi-scale decomposition — to be learnable.

Neither claimed superiority over the other.
