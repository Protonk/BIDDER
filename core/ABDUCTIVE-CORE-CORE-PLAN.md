# Abductive key — rewrite plan (leaky-parameterization framing)

A staged plan for updating `core/ABDUCTIVE-KEY.md` now that we have
three independent "obvious in retrospect" extractions of the row
parameter `n_k` and a documented pattern of being surprised by them.
This file is the plan, not the edit. Execute when ready.


## Goal

Apply *Option 2* from the strategic discussion:

- Rewrite the existing "## The rank-1 view" section so it leads with
  the **leaky parameterization** observation rather than with the
  rank-1 outer product. The outer product remains as the canonical
  consequence; a parallel extraction (the first-column / row-minimum
  fact) is added as a second consequence.
- Expand the existing "## A note on visibility" section by one
  paragraph at the end, acknowledging that the same kind of
  "structurally trivial inversion" has now surprised us three
  times, with cross-references to the two new instances.
- Do **not** touch any other section. Setup, Claim, Proof, Why the
  hypotheses matter, In BQN, Examples all remain exactly as
  written. The document title stays "Abductive Key" and the
  document's original load-bearing result remains the
  diagonal-divides-by-position recovery.


## The metaphor: leaky parameterization

The right framing is "**the n-prime row is parameterized by a single scalar
`n_k`, and that scalar leaks out of every available channel**."

- Channel 1: the diagonal `(k, k)` divided by `k` returns `n_k`
  (the abductive key itself).
- Channel 2: the first column cell `(k, 1)` *is* `n_k`, because
  `j_1(n_k) = 1` for any `n_k ≥ 2`.
- Channel 3: in any sorted reading of a row's cells (or a multi-set
  containing them), the smallest entry of row `k` is `n_k` — same
  fact as channel 2, applied without column labels.

These are not three keys. They are three leaks of the same scalar
through the same loose lock. The hard work isn't finding the leaks;
it's noticing in advance that the parameterization is loose enough
that they're all there. We should expect more leaks. We should not
expect to predict in advance what they look like — we have a perfect
record so far of being surprised by them.

The "skeleton key" framing (one tool, many locks) was tempting but
wrong: it implies the keys are the clever objects, when really the
*lock* is the clever object — it's so weakly structured that almost
any reasonable extraction works. Naming the metaphor "leaky
parameterization" keeps the spotlight on the structure rather than
on the cleverness of the extractions, and it leaves room for the
inevitable next surprise without committing the document to a
predictive claim it can't back up.


## What changes

### 1. Rewrite "## The rank-1 view"

The current section has four paragraphs:

1. The shape of the rank-1 region as a function of the row list
2. The outer product framing and the diagonal-divides-by-position
   recovery
3. The "wearing two hats" observation about strict ascent
4. The "key" closing framing and the lossy-sieve / identification
   use cases

The rewrite keeps paragraphs 1 and 3 unchanged. Paragraph 2 gets a
new lead sentence that names parameterization explicitly. A new
paragraph about the second extraction goes between paragraphs 2
and 3. Paragraph 4's closing framing is rewritten to use leaky
parameterization.

#### Proposed new lead for paragraph 2

Replace the current paragraph 2 opening line with:

> The n-prime row at position `k` is parameterized by a single
> scalar: `n_k`. Every cell of row `k` is the function
> `k' → j_{k'}(n_k) · n_k` of that one parameter, where
> `j_{k'}(n) = k' + ⌊(k' − 1)/(n − 1)⌋`. Anything that recovers
> `n_k` recovers the row. In the rank-1 region the function
> simplifies to `T[k][k'] = k' · n_k`, and the entries are
> literally an outer product of the column vector `(1, 2, …, N)`
> and the row vector `(n_1, …, n_N)`...

The rest of paragraph 2 (the diagonal-divides-by-position result)
continues as in the current version.

#### Proposed new paragraph 2.5 (insert between paragraphs 2 and 3)

> A second extraction of `n_k` is even more elementary. The cell
> `T[k][1] = j_1(n_k) · n_k` equals `n_k` for any `n_k ≥ 2`,
> because `j_1 = 1`. So the first cell of every row is its row
> label, full stop. Two settings make use of this. In the cascade
> picture (`experiments/acm/diagonal/cascade_key/`), once `n_k`
> is decoded by any means, every later cell of row `k` is
> computable from `k'` and `n_k` alone via `j_{k'}(n_k) · n_k` —
> the entire row, including the cells past the rank-1 region,
> unlocks from a single value. In the unordered-multi-set picture
> (`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`),
> the row labels of an `N × N` n-prime table are exactly the
> row-wise minima of the cell values, and a greedy "take the
> smallest, strip its row, repeat" algorithm reconstructs the row
> list from the unordered multi-set with zero hints. The greedy
> theorem, its proof, and an empirical battery of 15 row lists
> live in `cantor_walk/verify_greedy.py` and the same folder's
> `UNORDERED-CONJECTURE.md` addendum.

Cross-references in this paragraph are deliberate and inline. The
cascade folder is where extraction-with-positions is demonstrated;
the unordered conjecture is where extraction-without-positions is
demonstrated; the addendum is where the pattern of repeated
surprises is recorded.

#### Proposed rewrite of paragraph 4

Replace the existing closing paragraph with:

> The dual observation is why we keep being surprised by results in
> this area. We do not have a single key that opens many locks; we
> have a single *lock* — "what is `n_k`?" — that is so weakly
> structured the parameter leaks out of every channel we look at.
> Each of the extractions above uses a different channel: the
> diagonal divided by position (the abductive key), the first
> cell of each row (the cascade key), the row-wise minimum of the
> cell values (the greedy extraction). They are not three different
> insights — they are three instances of the same observation,
> namely that the n-prime row is *rank-1 in the sense that it
> depends on one scalar*, and rank-1 inversions are all easy. The
> hard problem in this area isn't recovering `n_k`; that is free
> in at least two structurally distinct ways. The hard problem is
> noticing in advance that the construction has this much
> structure, so we stop framing recovery questions as if they were
> harder than they are.
>
> The lossy-sieve use of this inverts the usual sieve cost model:
> one parameter, no memory, factorization included. The
> identification use — treating an integer sequence as a one-pass
> test that asks "is this an ACM family in disguise?" — is the one
> most likely to surprise in another context.

The two existing sentences about lossy-sieve and identification
move down to the second paragraph here. They are still useful and
they should not be cut.


### 2. Expand "## A note on visibility"

Append one paragraph at the end of the existing section. The
existing two paragraphs (about how the lemma is elementary and the
discovery took several sittings) stay exactly as they are.

#### Proposed new closing paragraph

> We have now found this same kind of "obvious in retrospect"
> inversion three times. The original abductive key (this
> document) was the first. The cascade decoding of plot 4
> (`experiments/acm/diagonal/cascade_key/`) was the second, where
> we initially framed "do later patches admit their own keys" and
> the answer turned out to be "no — there's one key and it opens
> every lock in the row." The row-wise-minimum extraction in the
> unordered conjecture
> (`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`)
> was the third, where we initially proposed an `O(log N)`-hint
> backtracking solver and the actual answer was that greedy
> reconstructs from the multi-set with zero hints. Each time we
> framed the question as if we did not know the n-prime structure,
> and each time the structure made the question free. The
> "Notes on a pattern" section of the unordered-conjecture
> document records this and proposes a discipline for next time:
> before posing a recovery experiment in this area, write the
> half-line description of what the trivial extraction would be
> and check whether it already works. The same document's
> immediately-following "**The knife-edge: productive triviality**"
> section adds the cautious response — the leaky parameterization
> is either a *foothold* (rich consequences from a trivial
> surface) or a *perimeter* (no structure beneath the surface),
> and we are operating in a constructed space where the perimeter
> risk is sharper than usual. We do not yet know whether this
> pattern is a *principle* (every recovery question collapses) or
> a *coincidence* (we have found three accidents). Three is too
> small a number to choose between those, but it is large enough
> to expect a fourth — and large enough that we should ask, before
> leaning on any future result that depends on the parameterization,
> whether the result gives us a quantity not already in the
> definition.


### 3. What does NOT change

- **Title.** "Abductive Key" stays. Renaming to "Abductive
  Principle" or similar would overcommit to the pattern being
  general; we have three examples, not a theorem.
- **Setup / Claim / Proof / Why-the-hypotheses-matter / In-BQN /
  Examples sections.** All unchanged. The original abductive key
  result is still the canonical content of the document.
- **The "wearing two hats" observation in paragraph 3 of the
  rank-1 view section.** This stays exactly as written. It is
  the strongest single sentence in the document and should not be
  touched.
- **Section ordering.** No new top-level sections. The rewrite
  fits inside two existing sections.


## Cross-references collected

These should be the canonical pointers from the rewritten ABDUCTIVE
document. They are inline in the proposed paragraphs above; this
list is for the executor to double-check paths exist before
applying the edit.

| reference | what it is | where it appears in the rewrite |
|---|---|---|
| `experiments/acm/diagonal/cascade_key/` | plot 4: rank-1 patch staircase, cascade decoding visible as a heatmap | new paragraph 2.5 of "rank-1 view"; new closing paragraph of "note on visibility" |
| `experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md` | the greedy-extraction theorem, the addendum, the "notes on a pattern" section | new paragraph 2.5 of "rank-1 view"; new closing paragraph of "note on visibility" |
| `experiments/acm/diagonal/cantor_walk/verify_greedy.py` | empirical verification of the greedy theorem on 15 row lists | new paragraph 2.5 of "rank-1 view" |

These three cross-references are sufficient. The rewrite should
not point to plot 3 (the lattice scatter) or to `CANTORS-PLOT.md`,
because the abductive key itself doesn't depend on the wider
garden — it depends on the cascade and the unordered conjecture
specifically. Adding more cross-references would dilute the focus.

Verification before edit:

```
ls core/ABDUCTIVE-KEY.md
ls experiments/acm/diagonal/cascade_key/cascade_grid.png
ls experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md
ls experiments/acm/diagonal/cantor_walk/verify_greedy.py
```

All four should exist. If any is missing, the edit needs adjustment
before proceeding.


## Risks and notes

### Risk 1: overclaiming generality

We have three examples. The temptation is to write "the n-prime
construction is uniformly invertible from any partial view," which
is *suggested* by the pattern but not *proven*. The rewrite
deliberately avoids that claim. The closing paragraph of the "note
on visibility" expansion explicitly says "we do not yet know
whether this pattern is a principle or a coincidence; three is too
small a number." Keep that hedge in. The fourth attempt might
prove the pattern wrong, and the document should be readable
without embarrassment if it does.

### Risk 2: making the abductive key feel like an afterthought

Option 2 deliberately leads with parameterization and demotes the
outer product framing to "one consequence." There is a risk that a
fresh reader will see the new paragraph 2.5 (the second extraction)
and conclude that the abductive key is just a corollary of an
elementary observation. Two countermeasures:

- The Setup / Claim / Proof sections still come first in document
  order. A fresh reader sees those before the rank-1 view section,
  and the abductive key is presented as the central result there.
- The closing paragraph of the rewrite explicitly says "the
  abductive key" and "the cascade key" and "the greedy extraction"
  as three named instances. The original result keeps its name.

If the reader feels the original result has been demoted, that
is mostly correct: it has been *contextualized* as one of several.
But the name remains canonical and the proof remains in the
document's main spine.

### Risk 3: the paragraph-2.5 insert feels grafted

A new paragraph in the middle of an existing section can feel
clumsy. To mitigate, the proposed text deliberately uses the same
voice as the surrounding paragraphs (terse, mathematical, parallel
constructions). It also explicitly grounds itself in the
parameterization framing introduced in the rewritten paragraph 2,
so there's continuity across the section.

If after applying the edit the paragraph reads as grafted, the
fix is to merge it more tightly into paragraph 2 — fold the
"second extraction" observation into the same paragraph as the
outer product, with both presented as parallel consequences of
the parameterization. That is a slightly more aggressive rewrite
and should be tried only if the staged version reads badly.

### Note: word "rank-1"

The phrase "rank-1" is doing two jobs in the rewrite. The first is
the usual linear-algebra sense (a matrix that factors as `u v^T`).
The second is a looser sense: "depends on a single scalar
parameter." These are related but not identical. The rewrite uses
both senses and signposts the looser one explicitly: "rank-1 in
the sense that it depends on one scalar." Keep the signpost. A
reader who knows linear algebra will catch the looser usage if
it's marked.

### Note: BQN section

The "## In BQN" section already implements the rank-1 leading
triangle as one line of code. It does not need updating. The new
"second extraction" — first cell equals row label — is one
character of BQN if you wanted (`⊏ T[k]` or similar) but adding
it to the BQN section is not necessary. The current BQN section
serves its purpose as an executable gloss of the proof.


## Execution checklist

When applying the plan:

1. Read the current `core/ABDUCTIVE-KEY.md` once end-to-end to
   confirm the section structure matches what this plan assumes.
2. Verify the three cross-reference paths exist (see the
   verification block above).
3. Apply the rewrite to "## The rank-1 view":
   - Update the lead sentence of paragraph 2.
   - Insert the new paragraph 2.5.
   - Replace paragraph 4 with the new closing paragraphs.
4. Apply the expansion to "## A note on visibility":
   - Append the new closing paragraph at the end of the section.
5. Re-read the rewritten sections in document context. Specifically
   check that:
   - Paragraph 2.5 doesn't read as grafted.
   - The cross-references are clickable / consistent with
     repository convention.
   - The "wearing two hats" observation in paragraph 3 still
     flows from paragraph 2's lead.
6. Do not touch any other section.


## Open question (for after the edit)

Is there a fourth extraction worth naming? The three we have all
exploit `T[k][1] = n_k` (extractions 2 and 3) or the rank-1 outer
product structure of the leading triangle (extraction 1). A fourth
would have to use a third structural property. Candidates:

- The product of all cells in row `k` is `n_k^N · ∏_{k'} j_{k'}(n_k)`,
  which depends on `n_k` in a more complex way but is a single
  number that determines `n_k`. Not a *trivial* extraction, but a
  lossy-then-recoverable one.
- The GCD of all cells in row `k` is `n_k` (since every cell is a
  multiple of `n_k` and `j_1 = 1` ensures `n_k` itself is among
  them). Trivial. Could be a fourth named extraction.
- The sum of all cells in row `k` is `n_k · ∑_{k'} j_{k'}(n_k)`,
  which is `n_k · S(N, n_k)` where `S` is a known function.
  Recoverable but slightly more involved.

Of these, the GCD extraction is the cleanest and the most "in the
spirit" of the existing three. It's worth flagging now in case we
hit a fourth surprise — the "Notes on a pattern" section could
then say "we predicted the GCD extraction in the rewrite plan."
Or we could just add it now as a fourth example and skip the
prediction.

This is for after the edit, not part of the edit itself. The plan
above is locked at three extractions for now.
