from ..cite import resolve
from ..link import *


def assert1(ref, url):
    book, chapter, verses = resolve(ref)
    assert make_html_churchofjesuschrist(book, chapter, verses) == 'https://www.churchofjesuschrist.org/study/scriptures/' + url


def test_html_churchofjesuschrist():
    assert1('Gen 1:1', 'ot/Gen/1.1?lang=eng')