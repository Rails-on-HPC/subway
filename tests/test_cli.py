import sys
import os
import json

work_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(work_path))

from subway.cli import SubwayCLI
from subway.utils import load_json


def test_version():
    argv = ["-V"]
    cl = SubwayCLI(_argv=argv)
    cl()


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
    # argv2 = ["-d", work_path, "config", "edit"]
    # cl = SubwayCLI(_argv=argv2)
    # cl()


def test_init(tmpdir):
    argv = ["-d", tmpdir, "init"]
    cl = SubwayCLI(_argv=argv)
    cl()
    argv = ["-d", tmpdir, "d", "reinit"]
    cl = SubwayCLI(_argv=argv)
    cl()


def test_initc(tmpdir):
    config_path = os.path.join(work_path, ".subway", "config.json")
    argv = ["-d", tmpdir, "init", "-c", config_path]
    cl = SubwayCLI(_argv=argv)
    cl()


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


def test_query_info():
    argv = ["-d", work_path, "query", "info"]
    cl = SubwayCLI(_argv=argv)
    cl()
    argv2 = ["-d", work_path, "query", "-j", "14293906", "i"]
    cl = SubwayCLI(_argv=argv2, _test=True)
    assert cl() == 10
    argv3 = ["-d", work_path, "query", "-j", "14293906", "checking_time"]
    cl = SubwayCLI(_argv=argv3, _test=True)
    cl()
    argv4 = ["-d", work_path, "query", "assoc"]
    cl = SubwayCLI(_argv=argv4, _test=True)
    assert cl() == 12


def test_query_condition(capsys):
    # caution: tso format is subtle for test due to timezone issue,
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
    cl = SubwayCLI(_argv=argv5)
    cl()
    captured = capsys.readouterr()
    assert captured.out == "1089b602-53c8-11ea-bf63-34363bc66daa\n"

    argv6 = [
        "-d",
        work_path,
        "q",
        "-s",
        "resource.param.list_0=2",
    ]
    # get list element with key in the form of list_n
    cl = SubwayCLI(_argv=argv6)
    cl()
    captured = capsys.readouterr()
    assert captured.out == "4b275a36-53c7-11ea-92bd-34363bc66daa\n"
