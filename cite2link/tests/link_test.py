from ..cite import resolve
from ..link import *


def test_churchofjesuschrist():
    def test(ref, url):
        book, chapter, verses = resolve(ref)
        assert make_churchofjesuschrist(
            book, chapter, verses) == 'https://www.churchofjesuschrist.org/study/scriptures/' + url

    test('A of F 1:7', 'pgp/a-of-f/1.7?lang=eng#p6')
    test('Official Declaration 2', 'dc-testament/od/2?lang=eng')
    test('Joseph Smith History 1:17', 'pgp/js-h/1.17?lang=eng#p16')
    test('ab 3:22,23', 'pgp/abr/3.22-23?lang=eng#p21')
    test('D&C 93:2, 4-6, 17, 5', 'dc-testament/dc/93.2,4-6,17?lang=eng#p1')
    test('1chr 3:15,14,13,15', 'ot/1-chr/3.13-15?lang=eng#p12')
    test('1st John 2 : 1, 4, 5 9', 'nt/1-jn/2.1,4-5,9?lang=eng')
    test('Moroni 10:4- 5', 'bofm/moro/10.4-5?lang=eng#p3')
    test('Gen 1:1', 'ot/gen/1.1?lang=eng')


def test_abbrev_ref():
    def test(ref, expected):
        book, chapter, verses = resolve(ref)
        assert make_short_ref(
            book, chapter, verses) == expected

    test('Joseph Smith --matt 1:17', 'JS-M 1:17')
    test('Art of Faith 1:7', 'A of F 1:7')
    test('Off Dec1', 'OD 1')
    test('ab 3:22,23', 'Abr 3:22-23')
    test('D&C 93:2, 4-6, 17, 5', 'D&C 93:2, 4-6, 17')
    test('1thessa 3: 1, 4, 5 9', '1 Thes 3:1, 4-5, 9')
    test('SecondJohn 1 :15,14,,12', '2 Jn 1:12, 14-15')
    test('Mor oni 10:4- 5', 'Moro 10:4-5')
    test('jOb33:1', 'Job 33:1')


def test_long_ref():
    def test(ref, expected):
        book, chapter, verses = resolve(ref)
        assert make_long_ref(
            book, chapter, verses) == expected

    test('Joseph Smith Matthew 1:1-3', 'Joseph Smith - Matthew 1:1-3')
    test('AOF 1:7', 'Articles of Faith 1:7')
    test('od1', 'Official Declaration 1')
    test('mose3:22, 23', 'Moses 3:22-23')
    test('jOb33:1', 'Job 33:1')
    test('D&C 93:2, 4-6, 17, 5', 'Doctrine & Covenants 93:2, 4-6, 17')
    test('1thessa 3: 1, 4, 5 9', '1 Thessalonians 3:1, 4-5, 9')
    test('SecondJohn 1 :15,14,,12', '2 John 1:12, 14-15')
    test('Mor oni 10:4- 5', 'Moroni 10:4-5')
    test('gEnesis1:1', 'Genesis 1:1')


def test_all():
    print_all(*resolve('Isa 29:14'))