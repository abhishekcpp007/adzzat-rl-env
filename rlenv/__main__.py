"""Command line entry point.

  python -m rlenv run   --task ordinal-teens --policy oracle [--grader v2] [--episodes 3]
  python -m rlenv grade --task ordinal-teens --file my_inflection.py
  python -m rlenv play  --task ordinal-teens    (you are the agent)
  python -m rlenv study                          (every policy x task x grader)
"""
import argparse
import json
import sys
import time
from pathlib import Path

from .env import InflectionEnv, ROOT, list_tasks
from .policies import POLICIES

RUNS_DIR = ROOT / "runs"


def run_episode(task, policy, grader, seed=None):
    env = InflectionEnv(task, grader=grader, seed=seed)
    try:
        obs = env.reset()
        start = time.time()
        result = POLICIES[policy](env, obs)
        seconds = round(time.time() - start, 1)
        details = result.info.get("details", {})
        return {"task": task, "policy": policy, "grader": grader, "reward": result.reward,
                "steps": env.steps, "seconds": seconds, "seed": details.get("seed"),
                "groups": {g: s["failed"] == 0 for g, s in details.get("groups", {}).items()},
                "error": details.get("error")}
    finally:
        env.close()


def save(rows, name):
    RUNS_DIR.mkdir(exist_ok=True)
    path = RUNS_DIR / name
    with path.open("a") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    return path


def cmd_run(args):
    rows = []
    for _ in range(args.episodes):
        row = run_episode(args.task, args.policy, args.grader, args.seed)
        print(json.dumps(row))
        rows.append(row)
    save(rows, "runs.jsonl")


def cmd_grade(args):
    env = InflectionEnv(args.task, grader="v2", seed=args.seed)
    try:
        env.reset()
        env.step({"type": "write", "path": "/app/inflection.py",
                  "content": Path(args.file).read_text()})
        result = env.step({"type": "submit"})
        print(result.info["log"])
        print("reward:", result.reward)
    finally:
        env.close()


def cmd_play(args):
    env = InflectionEnv(args.task, grader=args.grader, seed=args.seed)
    try:
        print(env.reset())
        print("Type a shell command to run it in /app as the agent. Type 'submit' to grade.")
        while True:
            line = input("agent$ ").strip()
            if line == "submit":
                result = env.step({"type": "submit"})
                print(result.info["log"])
                print("reward:", result.reward)
                return
            if line:
                print(env.step({"type": "bash", "cmd": line}).observation)
    finally:
        env.close()


def cmd_study(args):
    rows = []
    for task in list_tasks():
        for grader in ("v1", "v2"):
            for policy in POLICIES:
                for _ in range(args.episodes):
                    row = run_episode(task, policy, grader)
                    print(json.dumps(row), flush=True)
                    rows.append(row)
    path = save(rows, "study.jsonl")
    print("saved", path)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="rlenv")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("run", "grade", "play", "study"):
        p = sub.add_parser(name)
        if name != "study":
            p.add_argument("--task", required=True, choices=list_tasks())
        p.add_argument("--seed", type=int)
        if name in ("run", "play"):
            p.add_argument("--grader", default="v2", choices=["v1", "v2"])
        if name == "run":
            p.add_argument("--policy", required=True, choices=sorted(POLICIES))
        if name in ("run", "study"):
            p.add_argument("--episodes", type=int, default=1)
        if name == "grade":
            p.add_argument("--file", required=True)
    args = parser.parse_args(argv)
    {"run": cmd_run, "grade": cmd_grade, "play": cmd_play, "study": cmd_study}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
