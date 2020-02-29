import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from subway.cli import SubwayCLI


@pytest.mark.slurm
def test_rgd_template(tmpdir, clean_slurm):
    argv = ["-d", tmpdir, "debug", "setup", "rgd"]
    SubwayCLI(_argv=argv)()
    argv2 = ["-d", tmpdir, "r"]
    SubwayCLI(_argv=argv2)()
    argv3 = ["-d", tmpdir, "q", "t"]
    SubwayCLI(_argv=argv3)()
    argv4 = ["-d", tmpdir, "c", "show"]
    SubwayCLI(_argv=argv4)()
    argv5 = ["-d", tmpdir, "query", "-s", "state<>checked"]
    SubwayCLI(_argv=argv5)()


@pytest.mark.slurm
def test_rgd_conf(tmpdir, clean_slurm):
    argv = ["-d", tmpdir, "debug", "setup", "rgd", "-f", "conf"]
    SubwayCLI(_argv=argv)()
    argv2 = ["-d", tmpdir, "r"]
    SubwayCLI(_argv=argv2)()
    argv3 = ["-d", tmpdir, "q", "t"]
    SubwayCLI(_argv=argv3)()
    argv4 = ["-d", tmpdir, "c", "show"]
    SubwayCLI(_argv=argv4)()
    argv5 = ["-d", tmpdir, "query", "-s", "state<>checked"]
    SubwayCLI(_argv=argv5)()


@pytest.mark.slurm
def test_rgs_template(tmpdir, clean_slurm):
    argv = ["-d", tmpdir, "debug", "setup", "rgs"]
    SubwayCLI(_argv=argv)()
    argv2 = ["-d", tmpdir, "r"]
    SubwayCLI(_argv=argv2)()
    argv3 = ["-d", tmpdir, "q", "t"]
    SubwayCLI(_argv=argv3)()
    argv4 = ["-d", tmpdir, "c", "show"]
    SubwayCLI(_argv=argv4)()
    argv5 = ["-d", tmpdir, "query", "-s", "state<>checked"]
    SubwayCLI(_argv=argv5)()


@pytest.mark.slurm
def test_rgs_conf(tmpdir, clean_slurm):
    argv = ["-d", tmpdir, "debug", "setup", "rgs", "-f", "conf"]
    SubwayCLI(_argv=argv)()
    argv2 = ["-d", tmpdir, "r"]
    SubwayCLI(_argv=argv2)()
    argv3 = ["-d", tmpdir, "q", "t"]
    SubwayCLI(_argv=argv3)()
    argv4 = ["-d", tmpdir, "c", "show"]
    SubwayCLI(_argv=argv4)()
    argv5 = ["-d", tmpdir, "query", "-s", "state<>checked"]
    SubwayCLI(_argv=argv5)()
