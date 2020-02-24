import sys
import os
from functools import partial

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from subway.utils import replace_wildcard


def test_replace_wildcard():
    def translate_func(translate_dict, s):
        return translate_dict.get(s, "")

    caps_dict = {"a": "A", "b": "B", "c": "C", "d": "DD"}
    translate_pfunc = partial(translate_func, caps_dict)
    r = partial(replace_wildcard, translate_pfunc)

    assert r("") == ""
    assert r("a") == "a"
    assert r("abC") == "abC"
    for i in range(8):
        assert r("%" * i) == "%" * i
    assert r("%%a") == "%a"
    assert r("%%%a") == "%%a"
    assert r("%a") == "A"
    assert r("%ab") == "Ab"
    assert r("%eb") == "b"
    assert r("sf%c%dm%f") == "sfCDDm"
    assert r("%%ab%") == "%ab%"
    assert r("%Aal%cc%%") == "alCc%%"
    assert r("%ddD\n%%a") == "DDdD\n%a"
    assert r("slurm-%a.out") == "slurm-A.out"
    assert r("r%%%%a%a%%a%") == "r%%%aA%a%"
