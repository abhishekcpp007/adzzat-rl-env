import subprocess
import sys

import pytest

from helpers import ROOT, TASKS, score_file, task_modules

SEEDS = [0, 1, 2, 3, 4]


@pytest.mark.parametrize("task", TASKS)
def test_task_layout(task):
    task_dir = ROOT / "tasks" / task
    for rel in ["instruction.md", "task.toml", "environment/Dockerfile",
                "environment/app/inflection.py", "environment/app/test_visible.py",
                "solution/solve.sh", "solution/inflection.py", "tests/test.sh",
                "tests/grade.py", "tests/probe.py", "tests/reference.py"]:
        assert (task_dir / rel).is_file(), rel


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("task", TASKS)
def test_gold_scores_full(task, seed):
    reward, groups = score_file(task, ROOT / "tasks" / task / "solution" / "inflection.py", seed)
    assert reward == 1.0, groups


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("task", TASKS)
def test_starting_file_scores_zero(task, seed):
    reward, groups = score_file(task, ROOT / "tasks" / task / "environment" / "app" / "inflection.py", seed)
    assert reward == 0.0, groups


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("task", TASKS)
def test_every_bug_is_caught_and_nothing_else_breaks(task, seed):
    _, groups = score_file(task, ROOT / "tasks" / task / "environment" / "app" / "inflection.py", seed)
    regression = groups.pop("regression")
    if task != "acronym-support":
        assert regression is True
    assert not any(groups.values()), groups


@pytest.mark.parametrize("task", TASKS)
def test_visible_tests_fail_before_and_pass_after(task, tmp_path):
    app = ROOT / "tasks" / task / "environment" / "app"
    for source, want in [(app / "inflection.py", 1), (ROOT / "tasks" / task / "solution" / "inflection.py", 0)]:
        (tmp_path / "inflection.py").write_text(source.read_text())
        (tmp_path / "test_visible.py").write_text((app / "test_visible.py").read_text())
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                               "test_visible.py"], cwd=tmp_path, capture_output=True)
        assert proc.returncode == want, (source, proc.stdout.decode()[-2000:])


@pytest.mark.parametrize("gold", ["upstream/inflection.py", "src/golds/t3_acronyms.py"])
def test_golds_pass_upstream_suite(gold, tmp_path):
    (tmp_path / "inflection.py").write_text((ROOT / gold).read_text())
    (tmp_path / "test_inflection.py").write_text((ROOT / "upstream" / "test_inflection.py").read_text())
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                          cwd=tmp_path, capture_output=True)
    assert proc.returncode == 0, proc.stdout.decode()[-2000:]


def _plural_bugs():
    sys.path.insert(0, str(ROOT / "src" / "tasks"))
    from bugs import BUGS
    return BUGS["plural-rules"]


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("bug_index", range(4))
def test_partial_credit_with_one_bug_left(bug_index, seed, tmp_path):
    old, new = _plural_bugs()[bug_index]
    gold = (ROOT / "tasks" / "plural-rules" / "solution" / "inflection.py").read_text()
    path = tmp_path / "inflection.py"
    path.write_text(gold.replace(old, new))
    reward, groups = score_file("plural-rules", path, seed)
    assert reward == 0.75, groups
