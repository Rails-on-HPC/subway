#! /usr/bin/python3

import os

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from subway import cons

cons.work_dir = os.path.dirname(os.path.abspath(__file__))

from subway.workflow import main_once, main_rt

from subway.examples import RgDSub, RgDChk


if __name__ == "__main__":
    main_rt(
        RgDChk(_py="python", params=[[3, 0.5], [2, 0.4]]), RgDSub(), sleep_interval=3
    )
