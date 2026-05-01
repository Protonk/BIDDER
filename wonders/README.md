# Wonders and the Order of the Substrate

A working catalogue of the things this project has been struck by.

This is not a finding registry. The findings live in `algebra/`, the
experiments live in `experiments/`, the proofs live in their `.md`
files. Everything those documents lose — the *affective* register,
the impressions before resolution, the things that felt found rather
than built, the things that offended — lives here.

The argument: the project's epistemology is closer to natural history
than to modern mathematics. One substrate, catalogued. Some of what
the substrate does is common; some is rare; the rare-and-pretty things
are sometimes telling us something the common things are not. That's
wonder-cabinet logic. The closed-form theorems are the jewels at the
front of the case; this document is the drawer labels.

## The six categories

Each specimen lives in one category at a time. Categories are
*modes of being struck*, not topics. A specimen's category can change;
when it does, the previous category is preserved in the entry's
metadata.

- **Marvel.** Closed forms that came out cleaner than they had any
  right to. Found rather than built.
- **Prodigy.** Findings that appeared to violate the substrate's
  grammar, until they didn't. The initial impression is part of the
  entry.
- **Sport.** Specimens where the algebra behaved a-typically without
  violating any rule. Generic exceptions; alone in their neighbourhood.
- **Curiosity.** Things seen at least twice, suspected to be real, no
  probe yet. Curiosities have a deadline.
- **Monster.** Specimens forced by the construction that look
  pathological by ordinary aesthetic standards. The offense is data.
- **Wonder.** Unresolved. May resist resolution. The longest entries
  belong here, with frank notes on whether the wonder seems likely
  to remain one.

## The entry backbone

Every entry, regardless of category, has the same nine fields:

1. **Name.** Project-native, distinct from any other entry.
2. **Date entered.** When the specimen was named, not when it was
   first noticed.
3. **Category.** Current. With `Previously:` lines if it has moved.
4. **Description.** Two to four paragraphs.
5. **Evidence.** Citations: theorem files, anchor IDs, probe reports,
   lattice files, figures.
6. **Status.** Confidence (anchored / probe-validated / suggestive /
   one-off) and any open dependencies.
7. **Aesthetic note.** What about the specimen strikes the project.
   *Human-written.* Drafts left by the agent layer carry
   `TODO: aesthetic note (human)` on this line; an entry is a draft
   until the note is filled.
8. **Provocation.** What the specimen invites the project to do.
   Noted, not assigned.
9. **Cross-references.** Other specimens this one relates to.
10. **Discovery context.** A short paragraph on how the specimen
    surfaced — spectral, probe, agent, side-effect of unrelated work.
    The workflow is itself a finding.

## Standing rules

**Entering.** A specimen enters when its backbone fields can be
written. Aesthetic notes can carry `TODO` on entry; nothing else can.
Pace: a small handful per quarter is right.

**Reassigning.** When a specimen's understanding changes, its category
gets updated. The previous category is preserved as a `Previously:`
line in the entry; the date is logged. Reassignments are events.

**Aging out.** Curiosities carry a deadline. A curiosity that has
neither been promoted nor produced new evidence by its deadline gets
moved to the graveyard with a one-line note on what it lacked.

## What this isn't

A TODO list. Provocations are noted, not assigned.

A publication record. `algebra/` is the publication record.

A journal. Each entry has the same backbone and is referenceable.
*"See `wonders/marvel-row-ogf-cliff.md` for the discovery context"*
should be a thing one can write.

Aspirational. Entries go in when there's enough to write them.

## Conventions

Filename: `{category}-{slug}.md`. Reassignment is `git mv`, which
preserves history.

Index: `wonders/INDEX.md` is hand-rolled — the cabinet's first vitrine.
Not generated. (If it were scriptable, how wondrous could it be?)

Apparatus (glossary, reassignment log, cross-reference index) earns
its way in when the first entry forces it. Until then, `git log` and
the entries themselves are enough.
