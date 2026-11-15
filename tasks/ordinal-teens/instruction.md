# Wrong ordinal suffix for 11, 12 and 13

`/app/inflection.py` is a copy of the `inflection` library (a Python port of the
Rails inflector). A user reports this:

```python
>>> inflection.ordinalize(11)
'11st'
>>> inflection.ordinalize(112)
'112nd'
>>> inflection.ordinalize(-13)
'-13rd'
```

Numbers whose last two digits are 11, 12 or 13 should always end in `th`
(`11th`, `112th`, `-13th`, `1011th`). Every other number keeps its current
suffix (`1st`, `22nd`, `103rd`, `-1021st`).

Fix `ordinal` and `ordinalize` in `/app/inflection.py`. Don't change the public
API, and don't break any other function in the module.

`/app/test_visible.py` has a few examples you can run with `pytest`. The grader
uses its own, larger set of tests.
