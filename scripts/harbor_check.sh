#!/bin/bash
# Run Harbor's own oracle and nop agents on every task.
# Docker Desktop on macOS has no nftables, so Harbor's local docker provider
# refuses network_mode="no-network". This makes a temporary copy without that
# line. On Linux runners, pass --keep-network to use the tasks as they are.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
harbor="${HARBOR:-harbor}"
src="$root/tasks"
if [ "${1:-}" != "--keep-network" ]; then
  src="$(mktemp -d)"
  cp -R "$root/tasks/." "$src/"
  sed -i.bak '/^network_mode = "no-network"$/d' "$src"/*/task.toml
  rm -f "$src"/*/task.toml.bak
fi
for task in "$src"/*/; do
  for agent in oracle nop; do
    "$harbor" run -p "$task" -a "$agent" -o "$root/runs/harbor" -y -q > /dev/null 2>&1 || true
    result="$(ls -td "$root"/runs/harbor/*/ | head -1)"
    reward="$(find "$result" -name reward.txt | head -1 | xargs cat 2>/dev/null || echo missing)"
    echo "$(basename "$task") $agent reward=$reward"
  done
done
