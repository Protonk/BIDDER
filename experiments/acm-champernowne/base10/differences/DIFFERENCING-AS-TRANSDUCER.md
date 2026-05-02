# Differencing as Transducer

A note on what `δ = C_Bundle − C_Surv` actually does, prompted by
the right question — *could catastrophic cancellation be to blame?*
The surface answer is no; the experiments use exact `Fraction`
arithmetic and there is no floating-point ULP loss. The underlying
answer is yes, in an exact-arithmetic analogue: subtracting two
digit-concatenated streams of different lengths *transduces*
atom-level structure into digit-level noise. EXP01 and EXP02 read
out the noise. The relation lives somewhere the transducer can't
reach.

## The phenomenon

`C_Bundle` and `C_Surv` are digit concatenations of *different-length*
atom sequences (3,600 atoms vs 1,338 survivors at the Two Tongues
panel). Subtracting them as reals on a common denominator aligns
them by **digit position**, not by **atom**. The moment the bundle
includes an atom the survivor skips, the alignment drifts:

| digit pos | bundle digit | survivor digit | what these are |
|---|---|---|---|
| 1 | `2` | `2` | both atoms = `2` |
| 2 | `6` | `2` | bundle atom-2 = `6` ; survivor atom-2 = `22`, first digit |
| 3 | `1` | `2` | bundle atom-3 = `10`, first digit ; survivor atom-2 = `22`, second digit |
| 4 | `0` | `2` | bundle atom-3 = `10`, second digit ; survivor atom-3 = `26`, first digit |

After position 2, every digit-position subtraction compares unrelated
atoms' digits. The output is a generic rational of the appropriate
denominator size — *because that is what the operation produces from
atom-misaligned inputs*.

EXP01's "subtraction-borrow" signature (digits 0 and 9 spike, 1–8
near uniform) and EXP02's Gauss–Kuzmin partial-quotient distribution
are the direct readouts of this transduction.

## The transducer reading

Differencing on digit-concatenated streams is a *transducer*: it
converts one signal (atom-aligned structure) into another
(digit-aligned noise). The transformation is deterministic, exact,
and total when the input streams are misaligned at the atom level.

- **Input**: two digit streams.
- **Operation**: subtract on a common digit denominator.
- **Output**: a digit stream encoding positional difference.
- **Generic output** → maximally atom-misaligned.
- **Structured output** → some atom-alignment preserved through the
  operation.

So `δ` is not a *broken* observable. It is a *measurement of
alignment*. The L1-tracking observable in the cabinet's Two Tongues
curiosity does not go through this transducer — it tracks bundle and
survivor on the same atoms-processed axis, alignment preserved by
construction. That's why it picks up structure where `δ` doesn't.

## Why this matters for `differences/`

The original perpendicular pitch listed digit-frequency and continued
fraction as the cheap first probes. Both go through the transducer.
EXP01 and EXP02 came back null on those observables — and that
*can't* tell us about the relation, because the operation has already
destroyed atom-level structure before the observable measures
anything. The null is a measurement of the transducer, not of the
underlying signal.

The right perpendicular observables for the bundle-survivor relation
are the ones that preserve atom-level alignment by construction:

- **Survivor-to-bundle position map.** Each survivor `s_k` has a
  bundle position `b_k` where it first appeared. The function
  `k → b_k` is monotone-increasing. Its slope, gaps, and structure
  are atom-aligned and have nothing to do with digit subtraction.
- **Atom-class distribution.** Bundle atoms have multiplicities
  (1 = survivor, 2 = doubleton, 3+ = higher). The distribution of
  multiplicities across bundle position is atom-aligned and
  closed-form per `survivors/EXP14-FINDINGS.md`.
- **Stream-restricted observables.** Within each stream
  `n ∈ [n_0, n_1]`, the survivors-from-stream-n are a subset of
  full-stream-n. Compute any observable on each stream alone, then
  compare across streams.

## When the transducer is informative

The negative results aren't meaningless — they answer a different
question:

- *Alignment*: bundle and survivor are saturated-misaligned at the
  digit level. The Two Tongues panel's transducer fires totally.
- *Borrow content*: EXP01's overlap region's L1 deviation
  (≈ 0.106) measures how much arithmetic-borrow content the
  subtraction generates at this configuration. Compare across
  parameters to localise where the transducer fires more or less
  totally.
- *Genericity bound*: a future parameter sweep finding
  *non*-generic δ at some `(n_0, n_1, k)` would localise alignment-
  preserving structure that the transducer somehow lets through. So
  far we haven't seen it; the framing above suggests we shouldn't
  expect to.

## The lesson

When two streams differ in length by a structural rule, subtracting
them on a common digit-denominator *transduces* atom-level signal
into digit-level noise. The output is real and well-defined; it just
doesn't carry what the input did. **Use atom-aligned observables
instead.**

If the cabinet ever picks up another differencing-flavoured
specimen, this is the note to cite.

## Cross-references

- `experiments/acm-champernowne/base10/differences/EXP01-FINDINGS.md`
  — the digit-frequency null.
- `experiments/acm-champernowne/base10/differences/EXP02-FINDINGS.md`
  — the continued-fraction null.
- `experiments/acm-champernowne/base10/survivors/SURVIVORS.md` —
  the parent construction; the L1-tracking observable preserves
  atom alignment by design.
- `wonders/curiosity-two-tongues.md` — the cabinet entry that
  records the L1-tracking property and asked the perpendicular
  question this note answers.
