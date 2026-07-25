"""Parse and normalize citation text.

The pipeline is: ``parse()`` recognizes the shape of a citation string,
``resolve()`` turns it into a concrete :class:`~cite2link.books.Book` plus a
normalized verse list, and the ``*_verses`` helpers do the verse arithmetic.
"""

from __future__ import annotations

import re

from .books import Book, find_book
from .errors import BadVerseRange

# A single verse (an int) or an inclusive verse range (a start/end pair).
Verse = int | tuple[int, int]

scripture_cite_pat = re.compile(
    r"""
    ((?:first|1(?:st)?|sec(?:ond)?|2(?:nd)?|third|3(?:rd)?|fourth|4(?:th)?)?\s* # leading volume
    (?:[a-z&.-]+(?:\ +[a-z&.-]+)*)) # book/author, cap group 1
    \W*
    (\d+) # chapter (or item, for some sources), cap group 2
    (?: # everything after chapter/item is optional
    \s*:\s*
    ([-0-9,\ ]+) # verses, cap group 3
    )? # end of optional part
    """,
    re.I | re.VERBOSE,
)


gc_cit_pat = re.compile(
    r"""
    (a[pril]*|o[ctober]*)[, -.'_]*(?:19|20)?(\d{2}) # which General Conference and year
    \W+
    ((?:\w|[ '-])+) # author surname (supports unicode)
    (?: # everything after surname is optional
    [ :,;]+(.*) # delim, then author given name and/or initial(s) and/or title keywords
    )? # end of optional part
    """,
    re.I | re.VERBOSE | re.U,
)


def parse(ref: str, allow_gc: bool = False) -> tuple[str, str, str | None] | None:
    """Recognize a reference as matching a standard citation format.

    Returns a ``(book_name, chapter, verses)`` tuple of raw strings if the shape
    is recognized, else ``None``. This is syntactic analysis only: it does not
    check that the book name is valid or that the chapter/verse portion makes
    sense. Most callers want :func:`resolve`, which also looks the book up.

    ~4g46 The General Conference talk finder (cite2link.gc) is unfinished and
    inert. GC-citation parsing is therefore opt-in via ``allow_gc``: off by
    default so it can never shadow scripture parsing on the normal path
    (:func:`resolve` never enables it). See the tick for what remains.
    """
    if allow_gc:
        m = gc_cit_pat.match(ref)
        if m:
            return m.group(1)[0] + m.group(2), m.group(3).rstrip(), m.group(4)
    m = scripture_cite_pat.match(ref)
    if m:
        return m.group(1), m.group(2), m.group(3)
    return None


def resolve(ref: str) -> tuple[Book, str, list[Verse] | None] | None:
    """Resolve a reference to something this library knows about.

    Returns ``(book, chapter, verses)`` — where ``book`` is a :class:`Book`, and
    ``verses`` is a list of normalized ints and int pairs (or ``None`` for books
    cited without verses) — or ``None`` if the reference cannot be parsed or the
    book is unknown. Raises :class:`BadVerseRange` if the verse text is malformed.
    """
    triple = parse(ref)
    if not triple:
        return None
    book = find_book(triple[0])
    if not book:
        return None
    verses = normalize_verses(triple[2]) if book.chapter_and_verse else None
    return book, triple[1], verses


_verse_range_pat = re.compile(r"(\d+)-(\d+)")
_verse_splitter_pat = re.compile(r"[ ,]+")
_space_range_pat = re.compile(r" +-")
_range_space_pat = re.compile(r"- +")


def split_verses(verses: str) -> list[str]:
    """Split verse text on runs of commas and spaces, dropping empties."""
    verses = _verse_splitter_pat.split(_range_space_pat.sub("-", _space_range_pat.sub("-", verses)))
    return [v for v in verses if v]


def _to_int(token: str) -> int:
    """Parse a verse number, raising :class:`BadVerseRange` on non-numeric text."""
    try:
        return int(token)
    except ValueError:
        raise BadVerseRange(f'Not a verse number: "{token}".') from None


def get_nums_and_pairs_from_verses_text(verses: list[str]) -> list[Verse]:
    """Convert verse/range strings to ints and int pairs.

    ``'3', '5', '7-10'`` --> ``[3, 5, (7, 10)]``. Raises :class:`BadVerseRange`
    for a descending range or a non-numeric token.
    """
    items: list[Verse] = []
    for item in verses:
        m = _verse_range_pat.match(item)
        if m:
            pair = (int(m.group(1)), int(m.group(2)))
            if pair[0] > pair[1]:
                raise BadVerseRange(f'Bad range "{item}"; {m.group(1)} > {m.group(2)}.')
            items.append(pair)
        else:
            items.append(_to_int(item))
    return items


def join_nums_and_pairs(verses: list[Verse], joiner: str = ", ") -> str:
    """Join ints and int pairs into text: ``[3, 5, (7, 10)]`` --> ``"3, 5, 7-10"``."""
    return joiner.join(str(x) if isinstance(x, int) else f"{x[0]}-{x[1]}" for x in verses)


def normalize_verses(verses: str) -> list[Verse]:
    """Put verses into canonical form.

    Ordered, with no redundancies or overlaps, and with maximum use of ranges
    for terseness. Returns a list of ints and int pairs; call
    :func:`join_nums_and_pairs` to render it as text.
    """
    nums_and_pairs = get_nums_and_pairs_from_verses_text(split_verses(verses))
    # Sort by the starting verse.
    ordered = sorted(nums_and_pairs, key=lambda x: x if isinstance(x, int) else x[0])
    # Walk the sorted verses, coalescing consecutive/overlapping items into
    # ranges and dropping redundancies.
    result: list[Verse] = []
    end = -1
    for item in ordered:
        is_num = isinstance(item, int)
        new = item if is_num else item[0]
        # A gap wide enough to start a fresh item in the normalized list?
        if (new > end + 1) or not result:
            if is_num:
                end = new
                result.append(new)
            else:
                end = item[1]
                result.append((new, end))
        else:
            extend = False
            prev = result[-1]
            prev_is_num = isinstance(prev, int)
            # A value one past the last verse (e.g. "1, 2-3" that should be "1-3")?
            if new == end + 1:
                extend = True
            # An overlapping range that reaches past the current end?
            elif not is_num and item[1] > end:
                extend = True
            if extend:
                old_start = prev if prev_is_num else prev[0]
                result[-1] = (old_start, new) if is_num else (old_start, item[1])
                end = result[-1][1]
            # else this item is wholly contained in what we already have
    return result
