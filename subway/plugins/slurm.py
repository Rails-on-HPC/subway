from ..framework import PlainChk, PlainSub
from .slurmoo import SlurmJob
from ..config import history
from ..utils import now_ts


class SlurmChk(PlainChk):
    def is_finished(self, jobid):
        """
        This utils is to further distinguish those tasks that has incomplete outfile while still running

        :param jobid: relativepath
        :return:
        """
        sjob = SlurmJob(jobname=jobid)
        ifn = sjob.jobinfo["State"] == "COMPLETED"
        if ifn:
            history[jobid]["beginning_real_ts"] = sjob.jobinfo["Start_ts"]
            return True
        return False

    def is_aborted(self, jobid):
        sjob = SlurmJob(jobname=jobid)
        if sjob.jobinfo["State"] in [
            "BOOT_FAIL",
            "CANCELLED",
            "DEADLINE",
            "FAILED",
            "NODE_FAIL",
            "OUT_OF_MEMORY",
            "PREEMPTED",
            "STOPPED",
            "TIMEOUT",
        ]:
            history[jobid]["reason"] = sjob.jobinfo["State"]
            return True
        return False

    def is_checked(self, jobid):
        jid = getattr(history[jobid], "assoc", "")  # jobname for associate check job
        if jid:
            sjob = SlurmJob(jobname=jid)
            return sjob.jobinfo["State"] == "COMPLETED"
        # no independent checking job
        return True

    def is_frustrated(self, jobid):
        return False

    def is_resolved(self, jobid):
        return True

    def is_failed(self, jobid):
        return False

    def finishing_time(self, jobid):
        """


        :param jobid:
        :return:
        """
        sjob = SlurmJob(jobname=jobid)

        return sjob.jobinfo["End_ts"]

    def ending_time(self, jobid):
        """
        ending_time is reponsible for 4 states: checked resolved frustrated failed

        :param jobid:
        :return:
        """
        jid = getattr(history[jobid], "assoc", "")  # jobname for associate check job
        if jid:
            sjob = SlurmJob(jobname=jid)
            return sjob.jobinfo["End_ts"]
        return now_ts()


class SlurmSub(PlainSub):
    pass
