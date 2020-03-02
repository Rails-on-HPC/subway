# avoid using pyslurm as it is an external dependence and is not portable as well

import os
import re
import sys
import time
import subprocess
from datetime import datetime

from ..exceptions import SubwayException


slurm_abnormal_states = [
    "BOOT_FAIL",
    "CANCELLED",
    "DEADLINE",
    "FAILED",
    "NODE_FAIL",
    "OUT_OF_MEMORY",
    "PREEMPTED",
    "STOPPED",
    "TIMEOUT",
]


def _slurm_time_trans(timestr, _format="%Y-%m-%dT%H:%M:%S"):
    """
    Fault tolerant time string translate to time obj and time stamps

    :param timestr: str.
    :param _format: Optional[str]. Default as "%Y-%m-%dT%H:%M:%S" used in sacct output
    :return: Tuple[Datetime, float]. Datetime obj and timestamp.
    """
    try:
        timeob = datetime.strptime(timestr, _format)
        timets = timeob.timestamp()
    except ValueError:
        timeob = timestr
        timets = timeob
    return timeob, timets


class SlurmException(SubwayException):
    def __init__(self, message, code=90):
        super().__init__(message, code)


class SlurmValueError(SlurmException):
    def __init__(self, message, code=91):
        super().__init__(message, code)


# TODO: more robust interaction with sacct with various possibilities and error cases
# documentation for sacct: https://slurm.schedmd.com/sacct.html
class SlurmJob:
    """
    Abstraction for job **submitted** to slurm.
    """

    def __init__(self, jobname=None, jobid=None, sacct="sacct"):
        """

        :param jobname: Optional[str].
        :param jobid: Optional[str]. One must specify at least one between ``jobid`` and ``jobname``.
        :param sacct: Optional[str]. Binary for ``sacct`` in shell, default is "sacct".
        """
        self.sacct = sacct
        if (not jobname) and (not jobid):
            raise SlurmValueError("Must specify jobid or jobname")
        if jobid:
            self.jobid = jobid
        else:  # only jobname is defined (it is the user's responsibility to make sure that jobname is unique)
            self.jobid = self.get_jobid(jobname)
        self.jobinfo = self.get_jobinfo(self.jobid)
        self.jobname = self.jobinfo["JobName"]

    def get_jobid(self, jobname, tries=6, interval=0.8):
        """
        get jobid from jobname via sacct query

        :param jobname: str.
        :param tries: Optional[int]. Default 6. It is worthing noting that query soon after job submitted would meet empty line,
                so repetitive try is necessary.
        :param interval: Optional[float]. Default 0.8. Seconds between two tries.
        :return: str. jobid.
        :raises SlurmException: when failed to get jobid after ``tries`` tries.
        """
        for i in range(tries):
            try:
                return self._get_jobid(jobname)
            except SlurmException as e:
                if e.code != 98 or i == tries - 1:
                    raise e
                else:
                    print(e.message, file=sys.stderr)
                    time.sleep(interval)

    def get_jobinfo(self, jobid, tries=6, interval=0.8):
        """
        get job info from jobid via sacct query

        :param jobid: str, jobid in slurm system (not jobid in subway which is jobname in slurm!)
        :param tries: Optional[int]. Default 6. It is worthing noting that query soon after job submitted would meet ilegal line,
                so repetitive try is necessary.
        :param interval:  Optional[float]. Default 0.8. Seconds between two tries.
        :return: Dict. Slurm job info.
        """
        for i in range(tries):
            try:
                return self._get_jobinfo(jobid)
            except AssertionError as e:
                if i == tries - 1:
                    raise e
                else:
                    print("try refetching jobinfo", file=sys.stderr)
                    time.sleep(interval)

    def _get_jobid(self, jobname):
        r = subprocess.run(
            [self.sacct, "--name=%s" % jobname, "--format=JobID%50,Jobname%50"],
            stdout=subprocess.PIPE,
        )
        rl = r.stdout.decode("utf-8").split("\n")
        # print(rl)# seconds after job submit, no line is expected with rl[2] = ""
        if len(rl) > 2 and rl[2]:
            jid = [s for s in rl[2].split(" ") if s][0].strip()
            return jid
        errmsg = "no job name is %s, you may need wait for a second" % jobname
        raise SlurmException(errmsg, code=98)

    def _get_jobinfo(self, jobid):
        """
        get job relavant info from sacct by jobid

        :param jobid: str.
        :return: jobinfo: Dict[str, str], ``{'User': 'linuxuser', 'JobID': '4500', 'JobName': 'uuid',
                                'Partition': 'general', 'State': 'COMPLETED', 'Timelimit': '365-00:00+',
                                'Start': '2020-02-23T10:05:55', 'End': '2020-02-23T10:06:15',
                                'Elapsed': '00:00:20', 'NNodes': '1', 'NCPUS': '2'}``
        """
        # nodelist can be "None assigned"
        # Timelimit attr can also be problematic in some slurm, the result is nothing
        r = subprocess.run(
            [
                self.sacct,
                "-j",
                jobid,
                "--format=User%30,JobID%50,Jobname%50,partition%20,state%20,time,start,end,elapsed,nnodes,ncpus,nodelist",
                "-P",  # that is the key point for accurate parsing!
            ],
            stdout=subprocess.PIPE,
        )
        rl = r.stdout.decode("utf-8").split("\n")
        rl = rl[:2]
        rll = [[s.strip() for s in l.split("|")] for l in rl]

        assert len(rll[0]) == len(rll[1])
        info = {}
        for i, head in enumerate(rll[0]):
            info[head] = rll[1][i]
        info["Start_ob"], info["Start_ts"] = _slurm_time_trans(info["Start"])
        if info.get("End", ""):
            info["End_ob"], info["End_ts"] = _slurm_time_trans(info["End"])
        return info


class SlurmTask:
    """
    Abstraction for slurm job **to be submitted**.
    """

    def __init__(
        self,
        sbatch="sbatch",
        scancel="scancel",
        shebang="#!/bin/bash",
        sbatch_path=None,
        sbatch_options=None,
        sbatch_commands=None,
    ):
        """

        :param sbatch: string, binary for sbatch
        :param sbatch: string, binary for scancel
        :param shebang: string, the #! line
        :param sbatch_path: string, sbatch script path
        :param sbatch_options: list of strings, such as "--job-name=uuid"
        :param sbatch_commands: list of strings, main command, such as "python test.py"
        """
        self.sbatch = sbatch
        self.scancel = scancel
        if not sbatch_path:
            raise SlurmValueError("sbatch_path must be specified")
        self.sbatch_path = sbatch_path
        self.shebang = shebang
        if not sbatch_commands:
            sbatch_commands = []
        self.sbatch_commands = sbatch_commands
        if not sbatch_options:
            sbatch_options = []
            # TODO: support dict sbatch options, may a consistent option API for subway?
        self.sbatch_options = sbatch_options
        if not os.path.exists(sbatch_path):
            self._render_sbatch()
        self.jid = None
        self._slurm_outpath = None

    def _render_sbatch(self):
        """
        generate sbatch script for the task.

        :return: None.
        """
        sbatch_string = self.shebang + "\n"
        for opt in self.sbatch_options:
            sbatch_string += "#SBATCH  " + opt + "\n"
        for line in self.sbatch_commands:
            sbatch_string += line + "\n"
        sbatch_string += "\n"
        with open(self.sbatch_path, "w") as f:
            f.writelines([sbatch_string])
        os.chmod(self.sbatch_path, 0o700)

    def slurm_outpath(self):
        # very experimental, not recommended for any production environment
        # array job default out: slurm-%A_%a.out, plain job default: slurm-%j.out
        # -e --error
        # -o --output
        # TODO: support customization on output file
        # TODO: support jobname pattern?
        # TODO: support on array job output
        # TODO: relative output path
        outname = []
        if not self._slurm_outpath:
            # for opt in self.sbatch_options:
            #     if opt.startswith(("-e", "--error", "-o", "--output")):
            #         outname.append()
            _slurm_outpath = os.path.join(os.getcwd(), "slurm-" + self.jobid() + ".out")
            self._slurm_outpath = [_slurm_outpath]
        return self._slurm_outpath

    def submit(self):
        """
        submit jobs to slurm by ``sbatch`` in shell.

        :return: None.
        """
        if not os.path.exists(self.sbatch_path):
            raise SlurmException("No sbatch file at %s" % self.sbatch_path, code=92)
        self.outerr = subprocess.run(
            [self.sbatch, self.sbatch_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def stdouterr(self):
        """
        get stdout and stderr for sbatch command

        :return: Tuple[str, str], string for stdout and stderr.
        """
        stdout = self.outerr.stdout
        stderr = self.outerr.stderr
        if stdout:
            stdout = stdout.decode("utf-8")
        if stderr:
            stderr = stderr.decode("utf-8")
        return stdout, stderr

    def jobid(self):
        """
        Get jobid from stdout of ``sbatch``.

        :return: str. jobid
        :raises SlurmException: No legal stdout from sbatch command to capture the jobid.
        """
        if not self.jid:
            stdout, stderr = self.stdouterr()
            if stdout:
                l = re.search(r"Submitted batch job (\d.*)", stdout)
                self.jid = l.groups()[0]
                return self.jid
            raise SlurmException(
                "No stdout for sbatch submit, the err is %s" % stderr, code=93
            )
        else:
            return self.jid

    def cancel(self):
        """
        cancel the job

        :return: subprocess.CompletedProcess, from ``scancel``.
        """
        self.jobid()
        r = subprocess.run(
            [self.scancel, self.jid], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return r

    def delete(self, include_output=False):
        """
        Delete the sbatch script and slurm output (experimental)

        :param include_output: Optional[bool]. Default False, whether try to delete slurm output
        :return: None.
        """
        if os.path.exists(self.sbatch_path):
            os.remove(self.sbatch_path)
        else:
            print("sbatch file doesn't exist", file=sys.stderr)
        if include_output:
            for f in self.slurm_outpath():
                if os.path.exists(f):
                    os.remove(f)
                else:
                    print("output file %s is not generated" % f, file=sys.stderr)
