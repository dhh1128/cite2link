from ..cite import *


def assert_book(book, name, ordinal, abbrev, *names):
    assert book.names[0] == name
    assert book.ordinal == ordinal
    assert book.abbrev == abbrev
    if names:
        other_names = book.names[1:]
        for n in names:
            assert n in other_names

def test_book_counts():
    assert len(ot_books) == 39
    assert len(nt_books) == 27
    assert len(bom_books) == 15
    assert len(pgp_books) == 5

def test_easy_book():
    assert_book(nt_books[0], 'matthew', None, 'matt')

def test_ordinal_book():
    assert_book(bom_books[10], 'nephi', '3', 'ne')

def test_hard_book():
    assert_book(ot_books[21], 'song of solomon', None, 'song', 'sos', 'song of songs', 'canticles')

def test_uniques():

    # This test actually does a lot of work to calculate the correct minimum unique
    # abbreviation for each book. That's because calculating these abbreviations takes
    # longer than I want, so I want to hard-code the values in my array. If I get any
    # of the hard-coded values wrong, I want the test to tell me.

    def count_common(a, b):
        max_common = min(len(a), len(b))
        for i in range(max_common):
            if a[i] != b[i]:
                return i
        return max_common

    def uniques_are_perfect():
        perfect = True
        for collection in all_books:
            for book in collection:
                name = book.unique_basis
                common_len = 2 if book.ordinal else 1
                # Look at all other books; see which has the most letters in common
                # with the name of this one.
                for collection2 in all_books:
                    for book2 in collection2:
                        if book2 != book:
                            name2 = book2.unique_basis
                            common_len = max(common_len, count_common(name, name2))
                expected_unique = name[:common_len + 1]
                if book.unique != expected_unique:
                    print('Expected unique for %s to be "%s"' % (book.title, expected_unique))
                    perfect = False
        return perfect

    assert uniques_are_perfect()




