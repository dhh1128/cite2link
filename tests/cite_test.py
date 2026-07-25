from pytest import raises

from cite2link.cite import *


def assert_parse(ref, book, chapter, verse, allow_gc=False):
    b, ch, v = parse(ref, allow_gc=allow_gc)
    assert b == book
    assert ch == chapter
    assert v == verse


def test_parse():
    assert_parse("eph  4", "eph", "4", None)
    assert_parse("1jn01:06-10", "1jn", "01", "06-10")
    assert_parse("1jn.01:06-10", "1jn.", "01", "06-10")
    assert_parse("Gen 33:1, 3-4", "Gen", "33", "1, 3-4")
    assert_parse("1 Ne 3:7", "1 Ne", "3", "7")


def test_parse_gc():
    # ~4g46 GC-citation parsing is inert/opt-in; exercise it via allow_gc=True.
    assert_parse("april2006 wood:instruments", "a06", "wood", "instruments", allow_gc=True)
    assert_parse("OCTOB '96 nelson: Spirit of God", "O96", "nelson", "Spirit of God", allow_gc=True)
    assert_parse("o2013.bednar", "o13", "bednar", None, allow_gc=True)
    assert_parse("Apr20,holland ,songs", "A20", "holland", "songs", allow_gc=True)
    assert_parse(
        "Oct_17/O'Rourke;It's crazy--but oh well!",
        "O17",
        "O'Rourke",
        "It's crazy--but oh well!",
        allow_gc=True,
    )
    assert_parse("aP00; José de la Peña:Martí", "a00", "José de la Peña", "Martí", allow_gc=True)


def test_parse_returns_none_for_unparseable():
    assert parse("this is not a citation") is None


def test_parse_allow_gc_falls_through_to_scripture():
    # allow_gc=True but the text isn't a GC citation, so it still parses as
    # scripture rather than being swallowed by the GC branch.
    assert parse("Genesis 1:1", allow_gc=True) == ("Genesis", "1", "1")


def test_resolve_unparseable_returns_none():
    assert resolve("this is not a citation") is None


def test_resolve_unknown_book_returns_none():
    # Parses fine as a citation shape, but the book is not in the library.
    assert resolve("Nonexistent 3:4") is None


def test_parse_gc_off_by_default():
    # Without allow_gc, a GC-style citation must not be treated as one; it falls
    # through to the scripture matcher (which yields a different shape) or None.
    assert parse("o2013.bednar") != ("o13", "bednar", None)


def assert_norm(input, output):
    assert join_nums_and_pairs(normalize_verses(input)) == output


def test_normalize_verses():
    assert_norm("4 - 12 7", "4-12")
    assert_norm("1-3 2, 3, 1, 1", "1-3")
    assert_norm("1-3 2-4", "1-4")
    assert_norm("01", "1")
    assert_norm("1,", "1")
    assert_norm(", 1 3,,, 2", "1-3")
    assert_norm("1,2 3", "1-3")
    assert_norm("1", "1")


def assert_bad(input):
    with raises(ValueError):
        normalize_verses(input)


def test_unnormalizable_verses():
    assert_bad("3-")
    assert_bad("3-1 2")
