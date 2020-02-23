# TODO: object oriented slurm interface via cli, avoid using pyslurm as it is an external dependence and is not portable as well

import subprocess
from datetime import datetime

from ..exceptions import SubwayException


class SlurmException(SubwayException):
    def __init__(self, message, code=90):
        super().__init__(message, code)


class SlurmValueError(SlurmException):
    def __init__(self, message, code=91):
        super().__init__(message, code)


class SlurmJob:
    def __init__(self, jobname=None, jobid=None):
        if (not jobname) and (not jobid):
            raise SlurmValueError("Must specify jobid or jobname")
        if jobid:
            self.jobid = jobid
        else:  # only jobname is defined (it is the user's responsibility to make sure that jobname is unique)
            self.jobid = self.get_jobid(jobname)
        self.jobinfo = self.get_jobinfo(self.jobid)
        self.jobname = self.jobinfo["JobName"]

    @staticmethod
    def get_jobid(
        jobname
    ):  # TODO: pay attention on time interval when job acct is not generated
        r = subprocess.run(
            ["sacct", "--name=%s" % jobname, "--format=JobID%50,Jobname%50"],
            stdout=subprocess.PIPE,
        )
        rl = r.stdout.decode("utf-8").split("\n")
        if len(rl) > 2:
            jid = [s for s in rl[2].split(" ") if s][0].strip()
            return jid  # TODO: pay attention to mislocation
        raise SlurmException("no job name is %s" % jobname)

    @staticmethod
    def get_jobinfo(jobid):
        """

        :param jobid:
        :return: jobinfo: dict, {'User': 'linuxuser', 'JobID': '4500', 'JobName': 'uuid',
                                'Partition': 'general', 'State': 'COMPLETED', 'Timelimit': '365-00:00+',
                                'Start': '2020-02-23T10:05:55', 'End': '2020-02-23T10:06:15',
                                'Elapsed': '00:00:20', 'NNodes': '1', 'NCPUS': '2', 'NodeList': 'c7'}
        """
        r = subprocess.run(
            [
                "sacct",
                "-j",
                jobid,
                "--format=User%30,JobID%50,Jobname%50,partition%20,state%20,time,start,end,elapsed,nnodes,ncpus,nodelist",
            ],
            stdout=subprocess.PIPE,
        )
        rl = r.stdout.decode("utf-8").split("\n")
        rl = [rl[0], rl[2]]
        rl = [s.strip() for s in rl if s.strip()]
        rll = [[s for s in l.split(" ") if s] for l in rl]
        assert len(rll[0]) == len(rll[1])
        info = {}
        for i, head in enumerate(rll[0]):
            info[head] = rll[1][i]
        info["Start_ob"] = datetime.strptime(info["Start"], "%Y-%m-%dT%H:%M:%S")
        info["Start_ts"] = info["Start_ob"].timestamp()
        if info.get("End", ""):
            info["End_ob"] = datetime.strptime(info["End"], "%Y-%m-%dT%H:%M:%S")
            info["End_ts"] = info["End_ob"].timestamp()
        return info
