"""
Provide DSlurmSub and DSlurmChk class, with consideration on check scripts into slurm system
"""

import os
from abc import abstractmethod

from ..config import conf, history
from ..components import SlurmJob, SlurmTask
from .sslurm import SSlurmSub, SSlurmChk


class DSlurmSub(SSlurmSub):
    """
    Slurm submitter for DS scheme.
    """

    def submit_aborted(self, jobid):
        sbatch_path = os.path.join(
            conf["work_dir"], conf["check_inputs_dir"], history[jobid]["assoc"] + ".sh"
        )
        t = SlurmTask(sbatch_path=sbatch_path)
        t.submit()

    def submit_finished(self, jobid):
        self.submit_aborted(jobid)


class DSlurmChk(SSlurmChk):
    """
    Slurm checker for DS scheme.
    """

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
