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


## What depends on this

- **ACM-CHAMPERNOWNE.md**, "What Is Possible Now": the claim that
  first-digit distributions are exactly uniform.
- **BIDDER.md**, "The uniformity guarantee": the generator operates
  over a complete digit block and applies a bijection, so the
  leading-digit distribution is preserved.
- **EARLY-FINDINGS.md**, section 1: the empirical count (1111 of
  each digit in 1..9999) is a direct consequence — {1, ..., 9999}
  is the union of digit classes d = 1..4, each internally uniform.
- **Stratified sampling**: at block boundaries the generator has
  visited every stratum equally often, because each leading digit
  appeared exactly b^(d-1) times.

The lemma is trivial. Its consequences are not.


## Verification

The base-10 case for d = 2, 3, 4 can be checked against
`tests/test_acm_core.py::test_block_boundary_uniformity_*`,
which verifies exact digit counts at n = 99, 999, and 9999.
