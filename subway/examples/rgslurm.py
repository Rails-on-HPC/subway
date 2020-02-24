import os
from uuid import uuid1
from shutil import copyfile

from ..plugins import SSlurmChk, SSlurmSub
from ..config import conf
from subway.components import SlurmTask


class RgSSub(SSlurmSub):
    pass


class RgSChk(SSlurmChk):
    def _render_commands(self, jobid, param=None):
        mainp = os.path.join(conf["work_dir"], conf["executable"])
        # shall use ./miscs/rg_run.py
        inputp = os.path.join(conf["inputs_abs_dir"], jobid)
        outputp = os.path.join(conf["outputs_abs_dir"], jobid)
        command = "%s %s %s %s" % (
            self.kws.get("_py", "python3"),
            mainp,
            inputp,
            outputp,
        )
        return [command]

    def _render_options(self, jobid, param=None):
        r = super()._render_options(jobid, param)
        r.append("-n 1")
        return r

    def _render_input(self, jobid, param):
        L, l = param
        with open(os.path.join(conf["inputs_abs_dir"], jobid), "w") as f:
            f.writelines(["%s\n%s" % (L, l)])

    def check_checking_main(self, jobid):
        with open(os.path.join(conf["inputs_abs_dir"], jobid), "r") as f:
            L, l = f.readlines()
        L = float(L)
        l = float(l)
        with open(os.path.join(conf["outputs_abs_dir"], jobid), "r") as f:
            r = f.readlines()
        r = float(r[0])
        if r < l:
            print(
                "find the converged result, computation stopped for this parameter %s"
                % jobid
            )
            return []
        return [[L, l]]
