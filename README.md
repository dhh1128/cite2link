# cite2link

Convert scripture citations like `John 3:15` — and other canonical-source
references — into hyperlinks in several formats (a canonical
churchofjesuschrist.org URL, normalized short/long references, HTML, and
Markdown).

It is forgiving about how you write a reference. Abbreviations, alternate book
names, ordinals spelled any way (`1 Ne`, `First Nephi`, `1st nephi`), messy
verse lists, and out-of-order or overlapping verses are all normalized:

```console
$ cite2link "Hel 5:1, 3, 4, 5, 7"
churchofjesuschrist
  https://www.churchofjesuschrist.org/study/scriptures/bofm/hel/5.1,3-5,7?lang=eng

short ref
  Hel 5:1, 3-5, 7

long ref
  Helaman 5:1, 3-5, 7

html
  <a href="https://www.churchofjesuschrist.org/study/scriptures/bofm/hel/5.1,3-5,7?lang=eng">Hel 5:1, 3-5, 7</a>

markdown
  [Hel 5:1, 3-5, 7](https://www.churchofjesuschrist.org/study/scriptures/bofm/hel/5.1,3-5,7?lang=eng)
```

## Install

cite2link is a single command with **no runtime dependencies**. Install it as a
tool:

```bash
uv tool install cite2link      # or: pipx install cite2link
```

or add it to a project:

```bash
uv add cite2link               # or: pip install cite2link
```

Then run it:

```bash
cite2link "John 3:15"
cite2link 1 Ne 3:7             # quotes are optional if your shell allows it
```

## Using it as a library

The pieces the CLI is built from are public:

```python
from cite2link.cite import resolve
from cite2link.link import make_churchofjesuschrist, make_short_ref, print_all

resolved = resolve("Alma 32:21")  # -> (Book, chapter, [verses]) or None
if resolved:
    book, chapter, verses = resolved
    url = make_churchofjesuschrist(book, chapter, verses)
    label = make_short_ref(book, chapter, verses)
    print_all(book, chapter, verses)  # prints every style, like the CLI
```

`resolve()` returns `None` for anything it cannot parse or whose book it does
not recognize, and raises `cite2link.errors.BadVerseRange` (a subclass of both
`Cite2LinkError` and `ValueError`) for a malformed or descending verse range.

See the [Architecture & developer guide](docs/architecture.md) for how parsing,
resolution, and link generation fit together, and how to add a new output style
or source collection.

## Developer Quickstart

### Prerequisites

- [uv](https://docs.astral.sh/uv/) — manages the Python interpreter,
  virtualenv, and dependencies. uv will fetch a suitable Python (>=3.10).

### Setup

```bash
git clone https://github.com/dhh1128/cite2link.git
cd cite2link
uv sync                        # create the environment from uv.lock
```

### Running tests

```bash
uv run pytest                  # runs with coverage (fail_under = 95)
uv run --python 3.10 pytest    # prove the >=3.10 floor (CI runs 3.10–3.13)
```

### Lint & format

```bash
uv run ruff check .
uv run ruff format .
```

### Running the CLI from the checkout

```bash
uv run cite2link "Moroni 10:4-5"
```

## Project structure

- `src/cite2link/` — the library.
  - `cite.py` — parse a citation string and normalize its verses.
  - `books.py` — the canonical library of books and the fuzzy name lookup.
  - `link.py` — render a resolved citation into each output style (registered
    with the `@citation_style` decorator).
  - `app.py` — the `cite2link` command-line entry point.
  - `errors.py` — the exception hierarchy.
  - `gc.py` — an **unfinished, inert** General Conference talk finder (see
    below).
- `tests/` — the test suite.
- `scripts/` — maintenance tooling (`release.py`, `check_unicode.py`).
- `docs/` — the architecture / developer guide.

## The General Conference talk finder (unfinished)

`cite2link.gc` began as a way to turn a citation like `april2006 wood:instruments`
into a link to the talk. It is **not finished and not wired into the CLI**: it
only fetches raw search HTML, GC-citation parsing is opt-in
(`cite.parse(..., allow_gc=True)`) so it can't shadow scripture parsing, and its
only dependency (`requests`) lives behind an opt-in `[gc]` extra. The remaining
work is tracked in the repo's local [`tick`](https://github.com/dhh1128/tick)
ledger under mark `~4g46`.

## Contributing & security

- Development conventions for humans and AI agents live in
  [AGENTS.md](AGENTS.md).
- Report vulnerabilities privately per [SECURITY.md](SECURITY.md).

## License

[Apache-2.0](LICENSE).
