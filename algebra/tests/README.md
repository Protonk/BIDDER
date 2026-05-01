# Algebra test suite

Tests for the closed-form work in `algebra/`. The suite is layered: each
layer answers a different question, fails differently, and is read
differently. Conflating layers turns the suite into a thing you read
selectively, and that's where suites lose authority.

## Layers

| File | Layer | What failure means | First read |
|---|---|---|---|
| `test_smoke.py` | 5 — smoke | Imports broken, dependency missing, function silently renamed. The wheel is off. | the import line that failed |
| `test_primitives.py` | 2 — primitives | A building block (`factor_tuple`, `tau`, `decompose`, ...) has a bug, or two primitives drifted apart. | `algebra/predict_q.py` primitives section |
| `test_anchors.py` | 1 — anchors (the contract) | A closed-form theorem in `algebra/*.md` no longer matches `predict_q.py`. The contract drifted; one of them is wrong. | the named theorem's `.md` |
| `test_consistency.py` | 3 — cross-form | Two implementations of the same object disagree. The most likely cause is an indexing convention drift between forms. | the two functions named in the failure |
| `test_properties.py` | 4 — properties (Hypothesis) | A theorem doesn't hold on Hypothesis's minimized counterexample. Usually a boundary case the anchors didn't sample. | the theorem `.md`, then the implementation |
| `integration/` | 6 — integration | Two systems disagree on an external object (cached lattice file, OEIS-style table). | the integration test header |

Layers 1, 2, 3, 5 are present. Layer 4 (properties) is the next addition.

## Running

Fast mode (every commit, runs in seconds):

```
python3 algebra/tests/test_smoke.py
python3 algebra/tests/test_primitives.py
python3 algebra/tests/test_anchors.py
python3 algebra/tests/test_consistency.py
```

Slow mode (separate gate, on demand):

```
sage -python algebra/tests/integration/test_within_row_lattice.py
python3 algebra/tests/test_properties.py   # once Hypothesis suite is added
```

The integration test requires `numpy` and the cached lattice
`experiments/acm-champernowne/base10/q_distillery/q_lattice_4000_h6.npy`.
Run it via `sage -python` per `AGENTS.md`.

## What this suite is not

- **Not a coverage metric.** What's covered is the *algebra*, not the
  lines of `predict_q.py`. A suite that exercises every line but
  doesn't cross-check the C4 integer-language reading is weaker than a
  suite with worse line coverage but stronger algebraic cross-checks.
- **Not a substitute for `algebra/*.md`.** The `.md` files are the
  proofs; the tests gate the implementation against drift from the
  proofs. If a test ever passes by accident — implementation gives the
  right answer for the wrong reason — only the documentation catches
  it. Each anchor names the `.md` it pins; keep that link alive.

## Adding a new test

Ask: *what would it mean if this failed?*

- "The algebra is broken" → anchor (sparingly; one anchor per theorem)
- "A primitive has a bug" → primitives
- "Two forms have drifted" → consistency
- "The property fails on this input class" → properties
- "The wheels are off" → smoke
- "Two modules disagree" → integration

A test whose failure could mean any of those is a test that won't help
you when it fails. Pick one layer.
