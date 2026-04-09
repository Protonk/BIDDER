# Structural Signatures — Plan

This is the review copy for a small aggregation note:
`STRUCTURAL-SIGNATURES.md`.

The target is not "summarize base 2." The target is narrower:
collect a small packet of binary ACM findings that look stable
enough to reuse elsewhere in the repo without rereading five
separate experiment notes.

## Intended deliverable

Create `STRUCTURAL-SIGNATURES.md` as a compact base-2 synthesis with
four observable sections, each written in the same shape:

- **Claim**
- **Evidence in repo**
- **Relation to other observables**
- **Statistical confidence**
- **Semantic confidence**
- **Falsification**
- **Next check**

The doc should read as a map of what the binary ACM stream is
currently known to carry as signal, not as a gallery and not as a
grand unified theory.

It should also be explicit that these are **four observables arranged
into two larger families**, not four unrelated fundamentals:

- valuation-driven local structure
- order-dependent residual structure

## Scope

The first pass should cover four observables only.

### Two-family framing

The draft should state this up front so it does not accidentally
inflate the finding count.

Family A: **valuation-driven local structure**

- entry-local valuation bookkeeping
- boundary barcode

Family B: **order-dependent residual structure**

- Walsh order-sensitivity
- detrended disparity residual

The four sections stay useful because each family is seen through two
different observables. But the doc should say plainly that section 2 is
not independent of section 1 in the same way section 3 is not
independent of section 4.

### 1. Entry-local valuation signature

Core idea: bit-balance is controlled at per-entry resolution by
`v_2(entry)`, not by monoid label alone.

Primary sources:

- [HAMMING-BOOKKEEPING.md](HAMMING-BOOKKEEPING.md)
- [DETRENDED_RDS.md](disparity/DETRENDED_RDS.md)

Why it belongs:

- this is the cleanest closed-form foothold in the binary tree
- it corrects an easy misreading that still appears in older summaries
- other signatures should be stated relative to this first-order
  bookkeeping, not as if they replace it
- it is the anchor observable for Family A

### 2. Boundary barcode signature

Core idea: entry boundaries carry a visible local `v_2` barcode,
especially for even monoids and powers of two.

Primary sources:

- [BOUNDARY_STITCH.md](forest/boundary_stitch/BOUNDARY_STITCH.md)

Support sources:

- [BINARY.md](BINARY.md)
- [RLE.md](art/rle/RLE.md)

Why it belongs:

- it is the most local and visually legible structural signature
- it connects the valuation story to actual bit windows rather than
  only to averages
- it gives a concrete "what a boundary looks like" section that later
  visual or spectral notes can refer back to
- it is the boundary-local projection of Family A, not a separate
  first principle

### 3. Order-sensitive Walsh signature

Core idea: binary ACM streams carry a real higher-order Walsh family,
and entry order matters for all robust cells currently identified.

Primary source:

- [WALSH.md](forest/walsh/WALSH.md)

Why it belongs:

- it is the strongest current evidence that the stream carries
  structure not exhausted by marginal counts or `v_2(n)` alone
- it gives a clean control split: length + `v_2`, length-only,
  neither control reproduces
- it is already written in a portable-claims style
- it is the spectral observable for Family B

### 4. Detrended disparity residual

Core idea: after subtracting the closed-form drift at per-entry
resolution, a coherent low-frequency residual survives, and shuffle
weakens or destroys it.

Primary sources:

- [DETRENDED_RDS.md](disparity/DETRENDED_RDS.md)
- [KINK_DECOMPRESSION.md](disparity/rds_wavelet/KINK_DECOMPRESSION.md)

Why it belongs:

- it is the disparity-domain companion to Walsh
- it separates "known drift" from "surviving order-dependent signal"
- the recent kink note now says the right conservative thing:
  geometric spacing is disfavored, but stronger spacing claims stay open
- it is the low-frequency / time-domain observable for Family B

## Shared join artifact

The synthesis should contain one compact cross-monoid table. This is
the part the source notes cannot provide in isolation.

Use the monoid panel from
[DETRENDED_RDS.md](disparity/DETRENDED_RDS.md) as the row set, because
it is the broadest controlled panel already in hand.

Proposed columns:

| `n` | `v_2(n)` | `⟨v_2(entry)⟩` | valuation fit status | boundary stripe width | Walsh order metric | residual size |
|---|---:|---:|---|---:|---|---|

Intended meanings:

- `valuation fit status`
  Use the per-entry vs per-monoid comparison already reported in
  `detrended_rds_summary.csv`.
- `boundary stripe width`
  The forced stripe width is `v_2(n)` where the barcode applies.
- `Walsh order metric`
  One scalar derived from existing Walsh artifacts, for example mean
  robust-cell excess over shuffle or presence/absence in the Walsh
  panel. Blank cells are acceptable where the Walsh experiment has no
  measurement.
- `residual size`
  Use `|res_pe|max / √n_bits` from `detrended_rds_summary.csv`.

This table should be allowed to do real work. If it makes one prose
subsection shorter, that is a feature, not a problem.

## Explicit exclusions for v1

These are good topics, but they should stay out of the first
aggregation pass.

- [FINITE-RECURRENCE.md](FINITE-RECURRENCE.md)
  Reason: useful boundary condition, but not a measured signature.
- [forest/epsilon_teeth/](forest/epsilon_teeth/)
  Reason: important theory bridge, but a different kind of result.
- [forest/valuation/](forest/valuation/)
  Reason: better treated as a follow-on synthesis once the core
  signatures are stated cleanly.
- [forest/entropy_landscape/](forest/entropy_landscape/)
  Reason: potentially relevant, but not yet as crisp or reusable as the
  four sections above.
- base-2 art folders
  Reason: they are outputs and interpretations, not the right place to
  establish the claims packet.

One sentence in the intro should still point to
[FINITE-RECURRENCE.md](FINITE-RECURRENCE.md) as a separate boundary
condition on what kind of explanations might exist. It stays outside
the measured-signature packet, but the box should be drawn.

## Source precedence

The base-2 docs are not perfectly synchronized. The aggregation note
should use this precedence rule instead of flattening all notes into
one voice.

1. More specific experiment note beats older umbrella memo.
2. Later correction beats earlier summary.
3. Closed-form derivation and control-based note beat impressionistic
   README language.
4. A result with an explicit control
   (`shuffle`, `length`, `v_2`, or direct model comparison) beats a
   result without one.

In practice:

- [DETRENDED_RDS.md](disparity/DETRENDED_RDS.md) should override older
  per-monoid wording in umbrella notes when discussing bit-balance.
- [KINK_DECOMPRESSION.md](disparity/rds_wavelet/KINK_DECOMPRESSION.md)
  should be used with its current conservative caveats, not with the
  older stronger interpretation.
- [DISPARITY.md](disparity/DISPARITY.md) and
  [README.md](README.md) are framing docs, not authority for disputed
  technical wording.

For the kink subsection specifically: lift only the conservative
headline from [`KINK_DECOMPRESSION.md`](disparity/rds_wavelet/KINK_DECOMPRESSION.md)
that strict geometric spacing is disfavored under the current detector.
Treat the affine discussion there as caveat and follow-up, not as a
headline claim.

## Proposed section outline

The new doc should likely read in this order:

1. **What counts as a structural signature here**
   Short intro defining the term: a reproducible pattern in the binary
   stream that survives controls and is specific enough to guide later
   work.
2. **First-order valuation bookkeeping**
   Closed form and the per-entry correction.
3. **Boundary-local structure**
   What entry joins visibly force.
4. **Order-sensitive higher-order structure**
   Walsh family and shuffle result.
5. **Low-frequency residual structure**
   Detrended RDS and the anti-geometric kink result.
6. **What this packet does not yet explain**
   Short closing section listing open gaps instead of pretending the
   four signatures form a complete theory.

That order matters. The doc should move from local / closed-form /
easier-to-state structure toward higher-order / harder-to-explain
structure.

## Writing constraints

The finished note should:

- stay under roughly 3 to 4 printed pages
- avoid re-deriving proofs already written elsewhere
- avoid image-by-image narration
- avoid strong language like "established" where the underlying note
  still says "conservative reading" or "working conjecture"
- link outward aggressively instead of duplicating long tables
- let the join table replace prose rather than bloat beside it

The note should not become a second `BINARY.md`.

## Execution discipline

Each **Next check** must be script-runnable. It should name either an
existing script or a clearly-scoped new extraction script, plus one
concrete parameter or comparison to vary.

Allowed:

- rerun `walsh.py` or a Walsh post-process at `k = 4` or `k = 5`
- rerun `kink_decompression_n3.py` on `[1k, 5k]` and `[5k, 25k]`
- align `DETRENDED_RDS` excursions against power-of-two crossings

Not allowed:

- "investigate further"
- "needs more work"
- "future study"

## Open choices to decide while drafting

These are the only real judgement calls I expect.

### Whether to include the boundary barcode as a full section

My current answer is yes. It is the simplest local signature, and the
Walsh / disparity sections are easier to trust once the doc reminds the
reader that boundaries really do carry forced visible structure.

### Whether to include the kink-spacing result inside the disparity
section or as a footnote

My current answer is: include it, but keep it small.

Reason:

- it sharpens the statement from "there is a slow residual" to
  "the most visible excursions are not arranged in a strict geometric
  spacing law under the current detector"
- it also models the right epistemic tone for the whole aggregation:
  a real negative result, with careful limits
- and it should be phrased from the conservative headline only, not
  from the stronger spacing speculation the note explicitly backs away
  from

### Whether to mention finite-state nonrecognizability

My current answer is no for v1, except maybe one sentence in the
intro saying the packet is about measured signatures, not the broader
symbolic-dynamics boundary condition.

## Staleness rule

This note should declare when it is stale.

Cheapest workable rule:

- if a source note's portable-claims section changes materially, the
  corresponding section here is stale until reviewed

That implies a small discipline on the source notes:

- where possible, prefer a standardized summary block such as
  `Portable claims`, `What this establishes`, or `What this note
  supports`

`WALSH.md`, `DETRENDED_RDS.md`, and `KINK_DECOMPRESSION.md` already
have close variants of this. `HAMMING-BOOKKEEPING.md` has "The right
summary" near the end. `BOUNDARY_STITCH.md` does not yet have a compact
portable-claims block, so the draft should treat that note with extra
care rather than pretending it is already standardized.

## Minimal workflow

If this plan is approved, I would do the drafting in three passes.

1. Extract one paragraph of portable claims from each source note.
2. Draft the four-section synthesis with explicit caveats.
3. Tighten for overlap, especially between valuation bookkeeping and
   detrended disparity.

No new experiments are required for the first version.

## Desired outcome

After this doc exists, someone landing in `base2/` should be able to
answer four concrete questions quickly:

- What is the closed-form part of the binary signal?
- What does a boundary contribute locally?
- What evidence says order matters beyond marginal counts?
- What residual structure survives after the known drift is removed?

And two action-oriented questions:

- If I want to test whether one of these signatures survives in another
  base or stream family, which observable is the cleanest starting
  point?
- If I want to strengthen the order-dependent claim next, which script
  and parameter sweep should I run first?

If the draft starts answering many more questions than that, it is
trying to do too much.
