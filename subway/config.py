import os
import json
from .cons import work_dir
from .utils import load_json


def update_history():
    with open(conf["history_path"], "w") as f:
        json.dump(history, f, indent=2)


def update_config():
    with open(conf["config_path"], "w") as f:
        json.dump(conf, f, indent=2)


config_path = os.path.join(work_dir, ".subway", "config.json")
conf = load_json(config_path)

conf["config_path"] = config_path
conf["history_path"] = os.path.join(work_dir, ".subway", "history.json")
history = load_json(conf["history_path"])

conf["inputs_abs_dir"] = os.path.join(conf["work_dir"], conf["inputs_dir"])
conf["outputs_abs_dir"] = os.path.join(conf["work_dir"], conf["outputs_dir"])
