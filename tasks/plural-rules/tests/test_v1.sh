#!/bin/bash
# Grader v1: the first version, kept only to replay the exploit study.
set -uo pipefail
mkdir -p /logs/verifier
cd /tests
if PYTHONPATH=/app python3 -B -m pytest -q -p no:cacheprovider /tests/test_hidden_v1.py; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
