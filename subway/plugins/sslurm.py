"""
More specific slurm plugin for checker and submitter,
Extra S is for specific or single (indicates that check job not go through slurm)

"""
import os
from abc import abstractmethod
from uuid import uuid4
from functools import partial

from ..config import conf
from ..components import SlurmJob, SlurmTask
from ..utils import replace_wildcard
from .slurm import SlurmSub, SlurmChk


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

    def __init__(self, params=None, fromconf=True, **kwargs):
        self.fromconf = fromconf
        super().__init__(params, **kwargs)

    @abstractmethod
    def _render_input(self, jobid, param):
        """
        generate input files based on jobid and param

        :param jobid:
        :param param:
        :return:
        """
        pass

    def _render_sbatch(self, jobid, param=None):
        SlurmTask(
            sbatch_path=os.path.join(conf["inputs_abs_dir"], jobid + ".sh"),
            sbatch_commands=self._render_commands(jobid, param),
            sbatch_options=self._render_options(jobid, param),
        )

    @abstractmethod
    def _render_commands(self, jobid, param=None):
        return [""]

    def _replace_func(self, jobid, checkid, char):
        # a second thought: why not unify with {} as format
        if char == "j":
            return jobid
        elif char == "c":
            return checkid
        return ""

    def _substitue_opts(self, opts, jobid, checkid=""):
        """

        :param opts: lits of strings
        :return:
        """
        _preplace = partial(self._replace_func, jobid, checkid)
        for i, opt in enumerate(opts):
            opts[i] = replace_wildcard(_preplace, opt)
        return opts

    def _render_options(self, jobid, param=None):
        if not self.fromconf:
            opts = []
        ## read options from conf
        else:
            opts = conf["slurm_options"].copy()
        opts.append("--job-name %s" % jobid)
        opts = opts + self._render_options_append(jobid, param)
        return self._substitue_opts(opts, jobid)

    def _render_options_append(self, jobid, param=None):
        return []

    def _render_resource(self, jobid, param=None):
        return {}

    def _render_check(self, params):
        r = []
        for param in params:
            jobid = self._render_newid()
            self._render_input(jobid, param)
            self._render_sbatch(jobid, param)
            r.append((jobid, self._render_resource(jobid, param)))
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
