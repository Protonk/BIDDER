# EXP04 — random-subset control: the survivor filter is distinguishable

EXP01–03 characterised δ = C_Bundle − C_Surv but couldn't separate
"the survivor filter has signature" from "any 37%-thinning produces
this signature." The cabinet's Two Tongues curiosity asked the
question directly: *does the structured filter behave like a
uniform-random thinning, or is the L1 profile just robust to
sub-sampling?*

This experiment runs the control: pick 50 random 1338-of-3600 atom
subsets (preserving bundle read-order), compute their δ-signatures,
compare to the survivor's. Result: the survivor filter is
significantly different from random thinning at z = +2.2 to +2.5.
The previous "L1-tracking is the whole story" reading needs
sharpening — the L1-tracking story relative to *random* extends, but
the survivor filter imprints something *beyond* random.

## Setup

Same panel parameters: `[2, 10], k = 400`. For each of 50 random
seeds, sample 1338 of the 3600 bundle atoms uniformly without
replacement, sort by their original bundle position (preserving
order), build `C_Random` as their digit concatenation, compute
`δ_random = C_Bundle − C_Random`, and record the digit-frequency
signature of `δ_random`'s overlap region.

Compare to `δ_survivor`'s overlap-region signature (the EXP01
numbers) on the same observables.

## The numbers

```
                    survivor      random mean ± std       z-score
overlap length      4,894         4,784 ± 17
L1 from uniform     0.1063        0.0676 ± 0.0175         +2.21
χ² (9 dof)         95.38         37.50 ± 22.88           +2.53

per-digit comparison:
  digit  survivor freq   random mean ± std    z
    0      0.1293          0.1099 ± 0.0101    +1.92
    1      0.0938          0.0978 ± 0.0060    −0.67
    2      0.0889          0.0963 ± 0.0067    −1.11
    3      0.0838          0.0964 ± 0.0061    −2.07
    4      0.0936          0.0977 ± 0.0050    −0.83
    5      0.0946          0.0980 ± 0.0056    −0.61
    6      0.0964          0.0957 ± 0.0059    +0.12
    7      0.0991          0.0977 ± 0.0059    +0.24
    8      0.0966          0.1007 ± 0.0080    −0.51
    9      0.1238          0.1097 ± 0.0108    +1.31
```

## Reading

### 1. Random thinning *also* produces a borrow signature, just smaller

Random subsets give `L1 = 0.068` (non-zero). Their digit-0 frequency
sits at `0.110` (vs uniform `0.100`), digit-9 at `0.110`. So the
"0-and-9 spike" identified in EXP01 is a *generic feature of the
subtract-two-digit-streams operation*, not specific to the survivor
filter. EXP01 had no way to tell — the random-subset baseline didn't
exist yet.

### 2. The survivor's signature is significantly larger than random

Both globally (L1 z = +2.21, χ² z = +2.53) and per-digit (digit 0 at
z = +1.92, just under the 2σ threshold; digit 3 at z = −2.07; digit 9
at z = +1.31). The survivor filter pushes δ *further* from uniform
than a random subset does, particularly in the borrow-signature
digits (0 and 9 over-represented relative to random).

### 3. Digits 3 and 4 are *suppressed* in survivor relative to random

This is unexpected: random subsets distribute their digit content
evenly, but the survivor filter specifically pushes digits 3 and 4
*down* (and 0 and 9 *up*). The mechanism is presumably: survivors
preferentially have certain leading-digit profiles (primes in window,
plus T_B_low cofactor-multiples — see survivors/EXP14-FINDINGS.md),
and that specific profile, when subtracted from the bundle, produces
specific borrow patterns favouring some digit residues over others.

The `(3, 9)` and `(5, 1)` pairs were *under*-represented in EXP03's
digram analysis. That result is consistent with the per-digit
suppression of 3 here.

### 4. The cabinet curiosity gets a tentative sharpening

The cabinet's Two Tongues entry framed the open question as:

> *the structured filter behaves like a uniform-random sub-sample.
> Or the leading-digit profile is robust enough that even
> highly-structured sub-sampling preserves it. Or both.*

At this one panel, the first option is mildly disfavoured: the
survivor's δ-overlap signature differs from random's at z = +2.21 —
notable but not overwhelming for a single-panel observation, and
the test is on δ-overlap digits rather than the running L1 in the
Two Tongues plot itself. The second option (robustness) partially
survives: random thinning ALSO produces a borrow signature; the
survivor's signature is the random-thinning signature *plus* a
~2σ excess. EXP05 then tests whether this excess generalises across
panels.

So the tentative answer is: the L1-tracking property is *partly*
generic (random thinning matches the bundle's L1 too, modulo the
random's own borrow-induced excess) and *partly* survivor-specific
at this panel — pending the panel-sweep test that follows.

## What this combines with EXP01–03

```
EXP01 (single-digit):   δ has borrow signature.
                        Did not separate filter from random.
EXP02 (continued frac): δ is generic by every CF metric.
                        Did not separate filter from random.
EXP03 (digrams):        Pair correlations have weak residual,
                        χ² 110 vs bundle's 237.
EXP04 (random control): Survivor signature is z = +2.5 from random.
                        Filter is detectably specific at digit level.
```

The transducer note's claim that *δ characterises the operation, not
the relation* turns out to be partly right and partly wrong. The
operation produces a generic signature for any subtraction; the
relation imprints additional content beyond that signature; the
combined δ is the sum of operation + relation. EXP01 measured the
sum; EXP04 separates the two by adding a baseline.

The user's conservation intuition — *if mostly destructive, residual
content has to land somewhere* — is now empirically anchored by two
observations:
- Pair correlations carry residual (EXP03, χ² = 110)
- Single-digit signature carries residual *relative to random
  baseline* (EXP04, z = +2.2)

## What this opens

- **Mechanism for the digit-3 suppression.** Why does the survivor
  filter specifically push digit 3 *down* (z = −2.07)? The T_B_low
  decomposition from survivors/EXP14 might predict this — survivors
  are dominated by `c = d · m` with `d ∈ window, m < n_0`, and the
  multiset of those products at our parameters might over-represent
  certain leading digits in a way that propagates through subtraction.
  A direct calculation of survivor leading-digit frequencies (vs
  random) at EXP14's stratification is the natural follow-up.

- **Parameter sweep.** Does the z-score scale with `(n_0, n_1, k)`?
  If z is invariant or grows with parameters, the survivor-specific
  signature is robust; if it shrinks at larger parameters, the
  signal is finite-K only.

- **Structured-control hierarchy.** The random-subset control is
  *one* baseline. Other natural controls: (a) every-third-atom
  thinning (preserves order, more deterministic); (b) primes-only
  subset (atoms whose `m` is prime); (c) doubleton-only subset
  (atoms paired exactly twice). Each gives a different baseline; the
  survivor's z-score relative to each tells us *what kind* of filter
  it most resembles.

## Files

- `exp04_random_subset_control.py` — script.
- `exp04_random_subset_control.png` — four-panel figure: digit
  frequency comparison, L1 distribution histogram, per-digit
  z-scores, statistics table.
