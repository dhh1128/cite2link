from ..cite import resolve
from ..link import *


def check1(ref, url):
    book, chapter, verses = resolve(ref)
    assert make_churchofjesuschrist(book, chapter, verses) == 'https://www.churchofjesuschrist.org/study/scriptures/' + url


def test_churchofjesuschrist():
    check1('A of F 1:7', 'pgp/a-of-f/1.7?lang=eng#p6')
    check1('Official Declaration 2', 'dc-testament/od/2?lang=eng')
    check1('Joseph Smith History 1:17', 'pgp/js-h/1.17?lang=eng#p16')
    check1('ab 3:22,23', 'pgp/abr/3.22-23?lang=eng#p21')
    check1('D&C 93:2, 4-6, 17, 5', 'dc-testament/dc/93.2,4-6,17?lang=eng#p1')
    check1('1chr 3:15,14,13,15', 'ot/1-chr/3.13-15?lang=eng#p12')
    check1('1st John 2 : 1, 4, 5 9', 'nt/1-jn/2.1,4-5,9?lang=eng')
    check1('Moroni 10:4- 5', 'bofm/moro/10.4-5?lang=eng#p3')
    check1('Gen 1:1', 'ot/gen/1.1?lang=eng')
