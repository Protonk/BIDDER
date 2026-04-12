"""
build.py — Poor man's build step for BIDDER.

Reshapes the flat source tree into a proper Python package at
dist/bidder/. The package uses only relative imports — no sys.path
mutation, no bare cross-file imports with generic names. Callers put
the parent directory containing bidder/ on PYTHONPATH (or vendor
bidder/ under a directory already on PYTHONPATH) and `import bidder`
works without colliding with host modules named
api, sawtooth, coupler, bidder_block, etc.

The rewrite is explicit: for each source file in MODULES we apply a
small set of literal edits and copy the result to its destination
inside the package. Any edit whose `old` text is not present in the
source file is a hard build error — the build won't silently drift
out of sync with the source.

The source tree is not modified.

Usage:
    python3 build.py
    # or
    sage -python build.py
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
PKG = os.path.join(DIST, "bidder")


# ---- Exact edits, per source file. Order inside each list matters only
# if one edit could affect the match of a later edit; none of these do.

BIDDER_PY_SYSPATH = """\
import os
import sys

# Wire up sys.path for the implementation modules. The repo is not
# packaged; this matches the convention in core/api.py and
# tests/test_api.py.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, 'core'))
sys.path.insert(0, os.path.join(_HERE, 'generator'))

from api import (                     # noqa: E402
    fulfill,
    BidderBlock,
    MAX_PERIOD_V1,
    UnsupportedPeriodError,
)
from sawtooth import NPrimeSequence   # noqa: E402"""

BIDDER_PY_PACKAGE = """\
from ._api import (
    fulfill,
    BidderBlock,
    MAX_PERIOD_V1,
    UnsupportedPeriodError,
)
from ._sawtooth import NPrimeSequence"""


API_PY_SYSPATH = """\
import os
import sys

# Put generator/ on sys.path so `import bidder_block` resolves. This
# matches the existing cross-directory import convention in
# tests/test_acm_core.py, core/hardy_sidestep.py, and the experiment
# scripts — the repo is not packaged, and callers that import core/api
# are expected to have put core/ on their own sys.path already.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, '..', 'generator'))

from bidder_block import (  # noqa: E402
    BidderBlock,
    UnsupportedPeriodError,
    MAX_PERIOD_V1,
)"""

API_PY_PACKAGE = """\
from ._bidder_block import (
    BidderBlock,
    UnsupportedPeriodError,
    MAX_PERIOD_V1,
)"""


BIDDER_BLOCK_PY_IMPORT_COMMENT = """\
# coupler.py lives in the same directory; whoever imported this module
# already has generator/ on sys.path, so a bare `from coupler import Bidder`
# resolves. (coupler.py was renamed from bidder.py to avoid a collision
# with the project-root bidder.py.)
from coupler import Bidder"""

BIDDER_BLOCK_PY_IMPORT_PACKAGE = """\
from ._coupler import Bidder"""


# (source_rel, dest_rel_in_pkg, [(old, new), ...])
MODULES: list[tuple[str, str, list[tuple[str, str]]]] = [
    (
        "bidder.py",
        "__init__.py",
        [
            (BIDDER_PY_SYSPATH, BIDDER_PY_PACKAGE),
        ],
    ),
    (
        "core/api.py",
        "_api.py",
        [
            (API_PY_SYSPATH, API_PY_PACKAGE),
        ],
    ),
    (
        "generator/bidder_block.py",
        "_bidder_block.py",
        [
            (BIDDER_BLOCK_PY_IMPORT_COMMENT, BIDDER_BLOCK_PY_IMPORT_PACKAGE),
        ],
    ),
    (
        "core/sawtooth.py",
        "_sawtooth.py",
        [],
    ),
    (
        "generator/coupler.py",
        "_coupler.py",
        [],
    ),
]

# Non-Python files that ship inside the package.
EXTRA: list[tuple[str, str]] = [
    ("BIDDER.md", "BIDDER.md"),
]


def main() -> None:
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(PKG)

    written: list[str] = []

    for src_rel, dest_rel, edits in MODULES:
        src = os.path.join(HERE, src_rel)
        with open(src) as f:
            text = f.read()
        for old, new in edits:
            if old not in text:
                print(
                    f"error: edit not found in {src_rel}; "
                    f"source file has drifted from build.py.\n"
                    f"  first 60 chars of expected block: {old[:60]!r}",
                    file=sys.stderr,
                )
                sys.exit(1)
            text = text.replace(old, new, 1)
        dest = os.path.join(PKG, dest_rel)
        with open(dest, "w") as f:
            f.write(text)
        written.append(os.path.relpath(dest, DIST))

    for src_rel, dest_rel in EXTRA:
        src = os.path.join(HERE, src_rel)
        dest = os.path.join(PKG, dest_rel)
        shutil.copy2(src, dest)
        written.append(os.path.relpath(dest, DIST))

    print(f"dist/ built with {len(written)} files:")
    for rel in sorted(written):
        print(f"  {rel}")


if __name__ == "__main__":
    main()
