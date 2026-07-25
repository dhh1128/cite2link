"""Render a resolved citation into the various output styles.

Each ``make_*`` function turns a ``(book, chapter, verses)`` triple into one
string. Decorating it with :func:`citation_style` registers it (in definition
order) so :func:`print_all` can emit every style without a hand-maintained list
— add a new style by writing a decorated function, nothing else.
"""

from __future__ import annotations

from collections.abc import Callable

from .books import Book
from .cite import Verse, join_nums_and_pairs

# ~6aid Future: alternate link targets besides churchofjesuschrist.org (e.g.
# blueletterbible.com, biblehub.com). ~4fll Future: support Bible editions /
# translations (KJV vs NLT, ...) as another dimension of the generated link.
cojesuschrist_base = "https://www.churchofjesuschrist.org/study/scriptures/"

# (label, maker) pairs, in definition order. Populated by @citation_style.
CitationMaker = Callable[[Book, str, "list[Verse] | None"], str]
_styles: list[tuple[str, CitationMaker]] = []


def citation_style(label: str) -> Callable[[CitationMaker], CitationMaker]:
    """Register a maker under ``label`` for :func:`print_all` to emit."""

    def register(maker: CitationMaker) -> CitationMaker:
        _styles.append((label, maker))
        return maker

    return register


def embed_html(ref: str, inner: str) -> str:
    return f'<a href="{ref}">{inner}</a>'


def embed_markdown(ref: str, inner: str) -> str:
    return f"[{inner}]({ref})"


@citation_style("churchofjesuschrist")
def make_churchofjesuschrist(book: Book, chapter: str, verses: list[Verse] | None) -> str:
    book_slug = book.slug.lower().replace(" ", "-").replace("&", "")
    if verses:
        first_verse_item = verses[0]
        first_verse = first_verse_item if isinstance(first_verse_item, int) else first_verse_item[0]
        fragment = f"#p{first_verse - 1}" if first_verse > 1 else ""
        verse_text = "." + join_nums_and_pairs(verses, ",")
    else:
        verse_text = fragment = ""
    return (
        f"{cojesuschrist_base}{book.collection_key}/{book_slug}/"
        f"{chapter}{verse_text}?lang=eng{fragment}"
    )


@citation_style("short ref")
def make_short_ref(book: Book, chapter: str, verses: list[Verse] | None) -> str:
    verse_text = ":" + join_nums_and_pairs(verses, ", ") if verses else ""
    return f"{book.slug} {chapter}{verse_text}"


@citation_style("long ref")
def make_long_ref(book: Book, chapter: str, verses: list[Verse] | None) -> str:
    verse_text = ":" + join_nums_and_pairs(verses, ", ") if verses else ""
    return f"{book.title} {chapter}{verse_text}"


def print_all(book: Book, chapter: str, verses: list[Verse] | None) -> None:
    """Print every registered citation style, then HTML and Markdown links."""
    for label, maker in _styles:
        print(label)
        print(f"  {maker(book, chapter, verses)}\n")

    url = make_churchofjesuschrist(book, chapter, verses)
    inner = make_short_ref(book, chapter, verses)
    print("html\n  " + embed_html(url, inner) + "\n")
    print("markdown\n  " + embed_markdown(url, inner) + "\n")
