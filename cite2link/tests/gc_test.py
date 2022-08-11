from ..gc import *


def test_expand_conf_id():
    assert expand_conf_id("a06") == ('april', 2006)
    assert expand_conf_id("O71") == ('october', 2071)
    assert expand_conf_id("OCt95") == ('october', 1995)


def xtest_find_talk():
    resp = find_talk("a06", "wood", "instruments")
    print(resp)
    assert 'General Conference' in resp