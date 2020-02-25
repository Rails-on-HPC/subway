import os
from uuid import uuid4
from shutil import copyfile

from ..framework import PlainChk, PlainSub
from ..config import conf


class RgSub(PlainSub):
    def __init__(self, resource_limit=None, _py="python3"):
        self._py = _py
        super().__init__(resource_limit=resource_limit)

    def submit_pending(self, jobid):
        mainp = os.path.join(conf["work_dir"], conf["executable"])
        # shall use ./executables/randomg_run.py
        inputp = os.path.join(conf["inputs_abs_dir"], jobid)
        outputp = os.path.join(conf["outputs_abs_dir"], jobid)
        command = "%s %s %s %s" % (self._py, mainp, inputp, outputp)
        print("run %s" % command)
        os.system(command)


class RgChk(PlainChk):
    def check_kickstart(self):
        # newinput = str(uuid1())
        # L, l = self.params
        # print(L, l)
        # with open(os.path.join(conf["inputs_abs_dir"], newinput), "w") as f:
        #     f.writelines(["%s\n%s" % (L, l)])
        #
        # print("kickstart input")
        # return [(newinput, {})]
        r = []
        for param in self.params:
            nid = str(uuid4())
            L, l = param
            with open(os.path.join(conf["inputs_abs_dir"], nid), "w") as f:
                f.writelines(["%s\n%s" % (L, l)])
            r.append((nid, {}))
        return r

    def check_checking(self, outputpath):
        with open(os.path.join(conf["inputs_abs_dir"], outputpath), "r") as f:
            L, l = f.readlines()
        l = float(l)
        with open(os.path.join(conf["outputs_abs_dir"], outputpath), "r") as f:
            r = f.readlines()
        r = float(r[0])
        if r < l:
            print("find the converged result, computation stopped for this parameter")
            return []

        newinput = str(uuid4())
        print("begin copy file...")
        copyfile(
            os.path.join(conf["inputs_abs_dir"], outputpath),
            os.path.join(conf["inputs_abs_dir"], newinput),
        )
        return [(newinput, {})]
