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
        `DIY: depends.`
        If you try to customize this method,
        include ``super()._render_input`` is strongly recommended.
        Generate input files based on jobid and param.
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
        """
        `DIY: depends`
        Default impl adds param and job_count=1 to resource dict.
        Even if you customize this method, we recommend you add ``super()._render_resource`` in your method.

        :param jobid: str.
        :param checkid: Optional[str], default "".
        :param param: Optional[Union[List, Dict]].
        :param prefix: Optiona[str], default "".
        :return: Dict, resource dict.
        """
        res = {}
        res["job_count"] = 1
        res["param"] = param
        return res

    def _render_newid(self):
        """
        `DIY: depends.`
        generate new job id.
        In most cases, the default implementation by ``uuid4`` is good enough.

        :return: str. jobid
        """
        return str(uuid4())

    def _render_check(self, params, jobid=None, _type="main", prefix=""):
        """
        `DIY: not recommend.`
        main entrance to rendered mixin, shall be called in checker class, check_* methods.

        :param params: List[Union[Dict, List]].
        :param jobid: Optional[str]. Default None for new job render, and jobid is give for assoc job render.
        :param _type: Optional[str]. Default "main". Current options also include "check".
        :param prefix: Optional[str]. Default ``""``.
        :return: List[Tuple[str, Dict[str, Any]]]. List of pairs with jobid and resource dict for new jobs or assoc job.
        """
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
