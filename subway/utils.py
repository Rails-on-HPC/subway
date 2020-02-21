import json
from datetime import datetime


def now_ts():
    return datetime.now().timestamp()


def load_json(conf_file):
    with open(conf_file, "r") as fp:
        conf_dict = json.load(fp)
    return conf_dict
