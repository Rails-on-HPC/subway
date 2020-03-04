"""
puerly linux nohup interface for job submission
"""

import os
import shlex
import subprocess
from abc import abstractmethod

from .renderer import PlainRenderer
from ..framework import PlainSub, PlainChk
from ..config import history, conf
from ..exceptions import SubwayException
from ..utils import flatten_dict


class NHException(SubwayException):
    pass


class NHSChk(PlainChk, PlainRenderer):
    """
    checker using non-blocking subprocess.Popen
    """

    def check_kickstart(self):
        return self._render_check(self.params)

    @abstractmethod
    def check_checking_main(self, jobid):
        """
        `DIY:MUST`.

        :param jobid: str.
        :return: List[Union[Dict, List]]. list of param for new jobs
        """
        return []

    def check_checking(self, jobid):
        params = self.check_checking_main(jobid)
        return self._render_check(params)

    def is_finished(self, jobid):
        """
        Using Popen.poll() to detect whether job is finished.
        For restarted subway run which lose popen object in the memory, use ps pid instead.

        :param jobid: str.
        :return:
        """
        popen = history[jobid]["popen"]
        if isinstance(popen, subprocess.Popen):
            if popen.poll() is None:
                return False
            else:
                return True
        if isinstance(popen, int):
            r = subprocess.run(["ps", str(popen)], stdout=subprocess.PIPE)
            psr = len([s for s in r.stdout.decode("utf-8").split("\n") if s.strip()])
            if psr == 2:
                return False
            elif psr == 1:
                return True
        return False

    def is_aborted(self, jobid):
        """
        Default to False.
        One can hack history in check_finished and
        manually change the state to aborted.

        :param jobid: str.
        :return: bool.
        """
        return False

    def is_checked(self, jobid):
        # no independent checking job
        return True

    def is_frustrated(self, jobid):
        # no independent checking job, always checked instead of frustrated
        return False

    def is_resolved(self, jobid):
        self.is_checked(jobid)

    def is_failed(self, jobid):
        self.is_frustrated(jobid)


class NHSSub(PlainSub):
    """
    submitter using non-blocking subprocess.Popen
    """

    def submit_pending(self, jobid):
        """
        `DIY: not recommend.`
        Already well written, submit with command from ``nohup_command`` in config.json,
        or from ``command`` argument when initializing the submitter.

        :param jobid: str.
        :return: None.
        """
        if self.kws.get("command"):
            command = self.kws["command"]
        elif conf.get("nohup_command"):
            command = conf["nohup_command"]
        else:
            raise ValueError("no commands template is specified")

        info_dict = flatten_dict(
            {
                "conf": conf,
                "param": history[jobid]["resource"].get("param"),
                "jobid": jobid,
            }
        )
        command = command.format(**info_dict)

        r = subprocess.Popen(
            shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        history[jobid]["pid"] = r.pid
        history[jobid]["popen"] = r
