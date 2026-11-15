"""A small gym-style environment around the Harbor tasks in tasks/.

Each episode runs in its own container from the task image. The agent acts as
the non-root user `agent` with no network. On submit, only /app/inflection.py
is copied into a fresh grading container, so nothing else the agent did in
its own container can reach the grader.
"""
import io
import json
import shlex
import subprocess
import tarfile
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"
AGENT_USER = "agent"
MAX_STEPS = 50
BASH_TIMEOUT_SEC = 60
OUTPUT_LIMIT = 8000
READ_LIMIT = 200_000
SUBMISSION = "/app/inflection.py"


def list_tasks():
    return sorted(p.name for p in TASKS_DIR.iterdir() if (p / "task.toml").exists())


def _docker(*args, check=True, input_bytes=None, timeout=None):
    return subprocess.run(["docker", *args], check=check, capture_output=True,
                          input=input_bytes, timeout=timeout)


def build_image(task):
    tag = "inflection-env/%s:latest" % task
    _docker("build", "-q", "-t", tag, str(TASKS_DIR / task / "environment"))
    return tag


def _tar_dir(path, arcname):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        tar.add(str(path), arcname=arcname)
    return buf.getvalue()


@dataclass
class StepResult:
    observation: str
    reward: float = 0.0
    done: bool = False
    info: dict = field(default_factory=dict)


class InflectionEnv:
    """Actions are dicts:

    {"type": "bash", "cmd": "..."}            run a shell command in /app
    {"type": "read", "path": "..."}           read a file
    {"type": "write", "path": "...", "content": "..."}
    {"type": "submit"}                        grade /app/inflection.py and end
    """

    def __init__(self, task, grader="v2", seed=None):
        if task not in list_tasks():
            raise ValueError("unknown task %r, pick one of %s" % (task, list_tasks()))
        if grader not in ("v1", "v2"):
            raise ValueError("grader must be v1 or v2")
        self.task = task
        self.grader = grader
        self.seed = seed
        self.task_dir = TASKS_DIR / task
        self.image = build_image(task)
        self.container = None
        self.steps = 0
        self.trajectory = []

    def reset(self):
        self.close()
        self.container = "inflection-ep-" + uuid.uuid4().hex[:12]
        _docker("run", "-d", "--name", self.container, "--network", "none",
                "--user", AGENT_USER, self.image, "sleep", "infinity")
        self.steps = 0
        self.trajectory = []
        instruction = (self.task_dir / "instruction.md").read_text()
        listing = self._exec("ls -la /app").stdout.decode()
        return instruction + "\n\nFiles in /app:\n" + listing

    def _exec(self, cmd, user=AGENT_USER, input_bytes=None):
        return _docker("exec", "-i", "-u", user, "-w", "/app", self.container, "bash", "-c", cmd,
                       check=False, input_bytes=input_bytes, timeout=BASH_TIMEOUT_SEC)

    def step(self, action):
        if self.container is None:
            raise RuntimeError("call reset() first")
        self.steps += 1
        kind = action.get("type")
        if kind == "bash":
            try:
                proc = self._exec(action["cmd"])
                out = (proc.stdout + proc.stderr).decode(errors="replace")
                obs = "exit=%d\n%s" % (proc.returncode, out[-OUTPUT_LIMIT:])
            except subprocess.TimeoutExpired:
                obs = "command timed out after %ds" % BASH_TIMEOUT_SEC
            result = StepResult(obs)
        elif kind == "read":
            proc = self._exec("cat -- %s" % shlex.quote(action["path"]))
            text = (proc.stdout or proc.stderr).decode(errors="replace")
            if len(text) > READ_LIMIT:
                text = text[:READ_LIMIT] + "\n[truncated at %d characters]" % READ_LIMIT
            result = StepResult(text)
        elif kind == "write":
            proc = self._exec("cat > %s" % shlex.quote(action["path"]),
                              input_bytes=action["content"].encode())
            result = StepResult("ok" if proc.returncode == 0 else proc.stderr.decode(errors="replace"))
        elif kind == "submit":
            reward, details = self.grade()
            result = StepResult("graded", reward=reward, done=True, info=details)
        else:
            result = StepResult("unknown action type %r" % kind)
        if not result.done and self.steps >= MAX_STEPS:
            reward, details = self.grade()
            result = StepResult(result.observation + "\nstep limit reached, graded",
                                reward=reward, done=True, info=details)
        self.trajectory.append({"action": action, "observation": result.observation[:2000],
                                "reward": result.reward, "done": result.done})
        return result

    def grade(self):
        if self.grader == "v1":
            return self._grade_in_place()
        return self._grade_fresh()

    def _grade_env(self):
        return ["-e", "GRADING_SEED=%d" % self.seed] if self.seed is not None else []

    def _grade_fresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp) / "inflection.py"
            got = _docker("cp", "%s:%s" % (self.container, SUBMISSION), str(local), check=False)
            grader = "inflection-grade-" + uuid.uuid4().hex[:12]
            _docker("run", "-d", "--name", grader, "--network", "none", "--user", "root",
                    self.image, "sleep", "infinity")
            try:
                _docker("exec", grader, "rm", "-f", SUBMISSION)
                if got.returncode == 0:
                    _docker("cp", str(local), "%s:%s" % (grader, SUBMISSION))
                _docker("cp", str(self.task_dir / "tests"), "%s:/tests" % grader)
                proc = _docker("exec", *self._grade_env(), grader, "bash", "/tests/test.sh",
                               check=False, timeout=600)
                return self._read_reward(grader, proc)
            finally:
                _docker("rm", "-f", grader, check=False)

    def _grade_in_place(self):
        _docker("exec", "-i", "-u", "root", self.container, "tar", "-x", "-C", "/",
                input_bytes=_tar_dir(self.task_dir / "tests", "tests"))
        proc = _docker("exec", "-u", "root", *self._grade_env(), "-w", "/tests", self.container,
                       "bash", "/tests/test_v1.sh", check=False, timeout=600)
        return self._read_reward(self.container, proc)

    def _read_reward(self, container, proc):
        def cat(path):
            return _docker("exec", "-u", "root", container, "cat", path, check=False).stdout.decode()
        raw = cat("/logs/verifier/reward.txt").strip()
        try:
            reward = float(raw)
        except ValueError:
            reward = 0.0
        details = {"grader": self.grader, "log": (proc.stdout + proc.stderr).decode(errors="replace")[-4000:]}
        extra = cat("/logs/verifier/details.json")
        if extra:
            details["details"] = json.loads(extra)
        return reward, details

    def close(self):
        if self.container:
            _docker("rm", "-f", self.container, check=False)
            self.container = None
