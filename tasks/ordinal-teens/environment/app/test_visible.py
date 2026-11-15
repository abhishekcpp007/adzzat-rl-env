import inflection


def test_teens():
    assert inflection.ordinalize(11) == "11th"
    assert inflection.ordinalize(112) == "112th"
    assert inflection.ordinalize(-13) == "-13th"


def test_others_unchanged():
    assert inflection.ordinalize(1) == "1st"
    assert inflection.ordinalize(22) == "22nd"
    assert inflection.ordinalize(103) == "103rd"
