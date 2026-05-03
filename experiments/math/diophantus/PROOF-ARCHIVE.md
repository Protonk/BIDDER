# PROOF-ARCHIVE: clause 3″ trigger set — exploration record

This file holds the older / exploratory material from the proof-lift
investigation. The current proof and recommendations live in
`PROOF-LIFT.md`; this is the journey, kept because the journey
informs follow-up work and is part of the epistemic shape of the
investigation.

## Setup (the trajectory framework)

Fix `(b, n, d)` and `W = b^(d-1)`. Write the last two base-`n`
digits of `W` as `(s, r)`:

```
W = (… · n²) + s · n + r,    0 ≤ r, s ≤ n − 1.
```

So `r = W mod n` and `s = ⌊W/n⌋ mod n`. The substrate's per-strip
counts are

```
c_n[k]  = ⌊W/n⌋  + extras_n[k],
c_n²[k] = ⌊W/n²⌋ + extras_n²[k],
```

with `extras_n[k] ∈ {0, 1}` (universal spread bound). The atom
count `c_n[k] − c_n²[k]` is constant in k iff
`extras_n[k] = extras_n²[k]` for all `k ∈ {1, …, b−1}` — clause 3″'s
alignment hypothesis.

**Carry formulation.**

```
extras_n[k]  = [(kr − 1)  mod n  ≥ n − r]
extras_n²[k] = [(kr′ − 1) mod n² ≥ n² − r′]
```

with `r′ = W mod n² = r + s · n`.

**Trajectory framework.** Define

```
a_k := (kr − 1) mod n            (low base-n digit of (kr′ − 1))
β_k := ⌊(kr′ − 1)/n⌋ mod n       (high base-n digit of (kr′ − 1))
```

so `(a_k, β_k)` are the last two base-`n` digits of `kr′ − 1`.

**Alignment region A ⊂ (Z/n)².** Working out the indicator algebra:
clause 3″ fires iff for every `k ∈ {1, …, b−1}`:

```
a_k ≥ n − r   ⟹   β_k ∈ {n − s − 1, …, n − 1}     (size s+1)
a_k <  n − r  ⟹   β_k ∈ {0, …, n − s − 1}          (size n−s)
```

Verified 27/27 in the b = 10 sweep by `trajectory.py`.

This trajectory framework was the entry point. It expresses the
alignment as a discrete-dynamical question on `(Z/n)²`. The
structural theorem in `PROOF-LIFT.md` reformulates this on
subsets of `{1, …, b−1}`, which is what made the proof tractable.

## What's already known (clauses 3 / 3′)

The substrate's `c_n` is constant in k iff there are no `extras_n` —
equivalently, the rotation `{kr/n}` for k=1..b-1 stays in
`[0, (n−r)/n]`. By the three-distance theorem this happens iff
`(b − 1)·r ≤ n − r`, i.e., `b · r ≤ n`. So:

- **`br ≤ n`**: c_n constant ⟹ clause 3 (Family E proper, when
  `n ∈ [b^(d-1), ⌊(b^d−1)/(b−1)⌋]`) or clause 3′ (Generalised
  Family E, otherwise).
- **`br > n`**: c_n has at least one extra. Clause 3″ is the
  question of when the extras of c_n are *cancelled* by the
  extras of c_n².

Clause 3″ is therefore strictly disjoint from clauses 3 and 3′.

## Reformulation as a base-coupling problem

Let `r′ = W mod n² = r + s · n`. Clause 3″'s alignment is equivalent
to: for `k = 1, …, b − 1`, the integer `kr′ − 1` has its last two
base-`n` digits in the aligned region A.

Equivalently: the orbit `{k · b^(d-1) − 1 mod n²}_{k=1..b-1}` lies
in a specific subset of `Z/n²` — the "aligned coset of length
`b − 1`."

This is a **base-`b` × base-`n` interaction**.

## Empirical exploration of simple predicates

`predicate_search.py` tested candidate closed-form predicates against
a wider sweep (b = 10, n ≤ 400, d ≤ 8) containing 51
`n²`-cancellation cells:

| candidate | TP | FN | FP | precision | recall |
|---|---|---|---|---|---|
| `r = s` | 20 | 31 | 24 | 0.45 | 0.39 |
| `(n+1) ∣ (W − ⌊W/n²⌋)` *(equivalent to r = s)* | 20 | 31 | 24 | 0.45 | 0.39 |
| `r = s ∧ br > n` | 20 | 31 | 17 | 0.54 | 0.39 |
| `\|r − s\| ≤ 1` | 31 | 20 | 465 | 0.06 | 0.61 |
| `r = s ∧ ¬smooth ∧ ¬Family-E` | 20 | 31 | 24 | 0.45 | 0.39 |

**No simple candidate works.** The most "clean" predicate (`r = s`)
covers fewer than 40% of the alignment cells AND admits 24 false
positives (cells where r=s but spread > 0).

False negatives — cells where alignment fires despite `r ≠ s` —
include `(n=83, d=5)` r-s=3, `(n=118, d=5)` r-s=4, `(n=146, d=5)`
r-s=4. These fire because the trajectory threads the aligned
region anyway, despite the `r ≠ s` offset.

### Algebraic identity

```
r − s ≡ W − ⌊W/n²⌋ (mod n + 1)
```

Direct: `W = ns + r + n²·⌊W/n²⌋`, so
`W − ⌊W/n²⌋ ≡ ns + r − ⌊W/n²⌋ ≡ −s + r (mod n+1)` using
`n ≡ −1, n² ≡ 1 (mod n+1)`. Useful for testing `r = s` candidates
but doesn't translate to an alignment characterisation.

### What the cells actually look like

```
   n   d     r       s    r=s?   r−s   pattern
  19   3     5       5    YES      0   001000100
  26   4    12      12    YES      0   010101010
  36   4    28      27    no       1   111011101
  39   4    25      25    YES      0   101101101
  49   4    20      20    YES      0   010100101
  99   4    10      10    YES      0   000000001
  83   5    40      37    no       3   010101010
 118   5    88      84    no       4   110111011
 124   5    80      80    YES      0   101101101
 136   5    72      73    no      −1   101010101
 146   5    72      68    no       4   010101010
 195   5    55      51    no       4   001000100
 199   5    50      50    YES      0   001000100
  98   6    40      40    YES      0   010100101
 115   6    65      64    no       1   101010110
 155   6    25      25    YES      0   000001000
 172   6    68      65    no       3   010010100
 199   6   102     104    no      −2   101010101
  43   7    35      35    YES      0   111101111
  73   7    46      47    no      −1   101101101
  79   7    18      18    YES      0   000100010
  97   7    27      27    YES      0   001000100
 134   7    92      92    YES      0   110110110
 137   7    37      38    no      −1   001000100
 155   7    95      96    no      −1   101101011
 187   7   111     111    YES      0   101011010
 198   7   100     100    YES      0   101010101
```

Patterns are diverse (`001000100`, `010101010`, `111011101`,
`000000001`, ...) and the same pattern occurs for cells with very
different `(r, s)`. The alignment isn't picking out a single
trajectory shape; it's selecting `(b, n, d)` whose trajectory
threads the aligned region.

## What I tried that didn't work

- **`r = s`**: necessary in some cells, sufficient in none.
  31 FN, 24 FP across the b = 10, n ≤ 400, d ≤ 8 sweep.
- **`|r − s| ≤ 1`**: better recall, worse precision (465 FP).
- **`r = s ∧ br > n`**: same recall as `r = s`, slightly fewer FPs
  (because GFE-overlap is removed); doesn't close the case.
- **`gcd(r, n) = gcd(s, n) = 1`**: many cells satisfy, many cells
  satisfy and don't align. Not a clean predicate.
- **Periodicity-of-trajectory tests**: trajectories are diverse;
  don't reduce to a single periodicity class.

These are the obvious-first algebraic attempts. None lands. The
key insight that broke the impasse: stop looking for a predicate on
`(r, s)` directly and instead reformulate as the Beatty-pair
coincidence on subsets of `{1, …, b−1}`. That gave the structural
theorem.

## Investigation A: the j-ladder of necessary conditions (full)

The Beatty inequality `(jn) mod r ≥ ⌈jr/(n+1)⌉` for `j = 1..M`
factors into a chain of conditions C_1, C_2, …, C_M.

**C_1 (proved).** `r ∤ n`. Proof: `⌈r/(n+1)⌉ = 1` for `1 ≤ r ≤ n`,
so the j = 1 inequality reduces to `n mod r ≥ 1`.

**C_2 (proved, case-split).**
- If `2r ≤ n+1`: `r ∤ 2n`. (For odd r, equivalent to C_1; for even
  r, strictly stronger.)
- If `2r > n+1`: `2n mod r ≥ 2`.

**C_3 (proved, three-case-split).**
- If `3r ≤ n+1`: `r ∤ 3n`.
- If `n+1 < 3r ≤ 2(n+1)`: `3n mod r ≥ 2`.
- If `3r > 2(n+1)`: `3n mod r ≥ 3`.

**General C_j.** With `k_j = ⌈jr/(n+1)⌉`, the condition is
`(jn) mod r ≥ k_j`. The threshold `k_j` increases by 1 each time
`j` crosses a multiple of `(n+1)/r`.

### Empirical observation in the substrate context

In the b = 10, n ≤ 5000, d ≤ 14 substrate-context sweep with r = s,
n² > W, M ≥ 1: every cell either fails C_1 (i.e., r | n) or passes
all of C_1, …, C_M. **Zero cells fail first at j > 1.**

In the **decoupled** sweep (just (n, r) with r ∤ n, no substrate
constraint, j up to 20), j > 1 failures abound: 478 (n, r) pairs
first fail at j = 2, 680 at j = 3, etc.

The contrast pinpoints the mechanism: the substrate constraint
`W = r(n+1) = b^(d-1)` (i.e., `r(n+1)` must be a power of b)
restricts (n, r) tightly enough that the j-ladder collapses to its
j = 1 element. This is the empirical content of Conjecture A.

## Earlier framings of the open question

Pre-theorem framing: *"what (b, n, d) make the orbit
`{k · b^(d-1) − 1 mod n²}_{k=1..b−1}` lie in a specific aligned
subset of `Z/n²`?"* — preserved here for the historical record.
The structural theorem (in `PROOF-LIFT.md`) subsumes this framing
on the n² > W sub-locus by reducing the alignment to a Beatty-pair
coincidence on subsets of `{1, …, b−1}`.

## Sharper outflows considered (proposals before structural proof)

These were the proposed paths before the structural theorem landed.
Outflow A is what was executed and produced the structural theorem
plus the Beatty-reduction lemma. B and C are still potential
follow-ups.

**Outflow A (executed).** Subset characterisation for n² > W. The
n² > W cells form a sub-locus where `r′ = W` exactly and the
alignment condition simplifies. This produced the structural
theorem.

**Outflow B (potential).** Trajectory-density theorem. Rather than
a closed form, prove that the asymptotic density of n²-cancellation
cells in `(b, n, d)` space is `Θ(1/log)` or similar. Achievable
via Weyl-sum machinery on the orbit `{k · b^(d-1) mod n²}`.
Estimated cost: 2–3 weeks. Output: an asymptotic density theorem.

**Outflow C (potential negative result).** Prove that the
closed-form characterisation is **not first-order expressible** in
`(b, n, d)` over Presburger arithmetic. Useful as a stop-loss if
the closed form provably can't be written in elementary form.
Estimated cost: 2 weeks to 2 months.

## n² ≤ W sub-locus

For n² ≤ W (1205 cells in the swept range; 34 spread-zero cells
outside smooth and Family E), multiples of n² may appear more than
once per strip. The structural theorem generalises in spirit but
its statement requires multi-multiplicity bookkeeping:
`extras_n²[k]` is no longer a 0/1 indicator but a count, and the
"alignment" condition becomes a multiset coincidence rather than
a set coincidence. Out of scope; natural follow-up after the
n² > W Beatty-pair coincidence is characterised.
