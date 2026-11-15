#!/bin/bash
# Run Claude Code in headless mode as the agent on one task, then grade it.
# Usage: scripts/agent_check.sh <task> <model> <run-id>
# The agent gets a scratch copy of the task's /app folder and nothing else.
set -euo pipefail
task="$1"; model="$2"; run="$3"
root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/runs/agent/$task/$model-$run"
work="$(mktemp -d /tmp/inflection-agent-XXXXXX)"
mkdir -p "$out"
cp "$root/tasks/$task/environment/app/"*.py "$work/"
python3 -m venv "$work/.venv" >/dev/null
"$work/.venv/bin/pip" install -q pytest==8.3.3
prompt="$(sed 's#/app/#./#g; s#/app#.#g' "$root/tasks/$task/instruction.md")

The files are in the current directory. Run tests with: .venv/bin/python -m pytest -q"
cd "$work"
start=$(date +%s)
claude -p "$prompt" --model "$model" --max-turns 40 --output-format stream-json --verbose \
  --setting-sources project --no-session-persistence \
  --allowedTools "Read" "Edit" "Write" "Glob" "Grep" "Bash(.venv/bin/python:*)" \
  > "$out/transcript.jsonl" 2> "$out/stderr.txt" || true
echo $(( $(date +%s) - start )) > "$out/seconds.txt"
cp "$work/inflection.py" "$out/inflection.py"
cd "$root"
python3 -m rlenv grade --task "$task" --file "$out/inflection.py" > "$out/grade.txt" 2>&1 || true
python3 scripts/audit_transcript.py "$out/transcript.jsonl" "$work" > "$out/audit.txt"
echo "$task $model $run: $(grep '^reward:' "$out/grade.txt") $(head -1 "$out/audit.txt") seconds=$(cat "$out/seconds.txt")"
rm -rf "$work"
