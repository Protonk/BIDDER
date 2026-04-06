# Simple Epsilon

## The Experiment

For n = 1..N, compute the binary Champernowne real C_2(n) using the
first K n-primes of monoid n. Plot log_2(C_2(n)) vs n — the binary
sawtooth. Within each bit-length class, extract the base-2 mantissa
m = n/2^d and compare the sawtooth to the literal epsilon function
epsilon(m) = log_2(1+m) - m.

Three panels:
1. The raw sawtooth: log_2(C_2(n)) vs n
2. The sawtooth residual above its secant, overlaid with epsilon(m)
3. The second-order residual: sawtooth - secant - epsilon


## The Prediction

**The second-order residual will be a descending staircase.**

Positive, roughly flat within each tooth, halving at each tooth
boundary. The staircase walks down toward zero as bit-length
increases.

The mechanism: C_2(n) = 1 + n/2^d + (second entry)/2^(d+d_2) + ...

The first term gives log_2(1+m) exactly — pure positional arithmetic.
The second entry (approximately 2n for most monoids) adds a correction
of order 2n/2^(2d+1) ~ 1/2^d. In log_2 space, this is a positive
bump of size ~1/(2^d * ln 2). When d increases by 1, the bump halves.


## What This Would Mean

If the staircase prediction holds, the epsilon identity is **real but
structurally trivial.**

It holds because concatenation front-loads information. The first
entry of the binary Champernowne real IS n. And log_2(1+m) is what
you get from writing any positive integer in binary — it's the
shape of positional notation itself, not a property of ACMs.

The later entries carry the ACM structure: the sieve, the monoid
parameter, the factorization. But they are exponentially buried
beneath the first entry. The second entry contributes at order 1/2^d.
The third at order 1/2^(2d). The algebra is suppressed by the same
mechanism that makes floating-point arithmetic work — low-order bits
don't change the leading behavior.

**The epsilon identity tells us about how we write numbers, not about
which numbers we write.**

The ACM algebra is invisible in the Champernowne real's scalar value.
It lives in the stream's statistics — run lengths (experiment 1),
boundary patterns (experiment 3), bit balance (experiment 2). The
scalar log_2(C_2(n)) is too coarse a measurement to see the algebra.


## What Would Prove This Wrong

If the second-order residual has **structure beyond a decaying
staircase** — sub-teeth, monoid-dependent patterns, dependence on
n's factorization — then the algebra is reaching through the
exponential suppression to shape the Champernowne real itself. That
would mean the epsilon identity is deeper than positional notation.
The ACM structure would be imprinting on the real's value, not just
on the stream's statistics.

Specific things to watch for:
- Sub-teeth at n ~ 2^(d+1)/3 (where the third n-prime crosses a
  power of 2 and gains a bit)
- Different residual levels for n=2 vs n=3 (the only monoid where
  the second n-prime is 3n rather than 2n)
- n=1 behaving anomalously (ordinary primes have closely-packed
  early entries, violating the exponential separation)
- Any dependence of the staircase height on n's factorization
  within a tooth
