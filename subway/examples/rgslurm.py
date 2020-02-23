import os
from uuid import uuid1
from shutil import copyfile

from ..plugins import SlurmChk, SlurmSub
from ..config import conf


class RgSSub(SlurmSub):
    def __init__(self, resource_limit=None, _py="python3"):
        self._py = _py
        super().__init__(resource_limit=resource_limit)

    def submit_pending(self, jobid):

        sbatchfile = os.path.join(conf["inputs_abs_dir"], jobid + ".sh")
        command = "sbatch %s" % sbatchfile
        print(command)
        os.system(command)


class RgSChk(SlurmChk):
    def __init__(self, params=None, _py="python3"):
        self._py = _py
        super().__init__(params)

    def render_sbatch(self, jobid):
        mainp = os.path.join(conf["work_dir"], conf["executable"])
        # shall use ./executables/randomg_run.py
        inputp = os.path.join(conf["inputs_abs_dir"], jobid)
        outputp = os.path.join(conf["outputs_abs_dir"], jobid)
        command = "%s %s %s %s" % (self._py, mainp, inputp, outputp)
        sbatch_template = f"""#! /bin/bash
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --job-name {jobid}
{command}
"""
        with open(os.path.join(conf["inputs_abs_dir"], jobid + ".sh"), "w") as f:
            f.writelines([sbatch_template])

    def check_kickstart(self):
        newinput = str(uuid1())
        L, l = self.params
        print(L, l)
        with open(os.path.join(conf["inputs_abs_dir"], newinput), "w") as f:
            f.writelines(["%s\n%s" % (L, l)])
        print("kickstart input")
        self.render_sbatch(newinput)
        print("kickstart sbatch")
        return [(newinput, {})]

    def check_checking(self, jobid):
        with open(os.path.join(conf["inputs_abs_dir"], jobid), "r") as f:
            L, l = f.readlines()
        l = float(l)
        with open(os.path.join(conf["outputs_abs_dir"], jobid), "r") as f:
            r = f.readlines()
        r = float(r[0])
        if r < l:
            print("find the converged result, computation stopped for this parameter")
            return []

        newinput = str(uuid1())
        print("begin copy input file...")
        copyfile(
            os.path.join(conf["inputs_abs_dir"], jobid),
            os.path.join(conf["inputs_abs_dir"], newinput),
        )
        print("begin create new sbatch file...")
        self.render_sbatch(newinput)
        return [(newinput, {})]
