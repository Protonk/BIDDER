# Block Uniformity

The counting lemma behind every exact-uniformity claim in this repo.


## Lemma

In base b >= 2, the integers in the digit class
{b^(d-1), ..., b^d - 1} have leading base-b digits exactly
equidistributed over {1, ..., b-1}. Each digit appears exactly
b^(d-1) times.


## Proof

A d-digit base-b integer has the form d_1 d_2 ... d_d where
d_1 in {1, ..., b-1} and d_2, ..., d_d in {0, ..., b-1}. For
each choice of d_1, the remaining d-1 positions range freely,
giving b^(d-1) integers. The block has (b-1) * b^(d-1) integers
total. Partitioned by leading digit, each of the b-1 classes has
exactly b^(d-1) members.


## In BQN

The following uses canonical names from `guidance/BQN-AGENT.md`.
These are exact-math specifications; the implementations in
`core/acm_core.py` and `core/acm_core.c` approximate them where
floating-point truncation is unavoidable.

Definitions (repeated here so the proof can be checked in place):

```bqn
Digits10     ← {𝕩<10 ? ⟨𝕩⟩ ; (𝕊⌊𝕩÷10)∾⟨10|𝕩⟩}
LeadingInt10 ← {⊑ Digits10 𝕩}
```

The digit class d = 2 in base 10 is the 90 integers 10..99:

```bqn
10 + ↕ 90                             # ⟨10, 11, 12, ..., 99⟩
```

Extract leading digits:

```bqn
LeadingInt10¨ 10 + ↕ 90
# ⟨1,1,...,1, 2,2,...,2, ..., 9,9,...,9⟩
#  └──10──┘  └──10──┘       └──10──┘
```

Nine groups of ten. Each digit 1-9 appears exactly
10 = 10^1 = b^(d-1) times.

The same holds at every digit class. At d = 3, the block is
100 + ↕ 900 and each leading digit appears 100 = 10^2 times.
At d = 4, 1000 + ↕ 9000 and each appears 1000 = 10^3 times.
The ratio never drifts — it is always exactly 1/(b-1).

In general, the digit class d in base b:

```bqn
b⋆d-1 + ↕ (b-1)×b⋆d-1
```

This is not a canonical named expression — it is used once, here,
in the proof. It mirrors the operating block B_d defined in
`generator/BIDDER.md`.


## Sieved version: n-primes inside the block

The integer lemma says that *every* integer in `{b^(d-1), …, b^d − 1}`
contributes to the leading-digit count. The same exact equidistribution
can hold for the n-prime sieve of the block; we give a sufficient
condition on `(b, n, d)` for it to hold. The condition is **not
necessary** — there are `(b, n, d)` where the hypothesis fails but
exact uniformity holds anyway. Counterexamples and a partial story
appear after the proof; we do not have a sharp characterization.

**Lemma (sieved block — sufficient condition).** Let `b ≥ 2`, `n ≥ 2`,
`d ≥ 1` with `n² | b^(d-1)`. The n-primes of monoid `nZ+` lying in the
digit class
`{b^(d-1), …, b^d − 1}` have leading base-`b` digits exactly
equidistributed over `{1, …, b−1}`. Each digit appears as the leading
digit of exactly

    b^(d-1) · (n − 1) / n²

n-primes in the block. The total number of n-primes in the block is
`(b−1) · b^(d-1) · (n−1) / n²`, smaller than the integer block by a
factor of `n² / (n−1)`.

**Scope.** The smooth condition `n² | b^(d-1)` requires `n` to be
*b*-smooth (every prime factor of `n` divides `b`). For prime `n`
coprime to `b` — most of the n-panel in `experiments/acm-flow/cf/`
— no `d` satisfies smooth, and the closed-form count is then
asymptotic with `O(1)` per-block correction (bounded by the spread
bound below). What's "exact" is restricted to smooth, Family E, and
lucky-cancellation triples; what carries the load downstream is the
asymptotic form.

**Proof.** Fix `j ∈ {1, …, b−1}` and consider the leading-digit strip

    S_j = [j·b^(d-1), (j+1)·b^(d-1) − 1].

The strip has length `b^(d-1)`. By hypothesis `n² | b^(d-1)`, so
`n² | j·b^(d-1)` for any `j`, and in particular `n | j·b^(d-1)` and
`n² | (j+1)·b^(d-1)`. Hence `S_j` starts at a multiple of `n²` and
its length `b^(d-1)` is divisible by both `n` and `n²`.

The count of multiples of `n` in any contiguous interval of length `L`
that starts at a multiple of `n` and has `n | L` is exactly `L / n`,
with no boundary correction. Applying this twice:

- multiples of `n`  in `S_j`: exactly  `b^(d-1) / n`,
- multiples of `n²` in `S_j`: exactly  `b^(d-1) / n²`.

The n-primes of `nZ+` are the multiples of `n` that are not multiples
of `n²`. Subtracting,

    (n-primes in S_j) = b^(d-1)/n − b^(d-1)/n² = b^(d-1)·(n−1)/n²,

which is independent of `j`. Each leading-digit strip has the same
count, so the leading-digit distribution is exactly uniform. ∎


## A spread bound that always holds

When `n² ∤ b^(d-1)` we still get a bound on how far the counts can
drift, by the same kind of divmod argument.

**Bound.** For any `b ≥ 2`, `n ≥ 2`, `d ≥ 1`, the per-leading-digit
counts of n-primes in the block `{b^(d-1), …, b^d − 1}` differ by
at most 2.

**Proof.** The count of multiples of any positive integer `m` in a
contiguous interval of length `L` is either `⌊L/m⌋` or `⌈L/m⌉`,
because the interval covers either `⌊L/m⌋` complete copies of the
period `m` or one more. So the count of multiples of `n` in any
strip lies in `{⌊L/n⌋, ⌈L/n⌉}` (with `L = b^(d-1)`), and the count
of multiples of `n²` lies in `{⌊L/n²⌋, ⌈L/n²⌉}`. The n-prime count
is the difference. Its maximum is `⌈L/n⌉ − ⌊L/n²⌋` and its minimum
is `⌊L/n⌋ − ⌈L/n²⌉`, so the spread (max − min) is bounded by

    (⌈L/n⌉ − ⌊L/n⌋) + (⌈L/n²⌉ − ⌊L/n²⌋)  ≤  1 + 1  =  2. ∎

The bound is tight. Two cases where the spread reaches 2:

| (b, n, d)  | per-digit counts | spread |
|------------|------------------|--------|
| (4, 3, 2)  | `1 0 2`          | 2      |
| (4, 6, 3)  | `3 1 3`          | 2      |

A brute-force sweep over `b, n ≤ 10` and `d ≤ 5` finds no spread
larger than 2; see `tests/test_acm_core.py::test_block_uniformity_sieved_spread_bound`.


## A second sufficient family

The smooth lemma is one clean family of `(b, n, d)` where exact
uniformity holds. There is a second clean family, disjoint from the
first, that captures a different part of the locus and has its own
one-paragraph proof.

**Lemma (sieved block — Family E).** Let `b ≥ 2`, `d ≥ 2`, and `n` an
integer with

    b^(d-1)  ≤  n  ≤  ⌊(b^d − 1) / (b − 1)⌋.

Then the n-primes of monoid `nZ+` lying in the block
`{b^(d-1), …, b^d − 1}` are exactly

    {n, 2n, 3n, …, (b−1)n}

— `b − 1` elements, one per leading base-`b` digit. The per-leading-digit
count is exactly `1`.

**Proof.** Write `j = n − b^(d-1)`, so `j ≥ 0`. The upper bound on `n`
gives `(b − 1)·n ≤ b^d − 1`, equivalently `(b − 1)·j ≤ b^(d-1) − 1`.

For each `k ∈ {1, …, b − 1}`, consider `k·n = k·b^(d-1) + k·j`.

*In-block.* The lower bound `k·n ≥ k·b^(d-1) ≥ b^(d-1)` is immediate.
The upper bound is `k·n ≤ (b − 1)·n ≤ b^d − 1`.

*Leading digit.* From `k·j ≤ (b − 1)·j ≤ b^(d-1) − 1 < b^(d-1)`,
we get `k·n = k·b^(d-1) + k·j < (k + 1)·b^(d-1)`. So `k·n` lies in
the strip `[k·b^(d-1), (k + 1)·b^(d-1) − 1]` and has leading base-`b`
digit `k`.

*No further multiples.* The next multiple of `n` after `(b − 1)·n`
is `b·n ≥ b·b^(d-1) = b^d > b^d − 1`, outside the block.

*Sieve removes nothing.* `n² ≥ (b^(d-1))² = b^(2d-2) ≥ b^d` for
`d ≥ 2`, so no multiple of `n²` lies in the block at all. Each
`k·n` is therefore an n-prime.

The n-primes of `nZ+` in the block are exactly `{1·n, 2·n, …, (b − 1)·n}`,
and these fall into distinct leading-digit strips by construction. The
per-strip count is exactly `1`. ∎

**Disjointness from the smooth family.** Family E lies entirely
outside the smooth family for `d ≥ 2`. The smooth condition
`n² | b^(d-1)` requires `n² ≤ b^(d-1)`, but Family E requires
`n ≥ b^(d-1)`, so `n² ≥ b^(2d-2) > b^(d-1)` for `d ≥ 2`. The two
families partition their union into disjoint pieces.

**Concrete counts.** For each `(b, d)` with `d ≥ 2`, Family E provides
`⌊(b^(d-1) − 1)/(b − 1)⌋ + 1` legal `n` values, all giving a block of
size exactly `b − 1` (the minimum at that alphabet, one element per
leading digit):

| (b, d)   | Family E n-values             | count of n |
|----------|-------------------------------|-----------:|
| (2, 2)   | {2, 3}                        |          2 |
| (3, 3)   | {9, 10, 11, 12, 13}           |          5 |
| (4, 2)   | {4, 5}                        |          2 |
| (4, 3)   | {16, 17, 18, 19, 20, 21}      |          6 |
| (4, 4)   | {64, 65, …, 85}               |         22 |
| (10, 2)  | {10, 11}                      |          2 |
| (10, 3)  | {100, 101, …, 111}            |         12 |
| (10, 4)  | {1000, 1001, …, 1111}         |        112 |
| (10, 5)  | {10000, 10001, …, 11111}      |       1112 |

The smooth family gives a sparse set of *large* blocks; Family E
gives a dense set of *minimal* blocks. The two cover different ends
of the period dial: smooth picks up high-period generators with a
narrow choice of `n`, Family E picks up the floor case with a wide
choice of `n` (one element per leading digit, always).

**Audit cost.** Together the two sufficient families give a cheap
two-step exact-uniformity check:

1. Compute `n − b^(d-1)`. If the result lies in
   `[0, ⌊(b^(d-1) − 1)/(b − 1)⌋]`, **Family E** applies. Done.
2. Otherwise compute `b^(d-1) mod n²`. If zero, the **smooth lemma**
   applies. Done.
3. Otherwise no exact-uniformity certificate is available; fall back
   to the spread bound (`≤ 2`).

No enumeration in any branch. Step 1 is one subtraction and one
comparison; step 2 is one multiplication and one modulus.


## When uniformity holds without either family

The two sufficient families together cover only a fraction of the
exact-uniformity locus. A brute-force sweep over `b ≤ 12`, `d ≤ 5`,
and `n` ranging up past the block finds **22,205** triples that give
exact uniformity but lie outside both families. The locus is therefore
much larger than the proven sufficient pieces, and the gap is dense,
not sporadic.

The canonical witness is `(b, n, d) = (4, 5, 5)`. Smooth fails
(`25 ∤ 256`), and Family E fails (`5 < 256 = b^(d-1)`). Yet
`acm_n_primes` confirms exact uniformity with counts `[41, 41, 41]`
on the block `[256, 1023]`.

**Mechanism.** The strip starts `256, 512, 768` all happen to land in
residues mod 25 that give exactly `⌊256/25⌋ = 10` multiples of 25 each
— neither strip captures an "extra" multiple, so all three strips
agree on both `(multiples of 5)` and `(multiples of 25)`. This is a
"lucky cancellation" of the kind the spread bound counted but the
sufficient lemmas do not capture.

We do not have a closed-form characterization of *all* lucky cases.
Whether there is a third clean family — or a unified sufficient
condition that subsumes the lucky cancellations — is open.

`(4, 5, 5)` is the regression fixture in
`tests/test_acm_core.py::test_block_uniformity_sieved_unconditional_witnesses`.
The earlier `(4, 4, 2)` witness has been subsumed: it is the `j = 0`
case of Family E for `(b, d) = (4, 2)` and is now covered by
`tests/test_acm_core.py::test_block_uniformity_sieved_family_e`.


## Concrete legal triples for the smooth family

The hypothesis `n² | b^(d-1)` requires `n` to be **b-smooth** (every
prime factor of `n` divides `b`) plus a depth condition on `d`. This
is the structure of the smooth condition itself, *not* a necessary
condition for exact uniformity (see Family E above and the
unconditional witnesses below).

| (b, n, d)   | block size  | per-digit count |
|-------------|------------:|----------------:|
| (10, 2, 3)  | 225         | 25              |
| (10, 5, 3)  | 144         | 16              |
| (10, 10, 3) | 81          | 9               |
| (10, 2, 4)  | 2 250       | 250             |
| (10, 4, 5)  | 16 875      | 1 875           |
| (2,  2, 3)  | 1           | 1 (degenerate)  |

For `b = 2`, the sufficient condition admits only powers of 2 as `n`;
for `b` prime, only powers of `b`. The sufficient condition is therefore
narrower than the integer lemma. The locus of exact uniformity in
`(b, n, d)`-space is broader than the sufficient condition; how much
broader is open.


## Connection to Hardy sidestep

The two theorems form a recipe:

- `core/HARDY-SIDESTEP.md` gives termwise random access into the
  K-th n-prime of `nZ+`, for any `n ≥ 2`, in `polylog(K + n)` bit
  operations. About one monoid in isolation.
- The sieved block lemma above gives the *statistical* property that
  makes a window of that monoid usable as a generator block, when
  `n² | b^(d-1)`. About the intersection of one monoid with a
  positional-notation interval.

Together they specify an "n-prime BIDDER variant" at the math layer:

1. Pick `(b, n, d)` with `n² | b^(d-1)`.
2. Block = the n-primes of `nZ+` in `[b^(d-1), b^d − 1]`.
3. Block size = `(b−1) · b^(d-1) · (n−1)/n²`.
4. Random access into the block by index via the Hardy closed form
   plus a window offset; both are O(1) bignum work.
5. Exact leading-digit uniformity by the sieved lemma.

The cipher layer (a keyed PRP on the block index space) is identical
in shape to integer BIDDER's and is unaffected by either theorem.
This is the math side of the construction; nothing in this section
asserts that the variant has been built or that it has a property
the integer BIDDER lacks.


## Corollary: the encoding preserves it

The leading digit of the n-Champernowne real C_b(n) is the leading
digit of n. (The first n-prime of monoid n is n itself, and its
decimal representation is the first thing concatenated after "1.".)

So over a complete digit class, the leading digits of C_b are the
same multiset as the leading digits of n — which are uniform by
the lemma. The encoding does not create the uniformity; positional
notation creates it, and the encoding preserves it.

In BQN, using the exact-concatenation specification `ChamDigits10`
and the n-prime sieve `NPn2` (both from `guidance/BQN-AGENT.md`):

```bqn
NPn2         ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}
ChamDigits10 ← {⥊ Digits10¨ 𝕩}

ChamDigits10 (5↑ 10 NPn2 5)
# ⟨1,0,2,0,3,0,4,0,5,0⟩
```

The first 5 10-primes are 10, 20, 30, 40, 50 (multiples of 10
whose cofactor is not divisible by 10). Their concatenated digit
stream starts with 1 — the leading digit of n = 10. The
Champernowne real is 1.1020304050..., and its leading fractional
digit is 1.

Over the full block {10, ..., 99}, these first digits cycle
through 1..9, each appearing 10 times. The encoding is a
transparent window onto the block's digit structure.


## Downstream observables

The doc's two lemmas — the integer lemma and the sieved lemma — reach
several otherwise-distinct observables. See
`arguments/UNIFORMITY-FOUR-WAYS.md` for the four-ways reading.

The **sieved lemma**'s residue-counting fact reaches three:

- **CF spike formula `T_k`** (`experiments/acm-flow/cf/MEGA-SPIKE.md`).
  The cumulative digit count `T_k = Σ_{d=1}^{k} d · N_d(n, b)` is this
  count integrated by digit weight. The closed-form spike scale
  `S_k = D_k − C_{k−1} = (n − 1)/n² · (b^{k−1}(k(b−2) + b/(b−1))
  − 1/(b−1))` is a smooth-family sum.

- **Multiplication-table asymptote**
  (`experiments/acm-flow/mult-table/`). `M_n(K)/M_Ford(K) → α_n =
  (n − 1)/n` is the density of integers not divisible by n. M_n's
  atoms have the form `n · c` with `n ∤ c`; their distinct products
  land in residues not divisible by n, and Ford's image-counting
  anatomy applied under that residue restriction gives `α_n`.

- **Off-spike cofactor cycle slope**
  (`experiments/acm-flow/cf/OFFSPIKE-RESULT.md`). The slope `(n − 1)`
  in `δ_k(n) = (n − 1)k + offset(n)` is the cofactor cycle length —
  the numerator of the smooth-block density `(n − 1)/n²`.

The **integer lemma** plus the corollary in §"Corollary: the encoding
preserves it" below reaches a fourth observable through a different
parent fact:

- **First-digit uniformity of `C_b(n)`** (`core/ACM-CHAMPERNOWNE.md`,
  `sources/EARLY-FINDINGS.md`). The leading-digit distribution of
  `C_b(n)` over a digit class equals the leading-digit distribution
  of `n` over that class, which is uniform by the integer lemma. This
  doesn't use the sieved lemma; it uses positional notation directly.

CF, multiplicative, spectroscopic, and digit-frequency observables
all collapse to angles on this one doc — three on the sieved lemma,
one on its parent integer lemma.


## Literature placement

`EXPERIMENTAL.md` brief #1 asks whether the smooth-block lemma above
is a strict refinement of Copeland–Erdős for ACM-Champernowne reals,
and where it sits in the equidistribution literature. This section
records the placement.


### The relevant external literature

#### Copeland–Erdős 1946 — `sources/COPELAND-ERDOS.md`

For any increasing integer sequence with density `> N^{1−ε}`, the
base-`b` concatenation is normal in base `b`. Asymptotic frequency
statement; covers ACM n-primes (density `(n−1)/n²` is linear,
trivially clears the hypothesis).

#### Davenport–Erdős 1952 — `sources/champ-cf/Davenport-Erdos.pdf`

Theorem 1: for any polynomial `f(x)` with positive-integer values at
positive integers, `0.f(1)f(2)f(3)…` is normal in base 10. Method:
Weyl + Besicovitch (ε,k)-normality of individual integers. Companion
Theorem 2 gives an averaged (ε,k)-normality statement. Asymptotic
frequency; not a block-boundary exact count.

#### Schiffer 1986 — `sources/champ-cf/aa4726.pdf`

*Acta Arithmetica* **47** (1986), 175–186. Submitted 5 June 1985;
originally a doctoral thesis under J. Schoissengeier. Bibliography
is five entries: Champernowne 1935, Davenport–Erdős 1953, Kuipers–
Niederreiter 1973, Schoissengeier 1978 (Schiffer's immediate
predecessor for the precise estimation), Vaughan 1981 (the
Hardy–Littlewood method, used for the trigonometric sum bound).

Four theorems. Verbatim:

- **Theorem 1.** "Let `f(n)` be a polynomial in `n` with rational
  coefficients, `f` not constant and let `(d_n)` be a bounded
  sequence of rational numbers, such that `f(n) + d_n` is a positive
  integer for all `n ≥ 1`. Then `D(N, ω) = O(1/log N)` for
  `ω = 0.(f(1)+d_1)(f(2)+d_2)…`."
- **Theorem 2.** Same `O(1/log N)` upper bound under a stronger
  differentiability hypothesis on `f`, allowing real-coefficient `f`
  and bounded real `(d_n)`.
- **Theorem 3.** "Let `f(n)` be a linear polynomial with rational
  coefficients, `f(n) ≥ 1` for `n = 1, 2, …` and
  `ω = 0.[f(1)][f(2)]…`. Then `D(N, ω) > K · 1/log N` for **all**
  `N` and a constant `K > 0`."
- **Theorem 4.** Same `D > K / log N` lower bound under Theorem 2's
  hypotheses, but only "for an **infinite number** of `N`'s."

For Champernowne-type constants the discrepancy is `Θ(1/log N)` —
Theorem 1 (upper) plus Theorem 3 (lower) when there is no shift, or
Theorem 2 plus Theorem 4 (infinitely-often) under shifts.

Method: trigonometric sums (Weyl) for the upper bounds; combinatorial
sub-block-occurrence counting (Lemma 2: difference of `N(B_1)` and
`N(B_2)` for two specific blocks) for the lower bounds.

#### Nakai–Shiokawa — extension to real-coefficient polynomials

Generalises Schiffer to non-constant `f` with real coefficients,
`f(t) > 0` for all `t > 0`. Same `Θ(1/log N)` discrepancy. (Per
Becher–Graus 2024.)

#### Schmidt 1972 — universal discrepancy floor

For *all* sequences `(x_n) ⊂ [0,1)`, infinitely many `N` have
`D(N) > K · log(N) / N`. Universal lower bound for any sequence; van
der Corput sequences attain it.

#### Gál–Gál, Philipp, Fukuyama — almost-everywhere law

For every base `b ≥ 2` and almost every real `α`,

    D((b^n α mod 1), N)  =  O( √(log log N) / √N )

(law of iterated logarithm scale). Champernowne-type constants are
much worse than this — they decay only at `1/log N`.

#### Bugeaud 2012 (Cambridge Tract 193) — `sources/champ-cf/Bugeaud2012.pdf`

§4 "Normal numbers" surveys the field. §4.2 covers Champernowne
1933 and a Theorem 4.10 generalising Copeland–Erdős with allowed
repetition (new in Bugeaud — "for `m > 1` has not been published
previously"); proof goes through (ε,k)-normality of integers, not
block-boundary counts. §4.5 covers Mahler's transcendence proof and
the lacunary-sum representation `Σ c_n / 10^{f(n)}` of the
Champernowne constant. §4.7 Notes co-cite Schiffer with two other
references for the lower bound `D_N ≥ c / log N`. Bugeaud's notes do
not record any block-boundary exact-count result.

#### Becher–Graus 2024 — `arXiv:2407.13114` / *Amer. Math. Monthly* 131:1

Discrete elementary proof of Schiffer's bound for the Champernowne
constant (no exponential sums). Modern restatement; proof by careful
counting, closer in spirit to Champernowne's own 1933 method.


### Hierarchy summary

For a sequence in `[0,1)` viewed through the discrepancy `D(N)`:

| class | `D(N)` rate | reference |
|---|---|---|
| universal floor (any sequence) | `Ω(log N / N)` | Schmidt 1972 |
| van der Corput / low-discrepancy | `O(log N / N)` | classical |
| almost every real (LIL scale) | `O(√(log log N) / √N)` | Gál–Gál; Philipp; Fukuyama |
| Champernowne-type concatenations | `Θ(1/log N)` | Schiffer 1986; Nakai–Shiokawa |

`Θ(1/log N)` is far above the LIL scale. Champernowne-type constants
"are normal but approach normality slowly."


### Schiffer Theorem 1 directly covers ACM-Champernowne (upper bound)

For prime `n`, the K-th n-prime is

    p_K = n · c_K,    c_K = q n + r + 1,
                      (q, r) = divmod(K − 1, n − 1).

Take the linear rational polynomial

    f(K) = n² K / (n − 1).

Then `d_K := p_K − f(K)` is a function only of
`r = (K − 1) mod (n − 1) ∈ {0, …, n − 2}`, so `(d_K)` is a bounded
sequence of rational numbers and `f(K) + d_K = p_K ∈ ℕ` for all
`K ≥ 1`. Schiffer Theorem 1 applies and gives

    D(C_b(n), N) = O(1 / log N)

for prime `n` in base 10. (The proof is essentially base-agnostic
modulo the analogous Weyl bounds; Schiffer states the result in
base 10.)


### Schiffer Theorem 3 does NOT directly cover ACM (matching lower)

Theorem 3's `D > K / log N` for **all** `N` is stated for *pure*
linear `f` with no shift. The shifted version is Theorem 4, which
only gives "infinitely many N." So for ACM-Champernowne we have:

- upper bound `O(1/log N)` for all `N` — directly Schiffer Thm 1.
- lower bound `> K / log N` for **infinitely many** `N` — via
  Schiffer Thm 4 (under Thm 2's differentiability hypotheses, which
  are satisfied trivially by a linear `f`).

The matching all-N lower bound for ACM is not stated by Schiffer.
Plausibly available by adapting Theorem 3's combinatorial argument,
but the adaptation is not in the literature reached.


### What Schiffer does not have

Schiffer's Lemma 1 (the core counting lemma, p. 178) aggregates
sub-block occurrences integer-by-integer:

    Σ_{u ≤ x ≤ v} Σ_{0 ≤ t < 10^{n−k}} 1{f(x) ≡ b + t · 10^n}
        = 10^{−k}(v − u) + O(…)

and his Theorem 1 proof composes this over the entire range
`1 ≤ x ≤ T`. **There is no isolation of digit-class boundaries**
(transitions where `f(x)` first reaches `n + 1` digits). The proof
is structurally an integer-aggregation argument, not a block-by-block
exact-count argument.

This document's smooth-block lemma is the opposite. It computes
`N_d(n, b) = (b − 1) b^{d−1} (n − 1) / n²` exactly whenever
`n² | b^{d−1}` — a finite, position-specific exact statement at
radix-block boundaries, the very thing Schiffer's method does not
surface.


### Net comparison

|  | Schiffer 1986 | this document |
|---|---|---|
| altitude | asymptotic, integrated over `N` | finite, at specific `T_k` |
| object | `D(α, N) = O(1/log N)` (and `Ω`) | exact `N_d(n, b)` at smooth block |
| method | Weyl trig sums + combinatorial diffs | residue counting on `M_n` monoid |
| hypothesis | polynomial `f` with bounded shift | smooth `n² \| b^{d−1}` plus spread ≤ 2 |
| coverage | all `N` (Thm 1, 3) or infinitely many `N` (Thm 2, 4) | every smooth d-block |

The two are **compatible** — Schiffer's `Θ(1/log N)` average is what
the substrate decomposition (zero contribution at smooth boundaries,
spread ≤ 2 at non-smooth, plus within-block residual) integrates to
— but they are **structurally orthogonal**. Schiffer does not have a
block-boundary exact-count lemma anywhere in the proof; if he did,
the `(b − 1)/n²` density factor would appear, and it does not.


### Verdict for brief #1

**Strict refinement of Copeland–Erdős for ACM-Champernowne reals?**
Yes. The smooth-block lemma gives exact closed-form boundary counts
whereas CE gives only asymptotic frequency. Relationship:
"exact-finite refines asymptotic-aggregate."

**Strict refinement of Schiffer 1986 for ACM-Champernowne reals?**
Different altitude, not strictly above or below. Schiffer Theorem 1
directly proves `D(C_b(n), N) = O(1/log N)` for ACM via the rational-
shift construction above. The smooth-block lemma does not contradict
this and is not subsumed by it: Schiffer does not isolate radix-block
boundaries anywhere in his proof, and the smooth-block exact-count
form is structurally orthogonal to his integer-aggregation method.

**Where it sits.**

- *Below* Schiffer 1986 in altitude (Schiffer is asymptotic, the
  smooth-block lemma is finite/position-specific).
- *Compatible with* Schiffer's `Θ(1/log N)` rate — the smooth-block
  exact count is part of what averages out to the asymptotic.
- *Without precedent* in the pre-2000 discrepancy-theory line.
  Schiffer cites only Champernowne, Davenport–Erdős, Kuipers–
  Niederreiter, Schoissengeier 1978, Vaughan 1981 — none of these
  contains a smooth-block exact-count statement. The combinatorial
  counting tradition (Niven–Zuckerman, Maxfield) similarly treats
  blocks via averaged frequencies.

**"Probably nothing" signal.** Not triggered. The smooth-block
exact-count form is genuinely sharper than the literature reached.

**Reach goal.** A clean theorem of the form "for sequences `A`
satisfying [strengthened counting condition], the base-`b`
Champernowne real has zero discrepancy at every digit-class
boundary, with the smooth and Family E lemmas as instances." This
is conjecturally available — the smooth-block lemma is the
`M_n`-monoid instance — but the *general* statement (for arbitrary
CE sequences) has not been formulated here and is not on the page
in any of the sources reached. Worth pursuing.


### Caveats and gaps

The placement rests on the actual Schiffer 1986 paper
(`sources/champ-cf/aa4726.pdf`). What remains uncertain:

- **Nakai–Shiokawa.** Quoted by Becher–Graus 2024 as extending
  Schiffer to non-constant `f` with real coefficients, `f(t) > 0`.
  Not on file. Probably does not change anything for ACM-Champernowne
  — the rational-shift route through Schiffer Theorem 1 already
  covers it.
- **Schoissengeier 1978** (Sitzungsber. Öst. Akad. Wiss.,
  Math.-Natur. Kl., Abt. II, **187**, 225–235). Schiffer's named
  predecessor for "a more precise estimation" of Davenport–Erdős's
  `D(N, ω(f)) → 0`. Not on file. The likely closest pre-1986
  reference for Champernowne-type discrepancy.
- **Bugeaud's [232], [536].** Co-cited with Schiffer [621] for the
  lower bound `D_N ≥ c / log N`. Now that Schiffer himself proves
  this (Thm 3 for pure linear, Thm 4 for infinitely many N), [232]
  and [536] are likely Schoissengeier and Nakai–Shiokawa.
- **Niederreiter's discrepancy work** (cited by Schiffer via the
  Kuipers–Niederreiter textbook). Niederreiter's primary discrepancy
  contributions are on quasi-Monte Carlo / `(t, m, s)`-nets and
  general equidistribution, not Champernowne-type concatenations.
  The textbook is the relevant reference, not standalone papers.
- **Pre-2000 exact-block-uniformity lemma.** Schiffer's paper
  confirms there is none in his line. The combinatorial counting
  tradition (Champernowne 1933, Niven–Zuckerman 1951, Maxfield,
  Pillai) treats blocks via averaged frequencies, not boundary-
  position exact counts. The smooth-block lemma is structurally
  novel relative to this tradition.


## What depends on this

- **ACM-CHAMPERNOWNE.md**, "What Is Possible Now": the claim that
  first-digit distributions are exactly uniform.
- **BIDDER.md**, "The uniformity guarantee": the generator operates
  over a complete digit block and applies a bijection, so the
  leading-digit distribution is preserved. (Integer lemma only;
  BIDDER does not currently use the sieved version.)
- **sources/EARLY-FINDINGS.md**, section 1: the empirical count
  (1111 of each digit in 1..9999) is a direct consequence —
  {1, ..., 9999} is the union of digit classes d = 1..4, each
  internally uniform.
- **Stratified sampling**: at block boundaries the generator has
  visited every stratum equally often, because each leading digit
  appeared exactly b^(d-1) times.
- **HARDY-SIDESTEP.md**, "Why this matters for ACM-Champernowne":
  the sieved lemma is what would let an "n-prime BIDDER variant"
  inherit exact uniformity from a smaller block. The Hardy closed
  form is what would give it O(1) bignum index-into-block.

The integer lemma is trivial. The sieved lemma is two more divmods.
Their consequences are not.


## Verification

The base-10 integer case for d = 2, 3, 4 is checked against
`tests/test_acm_core.py::test_block_boundary_*`, which verifies
exact digit counts at n = 99, 999, and 9999.

The sieved lemmas have four companion tests in the same file:

- `test_block_uniformity_sieved_sufficient` — sweeps `(b, n, d)`
  with `b, n ∈ [2, 10]`, `d ∈ [1, 5]`, and `n² | b^(d-1)`, asserting
  exact uniformity and the count formula `b^(d-1)·(n − 1)/n²` for every
  legal triple of the **smooth family**.
- `test_block_uniformity_sieved_family_e` — sweeps `(b, d)` with
  `b ∈ [2, 10]`, `d ∈ [2, 5]`, generates every Family E `n` for that
  `(b, d)`, and asserts exact uniformity with count `1` per leading
  digit. Also asserts disjointness from the smooth family.
- `test_block_uniformity_sieved_unconditional_witnesses` — pins
  `(4, 5, 5)` as the canonical witness *outside both* sufficient
  families (lucky cancellation case).
- `test_block_uniformity_sieved_spread_bound` — sweeps the same
  `(b, n, d)` cube and asserts that the per-digit spread is at most 2
  even when neither sufficient family applies.
