import inflection


def test_plurals():
    assert inflection.pluralize("city") == "cities"
    assert inflection.pluralize("wolf") == "wolves"
    assert inflection.pluralize("roof") == "rooves"
    assert inflection.pluralize("dish") == "dishes"


def test_singular():
    assert inflection.singularize("cities") == "city"


def test_untouched():
    assert inflection.pluralize("person") == "people"
    assert inflection.pluralize("sheep") == "sheep"
