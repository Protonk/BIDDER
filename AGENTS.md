# AGENTS.md

## Build and test

Python tests (no dependencies beyond stdlib):

    python3 tests/test_bidder.py
    python3 tests/test_speck.py

Python core tests (requires sage for numpy):

    sage -python tests/test_acm_core.py

C tests:

    gcc -O2 -o test_acm_core_c tests/test_acm_core_c.c core/acm_core.c -lm
    ./test_acm_core_c

    gcc -O2 -o test_bidder_c tests/test_bidder_c.c generator/bidder.c -lm
    ./test_bidder_c

Plots and experiments require `sage -python`, not `python3`.
sage carries numpy and matplotlib internally.

## Repo structure

- `core/` — n-prime and Champernowne real definitions (Python + C).
  `acm_core.py` is imported by all experiment scripts.
  Don't modify without reason.
- `generator/` — the BIDDER block generator (Python + C). Has its
  own `AGENTS.md` with implementation-specific rules.
- `tests/` — all test suites. Keep green.
- `experiments/` — exploration scripts and visualizations, organized
  source-first under `acm-champernowne/`, `bidder/`, `math/`, and
  `future/`. See `experiments/README.md` for the classification rule.
- `sources/` — reference papers and early findings. Read-only.
- `nasties/` — known bugs and edge-case documentation.
- `guidance/` — agent guidance documents.

## Experiment conventions

Experiments live under `experiments/<source-family>/` (and a `<base>/`
level inside `acm-champernowne/`). Each leaf experiment has its own
script and output PNGs. Follow these patterns:

- Dark background: `#0a0a0a`
- Text color: white
- Color palette: `#ffcc5c` (yellow), `#6ec6ff` (blue),
  `#ff6f61` (red), `#88d8b0` (green)
- Scripts use `sage -python` and insert paths to `core/` and
  `generator/` via `__file__`-based path construction.
- Each experiment directory may have a doc named for its folder
  (e.g., `SIEVES.md` in `experiments/sieves/`)

## Design doc

`generator/BIDDER.md` is the source of truth for the
generator's design, findings, and open questions. Update it
when a question is answered or a finding is confirmed.

## Documentation

Don't create documentation files unless asked. Don't add
docstrings, comments, or type annotations to code you didn't
change.
