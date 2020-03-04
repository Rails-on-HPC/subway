"""
basic slurm plugin with some improvement on bool and time relevant methods.
"""

from ..framework import PlainChk, PlainSub
from ..components import SlurmJob
from ..config import history
from ..utils import now_ts
from ..components.slurmoo import slurm_abnormal_states


class SlurmChk(PlainChk):
    """
    Low level checker for slurm with only some ``is_*`` and ``*_time`` methods redefined.
    General users are recommended to use :class:`subway.plugins.sslurm.SSlurmChk` instead.
    """

    def is_finished(self, jobid):
        """
        Determine job states based on sacct of main job.

        :param jobid: str.
        :return: bool.
        """
        sjob = SlurmJob(jobname=jobid)
        ifn = sjob.jobinfo["State"] == "COMPLETED"
        if ifn:
            history[jobid]["beginning_real_ts"] = sjob.jobinfo["Start_ts"]
            return True
        return False

    def is_aborted(self, jobid):
        """
        Determine job states based on sacct of main job.

        :param jobid: str.
        :return: bool.
        """
        sjob = SlurmJob(jobname=jobid)
        if sjob.jobinfo["State"] in slurm_abnormal_states:
            history[jobid]["reason"] = sjob.jobinfo["State"]
            return True
        return False

    def is_checked(self, jobid):
        """
        For DS scheme, judge based on slurm job state of check job.
        For SS scheme, always return True.

        :param jobid: str.
        :return: bool.
        """
        jid = getattr(history[jobid], "assoc", "")  # jobname for associate check job
        if jid:
            sjob = SlurmJob(jobname=jid)
            return sjob.jobinfo["State"] == "COMPLETED"
        # no independent checking job
        return True

    def is_frustrated(self, jobid):
        """
        For DS scheme, judge based on slurm job state of check job.
        For SS scheme, always return False.

        :param jobid: str.
        :return: bool.
        """
        jid = getattr(history[jobid], "assoc", "")  # jobname for associate check job
        if jid:
            sjob = SlurmJob(jobname=jid)
            if sjob.jobinfo["State"] in slurm_abnormal_states:
                history[jobid]["check_reason"] = sjob.jobinfo["State"]
                return True
            return False
        # no independent checking job, always checked instead of frustrated
        return False

    def is_resolved(self, jobid):
        self.is_checked(jobid)

    def is_failed(self, jobid):
        self.is_frustrated(jobid)

    def finishing_time(self, jobid):
        """
        get finish time from sacct.

        :param jobid: str.
        :return: float, timestamp.
        """
        sjob = SlurmJob(jobname=jobid)

        return sjob.jobinfo["End_ts"]

    def ending_time(self, jobid):
        """
        For DS scheme, return finish time of check slurm job.
        For SS scheme, simply return now.

        :param jobid: str.
        :return: float, timestamp.
        """
        jid = getattr(history[jobid], "assoc", "")  # jobname for associate check job
        if jid:
            sjob = SlurmJob(jobname=jid)
            return sjob.jobinfo["End_ts"]
        return now_ts()


class SlurmSub(PlainSub):
    """
    Exactly the same as :class:`subway.framework.PlainSub`.
    """

    pass
