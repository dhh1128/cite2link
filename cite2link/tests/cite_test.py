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
        for book in next_book(all_books):
            name = book.unique_basis
            common_len = 2 if book.ordinal else 1
            # Look at all other books; see which has the most letters in common
            # with the name of this one.
            for book2 in next_book(all_books):
                if book2 != book:
                    name2 = book2.unique_basis
                    common_len = max(common_len, count_common(name, name2))
            expected_unique = name[:common_len + 1]
            if book.unique != expected_unique:
                print('Expected unique for %s to be "%s"' % (book.title, expected_unique))
                perfect = False
        return perfect

    assert uniques_are_perfect()


def assert_found(lookup, title):
    x = find_book(lookup)
    assert x
    assert x.title == title


def test_books_found():
    assert_found('eze', 'Ezekiel')
    assert_found('do', 'Doctrine and Covenants')
    assert_found('d&amp;c', 'Doctrine and Covenants')
    assert_found('d&c', 'Doctrine and Covenants')
    assert_found('dc', 'Doctrine and Covenants')
    assert_found('lu', 'Luke')
    assert_found('Matthe', 'Matthew')
    assert_found('sos', 'Song of Solomon')
    assert_found('Canticles', 'Song of Solomon')
    assert_found('1jn', '1 John')
    assert_found('ThirdJohn.', '3 John')
    assert_found('2nd Pet.', '2 Peter')
    assert_found('4th nephi', '4 Nephi')
    assert_found('3 ne.', '3 Nephi')
    assert_found('1chr', '1 Chronicles')
    assert_found('1 chron', '1 Chronicles')
    assert_found('genesis', 'Genesis')


def test_books_not_found():
    # Not enough characters for reliable match
    assert find_book('m') is None
    # Too many characters
    assert find_book('matthewx') is None
    # Partial name that isn't canonical and therefore not truncatable
    assert find_book('Cantic') is None


def xtest_parse():
    x = parse("1 Ne 3:7")
    assert x.book.title == "1 Ne"
    assert x.chapter == '3'
    assert x.verses == ['7']

