"""
smarter file rendered can be utilized in _render_input of SSlurmChk
"""
import json

from ..utils import simple_template_render, flatten_dict

# TODO: provide smart unified API to generate files with given python data structure
# .xml .json .yaml/toml .txt .csv
def generate_file(
    data, output_path, output_format=None, output_config=None, output_template=None
):
    if not output_config:
        output_config = {}

    # firstly transform everything to standard intermediate state as a dict json like
    data = jsonify(data, _outer_most=True)
    if output_template:
        simple_template_render(output_template, output_path, flatten_dict(data))
    if output_format == "json":
        with open(output_path, "w") as f:
            json.dump(data, f)
            return


def jsonify(data, _outer_most=False, _outer=True, func=None):
    if data is None:
        return None
    elif isinstance(data, dict):  # auto support collections.OrderedDict
        for k, v in data.items():
            data[k] = jsonify(v, _outer=False, func=func)
    elif isinstance(data, list) or isinstance(data, set) or isinstance(data, tuple):
        data = list(data)
        for i, d in enumerate(data):
            data[i] = jsonify(d, _outer=True, func=func)
        if _outer:
            data = {"list": data}
    elif isinstance(data, str) or isinstance(data, int) or isinstance(data, float):
        if _outer_most:
            data = {type(data).__name__: data}
    else:
        if func:
            data = func(data)
        else:
            raise ValueError("Unsupported data type %s to jsonify" % type(data))

    return data
