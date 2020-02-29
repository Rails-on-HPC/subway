"""
More specific slurm plugin for checker and submitter,
Extra S is for specific or single (indicates that check job not go through slurm)

"""
import os
from abc import abstractmethod
from uuid import uuid4
from functools import partial

from ..config import conf, history
from ..components import SlurmJob, SlurmTask
from ..utils import flatten_dict
from .slurm import SlurmSub, SlurmChk
from ..components.genfiles import generate_file


class SSlurmSub(SlurmSub):
    def submit_pending(self, jobid):
        sbatch_path = os.path.join(conf["inputs_abs_dir"], jobid + ".sh")
        t = SlurmTask(sbatch_path=sbatch_path)
        t.submit()
        # print(t.jobid())


class SSlurmChk(SlurmChk):
    """
    For subclass to be usable, one need to define methods including:
    _render_input, _render_commands, _render_options_append (if needed)
    _render_resource (default {}, if needed), _render_newid (default uuid1, if needed)
    and specifically check_checking_main
    """

    def __init__(self, params=None, _from="conf", **kwargs):
        """

        :param params:
        :param _from: str. conf, template.
        :param kwargs:
        """
        self._from = _from
        super().__init__(params, **kwargs)

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

    def _render_sbatch(self, jobid, checkid="", param=None, prefix=""):
        if not prefix:
            _sbatch_path = os.path.join(conf["inputs_abs_dir"], jobid + ".sh")
        elif prefix == "check_":
            _sbatch_path = os.path.join(
                conf[prefix + "inputs_abs_dir"], checkid + ".sh"
            )
        if self._from == "conf":
            SlurmTask(
                sbatch_path=_sbatch_path,
                sbatch_commands=self._render_commands(
                    jobid=jobid, checkid=checkid, param=param, prefix=prefix
                ),
            )

        elif self._from == "template":
            _sbatch_template = os.path.join(
                conf["work_dir"], conf[prefix + "slurm_template"]
            )
            info_dict = flatten_dict(
                {"conf": conf, "param": param, "jobid": jobid, "checkid": checkid,}
            )
            generate_file(
                info_dict, output_path=_sbatch_path, output_template=_sbatch_template
            )
            SlurmTask(sbatch_path=_sbatch_path)

        else:
            raise ValueError("_from must be conf or template")

    def _render_commands(self, jobid, checkid="", param=None, prefix=""):
        commands = conf.get(prefix + "slurm_commands", []).copy()
        opts = conf.get(prefix + "slurm_options", []).copy()
        opts = ["#SBATCH " + opt for opt in opts]
        if checkid:
            _id = checkid
        else:
            _id = jobid
        opts.append("#SBATCH --job-name %s" % _id)
        commands = opts + commands
        return self._substitue_opts(
            opts=commands, jobid=jobid, checkid=checkid, param=param
        )

    # def _replace_func(self, jobid, checkid, char):
    #     # a second thought: why not unify with {} as format
    #     if char == "j":
    #         return jobid
    #     elif char == "J":
    #         return checkid
    #     elif char == "i":
    #         return os.path.join(conf.get("inputs_abs_dir", ""), jobid)
    #     elif char == "o":
    #         return os.path.join(conf.get("outputs_abs_dir", ""), jobid)
    #     elif char == "I":
    #         return os.path.join(conf.get("check_inputs_abs_dir", ""), checkid)
    #     elif char == "O":
    #         return os.path.join(conf.get("check_outputs_abs_dir", ""), checkid)
    #     elif char == "e":
    #         return os.path.join(conf["work_dir"], conf.get("executable", ""))
    #     elif char == "E":
    #         return os.path.join(conf["work_dir"], conf.get("check_executable", ""))
    #     elif char == "v":
    #         return conf.get("executable_version", "")
    #     elif char == "V":
    #         return conf.get("check_executable_version", "")
    #     elif char == "w":
    #         return conf.get("work_dir", "")
    #     return ""

    def _substitue_opts(self, opts, jobid, checkid="", param=None):
        """

        :param opts: lits of strings
        :return:
        """
        info_dict = flatten_dict(
            {"conf": conf, "param": param, "jobid": jobid, "checkid": checkid,}
        )
        # print(info_dict)
        for i, opt in enumerate(opts):
            opts[i] = opt.format(**info_dict)  # sep="." doesn't work here
        # f-sring is way better for {a[b]} support naturally, but considering py3.5 here...
        return opts

    def _render_resource(self, jobid, checkid="", param=None):
        res = {}
        res["job_count"] = 1
        return res

    def _render_check(self, params):
        r = []
        for param in params:
            jobid = self._render_newid()
            self._render_input(jobid=jobid, param=param)
            self._render_sbatch(jobid=jobid, param=param)
            r.append((jobid, self._render_resource(jobid=jobid, param=param)))
        return r

    def _render_newid(self):
        return str(uuid4())

    def check_kickstart(self):
        return self._render_check(self.params)

    @abstractmethod
    def check_checking_main(self, jobid):
        """

        :param jobid:
        :return: list of param for new jobs
        """
        return []

    def check_checking(self, jobid):
        params = self.check_checking_main(jobid)
        return self._render_check(params)
