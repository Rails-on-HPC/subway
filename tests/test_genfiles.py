import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from subway.components.genfiles import jsonify, generate_file


def test_jsonify():
    assert jsonify([1, 2, [2, 3]], _outer_most=True) == {
        "list": [1, 2, {"list": [2, 3]}]
    }
    assert jsonify({"a": "A", "b": None, "c": [1, 2]}, _outer_most=True) == {
        "a": "A",
        "b": None,
        "c": [1, 2],
    }
    assert jsonify((1, 3.0), _outer_most=True) == {"list": [1, 3]}
    assert jsonify(1, _outer_most=True) == {"int": 1}


@pytest.mark.parametrize(
    "template",
    [
        ["{a~b}b{a~c~list_0}d", "1b2d"],
        ["{a~c~list_1}c{d}", "3cef"],
        ["a", "a"],
        ["J=\n{a~b}", "J=\n1"],
    ],
    indirect=True,
)
def test_generate_file_template(template):
    data = {"a": {"b": 1, "c": [2, 3]}, "d": "ef"}
    generate_file(
        data,
        output_template=os.path.join(os.path.dirname(__file__), "test.template"),
        output_path=os.path.join(os.path.dirname(__file__), "test.out"),
    )
