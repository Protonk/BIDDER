# AGENTS.md

## Sage has tools

>use sage to invoke python

Use sage for `numpy`, `scipy`, and `matplotlib`. Do not attempt to install these or use the system version.

As an example, run a script from the repo root:

```
sage -python tests/test_acm_core.py
```

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
slow, the answer is to precompute with `list(B)`, restructure
the caller, or use the C build (`import bidder_c`).

The C implementation lives at `bidder_root.c` +
`generator/bidder.c`, with an opaque FFI layer in
`bidder_opaque.c` (all symbols prefixed `bdo_`). Build with
`make`. The shared library is consumed by `dist/bidder_c/` via
ctypes. If you modify the cipher backend, you must update both
`generator/coupler.py` (Python) and `generator/bidder.c` (C),
then run `python3 tests/test_dual_parity.py` to verify they
agree.

## Importing BIDDER in experiments

Experiments that use BIDDER cipher as their randomness source
should prefer the C path for speed but fall back to pure Python:

```python
try:
    import bidder_c as bidder
except ImportError:
    import bidder
```

Both paths produce identical results. The C path is ~1000x faster
for `.at()` throughput, which matters for experiments that call it
millions of times. The Python path works without a build step.

Every experiment must run correctly with *either* import. No
figure, assertion, or result may depend on which path was taken.
If an experiment intentionally compares BIDDER against numpy (e.g.
`bidder_comparison.py`), it uses explicit imports, not the
fallback pattern.

## Signposting is for the birds

When creating documentation, say what you want to say briefly enough to not need a road map. Agents and humans can read 400-600 word documents without constant semaphore.
