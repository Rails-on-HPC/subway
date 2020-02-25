"""
actions when sub init in cli, including mkdir, touch files and render templates in templates fold
"""
import os, sys, json, shutil

## note conf here is not from config.json, since there is no such file at the phase
## the source of the conf here should be interactive cli or specify json file from sub init -f config.json
def env_init(path, conf=None, fromfile=None, include_main=True):

    if not conf:
        conf = default_conf(path)
    mkdirs(path, conf)
    render_config(path, conf)
    render_history(path)
    if include_main:
        render_main(path, conf, fromfile)


def default_conf(path):
    conf = {}
    conf["inputs_dir"] = "inputs"
    conf["outputs_dir"] = "outputs"
    conf["check_inputs_dir"] = "cinputs"
    conf["check_outputs_dir"] = "coutputs"
    conf["work_dir"] = path  # not necessary, can serve as a double check
    conf["resource_limit"] = {}
    conf["entry_point"] = "main.py"
    return conf


def mkdirs(path, conf):
    os.mkdir(os.path.join(path, conf["inputs_dir"]))
    os.mkdir(os.path.join(path, conf["outputs_dir"]))
    os.mkdir(os.path.join(path, ".subway"))
    os.mkdir(os.path.join(path, conf["check_inputs_dir"]))
    os.mkdir(os.path.join(path, conf["check_outputs_dir"]))


def render_config(path, conf):
    with open(os.path.join(path, ".subway", "config.json"), "w") as f:
        json.dump(conf, f, indent=2)


def render_history(path):
    with open(os.path.join(path, ".subway", "history.json"), "w") as f:
        json.dump({}, f, indent=2)


def render_main(path, conf, fromfile=None):
    """
    render main.py as detailed as possible

    :param path:
    :param conf:
    :param fromfile: file path string
    :return:
    """
    if not conf:
        entry_point = "main.py"
    else:
        entry_point = conf.get("entry_point", "main.py")
    if not fromfile:
        mainpy = f"""#! {sys.executable}

import os

from subway import cons

cons.work_dir = os.path.dirname(os.path.abspath(__file__))

from subway.config import conf, history

from subway.workflow import main_once, main_rt

from subway.plugins import DebugSub, DebugChk



if __name__ == "__main__":
    main_once(DebugChk(), DebugSub())

    """
        with open(os.path.join(path, entry_point), "w") as f:
            f.writelines([mainpy])
    else:  # fromfile
        shutil.copyfile(fromfile, os.path.join(path, entry_point))
    os.chmod(os.path.join(path, entry_point), 0o700)
