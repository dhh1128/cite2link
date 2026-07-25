from cite2link.cite import normalize_verses
from cite2link.errors import BadVerseRange, Cite2LinkError


def test_bad_verse_range_is_cite2link_error_and_value_error():
    assert issubclass(BadVerseRange, Cite2LinkError)
    # Backward compatibility: existing `except ValueError` callers still catch it.
    assert issubclass(BadVerseRange, ValueError)


def test_descending_range_raises_bad_verse_range():
    try:
        normalize_verses("5-3")
    except BadVerseRange as e:
        assert "5" in str(e) and "3" in str(e)
    else:
        raise AssertionError("expected BadVerseRange")


def test_non_numeric_verse_raises_bad_verse_range():
    try:
        normalize_verses("3-")
    except BadVerseRange:
        pass
    else:
        raise AssertionError("expected BadVerseRange")
