import sys
import os
import pytest
from functools import partial
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from subway.utils import (
    replace_wildcard,
    simple_template_render,
    statement_parser,
    md5file,
    flatten_dict,
    editor,
)


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


@pytest.mark.parametrize(
    "template",
    [["{a}b{c}d", "AbCd"], ["{c}c{c}", "CcC"], ["a", "a"], ["{b}", "B"]],
    indirect=True,
)
def test_template_render(template):
    simple_template_render(
        os.path.join(os.path.dirname(__file__), "test.template"),
        os.path.join(os.path.dirname(__file__), "test.out"),
        {"a": "A", "b": "B", "c": "C"},
    )
    # with open(os.path.join(os.path.dirname(__file__), "test.out"), "r") as f:
    #     s = f.read()
    # assert s == "AbCd"


def test_statement_parser():
    stdans1 = {
        "a": ("=", "b"),
        "cc": ("=", "ad"),
        "e": (">", 17),
        "f": ("<=", datetime(2020, 2, 2)),
    }
    assert statement_parser("a=b;cc=ad e>17; f<=datetime(2020,2,2)") == stdans1
    assert statement_parser("a=b;cc=ad e>17;  f<=datetime(2020,2,2)") == stdans1
    assert statement_parser("a=b; cc=ad e>17;  f<=datetime(2020,2,2)") == stdans1
    assert statement_parser("a=b cc=ad e>17 f<=datetime(2020,2,2)") == stdans1


def test_md5file():
    assert (
        md5file(os.path.join(os.path.dirname(__file__), ".subway", "history.json"))
        == "ac9501d73459152e7e1c2ce11b6d9a7b"
    )


def test_flatten_dict():
    assert flatten_dict({"a": 1, "b": "cc"}, parent_key="h") == {"ha": 1, "hb": "cc"}
    assert flatten_dict(
        {"d": [{"m": "n", "k": ["zz"]}, 2, [3, 4]], "c": 1}, sep="~"
    ) == {
        "c": 1,
        "d~list_0~k~list_0": "zz",
        "d~list_0~m": "n",
        "d~list_1": 2,
        "d~list_2~list_0": 3,
        "d~list_2~list_1": 4,
    }


def _run(name):
    if name[0].endswith("vim"):
        raise OSError("no vim found")


def test_editor():
    editor(os.path.join(os.path.dirname(__file__), ".subway", "config.json"), _run=_run)
