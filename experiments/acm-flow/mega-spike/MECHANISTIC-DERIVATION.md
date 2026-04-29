# Mechanistic Derivation Attempt — δ_k(n) ≈ (n−1)k + offset(n)

Phase 3.1 (B), step (α). Take the empirical pattern from
`OFFSPIKE-RESULT.md` and `PRIMITIVE-ROOT-FINDING.md` and try to
derive it from CF first principles plus the structure of n-prime
concatenation.

What's derived here, what's conjectured:

- **Derived (with one heuristic step):** the slope `(n − 1)` comes
  from the cofactor cycle structure of n-primes in a d=k block.
- **Partly derived:** the universal `log_b(b/(b−1))` constant in the
  spike formula reflects the boundary-truncation factor under
  Block-Uniformity.
- **Conjectured (not derived):** `offset(n) = log_b(b/n)` for
  primitive-root primes and `log_b(b/n²)` for small-ord primes.
  The connection to `ord(b, n)` is empirically clean but the
  mechanism is open.


## Setup recap

For prime n with `gcd(n, b) = 1`, let p_K(n) = n · c_K denote the
K-th n-prime, where c_K is the K-th positive integer coprime to n.
Hardy's closed form gives c_K = q_K·n + r_K + 1 with
(q_K, r_K) = divmod(K − 1, n − 1), so cofactors enumerate the
integers `{c : n ∤ c}` in increasing order, with density (n−1)/n
in the integers.

The d=k digit block contains atoms `p_K(n)` with `b^{k−1} ≤ p_K(n)
< b^k`. Under the smooth condition `n² | b^{k−1}`, the count is
exactly

    N_k(n, b) = (b − 1) b^{k−1} (n − 1) / n²

(`core/BLOCK-UNIFORMITY.md`).

The boundary digit positions are

    T_k = Σ_{d=1}^{k} d · N_d(n, b) = cumulative digit count through d=k block.

The d=k mega-spike is the largest partial quotient `a_{i_k}` near
the convergent that matches the digit expansion through the d=k
boundary. The empirical formula is

    log_b(a_{i_k}) = T_k − 2 L_{k−1} + log_b(b/(b−1)) − O(b^{−k}),
    L_{k−1} := log_b(q_{i_k − 1}).

Substituting `L_{k−1} = C_{k−1} + δ_k(n)` with
`C_{k−1} = T_{k−1} = Σ_{d=1}^{k−1} d · N_d`:

    δ_k(n) = (n − 1) k + offset(n) − O(b^{−k}).

We want to derive both `(n − 1) k` and `offset(n)`.


## Standard CF identity for the spike

Let p_i / q_i be the i-th convergent of `x = C_b(n)`. The exact
identity:

    | x − p_i / q_i | = 1 / (q_i · (a_{i+1} q_i + q_{i−1}))

So

    a_{i+1} q_i² + a_{i+1} q_i · (q_{i−1} / q_i) = 1 / | x − p_i / q_i |.

Taking log_b, and writing `α := q_{i−1}/q_i ∈ (0, 1)`,

    log_b(a_{i+1}) = − log_b | x − p_i/q_i | − 2 log_b(q_i)
                    − log_b(1 + α / a_{i+1}).

For large `a_{i+1}` the last term is negligible, giving

    log_b(a_{i+1}) ≈ L_{match}(i) − 2 log_b(q_i),

where `L_{match}(i) = − log_b | x − p_i/q_i |` is the convergent's
log-matching-length to x.

For the convergent immediately before the d=k spike, we observe

    L_{match}(i_k − 1) = T_k + log_b(b/(b−1)).

The "extra" `log_b(b/(b−1))` says the convergent matches T_k digits
plus a fractional `log_b(b/(b−1)) ≈ 0.046` digit's worth of
agreement at position T_k + 1. Mechanistically, this is the
boundary-truncation factor: the residual `x − p/q` past T_k is
approximately `(b−1)/b · b^{−T_k}`, not `b^{−T_k}` exactly. The
factor `(b−1)/b` reflects that the digits past T_k start with the
leading digit of the smallest (k+1)-digit n-prime — which is
guaranteed to be ≥ 1 (it begins with `1` typically), giving y ≥ 1/b
in the residual fraction; the asymptotic-average reflects density
considerations one layer down.

We treat `log_b(b/(b−1))` as a derived universal constant and
proceed.


## Why log_b(q_{i_k − 1}) = C_{k−1} + (n − 1) k + offset(n)

The key structural fact: the convergent before the d=k mega-spike is
the *best rational approximation to x with denominator small enough
to "stop before" the d=k boundary's full structure*.

Concretely: q_{i_k − 1} matches digits up through approximately
position `2 · log_b(q_{i_k − 1})` (Khinchin-typical). For our
empirical value, that's `2(C_{k−1} + (n−1)k + offset)` ≈ `2 C_{k−1} +
2(n−1)k + small`. But the convergent matches T_k = C_{k−1} + D_k
digits. So

    T_k ≈ 2 C_{k−1} + 2 (n − 1) k.

Solving for D_k:

    D_k ≈ C_{k−1} + 2 (n − 1) k.

Under the smooth-block condition this isn't quite right —
`D_k = N_k · k` and `C_{k−1} = Σ N_d · d`. Plugging:

    N_k · k − Σ_{d=1}^{k−1} N_d · d = 2(n − 1) k + small.

This recovers a constraint on the substrate counts. Whether it
holds asymptotically is a question for direct calculation; for
small k it doesn't hold tightly. So Khinchin-typical is the wrong
heuristic for the convergent matching length here. The convergent
isn't typical: it's *better* than typical because of substrate
structure.

The empirical fact `L_{k−1} = C_{k−1} + (n − 1) k + offset(n)` says
the convergent denominator is `b^{C_{k−1} + (n−1)k + offset(n)}` —
much smaller than the typical-CF prediction `b^{T_k/2}`.

Here's the proposed mechanism for `(n − 1) k`:

**Cofactor cycle conjecture.** For prime n, the cofactor sequence
`c_1, c_2, c_3, ...` is the integers coprime to n in order. Within
any window of n consecutive integers, exactly (n − 1) are coprime
to n. So the cofactors in a d=k block come in *cycles of length
n − 1* — every (n−1) cofactors, one "skip" occurs (the cofactor that
would have been a multiple of n is omitted).

Inside each cycle of n−1 cofactors, the atom values increase by n
each step. Between cycles, the jump is 2n.

Consequence: the digit pattern of the n-prime concatenation has a
local period of (n − 1) atoms = (n − 1) · k digits inside d=k
block.

The convergent before the d=k mega-spike captures *one full cycle
of n − 1 atoms past the d=(k−1) boundary*. Past that point, the
"2n skip" disrupts the local period and the convergent can't extend
its match without paying a denominator cost.

So:

    log_b(q_{i_k − 1}) ≈ position at end of (n − 1)-th atom of d=k block + offset(n)
                       = C_{k−1} + (n − 1) k + offset(n).

This gives the slope `(n − 1)`.

**Status of this argument:** the cofactor-cycle structure is exact;
the link from "cycle disruption" to "convergent denominator stops
growing" is heuristic, not proven. A rigorous version would need
to track the CF state through the cycle and show the next PQ jumps
(causing the "stop") at the cycle boundary.


## Why offset(n) depends on ord(b, n)

This is conjectural. Three observations:

**(i)** For primitive-root primes (`ord(b, n) = n − 1`), the
empirical offset is `log_b(b/n)`. Equivalently,

    q_{i_k − 1} ≈ (b/n) · b^{C_{k−1} + (n−1)k}
               = b · b^{C_{k−1} + (n−1)k} / n.

So q has a *factor of n in its denominator* relative to the
"natural" scale `b^{C_{k−1} + (n−1)k + 1}`.

**(ii)** For small-ord primes (ord = 1 or 2), the offset is
`log_b(b/n²)`, i.e.

    q_{i_k − 1} ≈ b · b^{C_{k−1} + (n−1)k} / n².

An *extra factor of n* in the denominator.

**(iii)** The shift between Family A and Family B is exactly
`−log_b(n)`. The shift's sign (always reducing q) and its magnitude
(exactly one factor of n) suggest a discrete arithmetic event.

**Mechanistic proposal.** When `1/n` has short period in base b,
the n-prime concatenation has a *redundancy* at the period scale:
consecutive atom blocks share digit substructure. This redundancy
allows the convergent denominator to absorb an extra factor of n
into a smaller q.

Specifically: the period of `1/n` in base b is `ord(b, n)`.

- For ord = 1 (n=3): `1/n = 0.ddd...` with `d = (b−1)/n`.
  Multiples of n in base b have *constrained digit sums*: digit
  sum ≡ 0 (mod n). The integer formed by concatenating them is
  *automatically divisible by n* (digit-sum test). One factor of
  n is "absorbed" into M, allowing `M = n · M'`, and the convergent
  denominator can be `b^{T_k}/n` or smaller.

- For ord = 2 (n=11): `1/n = 0.dd dd ...` with 2-digit repeating
  block. Multiples of 11 in base 10 satisfy the *alternating-sum*
  divisibility test. The integer formed by concatenating 11-primes
  has alternating-digit-sum ≡ 0 (mod 11). One factor of 11
  absorbed. Maybe also a *second* factor under richer
  substrate-redundancy arguments.

- For primitive root: no short-period redundancy. Only one factor
  of n absorbed (Family A).

This gets the family classification right (Family A: one factor of
n; Family B: two factors of n) but the "second factor for ord ≤ 2"
isn't fully derived — it's plausible from the period-2 redundancy
but the explicit chain isn't yet written.

**Status of this argument:** the digit-sum divisibility (ord = 1)
and alternating-sum divisibility (ord = 2) are exact substrate
facts. The chain "divisibility of M ⇒ extra factor of n in
convergent denominator" is conjectural at the level of CF analysis.
A rigorous derivation would track how M's divisibility lifts to
the convergent.


## What the derivation would have to show, fully

A rigorous mechanistic derivation needs to:

1. Show that `q_{i_k − 1}` is exactly the largest q < some threshold
   such that the rational p/q matches the digit string of x for
   ≥ T_k positions. (Standard CF theory provides the framework;
   the application to our specific x needs work.)

2. Show that for x = C_b(n), the integer M = (digit prefix as
   integer) is divisible by n^j(n) where j(n) = 1 for primitive
   root and j(n) = 2 for ord ≤ 2. (Digit-sum / alternating-sum
   tests provide this for ord = 1, 2; for primitive root the
   divisibility comes from the last atom alone — `n | last atom`
   gives `n | M` always, and there's no further structural factor.)

3. Show that the convergent denominator `q_{i_k − 1}` equals
   `b^{T_{k−1} + (n−1)k + 1} / n^{j(n)}` to within O(b^{−k})
   corrections. (This is the load-bearing step; it links the
   integer divisibility of M to the convergent denominator.)

Step 3 is the missing piece. The other two are either substrate
facts or standard CF theory.


## Empirical check of the divisibility mechanism

I tested the divisibility hypothesis directly: compute M (the
integer formed by concatenating atoms through d=k) and find the
largest j with `n^j | M`. The hypothesis predicts j = 1 for
Family A and j = 2 for Family B.

| n | k | T_k | max j with n^j ∣ M | predicted family-j | matches? |
|---|---|---|---|---|---|
| 3 (ord=1) | 2 | 42 | **2** | 2 | ✓ |
| 3 (ord=1) | 3 | 642 | **5** | 2 | ✓ (more) |
| 3 (ord=1) | 4 | 8642 | **2** | 2 | ✓ |
| 5 (gcd=5) | 2..4 | … | 1 | (Family D) | partial |
| 7 (ord=6=n−1) | 2..4 | … | 1 | 1 | ✓ |
| 11 (ord=2) | 2..4 | … | 1 | 2 | **✗** |

**The divisibility hypothesis works for ord = 1 (n = 3) and
primitive root (n = 7), but FAILS for ord = 2 (n = 11).** For
n = 11, M is only divisible by n^1 at every k tested, yet the
convergent denominator empirically absorbs n^2. So the "extra
factor of n in Family B" does **not** come from M's divisibility
in the ord = 2 case.

This refutes the simple "M divisibility = convergent denominator
factor" mechanism for Family B.

### What the ord = 2 case might be doing instead

The convergent denominator could absorb a factor of n that doesn't
come from immediate truncation divisibility. Two hypotheses:

(i) The recurring-decimal structure of 1/n (period 2 for n = 11)
    induces a CF structure where convergent denominators include
    factors of `n^2` from the recurring period itself, independent
    of the truncated-prefix divisibility.

(ii) The convergent denominator captures M / b^{some power} where
     b^power "removes" some leading digits, and the remainder is
     divisible by n^2 even when M itself isn't.

Both are speculative; I don't have a clean derivation. The empirical
fact that offset(11) = log_b(b/n²) at k = 4 (matching to 5 decimals)
is robust, but the mechanism doesn't reduce to the simple
divisibility argument that works for ord = 1.

So the "Family B" classification is empirically real but the
mechanism is **only partially derived** — clean for ord = 1, open
for ord = 2.

## Practical residue

The derivation is **partial**: the slope `(n − 1)` has a
suggestive cycle-based mechanism; the offset `log_b(b/n^{j(n)})`
has a divisibility mechanism that works for ord = 1 but **not** for
ord = 2 in any clean form; the link from substrate structure to
convergent denominator factor is the open analytic step.

What this means for the affordances frame in
`SURPRISING-DEEP-KEY.md`:

- The substrate-transparency of n-prime concatenation reaches into
  the CF expansion through *digit-sum / alternating-sum
  divisibility tests*. These are elementary, substrate-driven
  facts about how multiples of n look in base b.
- The leakage to `offset(n) = log_b(b/n^{j(n)})` is consistent
  with these facts but isn't yet derived from them. The next layer
  of the pattern is "how does CF theory translate substrate
  divisibility into convergent denominator factors."
- The "intermediate ord" cases (n = 13, 31, possibly 23 in the
  panel) might correspond to *partial* divisibility — fractional
  factors of n absorbed — which the panel's k = 4 measurements
  capture incompletely.

So the mechanistic story is: substrate provides divisibility,
divisibility lifts to convergent denominator via CF structure,
convergent denominator yields offset(n). Each step is plausible;
the full chain isn't yet rigorous.


## Where the residue goes (per the metaphysical commitment)

Even if the full chain were closed, the unclosability would still
have to live somewhere because ACM-Champernowne is conjecturally
normal/irrational. Three candidate sites:

- The b^{−k} tail in δ_k(n). Same b^{−k} family as in the spike
  formula and the multi-k corrections; same suspected origin
  (boundary alignment of consecutive convergents).
- Intermediate-ord behavior. n = 13, 31, 23: their offset values
  don't fit the j(n) ∈ {1, 2} story, suggesting fractional or
  multi-mode divisibility absorption.
- The Khinchin-typical off-spike CF behavior between mega-spikes
  is *not* purely substrate-driven. The off-spike PQs encode
  arithmetic information beyond the mega-spike formula. Phase 4
  pooling can't pretend they don't.


## Files

- This document: derivation attempt, partial.
- `MULTI-K-RESULT.md`, `OFFSPIKE-RESULT.md`,
  `EXTENDED-PANEL-RESULT.md`, `PRIMITIVE-ROOT-FINDING.md`: the
  empirical findings the derivation tries to explain.
