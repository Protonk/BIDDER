# Collection Plan

Plans for two artifacts derived from the theory survey in
[`SURVEY.md`](SURVEY.md): per-shelf summaries (not yet written)
and the curated collection at [`COLLECTION.md`](COLLECTION.md)
(built, pointing into the survey until the summaries catch up).
This file holds only the plans — the survey itself is elsewhere.


## Shelf Summaries

This is a plan for how per-shelf summaries will be written, not
the summaries themselves. The goal is to make the theory docs
easier to enter: a new reader — or a returning one after a gap —
should be able to get what a doc carries, how it fits, and its
current status without opening the file.
[`SURVEY.md`](SURVEY.md) puts the docs in reach; the summaries
will put the *content* in reach.

### Deliverables

Two products, both derived from the shelf structure in
[`SURVEY.md`](SURVEY.md).

1. **Summaries.** One file per shelf, each entry hand-written at
   a length appropriate to the shelf's role. Summaries are entry
   points, not substitutes — the source docs stay load-bearing.
2. **Index.** A stripped-down hook list derived from the plan and
   the summary entries. Usable as the daily-driver entry point
   when a reader does not yet know what they are looking for.
   [`SURVEY.md`](SURVEY.md) is the catalog-with-provenance; the
   index is the quick lookup.

### Proposed location

```
summaries/
  INDEX.md       stripped-down hook list
  SHELF-A.md     core collection — longest, most structured
  SHELF-B.md     strong satellites
  SHELF-C.md     context and scaffolding
  SHELF-D.md     gallery and side artifacts
  SHELF-E.md     companion code prose
```

A new top-level `summaries/` directory, sibling of `core/` and
`experiments/`. Bidirectional pointers: each source doc gains a
`Summary:` line in its "See also" section pointing at its entry;
each summary entry begins with the path back to its source.
Grouped entries are a Shelf D exception — see the Shelf D
template below for the anchor semantics.

### Shape per shelf

Different shelves carry different content, so the summary template
varies. Lengths are targets, not caps.

**Shelf A — 18 entries, ~200–300 words each.** Four sub-templates,
one per sub-section of Shelf A in [`SURVEY.md`](SURVEY.md).

*Exact theorem* (5 entries):
- **Claim.** The theorem statement in one or two sentences, using
  the doc's own vocabulary.
- **Mechanism.** One paragraph on the proof shape (one-line
  counting argument, divmod, induction on ascent, Euler-Maclaurin,
  etc.).
- **Depends on / supports.** Nearest upstream and downstream docs.
- **Status.** Proved; with or without open follow-ups.

*Meta-theory / discipline* (3 entries):
- **Thesis.** The single observation the doc is built around.
- **Case studies.** The specific worked examples that support it
  (three surprises, four layers, frame-level corrections).
- **Discipline prescribed.** The rule the doc asks future work to
  follow.
- **See also.**

*Interface bridge* (4 entries):
- **Bridges.** Which layer connects to which (cipher API to
  integer-block lemma; root to both paths; tests to claims).
- **Presents.** The forms each claim is given (English / Python /
  BQN; Proved / Measured / Not claimed).
- **Excludes.** What the doc is explicit about not covering.
- **See also.**

*Frontier note* (6 entries):
- **Status.** Proved / conjectured / audited down / first findings.
- **Current evidence.** One paragraph on what supports or qualifies
  the status.
- **Depends on.** The upstream theorem or construction.
- **Open questions.** One or two unresolved threads.

**Shelf B — 18 entries, ~100–200 words each.** Single template:
- **Setup.** Stream, monoid panel, band, cipher, scale.
- **Headline.** The single result — a number, a negative finding,
  a corrected reading, a closed form.
- **Control.** What the result is tested against (shuffle, FPC,
  white-noise panel, ideal null).
- **Open.** The one most important unresolved question.

**Shelf C — 15 entries, 30–80 words each.** Pointer-style. Name the
discipline the doc enforces or the cluster it indexes and point
into that cluster. No claim / mechanism structure — overkill for a
plan or README. Several entries can compress to one line.

**Shelf D — 13 entries, 30–60 words each.** Line worth lifting.
Usually the existing `hook:` from the survey plus one phrase naming
the takeaway a reader should carry. Grouped entries are allowed on
this shelf only (the fabric family becomes one entry with
sub-bullets). A grouped entry uses a header anchor (e.g.
`#fabric-family`) and opens with multiple `source:` lines, one per
constituent doc; each source doc's `Summary:` back-pointer targets
that group anchor rather than a per-doc anchor.

**Shelf E — 8 entries, 20–50 words each.** Cross-reference. Name
the module, the canonical BQN name it corresponds to (for `core/`),
and the test or theorem it supports. Pointers back into Shelf A,
not standalone summaries.

### Order of operations

1. **Shelf A first.** The collection nucleus; the summaries here
   do the most work. 18 entries, ~4,000–5,400 words total. Within
   Shelf A, write the five exact theorem docs first (clearest
   shape), then the three meta-theory docs, then the four
   interface bridges, then the six frontier notes (hardest, mixed
   shape).
2. **Shelf B second.** The "depends on / supports" pointers in
   Shelf A entries will target Shelf B in several places; writing
   B with those pointers in hand keeps the references aligned.
3. **Shelves C, D, E in any order.** Shorter, independent,
   probably one session each.
4. **INDEX.md last.** Derived from the five shelf files, not
   written from scratch. Index hooks should mirror the shelf-entry
   opening lines so the two products cannot drift silently.

### Audit discipline

Lifted from `STRUCT-SIG-PLAN.md`'s staleness rule: a summary is
stale when the source doc's portable-claims block (or equivalent
compact summary section) changes materially. For docs without an
explicit portable-claims block, a summary is stale when its hook
line in [`SURVEY.md`](SURVEY.md) would need to be rewritten —
this ties staleness to the survey itself, which every shelf
entry has by construction. Each summary entry gets a `source:`
line and a `last reviewed:` line at the bottom.
No automatic regeneration — a summary written after *reading* the
source is stronger than one generated *from* it. The WALSH doc's
audit policy is the canonical precedent: the policy is not to
depend on summary design.

### Out of scope for this phase

- **Auto-generation.** Summaries are hand-written. The repo already
  distrusts automated summaries; the WALSH audit trail exists
  specifically because an earlier summary that looked clean had
  already destroyed the information needed to catch a wrong
  reading.
- **Replacing source docs.** Summaries are entry points. Nothing
  in `core/` or `experiments/` moves or shrinks.
- **Cross-shelf cross-cuts.** The correction-discipline cross-cut
  noted in the earlier review is a separate future product if
  wanted. One thing at a time.
- **A new notation layer.** Summaries use the source docs'
  vocabulary and the canonical BQN names from
  `guidance/BQN-AGENT.md`. No new glossary.
- **Rewriting the survey or this plan.** [`SURVEY.md`](SURVEY.md)
  and COLLECTION-PLAN.md are parallel to the summaries; normal
  updates to either continue as the work grows, but writing
  summaries does not itself force a rewrite of the catalog or
  the plans.


## COLLECTION.md creation

This section holds the plan that produced
[`COLLECTION.md`](COLLECTION.md) — a curated reader's guide to
the theory work documented in [`SURVEY.md`](SURVEY.md). Not a
second survey, not a table of contents, not a summary aggregator.
An editorial artifact that commits to a reading of what the body
of work is for and how to enter it.

**Status: built ahead of the summaries.** The plan originally
listed the per-shelf summaries as a prerequisite, on the
assumption that chapters in the collection would cite summary
entries as their content. COLLECTION.md was built before the
summaries exist, so its entries currently point directly into
[`SURVEY.md`](SURVEY.md) anchors. When the summaries are
written, the COLLECTION.md pointers should be updated to target
the summary entries instead.

### Three-layer reader's experience

The survey, summaries, and collection form three layers with a
clean division of labour:

- **[`SURVEY.md`](SURVEY.md)** — navigation. "Where is X? What
  shelf?"
- **`summaries/`** — content. "What does X say?"
- **[`COLLECTION.md`](COLLECTION.md)** — argument. "Why does X
  matter, and how does it fit with Y?"

A doc can appear in all three without duplication because each
layer answers a different question.

### Outline (as built)

- **Preface.** ~1 page. What this repo is, what it isn't, what
  distinguishes it from the literature it borrows from.
- **Themed chapters** — not genre shelves. Five chapters as
  built: *The Construction* / *The Generator* / *The Recovery
  Thread* / *The Binary Frontier* / *The Discipline*.
- **Reading paths.** Five linear sequences through the chapters
  for different entry points (math-first, engineer-first,
  skeptic-first, meta-first, "if you have one hour").
- **Cross-cuts** that the shelf structure cannot surface —
  promoted to first-class sections, not footnotes. The leaky
  parameterization thread; the correction/retraction discipline
  across ~8 docs; the three-layer English/Python/BQN presentation
  format; the "constructed space" epistemic caveat from
  UNORDERED-CONJECTURE. The hot-vs-cold agent discipline from
  PAIR-PROGRAMMING is folded into Chapter 5.
- **Selection rule.** Explicit. The collection is smaller than
  the survey on purpose (~22 docs versus the survey's ~70+).
  Rule: *a doc earns a slot if the collection's argument depends
  on it, or if reading it materially changes what you expect
  from the rest.*

### Open questions (flagged for future revisits)

- **Single file or directory?** COLLECTION.md at root was
  chosen for v1 (one landing page, forced compactness) over
  `collection/` with one file per chapter (scales better,
  mirrors `summaries/`). Revisit if the collection grows.
- **Thesis preface or descriptive preface?** Thesis was chosen
  — the preface commits to a reading rather than describing
  the repo neutrally. The alternative would have been blander
  but safer.
- **In-place editorial versus cited content.** v1 carries
  ~30–40% in-place editorial prose with ~60–70% structured
  pointers; with the summaries built, the ratio can shift
  further toward citation.
- **Relationship to the root README.** The README currently
  does not point at COLLECTION.md. Whether to add a pointer, or
  to let COLLECTION.md supersede the reader-facing parts of the
  README, is an open question.
- **Audit discipline.** COLLECTION.md currently inherits the
  summaries' staleness rule by proxy (its pointers target
  survey entries, and survey hooks are the staleness trigger).
  Whether it needs its own rule is open.
