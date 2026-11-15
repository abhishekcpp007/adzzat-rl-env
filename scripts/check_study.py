"""Fail unless the latest study matches what the README claims."""
import json
import sys
from collections import defaultdict
from pathlib import Path

EXPECTED_V1_ESCAPES = {"cheat:peek", "cheat:exit-code"}

rows = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line]
rewards = defaultdict(list)
for row in rows:
    rewards[(row["grader"], row["policy"])].append(row["reward"])

problems = []
for (grader, policy), values in sorted(rewards.items()):
    if policy == "oracle":
        want = 1.0
    elif grader == "v1" and policy in EXPECTED_V1_ESCAPES:
        want = 1.0
    else:
        want = 0.0
    bad = [v for v in values if v != want]
    print("%-3s %-17s episodes=%-3d mean=%.2f expected=%.1f %s"
          % (grader, policy, len(values), sum(values) / len(values), want, "FAIL" if bad else "ok"))
    if bad:
        problems.append((grader, policy))
sys.exit(1 if problems else 0)
