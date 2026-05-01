# probes/

Designed perturbations of the substrate. Each probe applies a
transducer to a substrate input and reads off, in a fixed list of
channels, where the structure ends up. A probe earns its keep by
being reusable across structural features and across transducer
families. The discipline here mirrors `algebra/README.md` at a
different layer: probes are to experiments as theorems are to
algebra.

## A probe: the five components

Every probe specifies five components before any code runs. They are
the equivalent of a theorem's Statement / BQN / Proof / Anchor.

- **Target.** The structural feature being probed, written with its
  type — the coordinate system on the substrate that the feature
  lives in. "Leading-digit Benford slope at fixed `(n, b)` over the
  first `K` atoms of `M_n`" qualifies; "leading-digit behaviour"
  does not.
- **Transducer.** The destroyer or coordinate change applied to the
  substrate. Specified as a deterministic operation with all
  parameters bound at probe-definition time, plus an explicit
  *information budget* (what the transducer is allowed to know
  about the substrate: blind, or structured with named side
  information).
- **Channels.** The finite list of coordinates in which recovery
  will be attempted. See §"Channels" for rules.
- **Recovery.** A function from each channel's output to a verdict
  in `{present, partial, absent}` and a numeric strength. Computable
  without human inspection.
- **Anchor.** At least one input where the expected outcome is
  known and the probe must reproduce it. Same role as `A1..A10` in
  `algebra/test_anchors.py`. A probe that fails its anchor cannot
  be cited.

## Channels

Three rules.

- **Motivated, not enumerated.** List the projections that have a
  substantive reason to be a recovery coordinate — coordinates the
  algebra suggests, coordinates a previous probe's findings
  suggest, coordinates the transducer's structure suggests. Each
  channel's PROBE.md entry includes its one-line reason.
- **The no-op channel is mandatory.** Same coordinate system as
  the original target, applied to the post-transducer output. This
  is the control: a no-op recovery means the transducer was weak,
  and you can't rule that out without the channel.
- **An adversarial channel is mandatory.** A coordinate the
  algebra does not predict, or one the transducer should have
  explicitly destroyed. This is the noise floor: a recovery here
  is either a false positive or evidence the structure is more
  pervasive than the target claimed.

A channel returns a verdict (present/partial/absent) and a strength
(numeric, calibrated against the no-op channel under the identity
transducer in §"Calibrations"). Channels are independent — each
channel's verdict is computable from the post-transducer output
and the target descriptor, without reference to any other channel.

## Calibrations

Before a probe can anchor a citation it must pass three calibration
runs. The runs go in `runs/` and stay there as part of the probe's
record.

- **Identity calibration.** Transducer = identity. The no-op
  channel reports the structure at full strength; the adversarial
  channel reports below threshold. Failure here is a probe-side
  bug, not a substrate finding.
- **Known-recovery calibration.** Transducer is one whose effect
  on the target structure is known closed-form (or constructed
  by hand for a synthetic case). The probe must locate the
  structure in the predicted channel at the predicted strength.
- **Null calibration.** Substrate input on which the target
  structure is known to be absent. All channels report below
  threshold. A recovery on the null is a bug or an unspecified
  finding; either way, diagnose before treating the probe as
  ready.

A probe that hasn't passed all three is in the *menagerie* (see
§"Menagerie and graveyard"); it can produce hypotheses but cannot
be cited.

## Information budget

The transducer's information budget is part of the probe spec, not
an implementation detail. Three categories:

- **Blind.** Sees only the post-substrate output stream. No access
  to `n`, `h`, `K`-indexing, or any algebra-side data.
- **Structured.** Sees the output stream plus named side
  information. The side-information list is enumerated in PROBE.md.
- **Composed.** A stack of transducers applied in order, each with
  its own budget. The composition's effective budget is the union;
  each stage is documented separately.

A transducer that "secretly" knows side information it didn't
declare is doing something different from one that didn't, and
the findings are not comparable. The information-budget line is
where most confusion enters; write it down first.

## Directory layout

```
probes/
  README.md                        this file
  _harness.py                      shared run harness (created when probe 2 lands)
  <probe_name>/
    PROBE.md                       human-readable specification
    probe.py                       executable definition
    anchors.py                     contract; runs the probe against known-outcome inputs
    channels/                      created only when a probe has 4+ channels
      <channel>.py
    runs/
      <date>_<config>/
        config.json                exact config used; includes git SHA of imported
                                   algebra/ files
        output.npz                 post-transducer output (saved before channel runs)
        report.md                  per-run report (no interpretation)
        figures/
```

Probes start flat. The `channels/` subdir emerges when a probe
genuinely has more channels than fit in a single readable
`probe.py`. The shared `_harness.py` is created when the second
probe lands and the commonalities are visible — not before.

## PROBE.md template

```
# <Probe name>

## Target
<Type signature, then one paragraph specifying the target precisely.>

## Transducer
<Operation, with all parameters bound. Information budget.
Stack depth if composed.>

## Channels
| name | motivation | role |
|---|---|---|
| <no-op>      | identical coordinate system to target | control |
| <channel>    | <one-line reason>                      | primary |
| ...          |                                       |          |
| <adversarial>| <one-line reason it should be silent> | noise floor |

## Recovery
<For each channel: the function from channel output to
(verdict, strength). Threshold or exact criterion. The threshold
is set here, not after the run.>

## Anchor
<The known-outcome input(s) and expected verdict. Cite the
algebra/ theorem(s) the anchor relies on, with anchor numbers
A1..A10 where applicable.>
```

No "what this predicts," no "reading," no "what this does not
predict." Same membrane as `algebra/`.

## Per-run report template

```
# Run <date>_<config>

## Config
<config.json contents inline, plus git SHAs of imported algebra/ files>

## Channel results
| channel | verdict | strength | threshold | notes |
|---|---|---|---|---|

## Anchor comparison
<For each anchor: expected, actual, match/mismatch.>

## Anomalies
<Channels that hit the threshold edge, unexpected verdicts on the
no-op or adversarial channel, calibration drift since prior runs
of the same config.>
```

The per-run report records what happened. Interpretation — what
the finding means — is a separate document and does not go in
`runs/`. This mirrors the `algebra/` rule that closed-form theorem
files have no "reading" section.

## Menagerie and graveyard

- **Menagerie.** Pre-calibration scripts and probes-in-progress.
  Anything that hasn't passed all three calibrations. Useful for
  hypothesis generation; cannot be cited as a finding. Lives
  alongside calibrated probes but is flagged as menagerie in its
  PROBE.md (a single line at the top, e.g. `Status: menagerie —
  identity calibration pending`).
- **Graveyard.** Post-mortem record of probes that failed their
  anchors, failed calibrations and were diagnosed, were retracted,
  or were superseded. Each graveyard entry is one paragraph: what
  the probe targeted, what went wrong, what was learned. The
  graveyard is consulted before any new probe is set up.

The graveyard is appended-to, not edited or deleted. A failed
calibration that turns out to have been a bug gets a follow-up
entry, not a redaction.

## Workflow standard

For each probe:

1. **State** the five components in `PROBE.md`. Channels list with
   one-line motivations. Information budget written down.
2. **Implement** in `probe.py` and `anchors.py`. The implementation
   is a translation of the spec; if the implementation seems to
   require something not in the spec, fix the spec first.
3. **Calibrate.** Run identity / known-recovery / null. Save all
   three runs in `runs/` regardless of outcome. Diagnose any
   failures before declaring the probe ready.
4. **Run.** New runs go in `runs/<date>_<config>/`. Nothing
   overwrites prior runs.
5. **Report.** The per-run `report.md` follows the template.
   Anomalies get flagged. Interpretation goes elsewhere.

## Adding a new probe

1. Create `probes/<probe_name>/` with `PROBE.md`, `probe.py`,
   `anchors.py`.
2. Run all three calibrations; save in `runs/`.
3. Append to this README's probe index (one line).
4. If the probe overlaps with anything in the graveyard, cite the
   graveyard entry in `PROBE.md` and explain how this probe
   differs.

## Adding a new channel to an existing probe

A new channel can be added between runs. The PROBE.md channel
table must be updated, the channel must be motivated in the same
form as the others, and the probe's calibrations must be re-run
with the new channel included. A channel added after a finding
without re-calibration is a *post-hoc channel* and must be flagged
as such in the report; it can produce hypotheses but cannot
strengthen a finding from the same run.

## Probe index

(Populated as probes land.)
