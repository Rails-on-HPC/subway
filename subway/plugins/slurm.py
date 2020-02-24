from ..framework import PlainChk, PlainSub
from subway.components import SlurmJob
from ..config import history
from ..utils import now_ts
from ..components.slurmoo import slurm_abnormal_states


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
        if sjob.jobinfo["State"] in slurm_abnormal_states:
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
