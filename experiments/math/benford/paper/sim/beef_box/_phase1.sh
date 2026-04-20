#!/usr/bin/env bash
# Internal helper — do not invoke directly; runs inside the 'phase1'
# window of the 'beef-sims' tmux session spawned by launch.sh.
#
# Sequentially runs the three cheap sims (preflight → run3 → run4).
# If all succeed, spawns run1 and run2 in parallel tmux windows.
# If any fail, bails via `set -e` and leaves the window open with
# the error visible.

set -euo pipefail

BEEF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="$BEEF_DIR/logs"
SESSION="beef-sims"
PYTHON_CMD="${PYTHON_CMD:-python3 -u}"

cd "$BEEF_DIR"

log_step () {
  printf '\n\033[1;36m[phase1 %s] %s\033[0m\n' "$(date +%H:%M:%S)" "$1"
}

log_step "starting preflight"
$PYTHON_CMD run_preflight_reference.py 2>&1 | tee "$LOGS_DIR/preflight.log"

log_step "preflight done, starting run3 (non-√2 delta IC substitutions)"
$PYTHON_CMD run3_non_sqrt2_delta.py 2>&1 | tee "$LOGS_DIR/run3.log"

log_step "run3 done, starting run4 (high-mode B3)"
$PYTHON_CMD run4_high_mode_b3.py 2>&1 | tee "$LOGS_DIR/run4.log"

log_step "phase1 complete; spawning run1 and run2 parallel windows"

# Run 1 (~15–20 hrs, N = 10⁸).  `; read` keeps the window open after
# the sim exits (crashed or completed) so you can see final state on
# attach.
tmux new-window -t "$SESSION" -n run1 -c "$BEEF_DIR" \
  "$PYTHON_CMD run1_full_m4.py 2>&1 | tee '$LOGS_DIR/run1.log'; \
   echo '[run1] exited at '\$(date)'. press enter to close.'; \
   read"

# Run 2 (~5 days, N = 10⁹, peak ~30–35 GB).
tmux new-window -t "$SESSION" -n run2 -c "$BEEF_DIR" \
  "$PYTHON_CMD run2_long_anchor.py 2>&1 | tee '$LOGS_DIR/run2.log'; \
   echo '[run2] exited at '\$(date)'. press enter to close.'; \
   read"

log_step "run1 and run2 launched. Ctrl-B n to switch windows, Ctrl-B d to detach."
log_step "this phase1 window will stay open; press enter to close it."
read
