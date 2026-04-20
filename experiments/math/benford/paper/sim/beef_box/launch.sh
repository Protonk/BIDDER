#!/usr/bin/env bash
# Entry point: creates a detached tmux session `beef-sims` that runs the
# four expensive sims + preflight regen without depending on the SSH
# tunnel staying up. Reattach later with `tmux attach -t beef-sims`.
#
# Execution order:
#   phase1 window: preflight → run3 → run4 (cheap; ~45 min total).
#                  Sanity check — if any of these fail, the expensive
#                  runs do NOT start.
#   run1 window:   N = 10⁸, full-M4 on √2 IC (~15–20 hrs).
#   run2 window:   N = 10⁹, M3 IC (b) extended to n = 20,000 (~5 days).
#
# Override python interpreter with PYTHON_CMD env var, e.g.
#   PYTHON_CMD='sage -python' ./launch.sh

set -euo pipefail

BEEF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="$BEEF_DIR/logs"
PHASE1_SCRIPT="$BEEF_DIR/_phase1.sh"
SESSION="beef-sims"
PYTHON_CMD="${PYTHON_CMD:-python3 -u}"

mkdir -p "$LOGS_DIR"

# --- Pre-flight checks (on the launcher side, not the sim side) ------

# 1. tmux available?
if ! command -v tmux >/dev/null; then
  echo "ERROR: tmux not on PATH. Install with: sudo apt install tmux"
  exit 1
fi

# 2. session already exists? Don't silently stomp on a running queue.
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "ERROR: tmux session '$SESSION' already exists. Either attach:"
  echo "    tmux attach -t $SESSION"
  echo "or nuke it and re-run launch.sh:"
  echo "    tmux kill-session -t $SESSION"
  exit 1
fi

# 3. all sim scripts in place?
for script in run_preflight_reference.py run3_non_sqrt2_delta.py \
              run4_high_mode_b3.py run1_full_m4.py run2_long_anchor.py \
              _phase1.sh; do
  if [[ ! -f "$BEEF_DIR/$script" ]]; then
    echo "ERROR: missing $BEEF_DIR/$script"
    exit 1
  fi
done

# 4. helper script executable?
chmod +x "$PHASE1_SCRIPT"

# 5. python interpreter can import numpy?
if ! $PYTHON_CMD -c 'import numpy; print("numpy", numpy.__version__)' 2>&1; then
  echo "ERROR: '$PYTHON_CMD' cannot import numpy. Fix before launching."
  exit 1
fi

# --- Launch the session ----------------------------------------------

tmux new-session -d -s "$SESSION" -n phase1 -c "$BEEF_DIR" \
  -e "PYTHON_CMD=$PYTHON_CMD" \
  "bash '$PHASE1_SCRIPT'"

cat <<EOF

Launched tmux session: $SESSION
Phase1 window is now running preflight → run3 → run4.
On success it will spawn run1 and run2 in parallel windows.

Windows will be:
  phase1   → preflight (~30s) → run3 (~15min) → run4 (~10min)
  run1     → ~15–20 hrs   (N = 10⁸, full-M4 on √2 IC)
  run2     → ~5 days      (N = 10⁹, LONG-ANCHOR)

Controls:
  Attach:   tmux attach -t $SESSION
  Detach:   Ctrl-B then d
  Switch:   Ctrl-B then n (next) / p (prev) / <digit> (by index)
  List:     tmux list-windows -t $SESSION
  Nuke:     tmux kill-session -t $SESSION

Logs (tail from any SSH session without attaching):
  tail -f $LOGS_DIR/preflight.log
  tail -f $LOGS_DIR/run3.log
  tail -f $LOGS_DIR/run4.log
  tail -f $LOGS_DIR/run1.log
  tail -f $LOGS_DIR/run2.log

NOTES:
  * Partial checkpoints (run1 + run2, every 1000 sim steps) are saved
    to *.partial.npz. The scripts do NOT auto-resume on restart — a
    fresh launch starts from step 0. If run2 crashes at day 3 and you
    want to resume, stop and ask before relaunching.
  * Run 2 peak memory ~30–35 GB. Safe to run concurrently with Run 1
    (~3 GB) on the 64 GB beef box; adding any other heavy process may
    push over.
EOF
