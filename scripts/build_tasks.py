"""Build the Harbor task folders in tasks/ from the sources in src/."""
import json
import shutil
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "tasks"
BASE_IMAGE = "python:3.12-slim@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54"
PYTEST_VERSION = "8.3.3"

sys.path.insert(0, str(SRC / "tasks"))
from bugs import BUGS  # noqa: E402
sys.path.insert(0, str(SRC / "cases"))
from importlib import import_module  # noqa: E402

DOCKERFILE = f"""FROM {BASE_IMAGE}
RUN pip install --no-cache-dir pytest=={PYTEST_VERSION} \\
 && useradd --create-home --uid 1000 agent
WORKDIR /app
COPY app/ /app/
RUN chown -R agent:agent /app
"""

TASK_TOML = """schema_version = "1.1"

[task]
name = "abhishek/inflection-{name}"
description = "{title}"
keywords = ["python", "inflection", "debugging"]

[metadata]
difficulty = "{difficulty}"
category = "software-engineering"
tags = ["python", "bugfix"]
expert_time_estimate_min = {expert_minutes}
reward_mode = "{mode}"

[agent]
timeout_sec = 1800.0
user = "agent"

[verifier]
timeout_sec = 300.0
user = "root"

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 1024
storage_mb = 2048
network_mode = "no-network"
"""

SOLVE = """#!/bin/bash
set -euo pipefail
cp /solution/inflection.py /app/inflection.py
"""

GRADER_FILES = ["grade.py", "probe.py", "test.sh", "test_v1.sh", "test_hidden_v1.py"]


def inject(text, bugs):
    for old, new in bugs:
        if text.count(old) != 1:
            raise SystemExit("bug anchor not found exactly once: %r" % old)
        text = text.replace(old, new)
    return text


def start_file(name, gold_text):
    if name == "acronym-support":
        return (ROOT / "upstream" / "inflection.py").read_text()
    return inject(gold_text, BUGS[name])


def build(spec_path):
    spec = tomllib.loads(spec_path.read_text())
    name = spec["name"]
    src_dir = SRC / "tasks" / name
    out = OUT / name
    shutil.rmtree(out, ignore_errors=True)
    gold_text = (ROOT / spec["gold"]).read_text()
    instruction = (src_dir / "instruction.md").read_text()
    title = instruction.splitlines()[0].lstrip("# ").replace('"', "'")

    (out / "environment" / "app").mkdir(parents=True)
    (out / "solution").mkdir()
    (out / "tests").mkdir()
    (out / "instruction.md").write_text(instruction)
    (out / "task.toml").write_text(TASK_TOML.format(title=title, **spec))
    (out / "environment" / "Dockerfile").write_text(DOCKERFILE)
    (out / "environment" / ".dockerignore").write_text("**/__pycache__\n")
    (out / "environment" / "app" / "inflection.py").write_text(start_file(name, gold_text))
    shutil.copy(src_dir / "test_visible.py", out / "environment" / "app" / "test_visible.py")
    shutil.copy(ROOT / "upstream" / "LICENSE", out / "environment" / "app" / "LICENSE.inflection")
    (out / "solution" / "solve.sh").write_text(SOLVE)
    (out / "solution" / "solve.sh").chmod(0o755)
    (out / "solution" / "inflection.py").write_text(gold_text)

    for filename in GRADER_FILES:
        shutil.copy(SRC / "grader" / filename, out / "tests" / filename)
    shutil.copy(SRC / "cases" / "common.py", out / "tests" / "common.py")
    shutil.copy(SRC / "cases" / (spec["cases"] + ".py"), out / "tests" / "cases.py")
    (out / "tests" / "reference.py").write_text(gold_text)
    groups = import_module(spec["cases"]).GROUPS
    (out / "tests" / "grading.json").write_text(
        json.dumps({"task": name, "mode": spec["mode"], "groups": groups}, indent=2) + "\n")
    print("built", out.relative_to(ROOT))


def main():
    for spec_path in sorted((SRC / "tasks").glob("*.toml")):
        build(spec_path)


if __name__ == "__main__":
    main()
