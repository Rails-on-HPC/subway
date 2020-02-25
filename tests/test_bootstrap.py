import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from subway.bootstrap import env_init


def test_env_init(tmpdir):
    env_init(tmpdir)
