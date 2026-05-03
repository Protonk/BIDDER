# Interlocking defects

The ACM substrate (`core/ACM-CHAMPERNOWNE.md`) has one defect: the
multiplicative monoid `M_n = nℤ⁺ ∪ {1}` cannot factor through residues
that are missing. This forces n-prime atoms and produces non-unique
factorization. The defect is purely multiplicative — `M_n` carries no
additive structure to be deficient.

A *numerical semigroup* `S ⊂ ℕ` is the inverse arrangement: a finite
additive defect (the gap set), no native multiplicative restriction.
But `S` *also* sits inside `(ℕ, ·)`, and the additive gaps then *force*
a multiplicative defect — irreducibles in `(S, ·)`, including elements
composite in `ℤ` that cannot be factored without leaving `S`.

The two defects interlock through the gap set. This directory studies
that interlock through the same lens used for `M_n` in `core/`: take
the irreducibles, encode them Champernowne-style, and ask what the
digit stream looks like.


## 1. Numerical semigroups

A **numerical semigroup** is a subset `S ⊆ ℕ` containing `0`, closed
under addition, with finite complement `G = ℕ \ S`.

Equivalently: pick positive integers `g₁, …, g_k` with
`gcd(g₁, …, g_k) = 1` and let `S = ⟨g₁, …, g_k⟩` be all non-negative
integer combinations. This gcd condition is exactly the condition that
the complement is finite.

- `G = ℕ \ S` — the **gap set**. Finite by construction.
- `F(S) = max(G)` — the **Frobenius number**. Past `F`, every integer
  is in `S`.
- `m(S) = min(S \ {0})` — the **multiplicity**.

**Running example.** `S = ⟨3, 5⟩`:

    S = {0, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, …}
    G = {1, 2, 4, 7}
    F = 7
    m = 3

Past `7`, every integer is in `S`.

Standard reference: Rosales & García-Sánchez, *Numerical Semigroups*
(Springer, 2009). The non-unique-factorization machinery covering both
ACMs and numerical semigroups is in Geroldinger & Halter-Koch,
*Non-Unique Factorizations* (CRC, 2006).


## 2. Numerical semigroups under multiplication

`S` is also a subset of `(ℕ, ·)`. Define

    A_S := { m ∈ S \ {0, 1}
             : no factorization m = a · b with a, b ∈ S \ {1} exists }

— the **multiplicative atoms of `S`**. (We exclude `1` from factor
candidates; `1 ∉ S` for any non-trivial numerical semigroup anyway.)

For `S = ⟨3, 5⟩`, products of any two elements of `S \ {0}` are at
least `m² = 9 > F = 7`, so all products land in `S` and the question
reduces to ordinary factorization in `ℤ` constrained to factor pairs
inside `S`.

**Atoms of `⟨3, 5⟩` up to 30.**

| `m` | factor pairs in `ℤ`        | both in `S`? | atom? |
|-----|----------------------------|--------------|-------|
|  3  | —                          |              |  yes  |
|  5  | —                          |              |  yes  |
|  6  | (2, 3)                     | 2 ∉ S        |  yes  |
|  8  | (2, 4)                     | 2, 4 ∉ S     |  yes  |
|  9  | (3, 3)                     | yes          |  no   |
| 10  | (2, 5)                     | 2 ∉ S        |  yes  |
| 11  | —                          |              |  yes  |
| 12  | (2, 6), (3, 4)             | 2, 4 ∉ S     |  yes  |
| 13  | —                          |              |  yes  |
| 14  | (2, 7)                     | 2, 7 ∉ S     |  yes  |
| 15  | (3, 5)                     | yes          |  no   |
| 16  | (2, 8), (4, 4)             | 2, 4 ∉ S     |  yes  |
| 17  | —                          |              |  yes  |
| 18  | (2, 9), (3, 6)             | (3, 6) yes   |  no   |
| 19  | —                          |              |  yes  |
| 20  | (2, 10), (4, 5)            | 2, 4 ∉ S     |  yes  |
| 21  | (3, 7)                     | 7 ∉ S        |  yes  |
| 22  | (2, 11)                    | 2 ∉ S        |  yes  |
| 23  | —                          |              |  yes  |
| 24  | (2, 12), (3, 8), (4, 6)    | (3, 8) yes   |  no   |
| 25  | (5, 5)                     | yes          |  no   |
| 26  | (2, 13)                    | 2 ∉ S        |  yes  |
| 27  | (3, 9)                     | yes          |  no   |
| 28  | (2, 14), (4, 7)            | 2, 4, 7 ∉ S  |  yes  |
| 29  | —                          |              |  yes  |
| 30  | (2, 15), (3, 10), (5, 6)   | (3, 10) yes  |  no   |

Non-unique factorization is immediate:

    30 = 3 · 10 = 5 · 6        (in `S`, two atom factorizations)
    60 = 3 · 20 = 5 · 12 = 6 · 10


## 3. Two defects

Each numerical semigroup carries **two** defect sets:

- **Additive defect.** The gap set `G ⊂ ℕ`. Finite. Closes at `F`.
- **Multiplicative defect.** The atom set `A_S ⊂ S`. Infinite. Thins
  but never closes.

Density contrast with the ACM substrate:

| structure                    | atom density                | atom locator     |
|------------------------------|-----------------------------|------------------|
| `ℤ⁺` (n = 1, ordinary primes)| `π(N) ~ N / ln N`           | super-polylog    |
| `M_n` (`n ≥ 2`, `nℤ⁺ ∪ {1}`) | `(n−1)/n` of multiples of n | polylog (`core/HARDY-SIDESTEP.md`) |
| `(S, ·)` (numerical semigroup) | `~ c(S) · N / ln N`       | super-polylog    |

The ACM density is a **constant fraction** of the underlying multiples.
That is what makes the substrate clauses in `paper/PAPER.md` §3 work:
per-strip atom counts are regular, leading-digit spreads are bounded.

The numerical-semigroup atom density goes like `1 / ln N` — same order
as the ordinary primes. The leading-order contribution comes from
ordinary primes in `S` plus gap-times-prime products `g · p` for
`g ∈ G \ {1}`. Each family contributes `π(N/g)` up to lower-order edge
effects.

For `S = ⟨3, 5⟩`, the leading-order model is

    A_S  ≈  { primes p ∈ S }
         ∪  { 2p : p prime, p ≥ 3 }
         ∪  { 4p : p prime, p ≥ 3 }
         ∪  { 7p : p prime, p ≥ 2 }

This is not an exhaustive classification. Gap-stuck composites such as
`16, 32, 56, 98, 343` also occur, but they are lower-order terms rather
than new prime-rate layers. Composite products of gaps are not
automatically new layers: if `h ∈ S`, then `h · p` is reducible for
every prime `p ∈ S`, via the factorization `h · p`. Thus `42 = 14 · 3`
and `70 = 14 · 5` are reducible, while `56 = 7 · 8` and `98 = 2 · 49`
survive because every divisor pair still touches `G`.

**The Hardy sidestep does not transfer.** `core/HARDY-SIDESTEP.md`
gives `p_K(n) = n(qn + r + 1)` for `M_n` because the irreducibility
predicate `n ∤ k` is a single residue condition. The
`A_S`-irreducibility predicate is global — it asks whether *any*
divisor pair `(d, m/d)` lands inside `S` — and inherits the
prime-distribution irregularity. No comparable residue-class closed
form for the K-th atom is available.


## 4. The shared object

**Theorem (gap-determination of atoms).** Let `S` be a numerical
semigroup with gap set `G`. For `m ∈ S \ {0, 1}`,

    m ∈ A_S   ⟺   ∀ d | m with 2 ≤ d ≤ m/2:   d ∈ G  or  m/d ∈ G.

*Proof.* `m ∉ A_S` iff there is a factorization `m = a · b` with
`a, b ∈ S \ {1}`, i.e., `a, b ∈ S` and `a, b ≥ 2`. Since `m = a · b`,
either side ranges over divisors `d | m` with `2 ≤ d ≤ m/2` (the
square root case `d = m/d` is symmetric). Such a factorization exists
iff there is a divisor pair *avoiding* `G` on both sides. Negate. ∎

When `S \ {0}` is multiplicatively closed, this is literally the atom
set of that multiplicative semigroup. The condition `m(S)² > F(S)` is
a convenient sufficient closure test, used by `⟨3, 5⟩`; it is not
necessary (`⟨3, 7⟩` is closed even though `3² < 11`).

The atom set `A_S` is therefore a deterministic image of the gap set
`G` under the divisor lattice of `ℤ`. Two consequences:

1. **Gap sets are visible in atoms.** `A_⟨3,5⟩` and `A_⟨3,7⟩` and
   `A_⟨4,5⟩` differ in early atoms in ways that reflect their
   respective `G`.
2. **The interlocking is asymmetric.** `G` is a finite set; it
   determines, via an infinite divisor-lattice computation, an
   infinite atom set `A_S`. The "shape" of `A_S` past `F` is dominated
   by *which small integers are in `G`*, since their prime multiples
   supply the leading-order layers.

`M_n` fits this frame as a degenerate edge case: take `G = ℕ \ (nℤ ∪ {0, 1})`
(infinite, not a numerical semigroup). The same predicate then reduces
to the ACM atom condition. So `M_n` is the "pure multiplicative defect"
limit; numerical semigroups are the "interlocking" case where additive
and multiplicative defects co-exist and the second is forced by the
first.


## 5. The shared digit stream

The digit-stream object that `core/ACM-CHAMPERNOWNE.md` builds for
`M_n` lifts directly to `(S, ·)`. List `A_S` in ascending order, take
decimal digits, place after `1.`:

    cham_S := 1.‖ digits(a₁) ‖ digits(a₂) ‖ digits(a₃) ‖ …

For `S = ⟨3, 5⟩` the first 12 atoms are
`3, 5, 6, 8, 10, 11, 12, 13, 14, 16, 17, 19`, giving

    cham_⟨3,5⟩ ≈ 1.35681011121314161719…

This is the same surface the ACM diagnostics already act on: per-strip
leading-digit count, sawtooth of `log₁₀(aₖ)`, ε-bump damage function,
rolling-shutter under addition. All four lift unchanged.

**Predicted geometry.**

1. **Leading digit distribution.** `M_n` atoms are exactly uniform
   per-decade (`paper/PAPER.md` §3, clauses 1–4). `A_S` atoms are a
   superposition of `π`-rate sequences (primes, scaled primes by each
   `g ∈ G \ {1}`). The prediction is not exact uniformity: full-decade
   counts should be close to uniform at leading order, with
   gap-dependent residuals from the scaled-prime layers.

2. **Sawtooth of `log₁₀ A_S`.** `M_n`'s sawtooth is the clean
   `log₁₀(1 + m)` mantissa curve (see `core/ACM-CHAMPERNOWNE.md` §4).
   For `A_S` the sawtooth should still trace the mantissa curve in
   gross shape, with finer-scale modulation reflecting the spectral
   content of the gap-shifted prime mixture.

3. **Damage function (ε-bump).** Defined as deviation of
   `log₁₀(1 + m)` from its endpoint secant. For `M_n` the bump peaks
   near mantissa midpoint and codes "compositeness pressure" (`core/`
   item 4). For `A_S` the bump's shape should depend on which `g ∈ G`
   contribute most strongly — small-`g` gaps shift weight differently
   than large-`g` gaps. Not predicted; experimentally diagnostic.

4. **Rolling-shutter under addition.** `M_n` exhibits a rolling
   shutter that never converges (`core/ACM-CHAMPERNOWNE.md` §"What is
   possible now", item 2). For `A_S` we *do not know* whether the
   shutter persists, breaks, or sharpens — the additive defect `G` is
   directly involved in iterated sums and could change the dynamics.

5. **Block-uniformity / spread bound.** The substrate theorems give
   per-strip spread `≤ 2` for `M_n` over leading digits. For `A_S`, the
   working prediction is that no comparable constant spread bound holds:
   the atoms are a `π`-rate set, so per-strip fluctuations should be on
   prime-count scale rather than bounded-strip scale.


## What's open

Concrete first questions, ordered by experimental cost.

1. **First-digit fingerprint.** Build `A_⟨3,5⟩` up to `N = 10⁶`. Plot
   per-decade leading-digit histogram alongside primes, `M_2`-atoms,
   `M_3`-atoms, `M_5`-atoms. Does the `A_S` histogram sit closer to
   primes than to any `M_n`? Does the residual against uniform, and
   secondarily against Benford, encode `G`?

2. **Generator-family scan.** Repeat (1) for
   `⟨3, 7⟩, ⟨4, 5⟩, ⟨5, 7⟩, ⟨3, 5, 7⟩`. Hold `F` roughly fixed and
   vary the gap set's small-integer content. The prediction is that
   `G ∋ 2` produces a different fingerprint than `G ∌ 2` (since `2`
   contributes the densest shifted-prime layer).

3. **Spread profile.** For each `S`, compute per-strip atom counts on
   a sweep over `(b, d)` analogous to
   `experiments/acm-champernowne/substrate-phase/`. Confirm the spread
   is unbounded (or document the bound). If a clean asymptotic spread
   law exists, it is a new theorem. In the same sweep, record the
   ε-bump profile.

4. **Frobenius detection.** Is there *any* digit-stream diagnostic
   whose phase boundary lies at `F`? The early atoms (those `≤ F²` or
   so) are the only ones where the gap set's specific identity has
   not yet been "averaged out" by the prime-rate density of large
   atoms. A discontinuity at `F` in any spectral / sawtooth diagnostic
   would be a sharp affirmative.

5. **Shutter under addition.** Pairwise sums `aᵢ + aⱼ` for
   `aᵢ, aⱼ ∈ A_S`. Does the rolling shutter from `M_n` survive? Does
   the additive structure of `S` (which now matters because we are
   *adding*) interact with the multiplicative atom set in any
   detectable way?

6. **Composition with the ACM substrate.** `A_S ∩ nℤ` for `n` such
   that `n ∈ S`. This is the "doubly atomic" set: irreducible in
   `(S, ·)` and a multiple of `n`. Its leading-digit and sawtooth
   behaviour is the natural place to look for *interaction* between
   the two defect mechanisms rather than each in isolation.


## Files

- `INTERLOCKING-DEFECTS.md` — this anchor doc.

To come, in dependency order:

- `ns_atoms.py` — atom enumerator for `(S, ·)` from generators.
- `cham_ns.py` — Champernowne encoder for `A_S`.
- `diagnostics.py` — first-digit / sawtooth / damage / spread reports
  matching the `M_n` diagnostics in `core/`.
- One findings file per question above as it closes.


## References

- `core/ACM-CHAMPERNOWNE.md` — the ACM substrate and its Champernowne
  encoding. Half of the "interlocking" sits here.
- `core/HARDY-SIDESTEP.md` — the closed form `p_K(n)` that does *not*
  generalise to `(S, ·)`; the contrast bounds what is hard about the
  numerical-semigroup case.
- `algebra/README.md` — the closed-form workflow standard. Any
  theorem this directory produces should slot into the same
  state / implement / anchor / verify / document pipeline.
- `paper/PAPER.md` §3 — the substrate clauses for `M_n`. The clauses
  this directory pursues are the `(S, ·)` analogues; a comparable
  clean-statement version is the long-term target.
- Rosales & García-Sánchez, *Numerical Semigroups* (Springer, 2009) —
  standard NS reference (gap set, Frobenius, Apéry, multiplicity).
- Geroldinger & Halter-Koch, *Non-Unique Factorizations* (CRC, 2006) —
  the abstract framework that covers both ACMs and numerical
  semigroups; sets / lengths / elasticity / catenary degree if those
  invariants ever come up here.
