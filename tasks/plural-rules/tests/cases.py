import re

from common import CONSONANTS, WORDS, call, regression_cases, stem

TARGET_ENDINGS = re.compile(r"([^aeiouy]y|[lr]f|sh|ss|[^aeiouy]ies|[^aeiouy]ys)$", re.IGNORECASE)

GROUPS = ["y_to_ies", "f_to_ves", "sh_ss_to_es", "ies_to_y", "regression"]

FIXED = {
    "y_to_ies": ["city", "party", "query", "fly", "Company", "category", "soliloquy"],
    "f_to_ves": ["wolf", "shelf", "half", "elf", "dwarf", "Calf"],
    "sh_ss_to_es": ["dish", "wish", "kiss", "class", "Bush", "process", "address"],
    "ies_to_y": ["cities", "parties", "queries", "flies", "Companies", "categories"],
}

KEEP = ["box", "church", "knife", "life", "day", "toy", "chief", "roof", "bus",
        "person", "child", "sheep", "fish", "octopus", "matrix", "quiz", "ox",
        "mouse", "potato", "status", "axis", "series", "movies", "news", "wives",
        "boys", "days", "buses", "analyses", "people", "children"]


def fixed_cases():
    cases = []
    for group, words in FIXED.items():
        fn = "singularize" if group == "ies_to_y" else "pluralize"
        cases += [call(group, fn, w) for w in words]
    cases += [call("regression", "pluralize", w) for w in KEEP]
    cases += [call("regression", "singularize", w) for w in KEEP]
    return cases


def random_cases(rng, reference):
    cases = []
    for _ in range(40):
        consonant = rng.choice(CONSONANTS.replace("y", ""))
        cases.append(call("y_to_ies", "pluralize", stem(rng) + consonant + "y"))
        cases.append(call("f_to_ves", "pluralize", stem(rng) + rng.choice("lr") + "f"))
        cases.append(call("sh_ss_to_es", "pluralize", stem(rng) + rng.choice(["sh", "ss"])))
        cases.append(call("ies_to_y", "singularize", stem(rng) + consonant + "ies"))
        cases.append(call("regression", "pluralize", stem(rng) + rng.choice(["x", "ch", "o", "ay", "ey", "fe", "t", "is"])))
    return cases + regression_cases(rng, 20, avoid=touches_target_rules)


def touches_target_rules(case):
    text = case["args"][0]
    if not isinstance(text, str) or case["fn"] not in ("pluralize", "singularize", "tableize"):
        return False
    last = re.split(r"[_\s]|(?<=[a-z])(?=[A-Z])", text)[-1]
    return bool(TARGET_ENDINGS.search(last))
