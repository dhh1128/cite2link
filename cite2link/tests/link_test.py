from ..cite import resolve
from ..link import *


def assert1(ref, url):
    book, chapter, verses = resolve(ref)
    assert make_churchofjesuschrist(book, chapter, verses) == 'https://www.churchofjesuschrist.org/study/scriptures/' + url


def test_churchofjesuschrist():
    assert1('Joseph Smith History 1:17', 'pgp/js-h/1.17?lang=eng#p16')
    assert1('ab 3:22,23', 'pgp/abr/3.22-23?lang=eng#p21')
    assert1('D&C 93:2, 4-6, 17, 5', 'dc-testament/dc/93.2,4-6,17?lang=eng#p1')
    assert1('1chr 3:15,14,13,15', 'ot/1-chr/3.13-15?lang=eng#p12')
    assert1('1st John 2 : 1, 4, 5 9', 'nt/1-jn/2.1,4-5,9?lang=eng')
    assert1('Moroni 10:4- 5', 'bofm/moro/10.4-5?lang=eng#p3')
    assert1('Gen 1:1', 'ot/gen/1.1?lang=eng')
