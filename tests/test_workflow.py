import sys
import os

work_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(work_path))

from subway import cons

cons.work_dir = work_path
from subway.plugins import DebugSub, DebugChk
from subway.workflow import main_once, main_rt


def test_main_once(history):
    main_once(DebugChk(True), DebugSub())
    main_once(DebugChk(), DebugSub())
    main_once(DebugChk(), DebugSub())


def test_main_rt(history):
    main_rt(DebugChk(True), DebugSub(), sleep_interval=0.3, loops=5)
