# Add acronym support

`/app/inflection.py` is a copy of the `inflection` library (a Python port of the
Rails inflector). Its docs admit this limitation:

```python
>>> inflection.camelize(inflection.underscore("IOError"))
'IoError'
```

Add acronym support, similar to Rails' `inflect.acronym`.

## New functions

- `add_acronym(word)` registers an acronym. A valid acronym is a `str` that
  starts with an upper case ASCII letter and has at least two characters, all
  of them upper case ASCII letters or digits (`API`, `IO`, `HTML5`). Anything
  else raises `ValueError` and registers nothing. Adding the same acronym twice
  is allowed and has no extra effect.
- `clear_acronyms()` removes every registered acronym.

With no acronyms registered, every function must behave exactly as it does
now.

## Behavior with acronyms registered

A "chunk" is a run of ASCII letters and digits between underscores. A chunk
matches an acronym when they are equal ignoring case.

1. `camelize(s)`: a chunk that matches an acronym is written as the acronym.
   Other chunks behave as today. `camelize("my_api_url_parser")` gives
   `MyAPIURLParser`.
2. `camelize(s, False)`: same, except that when the first chunk matches an
   acronym it is written fully in lower case. `camelize("api_client", False)`
   gives `apiClient`, and `camelize("client_api", False)` gives `clientAPI`.
3. `underscore(s)`: registered acronyms inside CamelCase text are treated as
   one word. For every snake_case string `s` whose chunks are lower case
   words made only of letters, or registered acronyms written in lower case,
   `underscore(camelize(s)) == s`.
   `underscore("MyAPIURLParser")` gives `my_api_url_parser` and
   `underscore("IOError")` gives `io_error`.
4. `humanize(s)` and `titleize(s)`: after the usual processing, any word
   (a run of ASCII letters and digits) that matches an acronym is written as
   the acronym. `humanize("api_key")` gives `API key`, and
   `titleize("MyAPIURLParser")` gives `My API URL Parser`.

The tests never register two acronyms where one is a prefix of the other.

## Example, with `API`, `URL`, `IO` and `HTML5` registered

```python
camelize("io_error")             # 'IOError'
camelize("api_v2")               # 'APIV2'
underscore("HTML5Parser")        # 'html5_parser'
humanize("client_api_id")        # 'Client API'
titleize("the_api_of_io")        # 'The API Of IO'
```

Keep the change inside `/app/inflection.py` and don't break any other function.

`/app/test_visible.py` has a few examples you can run with `pytest`. The grader
uses its own, larger set of tests, and it resets the registry with
`clear_acronyms()` between tests.
