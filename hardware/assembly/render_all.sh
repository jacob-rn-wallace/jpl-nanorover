#!/usr/bin/env bash
# Render the Blender views listed in docs/render-jobs.md.   Usage: hardware/assembly/render_all.sh [view-id ...]   (no arguments: every job)
# Picks the Blender binary and device itself: macOS uses /Applications/Blender.app and the Metal GPU; elsewhere BLENDER (default ~/tools/blender-4.5.9-linux-x64/blender) on the CPU.
# Job ids and settings are the same as in docs/render-jobs.md; keep the two in step.
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ "$(uname)" == "Darwin" ]]; then BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"; DEVICE="${DEVICE:-gpu}"
else BLENDER="${BLENDER:-$HOME/tools/blender-4.5.9-linux-x64/blender}"; DEVICE="${DEVICE:-cpu}"; fi
for f in hardware/assembly/out/blender/struts.stl hardware/assembly/out/blender/wheels.stl; do
  [[ -f "$f" ]] || { echo "missing $f: copy it from the desktop machine or regenerate it (docs/blender-render.md, 'Setup on an Apple Silicon Mac')"; exit 1; }
done
# id | VIEW | extra environment | RES | SAMPLES
JOBS=(
  "R1|hero||1600x1000|96"
  "R2|rear||1600x1000|96"
  "R3|top||1600x1000|96"
  "R4|detail||1500x940|96"
  "R5|cells||1500x940|96"
  "R6|window||1500x940|96"
  "R7|window|LED=on SUFFIX=-lit|1500x940|96"
)
want=("$@")
for job in "${JOBS[@]}"; do
  IFS='|' read -r id view extra res samples <<<"$job"
  if [[ ${#want[@]} -gt 0 ]] && [[ ! " ${want[*]} " =~ " $id " ]]; then continue; fi
  echo "== $id: view $view ${extra:-} $res $samples samples, device $DEVICE"
  start=$(date +%s)
  env VIEW="$view" RES="$res" SAMPLES="$samples" DEVICE="$DEVICE" $extra "$BLENDER" -b -P hardware/assembly/blender_render.py 2>&1 | grep -E "render device|no GPU|wrote|Error" || true
  echo "   $id took $(( $(date +%s) - start )) s"
done
