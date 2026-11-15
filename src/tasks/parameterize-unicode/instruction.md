# parameterize mangles accented text and custom separators

`/app/inflection.py` is a copy of the `inflection` library (a Python port of the
Rails inflector). Two users report problems with URL slugs.

The first one:

```python
>>> inflection.parameterize("Jürgen Müller")
'j-rgen-m-ller'
>>> inflection.transliterate("Ærøskøbing")
'rskbing'
```

Accented letters should turn into their plain ASCII letter (`ü` becomes `u`,
`é` becomes `e`), so the slug is `jurgen-muller`. Characters with no ASCII
version can be dropped. The fix belongs in `transliterate`, which
`parameterize` calls.

The second one:

```python
>>> inflection.parameterize("  Hello, World!  ", separator="_")
'_hello__world_'
```

With any separator, `parameterize` should never leave two separators in a row
and should never start or end with one, so this should be `hello_world`. The
default separator `-` already works that way. An empty separator just removes
the unwanted characters. Tests only use a single character or the empty string
as a separator.

Fix both problems in `/app/inflection.py`. Don't change the public API, and
don't break any other function in the module.

`/app/test_visible.py` has a few examples you can run with `pytest`. The grader
uses its own, larger set of tests.
