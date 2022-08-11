from pytest import raises

from ..cite import *


def assert_parse(ref, book, chapter, verse):
    b, ch, v = parse(ref)
    assert b == book
    assert ch == chapter
    assert v == verse


def test_parse():
    assert_parse("eph  4", 'eph', '4', None)
    assert_parse("1jn01:06-10", '1jn', '01', '06-10')
    assert_parse("1jn.01:06-10", '1jn.', '01', '06-10')
    assert_parse("Gen 33:1, 3-4", 'Gen', '33', '1, 3-4')
    assert_parse("1 Ne 3:7", '1 Ne', '3', '7')


def test_parse_gc():
    assert_parse("april2006 wood:instruments", "a06", "wood", "instruments")
    assert_parse("OCTOB '96 nelson: Spirit of God", "O96", "nelson", "Spirit of God")
    assert_parse("o2013.bednar", "o13", "bednar", None)
    assert_parse("Apr20,holland ,songs", "A20", "holland", "songs")
    assert_parse("Oct_17/O'Rourke;It's crazy--but oh well!", "O17", "O'Rourke", "It's crazy--but oh well!")
    assert_parse("aP00; José de la Peña:Martí", "a00", "José de la Peña", "Martí")


def assert_norm(input, output):
    assert join_nums_and_pairs(normalize_verses(input)) == output


def test_normalize_verses():
    assert_norm('4 - 12 7', '4-12')
    assert_norm('1-3 2, 3, 1, 1', '1-3')
    assert_norm('1-3 2-4', '1-4')
    assert_norm('01', '1')
    assert_norm('1,', '1')
    assert_norm(', 1 3,,, 2', '1-3')
    assert_norm('1,2 3', '1-3')
    assert_norm('1', '1')


def assert_bad(input):
    with raises(Exception):
        normalize_verses(input)


def test_unnormalizable_verses():
    assert_bad('3-')
    assert_bad('3-1 2')
