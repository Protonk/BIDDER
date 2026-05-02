#!/usr/bin/env bash
# replicate.sh — reproduce every measurement and use-case figure
# referenced in the JStatSoft paper.
#
# Run from the bidder-stat/ root via `make replicate`, which also
# builds libbidder and runs the test suite first.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
cd "$ROOT"

# sage -python carries the numpy + matplotlib that the measurements
# rely on (per AGENTS.md in the upstream repo). If sage is not on
# the path, fall back to python3 and require numpy + matplotlib to
# be importable.
if command -v sage >/dev/null 2>&1; then
    PY="sage -python"
else
    PY="python3"
fi

echo "=== M1: cycle-walking decision rule ==="
$PY replication/m1_cycle_walking.py

echo
echo "=== M2: FPC realisation gap ==="
$PY replication/m2_fpc_gap.py

echo
echo "=== M3: comparison ==="
$PY replication/m3_comparison.py

echo
echo "=== M4: throughput at scale ==="
$PY replication/m4_throughput.py

echo
echo "=== Use cases (§7.1-§7.6) ==="
echo "(Pending: use_case_06 first, others to follow.)"
# Each use case will land as `replication/use_case_<n>.py` per
# WORKSET.md Phase 3 / OUTLINE.md §7.<n>.

echo
echo "=== Replication complete ==="
