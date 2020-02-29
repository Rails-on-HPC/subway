# checker - plainchk - slurmchk - sslurmchk - dslurmchk - rgdchk

import os

from ..plugins import DSlurmChk, DSlurmSub
from ..config import conf, history


class RgDSub(DSlurmSub):
    pass


class RgDChk(DSlurmChk):
    def _render_input(self, jobid, checkid="", param=None, prefix=""):
        if not prefix:
            super()._render_input(jobid, checkid, param, prefix)
        else:  # check input
            with open(os.path.join(conf["inputs_abs_dir"], jobid), "r") as f:
                _, l = f.readlines()
            l = float(l)
            with open(os.path.join(conf["check_inputs_abs_dir"], checkid), "w") as f:
                f.writelines(["%s\n%s" % (l, param)])

    def check_checking_main(self, jobid):
        with open(
            os.path.join(
                conf["work_dir"], conf["check_outputs_dir"], history[jobid]["assoc"]
            ),
            "r",
        ) as f:
            b = f.readlines()
        b = float(b[0])
        if b < 0:
            return []
        else:
            with open(os.path.join(conf["inputs_abs_dir"], jobid), "r") as f:
                L, l = f.readlines()
            L = float(L)
            l = float(l)
            return [(L, l)]

    def _render_check_input(self, jobid, checkid, param):
        with open(os.path.join(conf["inputs_abs_dir"], jobid), "r") as f:
            _, l = f.readlines()
        l = float(l)
        with open(
            os.path.join(conf["work_dir"], conf["check_inputs_dir"], checkid), "w"
        ) as f:
            f.writelines(["%s\n%s" % (l, param)])
        # check script should be line2 - line1

    def check_finished_main(self, jobid):
        with open(os.path.join(conf["outputs_abs_dir"], jobid), "r") as f:
            r = f.readlines()
        r = float(r[0])

        return [r]  # check_param
