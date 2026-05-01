# Probes test suite

Tests for the probes in `experiments/probes/`. Layered the same way as
`algebra/tests/`: each layer answers a different question, fails
differently, and is read differently. Mirrors that suite's idiom; see
`algebra/tests/README.md` for the parent rationale.

## Layers

| File | Layer | What failure means | First read |
|---|---|---|---|
| `test_smoke.py` | 5 — smoke | Imports broken, lattice file missing, public symbol silently renamed. The wheel is off. | the import line that failed |
| `test_primitives.py` | 2 — primitives | A channel, transducer, or predicted-set helper has a bug. | `experiments/probes/<probe>/probe.py` primitives section |
| `test_anchors.py` | 1 — anchors (the contract) | A probe's `anchors.py` no longer passes. The probe's contract drifted. | the probe's `PROBE.md` § "Anchor" |
| `test_consistency.py` | 3 — cross-form | Two paths to the same quantity disagree (algebra-row vs `q_row`, lattice-vs-algebra substrate, reverse² vs identity, predicted reversal-symmetry vs measured `no_op` strength). | the two functions named in the failure |
| `integration/test_kernel_zero_calibrations.py` | 6 — integration | The full calibration pipeline (lattice substrate × three transducers × four channels) reports an unexpected verdict pattern. | the run's `report.md` and `figures/` |

## Running

Fast mode (every commit, runs in seconds):

```
python3 algebra/tests/probes/test_smoke.py
python3 algebra/tests/probes/test_primitives.py
python3 algebra/tests/probes/test_anchors.py
python3 algebra/tests/probes/test_consistency.py
```

The smoke and consistency tests need numpy + matplotlib (per
`AGENTS.md`, available via `sage -python`). Anchors and primitives
also need numpy. All four are short enough to run via sage in seconds:

```
sage -python algebra/tests/probes/test_smoke.py
sage -python algebra/tests/probes/test_primitives.py
sage -python algebra/tests/probes/test_anchors.py
sage -python algebra/tests/probes/test_consistency.py
```

Slow mode (separate gate, on demand):

```
sage -python algebra/tests/probes/integration/test_kernel_zero_calibrations.py
```

The integration test runs the three full kernel_zero calibrations at
K = 4000 across 24 (p, h) cells. Requires
`experiments/acm-champernowne/base10/q_distillery/q_lattice_4000_h6.npy`
(the only committed height; others regenerable via the regen script in
that directory).

## What this suite is not

- **Not a coverage metric.** What's covered is the *probe*, not lines
  of `probe.py`.
- **Not a substitute for `PROBE.md`.** The `.md` is the spec; tests
  gate the implementation against drift from the spec.
- **Not the calibration gate.** The probe's own `anchors.py` plus the
  three calibration runs in `runs/` are the primary contract. The
  tests here check that the contract still passes, not that it is
  the right contract.

## Adding a new test

Ask: *what would it mean if this failed?*

- "The probe's contract drifted" → anchors
- "A channel or transducer has a bug" → primitives
- "Two paths to the same quantity disagree" → consistency
- "An import is broken" → smoke
- "The end-to-end pipeline behaves wrong" → integration

A test whose failure could mean any of these is a test that won't
help you when it fails. Pick one layer.

## Adding a new probe

When a second probe lands (e.g., `probes/benford/`), append to each
test file a new section that imports the new probe's module and runs
its layer-appropriate checks. Don't fork test files per probe — the
suite is layered by *question*, not by probe.
