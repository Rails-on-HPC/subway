"""
import config from ``config.json``
"""

import os
import json
from .cons import work_dir
from .utils import load_json


config_path = os.path.join(work_dir, ".subway", "config.json")
conf = load_json(config_path)

assert conf.get("work_dir", work_dir) == work_dir

conf["work_dir"] = work_dir
conf["config_path"] = config_path
conf["history_path"] = os.path.join(work_dir, ".subway", "history.json")
history = load_json(conf["history_path"])


def _conf_abs_dir(prefix):
    relkey = prefix + "_dir"
    abskey = prefix + "_abs_dir"
    if conf.get(relkey):
        conf[abskey] = os.path.join(conf["work_dir"], conf[relkey])


for prefix in ["inputs", "outputs", "check_inputs", "check_outputs"]:
    _conf_abs_dir(prefix)


def update_history():
    """
    write ``history`` in memory back to ``history.json``.

    :return: None.
    """
    with open(conf["history_path"], "w") as f:
        json.dump(history, f, indent=2)


def update_conf():
    """
    write ``conf`` in memory back to ``config.json``.

    :return: None.
    """
    with open(conf["config_path"], "w") as f:
        json.dump(conf, f, indent=2)
