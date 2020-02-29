import pytest

from shutil import copyfile, rmtree
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
    parser.addoption(
        "--slurm", action="store_true", default=False, help="enable slurm tests",
    )
    parser.addoption(
        "--long", action="store_true", default=False, help="enable long tests",
    )


def pytest_collection_modifyitems(config, items):
    """
    if --slurm not specified, the test functions marked by slurm is omitted
    """
    if config.getoption("--slurm"):
        return  ## run all
    skip_slurm = pytest.mark.skip(reason="need --slurm option to run")
    for item in items:
        if "slurm" in item.keywords:
            item.add_marker(skip_slurm)
    if config.getoption("--long"):
        return
    skip_long = pytest.mark.skip(reason="need --long option to run")
    for item in items:
        if "long" in item.keywords:
            item.add_marker(skip_long)
    # no --long no --slurm or only --long


# it is weird only `pytest tests --slurm` works while `pytest --slurm` incurs error
# though `pytest` works fine


@pytest.fixture(scope="function")
def history():
    """
    This function should be implicitly called for each test, since the db is closed each time
    """
    backup_history()
    yield
    reset_history()


@pytest.fixture(scope="function")
def tmpdir():
    tmp_path = os.path.join(work_path, "test_tmp")
    os.mkdir(tmp_path)
    yield tmp_path
    rmtree(tmp_path)


@pytest.fixture(scope="function")
def clean_slurm():
    yield
    cwd = os.getcwd()
    sout = [
        f
        for f in os.listdir(cwd)
        if os.path.isfile(os.path.join(cwd, f))
        and f.startswith("slurm-")
        and f.endswith(".out")
    ]
    for f in sout:
        os.remove(os.path.join(cwd, f))


@pytest.fixture(scope="function")
def template(request):
    _in, _out = request.param
    with open(os.path.join(work_path, "test.template"), "w") as f:
        f.writelines([_in])
    os.system("echo writing.....")
    yield
    with open(os.path.join(work_path, "test.out"), "r") as f:
        out = f.read()
    os.remove(os.path.join(work_path, "test.template"))
    os.remove(os.path.join(work_path, "test.out"))
    assert out == _out
