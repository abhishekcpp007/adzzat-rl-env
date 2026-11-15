import string

from common import WORDS, call, snake

GROUPS = ["registry", "camelize", "underscore", "humanize", "titleize", "regression"]

FIXED_ACRONYMS = ["API", "URL", "IO", "HTML5", "ID"]

FIXED_SNAKE = ["api_client", "client_api", "my_api_url_parser", "io_error",
               "html5_parser", "api_v2", "user_id", "url", "id", "api_key_id",
               "the_api_of_io", "rapid_api"]


def with_acronyms(acronyms, group, fn, *args, **kwargs):
    case = call(group, fn, *args, **kwargs)
    case["acronyms"] = list(acronyms)
    return case


def fixed_cases():
    cases = [
        with_acronyms([], "registry", "add_acronym", "Api"),
        with_acronyms([], "registry", "add_acronym", "A"),
        with_acronyms([], "registry", "add_acronym", "2FA"),
        with_acronyms([], "registry", "add_acronym", ""),
        with_acronyms([], "registry", "add_acronym", "HTTP"),
        with_acronyms(["API"], "registry", "camelize", "api_client"),
        with_acronyms(["API", "API"], "registry", "camelize", "api_client"),
        with_acronyms([], "registry", "camelize", "api_client"),
        with_acronyms([], "registry", "underscore", "APIClient"),
    ]
    for word in FIXED_SNAKE:
        camel_upper = with_acronyms(FIXED_ACRONYMS, "camelize", "camelize", word)
        camel_lower = with_acronyms(FIXED_ACRONYMS, "camelize", "camelize", word, False)
        cases += [camel_upper, camel_lower,
                  with_acronyms(FIXED_ACRONYMS, "humanize", "humanize", word),
                  with_acronyms(FIXED_ACRONYMS, "titleize", "titleize", word)]
    for camel in ["APIClient", "ClientAPI", "MyAPIURLParser", "IOError",
                  "HTML5Parser", "APIV2", "UserID", "ParseHTML5Document"]:
        cases += [with_acronyms(FIXED_ACRONYMS, "underscore", "underscore", camel),
                  with_acronyms(FIXED_ACRONYMS, "titleize", "titleize", camel)]
    return cases


def random_acronyms(rng):
    chosen = []
    for _ in range(rng.randint(1, 4)):
        letters = "".join(rng.choice(string.ascii_uppercase) for _ in range(rng.randint(2, 4)))
        if rng.random() < 0.2:
            letters += rng.choice(string.digits)
        if any(a.startswith(letters) or letters.startswith(a) for a in chosen):
            continue
        chosen.append(letters)
    return chosen


def camelized(reference, acronyms, word):
    reference.clear_acronyms()
    for acronym in acronyms:
        reference.add_acronym(acronym)
    try:
        return reference.camelize(word)
    finally:
        reference.clear_acronyms()


def random_cases(rng, reference):
    cases = []
    for _ in range(80):
        acronyms = random_acronyms(rng)
        vocabulary = WORDS + [a.lower() for a in acronyms] * 6
        word = snake(rng, vocabulary)
        cases += [
            with_acronyms(acronyms, "camelize", "camelize", word),
            with_acronyms(acronyms, "camelize", "camelize", word, False),
            with_acronyms(acronyms, "humanize", "humanize", word),
            with_acronyms(acronyms, "titleize", "titleize", word),
            with_acronyms(acronyms, "underscore", "underscore", word),
            with_acronyms(acronyms, "underscore", "underscore", camelized(reference, acronyms, word)),
        ]
    for _ in range(40):
        word = snake(rng, WORDS)
        camel = "".join(part.capitalize() for part in word.split("_"))
        cases += [
            with_acronyms([], "regression", "camelize", word),
            with_acronyms([], "regression", "camelize", word, False),
            with_acronyms([], "regression", "underscore", camel),
            with_acronyms([], "regression", "humanize", word + rng.choice(["", "_id"])),
            with_acronyms([], "regression", "titleize", camel),
            with_acronyms([], "regression", "tableize", camel),
        ]
    return cases
