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


def test_query(capsys):
    argv = ["-d", work_path, "query", "root"]
    cl = SubwayCLI(_argv=argv)
    cl()
    captured = capsys.readouterr()
    assert captured.out == "2fc840de-53c7-11ea-8f52-34363bc66daa" + "\n"
