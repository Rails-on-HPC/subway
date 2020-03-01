"""
Provide DSlurmSub and DSlurmChk class, with consideration on check scripts into slurm system
"""

import os
from abc import abstractmethod

from ..config import conf, history
from ..components import SlurmJob, SlurmTask
from .sslurm import SSlurmSub, SSlurmChk


class DSlurmSub(SSlurmSub):
    def submit_aborted(self, jobid):
        sbatch_path = os.path.join(
            conf["work_dir"], conf["check_inputs_dir"], history[jobid]["assoc"] + ".sh"
        )
        t = SlurmTask(sbatch_path=sbatch_path)
        t.submit()

    def submit_finished(self, jobid):
        self.submit_aborted(jobid)


# TODO: sslurm is expected to merge into dslurm totally
class DSlurmChk(SSlurmChk):
    """
    For subclass to be usable, one need to define methods including:
    _render_input, _render_commands, _render_options_append (if needed)
    _render_resource (default {}, if needed), _render_newid (default uuid1, if needed)
    and specifically check_checking_main
    """

    def _render_check(self, params, jobid=None, _type="main"):
        if _type == "main":
            r = []
            for param in params:
                jobid = self._render_newid()
                self._render_input(jobid=jobid, param=param)
                self._render_sbatch(jobid=jobid, param=param)
                r.append((jobid, self._render_resource(jobid=jobid, param=param)))
            return r
        elif _type == "check":
            if params:
                assert len(params) == 1
                param = params[0]
                checkid = self._render_newid()
                self._render_input(
                    jobid=jobid, checkid=checkid, param=param, prefix="check_"
                )
                self._render_sbatch(
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

    def check_finished(self, jobid):  # should generate check input and check sbatch
        params = self.check_finished_main(jobid)
        return self._render_check(params=params, jobid=jobid, _type="check")

    @abstractmethod
    def check_finished_main(self, jobid):
        """

        :param jobid: str.
        :return: List[Tuple[str, Dict[str, Any]]]. The length of the list must be 0 or 1.
                ``[(checkid, check_resource)]``
        """
        return []
