import os
import secrets
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import inflection  # noqa: E402
from grade import build_cases  # noqa: E402
from probe import call_case  # noqa: E402

SEED = int(os.environ.get("GRADING_SEED") or secrets.randbits(32))
CASES, EXPECTED = build_cases(SEED)


def test_hidden_cases():
    failures = [case for case, want in zip(CASES, EXPECTED) if call_case(inflection, case) != want]
    assert not failures, failures[:3]
