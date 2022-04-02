from ..cite import *
from ..link import *

def test_churchofjesuschrist():
    b, ch, v = parse('Gen 1:1')
    book = find_book(b)
    v = join_nums_and_pairs(normalize_verses(v))
    assert make_churchofjesuschrist(book, ch, v) == 'x'