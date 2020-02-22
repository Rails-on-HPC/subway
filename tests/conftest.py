import pytest

from shutil import copyfile
import sys
import os

work_path = os.path.dirname(__file__)


def backup_history():
    copyfile(
        os.path.join(work_path, ".subway", "history.json"),
        os.path.join(work_path, ".subway", "history.json.backup"),
    )


def reset_history():
    copyfile(
        os.path.join(work_path, ".subway", "history.json.backup"),
        os.path.join(work_path, ".subway", "history.json"),
    )


@pytest.fixture(scope="function")
def history():
    """
    This function should be implicitly called for each test, since the db is closed each time
    """
    backup_history()
    yield
    reset_history()
