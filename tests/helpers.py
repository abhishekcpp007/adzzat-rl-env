import importlib.util
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS = sorted(p.name for p in (ROOT / "tasks").iterdir() if (p / "task.toml").exists())


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def task_modules(task):
    tests_dir = ROOT / "tasks" / task / "tests"
    if str(tests_dir) in sys.path:
        sys.path.remove(str(tests_dir))
    sys.path.insert(0, str(tests_dir))
    for name in ("common", "probe", "grade"):
        sys.modules.pop(name, None)
    grade = load_module(tests_dir / "grade.py", "grade_" + task.replace("-", "_"))
    cases = load_module(tests_dir / "cases.py", "cases_" + task.replace("-", "_"))
    reference = load_module(tests_dir / "reference.py", "reference_" + task.replace("-", "_"))
    config = json.loads((tests_dir / "grading.json").read_text())
    return grade, cases, reference, config


def score_file(task, path, seed):
    grade, cases_module, reference, config = task_modules(task)
    candidate = load_module(path, "candidate_%s_%d" % (task.replace("-", "_"), seed))
    cases = cases_module.fixed_cases() + cases_module.random_cases(random.Random(seed), reference)
    expected = [grade.call_case(reference, c) for c in cases]
    actual = [grade.call_case(candidate, c) for c in cases]
    reward, groups = grade.score(config, cases, expected, actual)
    return reward, {g: s["failed"] == 0 for g, s in groups.items()}
