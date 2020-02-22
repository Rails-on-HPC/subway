import sys
import os

work_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(work_path))

from subway.cli import SubwayCLI

def test_config():
    argv = ["-d", work_path, "config", "show"]
    # raise Exception("what is here", argv, "\n")
    cl = SubwayCLI(_argv=argv)
    cl()