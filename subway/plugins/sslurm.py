"""
More specific slurm plugin for checker and submitter,
Extra S is for specific or single (indicates that check job not go through slurm)

"""

import os
from abc import abstractmethod

from .renderer import PlainRenderer
from ..config import conf, history
from ..components import SlurmJob, SlurmTask
from ..utils import flatten_dict
from .slurm import SlurmSub, SlurmChk
from ..components.genfiles import generate_file


class SSlurmSub(SlurmSub):
    """
    Slurm checker with SS scheme.
    """

    def submit_pending(self, jobid):
        """
        `DIY: not recommend.`
        Default impl is submitting jobs via sbatch, it is in general good enough.

        :param jobid: str.
        :return: None.
        """
        sbatch_path = os.path.join(conf["inputs_abs_dir"], jobid + ".sh")
        t = SlurmTask(sbatch_path=sbatch_path)
        t.submit()
        # print(t.jobid())


class SSlurmChk(SlurmChk, PlainRenderer):
    """
    Slurm submitter with SS scheme and PlainRender mixin.
    """

    def __init__(self, params=None, _from="conf", **kwargs):
        """

        :param params: List[Dict, List].
        :param _from: str. conf, template.
        :param kwargs:
        """
        self._from = _from
        super().__init__(params, **kwargs)

    def _render_input(self, jobid, checkid="", param=None, prefix=""):
        """
        `DIY: depends`.
        Generate input files based on jobid and param.
        The default impl can render param to input.template and similar to sbatch.template.
        But this is not general enough for all user case,
        the user can simply rewrite this method.

        :param jobid: str.
        :param param: Unoin[Dict, List, Tuple].
        :return: None.
        """
        super()._render_input(jobid=jobid, checkid=checkid, param=param, prefix=prefix)
        self._render_sbatch(jobid=jobid, checkid=checkid, param=param, prefix=prefix)

    def _render_sbatch(self, jobid, checkid="", param=None, prefix=""):
        """
        render sbatch script from template file or config.json. called from ``_render_input``

        :param jobid: str.
        :param checkid: Optiona[str].
        :param param: Union[List, Dict].
        :param prefix: Optional[str].
        :return: None.
        """
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

    def _substitue_opts(self, opts, jobid, checkid="", param=None):
        """
        inner function to render slurm commands from templates.

        :param opts: List[str].
        :return: List[str].
        """
        info_dict = flatten_dict(
            {"conf": conf, "param": param, "jobid": jobid, "checkid": checkid,}
        )
        # print(info_dict)
        for i, opt in enumerate(opts):
            opts[i] = opt.format(**info_dict)  # sep="." doesn't work here
        # f-sring is way better for {a[b]} support naturally, but considering py3.5 here...
        return opts

    def check_kickstart(self):
        """
        Directly call ``_render_check(self.params)``.

        :return:
        """
        return self._render_check(self.params)

    @abstractmethod
    def check_checking_main(self, jobid):
        """
        `DIY: must`.
        Given jobid of job in state of checking, return params list for new jobs to be run.

        :param jobid: str.
        :return: List[Tuple[str, Dict[str, Any]]].
        """
        return []

    def check_checking(self, jobid):
        """
        Call ``check_checking_main`` to get params and then call ``_render_check``.

        :param jobid: str.
        :return:
        """
        params = self.check_checking_main(jobid)
        return self._render_check(params)
