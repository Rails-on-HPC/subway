import sys
import os
import json

work_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(work_path))

from subway.cli import SubwayCLI
from subway.utils import load_json


def test_config(capsys):
    argv = ["-d", work_path, "config", "show"]
    cl = SubwayCLI(_argv=argv)
    cl()
    captured = capsys.readouterr()
    assert (
        captured.out
        == json.dumps(
            load_json(os.path.join(work_path, ".subway", "config.json")), indent=2
        )
        + "\n"
    )


def test_query_root(capsys):
    argv = ["-d", work_path, "query", "root"]
    cl = SubwayCLI(_argv=argv)
    cl()
    captured = capsys.readouterr()
    assert captured.out == "2fc840de-53c7-11ea-8f52-34363bc66daa" + "\n"


def test_query_leaves(capsys):
    argv = ["-d", work_path, "query", "leaves", "-j", "fe6"]
    cl = SubwayCLI(_argv=argv)
    cl()
    captured = capsys.readouterr()
    assert (
        captured.out
        == "14293906-53c8-11ea-b8c1-34363bc66daa\n"
        + "094816fe-53c8-11ea-885f-34363bc66daa\n"
    )


def test_query_condition(capsys):
    # caution: tso format is not suitable for test due to timezone issue,
    # may fail in CI with different tz
    argv = [
        "-d",
        work_path,
        "q",
        "-s",
        "beginning_ts>1582192941; state=pending",
    ]
    cl = SubwayCLI(_argv=argv)
    cl()
    captured = capsys.readouterr()
    assert captured.out == "14293906-53c8-11ea-b8c1-34363bc66daa\n"

    argv2 = ["-d", work_path, "q", "-s", "next>0ce870a6-53c8-11ea-9f9d-34363bc66daa"]
    cl = SubwayCLI(_argv=argv2)
    cl()
    captured = capsys.readouterr()
    assert captured.out == "02089a58-53c8-11ea-ae5b-34363bc66daa\n"

    argv3 = [
        "-d",
        work_path,
        "q",
        "-s",
        "prev<['14293906-53c8-11ea-b8c1-34363bc66daa','05a83858-53c8-11ea-9091-34363bc66daa']",
    ]
    # note the single quote ' in the list
    cl = SubwayCLI(_argv=argv3)
    cl()
    captured = capsys.readouterr()
    assert captured.out == "094816fe-53c8-11ea-885f-34363bc66daa\n"

    argv4 = [
        "-d",
        work_path,
        "q",
        "-s",
        "resource.cpu_count>1",
    ]
    # note the single quote ' in the list
    cl = SubwayCLI(_argv=argv4)
    cl()
    captured = capsys.readouterr()
    assert captured.out == "1089b602-53c8-11ea-bf63-34363bc66daa\n"

    argv5 = [
        "-d",
        work_path,
        "q",
        "-s",
        "resource.cpu_count<>1",
    ]
    # note the single quote ' in the list
    cl = SubwayCLI(_argv=argv5)
    cl()
    captured = capsys.readouterr()
    assert captured.out == "1089b602-53c8-11ea-bf63-34363bc66daa\n"
