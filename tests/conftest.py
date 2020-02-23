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


def pytest_addoption(parser):
    parser.addoption('--slurm', action='store_true',
                     default=False, help="enable longrundecorated tests")


def pytest_collection_modifyitems(config, items):
    """
    if -all not specified, the test functions marked by slurm is omitted
    """
    if config.getoption("--slurm"):
        return
    skip_slurm = pytest.mark.skip(reason="need --all option to run")
    for item in items:
        if "slurm" in item.keywords:
            item.add_marker(skip_slurm)


@pytest.fixture(scope="function")
def history():
    """
    This function should be implicitly called for each test, since the db is closed each time
    """
    backup_history()
    yield
    reset_history()
