# PROOF-LIFT: clause 3″ trigger set

The substrate paper's open question — *characterise the integer
triples `(b, n, d)` for which clause 3″'s Beatty pattern-alignment
hypothesis fires* — is partially closed. A structural theorem
fully characterises spread = 0 in the n² > W sub-locus (proved,
verified 1925/1925 cells); a reduction lemma shrinks the r = s
sub-sub-case (under n² > W) to a single integer inequality
(proved, verified 17/17); and a closed-form conjecture in that
sub-sub-case is empirically verified at b = 10 (n ≤ 5000, d ≤ 14,
zero exceptions). The conjecture is **base-specific**: it fails at
b = 6 (counterexample (b, n, d) = (6, 23, 4)), so the empirical
support does not extend to general b.

The exploration record — predicate searches, the (a_k, β_k)
trajectory framing, the j-ladder, the things that didn't work —
lives in `PROOF-ARCHIVE.md`.

This document was audit-corrected. Two prior errors are now fixed:
M was `⌊bW/n²⌋` and should have been `⌊(bW − 1)/n²⌋` (the block
ends at `bW − 1`); the Beatty-reduction lemma's right-hand side
was `⌈jr/(n+1)⌉` and should have been `⌈jn/(n+1)⌉` (the proof
sketch derives the `n` numerator). Both are corrected throughout.
The verification scripts have been updated to use the corrected
formulas; all numbers in this document reflect re-runs.

## A. The proof

Three results, in dependency order.

### A.1 Structural theorem (n² > W sub-locus)

**Theorem.** Fix `(b, n, d)` with `b ≥ 2`, `d ≥ 1`, `n ≥ 2`,
outside the smooth regime (`n² ∤ W = b^(d-1)`) and outside classical
Family E. Suppose `n² > W`. Set `r := W mod n`,
`E_n := #{k ∈ {1..b−1} : extras_n[k] = 1}`,
`M := ⌊(bW − 1)/n²⌋`. Define

```
S₁ := { ⌈(jn + 1)/r⌉ − 1 : j = 1, …, E_n }   (S₁ = ∅ when r = 0)
S₂ := { ⌊jn²/W⌋          : j = 1, …, M }
```

both subsets of `{1, …, b − 1}`. Then `B_{b,d}` has spread = 0 iff
one of:

- **(i)** `S₁ = S₂`,
- **(ii)** `S₁ = ∅` and `S₂ = {1, …, b − 1}`,
- **(iii)** `S₁ = {1, …, b − 1}` and `S₂ = ∅`.

**On the M formula.** The block `B_{b,d}` is `[W, bW − 1]`. The
number of multiples of `n²` in this block is the count of `j ≥ 1`
with `j·n² ≤ bW − 1`, which is `⌊(bW − 1)/n²⌋`. Using `⌊bW/n²⌋`
mishandles the case `n² | bW`, where `bW` itself is outside the
block: at `(b, n, d) = (10, 100, 4)`, `n² = 10000 = bW`, but
`⌊bW/n²⌋ = 1` would erroneously place `j = 1` at strip
`⌊10000/1000⌋ = 10`, outside `{1, …, 9}`.

**On r = 0.** `r = 0` means `n | W` but `n² ∤ W` (smooth is `n² | W`,
explicitly excluded). When `r = 0`, every leading-digit strip starts
at a multiple of `n`, so `extras_n[k] = 0` for all k and `E_n = 0`,
giving `S₁ = ∅` by convention; the closed-form expression is then
not invoked.

**Proof.** Three steps.

*(Closed form for `S₁`.)* For `r ≥ 1`,
`extras_n[k] = ⌊((k+1)r − 1)/n⌋ − ⌊(kr − 1)/n⌋ ∈ {0, 1}`. The j-th
value of `k` with `extras_n[k] = 1` is the smallest `k` with
`(k+1)r ≥ jn + 1`, giving `k_j = ⌈(jn + 1)/r⌉ − 1`. So `S₁` is
exactly the strips with `extras_n[k] = 1`. For `r = 0`, every
extras is 0, so `S₁ = ∅`.

*(Closed form for `S₂`.)* For `n² > W`, consecutive multiples of
`n²` are spaced `n² > W` apart, exceeding the strip width. So each
strip contains at most one multiple of `n²`, and the strip
containing `j·n²` (when `j·n² ≤ bW − 1`) is `⌊j·n²/W⌋`. Hence
`extras_n²[k] = 1` iff `k ∈ S₂`.

*(Three-case decomposition.)* Atom count:
```
A_k = c_n[k] − c_n²[k]
    = (⌊W/n⌋ − ⌊W/n²⌋) + (extras_n[k] − extras_n²[k]).
```
The first parenthetical is constant in k, so `A_k` is constant iff
`δ_k := extras_n[k] − extras_n²[k]` is constant. Since both
`extras_n[k], extras_n²[k] ∈ {0, 1}`, we have `δ_k ∈ {−1, 0, +1}`.
The only ways `δ_k` can be constant in k are:
- `δ_k = 0`: `extras_n[k] = extras_n²[k]` for all k, i.e.,
  `S₁ = S₂` — case (i).
- `δ_k = +1`: `extras_n[k] = 1, extras_n²[k] = 0` for all k, i.e.,
  `S₁ = full set, S₂ = ∅` — case (iii).
- `δ_k = −1`: `S₁ = ∅, S₂ = full set` — case (ii).

(There is no "averaging" escape: the values are `{0, 1}`, so the
difference is constant in k iff each sequence is constant in k.)
Exhaustive. ∎

**Verification.** `structural_theorem.py` — closed-form `S₁, S₂`
agree with direct strip-counting on all 1925 cells of the b = 10
sweep in the n² > W sub-locus (zero discrepancies); spread = 0 ⟺
structural predicate holds on all 1925 cells (zero theorem
violations). Case decomposition: 803 in (i), 5 in (ii), 0 in
(iii).

**Where clause 3″ proper sits.** Case (i) with both `S₁` and `S₂`
non-empty. In the swept range, that's 17 cells (the n² > W subset
of the original 27). Cases (ii) and (iii) are GFE-extended cells
captured under the spread-zero umbrella but not under clause 3″
proper.

### A.2 Beatty-reduction lemma (r = s sub-sub-case under n² > W)

**Lemma.** Suppose `r = s` (where `r = W mod n`,
`s = ⌊W/n⌋ mod n`) **and** `n² > W`. These two together force
`W = r(n+1)`. Let `M = ⌊(bW − 1)/n²⌋`, and assume `M ≥ 1` and
`E_n ≥ 1` (so `S₁` and `S₂` are non-empty). Then case (i) of A.1
holds iff

```
(jn) mod r  ≥  ⌈jn/(n+1)⌉      for all j ∈ {1, …, M}.
```

The ceiling form is the universal statement; `M ≥ n` is possible
(e.g., (b, n, d) = (10, 4, 2) has M = 6, n = 4), so the
simplification `⌈jn/(n+1)⌉ = j` is only valid for `j ≤ n` and is
*not* universal across the lemma's regime.

**On the M ≥ 1 guard.** Without it, M = 0 makes the inequality
vacuously true while case (i) with non-empty subsets is false; the
biconditional collapses. M = 0 cells have `S₂ = ∅`; if also
`E_n = 0`, they satisfy case (i) only vacuously (`S₁ = S₂ = ∅`)
and are excluded from clause 3″ proper by the non-empty guard.

**Proof of `W = r(n+1)`.** `r = s` means `W mod n = ⌊W/n⌋ mod n`.
Write `W = Qn² + sn + r` with `Q = ⌊W/n²⌋`. The hypothesis `n² > W`
gives `Q = 0`, so `W = sn + r = rn + r = r(n+1)`. (Without
`n² > W`, `Q ≥ 1` is possible and `r = s` does *not* force
`W = r(n+1)`.)

**Proof of the inequality.** Write `β := n/r`,
`α := n²/W = β · n/(n+1)`, `X_j := (jn+1)/r`, `Y_j := jn²/W`.
Direct computation: `X_j − Y_j = ((j+1)n + 1)/(r(n+1)) > 0`.

The j-th element of `S₁` is `⌈X_j⌉ − 1`; the j-th element of
`S₂` is `⌊Y_j⌋`. Equality `⌈X_j⌉ − 1 = ⌊Y_j⌋` holds iff
`{jβ} ∈ [jn/(r(n+1)), (r−1)/r]`. The upper bound is automatic
(`{jβ}·r ≤ r − 1` always for `r ≥ 1`); the lower bound, multiplied
by `r`, gives `(jβ)·r ≥ jn/(n+1)`, i.e., `(jn) mod r ≥ jn/(n+1)`.
Since `(jn) mod r` is an integer, discreteness gives the ceiling:
`(jn) mod r ≥ ⌈jn/(n+1)⌉`. ∎

**Verification.** `beatty_reduction.py` (corrected) — predicate
matches case-(i) firing on 17/17 r = s cells (b = 10 sweep), zero
mismatches.

### A.3 Conjecture A (closed-form, b = 10)

> **Conjecture (b = 10).** Let `(10, n, d)` satisfy: `r = s`,
> `n² > W = r(n+1)`, `r ∤ n`, `br > n` (not GFE), and `M ≥ 1`.
> Then case (i) holds — equivalently,
> `(jn) mod r ≥ ⌈jn/(n+1)⌉` for all `j ∈ {1, …, M}`.

If proved, this collapses the Beatty inequality to its `j = 1`
element: in the b = 10 substrate r = s sub-sub-case (with M ≥ 1),
**alignment iff `r ∤ n`**.

**Status.**
- Empirically verified across `b = 10`, `n ≤ 5000`, `d ≤ 14`
  (zero exceptions). The decoupled sweep (without the substrate
  constraint `W = r(n+1) = b^(d-1)`) finds j > 1 failures in
  abundance — confirming the j-ladder collapse is real and
  substrate-driven.
- **Base-specific.** The same statement at `b = 6` is false:
  `(b, n, d) = (6, 23, 4)` satisfies `r = s = 9`, `n² = 529 > 216 = W
  = r(n+1)`, `r ∤ n`, `br = 54 > 23 = n`, but `(jn) mod r = 1 < 2 =
  j` at `j = 2`, and case (i) directly fails (`S₁ = {2, 5}`,
  `S₂ = {2, 4}`). So the empirical b = 10 support does not extend
  to general b. Whether an analogous conjecture (perhaps with
  additional hypotheses) holds for other bases is itself open.

**Proof structure (partial).** Two parts.
- (1) `M < r/gcd(n, r)` for substrate-compatible `(n, r)` at b = 10
  with `r ∤ n`. **Verified 40/40** in the wider sweep, with min
  headroom 2 and the simpler sufficient condition `n > b·gcd(n, r)`
  also holding 40/40 (`conjecture_A_partial.py`). This kills the
  `j_fail = r/gcd(n, r)` obstruction.
- (2) The inequality `(jn) mod r ≥ ⌈jn/(n+1)⌉` holds at every
  `j ∈ [1, M]`, given (1) and `r ∤ n`. **Open**, b = 10. Needs
  continued-fraction / three-distance machinery on the rotation `(jn) mod r`
  exploiting the b = 10-smoothness of `r(n+1) = 10^(d-1)`. The
  base-specificity of the conjecture suggests the proof must use
  base-smoothness in an essential way — a generic
  Diophantine argument would extend to other bases, where the
  conjecture is false.

### A.4 How they connect

```
substrate paper's open question:
    "characterise (b, n, d) where clause 3″ fires"

    │   Structural theorem (A.1) — proved
    ▼
    spread = 0 in n² > W sub-locus iff
    structural predicate on (S₁, S₂)

    │   case (i) with S₁, S₂ non-empty is clause 3″ proper
    ▼
    when does S₁ = S₂ (non-empty)?

    │   Beatty-reduction lemma (A.2), specialised to r = s and n² > W
    │   (with M ≥ 1, E_n ≥ 1)
    │   — proved
    ▼
    iff (jn) mod r ≥ ⌈jn/(n+1)⌉ for j = 1..M
    (the simplification ⌈jn/(n+1)⌉ = j applies only for j ≤ n,
     not universally — M ≥ n+1 is possible, e.g., (b,n,d) = (10,4,2)
     has M = 6, n = 4)

    │   Conjecture A (A.3), b = 10 only
    │   — empirically verified, not proved
    │   — base-specific (false at b = 6)
    ▼
    iff r ∤ n      ← single one-line predicate (b = 10 only,
                     conjectural)
```

The chain reduces the substrate paper's open question to a
b = 10-specific conjecture. Each arrow's status is labelled.

## B. Paper-side recommendation

**Insertion point.** `paper/PAPER.md`, **line 110** — the start of
the existing `Remark 3.11 ($n^2$-cancellation residual)`. Replace
the existing remark (lines 110–112) with three new items: a
theorem, a lemma, and a remark.

The current Remark 3.11 says only "the alignment condition is
verified 27/27 in the swept range; characterising the trigger set
is open." The new content replaces this with a proven theorem, a
proven reduction lemma, and an explicitly-stated conjecture
labelled with its b = 10 scope.

**What to insert** (replacing lines 110–112):

> **Theorem 3.11 (Structural decomposition of spread-zero, $n^2 > W$).**
> Fix $(b, n, d)$ outside the smooth regime and classical Family E,
> with $n^2 > W = b^{d-1}$. Let $r = W \bmod n$, $E_n = \#\{k \in
> \{1,\ldots,b-1\} : \text{extras}_n[k] = 1\}$, and
> $M = \lfloor (bW - 1)/n^2 \rfloor$. Define
> $$
> S_1 := \{\lceil (jn+1)/r \rceil - 1 : j = 1, \ldots, E_n\}
> \quad (S_1 = \emptyset \text{ if } r = 0),
> \quad
> S_2 := \{\lfloor jn^2/W \rfloor : j = 1, \ldots, M\},
> $$
> both subsets of $\{1, \ldots, b-1\}$. Then $B_{b,d}$ has spread =
> 0 iff (i) $S_1 = S_2$, or (ii) $S_1 = \emptyset$ and $S_2 =
> \{1, \ldots, b-1\}$, or (iii) $S_1 = \{1, \ldots, b-1\}$ and
> $S_2 = \emptyset$.
>
> [proof: the three-step argument from A.1]

> **Lemma 3.12 (Beatty-pair coincidence reduction, $r = s$ and $n^2 > W$).**
> If additionally $r = \lfloor W/n \rfloor \bmod n$ (so $r = s$)
> and $n^2 > W$, then $W = r(n+1)$. Assuming $M \geq 1$ and
> $E_n \geq 1$ (so $S_1, S_2$ are non-empty), case (i) of Theorem
> 3.11 holds iff
> $$
> (jn) \bmod r \;\geq\; \lceil jn/(n+1) \rceil \qquad \text{for all
> } j \in \{1, \ldots, M\}.
> $$
> For $j \leq n$, $\lceil jn/(n+1) \rceil = j$; for $j > n$, the
> ceiling is strictly less than $j$. Both ranges occur in the
> regime — $M = 6 > 4 = n$ at $(b, n, d) = (10, 4, 2)$ — so the
> ceiling form is the universal statement.

> **Remark 3.13 (Conjecture and open question).** In the $b = 10$
> substrate $r = s$ sub-sub-case with $M \geq 1$, we conjecture that
> the inequality of Lemma 3.12 holds at every $j \in [1, M]$ iff
> $r \nmid n$ — i.e., the j-ladder of necessary conditions collapses
> to its $j = 1$ element under the substrate constraint. Verified
> empirically on $b = 10$, $n \leq 5000$, $d \leq 14$ (zero
> exceptions). The conjecture is base-specific: at $b = 6$, the cell
> $(b, n, d) = (6, 23, 4)$ satisfies the hypotheses but has the
> inequality fail at $j = 2$, so the conjecture is false for general
> $b$. A proof at $b = 10$ would close clause 3″ in the $r = s$
> sub-sub-case to the single-line predicate $r \nmid n$.

**Numbering after insertion.** The current paper has no Theorem
3.11 (the existing 3.11 is a Remark). Inserting Theorem 3.11,
Lemma 3.12, Remark 3.13 cleanly replaces the existing Remark 3.11
without renumbering anything earlier. The Conclusion (line 227)
update: "the trigger-set conjecture of Remark 3.13 (b = 10) is the
open question this paper leaves on the table."

## C. The open question, framed

### What it leaves open for BIDDER users (pragmatically)

A BIDDER user wanting exact-uniformity `P` already has three
recognised regimes — Theorems 3.5 (smooth-sieved), 3.6 (Family E),
3.7 (Generalised Family E) — each closed-form-checkable in `O(1)`
or `O(b)`. Anywhere outside the three regimes, the user has the
universal spread bound (≤ 2; Theorem 3.9) but no *exact* contract.

The structural theorem (3.11) sharpens this picture in the n² > W
sub-locus: spread = 0 outside the proven regimes is fully
characterised by an `O(b)` test on the two subsets `S₁, S₂` of
`{1, …, b−1}`. A user *can already* use this to recognise
exact-uniformity `P` in the n²-cancellation regime, by computing
`S₁` and `S₂` and checking the three-case predicate. **This is
universal in `b` and is the user-facing payload of the work.**

The Beatty-reduction lemma (3.12) provides a sharper test in the
r = s sub-sub-case (under n² > W and with M ≥ 1, E_n ≥ 1): case (i)
reduces to the single inequality `(jn) mod r ≥ ⌈jn/(n+1)⌉` for
j = 1..M. Same complexity (`O(b)`) but mathematically sharper — and
universal in b. (The simplification `⌈jn/(n+1)⌉ = j` is valid only
when `j ≤ n`, which is not guaranteed across the regime.)

**What closing Conjecture A would buy.** A one-line `O(1)` test
*at b = 10*: in the b = 10 substrate r = s sub-sub-case, alignment
iff `r ∤ n`. Marginal practical gain over the existing `O(b)` test
(a constant-factor speedup on a check that's already trivial), and
restricted to a single base. The conjecture's mathematical
content — a proof of why the j-ladder collapses at b = 10
specifically — is what would be earned, not the user-facing
predicate.

### Why we don't close it

Five reasons:

1. **Toolset mismatch.** The substrate paper's proofs are divmod
   arithmetic on integer block counts. Closing Conjecture A
   requires Beatty / three-distance / continued-fraction machinery
   on rotations of `Z/r`, plus arguments specific to base-10
   smoothness of `r(n+1)`. That toolset is foreign to the rest of
   §3.

2. **Base specificity.** The conjecture is false at b = 6
   ((6, 23, 4) is a counterexample). A correct proof must use
   b = 10 in an essential way — a generic Diophantine argument
   would extend to b = 6 and contradict the counterexample. Pinning
   down the base-10-specific structure is its own research project.

3. **The user contract doesn't change.** Either way, a user has a
   checkable predicate for spread = 0 in the n²-cancellation
   regime — `O(b)` via Theorem 3.11 / Lemma 3.12, or `O(1)` if
   Conjecture A is proven. The exact-uniformity contract on the
   cipher composition (§5) reaches every spread = 0 cell regardless.

4. **Empirical extensiveness as alternative evidence.** The
   conjecture is verified at b = 10 across `n ≤ 5000`, `d ≤ 14`
   with zero exceptions, and the decoupled sweep confirms the
   j-ladder collapse is real and substrate-driven. A reader who
   doesn't trust the conjecture can verify it computationally to
   any bound; the verification is `O(b)` per cell.

5. **The journey has the right epistemic shape.** The paper now
   names a specific integer inequality (`(jn) mod r ≥ ⌈jn/(n+1)⌉`),
   with the simplification to `(jn) mod r ≥ j` only when `j ≤ n`; the
   substrate-context-vs-decoupled contrast that explains why the
   collapse is non-trivial, the base-specificity that scopes the
   conjecture, and the partial proof (part 1 verified 40/40, part 2
   needing base-10-aware Beatty machinery). That is the shape of
   "open question with a clean reduction" — not "we left this
   hanging." A reader who wants to contribute the missing proof has
   a concrete entry point. A reader who doesn't has a bounded
   operating envelope.

The conjecture stays open because closing it is its own paper, not
a bullet point in this one.

## Files

- `trajectory.py` — trajectory framework (entry point);
  alignment-region verification on 27 cells.
- `predicate_search.py` — confirms no simple predicate on `(r, s)`
  characterises the trigger set.
- `n2_gt_W_probe.py` — the count condition `E_n = M_{n²}` is
  necessary in the n² > W sub-locus (17/17).
- `structural_theorem.py` — proves and verifies the structural
  theorem (1925/1925, zero violations). Uses corrected
  `M = ⌊(bW − 1)/n²⌋` and the `r = 0 ⇒ S₁ = ∅` convention.
- `beatty_reduction.py` — proves the r = s reduction lemma
  with corrected `⌈jn/(n+1)⌉` predicate (17/17 cells, zero
  mismatches).
- `boundary_conditions.py` — Investigation A: proves C_1 (r ∤ n)
  and gives the simplified C_j: jn mod r ≥ j (for j ≤ n);
  verifies that every M ≥ 1 b = 10 substrate r = s cell either
  fails C_1 or passes all C_j.
- `conjecture_probe.py` — wider b = 10 substrate sweep
  (n ≤ 5000, d ≤ 14, no exceptions) plus decoupled sweep
  (j > 1 failures abound), establishing the j-ladder collapse as
  substrate-driven.
- `conjecture_A_partial.py` — verifies part (1) of Conjecture A's
  proof (40/40, headroom analysis) at b = 10.
- `PROOF-ARCHIVE.md` — earlier exploration record (predicate
  searches, the trajectory framework details, the j-ladder
  case-splits as originally derived (with the wrong predicate),
  sharper-outflow proposals B and C, the n² ≤ W follow-up scope).
- This file — current proof, paper-side recommendation, open-
  question framing.
