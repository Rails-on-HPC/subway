import sys
import os
import pytest

work_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(work_path))

from subway import cons

cons.work_dir = work_path
from subway.plugins import DebugSub, DebugChk
from subway.workflow import main_once, main_rt
from subway.cli import SubwayCLI


def test_main_once(history):
    main_once(DebugChk(is_next=True, test=True), DebugSub())
    main_once(DebugChk(is_next=False, test=True), DebugSub())
    main_once(DebugChk(is_next=False, test=True), DebugSub())
    main_once(DebugChk(is_next=False, test=True), DebugSub())


def test_main_rt(history):
    main_rt(DebugChk(is_next=True, test=True), DebugSub(), sleep_interval=0.3, loops=5)


@pytest.mark.long
def test_rgl(tmpdir):
    argv = ["-d", tmpdir, "debug", "setup", "rgl"]
    SubwayCLI(_argv=argv)()
    argv2 = ["-d", tmpdir, "r"]
    SubwayCLI(_argv=argv2)()
    argv3 = ["-d", tmpdir, "q", "t"]
    SubwayCLI(_argv=argv3)()
    argv4 = ["-d", tmpdir, "c", "show"]
    SubwayCLI(_argv=argv4)()
    argv5 = ["-d", tmpdir, "query", "-s", "state<>checked"]
    SubwayCLI(_argv=argv5)()
