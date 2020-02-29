import os

from ..plugins import SSlurmChk, SSlurmSub
from ..config import conf


class RgSSub(SSlurmSub):
    pass


class RgSChk(SSlurmChk):
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
            return []  # no new calculation is needed
        return [[L, l]]
