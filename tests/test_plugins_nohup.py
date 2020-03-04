import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from subway.cli import SubwayCLI


@pytest.mark.long
def test_rgn(tmpdir):
    argv = ["-d", tmpdir, "debug", "setup", "rgn"]
    SubwayCLI(_argv=argv, _test=True)()
    argv2 = ["-d", tmpdir, "r"]
    SubwayCLI(_argv=argv2, _test=True)()
    argv3 = ["-d", tmpdir, "q", "t"]
    SubwayCLI(_argv=argv3, _test=True)()
    argv4 = ["-d", tmpdir, "c", "show"]
    SubwayCLI(_argv=argv4, _test=True)()
    argv5 = ["-d", tmpdir, "query", "-s", "state<>checked"]
    SubwayCLI(_argv=argv5, _test=True)()


@pytest.mark.long
def test_pin(tmpdir):
    argv = ["-d", tmpdir, "debug", "setup", "pin"]
    SubwayCLI(_argv=argv, _test=True)()
    argv2 = ["-d", tmpdir, "r"]
    SubwayCLI(_argv=argv2, _test=True)()
    argv3 = ["-d", tmpdir, "q", "t"]
    SubwayCLI(_argv=argv3, _test=True)()
    argv4 = ["-d", tmpdir, "c", "show"]
    SubwayCLI(_argv=argv4, _test=True)()
    argv5 = ["-d", tmpdir, "query", "-s", "state<>checked"]
    SubwayCLI(_argv=argv5, _test=True)()
