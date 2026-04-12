"""
build.py — Poor man's build step for BIDDER.

Runs `import bidder` in a subprocess, captures every loaded module
whose source file lives inside this repo, and copies those files
(preserving layout) into dist/. The import graph defines the package.

Anything not reachable via `import bidder` — experiments/, tests/,
COLLECTION.md, nasties/, sources/, guidance/ — is left behind.

Files that should ship but aren't Python-importable (docs, C twins,
etc.) go in EXTRA below. That list is the explicit part of the
package definition; the traced set is the implicit part.

Usage:
    python3 build.py
    # or
    sage -python build.py

Then smoke-test:
    (cd dist && python3 -c "import bidder; print(list(bidder.cipher(10, b'doc')))")
"""

import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
ENTRY = "bidder"

# Non-Python files to ship alongside the traced module set. Repo-relative.
# Grow this as the user-guide / doc set grows.
EXTRA = [
    "BIDDER.md",
]


TRACE_SCRIPT = r"""
import os, sys, json
import bidder  # noqa: F401
root = os.environ["BIDDER_REPO_ROOT"]
paths = []
for m in sys.modules.values():
    f = getattr(m, "__file__", None)
    if f:
        paths.append(os.path.abspath(f))
kept = sorted({p for p in paths if p.startswith(root + os.sep)})
print(json.dumps(kept))
"""


def trace_modules() -> list[str]:
    env = {**os.environ, "BIDDER_REPO_ROOT": HERE}
    out = subprocess.check_output(
        [sys.executable, "-c", TRACE_SCRIPT],
        cwd=HERE,
        env=env,
        text=True,
    )
    return json.loads(out.strip().splitlines()[-1])


def copy_into_dist(src_abs: str) -> str:
    rel = os.path.relpath(src_abs, HERE)
    dst = os.path.join(DIST, rel)
    os.makedirs(os.path.dirname(dst) or DIST, exist_ok=True)
    shutil.copy2(src_abs, dst)
    return rel


def main() -> None:
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    traced = [p for p in trace_modules() if p.endswith(".py")]

    copied: list[str] = []
    for src in traced:
        copied.append(copy_into_dist(src))

    for rel in EXTRA:
        src = os.path.join(HERE, rel)
        if not os.path.exists(src):
            print(f"warning: EXTRA entry missing: {rel}", file=sys.stderr)
            continue
        copied.append(copy_into_dist(src))

    print(f"dist/ built with {len(copied)} files:")
    for rel in sorted(copied):
        print(f"  {rel}")


if __name__ == "__main__":
    main()
