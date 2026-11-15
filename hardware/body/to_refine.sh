#!/bin/bash
# Refine a topology-optimisation result at 2.9 mm and sharpen it with penalty continuation, in checkpointed chunks.
#   hardware/body/to_refine.sh MASS_G [START_STAGE]        run from the repository root; MASS_G is 40, 80, 120 or 200 (a 3.8 mm result for it must exist: to_run.py --n 36 --mass MASS_G)
#   START_STAGE: A (2.9 mm, penalty 3; default), 4 (penalty 4, from the A result) or 5 (penalty 5, from the p4 result): resume after an interruption
# Needs .venv-to (pyMOTO; hardware/body/requirements-to.txt), the 48 grid (.venv/bin/python hardware/body/to_inputs.py --grid 48) and, to plot, matplotlib in .venv-to.
# Each stage saves a result and a picture, and COMMITS AND PUSHES them (set COMMIT=0 to skip): background jobs die when a session ends, so every chunk is a checkpoint.
# Logs: ${LOGDIR:-/tmp/to_refine}_<mass>.  Timings on the 4-core desktop: stage A 20 to 35 minutes, each 15-iteration chunk 8 to 12 minutes (6 chunks).
M=${1:?mass in g}; STAGE=${2:-A}; COMMIT=${COMMIT:-1}
LOG=${LOGDIR:-/tmp/to_refine}_$M; mkdir -p "$LOG"
cd "$(dirname "$0")/../.." || exit 1
commit () {   # result, picture, message
  [ "$COMMIT" = 1 ] || return 0
  git add "$1" "$2" >> "$LOG/git.log" 2>&1
  git commit -q -m "$3

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" >> "$LOG/git.log" 2>&1
  git pull -q --rebase >> "$LOG/git.log" 2>&1; git push -q origin HEAD >> "$LOG/git.log" 2>&1
}
res=hardware/body/out/to_result_n48_m$M.npz
if [ "$STAGE" = A ]; then
  .venv-to/bin/python -u hardware/body/to_run.py --n 48 --mass "$M" --maxit 60 --start hardware/body/out/to_result_n36_m$M.npz > "$LOG/A.log" 2>&1
  [ -f "$res" ] && .venv-to/bin/python hardware/body/to_plot.py "$res" > /dev/null 2>&1 && commit "$res" docs/images/to-n48_m$M.png "Topology optimisation, $M g refined at 2.9 mm (n = 48)"
fi
prev=$res; [ "$STAGE" = 5 ] && prev=hardware/body/out/to_result_n48_m${M}_p4.npz
for stage in "4 3" "5 3"; do
  set -- $stage; p=$1; chunks=$2
  [ "$STAGE" = 5 ] && [ "$p" = 4 ] && continue
  pres=hardware/body/out/to_result_n48_m${M}_p$p.npz
  for c in $(seq 1 $chunks); do
    .venv-to/bin/python -u hardware/body/to_run.py --n 48 --mass "$M" --maxit 15 --p $p --start "$prev" > "$LOG/p${p}_$c.log" 2>&1
    if [ -f "$pres" ]; then prev=$pres; .venv-to/bin/python hardware/body/to_plot.py "$pres" > /dev/null 2>&1; commit "$pres" docs/images/to-n48_m${M}_p$p.png "Topology optimisation, $M g, penalty $p, checkpoint $c of $chunks at 2.9 mm"; fi
  done
done
echo done > "$LOG/done"
