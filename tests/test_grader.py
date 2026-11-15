import random

import pytest

from helpers import task_modules


def fake_run(groups, failing):
    cases = [{"group": g} for g in groups]
    expected = [{"ok": True, "value": "x"} for _ in groups]
    actual = [{"ok": True, "value": "bad" if g in failing else "x"} for g in groups]
    return cases, expected, actual


def test_partial_credit_counts_fixed_groups():
    grade, _, _, config = task_modules("plural-rules")
    reward, _ = grade.score(config, *fake_run(config["groups"], {"f_to_ves"}))
    assert reward == 0.75


def test_partial_credit_is_zero_when_something_else_breaks():
    grade, _, _, config = task_modules("plural-rules")
    reward, _ = grade.score(config, *fake_run(config["groups"], {"regression"}))
    assert reward == 0.0


def test_binary_task_needs_every_group():
    grade, _, _, config = task_modules("acronym-support")
    assert grade.score(config, *fake_run(config["groups"], set()))[0] == 1.0
    assert grade.score(config, *fake_run(config["groups"], {"titleize"}))[0] == 0.0


def test_non_string_results_are_rejected():
    grade, _, _, _ = task_modules("ordinal-teens")

    class Liar(str):
        def __eq__(self, other):
            return True

    class Module:
        @staticmethod
        def ordinal(n):
            return Liar("st")

    assert grade.call_case(Module, {"fn": "ordinal", "args": [11]})["ok"] is False


def test_exceptions_are_compared_by_type():
    grade, _, reference, _ = task_modules("acronym-support")
    result = grade.call_case(reference, {"fn": "add_acronym", "args": ["Api"], "acronyms": []})
    assert result == {"ok": False, "error": "ValueError"}


@pytest.mark.parametrize("seed", range(30))
def test_acronym_round_trip_holds_on_generated_inputs(seed):
    _, cases_module, reference, _ = task_modules("acronym-support")
    rng = random.Random(seed)
    for _ in range(50):
        acronyms = cases_module.random_acronyms(rng)
        words = cases_module.WORDS + [a.lower() for a in acronyms] * 6
        word = cases_module.snake(rng, words)
        reference.clear_acronyms()
        for acronym in acronyms:
            reference.add_acronym(acronym)
        assert reference.underscore(reference.camelize(word)) == word, (acronyms, word)
    reference.clear_acronyms()


def test_random_cases_change_with_the_seed():
    _, cases_module, reference, _ = task_modules("ordinal-teens")
    first = cases_module.random_cases(random.Random(1), reference)
    second = cases_module.random_cases(random.Random(2), reference)
    assert first != second
