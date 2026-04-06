# BQN for Specification

BQN is the documentation language of this project. It expresses
constructions as executable one-liners alongside the C and Python
implementations. It is not the primary implementation language. It
is a lens — terse, grammatically regular, and readable once you
know five rules.

This document is a reference for agents producing BQN expressions
in this codebase. It covers enough of the language to express the
ACM-Champernowne pipeline and its variants. It does not cover the
full language.


## Grammar

BQN has four roles. Every token occupies exactly one role, and
the role is determined by its spelling:

| Role     | Case/shape  | Example         | What it is              |
|----------|-------------|-----------------|-------------------------|
| Subject  | lowercase   | `x`, `3`, `⟨⟩`  | Data. A value.          |
| Function | Uppercase   | `+`, `⌽`, `F`   | Takes 1 or 2 subjects.  |
| 1-mod    | superscript | `˜`, `¨`, `⌜`   | Takes 1 operand (left). |
| 2-mod    | superfixed  | `∘`, `⊸`, `⟜`   | Takes 2 operands.       |

Functions apply to subjects and return subjects.
Modifiers take functions (or subjects) and return functions.

That is the entire grammar. There are no exceptions, no context-
dependent reinterpretation, no verb/adverb ambiguity. If you know
a token's role, you know how it combines.


## Evaluation

BQN evaluates **right to left**, like all APL descendants.

```
   3 × 4 + 1     ⍝ 3 × (4 + 1) = 15, not (3×4)+1
```

A function with a left argument is **dyadic** (two arguments).
Without one, it is **monadic** (one argument). Most symbols have
both a monadic and a dyadic meaning:

| Symbol | Monadic         | Dyadic            |
|--------|-----------------|-------------------|
| `+`    | (identity)      | add               |
| `-`    | negate          | subtract          |
| `×`    | sign            | multiply          |
| `÷`    | reciprocal      | divide            |
| `⌊`    | floor           | min               |
| `⌈`    | ceiling         | max               |
| `|`    | absolute value  | modulo            |
| `⋆`    | e^x             | power             |
| `√`    | square root     | nth root          |
| `⌽`    | reverse         | rotate            |
| `↑`    | prefixes        | take              |
| `↓`    | suffixes        | drop              |
| `/`    | indices         | replicate/filter  |
| `⊔`    | group           | group by          |
| `∾`    | join            | join to           |
| `≠`    | length          | not equal         |
| `⥊`    | deshape (flat)  | reshape           |


## Modifiers (the important ones)

```
F¨ x        ⍝ map: apply F to each element of x
F˜ x        ⍝ self: x F x
x F⌜ y      ⍝ table: F applied to all pairs (outer product)
F´ x        ⍝ fold (reduce) x by F
F` x        ⍝ scan x by F
F∘G x       ⍝ compose: F(G(x))
F⊸G x       ⍝ bind left: (F x) G x.   dyadic: x F⊸G y = (F x) G y
x F⟜G y     ⍝ bind right: x F (G y).   monadic: F⟜G x = (G x) F x... no:
```

The two bind modifiers `⊸` and `⟜` are the workhorses. They
partially apply:

```
   3⊸+ x       ⍝ 3 + x       (left argument fixed to 3)
   +⟜3 x       ⍝ x + 3       (right argument fixed to 3)
   F⊸G x       ⍝ (F x) G x   (monadic: F computes the left arg)
   F⟜G x       ⍝ x F (G x)   (monadic: G computes the right arg)
```

The train (fork): `F G H` applied to `x` means `(F x) G (H x)`.
Three functions in a row form an implicit fork. This is how you
write point-free expressions.


## Blocks and assignment

```
   F ← {𝕩 + 1}          ⍝ monadic function (𝕩 = right arg)
   G ← {𝕨 × 𝕩}          ⍝ dyadic function (𝕨 = left, 𝕩 = right)
   𝕊                     ⍝ self-reference (for recursion)
   {𝕤⋄ body}             ⍝ 𝕤 declares the block as a function
```

Multiple statements separated by `⋄` or newlines. The last
expression is the return value.


## Arrays

```
   ⟨1, 2, 3⟩            ⍝ list
   3‿4‿5                 ⍝ strand notation (same as above, shorter)
   ↕ n                   ⍝ range: 0, 1, ..., n-1
   1 + ↕ n               ⍝ range: 1, 2, ..., n
   x / y                 ⍝ filter: keep elements of y where x is 1
```


## Predicates and filtering

```
   2 | x                 ⍝ x mod 2
   0 = 2 | x             ⍝ is x even?
   (0≠n|·)⊸/ n×1+↕m     ⍝ n-primes: multiples of n where n∤k
```

The last line is the core ACM filter, explained below.


## The ACM-Champernowne Pipeline in BQN

### n-primes (n ≥ 2)

The n-primes of monoid n are {n·k : n∤k, k ≥ 1}.

```
   NP ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}
```

Left arg `𝕨` = n, right arg `𝕩` = count (upper bound on how
many k values to scan; output may be shorter). `1+↕𝕩×𝕨` is the
candidate k values. `𝕨×` multiplies by n. The filter `(0≠𝕨|·)⊸/`
keeps only those where k mod n ≠ 0.

Usage: `2 NP 20` gives the first several 2-primes.

To get exactly K n-primes, generate more than enough and take K:

```
   NPK ← {𝕩↑ (0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}
```

### Champernowne real

Concatenate decimal digit lists and interpret:

```
   CDigits ← {⥊10{𝕨⊸(⌊∘÷˜)⟜(|˜)⍟(↕1+·⌊𝕨⊸⋆⁼)𝕩}¨ 𝕩}
```

This is harder to read and probably not worth golfing. For
specification purposes, the clearer form is:

```
   Digits ← {𝕩{𝕩<1 ? ⟨⟩ ; (𝕊⌊𝕩÷10)∾⟨10|𝕩⟩}𝕩}
   CDigits ← ⥊∘Digits¨
```

`Digits` converts an integer to a list of its decimal digits.
`CDigits` maps that over an array and flattens. The Champernowne
real is then `1` followed by a decimal point and `CDigits` of
the n-prime list.

### Leading digit

```
   LD ← {⌊𝕩÷10⋆⌊10⋆⁼𝕩}
```

Floor of x divided by 10 to the floor of its base-10 log.

### Benford reference

```
   Benford ← {10⋆⁼1+÷𝕩}
```

`log10(1 + 1/d)`.


## Binary Champernowne

For the binary experiments (Mallorn Seed), the pipeline changes:

```
   BinDigits ← {𝕩{𝕩<1 ? ⟨⟩ ; (𝕊⌊𝕩÷2)∾⟨2|𝕩⟩}𝕩}
   BStream ← ⥊∘BinDigits¨
```

Or, more idiomatically, using base conversion:

```
   BStream ← ⥊ 2{⌽𝕨⊸(⌊∘÷˜)⍟(↕1+·⌊𝕨⊸⋆⁼)𝕩}¨ ·
```

### RLE

```
   RLE ← {≠¨⊸(⟨⊑¨,≠¨⟩) ⊔𝕩}
```

Group consecutive equal elements, return value-length pairs.
(The exact BQN for this depends on taste; the point is that
grouping and counting are single operations.)

### 2-adic valuation

```
   V2 ← {0=2|𝕩 ? 1+𝕊⌊𝕩÷2 ; 0}
```

Count trailing factors of 2, recursively.


## Style Guide for This Project

**One-liners, not programs.** Each BQN expression should be a
single definition or a single pipeline. If it needs more than
two lines, it is too complex for its role here — simplify the
idea or leave it to Python.

**Name the construction.** Assign each expression to a named
function. `NP`, `CDigits`, `LD`, `Benford`, `V2`. These names
should match the terminology in ACM-CHAMPERNOWNE.md and the
Python/C function names where possible.

**Gloss every expression.** Every BQN line in the docs should
have a plain-English comment or a preceding sentence explaining
what it computes. The BQN is a formula, not a replacement for
the explanation.

**Don't optimize.** Clarity over brevity. If a two-character
savings makes the expression harder to gloss, keep the longer
version. This is specification, not golf.

**Test nothing.** BQN expressions in this project are not tested
in CI. They are documentation. The C and Python implementations
are the tested artifacts. If a BQN expression and a Python
function disagree, the Python is authoritative.

**Mark the role.** When adding BQN to a document, use a fenced
code block with language tag `bqn`:

````
```bqn
   NP ← {(0≠𝕨|·)⊸/ 𝕨×1+↕𝕩×𝕨}   # first ~𝕩 n-primes of monoid 𝕨
```
````


## Installing BQN

For verifying expressions interactively:

```
# CBQN (C implementation, recommended)
git clone https://github.com/dzaima/CBQN && cd CBQN && make
./BQN -e '2 {(0≠𝕨|·)⊸/𝕨×1+↕𝕩×𝕨} 20'

# Or use the online REPL: https://mlochbaum.github.io/BQN/try
```

No BQN dependency is required to build or run any part of this
project. It is a documentation tool only — until it isn't.


## Reference

- Language spec: https://mlochbaum.github.io/BQN
- Primer: https://mlochbaum.github.io/BQN/doc/quick.html
- All built-ins: https://mlochbaum.github.io/BQN/doc/primitive.html
- CBQN source: https://github.com/dzaima/CBQN
