# Architecture & developer guide

cite2link is a small, dependency-free library with a thin CLI on top. This
document explains how a citation string becomes a set of links, and how to
extend the tool.

## The pipeline

A reference flows through three stages:

```
"Hel 5:1, 3, 4, 5, 7"
        │
        ▼   cite.parse()          syntactic recognition
("Hel", "5", "1, 3, 4, 5, 7")
        │
        ▼   books.find_book()     fuzzy book lookup
        │   cite.normalize_verses()  verse arithmetic
(Book<Helaman>, "5", [1, (3, 5), 7])
        │
        ▼   link.make_*() / print_all()   rendering
canonical URL, short/long ref, HTML, Markdown
```

`cite.resolve()` ties the first two stages together and is the usual entry
point; `link.print_all()` performs the third.

### 1. Parsing — `cite.py`

`parse(ref)` matches the reference against `scripture_cite_pat` and returns a
raw `(book_name, chapter, verses)` string triple, or `None` if the shape isn't
recognized. It is purely syntactic — it doesn't validate the book or the verse
numbers.

There is a second, **inert** pattern, `gc_cit_pat`, for General Conference talk
citations. It is gated behind `parse(ref, allow_gc=True)` and off by default so
it can never shadow scripture parsing (see [The GC feature](#the-general-conference-feature-inert)).

### 2. Resolution — `books.py` + verse normalization

`find_book(name)` does the fuzzy matching. Every `Book` is declared with a
compact string DSL (documented at the top of `books.py`):

```
long name|alternate name|another alt:CanonAbbrev/unique
```

- The pipe-separated names are every way the book may be written.
- The part after `:` is the canonical abbreviation used in the short reference.
- The part after `/` is the **shortest prefix that uniquely identifies** the
  book across the whole corpus, precomputed so lookups are fast. The
  `test_uniques` test recomputes these and fails if any hard-coded value is
  wrong, so the data can't silently drift.
- A leading digit is an ordinal (`1 Nephi`); matching requires the ordinals to
  agree.
- A first name ending in `!` marks a book cited without chapter and verse (a
  single number, e.g. an Official Declaration), which sets
  `Book.chapter_and_verse = False`.

`find_book` normalizes HTML entities and ordinal spellings, then walks the
library. It matches on an exact name, or on the unique-prefix rule (so `Genes`
resolves to Genesis but `gesture` does not).

Verse text is normalized by `cite.normalize_verses()`: it splits the list,
converts individual verses and ranges to ints and `(start, end)` pairs, sorts
them, and coalesces consecutive or overlapping entries into the tersest form
(`1, 2-3` → `1-3`). A descending or non-numeric range raises
`errors.BadVerseRange`.

### 3. Rendering — `link.py`

Each output style is a `make_*` function decorated with `@citation_style("label")`,
which appends `(label, function)` to the `_styles` registry in definition order.
`print_all()` iterates that registry, then adds the HTML and Markdown wrappers
(which reuse the canonical URL and short reference). There is no hand-maintained
list of styles to keep in sync.

## Errors — `errors.py`

Everything the library raises descends from `Cite2LinkError`. `BadVerseRange`
also subclasses `ValueError`, so code that already catches `ValueError` keeps
working. The CLI catches `Cite2LinkError` and turns it into a clean stderr
message plus exit code 1.

## Extending cite2link

### Add a new output style

Write a decorated function in `link.py`:

```python
@citation_style("plain url")
def make_plain_url(book, chapter, verses):
    return make_churchofjesuschrist(book, chapter, verses)
```

It is picked up by `print_all()` automatically; add a test asserting its output.

### Add a book or collection

Add an entry to the appropriate `_load(...)` block in `books.py` using the DSL
above, then update the corresponding count in `tests/books_test.py`. Run
`test_uniques` — if it fails, copy the "expected unique" value it prints into
your `/unique` suffix.

### The General Conference feature (inert)

`gc.py` is unfinished and not reachable from the CLI. To resume it (tracked by
tick mark `~4g46`): replace the raw search-HTML scrape with a real lookup that
extracts the canonical talk URL, add a `make_*` style plus a resolution path for
GC citations, enable `tests/gc_test.py::xtest_find_talk`, and document the
`[gc]` extra. Until then, keep GC parsing behind `allow_gc` so it can't affect
scripture handling.

## Releasing

`scripts/release.py` bumps the single-sourced version in
`src/cite2link/__init__.py`, runs the tests, commits (with DCO sign-off), and
pushes a `vX.Y.Z` tag. That tag triggers `.github/workflows/release.yml`, which
re-tests, builds, and publishes to PyPI via Trusted Publishing. See the module
docstring in `release.py` for options and the one-time PyPI registration.
