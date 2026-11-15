import inflection


def test_accents():
    assert inflection.parameterize("Jürgen Müller") == "jurgen-muller"
    assert inflection.transliterate("älämölö") == "alamolo"


def test_custom_separator():
    assert inflection.parameterize("  Hello, World!  ", separator="_") == "hello_world"


def test_default_separator():
    assert inflection.parameterize("Donald E. Knuth") == "donald-e-knuth"
