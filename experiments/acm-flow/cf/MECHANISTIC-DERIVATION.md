# Mechanistic derivation of δ_k(n) ≈ (n − 1) k + offset(n)

The empirical decomposition `δ_k(n) = (n − 1) k + offset(n)`
(`OFFSPIKE-RESULT.md`, `EXTENDED-PANEL-RESULT.md`,
`PRIMITIVE-ROOT-FINDING.md`) admits a partial derivation from CF
first principles plus the structure of n-prime concatenation:

- The slope `(n − 1)` follows from the cofactor cycle structure of
  n-primes in a d=k block, with one heuristic step linking cycle
  disruption to convergent denominator growth.
- The universal `log_b(b/(b − 1))` constant in the spike formula
  comes from the boundary-truncation factor under
  `core/BLOCK-UNIFORMITY.md`.
- `offset(n) = log_b(b/n)` for primitive-root primes and
  `log_b(b/n²)` for `ord ≤ 2` is consistent with substrate
  divisibility absorption for `ord = 1`. For `ord = 2` the simple
  divisibility chain is empirically refuted; the mechanism is open.

The load-bearing step is to lift integer divisibility of the
boundary digit prefix to a factor in the convergent denominator.
That step is closed for `ord = 1` and open for `ord = 2` and
intermediate `ord`.


## Setup

For prime `n` with `gcd(n, b) = 1`, let `p_K(n) = n · c_K` denote
the K-th n-prime, where `c_K = q_K · n + r_K + 1` with
`(q_K, r_K) = divmod(K − 1, n − 1)`. Cofactors enumerate the
integers `{c : n ∤ c}` in increasing order, with density `(n − 1)/n`.

The d=k digit block contains atoms `p_K(n)` with
`b^{k−1} ≤ p_K(n) < b^k`. Under the smooth condition `n² | b^{k−1}`,
the count is exactly

    N_k(n, b) = (b − 1) b^{k−1} (n − 1) / n²,

and the boundary digit positions are

    T_k = Σ_{d=1}^{k} d · N_d(n, b) = cumulative digit count through d=k.

The d=k spike formula reads

    log_b(a_{i_k}) = T_k − 2 L_{k−1} + log_b(b/(b − 1)) − O(b^{−k}),
    L_{k−1} := log_b(q_{i_k − 1}).

Substituting `L_{k−1} = C_{k−1} + δ_k(n)` with `C_{k−1} = T_{k−1}`:

    δ_k(n) = (n − 1) k + offset(n) − O(b^{−k}).


## CF identity for the spike

From the standard CF identity

    | x − p_i / q_i | = 1 / (q_i · (a_{i+1} q_i + q_{i−1})),

taking `log_b` and dropping `log_b(1 + α / a_{i+1})` for
`α = q_{i−1}/q_i ∈ (0, 1)` and large `a_{i+1}`:

    log_b(a_{i+1}) = L_{match}(i) − 2 log_b(q_i),
    L_{match}(i) := −log_b |x − p_i / q_i|.

For the convergent immediately before the d=k spike, the matching
length is

    L_{match}(i_k − 1) = T_k + log_b(b / (b − 1)).

The `log_b(b / (b − 1))` says the convergent matches `T_k` digits
plus a fractional digit's worth of agreement at position `T_k + 1`:
the residual `x − p/q` past `T_k` is approximately `(b − 1)/b · b^{−T_k}`,
not `b^{−T_k}` exactly. The factor `(b − 1)/b` reflects that the
digits past `T_k` start with the leading digit of the smallest
(k+1)-digit n-prime, which averages out to that ratio over the
block.

This is a derived universal constant, not a fitted parameter.


## Why log_b(q_{i_k − 1}) = C_{k−1} + (n − 1) k + offset(n)

The convergent before the d=k mega-spike is the best rational
approximation to `x` with denominator small enough to "stop before"
the d=k boundary's full structure.

Khinchin-typical convergents match digits up through approximately
`2 · log_b(q_{i_k − 1})`. For the empirical value
`L_{k−1} = C_{k−1} + (n − 1) k + offset(n)`, that's
`2 C_{k−1} + 2(n − 1) k + small`. The convergent matches
`T_k = C_{k−1} + D_k` digits, so

    T_k ≈ 2 C_{k−1} + 2 (n − 1) k.

This recovers a constraint on the substrate counts that holds only
asymptotically; for small `k` the convergent is *better* than
typical because of substrate structure. The empirical fact
`L_{k−1} = C_{k−1} + (n − 1) k + offset(n)` puts the convergent
denominator at `b^{C_{k−1} + (n−1)k + offset(n)}`, much smaller
than the typical-CF prediction `b^{T_k/2}`.


### Cofactor cycle: the slope (n − 1)

For prime `n`, cofactors come in cycles of length `n − 1`: every
`(n − 1)` cofactors, one "skip" occurs (the cofactor that would
have been a multiple of `n` is omitted). Inside each cycle the
atom values increase by `n` each step; between cycles the jump
is `2n`.

Consequence: the digit pattern of the n-prime concatenation has a
local period of `(n − 1)` atoms = `(n − 1) · k` digits inside the
d=k block.

The convergent before the d=k mega-spike captures one full cycle
of `n − 1` atoms past the d=(k − 1) boundary. Past that point the
"2n skip" disrupts the local period and the convergent can't
extend its match without paying a denominator cost. So

    log_b(q_{i_k − 1}) ≈ C_{k−1} + (n − 1) k + offset(n).

The cofactor-cycle structure is exact; the link from "cycle
disruption" to "convergent denominator stops growing" is
heuristic. A rigorous version would track the CF state through
the cycle and show the next PQ jumps at the cycle boundary.


### offset(n) and ord(b, n)

`PRIMITIVE-ROOT-FINDING.md` classifies `offset(n)` for primes with
`ord(b, n) ∈ {1, 2, n − 1}` as:

    offset(p) = log_b(b/p)    if ord(b, p) = p − 1     (Family A)
    offset(p) = log_b(b/p²)   if ord(b, p) ≤ 2          (Family B)

Family A places one factor of `n` in the convergent denominator
relative to the natural scale `b^{C_{k−1} + (n−1)k + 1}`; Family B
places two factors. The shift between the families is exactly
`−log_b(n)`.

The proposed mechanism: when `1/n` has short period in base `b`,
the n-prime concatenation has redundancy at the period scale,
allowing the convergent denominator to absorb extra factors of `n`
into a smaller `q`.

- For ord = 1 (e.g. `n = 3`): `1/n = 0.ddd…` with `d = (b − 1)/n`.
  Multiples of `n` in base `b` satisfy digit-sum divisibility
  (digit-sum ≡ 0 mod `n`). The integer formed by concatenating
  atoms through the d=k boundary is divisible by `n` from the
  digit-sum test, in addition to the trivial divisibility from
  the last atom. One factor of `n` absorbed beyond the trivial.
- For ord = 2 (e.g. `n = 11`): `1/n = 0.dd dd …` with 2-digit
  period. Multiples satisfy the alternating-sum test. The
  alternating-sum of the concatenated integer is constrained,
  but the simple chain "divisibility of `M` ⇒ extra factor of `n`
  in convergent denominator" doesn't lift.
- For primitive root: no short-period redundancy. Only the
  trivial factor of `n` absorbed (Family A).


## Empirical check of the divisibility chain

Computing `M` (the integer formed by concatenating atoms through
d=k) and finding the largest `j` with `n^j | M`, the prediction
is `j = 1` for Family A and `j = 2` for Family B:

| n | k | T_k | max j with n^j ∣ M | predicted family-j | matches? |
|---|---|---|---|---|---|
| 3 (ord=1) | 2 | 42 | **2** | 2 | ✓ |
| 3 (ord=1) | 3 | 642 | **5** | 2 | ✓ (more) |
| 3 (ord=1) | 4 | 8642 | **2** | 2 | ✓ |
| 5 (gcd=5) | 2..4 | … | 1 | (Family D) | partial |
| 7 (ord=6=n−1) | 2..4 | … | 1 | 1 | ✓ |
| 11 (ord=2) | 2..4 | … | 1 | 2 | ✗ |

The divisibility chain works for `ord = 1` (`n = 3`) and for
primitive root (`n = 7`). It fails for `ord = 2` (`n = 11`): `M`
is divisible by `n^1` only, yet the convergent denominator
empirically absorbs `n^2`. The "extra factor of `n` in Family B"
does **not** come from `M`'s direct divisibility in the ord = 2
case.

What ord = 2 might be doing instead, both speculative:

- The recurring-decimal structure of `1/n` (period 2) induces a
  CF structure where convergent denominators include factors of
  `n²` from the recurring period itself, independent of
  truncated-prefix divisibility.
- The convergent denominator captures `M / b^{some power}` where
  `b^{power}` removes leading digits, and the remainder is
  divisible by `n²` even when `M` itself isn't.

Neither has a clean derivation. The Family B classification is
empirically real but the mechanism reduces to the simple
divisibility argument only for ord = 1.


## What full derivation would need

1. Show that `q_{i_k − 1}` is exactly the largest `q` below some
   threshold such that `p/q` matches the digit string of `x` for
   ≥ `T_k` positions. Standard CF theory provides the framework;
   the application to `x = C_b(n)` needs work.

2. Show that for `x = C_b(n)`, the integer `M` (digit prefix as
   integer) is divisible by `n^{j(n)}` where `j(n) = 1` for
   primitive root and `j(n) = 2` for ord ≤ 2. Digit-sum and
   alternating-sum tests provide this for ord = 1 and ord = 2;
   for primitive root the divisibility comes from the last atom
   alone.

3. Show that the convergent denominator `q_{i_k − 1}` equals
   `b^{T_{k−1} + (n−1)k + 1} / n^{j(n)}` to within `O(b^{−k})`
   corrections.

Step 3 is the load-bearing missing piece. It links integer
divisibility of `M` to the convergent denominator, and the simple
form of that link fails for ord = 2.


## Where the residual lives

- The `b^{−k}` tail in `δ_k(n)`. Same family as the spike formula's
  residual in `MULTI-K-RESULT.md`. Per-`n` coefficient `β(n)`,
  some `n` share, others don't.
- Intermediate-ord behaviour. `n ∈ {13, 23, 31}` deviate from
  Families A and B at `k = 4`. Either higher `k` resolves them
  or they form a third structural class.
- The off-spike CF behaviour between consecutive boundary spikes.
  This is what `L_{k−1}` actually carries beyond the boundary
  endpoints, and it is the same gap as the "spikes dominate"
  premise in `MU-CONDITIONAL.md`. Closing it closes both.


## Files

- This document — derivation, partial.
- `MULTI-K-RESULT.md`, `OFFSPIKE-RESULT.md`,
  `EXTENDED-PANEL-RESULT.md`, `PRIMITIVE-ROOT-FINDING.md` — the
  empirical findings the derivation explains.
