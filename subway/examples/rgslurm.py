import os

from ..plugins import SSlurmChk, SSlurmSub
from ..config import conf


class RgSSub(SSlurmSub):
    pass


class RgSChk(SSlurmChk):
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
            return []  # no new calculation is needed
        return [[L, l]]
