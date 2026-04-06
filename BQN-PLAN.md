# BQN Migration Plan

Goal: every `.md` doc that states a mathematical construction also
states it in BQN, using the canonical names from `guidance/BQN-AGENT.md`.
When an agent reads a math or design doc in the repo, the algebra is
demonstrated inline, not deferred to a separate reference. BQN is
annotation — no standalone `.bqn` files, no third implementation to
maintain.

"Done" means: an agent can open any mathematically substantive doc in
this repo and see the BQN one-liner next to the prose definition. It
never has to guess what a construction means algorithmically.


## Canonical vocabulary

These names are defined in `guidance/BQN-AGENT.md` and must be used
consistently everywhere:

| Name           | Domain             | Role                        |
|----------------|--------------------|-----------------------------|
| `NPn2`         | n >= 2, count      | n-primes (algebraic spec)   |
| `Digits10`     | positive integer   | exact decimal digit list    |
| `ChamDigits10` | list of integers   | exact decimal concatenation |
| `DigitCount10` | list of integers   | typographic cost            |
| `LeadingInt10` | positive integer   | integer leading digit       |
| `LD10`         | positive real      | log-based leading digit     |
| `Benford10`    | digit 1..9         | log10(1 + 1/d)             |
| `BinDigits`    | positive integer   | exact binary digit list     |
| `BStream`      | list of integers   | binary concatenation        |
| `V2`           | positive integer   | 2-adic valuation            |

Important note on `NPn2`: it is the algebraic sieve, not the Python/C
stopping rule. If a doc needs the first exactly `K` outputs, write
`K↑ n NPn2 K` and say explicitly that the slice is there to mirror the
implementation's generate-and-collect behavior.


## Phases

### Phase 1 — Public entry docs

These are the docs a reader or agent is most likely to open first. Put
the BQN here before lighter art docs or source-file headers.

**`README.md`**

| Section | Add |
|---------|-----|
| What this is | One compact BQN block or two short blocks introducing `NPn2`, `ChamDigits10`, and `LeadingInt10`. Keep it minimal; README should orient, not teach the whole vocabulary. |
| Key findings | Where the prose names exact uniformity or Benford, point back to the canonical BQN names rather than re-deriving them at length. |

**`core/ACM-CHAMPERNOWNE.md`**

| Section | Add |
|---------|-----|
| Construction > n-prime criterion | `NPn2` with gloss. Note `n = 1` is separate (trial division, no one-liner). |
| Construction > n-Champernowne real | `ChamDigits10` as the exact object; note that Python/C parse `"1." ++ digits` to float. Annotate the table of first-5-n-primes with BQN that makes the algebra visible without overstating the stopping logic: for `n >= 2` rows, use `5↑ n NPn2 5`; keep the `n = 1` row prose-only. |
| The Sieve Table | The sieve quotients are `{(0≠𝕨|·)⊸/ 1+↕𝕩×𝕨}` — the multiplier list before scaling by n. One-liner beside the table. |
| What Is Possible Now > first-digit distribution | `LeadingInt10` for the theorem-level claim. `Benford10` for the reference distribution. |
| What Is Possible Now > epsilon | The epsilon bump formula inline. |

**`experiments/stats/uniformity/UNIFORMITY.md`**

| Section | Add |
|---------|-----|
| Setup | `NPn2` with one short gloss; this doc is a public-facing explanation of the sieve and should not force the reader to infer the algorithm from prose alone. |
| The Champernowne encoding | `ChamDigits10` as the exact digit-stream object, with a short note that Python/C then parse `"1." ++ digits`. |
| Exact uniformity of leading digits | `LeadingInt10` for the theorem-level claim and `Benford10` for contrast. |

**`experiments/shutter/SHUTTER.md`**

| Section | Add |
|---------|-----|
| Opening description or "What makes it non-obvious" | One short BQN reference tying the image back to `LD10` on sums of Champernowne reals, with a sentence that this is the real-valued helper, not the integer theorem-level extractor. |


### Phase 2 — Secondary math docs

These are still central, but they mostly repeat or deepen the Phase 1
math vocabulary.

**`sources/EARLY-FINDINGS.md`**

| Section | Add |
|---------|-----|
| 1. Exact Uniformity | `LeadingInt10` definition. Note that the count is `LeadingInt10¨ 1+↕9999` partitioned by value. |
| 2. The Sawtooth | `ChamDigits10` (what the real is built from). |
| 6. The epsilon Connection | Epsilon formula. Cross-ref to `LD10` caveat in FIRST-DIGIT.md. |


### Phase 3 — Binary and nasties

These extend the vocabulary to base 2 and document edge cases.

**`experiments/binary/BINARY.md`**

| Section | Add |
|---------|-----|
| The Construction | `BinDigits` and `BStream`. Show the stream example as `BStream (8↑ 2 NPn2 8)` so the finite example matches the intended first-8 list. |
| 3. The Bit Stream > bit balance | The `(d+1)/(2d)` formula as a BQN expression on bit-length classes. |
| 4. RLE | `V2` definition. The trailing-zero count of an n-prime `n*k` is `V2 n×k` (which for even n is at least `V2 n`). |
| 5. The epsilon Connection | The epsilon_2 formula: `{(2⋆⁼1+𝕩)-𝕩}` for `m` in [0,1). Note this IS the SlideRule function. |

**`nasties/FIRST-DIGIT.md`**

| Section | Add |
|---------|-----|
| The bug | `LD10` as the exact mathematical definition. Then: "In floating point, `⌊10⋆⁼𝕩` can undercount at exact powers of 10. The Python/C implementations add `+1e-9`." |


### Phase 4 — Experiment and art docs

These are lighter touches. One or two BQN references per doc, pointing
back to the canonical names defined in Phase 1.

**`experiments/art/sieves/SIEVES.md`** — Note that the sieve at row n
is the finite prefix `count↑ n NPn2 count`. Reference `NPn2` and note
that the slice mirrors the implementation's exact-count behavior.

**`experiments/art/sieves/ULAM-SPIRAL.md`** — Sieve density at k counts
divisors n where k is in the output of `n NPn2`. Reference `NPn2`.

**`experiments/art/fabric/FABRIC.md`** — Each row is
`ChamDigits10 (K↑ n NPn2 K)`. Reference both names.

**`experiments/sawtooth/SAWTOOTH.md`** — The sawtooth is the real
parsed from `ChamDigits10`. Reference `ChamDigits10`.

**`experiments/math/arcs/ARCS.md`** — The epsilon bump formula if
it discusses the secant-vs-curve error. Light touch only.

**`experiments/binary/forest/boundary_stitch/BOUNDARY_STITCH.md`** —
`V2` definition for the barcode pattern.


### Phase 5 — Source-file headers

Intentional, not accidental: top-of-file block comments in mathematically
central source files are in scope when they help map the implementation
back to the canonical BQN names. Keep them short. Do not spread this to
plotting code, cipher internals, or anything under `generator/**`.

Last, not first. By this point every doc demonstrates the BQN. The
source files get a brief mapping comment at the top of the module, not
the definitions themselves (those still live in the docs).

**`core/acm_core.py`** — Add a short comment block listing the BQN
names that correspond to each public function:

```
# BQN companions (see guidance/BQN-AGENT.md):
#   acm_n_primes      -> NPn2 (n >= 2 only)
#   acm_champernowne_real -> parse of "1." ++ ChamDigits10
#   acm_digit_count   -> DigitCount10
#   acm_first_digit   -> LD10 (with +1e-9 guard)
#   acm_benford_pmf   -> Benford10
```

**`core/acm_core.c`** — Same mapping in the file header comment.

**`experiments/binary/binary_core.py`** — Same mapping in the module
header comment:

- `binary_stream` -> `BStream`
- `rle` -> prose only unless a readable BQN block exists
- `entry_boundaries` -> prose only unless a readable BQN block exists


## Rules for each insertion

Every BQN block added must satisfy:

1. Names a construction the repo already uses.
2. Uses the canonical name from the table above.
3. Says which file(s) implement it (e.g. "mirrors `core/acm_core.py`").
4. Says whether it is exact math, an implementation mirror, or a
   spec that the implementation approximates (e.g. float truncation).
5. Is readable enough that the gloss can be checked line by line.

Do not:

- Introduce new BQN names not in the canonical table without updating
  `guidance/BQN-AGENT.md` first.
- Add BQN to anything under `generator/**`.
- Add BQN to plotting code, experiment harnesses, or cipher internals.
- Combine multiple constructions into a single dense expression.
- Hide the `n = 1` special case inside `NPn2`.
- Use `NPn2` alone when a doc example needs the first exactly `K`
  results; slice explicitly with `K↑`.
- Use decimal-only helpers like `LeadingInt10` or `LD10` as if they
  were already generic in base `b`.


## Verification

After each phase, verify:

1. Every BQN expression in a doc matches the canonical definition in
   `guidance/BQN-AGENT.md` (name, argument order, semantics).
2. ACM-facing BQN is checked against `tests/test_acm_core.py`,
   `tests/test_acm_core_c.c`, and the behavior of `core/acm_core.py`
   / `core/acm_core.c`.
3. Binary-facing BQN is checked against
   `experiments/binary/binary_core.py` and the examples or invariants in
   `experiments/binary/BINARY.md` and `experiments/binary/forest/MALLORN-SEED.md`.
4. At least one concrete example per doc is checked against the
   implementing file or test suite for that domain.
5. No doc claims BQN computes something that the implementation does
   differently without saying so explicitly. Examples:
   exact concatenation vs. float parse, algebraic `NPn2` vs. exact-count
   stopping logic, and exact `LD10` vs. the implementation's `+1e-9` guard.


## What this does NOT cover

- Executable `.bqn` files. BQN is annotation, not a third codebase.
- BQN in test files. Tests speak Python and C.
- BQN in `generator/**`. The product side stays BQN-free.
- BQN for Speck, SHA-256, Feistel, or any cipher internals.
- BQN for numpy conveniences, CLI, or build instructions.
- New mathematical constructions. BQN documents what exists, it does
  not introduce new ideas.
