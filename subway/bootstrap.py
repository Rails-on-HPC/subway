"""
actions when sub init in cli, including mkdir, touch files and render templates in templates fold
"""
import os, sys, json

## note conf here is not from config.json, since there is no such file at the phase
## the source of the conf here should be interactive cli or specify json file from sub init -f config.json
def env_init(path, conf=None):

    if not conf:
        conf = default_conf(path)
    mkdirs(path, conf)
    render_config(path, conf)
    render_history(path)
    render_main(path, conf)


def default_conf(path):
    conf = {}
    conf["inputs_dir"] = "inputs"
    conf["outputs_dir"] = "outputs"
    # conf["main_prefix"] = "main"
    # conf["check_prefix"] = "check"
    conf["work_dir"] = path
    conf["resource_limit"] = {}
    conf["entry_point"] = "main.py"
    return conf


def mkdirs(path, conf):
    os.mkdir(os.path.join(path, conf["inputs_dir"]))
    os.mkdir(os.path.join(path, conf["outputs_dir"]))
    os.mkdir(os.path.join(path, ".subway"))


def render_config(path, conf):
    with open(os.path.join(path, ".subway", "config.json"), "w") as f:
        json.dump(conf, f, indent=2)


def render_history(path):
    with open(os.path.join(path, ".subway", "history.json"), "w") as f:
        json.dump({}, f, indent=2)


def render_main(path, conf):
    """
    render main.py as detailed as possible

    :param path:
    :param conf:
    :return:
    """
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

    with open(os.path.join(path, "main.py"), "w") as f:
        f.writelines([mainpy])
    os.chmod(os.path.join(path, "main.py"), 0o700)
