#!/bin/bash
set -uo pipefail
mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt
chown -R root:root /tests
chmod -R go-rwx /tests
python3 -I -B /tests/grade.py
