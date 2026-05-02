# BQN Agent Guidance

BQN is intended to become the compact documentation language for the
mathematical substrate of this repo. Right now, BQN lives in this guidance file, while the actual
project still speaks primarily in Python, C, prose, and plots.

Treat BQN here as an adoption target: BQN blocks appear inline in
existing `.md` docs alongside prose, as compact restatements of
constructions already implemented in Python and C. Short block comments
at the top of mathematically central source files are also acceptable
when they help map an implementation back to the canonical BQN names.
There is no standalone `acm_core.bqn` to maintain — the BQN is
annotation, not a third implementation.

Hard boundary: `generator/**` is out of scope for BQN. The product side
should stay BQN-free. If a generator doc needs mathematical provenance,
point back to the math docs rather than importing BQN into
`generator/**`.

This file should help an agent do two things:

1. write BQN that matches the repo we actually have
2. add BQN blocks to project docs where they clarify the algebra

## Scope

BQN belongs in this repo when it clarifies a mathematical construction
that already exists in code:

- `acm_n_primes` for `n >= 2`
- decimal digit expansion and concatenation
- leading-digit extraction
- digit-count / typographic-cost ideas
- Benford reference expressions
- binary Champernowne stream construction
- small algebraic helpers such as `v2`

BQN does **not** belong in this repo for:

- numpy batch conveniences
- plotting code
- experiment harnesses
- `generator/**` docs and source files
- Speck internals
- SHA-256 internals
- Feistel plumbing
- C memory management details
- CLI/build/test instructions

For BIDDER specifically, keep BQN on the ACM side only. The generator
may inherit mathematical provenance from `core/` and experiment docs,
but `generator/**` should remain prose and implementation, not BQN.


## The Repo Shapes The BQN

The repo has several constraints that BQN guidance should reflect.

### 1. `n = 1` is a real special case

`core/acm_core.py` treats `n = 1` as ordinary primes. That is not the
same construction as the clean monoid sieve for `n >= 2`.

So:

- use BQN one-liners for the `n >= 2` monoid case
- document the `n = 1` branch explicitly in prose
- do not hide trial division inside a "clean" ACM formula and pretend
  it is the same thing

### 2. Exact concatenation matters more than float parsing

`acm_champernowne_real` returns a Python float / C double, which means
long concatenations are truncated by IEEE 754 precision. That is an
implementation convenience, not the mathematical heart of the object.

So in BQN:

- specify the exact digit list or exact digit string first
- mention float parsing only as an implementation step in Python/C
- do not make the lossy float representation the primary spec

### 3. Integer leading digits and log-based leading digits are different roles

This repo uses two related but distinct ideas:

- theorem-level leading digit of an integer `n`
- utility-level `acm_first_digit(x)` for positive real `x`

When documenting exact block uniformity, prefer integer-digit extraction
via decimal digits, not the log-based helper. Use the log formula only
when you are mirroring `acm_first_digit`.

### 4. Binary work is separate, not an afterthought

The binary tree under `experiments/acm-champernowne/base2/` has its own vocabulary:

- binary concatenation
- run-length encoding
- entry boundaries
- `v2`

Take care when adapting BQN here.


## Minimal BQN Needed Here

This repo does not need a full BQN course. An agent only needs the
small slice that expresses the constructions above.

### Evaluation

BQN evaluates right to left.

```bqn
3 × 4 + 1   # 3 × (4 + 1)
```

### Blocks

```bqn
F ← {𝕩 + 1}
G ← {𝕨 × 𝕩}
```

### Arrays and ranges

```bqn
⟨1,2,3⟩
↕ 5        # 0 1 2 3 4
1 + ↕ 5    # 1 2 3 4 5
```

### Workhorse modifiers

```bqn
F¨ x        # map
F´ x        # fold
F⊸G x       # left bind / derived left argument
F⟜G x       # right bind / derived right argument
```

That is enough for almost everything this repo should say in BQN.


## Canonical Project Constructions

These are the expressions worth standardizing first. They are aligned
to the current repo and should be preferred over clever alternatives.

### `NPn2` - n-primes for `n >= 2`

This mirrors the monoid sieve in `core/acm_core.py` and `core/acm_core.c`.

```bqn
NPn2 ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}
```

Meaning:

- left argument `𝕨` is `n`
- right argument `𝕩` is the requested count (approximate — see note)
- generate candidate multipliers `k = 1..n×count`
- keep the multipliers `k` where `n∤k` (i.e. `n*k` is not divisible by `n²`)
- multiply surviving multipliers by `n` to get n-primes

**Important:**

- This is for `n >= 2`. `n = 1` remains prose plus Python/C, not
  this one-liner.
- This produces approximately `(n-1)×count` results, not exactly
  `count`. The Python/C implementations generate-and-collect until
  they have exactly `count` n-primes. The BQN one-liner is the
  algebraic specification (which n-primes exist), not a port of the
  stopping logic. If you need exactly `count`, take the first `count`
  elements of the result.

### `Digits10` - exact decimal digits of a positive integer

```bqn
Digits10 ← {𝕩<10 ? ⟨𝕩⟩ ; (𝕊⌊𝕩÷10)∾⟨10|𝕩⟩}
```

Use this as the base object for theorem-level statements. It is closer
to what the project actually cares about than the float parse.

### `ChamDigits10` - exact decimal concatenation

```bqn
ChamDigits10 ← {⥊ Digits10¨ 𝕩}
```

Given a list of integers, return the exact flattened digit stream.

This is the recommended BQN specification for the Champernowne payload.
If a doc needs the actual real, explain that Python/C then parse:

- `"1." + concatenated decimal digits`

and that only the prefix survives in binary floating-point.

### `DigitCount10` - typographic cost

```bqn
DigitCount10 ← {+´ ≠¨ Digits10¨ 𝕩}
```

This mirrors `acm_digit_count` conceptually, though the repo computes
the count directly from integers rather than by materializing nested
digit lists.

### `LeadingInt10` - leading decimal digit of an integer

```bqn
LeadingInt10 ← {⊑ Digits10 𝕩}
```

Use this for positional-notation theorems and exact block claims.

### `LD10` - leading significant digit of a positive real

This mirrors `acm_first_digit`.

```bqn
LD10 ← {⌊𝕩÷10⋆⌊10⋆⁼𝕩}
```

**Caveat:** This is the mathematical definition. In floating point,
`⌊log10(x)⌋` can undercount at exact powers of 10 (the same class of
bug catalogued in `wonders/curiosity-retired-first-digit.md`). The
Python/C implementations carry a `+1e-9` guard. Treat `LD10` as exact
math; note the guard when discussing the implementation.

Use this only when the repo is already discussing positive reals.

### `Benford10` - Benford reference

```bqn
Benford10 ← {10⋆⁼1+÷𝕩}
```

This is `log10(1 + 1/d)` for digit `d`.

### Binary core

These mirror `experiments/acm-champernowne/base2/binary_core.py`.

```bqn
BinDigits ← {𝕩<2 ? ⟨𝕩⟩ ; (𝕊⌊𝕩÷2)∾⟨2|𝕩⟩}
BStream   ← {⥊ BinDigits¨ 𝕩}
V2        ← {0=2|𝕩 ? 1+𝕊⌊𝕩÷2 ; 0}
```

`BStream` takes a list of integers and returns the concatenated bit
stream. In the repo, those integers are usually the first `count`
n-primes of a chosen monoid.

`V2` is the 2-adic valuation: the number of times 2 divides `𝕩`.
Defined for positive integers only — `V2(0)` infinite-loops because
0 is always even. The Python implementations guard `n == 0` explicitly.

### RLE and boundary helpers

These matter to the binary work, but they do not have to be one-line
golf. Use a block if it is clearer. The goal is to specify:

- consecutive equal-bit run grouping
- cumulative entry lengths / boundary positions

If a tidy one-liner harms readability, stop. Python is better.


## Naming Rules

Use names that make base and role obvious:

- `NPn2`, not just `NP`, when the formula excludes the `n = 1` case
- `Digits10`, `ChamDigits10`, `DigitCount10`, `LeadingInt10`, `LD10`
- `BinDigits`, `BStream`, `V2`

If a name should correspond to an implementation artifact, point to the
implementation path right next to it in prose:

- `core/acm_core.py`
- `core/acm_core.c`
- `experiments/acm-champernowne/base2/binary_core.py`


## Verification

BQN blocks are a fourth vertex in the DOCS :: C :: PYTHON triangle.
They stay honest the same way: by testing against known values.

When adding a BQN expression to a doc:

- verify it against the reference values in `tests/test_acm_core.py`
  (e.g. `3 NPn2 5` should start with `3, 6, 9, 15, ...`)
- if the BQN expression is an exact-math specification, note where it
  diverges from the lossy implementation (float truncation, stopping
  logic, edge-case guards)
- if Python or C change, check that the BQN gloss still matches

BQN is annotation — if it drifts from the implementation, the
implementation wins and the BQN gets updated.


## How To Write BQN In This Repo

Every BQN block added to a project doc should satisfy all of these:

1. It names a construction the repo already uses.
2. It says which file(s) implement that construction.
3. It says whether it is exact math, an implementation mirror, or an
   abstraction over an implementation detail.
4. It is readable enough that the gloss can be checked line by line.

Good:

```bqn
NPn2 ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}
```

"First `count` n-primes for `n >= 2`; mirrors the sieve logic of
`core/acm_core.py`."

Bad:

```bqn
F←{((0≠𝕨|·)⊸/𝕨×1+↕𝕩×𝕨)∾...}
```

## References

Project docs the BQN mirrors:

- [ACM-CHAMPERNOWNE.md](core/ACM-CHAMPERNOWNE.md) — the math
- [curiosity-retired-first-digit.md](wonders/curiosity-retired-first-digit.md) — the truncation bug (`LD10` caveat)
- `core/acm_core.py`, `core/acm_core.c` — implementations
- `experiments/acm-champernowne/base2/binary_core.py` — binary constructions

BQN language:

- Language spec: https://mlochbaum.github.io/BQN
- Quick reference: https://mlochbaum.github.io/BQN/doc/quick.html
- Built-ins: https://mlochbaum.github.io/BQN/doc/primitive.html
- CBQN: https://github.com/dzaima/CBQN
