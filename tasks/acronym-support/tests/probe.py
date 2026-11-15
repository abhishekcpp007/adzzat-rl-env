import json
import sys


def call_case(module, case):
    try:
        if "acronyms" in case:
            module.clear_acronyms()
            for acronym in case["acronyms"]:
                module.add_acronym(acronym)
        fn = getattr(module, case["fn"])
        value = fn(*case["args"], **case.get("kwargs", {}))
    except BaseException as exc:
        return {"ok": False, "error": type(exc).__name__}
    if value is not None and type(value) is not str:
        return {"ok": False, "error": "WrongType:" + type(value).__name__}
    return {"ok": True, "value": value}


def main():
    workdir = sys.argv[1]
    payload = json.loads(sys.stdin.read())
    nonce = payload["nonce"]
    sys.path.insert(0, workdir)
    try:
        import inflection
    except BaseException as exc:
        results = [{"ok": False, "error": "ImportError:" + type(exc).__name__}] * len(payload["cases"])
    else:
        results = [call_case(inflection, case) for case in payload["cases"]]
    sys.stdout.write("\n" + nonce + json.dumps(results) + nonce + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
