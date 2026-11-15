# Several English plural rules are broken

`/app/inflection.py` is a copy of the `inflection` library (a Python port of the
Rails inflector). After a bad refactor of the rule tables, users report:

```python
>>> inflection.pluralize("city")
'citys'          # should be 'cities'
>>> inflection.pluralize("wolf")
'wolfs'          # should be 'wolves'
>>> inflection.pluralize("dish")
'dishs'          # should be 'dishes'
>>> inflection.singularize("cities")
'citie'          # should be 'city'
```

The rules involved:

- a consonant followed by `y` pluralizes to `ies` (`party`, `parties`)
- a word ending in `lf` or `rf` pluralizes to `ves` (`shelf`, `shelves`)
- a word ending in `sh` or `ss` pluralizes to `es` (`kiss`, `kisses`)
- a word ending in a consonant followed by `ies` singularizes to `y`

Each of these four problems is scored on its own, so fixing some of them earns
partial credit. Breaking any other behavior of the module (for example
irregular words like `person`, or uncountable words like `sheep`) scores zero.

`/app/test_visible.py` has a few examples you can run with `pytest`. The grader
uses its own, larger set of tests.
