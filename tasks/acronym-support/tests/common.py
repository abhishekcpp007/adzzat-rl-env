import string

WORDS = [
    "account", "address", "agent", "apple", "batch", "billing", "bridge",
    "buffer", "cache", "client", "cluster", "config", "cursor", "device",
    "error", "event", "field", "filter", "folder", "graph", "group", "handler",
    "header", "image", "index", "invoice", "item", "job", "kernel", "label",
    "ledger", "loader", "manager", "message", "model", "node", "order",
    "owner", "packet", "page", "parser", "payment", "policy", "queue",
    "record", "report", "request", "router", "salary", "schema", "server",
    "session", "signal", "socket", "stream", "table", "task", "ticket",
    "token", "type", "user", "value", "vector", "widget", "worker", "zone",
]

VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnprstvwz"


def snake(rng, words, min_parts=1, max_parts=4):
    return "_".join(rng.choice(words) for _ in range(rng.randint(min_parts, max_parts)))


def stem(rng, min_len=2, max_len=6):
    out = []
    for i in range(rng.randint(min_len, max_len)):
        out.append(rng.choice(CONSONANTS if i % 2 == 0 else VOWELS))
    return "".join(out)


def call(group, fn, *args, **kwargs):
    case = {"group": group, "fn": fn, "args": list(args)}
    if kwargs:
        case["kwargs"] = kwargs
    return case


def regression_cases(rng, count, avoid=None):
    cases = []
    for _ in range(count):
        word = snake(rng, WORDS)
        camel = "".join(part.capitalize() for part in word.split("_"))
        cases += [
            call("regression", "camelize", word),
            call("regression", "camelize", word, False),
            call("regression", "underscore", camel),
            call("regression", "humanize", word + rng.choice(["", "_id"])),
            call("regression", "titleize", camel),
            call("regression", "dasherize", word),
            call("regression", "tableize", camel),
            call("regression", "pluralize", rng.choice(WORDS)),
            call("regression", "singularize", rng.choice(WORDS) + "s"),
            call("regression", "ordinalize", rng.randint(-2000, 2000)),
            call("regression", "parameterize", word.replace("_", " ").title() + "!"),
        ]
    if avoid:
        cases = [case for case in cases if not avoid(case)]
    return cases


PRINTABLE = string.ascii_letters + string.digits + " !?,.;:'\"()&/"
