# inflection-env

A small RL environment built from the [`inflection`](https://github.com/jpvanhala/inflection)
library. It has four coding tasks in Harbor format plus a contamination probe, a gym-style Python
interface, a grader the agent can't read or reach, and a measured study of
what happens when you try to cheat it.

- [SCOPE.md](SCOPE.md): what the agent does, what success is, why a lab would care
- [RESULTS.md](RESULTS.md): exploit attempts, agent runs, and what they don't prove

## Quick start

You need Docker and Python 3.12.

```bash
make setup                                   # venv with pytest
make run TASK=acronym-support POLICY=oracle  # one episode, prints the reward
make grade TASK=acronym-support FILE=path/to/inflection.py   # grade any file
```

Other commands:

```bash
make test        # 143 unit tests, no Docker needed
make study       # every policy on every task with both graders, then checks the table
make play TASK=ordinal-teens   # you are the agent: type shell commands, then `submit`
make harbor      # Harbor's own oracle and nop agents on all five tasks
```

## Layout

```
upstream/            inflection 0.5.1 as released, with its LICENSE and test suite
src/golds/           reference for the acronym feature (upstream is the reference for the rest)
src/tasks/           instructions, visible tests, bug list, per-task settings
src/cases/           fixed and random case generators, one file per task
src/grader/          grade.py, probe.py, test.sh (plus the old v1 grader for the study)
scripts/build_tasks.py   writes tasks/ from src/ (CI fails if they drift)
tasks/<name>/        Harbor tasks: instruction.md, task.toml, environment/, solution/, tests/
rlenv/               the environment, scripted policies and the CLI
tests/               unit tests for golds, bugs, graders and partial credit
runs/                study results, agent transcripts and grades
```

## The interface

```python
from rlenv.env import InflectionEnv

env = InflectionEnv("plural-rules")
obs = env.reset()          # instruction plus a listing of /app
result = env.step({"type": "bash", "cmd": "python -m pytest -q"})
result = env.step({"type": "read", "path": "/app/inflection.py"})
result = env.step({"type": "write", "path": "/app/inflection.py", "content": "..."})
result = env.step({"type": "submit"})
result.reward, result.done, result.info["details"]["groups"]
```

The observation is text. Each action is one of four dicts, and an episode ends
on `submit` or after 50 steps. Every step runs as the user `agent` in a
container started with `--network none`.

## How grading works

1. `submit` copies `/app/inflection.py` out of the agent's container. Nothing
   else crosses over.
2. A fresh container starts from the clean task image. The file goes in, and
   so does `tests/`, which the agent never saw.
3. `test.sh` locks `/tests` to root. `grade.py` builds the fixed cases plus a
   few hundred random ones from a new seed, and runs the reference on them.
4. The submitted module runs in a separate process as `nobody`, through
   `probe.py`. That process gets the inputs on stdin and returns the outputs
   between two random markers. It can't read the reference and has nothing to
   copy.
5. Results are compared case by case. A result has to be a real `str`, so a
   string subclass that lies in `__eq__` doesn't count, and exceptions are
   compared by type.

The seed lands in `/logs/verifier/details.json` with per-group counts and a
few failing examples, so `GRADING_SEED=<seed>` replays a run exactly.

## Harbor

Each folder in `tasks/` is a Harbor task. `task.toml` runs the agent as
`agent` and the verifier as `root`, with `network_mode = "no-network"`.
`harbor run -p tasks/acronym-support -a oracle` scores 1.0 and `-a nop`
scores 0.0 on all of them (`runs/harbor_summary.txt`).

On Docker Desktop for macOS Harbor's local provider can't enforce
`no-network`, because the VM kernel lacks nftables. `make harbor` works around
that by running a temporary copy without the line. On Linux use
`scripts/harbor_check.sh --keep-network`.

Under Harbor the verifier shares the agent's container, so it's weaker than
`rlenv`'s fresh-container grading. Running the agent as a non-root user covers
most of the gap: it can't touch the Python install, `setpriv` or `/tests`.
RESULTS.md lists what's left.

## Adding a task

Add a `(old, new)` pair to `src/tasks/bugs.py`, an instruction and visible
tests under `src/tasks/<name>/`, a case file under `src/cases/`, and a
`src/tasks/<name>.toml`. Then run `make tasks test`. The unit tests check that
the gold scores 1.0 on five seeds, the starting file scores 0.0, every scored
group catches its bug, and the visible tests fail before the fix and pass
after.

## Portfolio evidence

My earlier RL environment work is [Gauntlet](https://github.com/abhishekcpp007/gauntlet-harness).
It turns freshly merged GitHub PRs into Docker environments for coding agents,
and the reward comes from hidden tests. I wrote all of it: the task mining,
the grader, the canary tests and file hashing that catch tampering, and the
cheater policies that attack my own grader. Its Gauntlet Live set has 53
tasks, where the oracle resolves 53 of 53 and the forging cheater is caught on
53 of 53.

## AI tools used

I built this with Claude Code (Claude Opus) as a pair programmer. It wrote
most of the first drafts of the code and docs from my design, and I reviewed,
ran and changed them. The design choices are mine: the library, the four
tasks, the differential grader, running the probe as `nobody`, and the exploit
list. The agent runs in RESULTS.md used Claude Code in headless mode with
Haiku and Sonnet through my existing Claude Code plan, so they cost nothing
extra. No paid API calls or cloud compute were used.

## License

My code is MIT. `upstream/` and the copies of `inflection.py` in `tasks/` are
inflection 0.5.1, MIT, copyright Janne Vanhala (see `upstream/LICENSE`).
