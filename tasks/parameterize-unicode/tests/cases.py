from common import PRINTABLE, WORDS, call, regression_cases

GROUPS = ["transliterate", "parameterize", "regression"]

ACCENTED = "àáâäãåçèéêëìíîïñòóôöõùúûüýÿÀÁÂÄÃÅÇÈÉÊËÌÍÎÏÑÒÓÔÖÕÙÚÛÜÝ"
SEPARATORS = ["-", "_", ".", "+", "~", ""]

FIXED_TEXT = ["Jürgen Müller", "Ærøskøbing", "älämölö", "Crème brûlée",
              "  Hello, World!  ", "Donald E. Knuth", "São Paulo -- Brasil",
              "--already--dashed--", "naïve café", "a__b", "Ünïcödé___Tëst"]


def fixed_cases():
    cases = []
    for text in FIXED_TEXT:
        cases.append(call("transliterate", "transliterate", text))
        for sep in SEPARATORS:
            cases.append(call("parameterize", "parameterize", text, separator=sep))
    return cases


def random_text(rng):
    pool = PRINTABLE + ACCENTED * 2 + "_-"
    parts = []
    for _ in range(rng.randint(1, 5)):
        if rng.random() < 0.5:
            word = rng.choice(WORDS)
            word = "".join(rng.choice(ACCENTED) if rng.random() < 0.2 else ch for ch in word)
        else:
            word = "".join(rng.choice(pool) for _ in range(rng.randint(1, 8)))
        parts.append(word)
    return rng.choice([" ", "  ", " - ", "__", ", "]).join(parts)


def random_cases(rng, reference):
    cases = []
    for _ in range(120):
        text = random_text(rng)
        cases.append(call("transliterate", "transliterate", text))
        cases.append(call("parameterize", "parameterize", text, separator=rng.choice(SEPARATORS)))
    return cases + regression_cases(rng, 20)
