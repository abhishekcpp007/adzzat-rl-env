import pytest

import inflection


@pytest.fixture(autouse=True)
def acronyms():
    inflection.clear_acronyms()
    for word in ["API", "URL", "IO", "HTML5"]:
        inflection.add_acronym(word)
    yield
    inflection.clear_acronyms()


def test_camelize():
    assert inflection.camelize("my_api_url_parser") == "MyAPIURLParser"
    assert inflection.camelize("api_client", False) == "apiClient"


def test_underscore():
    assert inflection.underscore("MyAPIURLParser") == "my_api_url_parser"
    assert inflection.underscore("IOError") == "io_error"


def test_humanize_titleize():
    assert inflection.humanize("api_key") == "API key"
    assert inflection.titleize("MyAPIURLParser") == "My API URL Parser"


def test_invalid():
    with pytest.raises(ValueError):
        inflection.add_acronym("Api")
