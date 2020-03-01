"""
actions when sub init in cli, including mkdir, touch files and render templates in templates fold
"""

import os
import sys
import json
import shutil

## note conf here is not from config.json, since there is no such file at the phase
## the source of the conf here should be interactive cli or specify json file from sub init -f config.json
def env_init(path, conf=None, fromfile=None, include_main=True):
    """
    initialize a subway project including:
    mkdir .subway, and inputs/outputs check inputs/outputs dirs if possible
    create config.json and empty history.json within .subway
    render an example main.py

    :param path: str. absolute path for subway project dir
    :param conf: Optional[Dict], Default None, indicates a simple default config is applied.
    :param fromfile: Optional[str]. Default None, indicates a default example main.py will be rendered.
                If specified as a full path, the corresponding file will be copied into subway project
                as entry point.
    :param include_main: Optional[bool], default True. If False, main.py is not rendered.
    :return: None.
    """
    if not conf:
        conf = default_conf(path)
    mkdirs(path, conf)
    render_config(path, conf)
    render_history(path)
    if include_main:
        render_main(path, conf, fromfile)


def default_conf(path):
    """
    generate default config dict for subway project

    :param path: str. ``conf["work_dir] = path``
    :return: Dict. The default config dict.
    """
    conf = {}
    conf["inputs_dir"] = "inputs"
    conf["outputs_dir"] = "outputs"
    conf["check_inputs_dir"] = "cinputs"
    conf["check_outputs_dir"] = "coutputs"
    conf["work_dir"] = path  # not necessary, can serve as a double check
    conf["resource_limit"] = {}
    conf["entry_point"] = "main.py"
    conf["_py"] = sys.executable
    return conf


def mkdirs(path, conf):
    """
    mkdirs for "inputs_dir", "outputs_dir", "check_inputs_dir", "check_outputs_dir",
    if they are mentioned in conf dict

    :param path: str. full path for subway project.
    :param conf: Dict. config dict for subway project.
    :return: None
    """
    os.mkdir(os.path.join(path, ".subway"))
    for d in ["inputs_dir", "outputs_dir", "check_inputs_dir", "check_outputs_dir"]:
        _mkdir(path, conf, d)


def _mkdir(path, conf, key):
    if conf.get(key):
        os.mkdir(os.path.join(path, conf.get(key)))


def render_config(path, conf):
    """
    generate config.json based on conf dict within .subway dir

    :param path: str. full path for subway project.
    :param conf: Dict. config dict for subway project.
    :return: None
    """
    with open(os.path.join(path, ".subway", "config.json"), "w") as f:
        json.dump(conf, f, indent=2)


def render_history(path):
    """
    generate empty history.json with only ``{}`` within .subway dir

    :param path: str. full path for subway project.
    :return: None
    """
    with open(os.path.join(path, ".subway", "history.json"), "w") as f:
        json.dump({}, f, indent=2)


def render_main(path, conf, fromfile=None):
    """
    render main.py as detailed as possible and make its permission 700 (executable).

    :param path: str. full path for subway project.
    :param conf: Dict. config dict for subway project.
    :param fromfile: Optional[str]. Default None, indicates a default example main.py will be rendered.
                If specified as a full path, the corresponding file will be copied into subway project
                as entry point.
    :return: None.
    """
    if not conf:
        entry_point = "main.py"
    else:
        entry_point = conf.get("entry_point", "main.py")
    if not fromfile:
        mainpy = """#! {_py}

import os

from subway import cons

cons.work_dir = os.path.dirname(os.path.abspath(__file__))

from subway.config import conf, history

from subway.workflow import main_once, main_rt

from subway.plugins import DebugSub, DebugChk



if __name__ == "__main__":
    main_once(DebugChk(), DebugSub())

    """.format(
            _py=sys.executable
        )

        with open(os.path.join(path, entry_point), "w") as f:
            f.writelines([mainpy])
    else:  # fromfile
        shutil.copyfile(fromfile, os.path.join(path, entry_point))
    os.chmod(os.path.join(path, entry_point), 0o700)
