from common import call, regression_cases

GROUPS = ["ordinal", "regression"]

FIXED = [11, 12, 13, 111, 112, 113, 1011, 1012, 1013, -11, -12, -13, -111,
         -1013, 1, 2, 3, 4, 21, 22, 23, 101, 102, 103, 0, 10, 14, 20, 100]


def fixed_cases():
    cases = []
    for n in FIXED:
        cases.append(call("ordinal", "ordinal", n))
        cases.append(call("ordinal", "ordinalize", n))
    return cases


def random_cases(rng, reference):
    cases = []
    for _ in range(150):
        n = rng.randint(-10 ** 6, 10 ** 6)
        if rng.random() < 0.5:
            n = n - n % 100 + rng.choice([11, 12, 13])
        cases.append(call("ordinal", rng.choice(["ordinal", "ordinalize"]), n))
    return cases + regression_cases(rng, 20, avoid=touches_teens)


def touches_teens(case):
    return case["fn"] == "ordinalize" and abs(case["args"][0]) % 100 in (11, 12, 13)
