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

# All Python runs through the locked .venv. Run `make venv` first
# to bootstrap it. Versions pinned in requirements.txt.
VENV_PY="$ROOT/.venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
    echo "error: $VENV_PY not found." >&2
    echo "Run \`make venv\` first to bootstrap the locked environment." >&2
    exit 1
fi
PY="$VENV_PY"

echo "=== M1: cycle-walking decision rule ==="
$PY replication/m1_cycle_walking.py

echo
echo "=== M2: FPC realisation gap ==="
$PY replication/m2_fpc_gap.py

echo
echo "=== M2-anomaly: P=1000 anomaly probe (neighbour P + integrand sweep) ==="
$PY replication/m2_anomaly_probe.py

echo
echo "=== M2-domain: Feistel domain s sweep (s=15..100, three probes per s) ==="
$PY replication/m2_feistel_domain.py

echo
echo "=== M2-pow2: power-of-2 Feistel domain bands (s=62..67, s=126..130) ==="
$PY replication/m2_power_of_two.py

echo
echo "=== M3: comparison ==="
$PY replication/m3_comparison.py

echo
echo "=== M4: throughput at scale ==="
$PY replication/m4_throughput.py

echo
echo "=== D4: C-direct throughput ==="
if [ -x replication/bench_c ]; then
    ./replication/bench_c replication/d4_results.md
else
    echo "(bench_c not built; run \`make bench-c\` to build and run)"
fi

echo
echo "=== D1: FF1 throughput + FPC tightness ==="
$PY replication/d1_measure.py

echo
echo "=== §7.1 Stratified survey design (use_case_01) ==="
$PY replication/use_case_01_stratified_survey.py

echo
echo "=== §7.2 Benford-test null (use_case_02) ==="
$PY replication/use_case_02_benford_null.py

echo
echo "=== §7.2 Prefix imbalance diagnostic (use_case_02) ==="
$PY replication/use_case_02_prefix_imbalance.py

echo
echo "=== §7.3 Cross-validation (use_case_03) ==="
$PY replication/use_case_03_cross_validation.py

echo
echo "=== §7.4 Format-preserving permutation (use_case_04) ==="
$PY replication/use_case_04_fpe.py

echo
echo "=== §7.6 Variance-controlled MC (use_case_06) ==="
$PY replication/use_case_06_variance_mc.py

# §7.5 was cut per audit Q4 (overlapped §7.2 / §7.4).

echo
echo "=== Replication complete ==="
