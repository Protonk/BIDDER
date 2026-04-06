# Regrade Plan

This plan reorganizes `experiments/` by what an experiment actually
depends on, not by its visual style or by when it was added.

The goal is simple: when someone opens a folder, they should be able to
answer three questions immediately.

1. What is the source object?
2. What base is it in, if base matters?
3. Is this a finished experiment family, a theory note, or a future
   holding area?

## Target Top Level

The proposed top-level split is:

```text
experiments/
  README.md
  REGRADE-PLAN.md
  acm-champernowne/
    README.md
    base10/
      README.md
      art/
      sawtooth/
      shutter/
      stats/
    base2/
      README.md
      art/
      disparity/
      forest/
  bidder/
    README.md
    art/
    dither/
    reseed/
    stratified/
    digits/
  math/
    README.md
    arcs/
  future/
    README.md
    wibblywobblies/
```

## Classification Rules

These rules should decide placement.

### `acm-champernowne/`

Use this when the experiment's source is the ACM-Champernowne
construction itself.

- If it builds decimal digit streams or decimal Champernowne reals, it
  belongs under `base10/`.
- If it builds binary concatenations or binary-derived objects, it
  belongs under `base2/`.
- Art vs stats vs shutter vs sawtooth are secondary subdivisions inside
  the source/base bucket.

### `bidder/`

Use this when the experiment's primary source is BIDDER output, even if
the experiment later compares that output to numpy or to ACM-inspired
controls.

- Base stays local to the experiment unless a whole family splits by
  base.
- The important fact is that the source is already scrambled and exactly
  uniform by design.

### `math/`

Use this for base-generic theory or geometric analysis that is not best
understood as "an experiment on one concrete stream family."

- This is where reusable theory lives.
- If the content later grows a direct source-family home, it can move
  out.

### `future/`

Use this for active ideas, naming work, speculative framing, or half-set
theory that does not yet have a stable home.

- This is a holding area, not a graveyard.
- Material should leave `future/` once its real home is obvious.

## Documentation Spine

The new tree should have a small number of orientation docs.

### Required index docs

- `experiments/README.md`
  - one-page map of the whole tree
  - explains the source-first classification rule
- `experiments/acm-champernowne/README.md`
  - explains why ACM splits by base
- `experiments/acm-champernowne/base10/README.md`
  - points to sawtooth, shutter, stats, and art families
- `experiments/acm-champernowne/base2/README.md`
  - points to `forest/`, `art/rle/`, and `disparity/`
- `experiments/bidder/README.md`
  - explains that these are post-scramble / generator-facing
    experiments
- `experiments/math/README.md`
  - explains that these are source-agnostic or base-generic
- `experiments/future/README.md`
  - explains that contents are provisional

### Existing family docs to preserve as anchors

These should stay the primary topic docs inside their families.

- `sawtooth/SAWTOOTH.md`
- `shutter/SHUTTER.md`
- `stats/uniformity/UNIFORMITY.md`
- `binary/BINARY.md` or its successor under `base2/`
- `art/fabric/FABRIC.md`
- `art/fabric/inverted/INVERTED.md`
- `art/fabric/noising/NOISING.md`
- `binary/forest/*` docs

The regrade should not flatten those topic docs into one central wiki.
The index docs should point to them.

## Naming Guidance

Some current names are too vague and should not survive unchanged.

- `others/` should become `bidder/digits/` or `bidder/other_digits/`
  rather than staying `others/`
- `binary/` should become a base classification, not a parallel world
- `future/` should be explicit about being temporary

## Current Leaf Mapping

This is the practical regrade map from the current tree.

| Current leaf | Category | Proposed destination |
|---|---|---|
| `experiments/sawtooth/` | ACM-Champernowne base-10 | `experiments/acm-champernowne/base10/sawtooth/` |
| `experiments/shutter/` | ACM-Champernowne base-10 | `experiments/acm-champernowne/base10/shutter/` |
| `experiments/stats/uniformity/` | ACM-Champernowne base-10 in practice | `experiments/acm-champernowne/base10/stats/uniformity/` |
| `experiments/stats/compare/` | ACM-Champernowne base-10 | `experiments/acm-champernowne/base10/stats/compare/` |
| `experiments/art/collapse/` | ACM-Champernowne base-10 | `experiments/acm-champernowne/base10/art/collapse/` |
| `experiments/art/fabric/noising/` | ACM-Champernowne base-10 | `experiments/acm-champernowne/base10/art/fabric/noising/` |
| `experiments/art/fabric/inverted/` | ACM-Champernowne base-10 | `experiments/acm-champernowne/base10/art/fabric/inverted/` |
| `experiments/art/sieves/` | ACM-Champernowne base-10 | `experiments/acm-champernowne/base10/art/sieves/` |
| `experiments/art/sunflower/` | ACM-Champernowne base-10 | `experiments/acm-champernowne/base10/art/sunflower/` |
| `experiments/art/rle/` | ACM-Champernowne base-2 | `experiments/acm-champernowne/base2/art/rle/` |
| `experiments/binary/disparity/` | ACM-Champernowne base-2 | `experiments/acm-champernowne/base2/disparity/` |
| `experiments/binary/forest/violin/` | ACM-Champernowne base-2 | `experiments/acm-champernowne/base2/forest/violin/` |
| `experiments/binary/forest/autocorrelation/` | ACM-Champernowne base-2 | `experiments/acm-champernowne/base2/forest/autocorrelation/` |
| `experiments/binary/forest/one_bias/` | ACM-Champernowne base-2 | `experiments/acm-champernowne/base2/forest/one_bias/` |
| `experiments/binary/forest/entropy_landscape/` | ACM-Champernowne base-2 | `experiments/acm-champernowne/base2/forest/entropy_landscape/` |
| `experiments/binary/forest/epsilon_teeth/` | ACM-Champernowne base-2 | `experiments/acm-champernowne/base2/forest/epsilon_teeth/` |
| `experiments/binary/forest/boundary_stitch/` | ACM-Champernowne base-2 | `experiments/acm-champernowne/base2/forest/boundary_stitch/` |
| `experiments/binary/forest/rle_spectroscopy/` | ACM-Champernowne base-2 | `experiments/acm-champernowne/base2/forest/rle_spectroscopy/` |
| `experiments/reseed/` | BIDDER | `experiments/bidder/reseed/` |
| `experiments/dither/` | BIDDER | `experiments/bidder/dither/` |
| `experiments/stratified/` | BIDDER | `experiments/bidder/stratified/` |
| `experiments/others/` | BIDDER | `experiments/bidder/digits/` |
| `experiments/art/contamination/` | BIDDER | `experiments/bidder/art/contamination/` |
| `experiments/math/arcs/` | Math | `experiments/math/arcs/` |
| `experiments/wibblywobblies/` | Future for now | `experiments/future/wibblywobblies/` |

## Non-Leaf Notes

Some current non-leaf directories also need a home.

- `experiments/art/fabric/`
  - should move as a family root to
    `experiments/acm-champernowne/base10/art/fabric/`
  - this carries root-level files (4 scripts, 3 PNGs, and `FABRIC.md`)
    in addition to the `inverted/` and `noising/` subdirectories listed
    in the leaf mapping
  - its current subdocs already justify that family structure
- `experiments/binary/`
  - should stop being a sibling taxonomy
  - conceptually it becomes `acm-champernowne/base2/`
- `experiments/stats/`
  - should become a subdivision inside the relevant source/base bucket,
    not a separate top-level axis
- `experiments/art/`
  - should also stop being a separate top-level axis
  - art should live under the source family it renders

## Root-Level Files

Some current directories contain root-level files that the leaf mapping
does not cover. These need explicit destinations.

- `experiments/binary/binary_core.py`
  - shared utility for stream generation, RLE, and entry-boundary
    tracking; imported by scripts across `binary/forest/` and `art/rle/`
  - should move to
    `experiments/acm-champernowne/base2/binary_core.py`
  - Phase 3 import fixups depend on this landing first
- `experiments/binary/FINITE-RECURRENCE.md`
  - theory doc (finite automata vs. binary Champernowne streams)
  - scoped to binary despite the general claim, so it belongs under
    `experiments/acm-champernowne/base2/FINITE-RECURRENCE.md`
    rather than `math/`
- `experiments/art/PITCH.md`
  - curatorial overview of five ACM art pieces; four of the five land
    under `acm-champernowne/base10/`
  - should move to
    `experiments/acm-champernowne/base10/art/PITCH.md`
  - its cross-reference to `math/arcs/` will need a link update in
    Phase 3

## Migration Principles

The move should be structural, not interpretive.

- Move whole families first.
- Do not rewrite experiment content while moving it.
- Preserve filenames where possible.
- Fix imports and doc links only after the directories settle.
- Avoid mixed-category folders.

If a folder contains one dominant source and one control, classify by
the dominant source. Controls do not get to define the directory.

## Proposed Order Of Operations

### Phase 1: Create the new skeleton

- create the top-level destination directories (empty)
- leave the current folders in place during this phase

### Phase 2: Move the obvious families

- move all ACM base-10 families
- move all ACM base-2 families
- move all BIDDER families
- move `math/arcs`
- move `wibblywobblies` into `future/`

### Phase 3: Repair links and imports

- update relative import paths in scripts
- update links inside family docs
- update any root references that point to old paths

### Phase 4: Add root orientation docs

- write the small `README.md` files after the tree exists
- keep them short and navigational

## Desired End State

At the end of the regrade, "what is this experiment?" should be obvious
from the path alone.

Examples:

- `experiments/acm-champernowne/base10/shutter/`
  means decimal ACM source, un-scrambled
- `experiments/acm-champernowne/base2/forest/rle_spectroscopy/`
  means binary ACM source, un-scrambled
- `experiments/bidder/dither/`
  means generator output, already scrambled
- `experiments/math/arcs/`
  means theory, not one concrete source stream
- `experiments/future/wibblywobblies/`
  means not yet fully integrated

That is the whole point of the regrade.
