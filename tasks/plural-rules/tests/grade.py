import importlib.util
import json
import os
import random
import secrets
import shutil
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
APP_FILE = "/app/inflection.py"
VERIFIER_DIR = "/logs/verifier"
NOBODY_UID = 65534
NOBODY_GID = 65534
PROBE_TIMEOUT_SEC = 120

sys.path.insert(0, TESTS_DIR)

from probe import call_case  # noqa: E402


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_cases(seed):
    reference = load_module(os.path.join(TESTS_DIR, "reference.py"), "reference")
    cases_module = load_module(os.path.join(TESTS_DIR, "cases.py"), "cases")
    cases = cases_module.fixed_cases() + cases_module.random_cases(random.Random(seed), reference)
    expected = [call_case(reference, case) for case in cases]
    return cases, expected


def run_probe(cases):
    workdir = tempfile.mkdtemp(prefix="probe-")
    os.chmod(workdir, 0o755)
    shutil.copy(APP_FILE, os.path.join(workdir, "inflection.py"))
    shutil.copy(os.path.join(TESTS_DIR, "probe.py"), os.path.join(workdir, "probe.py"))
    for name in os.listdir(workdir):
        os.chmod(os.path.join(workdir, name), 0o644)
    nonce = secrets.token_hex(16)
    command = ["setpriv", "--reuid=%d" % NOBODY_UID, "--regid=%d" % NOBODY_GID,
               "--clear-groups", sys.executable, "-I", "-B",
               os.path.join(workdir, "probe.py"), workdir]
    try:
        proc = subprocess.run(command, input=json.dumps({"nonce": nonce, "cases": cases}),
                              capture_output=True, text=True, timeout=PROBE_TIMEOUT_SEC,
                              cwd=workdir, env={"PATH": "/usr/local/bin:/usr/bin:/bin"})
    except subprocess.TimeoutExpired:
        return None, "probe timed out"
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    parts = proc.stdout.split(nonce)
    if len(parts) != 3:
        return None, "probe output missing (exit %s): %s" % (proc.returncode, proc.stderr[-500:])
    return json.loads(parts[1]), None


def score(config, cases, expected, actual):
    groups = {group: {"passed": 0, "failed": 0, "examples": []} for group in config["groups"]}
    for case, want, got in zip(cases, expected, actual):
        stats = groups[case["group"]]
        if want == got:
            stats["passed"] += 1
        else:
            stats["failed"] += 1
            if len(stats["examples"]) < 3:
                stats["examples"].append({"call": case, "expected": want, "got": got})
    ok = {group: stats["failed"] == 0 for group, stats in groups.items()}
    if config["mode"] == "partial":
        if not ok["regression"]:
            reward = 0.0
        else:
            scored = [g for g in config["groups"] if g != "regression"]
            reward = sum(ok[g] for g in scored) / len(scored)
    else:
        reward = 1.0 if all(ok.values()) else 0.0
    return reward, groups


def main():
    os.makedirs(VERIFIER_DIR, exist_ok=True)
    os.chmod(TESTS_DIR, 0o700)
    with open(os.path.join(TESTS_DIR, "grading.json")) as f:
        config = json.load(f)
    seed = int(os.environ.get("GRADING_SEED") or secrets.randbits(32))
    cases, expected = build_cases(seed)
    details = {"seed": seed, "cases": len(cases)}
    if not os.path.isfile(APP_FILE):
        reward, details["error"] = 0.0, "no /app/inflection.py"
    else:
        actual, error = run_probe(cases)
        if error:
            reward, details["error"] = 0.0, error
        else:
            reward, details["groups"] = score(config, cases, expected, actual)
    details["reward"] = reward
    with open(os.path.join(VERIFIER_DIR, "details.json"), "w") as f:
        json.dump(details, f, indent=2, ensure_ascii=False)
    with open(os.path.join(VERIFIER_DIR, "reward.txt"), "w") as f:
        f.write("%s\n" % reward)
    print(json.dumps({k: v for k, v in details.items() if k != "groups"}))
    for group, stats in details.get("groups", {}).items():
        print("%-14s passed=%-4d failed=%d" % (group, stats["passed"], stats["failed"]))


if __name__ == "__main__":
    main()
