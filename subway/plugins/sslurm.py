"""
More specific slurm plugin for checker and submitter,
Extra S is for specific or single (indicates that check job not go through slurm)

"""
import os
from abc import abstractmethod
from uuid import uuid1

from ..config import conf
from ..components import SlurmJob, SlurmTask
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
    _render_input, _render_commands, _render_options (append to super() is recommended)
    _render_resource (default {}, if needed), _render_newid (default uuid1, if needed)
    and specifically check_checking_main
    """

    def __init__(self, params=None, **kwargs):
        self.kws = kwargs
        super().__init__(params)

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

    def _render_options(self, jobid, param=None):
        return ["-N 1", "--job-name %s" % jobid]

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
        return str(uuid1())

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
