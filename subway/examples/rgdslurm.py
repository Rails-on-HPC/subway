# checker - plainchk - slurmchk - sslurmchk - dslurmchk - rgdchk

import os

from ..plugins import DSlurmChk, DSlurmSub
from ..config import conf, history


class RgDSub(DSlurmSub):
    pass


class RgDChk(DSlurmChk):
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

    def _render_input(self, jobid, param):
        L, l = param
        with open(os.path.join(conf["inputs_abs_dir"], jobid), "w") as f:
            f.writelines(["%s\n%s" % (L, l)])

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

    def _render_check_commands(self, jobid, checkid, param=None):
        mainp = os.path.join(conf["work_dir"], conf["check_executable"])
        # shall use ./miscs/rg_check.py
        inputp = os.path.join(conf["work_dir"], conf["check_inputs_dir"], checkid)
        outputp = os.path.join(conf["work_dir"], conf["check_outputs_dir"], checkid)
        command = "%s %s %s %s" % (
            self.kws.get("_py", "python3"),
            mainp,
            inputp,
            outputp,
        )
        return [command]

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
