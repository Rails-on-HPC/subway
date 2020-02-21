import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from subway import htree
from subway import utils

history_path = os.path.join(os.path.dirname(__file__), "history.json")
history = utils.load_json(history_path)
h = htree.HTree(history)


def test_parent():
    assert (
        h.parent("acbc108c-53c7-11ea-853a-34363bc66daa", 0)
        == "2fc840de-53c7-11ea-8f52-34363bc66daa"
    )
    assert (
        h.parent("cd7ea6ba-53c7-11ea-9396-34363bc66daa", 2)
        == "336b38e2-53c7-11ea-ad00-34363bc66daa"
    )
    assert h.roots() == ["2fc840de-53c7-11ea-8f52-34363bc66daa"]


def test_child():
    assert h.children("2fc840de-53c7-11ea-8f52-34363bc66daa", 0) == [
        "14293906-53c8-11ea-b8c1-34363bc66daa"
    ]
    assert set(h.leaves()) == {
        "14293906-53c8-11ea-b8c1-34363bc66daa",
        "094816fe-53c8-11ea-885f-34363bc66daa",
        "fac8e892-53c7-11ea-9087-34363bc66daa",
        "f722f0ca-53c7-11ea-a2f8-34363bc66daa",
        "4b275a36-53c7-11ea-92bd-34363bc66daa",
    }
    assert set(h.end("fe689376-53c7-11ea-aa97-34363bc66daa")) == {
        "14293906-53c8-11ea-b8c1-34363bc66daa",
        "094816fe-53c8-11ea-885f-34363bc66daa",
    }


def test_dfs():
    dfslist = [
        "fe689376-53c7-11ea-aa97-34363bc66daa",
        "02089a58-53c8-11ea-ae5b-34363bc66daa",
        "0ce870a6-53c8-11ea-9f9d-34363bc66daa",
        "1089b602-53c8-11ea-bf63-34363bc66daa",
        "14293906-53c8-11ea-b8c1-34363bc66daa",
        "05a83858-53c8-11ea-9091-34363bc66daa",
        "094816fe-53c8-11ea-885f-34363bc66daa",
    ]

    for i, r in enumerate(h.DFSvisit("fe689376-53c7-11ea-aa97-34363bc66daa")):
        assert r == dfslist[i]
