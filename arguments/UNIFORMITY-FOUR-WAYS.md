# Block Uniformity Four Ways

A critique of `core/BLOCK-UNIFORMITY.md`. The question is not whether
the count is correct — it is — but what the count *is*, read literally
as a residue-counting fact, and how it powers four otherwise-distinct
observables in this project.

The reading below partitions the doc's content into a one-line
elementary fact, a sieved-monoid specialisation in two disjoint
sufficient families, an unconditional spread bound, and a long list
of downstream observables. The structural reading is that one
residue-counting fact reaches the spike formula, the multiplication
table, the off-spike cofactor cycle, and the ACM-Champernowne
digit-frequency claim simultaneously. That centrality is currently
distributed across many docs; the four-ways read surfaces it.


## The Object

`BLOCK-UNIFORMITY.md` documents three things layered on one substrate
fact.

1. **Integer leading-digit uniformity.** In the digit class
   `[b^{d−1}, b^d)`, each leading base-`b` digit `1, …, b−1` appears
   exactly `b^{d−1}` times. Trivial — positional notation.

2. **Sieved leading-digit uniformity for n-primes.** Two disjoint
   sufficient conditions on `(b, n, d)`:

   - **Smooth family** (`n² | b^{d−1}`): each leading-digit strip
     `[j · b^{d−1}, (j+1) · b^{d−1} − 1]` is exactly
     `b^{d−1} · (n − 1)/n²` n-primes long.
   - **Family E** (`b^{d−1} ≤ n ≤ ⌊(b^d − 1)/(b − 1)⌋`): the only
     n-primes in the block are `{n, 2n, …, (b − 1) n}`, one per
     leading digit.

   Both give exact uniformity. They cover disjoint regions of
   `(b, n, d)`-space. A brute-force sweep finds 22 205 lucky-cancellation
   triples (e.g. `(4, 5, 5)`) outside both families where exact
   uniformity holds anyway; no unifying sufficient condition is known.

3. **Spread bound.** Without any hypothesis, per-leading-digit counts
   differ by at most 2. Tight at `(4, 3, 2)` and `(4, 6, 3)`.

The total block count `(b − 1) · b^{d−1} · (n − 1)/n²` (smooth case)
is the corollary of (2) most heavily used downstream.


## Grand

The grand part is reach, not depth. One residue-counting fact powers
four structurally distinct observables in this project:

- **Spike formula `T_k`.** The cumulative digit count
  `T_k = Σ_{d=1}^{k} d · N_d(n, b)` in `experiments/acm-flow/cf/MEGA-SPIKE.md`
  is `BLOCK-UNIFORMITY` integrated by digit count. The closed-form
  spike scale `S_k = D_k − C_{k−1} = (n − 1)/n² · (b^{k−1}(k(b−2) +
  b/(b−1)) − 1/(b − 1))` is a smooth-family sum.
- **Multiplication-table asymptote.** `M_n(K)/M_Ford(K) → α_n = (n − 1)/n`
  in `experiments/acm-flow/mult-table/`. The factor `(n − 1)/n` is
  the same single-coprime density that the squared form `(n − 1)/n²`
  decomposes into when both factors of the product are required to be
  coprime; under Ford's image-counting anatomy, the relevant density
  is the single one.
- **Off-spike cofactor cycle slope.** `δ_k(n) = (n − 1)k + offset(n)`
  in `experiments/acm-flow/cf/OFFSPIKE-RESULT.md`. The slope `(n − 1)`
  is the cycle length of cofactors of n-primes, which is the
  numerator of the `BLOCK-UNIFORMITY` density.
- **ACM-Champernowne first-digit uniformity.** `core/ACM-CHAMPERNOWNE.md`
  and `EARLY-FINDINGS.md` claim exact-uniformity of the leading digits
  of `C_b(n)`. The claim *is* the sieved lemma plus the corollary at
  the bottom of `BLOCK-UNIFORMITY.md`.

For most concatenated-real constructions, the n-prime distribution by
digit length is not closed-form. Here it is, and the same closed form
appears in three CF / multiplicative / spectroscopic observables that
look unrelated. That reach is the substrate-transparency pattern in
`experiments/math/hardy/SURPRISING-DEEP-KEY.md` made specific.

The grand reading has a real caveat. The smooth condition `n² | b^{d−1}`
is *restrictive*: it requires `n` to be `b`-smooth (every prime factor
of `n` divides `b`). For prime `n` with `gcd(n, b) = 1` it never
holds. In those cases the closed form is asymptotic with `O(1)`
per-block correction, not exact at any `d`. Family E catches a
different sliver (where `n` is at the block boundary), and the
22 205 lucky-cancellation triples are dense but uncharacterised.
What's "exact" is restricted; what's used downstream is mostly
asymptotic.


## Mundane

Given positional notation, every claim in the doc is one or two
divmod arguments.

| feature | source |
|---|---|
| integer lemma | `d`-digit numbers split into `b − 1` leading-digit strips of length `b^{d−1}`. |
| smooth family | each strip has length `b^{d−1}` divisible by `n²` and starts at a multiple of `n²`; multiples of `n` in such a strip are exactly `b^{d−1}/n`; multiples of `n²` are `b^{d−1}/n²`; difference is `(n − 1)/n² · b^{d−1}`. Two divmods. |
| Family E | the only multiples of `n` in `[b^{d−1}, b^d)` are `n, 2n, …, (b−1)n`; the upper bound on `n` ensures all `b − 1` of these land in distinct leading-digit strips; `n² ≥ b^d` so no multiple of `n²` to sieve. One block-boundary argument. |
| spread bound | count of multiples of `m` in any interval of length `L` is `⌊L/m⌋` or `⌈L/m⌉`; spread of multiples is `≤ 1` for both `n` and `n²`; total spread `≤ 2`. One observation. |
| total block count | sum across leading digits of the smooth per-strip count. |

There is no new mathematics in `BLOCK-UNIFORMITY.md`. It is residue
counting on integer intervals, with positional notation supplying the
strip structure. The two sufficient families are not a deep result —
they are two ways of arranging for the divmod to be exact.

This is exactly the BIDDER blindness pattern in
`memory/abductive_surprise_pattern.md` waiting to be flagged: the
doc's content is *integer counting*, but the framing as "Block
Uniformity" with separate "Lemmas" and "Sufficient Families" can
suggest deeper structure than is actually there.


## Beautiful

Four features are pretty.

1. **One fact, four observables.** The reach catalogued in §"Grand"
   is the structurally striking feature. CF expansion is digit-string
   arithmetic; multiplication-table count is image-counting in a
   residue class; cofactor-cycle slope is a Hardy-bijection
   enumeration; first-digit uniformity is a measure-theoretic claim
   on a real number. They share one substrate fact: the density of
   integers not divisible by `n` in `[b^{d−1}, b^d)`, and how that
   density partitions across leading-digit strips when the smooth
   condition holds.

2. **Two disjoint sufficient families, different mechanisms.** Smooth
   (`n² | b^{d−1}`) and Family E (`b^{d−1} ≤ n ≤ ⌊(b^d − 1)/(b−1)⌋`)
   cover different regions of `(b, n, d)`-space and have different
   structural reasons for working. Smooth: each strip is "long enough"
   to admit a clean divmod. Family E: each strip contains "exactly one"
   n-prime by upper bound on `n`. Two disjoint conditions giving the
   same exact-uniformity conclusion.

3. **Lucky cancellations are dense.** The 22 205 triples outside both
   sufficient families with exact uniformity (e.g. `(4, 5, 5)`) say
   the locus of exact uniformity is much broader than the proven
   sufficient pieces. A unifying characterisation is open. This is a
   real piece of unknown structure, not a presentation artifact.

4. **Spread `≤ 2`** is unconditional and tight. Without smooth, without
   Family E, without lucky cancellation, the per-digit count varies by
   at most 2. The doc's bound is sharp; it cannot be improved.


## Contingent

Most of the surrounding presentation is contingent.

- **The name "Block-Uniformity."** "Uniformity" suggests
  measure-theoretic uniformity (a continuous distribution being
  uniform); the content is residue-counting closed forms on integer
  intervals, with sufficient conditions for exact equidistribution
  across leading-digit strips. The naming is fine but biases the
  reader toward viewing this as a probabilistic / measure-theoretic
  fact rather than as elementary integer counting.

- **The smooth-block hypothesis as the centerpiece.** The doc opens
  with the smooth lemma; Family E arrives later, framed as "a second
  sufficient family." Empirically the smooth family is *narrower*
  than Family E for many `(b, n)` pairs (smooth requires `n` to be
  `b`-smooth; Family E covers a wider range of `n`). The
  presentation order reflects discovery order, not coverage.

- **The "exact uniformity" framing.** For prime `n` coprime to `b`
  (the n-panel of the spike work), smooth never holds; what's used
  is the *asymptotic* count `(b − 1) b^{d−1} (n − 1)/n²` with `O(1)`
  per-block correction. The doc's "exact" claims are technically
  scoped to the sufficient families, but the asymptotic usage
  downstream is what carries the load. The doc could be more direct
  about which is which.

- **The "What depends on this" list.** Lists consumers individually.
  The reach is structural; the centrality is documented but
  distributed across docs. A "downstream observables" section
  pointing at the four observables in §"Grand" would surface the
  centrality directly.

- **The Hardy-sidestep "recipe" section.** Frames the construction
  as a possible cipher variant (n-prime BIDDER). Useful in context,
  but the recipe-shape framing makes the doc look like a building
  block in a generator-design pipeline; in practice the doc is
  consumed by analytic results, not by the generator. The recipe
  framing is contingent on the original BIDDER motivation; the
  current usage is broader.

- **The Family E concrete-counts table.** Lists per-(b, d) `n`-values
  and counts. Worked examples, not theorems. Pedagogically useful;
  not load-bearing.

- **The 22 205 lucky-cancellation count.** Specific to a brute-force
  sweep over `b ≤ 12, d ≤ 5`. Concrete, but the number itself is
  contingent on the sweep range; the *fact* that the locus is
  broader than both sufficient families is what's load-bearing.


## Exact-uniformity vs Asymptotic-density

A scope warning the doc doesn't quite make. The closed form
`N_d(n, b) = (b − 1) b^{d−1} (n − 1)/n²` is **exact** in three cases:

- smooth (`n² | b^{d−1}`),
- Family E (`b^{d−1} ≤ n ≤ ⌊(b^d − 1)/(b − 1)⌋`),
- lucky cancellation (no characterisation).

In every other `(b, n, d)`, the count is an integer that differs from
the closed form by `O(1)`, with the difference bounded by 2 (the
spread bound). For prime `n` coprime to `b` — the most-cited case
in the spike work — *no smooth (b, n, d) exists at all*, so what's
used downstream is the asymptotic form with `O(1)` correction per
block.

The downstream consumers handle this in different ways:

- `MEGA-SPIKE.md` distinguishes `T_k(actual)` from `T_k(smooth)` and
  uses `T_k(actual)` in the spike formula. The closed form `S_k` is
  a smooth-block expression; for non-smooth blocks `S_k` differs from
  actual `D_k − C_{k−1}` by `O(1)` per non-smooth block.
- `MULTI-K-RESULT.md` documents a per-(n, k) panel where smooth fails
  at `d = 1, 2` for many n-panel members; the residual collapses
  once `T_k(actual)` is used.
- `OFFSPIKE-RESULT.md` cites `(n − 1)/n²` as a substrate density
  without engaging the smooth condition explicitly.
- `mult-table/` works at large `K` where the residue density is
  asymptotic anyway; the smooth condition isn't relevant.

The pattern: every consumer needs the asymptotic form. The exact
form is a check on the asymptotic form when smooth holds. The doc
presents exact as the centerpiece, asymptotic as a fallback. In
practice the relationship is reversed.


## One-Line Summary

`core/BLOCK-UNIFORMITY.md` is two-line residue counting on integer
intervals — smooth-block divmod, Family E block-boundary argument,
and an unconditional spread bound — that powers four otherwise-distinct
observables of the project. The grand part is the reach, with the
caveat that "exact" is restricted and most usage is asymptotic. The
beautiful part is two disjoint sufficient families plus a dense
lucky-cancellation locus. The mundane part is divmod arithmetic. The
contingent part is the "uniformity" naming, the smooth-first
presentation order, and the centrality being distributed across
downstream docs rather than surfaced here.
