"""
Mixin for checker for higher level render and workflow
"""

import os
from uuid import uuid4

from ..config import history, conf
from ..utils import flatten_dict
from ..components.genfiles import generate_file


class PlainRenderer:
    def _render_input(self, jobid, checkid="", param=None, prefix=""):
        """
        generate input files based on jobid and param.
        The default impl can render param to input.template.
        But this is not general enough for all user case,
        the user can simply rewrite this method.

        :param jobid: str.
        :param param: Unoin[Dict, List, Tuple].
        :return: None.
        """
        info_dict = flatten_dict(
            {"conf": conf, "param": param, "jobid": jobid, "checkid": checkid,}
        )
        if not prefix:
            if conf.get("input_template"):
                generate_file(
                    data=flatten_dict(info_dict),
                    output_path=os.path.join(conf["inputs_abs_dir"], jobid),
                    output_template=os.path.join(
                        conf["work_dir"], conf["input_template"]
                    ),
                )
        elif prefix == "check_":
            if conf.get(prefix + "input_template"):
                generate_file(
                    data=flatten_dict(info_dict),
                    output_path=os.path.join(conf[prefix + "inputs_abs_dir"], checkid),
                    output_template=os.path.join(
                        conf["work_dir"], conf[prefix + "input_template"]
                    ),
                )

    def _render_resource(self, jobid, checkid="", param=None, prefix=""):
        res = {}
        res["job_count"] = 1
        return res

    def _render_newid(self):
        """
        generate new job id

        :return: str. jobid
        """
        return str(uuid4())

    def _render_check(self, params, jobid=None, _type="main", prefix=""):
        if _type == "main":
            r = []
            for param in params:
                jobid = self._render_newid()
                self._render_input(jobid=jobid, param=param, checkid="", prefix=prefix)
                r.append((jobid, self._render_resource(jobid=jobid, param=param)))
            return r
        elif _type == "check":
            if params:
                assert len(params) == 1  # check task is one-to-one with main task
                param = params[0]
                checkid = self._render_newid()
                self._render_input(
                    jobid=jobid, checkid=checkid, param=param, prefix="check_"
                )
                return [
                    (
                        checkid,
                        self._render_resource(
                            jobid=jobid, checkid=checkid, param=param
                        ),
                    )
                ]
