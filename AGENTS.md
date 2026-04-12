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

## Performance of BIDDER

The Python `bidder` package is pure interpreted Python — no C, no
NumPy, no JIT. Each `.at(i)` call runs Feistel rounds in a Python
loop. This is intentional: no build step, no platform binaries,
no dependencies. It is fast enough for its intended use (keyed
permutations up to period 4 billion, accessed sequentially or by
random access).

It is **not** a fast RNG replacement. Using `BidderBlock.at()` as a
per-element random source inside a tight numerical loop (hundreds
of millions of calls) will be orders of magnitude slower than
`numpy.random`. Example: generating 20k full permutations of
period 20k takes ~20 minutes vs. milliseconds for numpy.

Do not "fix" this by rewriting the cipher in C or adding NumPy
vectorization. The simplicity is the point. If a workload is
slow, the answer is to precompute with `list(B)` or restructure
the caller, not to optimize the backend.

## Signposting is for the birds

When creating documentation, say what you want to say briefly enough to not need a road map. Agents and humans can read 400-600 word documents without constant semaphore.
