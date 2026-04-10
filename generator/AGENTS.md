# generator/AGENTS.md

## Cross-language parity

The Python (`coupler.py`, renamed from `bidder.py`) and C
(`bidder.h` + `bidder.c`) implementations must produce identical
output for identical inputs. The Python file was renamed to
`coupler.py` to resolve an import collision with the project-root
`bidder.py`; the C files keep the `bidder_*` namespace prefix
unchanged. The cross-check test in `tests/test_bidder.py` enforces
parity with hardcoded expected values. Any change to one
implementation must be mirrored in the other.

## Feature set

Both implementations support exactly:
- Speck32/64 permutation for tight-fit blocks (cycle-walk ratio <= 64)
- Balanced Feistel with SHA-256-derived round keys for small blocks
- Base in [2, 2^32], block size up to 2^32
- Three operations: init, next, reset

Python also exposes `period` (property), `__iter__`, `__next__`,
and `__repr__` as language-required conventions. These are not
feature additions — they make the generator usable in `for` loops
and `repr()`. C does not need equivalents.

Do not add features to one language without the other. The
Python-specific conveniences above are the only exceptions.

## Speck variants

The generator uses only Speck32/64. The full Speck family
(all 10 variants, all test vectors) lives in `speck.py` as a
reference library. Do not add larger Speck variants to the
generator unless both Python and C are updated together.

## The alphabet excludes 0

The output alphabet is {1, ..., b-1}. The leading base-b digit
is never 0. This is structural and intentional. Do not "fix"
the output to include 0. The PractRand finding in
`BIDDER.md` documents why this is correct.

## Constants

These constants are shared between Python and C. Keep them
in sync:

    SPECK32_ROUNDS = 22
    FEISTEL_ROUNDS = 8
    MAX_CYCLE_WALK_RATIO = 64
