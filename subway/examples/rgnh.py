import os
from ..plugins import NHSChk, NHSSub
from ..config import conf


class RgNSub(NHSSub):
    pass


class RgNChk(NHSChk):
    def check_checking_main(self, jobid):
        with open(os.path.join(conf["inputs_abs_dir"], jobid), "r") as f:
            L, l = f.readlines()
        L = float(L)
        l = float(l)
        with open(os.path.join(conf["outputs_abs_dir"], jobid), "r") as f:
            r = f.readlines()
        r = float(r[0])
        print(r, l)
        if r < l:
            print(
                "find the converged result, computation stopped for this parameter %s"
                % jobid
            )
            return []  # no new calculation is needed
        return [[L, l]]
