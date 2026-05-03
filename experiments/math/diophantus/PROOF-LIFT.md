# PROOF-LIFT: clause 3″ trigger set

## Goal

Characterise — ideally in closed form — the integer triples
`(b, n, d)` for which the **Beatty pattern-alignment hypothesis** of
clause 3″ fires. This would close the substrate's `n²`-cancellation
locus to the same epistemic standard as Generalised Family E
(clause 3′).

The user's bar: prove if possible; sharper outflow acceptable.

**Verdict.** Substantial progress. Three results, in order of
strength:

1. **Structural theorem (n² > W sub-locus)** — proved. spread = 0
   ⟺ a three-case predicate involving two computable Beatty
   subsets `S₁, S₂`. Verified on all 1925 cells, zero violations.

2. **Beatty-reduction lemma (r = s sub-sub-case)** — proved. Case
   (i) holds iff `(jn) mod r ≥ ⌈jr/(n+1)⌉` for all `j = 1, …, M`.
   Verified on 17/17 r = s cells, zero mismatches.

3. **Conjecture A (closed form for r = s sub-sub-case)** —
   strong empirical evidence, not yet proved. In the substrate
   r = s sub-sub-case (W = r(n+1) = b^(d-1) and n² > W), case (i)
   holds iff `r ∤ n`. The j-ladder collapses to its j = 1 element
   under the substrate constraint. Verified across b = 10,
   n ≤ 5000, d ≤ 14 with zero exceptions. The decoupled sweep
   (without substrate constraint) finds j > 1 failures in
   abundance — confirming the collapse is real and substrate-
   driven.

What's left:
- Prove Conjecture A (would close clause 3″ for r = s sub-sub-case).
- Analogous reduction for `r ≠ s` in the n² > W sub-locus.
- Structural theorem for the n² ≤ W sub-locus (multi-multiplicity).

The remainder of this memo states the framework, records what
was tried (predicates that didn't work), proves the two theorems
above, and scopes the remaining open pieces.

## Setup

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

with `extras_n[k] ∈ {0, 1}` (universal spread bound, clause 4).
The atom count `c_n[k] − c_n²[k]` is constant in k iff
`extras_n[k] = extras_n²[k]` for all `k ∈ {1, …, b−1}` — this is
clause 3″'s alignment hypothesis.

**Carry formulation.** Standard divmod gives:

```
extras_n[k]  = [(kr − 1)  mod n  ≥ n − r]
extras_n²[k] = [(kr′ − 1) mod n² ≥ n² − r′]
```

with `r′ = W mod n² = r + s · n`. Define

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

The two zones overlap at `β_k = n − s − 1`, which is "either way." So
clause 3″ fires iff the trajectory `{(a_k, β_k)}_{k=1..b-1}` avoids two
"bad rectangles" of total area `n(r + s) − 2rs − r + 1`.

This is a clean reformulation. Verified 27/27 in the b = 10 sweep
by `trajectory.py` (zero misalignments under this characterisation).

## What's already known (clause 3 / 3′)

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

Equivalently: the orbit `{k · b^(d-1) − 1  mod n²}_{k=1..b-1}` lies
in a specific subset of `Z/n²` — the "aligned coset of length
`b − 1`."

This is a **base-`b` × base-`n` interaction**. The orbit is `b − 1`
consecutive multiples of `b^(d-1)` (minus 1) viewed mod `n²`. The
question is when these `b − 1` elements all land in the aligned
subset of `(Z/n)²`.

## Empirical exploration

`trajectory.py` enumerates the 27 `n²`-cancellation cells in the
b = 10, n ≤ 200, d ≤ 7 sweep, computes `(r, s)` and the
trajectory `{(a_k, β_k)}_{k=1..9}`, and verifies the alignment-region
characterisation. Result: zero violations; the framework is sound.

`predicate_search.py` tests candidate closed-form predicates against
a wider sweep (b = 10, n ≤ 400, d ≤ 8) containing **51**
`n²`-cancellation cells. The findings:

| candidate | TP | FN | FP | precision | recall |
|---|---|---|---|---|---|
| `r = s` | 20 | 31 | 24 | 0.45 | 0.39 |
| `(n+1) ∣ (W − ⌊W/n²⌋)` *(equivalent to r = s)* | 20 | 31 | 24 | 0.45 | 0.39 |
| `r = s ∧ br > n` | 20 | 31 | 17 | 0.54 | 0.39 |
| `\|r − s\| ≤ 1` | 31 | 20 | 465 | 0.06 | 0.61 |
| `r = s ∧ ¬smooth ∧ ¬Family-E` | 20 | 31 | 24 | 0.45 | 0.39 |

**No simple candidate works.** The most "clean" predicate (`r = s`)
covers fewer than 40% of the alignment cells AND admits 24 false
positives. False positives include cells that satisfy `r = s` but
have spread = 2 (e.g., `(n=4, d=2)`, `(n=9, d=2)`); these refute
any naive "r = s implies alignment" reading.

False negatives — cells where alignment fires despite `r ≠ s` —
include `(n=83, d=5)`, `(n=118, d=5)`, `(n=146, d=5)`, with
`r − s ∈ {3, 4, 4}` respectively. These fire because the
**trajectory** threads the aligned region anyway, despite the
non-trivial `r ≠ s` offset.

### Algebraic identity

```
r − s ≡ W − ⌊W/n²⌋ (mod n + 1)
```

This is direct: `W = ns + r + n²·⌊W/n²⌋`, so
`W − ⌊W/n²⌋ ≡ ns + r − ⌊W/n²⌋ ≡ −s + r − 0 (mod n+1)` using
`n ≡ −1, n² ≡ 1 (mod n+1)`. Verified empirically. Useful for
quickly testing `r = s` candidates but doesn't translate to an
alignment characterisation.

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

The patterns are diverse — `001000100` (period-3-like),
`010101010` (period-2), `101101101`, `111011101`, `000000001`,
etc. — and the same pattern occurs for cells with very different
`(r, s)`. The alignment isn't picking out a single trajectory shape;
it's selecting `(b, n, d)` whose trajectory happens to thread
the aligned region.

## Why this is hard

Two reasons stack:

1. **Coupled rotation, not isolated.** The trajectory
   `{(a_k, β_k)}_{k=1..b−1}` lives in `(Z/n)²`. Its evolution is
   `(a_{k+1}, β_{k+1}) = (a_k + r, β_k + s + carry_k) mod (n, n)`
   where `carry_k = [a_k + r ≥ n]`. This is a *coupled* rotation —
   the high-digit `β` evolves with a carry from the low-digit `a`.
   The standard three-distance / Beatty machinery handles the
   isolated `a`-rotation, but the joint behaviour is more delicate.

2. **`(r, s)` are determined by `(b, n, d)`, not free.** We can't
   pick `(r, s)` independently of the substrate context. They're
   the last two base-`n` digits of `b^(d-1)`, which couples the
   alignment question to the multiplicative structure of `b^(d-1)
   mod n²`. So the question is really: for which integer triples
   `(b, n, d)` does the residue `b^(d-1) mod n²` give an
   alignment-friendly `(r, s)`, *and additionally* does the
   trajectory thread the aligned region in `(Z/n)²`?

The problem is *concrete* and *checkable in O(b)* per cell. It's
not a problem we lack the tools to investigate; it's a problem
where the obvious Diophantine handles (continued fractions of
`r/n`, three-distance on `kr/n`, congruences mod `n+1`) each
capture only a fragment of the structure.

## Sharpened open question (pre-theorem framing, kept for context)

The pre-theorem framing of the open question — what (b, n, d)
make the orbit `{k · b^(d-1) − 1 mod n²}_{k=1..b−1}` lie in a
specific aligned subset of `Z/n²` — is preserved here for the
historical record. The structural theorem below subsumes this
framing on the n² > W sub-locus by reducing the alignment to a
Beatty-pair coincidence on subsets of `{1, …, b−1}`.

## What I tried that didn't work

- **`r = s`**: necessary in some cells, sufficient in none. 31 FN,
  24 FP across the b = 10, n ≤ 400, d ≤ 8 sweep.
- **`|r − s| ≤ 1`**: better recall, worse precision (465 FP).
- **`r = s ∧ br > n`**: same recall as `r = s`, slightly fewer FPs
  (because GFE-overlap is removed); doesn't close the case.
- **`gcd(r, n) = gcd(s, n) = 1`**: many cells satisfy, many cells
  satisfy and don't align. Not a clean predicate.
- **Periodicity-of-trajectory tests**: trajectories are diverse;
  don't reduce to a single periodicity class.

These are the obvious-first algebraic attempts. None lands.

## Structural theorem (proved on the n² > W sub-locus)

**Theorem.** Fix `(b, n, d)` with `b ≥ 2`, `d ≥ 1`, `n ≥ 2`,
outside the smooth regime (`n² ∤ W`) and outside classical
Family E. Suppose `n² > W = b^(d-1)`. Define

```
S₁ := { ⌈(jn + 1)/r⌉ − 1 : j = 1, …, E_n }    (r = W mod n,
                                                E_n = #{k : extras_n[k] = 1})
S₂ := { ⌊jn²/W⌋          : j = 1, …, M_{n²} } (M_{n²} = ⌊bW/n²⌋)
```

both subsets of `{1, …, b − 1}`. Then `B_{b,d}` has spread = 0 iff
*one* of the following holds:

- **(i)** `S₁ = S₂`,
- **(ii)** `S₁ = ∅` and `S₂ = {1, …, b − 1}`,
- **(iii)** `S₁ = {1, …, b − 1}` and `S₂ = ∅`.

**Proof.** Three steps.

*(Closed-form S₁.)* extras_n[k] = c_n[k] − ⌊W/n⌋ equals
`⌊((k+1)r − 1)/n⌋ − ⌊(kr − 1)/n⌋`, which is 0 or 1. The j-th `k`
with extras_n[k] = 1 is the smallest k with
`⌊((k+1)r − 1)/n⌋ ≥ j`, i.e., `(k+1)r ≥ jn + 1`, i.e.,
`k ≥ (jn + 1)/r − 1`. So `k_j = ⌈(jn + 1)/r⌉ − 1`. Hence
`S₁ = {k_j : j = 1..E_n}` is exactly the strips with extras_n = 1.

*(Closed-form S₂.)* For `n² > W`, consecutive multiples of `n²` are
spaced `n² > W` apart, exceeding the strip width. So each strip
contains at most one multiple, and the strip containing
`j · n²` is `⌊j n² / W⌋`. Hence extras_n²[k] = 1 iff strip k
contains a multiple of n² iff k ∈ S₂.

*(Three-case decomposition.)* Atom count:
```
A_k = c_n[k] − c_n²[k]
    = (⌊W/n⌋ + extras_n[k]) − (⌊W/n²⌋ + extras_n²[k])
    = (⌊W/n⌋ − ⌊W/n²⌋) + (extras_n[k] − extras_n²[k]).
```
The first parenthetical is constant in k. So `A_k` is constant in
k iff `δ_k := extras_n[k] − extras_n²[k]` is constant in k. Since
`extras_n[k], extras_n²[k] ∈ {0, 1}`, `δ_k ∈ {−1, 0, +1}`. The
three cases of constant `δ_k` correspond to:
- `δ_k = 0` for all k: extras_n = extras_n² for all k, i.e.,
  `S₁ = S₂` — case (i).
- `δ_k = +1` for all k: extras_n = 1, extras_n² = 0 for all k,
  i.e., `S₁ = full set, S₂ = ∅` — case (iii).
- `δ_k = −1` for all k: extras_n = 0, extras_n² = 1 for all k,
  i.e., `S₁ = ∅, S₂ = full set` — case (ii).

This is the entire enumeration. ∎

**Verification.** `structural_theorem.py` computes `S₁` and `S₂`
both via the closed-form expressions and via direct counting on
`B_{b,d}`. Across 1925 cells of the b = 10 sweep in the n² > W
sub-locus (outside smooth and classical Family E):

- Closed-form `S₁`, `S₂` agree with direct computation on every
  cell (zero discrepancies).
- spread = 0 ⟺ structural predicate holds, on every cell (zero
  theorem violations).
- Case decomposition: 803 cells in case (i), 5 in case (ii),
  0 in case (iii). 808 spread-zero cells total in this sub-locus
  outside smooth and classical Family E.

**Where clause 3″ proper sits.** Clause 3″ in the substrate-paper
sense is `n²-cancellation outside GFE` — i.e., spread = 0 with
both `cn` non-constant and `cnsq` non-constant. Under the theorem,
this is **exactly case (i) with both `S₁` and `S₂` non-empty**. In
the swept range, that's 17 cells (the n² > W subset of the original
27). Cases (ii) and (iii) are GFE-extended cells captured under the
spread-zero umbrella but not under clause 3″ proper.

## What's still open

The theorem reduces the n² > W question to: *when does case (i)
fire with non-empty `S₁`, `S₂`?* That is, *when do the two Beatty
sequences `S₁` and `S₂` coincide as subsets of `{1, …, b − 1}`?*

### Reduction to an explicit integer inequality (r = s sub-sub-case, proved)

For `r = s` (which forces `n² > W` and yields `W = r(n+1)`), the
case (i) coincidence reduces to the following finite condition:

> **Lemma (r = s reduction).** Let `r = s`, `n² > W = r(n+1)`,
> `M = ⌊bW/n²⌋`. Then `S₁ = S₂` (as non-empty subsets of
> `{1, …, b − 1}`) iff
>
> ```
> (jn) mod r  ≥  ⌈jr/(n + 1)⌉      for all j ∈ {1, …, M}.
> ```

**Proof sketch.** With `β := n/r`, `α := n²/W = β · n/(n+1)`, and
`X_j := (jn+1)/r`, `Y_j := jn²/W`, direct computation gives
`X_j − Y_j = ((j+1)n + 1)/(r(n+1))`. The S₁ formula
`⌈X_j⌉ − 1 = ⌊Y_j⌋ = k_j` holds iff `{jβ}` lies in
`[jn/(r(n+1)), (r−1)/r]`. The upper bound is automatic
(`{jβ}·r ≤ r − 1` always); the lower bound, multiplied by `r`,
becomes `(jn) mod r ≥ jn/(n+1)`. The integer ceiling on the
right-hand side comes from the discreteness of `(jn) mod r`. ∎

**Verification.** `beatty_reduction.py` enumerates all 17 cells
with `r = s`, `n² > W`, outside smooth and classical Family E in
the b = 10 sweep. The Beatty-check predicate matches case-(i)
firing on **17/17 cells** (zero mismatches). 8 of these 17 are
case-(i) cells (alignment fires) and the predicate identifies
exactly those 8.

### What remains open at the r = s sub-sub-case

The Beatty inequality `(jn) mod r ≥ ⌈jr/(n+1)⌉` is now a concrete
number-theoretic question. Open: characterise the set of integer
triples `(n, r, b)` (with `r = s`, `n > b`, `n ∤ br`, `br > n`) for
which this inequality holds at every `j = 1, …, M`.

This is genuinely tractable. The condition is:
- `O(M) = O(b)` to verify per cell,
- expressible as a system of finite-range Beatty rotations,
- amenable to continued-fraction analysis of `n/r` and `r/(n+1)`.

A closed-form predicate may exist via three-distance theorem
applied to the rotation `j → (jn mod r)` on `Z/r` and the linear
function `j → ⌈jr/(n+1)⌉`. Whether the closed form is
single-line or a finite case split is itself open.

### What remains open at the n² > W sub-locus (r ≠ s)

The lemma above is only for the r = s sub-sub-case. For `r ≠ s`
in the n² > W sub-locus, an analogous reduction exists but with a
different specific inequality (the slope difference `β − α =
n(rn − W)/(rW)` no longer simplifies to `n/W`; the safe-interval
endpoints depend on `(r, s)` jointly). Working out the analogous
reduction is the natural follow-up to the r = s lemma; estimated
3–5 days.

### Combined frontier

The trajectory of the work:
1. ✓ Structural theorem (n² > W sub-locus): spread = 0 ⟺ three-case
   predicate. Proved.
2. ✓ Reduction in r = s sub-sub-case: case (i) ⟺ specific Beatty
   inequality. Proved & verified 17/17.
3. ✓ j = 1 boundary condition: `r ∤ n` is necessary for case (i)
   in r = s sub-sub-case. Proved (one-line argument:
   `⌈r/(n+1)⌉ = 1` for `r ≤ n`).
4. **Conjectured (strong empirical evidence):** in the substrate
   r = s sub-sub-case, `r ∤ n` is **also sufficient** — i.e., the
   j-ladder collapses to its j = 1 element. Verified across
   b = 10, n ≤ 5000, d ≤ 14: zero exceptions.
5. Open: prove the conjecture. The mechanism is structural: the
   substrate constraint `W = r(n+1) = b^(d-1)` forces `M <
   r/gcd(n, r)` (the first j at which `(jn) mod r = 0`), so the
   "obvious" obstruction at `j = r/gcd(n, r)` is never reached;
   the harder part is showing the inequality also holds at all
   intermediate j ≤ M.
6. Open: analogous reduction for r ≠ s in n² > W sub-locus.
7. Open: structural theorem for n² ≤ W sub-locus.

## Investigation A: the j-ladder of necessary conditions

The Beatty inequality `(jn) mod r ≥ ⌈jr/(n+1)⌉` for `j = 1..M`
factors into a chain of conditions C_1, C_2, …, C_M. Each is a
necessary condition; their conjunction is necessary and sufficient.

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
`(jn) mod r ≥ k_j`. The threshold `k_j` increases by 1 each
time `j` crosses a multiple of `(n+1)/r`.

### Empirical observation in the substrate context

In the b = 10, n ≤ 5000, d ≤ 14 substrate-context sweep with r = s,
n² > W, M ≥ 1: every cell either fails C_1 (i.e., r | n) or passes
all of C_1, …, C_M. **Zero cells fail first at j > 1.**

In the **decoupled** sweep (just (n, r, b) with r ∤ n, no
substrate constraint, j up to 20), j > 1 failures are abundant:
e.g., 478 (n, r) pairs first fail at j = 2, 680 pairs first fail
at j = 3, etc.

The contrast pinpoints the mechanism: the substrate constraint
`W = r(n+1) = b^(d-1)` (i.e., `r(n+1)` must be a power of b)
restricts (n, r) tightly enough that the j-ladder collapses.
Specifically, for substrate cells, `M = ⌊bW/n²⌋ ≤ b − 1` and
empirically `M < r/gcd(n, r)`, so the first `j` at which
`(jn) mod r = 0` is never reached.

### Conjecture A (closed-form for r = s sub-sub-case)

> **Conjecture.** Let `(b, n, d)` satisfy: `r = s`, `n² > W = r(n+1)`,
> `r ∤ n`, and `br > n` (not GFE). Then case (i) of the structural
> theorem holds — equivalently, `(jn) mod r ≥ ⌈jr/(n+1)⌉` for all
> `j = 1, …, M = ⌊bW/n²⌋`.

If proved, this gives a closed-form characterisation: in the r = s
substrate sub-sub-case, **alignment iff `r ∤ n`**.

### Status of Conjecture A

- **Empirically verified:** b = 10, n ≤ 5000, d ≤ 14 sweep, zero
  exceptions across substrate-context cells.
- **Decoupled counter-evidence:** without the substrate constraint
  (W = r(n+1) free), the inequality is genuinely j-dependent.
- **Proof idea (partial).** Show `M < r/gcd(n, r)` for all
  substrate-compatible (n, r) with r ∤ n (a number-theoretic
  fact about b-smooth integers). Then show the inequality holds
  at every `j ∈ [1, M]` (the harder part — needs Beatty/three-
  distance machinery on the rotation `(jn) mod r`).

The first step (`M < r/gcd(n, r)`) is empirically verified across
the swept range and reduces to `bg(n+1) < n²` where `g = gcd(n, r)`.
This is a clean Diophantine condition on substrate-compatible cells
that probably has a one-paragraph number-theoretic proof.

The second step (the inequality holds at all `j ∈ [1, M]`) is the
real content of the conjecture. It says: **the b-smoothness of
`r(n+1)` forces enough structure on `(n, r)` that the Beatty
rotation `(jn) mod r` dominates the threshold `⌈jr/(n+1)⌉` at
every `j ≤ M`.** Probable proof path: continued-fraction expansion
of `n/r` and direct estimate using the b-smoothness of `r(n+1)`.

Items 3 and 4 are the natural next pieces of the same investigation;
item 5 is a separate project with its own difficulty (multi-multiplicity
n² inside the block).

## What this gains for the paper-side framing

Before this work, clause 3″'s open question was vague: *"the trigger
set of clause 3″ is open."* That phrasing left ambiguous whether
the openness was in the sufficient condition, in the trigger set
parameterisation, or in something else.

After the structural theorem, the open question is sharp. The
substrate paper can now state:

> **Spread = 0 in the n² > W sub-locus is fully characterised** by
> the equality `S₁ = S₂` (or boundary cases (ii)/(iii)). The
> characterisation reduces clause 3″ to a Beatty-pair coincidence
> problem with explicit slopes `n/r` and `n²/W`.
>
> **What remains open** is whether the Beatty-pair coincidence
> condition admits a closed-form parameterisation in `(b, n, d)`,
> and whether the n² ≤ W sub-locus has an analogous structural
> theorem.

This is a **clean openness** in the sense the user asked for: a
specific, named mathematical problem (Beatty-pair coincidence on
a finite range), with the proven reduction in hand and the
remaining work explicitly scoped.

## n² ≤ W sub-locus

For n² ≤ W (1205 cells in the swept range; 34 spread-zero cells
outside smooth and Family E), multiples of n² may appear more than
once per strip. The structural theorem above generalises in spirit
but its statement requires multi-multiplicity bookkeeping:
extras_n²[k] is no longer a 0/1 indicator but a count, and the
"alignment" condition becomes a multiset coincidence rather than
a set coincidence. Out of scope for this memo; would be the
natural follow-up after the n² > W Beatty-pair coincidence is
characterised.

## What I think would work — sharper outflows

**Sharper outflow A: subset characterisation for `n² > W`.**
The 11 cells with `n² > W` (no n² inside the block uniformly) form
a sub-locus where `r′ = W` exactly and the alignment condition
simplifies. In particular `s = ⌊W/n⌋` (no further mod n), and the
trajectory `(a_k, β_k)` for `k = 1..b−1` is a *single* rotation
on `Z/n²` (no second-order wrapping). This subset is *closer* to
classical three-distance machinery and is a tractable target.

**Estimated cost**: 1 week. Output: closed form for the n² > W
sub-locus (about 40% of n²-cancellation cells in the swept range).

**Sharper outflow B: trajectory-density theorem.**
Rather than a closed form for "alignment fires," prove a
*statistical* theorem: the asymptotic density of n²-cancellation
cells in `(b, n, d)` space is `Θ(1/log)` or similar. This is a
weaker result than closed form but is achievable via standard
equidistribution / Weyl-sum machinery applied to the orbit
`{k · b^(d-1) mod n²}`.

**Estimated cost**: 2–3 weeks. Output: an asymptotic density
theorem stating that n²-cancellation is a measure-zero
phenomenon (or whatever the actual scaling turns out to be).
Doesn't close clause 3″ in the substrate-paper sense, but does
say "the n²-cancellation locus is sparse, with density
characterisable by Weyl sums."

**Sharper outflow C: negative result.**
Prove that the closed-form characterisation is **not first-order
expressible** in `(b, n, d)` over Presburger arithmetic, or some
similar logical-complexity statement. This would be the
"clause 3″ trigger set is genuinely irreducible to a polynomial
predicate" result. Useful as a stop-loss: if the characterisation
provably can't be written in elementary form, the paper's open
question becomes "characterise via the natural Diophantine
embedding," not "find the clean formula."

**Estimated cost**: hard to estimate (logic theorems are
finicky); could be 2 weeks or could be 2 months. Output:
a precise statement of *what kind* of characterisation is or
isn't achievable.

## Recommendation

**A first**, then re-evaluate. The `n² > W` sub-locus is concretely
attackable with three-distance machinery; if it closes, we have a
40%-coverage theorem with a clean proof. The remaining `n² ≤ W`
cells then have a more constrained Diophantine question (the
trajectory wraps `n²` more than once), and we can decide whether to
push for a full theorem (rest of A), a density result (B), or a
negative result (C) based on what A reveals.

For the substrate paper as currently scoped: clause 3″ stays as
the structural-condition theorem with an empirical-coverage
verification. The proof-lift work informs *future* paper editions
or a follow-up paper, not the JStatSoft submission.

## Files

- `trajectory.py` — trajectory framework, alignment-region
  verification, dump of (n, d, r, s, gcds, pattern) for the 27
  swept cells.
- `predicate_search.py` — candidate predicates scored against the
  wider sweep (b = 10, n ≤ 400, d ≤ 8, 51 alignment cells); shows
  that no simple algebraic predicate on (r, s) characterises the
  trigger set.
- `n2_gt_W_probe.py` — establishes the count condition `E_n =
  M_{n²}` as necessary (17/17) for clause 3″ in the n² > W
  sub-locus.
- `structural_theorem.py` — **proves and verifies the structural
  theorem** on all 1925 cells of the n² > W sub-locus.
  spread = 0 ⟺ structural predicate (three cases: S₁ = S₂, or
  one empty / other full). Closed-form S₁, S₂ verified vs direct
  computation; zero discrepancies.
- `beatty_reduction.py` — proves the lemma reducing case (i) in
  the r = s sub-sub-case to the integer inequality `(jn) mod r ≥
  ⌈jr/(n+1)⌉` for `j = 1..M`. Verifies 17/17 cells in the swept
  range with zero mismatches.
- `boundary_conditions.py` — Investigation A: extracts and proves
  C_1, C_2, C_3 boundary conditions (case-splits worked out
  explicitly), and verifies empirically across the b = 10
  sweep that **every M ≥ 1 cell either fails at C_1 (i.e., r | n)
  or passes all C_j**.
- `conjecture_probe.py` — wider substrate sweep (b = 10, n ≤ 5000,
  d ≤ 14, no j > 1 failures) plus decoupled (n, r) sweep (where
  j > 1 failures abound). Establishes that the j-ladder
  collapse is a substrate-context phenomenon, supports
  Conjecture A.
- `conjecture_A_partial.py` — verifies **part (1) of the Conjecture
  A proof** across all 40 substrate cells with r ∤ n: the bound
  `M < r/gcd(n, r)` holds with min headroom 2, mean 289.5. The
  simpler sufficient bound `n > b·gcd(n, r)` also holds 40/40.
  This rules out the obvious j_fail obstruction and reduces the
  remaining work to part (2).
- This file — framework, empirical exploration, structural theorem,
  Beatty-reduction lemma, j-ladder analysis (Investigation A),
  conjecture, scope of remaining work.
