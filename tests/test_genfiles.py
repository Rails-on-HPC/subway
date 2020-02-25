import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from subway.components.genfiles import jsonify


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
